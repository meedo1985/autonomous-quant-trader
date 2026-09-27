"""Task 22: the executor state machine (Constitution sections 20-21).

A scripted venue drives each section 21 path; the governor is the real one.
"""

from __future__ import annotations

import itertools
import random
import re
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from aqt.backtest.costs import Side as TradeSide
from aqt.execution.machine import (
    TERMINAL,
    TRANSITIONS,
    Event,
    Executor,
    IllegalTransition,
    State,
    step,
)
from aqt.execution.orders import (
    ExecutorConfig,
    client_order_id_for,
    limit_price_for,
    order_quantity,
)
from aqt.execution.simulator import (
    ExchangeError,
    Order,
    OrderStatus,
    SimulatedTimeout,
    SymbolFilters,
)
from aqt.governor.authorization import (
    ActualState,
    Authorization,
    GovernorConfig,
    Proposal,
    RefusalCode,
    Side,
)
from aqt.governor.machine import Governor

MIDNIGHT = datetime(2026, 1, 5, tzinfo=UTC)
SECOND = timedelta(seconds=1)
MINUTE = timedelta(minutes=1)
PRICE = Decimal("100")
FILTERS = SymbolFilters(
    step_size=Decimal("0.001"),
    min_qty=Decimal("0.001"),
    max_qty=Decimal("100"),
    min_notional=Decimal("10"),
)
GOVERNOR = GovernorConfig(
    max_slippage_bps=Decimal("15"),
    authorization_ttl=2 * MINUTE,
    decision_window=5 * MINUTE,
)
CONFIG = ExecutorConfig(not_found_delay=10 * SECOND, absence_queries=2)
NOT_FOUND = ExchangeError("NOT_FOUND", "no such order")


class Clock:
    def __init__(self) -> None:
        self.now = MIDNIGHT
        self.slept: list[timedelta] = []

    def __call__(self) -> datetime:
        return self.now

    def sleep(self, duration: timedelta) -> None:
        self.slept.append(duration)
        self.now += duration


@dataclass
class ScriptedVenue:
    """Answers each call with the next scripted item: an `Exception` to raise,
    "fill" / "partial" for an order, or an `Order` to return as is."""

    places: list[object]
    queries: list[object] = field(default_factory=list)
    placed: list[tuple[str, TradeSide, Decimal, datetime]] = field(default_factory=list)
    queried: list[str] = field(default_factory=list)
    last: tuple[str, str, TradeSide, Decimal, datetime] | None = None
    limit: Decimal | None = None

    def _answer(self, item: object) -> Order:
        if isinstance(item, Exception):
            raise item
        if isinstance(item, Order):
            return item
        assert self.last is not None, "a query found an order never placed"
        client_order_id, symbol, side, quantity, decision_time = self.last
        executed = quantity if item == "fill" else quantity / 2
        return Order(
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            orig_qty=quantity,
            executed_qty=executed,
            status=OrderStatus.FILLED if item == "fill" else OrderStatus.EXPIRED,
            decision_time=decision_time,
            fill_time=decision_time,
            fill_price=PRICE,
            quote_amount=executed * PRICE,
            cost_quote=Decimal(0),
            cost_bps=Decimal(0),
            limit_price=self.limit,
        )

    def place_order(
        self,
        client_order_id: str,
        symbol: str,
        side: TradeSide,
        quantity: Decimal,
        decision_time: datetime,
        *,
        limit_price: Decimal | None = None,
    ) -> Order:
        self.limit = limit_price
        self.placed.append((client_order_id, side, quantity, decision_time))
        self.last = (client_order_id, symbol, side, quantity, decision_time)
        return self._answer(self.places.pop(0))

    def query_order(self, client_order_id: str) -> Order:
        self.queried.append(client_order_id)
        return self._answer(self.queries.pop(0))


def _state(exposure: str = "0") -> ActualState:
    held = Decimal(1000) * Decimal(exposure)
    return ActualState(
        symbol="BTCUSDT",
        base_quantity=held / PRICE,
        quote_balance=Decimal(1000) - held,
        mark_price=PRICE,
        as_of=MIDNIGHT,
    )


def _setup(
    venue: ScriptedVenue, target: float = 0.5
) -> tuple[Governor, Executor, Clock, Authorization, Proposal, ActualState]:
    clock = Clock()
    governor = Governor(GOVERNOR)
    proposal = Proposal("BTCUSDT", target, MIDNIGHT)
    state = _state()
    authorization = governor.decide(proposal, state, MIDNIGHT)
    assert isinstance(authorization, Authorization)
    executor = Executor(
        governor, venue, FILTERS, CONFIG, clock=clock, sleep=clock.sleep
    )
    return governor, executor, clock, authorization, proposal, state


def _events(result: object) -> list[Event]:
    return [t.event for t in result.transitions]  # type: ignore[attr-defined]


def test_a_confirmed_fill_keeps_the_reservation_for_reconciliation() -> None:
    venue = ScriptedVenue(places=["fill"])
    governor, executor, _, auth, proposal, state = _setup(venue)
    result = executor.execute(auth, proposal, state)
    assert result.state is State.FILLED
    assert (result.released, result.reconciliation_required) == (False, True)
    assert venue.placed == [
        (client_order_id_for(auth), TradeSide.BUY, Decimal("5.000"), MIDNIGHT)
    ]
    # Astra R-2: only reconciliation (Task 23) may release it.
    later = governor.decide(Proposal("BTCUSDT", 0.1, MIDNIGHT), state, MIDNIGHT)
    assert later.code is RefusalCode.OUTSTANDING_AUTHORIZATION  # type: ignore[union-attr]


def test_timeout_queries_the_client_order_id() -> None:
    venue = ScriptedVenue(places=[SimulatedTimeout("lost reply")], queries=["fill"])
    _, executor, clock, auth, proposal, state = _setup(venue)
    result = executor.execute(auth, proposal, state)
    assert _events(result) == [
        Event.REDEEMED,
        Event.OUTCOME_UNKNOWN,
        Event.FILL_CONFIRMED,
    ]
    assert venue.queried == [client_order_id_for(auth)]
    assert clock.slept == []
    assert len(venue.placed) == 1


def test_not_found_waits_the_protocol_delay_then_finds_the_order() -> None:
    venue = ScriptedVenue(
        places=[SimulatedTimeout("lost reply")], queries=[NOT_FOUND, "fill"]
    )
    _, executor, clock, auth, proposal, state = _setup(venue)
    result = executor.execute(auth, proposal, state)
    assert result.state is State.FILLED
    assert _events(result)[1:] == [
        Event.OUTCOME_UNKNOWN,
        Event.NOT_FOUND,
        Event.FILL_CONFIRMED,
    ]
    assert clock.slept == [CONFIG.not_found_delay]
    assert len(venue.placed) == 1


def test_confirmed_absence_resends_with_the_identical_client_order_id() -> None:
    venue = ScriptedVenue(
        places=[SimulatedTimeout("lost"), "fill"], queries=[NOT_FOUND, NOT_FOUND]
    )
    _, executor, clock, auth, proposal, state = _setup(venue)
    result = executor.execute(auth, proposal, state)
    assert result.state is State.FILLED
    assert _events(result) == [
        Event.REDEEMED,
        Event.OUTCOME_UNKNOWN,
        Event.NOT_FOUND,
        Event.ABSENCE_CONFIRMED,
        Event.AUTHORIZATION_VALID,
        Event.FILL_CONFIRMED,
    ]
    first, second = venue.placed
    assert first == second  # same id, side, quantity, and decision time
    assert clock.slept == [CONFIG.not_found_delay]


def test_absence_needs_the_configured_number_of_not_found_answers() -> None:
    config = replace(CONFIG, absence_queries=3)
    venue = ScriptedVenue(
        places=[SimulatedTimeout("lost"), "fill"],
        queries=[NOT_FOUND, NOT_FOUND, NOT_FOUND],
    )
    governor, _, clock, auth, proposal, state = _setup(venue)
    executor = Executor(
        governor, venue, FILTERS, config, clock=clock, sleep=clock.sleep
    )
    result = executor.execute(auth, proposal, state)
    assert result.state is State.FILLED
    assert _events(result).count(Event.NOT_FOUND) == 2
    assert clock.slept == [CONFIG.not_found_delay] * 2


def test_a_resend_after_expiry_is_refused_and_asks_for_a_new_authorization() -> None:
    venue = ScriptedVenue(places=[SimulatedTimeout("lost")], queries=[NOT_FOUND])
    governor, _, clock, auth, proposal, state = _setup(venue)

    def slow_sleep(duration: timedelta) -> None:
        clock.sleep(duration + GOVERNOR.authorization_ttl)

    executor = Executor(governor, venue, FILTERS, CONFIG, clock=clock, sleep=slow_sleep)
    venue.queries.append(NOT_FOUND)
    result = executor.execute(auth, proposal, state)
    assert result.state is State.NEW_AUTHORIZATION_REQUIRED
    assert _events(result)[-1] is Event.AUTHORIZATION_EXPIRED
    assert len(venue.placed) == 1  # no resend
    assert (result.released, result.reconciliation_required) == (False, True)
    # The old authorization is dead; only a new one can trade.
    assert governor.redeem(auth, state, clock.now).code is RefusalCode.ALREADY_USED


@pytest.mark.parametrize(
    "queries",
    [
        [SimulatedTimeout("query lost")],
        [ExchangeError("SERVER_BUSY", "try later")],
        [NOT_FOUND, RuntimeError("socket closed")],
    ],
    ids=["query-timeout", "query-error", "second-query-error"],
)
def test_unknown_ends_in_freeze_and_never_in_a_new_order(queries: list[object]) -> None:
    venue = ScriptedVenue(places=[SimulatedTimeout("lost")], queries=list(queries))
    governor, executor, clock, auth, proposal, state = _setup(venue)
    result = executor.execute(auth, proposal, state)
    assert result.state is State.FREEZE
    assert _events(result)[-1] is Event.QUERY_UNKNOWN
    assert len(venue.placed) == 1
    assert not result.released
    # The reservation stays until reconciliation, so nothing new is authorized.
    blocked = governor.decide(Proposal("BTCUSDT", 0.1, MIDNIGHT), state, clock.now)
    assert blocked.code is RefusalCode.OUTSTANDING_AUTHORIZATION  # type: ignore[union-attr]


def test_one_authorization_never_places_two_orders() -> None:
    venue = ScriptedVenue(places=["fill", "fill"])
    _, executor, _, auth, proposal, state = _setup(venue)
    assert executor.execute(auth, proposal, state).state is State.FILLED
    again = executor.execute(auth, proposal, state)
    assert again.state is State.REFUSED
    assert again.refusal is not None and again.refusal.code is RefusalCode.ALREADY_USED
    assert len(venue.placed) == 1


def test_random_venue_behaviour_never_exceeds_one_order_or_the_bound() -> None:
    """Fuzz: whatever the venue answers, every placement under one
    authorization is the same order, at or below the authorized quantity."""
    rng = random.Random(22)
    answers: list[object] = [
        "fill",
        "partial",
        NOT_FOUND,
        SimulatedTimeout("lost"),
        ExchangeError("SERVER_BUSY", "x"),
        ExchangeError("DUPLICATE_CLIENT_ORDER_ID", "x"),
        ExchangeError("FILTER_LOT_SIZE", "x"),
    ]
    for _ in range(400):
        venue = ScriptedVenue(
            places=[rng.choice(answers) for _ in range(20)],
            queries=[rng.choice(answers) for _ in range(20)],
        )
        _, executor, _, auth, proposal, state = _setup(venue)
        result = executor.execute(auth, proposal, state)
        assert result.state in TERMINAL
        assert len(set(venue.placed)) == 1
        assert all(q <= auth.max_base_quantity for _, _, q, _ in venue.placed)
        # Each resend follows at least one full protocol delay, and none is
        # allowed after expiry, so placements are bounded.
        assert (
            len(venue.placed) <= GOVERNOR.authorization_ttl / CONFIG.not_found_delay + 1
        )
        if result.state is State.FREEZE:
            assert not result.released


def test_an_order_that_does_not_match_what_was_sent_freezes() -> None:
    venue = ScriptedVenue(places=[SimulatedTimeout("lost")], queries=["fill"])
    _, executor, _, auth, proposal, state = _setup(venue)
    wrong = venue._answer  # noqa: SLF001 - build a well-formed order, then corrupt it

    def query(client_order_id: str) -> Order:
        return replace(wrong("fill"), orig_qty=Decimal("9"), executed_qty=Decimal("9"))

    venue.query_order = query  # type: ignore[method-assign]
    result = executor.execute(auth, proposal, state)
    assert result.state is State.FREEZE
    assert _events(result)[-1] is Event.ORDER_MISMATCH
    assert not result.released


def test_an_order_with_the_wrong_side_freezes_even_if_fully_filled() -> None:
    venue = ScriptedVenue(places=[SimulatedTimeout("lost")], queries=["fill"])
    _, executor, _, auth, proposal, state = _setup(venue)
    build = venue._answer  # noqa: SLF001

    def query(client_order_id: str) -> Order:
        return replace(build("fill"), side=TradeSide.SELL)

    venue.query_order = query  # type: ignore[method-assign]
    result = executor.execute(auth, proposal, state)
    assert result.state is State.FREEZE
    assert _events(result)[-1] is Event.ORDER_MISMATCH
    assert "venue has" in result.transitions[-1].detail


def test_a_duplicate_id_error_is_queried_not_taken_as_a_rejection() -> None:
    venue = ScriptedVenue(
        places=[ExchangeError("DUPLICATE_CLIENT_ORDER_ID", "exists")], queries=["fill"]
    )
    _, executor, _, auth, proposal, state = _setup(venue)
    result = executor.execute(auth, proposal, state)
    assert _events(result)[1:] == [Event.OUTCOME_UNKNOWN, Event.FILL_CONFIRMED]


def test_a_definite_rejection_ends_rejected_and_awaits_reconciliation() -> None:
    venue = ScriptedVenue(places=[ExchangeError("INSUFFICIENT_BALANCE", "USDT")])
    _, executor, _, auth, proposal, state = _setup(venue)
    result = executor.execute(auth, proposal, state)
    assert (result.state, result.order) == (State.REJECTED, None)
    assert (result.released, result.reconciliation_required) == (False, True)


def test_a_partial_fill_ends_partially_filled() -> None:
    venue = ScriptedVenue(places=["partial"])
    _, executor, _, auth, proposal, state = _setup(venue)
    result = executor.execute(auth, proposal, state)
    assert result.state is State.PARTIALLY_FILLED
    assert not result.released


def test_a_sleep_that_does_not_advance_the_clock_freezes() -> None:
    venue = ScriptedVenue(places=[SimulatedTimeout("lost")], queries=[NOT_FOUND])
    governor, _, clock, auth, proposal, state = _setup(venue)
    executor = Executor(
        governor, venue, FILTERS, CONFIG, clock=clock, sleep=lambda _: None
    )
    result = executor.execute(auth, proposal, state)
    assert result.state is State.FREEZE
    assert _events(result)[-1] is Event.CLOCK_FAULT
    assert len(venue.placed) == 1


def test_a_changed_state_refuses_and_abandons_the_authorization() -> None:
    venue = ScriptedVenue(places=["fill"])
    governor, executor, _, auth, proposal, _ = _setup(venue)
    moved = replace(_state(), quote_balance=Decimal("999"))
    result = executor.execute(auth, proposal, moved)
    assert result.state is State.REFUSED
    assert result.refusal is not None
    assert result.refusal.code is RefusalCode.STATE_CHANGED
    assert result.released
    assert venue.placed == []


def test_the_quantity_is_rounded_down_and_never_exceeds_the_bound() -> None:
    venue = ScriptedVenue(places=["fill"])
    _, _, _, auth, _, _ = _setup(venue)
    odd = replace(auth, max_base_quantity=Decimal("1.23456"))
    assert order_quantity(odd, FILTERS) == Decimal("1.234")
    capped = replace(auth, max_base_quantity=Decimal("250"))
    assert order_quantity(capped, FILTERS) == FILTERS.max_qty
    tiny = replace(auth, max_base_quantity=Decimal("0.0009"))
    assert order_quantity(tiny, FILTERS) == 0


def test_a_bound_below_the_minimum_places_nothing_and_releases() -> None:
    venue = ScriptedVenue(places=["fill"])
    governor, _, clock, auth, proposal, state = _setup(venue)
    filters = replace(FILTERS, min_qty=Decimal("10"))  # the bound is 5
    executor = Executor(
        governor, venue, filters, CONFIG, clock=clock, sleep=clock.sleep
    )
    result = executor.execute(auth, proposal, state)
    assert (result.state, result.released) == (State.REFUSED, True)
    assert result.reconciliation_required is False
    assert _events(result) == [Event.NO_QUANTITY]
    assert venue.placed == []
    # Redeemed by this run before release: it can never be used afterwards.
    assert governor.redeem(auth, state, clock.now).code is RefusalCode.ALREADY_USED


def test_a_proposal_that_does_not_match_the_authorization_is_refused() -> None:
    venue = ScriptedVenue(places=["fill"])
    _, executor, _, auth, _, state = _setup(venue)
    with pytest.raises(ValueError, match="proposal"):
        executor.execute(auth, Proposal("BTCUSDT", 0.9, MIDNIGHT), state)
    assert venue.placed == []


def test_the_adverse_move_is_reported_against_the_mark_price() -> None:
    venue = ScriptedVenue(places=[])
    _, executor, _, auth, proposal, state = _setup(venue)
    venue.places.append("fill")
    base = venue._answer  # noqa: SLF001

    def place(*args: object, limit_price: Decimal | None = None) -> Order:
        venue.limit = limit_price
        venue.last = (args[0], args[1], args[2], args[3], args[4])  # type: ignore[assignment]
        return replace(base("fill"), fill_price=Decimal("100.2"))

    venue.place_order = place  # type: ignore[assignment]
    result = executor.execute(auth, proposal, state)
    assert result.adverse_move_bps == Decimal("20")
    assert result.slippage_breach  # 20 bps > the 15 bps bound


def test_client_order_ids_are_deterministic_and_valid_for_binance() -> None:
    venue = ScriptedVenue(places=[])
    _, _, _, auth, _, _ = _setup(venue)
    identifier = client_order_id_for(auth)
    assert identifier == client_order_id_for(auth)
    assert re.fullmatch(r"[a-zA-Z0-9-_]{1,36}", identifier)
    assert client_order_id_for(replace(auth, nonce="other")) != identifier


def test_executor_config_rejects_open_values_it_cannot_honour() -> None:
    with pytest.raises(ValueError):
        ExecutorConfig(not_found_delay=timedelta(0), absence_queries=2)
    with pytest.raises(ValueError):
        ExecutorConfig(not_found_delay=SECOND, absence_queries=1)


def test_every_state_event_pair_is_defined_or_explicitly_rejected() -> None:
    for state, event in itertools.product(State, Event):
        if (state, event) in TRANSITIONS:
            assert step(state, event) is TRANSITIONS[(state, event)]
        else:
            with pytest.raises(IllegalTransition):
                step(state, event)


def test_terminal_states_have_no_way_out_and_others_have_one() -> None:
    sources = {state for state, _ in TRANSITIONS}
    assert sources.isdisjoint(TERMINAL)
    assert sources | TERMINAL == set(State)


def test_freeze_is_reachable_only_from_ambiguity_and_never_leads_to_placing() -> None:
    into_freeze = {
        event for (_, event), target in TRANSITIONS.items() if target is State.FREEZE
    }
    assert into_freeze == {
        Event.QUERY_UNKNOWN,
        Event.ORDER_MISMATCH,
        Event.SLIPPAGE_BREACH,
        Event.CLOCK_FAULT,
        Event.ATTEMPT_LIMIT,
    }
    into_submitting = {
        source
        for (source, _), target in TRANSITIONS.items()
        if target is State.SUBMITTING
    }
    assert into_submitting == {State.READY, State.CONFIRMED_ABSENT}


def test_a_replay_cannot_release_a_frozen_reservation() -> None:
    """Astra R-1: a second run of an already-redeemed authorization, even one
    whose quantity rounds to zero, must not release the reservation."""
    venue = ScriptedVenue(
        places=[SimulatedTimeout("lost")], queries=[SimulatedTimeout("?")]
    )
    governor, executor, clock, auth, proposal, state = _setup(venue)
    assert executor.execute(auth, proposal, state).state is State.FREEZE
    replay = Executor(
        governor,
        venue,
        replace(FILTERS, min_qty=Decimal("10")),
        CONFIG,
        clock=clock,
        sleep=clock.sleep,
    )
    result = replay.execute(auth, proposal, state)
    assert result.state is State.REFUSED
    assert (
        result.refusal is not None and result.refusal.code is RefusalCode.ALREADY_USED
    )
    assert not result.released
    blocked = governor.decide(Proposal("BTCUSDT", 0.1, MIDNIGHT), state, clock.now)
    assert blocked.code is RefusalCode.OUTSTANDING_AUTHORIZATION  # type: ignore[union-attr]


class SteppingClock(Clock):
    """Returns `readings` in order, then keeps the last one."""

    def __init__(self, readings: list[datetime]) -> None:
        super().__init__()
        self.readings = readings

    def __call__(self) -> datetime:
        if len(self.readings) > 1:
            self.now = self.readings.pop(0)
        else:
            self.now = self.readings[0]
        return self.now


def test_expiry_is_checked_at_the_submission_boundary() -> None:
    """Astra R-3: valid when redeemed, expired by the time of placement."""
    venue = ScriptedVenue(places=["fill"])
    governor, _, _, auth, proposal, state = _setup(venue)
    just_before = auth.expires_at - timedelta(microseconds=1)
    clock = SteppingClock([just_before, auth.expires_at])
    executor = Executor(
        governor, venue, FILTERS, CONFIG, clock=clock, sleep=clock.sleep
    )
    result = executor.execute(auth, proposal, state)
    assert result.state is State.NEW_AUTHORIZATION_REQUIRED
    assert _events(result) == [Event.REDEEMED, Event.AUTHORIZATION_EXPIRED]
    assert venue.placed == []
    # Astra R2-1: nothing was sent, so the reservation is given back and a
    # fresh decision is not blocked; the spent authorization stays spent.
    assert (result.released, result.reconciliation_required) == (True, False)
    assert governor.redeem(auth, state, clock.now).code is RefusalCode.ALREADY_USED
    fresh = governor.decide(Proposal("BTCUSDT", 0.5, MIDNIGHT), state, clock.now)
    assert isinstance(fresh, Authorization)


def test_a_clock_that_goes_backwards_freezes_instead_of_retrying() -> None:
    """Astra R-4: each placement rolls the clock back to issuance and times
    out; without the forward-only check this retried forever."""
    venue = ScriptedVenue(places=[], queries=[])
    governor, _, clock, auth, proposal, state = _setup(venue)
    clock.now = MIDNIGHT + SECOND

    def place(*args: object, **_: object) -> Order:
        venue.placed.append(args[0])  # type: ignore[arg-type]
        clock.now = MIDNIGHT
        raise SimulatedTimeout("lost")

    venue.place_order = place  # type: ignore[assignment]
    venue.queries.extend([NOT_FOUND] * 50)
    executor = Executor(
        governor, venue, FILTERS, CONFIG, clock=clock, sleep=clock.sleep
    )
    result = executor.execute(auth, proposal, state)
    assert result.state is State.FREEZE
    assert _events(result)[-1] is Event.CLOCK_FAULT
    assert len(venue.placed) == 1
    assert not result.released


def test_a_fill_beyond_the_slippage_bound_freezes() -> None:
    """Astra R-5: contained after the fact; a market order cannot be capped."""
    venue = ScriptedVenue(places=[])
    _, executor, _, auth, proposal, state = _setup(venue)
    base = venue._answer  # noqa: SLF001

    def place(*args: object, limit_price: Decimal | None = None) -> Order:
        venue.limit = limit_price
        venue.last = (args[0], args[1], args[2], args[3], args[4])  # type: ignore[assignment]
        return replace(base("fill"), fill_price=Decimal("100.2"))

    venue.place_order = place  # type: ignore[assignment]
    result = executor.execute(auth, proposal, state)
    assert result.state is State.FREEZE
    assert _events(result)[-1] is Event.SLIPPAGE_BREACH
    assert result.slippage_breach and not result.released


def test_a_clock_fault_at_the_end_is_not_hidden() -> None:
    """Astra R2-2: release reuses the last accepted reading instead of taking
    a new one that could fault silently after the terminal state."""
    venue = ScriptedVenue(places=["fill"])
    governor, _, _, auth, proposal, state = _setup(venue)
    clock = SteppingClock([MIDNIGHT, MIDNIGHT, MIDNIGHT - SECOND])
    executor = Executor(
        governor,
        venue,
        replace(FILTERS, min_qty=Decimal("10")),
        CONFIG,
        clock=clock,
        sleep=clock.sleep,
    )
    result = executor.execute(auth, proposal, state)
    assert result.state is State.REFUSED
    assert _events(result) == [Event.NO_QUANTITY]
    assert result.released


def test_every_order_carries_the_price_cap_of_its_authorization() -> None:
    venue = ScriptedVenue(places=["fill"])
    _, executor, _, auth, proposal, state = _setup(venue)
    result = executor.execute(auth, proposal, state)
    assert venue.limit == Decimal("100.1500")  # 100 * (1 + 15 bps)
    assert result.order is not None and result.order.limit_price == venue.limit


def test_the_price_cap_rounds_toward_the_mark_on_the_tick() -> None:
    venue = ScriptedVenue(places=[])
    _, _, _, auth, _, _ = _setup(venue)
    ticked = replace(FILTERS, tick_size=Decimal("0.1"))
    assert limit_price_for(auth, PRICE, ticked) == Decimal("100.1")  # buy: down
    sell = replace(auth, side=Side.SELL)
    assert limit_price_for(sell, PRICE, ticked) == Decimal("99.9")  # sell: up
    assert limit_price_for(sell, PRICE, FILTERS) == Decimal("99.8500")


def test_an_unfilled_capped_order_ends_not_filled() -> None:
    venue = ScriptedVenue(places=[])
    _, executor, _, auth, proposal, state = _setup(venue)
    base = venue._answer  # noqa: SLF001

    def place(*args: object, limit_price: Decimal | None = None) -> Order:
        venue.limit = limit_price
        venue.last = (args[0], args[1], args[2], args[3], args[4])  # type: ignore[assignment]
        return replace(
            base("fill"), executed_qty=Decimal(0), status=OrderStatus.EXPIRED
        )

    venue.place_order = place  # type: ignore[assignment]
    result = executor.execute(auth, proposal, state)
    assert result.state is State.NOT_FILLED
    assert _events(result)[-1] is Event.NO_FILL_CONFIRMED
    assert result.reconciliation_required and not result.released


def test_the_price_cap_is_never_looser_than_the_exact_bound() -> None:
    """Astra R3-1: 34-digit rounding once lifted 100.14 to 100.15."""
    from fractions import Fraction

    venue = ScriptedVenue(places=[])
    _, _, _, auth, _, _ = _setup(venue)
    sell = replace(auth, side=Side.SELL)
    ticked = replace(FILTERS, tick_size=Decimal("0.01"))
    near = Decimal("99." + "9" * 32)  # 100 - 1e-32, exactly
    assert limit_price_for(auth, near, ticked) == Decimal("100.14")
    above = Decimal("100." + "0" * 31 + "1")  # 100 + 1e-32
    assert limit_price_for(sell, above, ticked) == Decimal("99.86")
    rng = random.Random(31)
    for _ in range(500):
        mark = Decimal(rng.randrange(1, 10**34)).scaleb(-rng.randrange(0, 34))
        bps = Decimal(rng.randrange(0, 2000))
        for side_auth in (
            replace(auth, max_slippage_bps=bps),
            replace(sell, max_slippage_bps=bps),
        ):
            buy = side_auth.side is Side.BUY
            ratio = Fraction(bps) / 10_000
            bound = Fraction(mark) * (1 + ratio if buy else 1 - ratio)
            for filters in (FILTERS, ticked):
                cap = limit_price_for(side_auth, mark, filters)
                if cap is None:
                    continue
                assert (Fraction(cap) <= bound) if buy else (Fraction(cap) >= bound)


def test_no_valid_price_refuses_and_releases_instead_of_raising() -> None:
    """Astra R3-2: a tick coarser than the whole price used to raise and
    strand the redeemed reservation."""
    venue = ScriptedVenue(places=["fill"])
    governor, _, clock, auth, proposal, state = _setup(venue)
    executor = Executor(
        governor,
        venue,
        replace(FILTERS, tick_size=Decimal("200")),
        CONFIG,
        clock=clock,
        sleep=clock.sleep,
    )
    result = executor.execute(auth, proposal, state)
    assert result.state is State.REFUSED
    assert _events(result) == [Event.NO_VALID_PRICE]
    assert (result.released, result.reconciliation_required) == (True, False)
    assert venue.placed == []
    fresh = governor.decide(Proposal("BTCUSDT", 0.5, MIDNIGHT), state, clock.now)
    assert isinstance(fresh, Authorization)


def test_affordable_quantity_never_exceeds_the_cash_at_the_worst_cost() -> None:
    from fractions import Fraction

    from aqt.execution.orders import WORST_CASE_COST_BPS, affordable_quantity

    assert WORST_CASE_COST_BPS == Decimal("27.0")
    rng = random.Random(24)
    for _ in range(500):
        cash = Decimal(rng.randrange(0, 10**9)).scaleb(-rng.randrange(0, 6))
        cap = Decimal(rng.randrange(1, 10**8)).scaleb(-rng.randrange(0, 4))
        q = affordable_quantity(cash, cap, FILTERS)
        cost = Fraction(q) * Fraction(cap) * (1 + Fraction(27, 10_000))
        assert 0 <= Fraction(q) and cost <= Fraction(cash)
        one_more = (Fraction(q) + Fraction(FILTERS.step_size)) * Fraction(cap)
        assert one_more * (1 + Fraction(27, 10_000)) > Fraction(cash)
