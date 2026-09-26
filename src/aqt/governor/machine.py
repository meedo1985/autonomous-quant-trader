"""The governor: issues bounded authorizations or refuses (roadmap Task 21).

The exposure rules are not restated here. They come from the frozen
benchmark rules in `aqt.benchmarks.canonical` (`rebalance`,
`reaches_rebalance_band`, `is_scheduled_decision`), so the governor and the
backtester cannot disagree about what is allowed:

* `scope.risk_increase_rule`: increases only at 00:00 UTC, and only 24h after
  the last increase;
* `scope.intraday_action_rule`: intraday, only reductions of at least 0.10;
* `exposure_mapping.rebalance_band_absolute` 0.10;
* `scope.max_exposure_per_asset` 1.0: a target outside `[0, 1]` is refused,
  never clipped.

Every decision is computed from the `ActualState` passed in (section 20,
"re-evaluate from actual fills"). The governor keeps no exposure of its own;
it remembers only the nonces it issued and used.
"""

from __future__ import annotations

import math
import secrets
from collections.abc import Callable
from datetime import datetime
from decimal import ROUND_FLOOR, Context, Decimal
from fractions import Fraction

from aqt.benchmarks.canonical import (
    MAX_EXPOSURE,
    MIN_EXPOSURE,
    MINIMUM_HOLD_FOR_RISK_INCREASE,
    CanonicalBenchmarkError,
    ExposureState,
    RebalanceAction,
    is_scheduled_decision,
    reaches_rebalance_band,
    rebalance,
)
from aqt.governor.authorization import (
    PROTOCOL_SYMBOLS,
    ActualState,
    Authorization,
    GovernorConfig,
    Proposal,
    Refusal,
    RefusalCode,
    Side,
)

__all__ = ["Governor"]

_ROUND_DOWN = Context(prec=34, rounding=ROUND_FLOOR)


def _at_most(value: Fraction) -> Decimal:
    """`value` (>= 0) as a Decimal that never exceeds it."""
    return _ROUND_DOWN.divide(Decimal(value.numerator), Decimal(value.denominator))


def _default_nonce() -> str:
    return secrets.token_hex(16)


class Governor:
    """Issues and redeems authorizations. One instance per trading process."""

    def __init__(
        self,
        config: GovernorConfig,
        *,
        nonce_source: Callable[[], str] = _default_nonce,
    ) -> None:
        self._config = config
        self._nonce_source = nonce_source
        self._issued: dict[str, Authorization] = {}
        self._used: set[str] = set()
        self._outstanding: dict[str, Authorization] = {}

    def decide(
        self, proposal: Proposal, state: ActualState, now: datetime
    ) -> Authorization | Refusal:
        """Authorize `proposal` against the actual `state`, or refuse it."""
        if proposal.symbol not in PROTOCOL_SYMBOLS:
            return Refusal(RefusalCode.UNKNOWN_SYMBOL, proposal.symbol)
        if state.symbol != proposal.symbol:
            return Refusal(
                RefusalCode.SYMBOL_MISMATCH, f"{state.symbol} != {proposal.symbol}"
            )
        target = proposal.target_exposure
        if not math.isfinite(target) or not MIN_EXPOSURE <= target <= MAX_EXPOSURE:
            return Refusal(
                RefusalCode.TARGET_OUT_OF_RANGE,
                f"{target!r} is outside [{MIN_EXPOSURE}, {MAX_EXPOSURE}]",
            )
        if proposal.decision_time > now:
            return Refusal(
                RefusalCode.DECISION_IN_FUTURE, proposal.decision_time.isoformat()
            )
        window_end = proposal.decision_time + self._config.decision_window
        if now >= window_end:
            # A 00:00 proposal presented later must not pass as the scheduled
            # decision (T21-02, Astra R-1).
            return Refusal(
                RefusalCode.STALE_DECISION,
                f"decision at {proposal.decision_time.isoformat()} closed at "
                f"{window_end.isoformat()}; it is now {now.isoformat()}",
            )
        pending = self._outstanding.get(proposal.symbol)
        if pending is not None and now < pending.expires_at:
            # One executable transition at a time (Astra R-2): two
            # authorizations against the same state could together overshoot.
            return Refusal(
                RefusalCode.OUTSTANDING_AUTHORIZATION,
                f"{pending.nonce} is outstanding until "
                f"{pending.expires_at.isoformat()}",
            )
        if state.as_of > now:
            return Refusal(RefusalCode.STATE_FROM_FUTURE, state.as_of.isoformat())
        equity = state.equity
        if equity == 0:
            return Refusal(RefusalCode.NO_EQUITY, "the account holds nothing")

        current = state.exposure
        try:
            held = ExposureState(current, state.last_risk_increase_time)
        except CanonicalBenchmarkError as error:
            return Refusal(RefusalCode.INVALID_STATE, str(error))
        try:
            decision = rebalance(held, target, proposal.decision_time)
        except CanonicalBenchmarkError as error:
            return Refusal(RefusalCode.INVALID_DECISION_TIME, str(error))
        if decision.action is RebalanceAction.HOLD:
            return self._hold_refusal(proposal, state, current, decision.reason)

        change = decision.new_exposure - current
        # Exact, from holdings: the base quantity the target implies at the
        # mark price, minus the base quantity actually held, rounded toward
        # zero so the bound never exceeds it (Astra R-3).
        price = Fraction(state.mark_price)
        base = Fraction(state.base_quantity)
        target_base = (
            Fraction(Decimal(repr(decision.new_exposure)))
            * (base * price + Fraction(state.quote_balance))
            / price
        )
        quantity = _at_most(abs(target_base - base))
        nonce = self._nonce_source()
        if nonce in self._issued:
            raise RuntimeError("nonce source repeated a nonce; refusing to reuse it")
        authorization = Authorization(
            proposal_hash=proposal.proposal_hash(),
            state_reference=state.state_reference(),
            symbol=proposal.symbol,
            side=Side.BUY if change > 0 else Side.SELL,
            current_exposure=current,
            target_exposure=decision.new_exposure,
            max_base_quantity=quantity,
            max_slippage_bps=self._config.max_slippage_bps,
            issued_at=now,
            expires_at=min(now + self._config.authorization_ttl, window_end),
            nonce=nonce,
        )
        self._issued[nonce] = authorization
        self._outstanding[proposal.symbol] = authorization
        return authorization

    def redeem(
        self, authorization: Authorization, state: ActualState, now: datetime
    ) -> Refusal | None:
        """Mark `authorization` used, or refuse it. `None` means it may be used.

        Refused when this governor did not issue it, when it was already used,
        when it has expired, or when the actual state is no longer the state it
        was issued against.
        """
        issued = self._issued.get(authorization.nonce)
        if issued != authorization:
            return Refusal(RefusalCode.NOT_ISSUED_HERE, authorization.nonce)
        if authorization.nonce in self._used:
            return Refusal(RefusalCode.ALREADY_USED, authorization.nonce)
        if now >= authorization.expires_at:
            return Refusal(RefusalCode.EXPIRED, authorization.expires_at.isoformat())
        if state.state_reference() != authorization.state_reference:
            return Refusal(RefusalCode.STATE_CHANGED, "actual state differs from issue")
        self._used.add(authorization.nonce)
        return None

    @staticmethod
    def _hold_refusal(
        proposal: Proposal, state: ActualState, current: float, reason: str
    ) -> Refusal:
        change = proposal.target_exposure - current
        if not reaches_rebalance_band(change):
            return Refusal(RefusalCode.INSIDE_REBALANCE_BAND, reason)
        if change > 0 and not is_scheduled_decision(proposal.decision_time):
            return Refusal(RefusalCode.INCREASE_NOT_SCHEDULED, reason)
        last = state.last_risk_increase_time
        if (
            change > 0
            and last is not None
            and proposal.decision_time - last < MINIMUM_HOLD_FOR_RISK_INCREASE
        ):
            return Refusal(RefusalCode.MINIMUM_HOLD, reason)
        raise AssertionError(f"unclassified hold: {reason}")
