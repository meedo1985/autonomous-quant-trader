"""Task 21: the governor state machine (Constitution section 20)."""

from __future__ import annotations

import dataclasses
import random
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from fractions import Fraction

import pytest

from aqt.governor.authorization import (
    ActualState,
    Authorization,
    GovernorConfig,
    Proposal,
    Refusal,
    RefusalCode,
    Side,
)
from aqt.governor.machine import Governor

MIDNIGHT = datetime(2026, 1, 5, tzinfo=UTC)
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
PRICE = Decimal("100")
EQUITY = Decimal("1000")
MINUTE = timedelta(minutes=1)
CONFIG = GovernorConfig(
    max_slippage_bps=Decimal("15"),
    authorization_ttl=5 * MINUTE,
    decision_window=10 * MINUTE,
)


def _state(
    exposure: str, *, at: datetime = MIDNIGHT, last: datetime | None = None
) -> ActualState:
    held = EQUITY * Decimal(exposure)
    return ActualState(
        symbol="BTCUSDT",
        base_quantity=held / PRICE,
        quote_balance=EQUITY - held,
        mark_price=PRICE,
        as_of=at,
        last_risk_increase_time=last,
    )


def _decide(
    governor: Governor, target: float, state: ActualState, at: datetime
) -> Authorization | Refusal:
    return governor.decide(Proposal("BTCUSDT", target, at), state, at)


def _code(outcome: Authorization | Refusal) -> RefusalCode | None:
    return outcome.code if isinstance(outcome, Refusal) else None


def test_a_risk_increase_happens_only_at_the_scheduled_decision() -> None:
    governor = Governor(CONFIG)
    three_am = MIDNIGHT + 3 * HOUR
    refused = _decide(governor, 0.5, _state("0.2", at=three_am), three_am)
    assert _code(refused) is RefusalCode.INCREASE_NOT_SCHEDULED
    # The last increase was the previous scheduled decision, 24h earlier.
    authorized = _decide(governor, 0.5, _state("0.2", last=MIDNIGHT - DAY), MIDNIGHT)
    assert isinstance(authorized, Authorization)
    assert (authorized.side, authorized.target_exposure) == (Side.BUY, 0.5)


def test_a_risk_increase_inside_the_minimum_hold_is_refused() -> None:
    governor = Governor(CONFIG)
    # 23h after the last increase is 23:00, which is refused as unscheduled.
    eleven_pm = MIDNIGHT + 23 * HOUR
    late = _decide(governor, 0.5, _state("0.2", at=eleven_pm, last=MIDNIGHT), eleven_pm)
    assert _code(late) is RefusalCode.INCREASE_NOT_SCHEDULED
    # A second increase at the same scheduled decision is inside the 24h hold.
    again = _decide(governor, 0.5, _state("0.2", last=MIDNIGHT), MIDNIGHT)
    assert _code(again) is RefusalCode.MINIMUM_HOLD


def test_intraday_reductions_must_reach_the_band() -> None:
    governor = Governor(CONFIG)
    at = MIDNIGHT + 3 * HOUR
    small = _decide(governor, 0.41, _state("0.5", at=at), at)
    assert _code(small) is RefusalCode.INSIDE_REBALANCE_BAND
    large = _decide(governor, 0.39, _state("0.5", at=at), at)
    assert isinstance(large, Authorization)
    assert (large.side, large.target_exposure) == (Side.SELL, 0.39)
    assert large.max_base_quantity == Decimal("1.1")  # 0.11 * 1000 / 100


@pytest.mark.parametrize("target", [1.01, -0.01, float("nan"), float("inf")])
def test_a_target_outside_0_to_1_is_refused(target: float) -> None:
    outcome = _decide(Governor(CONFIG), target, _state("0.2"), MIDNIGHT)
    assert _code(outcome) is RefusalCode.TARGET_OUT_OF_RANGE


def test_an_authorization_carries_every_section_20_field() -> None:
    governor = Governor(CONFIG)
    state = _state("0.2")
    proposal = Proposal("BTCUSDT", 0.8, MIDNIGHT)
    authorization = governor.decide(proposal, state, MIDNIGHT)
    assert isinstance(authorization, Authorization)
    assert authorization.proposal_hash == proposal.proposal_hash()
    assert authorization.state_reference == state.state_reference()
    assert authorization.symbol == "BTCUSDT"
    assert authorization.target_exposure == 0.8
    assert authorization.max_base_quantity == Decimal("6")  # 0.6 * 1000 / 100
    assert authorization.max_slippage_bps == Decimal("15")
    assert authorization.expires_at == MIDNIGHT + CONFIG.authorization_ttl
    assert len(authorization.nonce) == 32
    assert {f.name for f in dataclasses.fields(Authorization)} >= {
        "proposal_hash",
        "state_reference",
        "symbol",
        "max_base_quantity",
        "max_slippage_bps",
        "expires_at",
        "nonce",
    }


def test_nonces_never_repeat() -> None:
    governor = Governor(CONFIG)
    nonces = set()
    for day in range(500):
        at = MIDNIGHT + day * DAY
        outcome = _decide(governor, 0.8, _state("0.2", at=at), at)
        assert isinstance(outcome, Authorization)
        nonces.add(outcome.nonce)
    assert len(nonces) == 500
    stuck = Governor(CONFIG, nonce_source=lambda: "same")
    _decide(stuck, 0.8, _state("0.2"), MIDNIGHT)
    tomorrow = MIDNIGHT + DAY
    with pytest.raises(RuntimeError, match="repeated a nonce"):
        _decide(stuck, 0.8, _state("0.2", at=tomorrow), tomorrow)


def test_an_authorization_is_single_use_unexpired_and_bound_to_its_state() -> None:
    governor = Governor(CONFIG)
    state = _state("0.2")
    authorization = governor.decide(Proposal("BTCUSDT", 0.8, MIDNIGHT), state, MIDNIGHT)
    assert isinstance(authorization, Authorization)

    expired = governor.redeem(authorization, state, authorization.expires_at)
    assert _code(expired) is RefusalCode.EXPIRED
    moved = _state("0.3")
    assert _code(governor.redeem(authorization, moved, MIDNIGHT)) is (
        RefusalCode.STATE_CHANGED
    )
    forged = dataclasses.replace(authorization, max_base_quantity=Decimal("60"))
    assert (
        _code(governor.redeem(forged, state, MIDNIGHT)) is RefusalCode.NOT_ISSUED_HERE
    )
    other = Governor(CONFIG)
    assert _code(other.redeem(authorization, state, MIDNIGHT)) is (
        RefusalCode.NOT_ISSUED_HERE
    )

    assert governor.redeem(authorization, state, MIDNIGHT + HOUR / 60) is None
    again = governor.redeem(authorization, state, MIDNIGHT + HOUR / 60)
    assert _code(again) is RefusalCode.ALREADY_USED


def test_after_a_partial_fill_decisions_use_the_actual_exposure() -> None:
    governor = Governor(CONFIG)
    # Authorized 0.2 -> 0.8, but only half filled: the account is at 0.5.
    first = _decide(governor, 0.8, _state("0.2"), MIDNIGHT)
    assert isinstance(first, Authorization) and first.target_exposure == 0.8
    at = MIDNIGHT + HOUR
    actual = _state("0.5", at=at, last=MIDNIGHT)

    # From the intended 0.8, a target of 0.45 would be a 0.35 reduction and
    # would be authorized. From the actual 0.5 it is inside the band.
    inside = _decide(governor, 0.45, actual, at)
    assert _code(inside) is RefusalCode.INSIDE_REBALANCE_BAND

    reduce = _decide(governor, 0.35, actual, at)
    assert isinstance(reduce, Authorization)
    assert reduce.current_exposure == 0.5
    assert reduce.max_base_quantity == Decimal("1.5")  # (0.5 - 0.35) * 1000 / 100


def test_no_input_increases_exposure_outside_the_scheduled_window() -> None:
    """A seeded random search over states, targets, times and last increases."""
    rng = random.Random(20260926)
    increases = 0
    for _ in range(5000):
        at = MIDNIGHT + rng.randrange(0, 24 * 14) * HOUR
        last = None if rng.random() < 0.3 else MIDNIGHT + rng.randrange(-5, 14) * DAY
        if last is not None and last > at:
            last = None
        current = f"{rng.randrange(0, 101) / 100:.2f}"
        target = rng.choice([rng.random(), rng.uniform(-0.2, 1.2), 0.0, 1.0])
        outcome = _decide(
            Governor(CONFIG), target, _state(current, at=at, last=last), at
        )
        if isinstance(outcome, Authorization):
            assert 0.0 <= outcome.target_exposure <= 1.0
            assert outcome.max_base_quantity >= 0
            if outcome.target_exposure > outcome.current_exposure:
                increases += 1
                assert at.hour == 0
                assert last is None or at - last >= DAY
    assert increases > 50  # the search did reach authorized increases


def test_a_stale_scheduled_proposal_cannot_increase_risk_later() -> None:
    """A 00:00 proposal presented at 03:00 is not a scheduled decision any more."""
    governor = Governor(CONFIG)
    three_am = MIDNIGHT + 3 * HOUR
    stale = governor.decide(
        Proposal("BTCUSDT", 0.8, MIDNIGHT), _state("0.2", at=three_am), three_am
    )
    assert _code(stale) is RefusalCode.STALE_DECISION
    just_in_time = MIDNIGHT + CONFIG.decision_window - timedelta(seconds=1)
    fresh = governor.decide(
        Proposal("BTCUSDT", 0.8, MIDNIGHT), _state("0.2", at=just_in_time), just_in_time
    )
    assert isinstance(fresh, Authorization)


def test_a_decision_cannot_be_issued_or_redeemed_after_its_window() -> None:
    """Astra R-1: a 00:00 increase cannot be carried later into the hour."""
    late = MIDNIGHT + CONFIG.decision_window
    refused = Governor(CONFIG).decide(
        Proposal("BTCUSDT", 0.8, MIDNIGHT), _state("0.2"), late
    )
    assert _code(refused) is RefusalCode.STALE_DECISION
    stale_proposal = Governor(CONFIG).decide(
        Proposal("BTCUSDT", 0.8, MIDNIGHT), _state("0.2"), MIDNIGHT + 59 * MINUTE
    )
    assert _code(stale_proposal) is RefusalCode.STALE_DECISION

    # A long TTL cannot extend the window either.
    long_ttl = dataclasses.replace(CONFIG, authorization_ttl=4 * HOUR)
    governor = Governor(long_ttl)
    state = _state("0.2")
    issued_late = MIDNIGHT + 9 * MINUTE
    authorization = governor.decide(
        Proposal("BTCUSDT", 0.8, MIDNIGHT), state, issued_late
    )
    assert isinstance(authorization, Authorization)
    assert authorization.expires_at == MIDNIGHT + CONFIG.decision_window
    assert _code(governor.redeem(authorization, state, MIDNIGHT + 3 * HOUR)) is (
        RefusalCode.EXPIRED
    )


def test_only_one_authorization_is_outstanding_per_symbol() -> None:
    """Astra R-2: two authorizations against one state could buy twice."""
    governor = Governor(CONFIG)
    state = ActualState("BTCUSDT", Decimal(2), Decimal(800), Decimal(100), MIDNIGHT)
    first = governor.decide(Proposal("BTCUSDT", 0.5, MIDNIGHT), state, MIDNIGHT)
    assert isinstance(first, Authorization) and first.max_base_quantity == 3
    second = governor.decide(Proposal("BTCUSDT", 0.5, MIDNIGHT), state, MIDNIGHT)
    assert _code(second) is RefusalCode.OUTSTANDING_AUTHORIZATION
    # Once the first has expired, a new decision starts from the actual state.
    after = first.expires_at
    filled = ActualState("BTCUSDT", Decimal(5), Decimal(500), Decimal(100), after)
    later = governor.decide(Proposal("BTCUSDT", 0.2, MIDNIGHT), filled, after)
    assert isinstance(later, Authorization) and later.side is Side.SELL


@pytest.mark.parametrize(
    ("base", "quote", "price", "target"),
    [
        ("0", "1000", "30000", 0.5),  # Astra R-3: exactly 1/60 BTC
        ("0", "1000", "3", 1.0),
        ("0", "7", "3", 1 / 3),
        ("1", "0", "7", 0.0),
        ("0.3", "0.7", "9", 0.1),
        ("12.345678901234567890123", "98765.4321", "29999.99999999", 0.95),
    ],
)
def test_the_quantity_bound_never_exceeds_the_exact_quantity(
    base: str, quote: str, price: str, target: float
) -> None:
    state = ActualState(
        "BTCUSDT", Decimal(base), Decimal(quote), Decimal(price), MIDNIGHT
    )
    outcome = Governor(CONFIG).decide(
        Proposal("BTCUSDT", target, MIDNIGHT), state, MIDNIGHT
    )
    assert isinstance(outcome, Authorization)
    held, p = Fraction(Decimal(base)), Fraction(Decimal(price))
    wanted = (
        Fraction(Decimal(repr(outcome.target_exposure)))
        * (held * p + Fraction(Decimal(quote)))
        / p
    )
    exact = abs(wanted - held)
    bound = Fraction(outcome.max_base_quantity)
    assert bound <= exact
    assert exact - bound <= exact * Fraction(1, 10**30) + Fraction(1, 10**60)
