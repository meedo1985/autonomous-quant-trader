"""Synthetic bar-semantics tests. No real market data, no network access."""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from aqt.data.bars import (
    BAR_INTERVAL,
    BAR_INTERVAL_LABEL,
    Bar,
    BarSemanticsError,
    BarSeries,
    contiguous_bar_series,
    require_utc,
)

_ORIGIN = datetime(2024, 1, 1, tzinfo=UTC)


def _ts(hour: int) -> datetime:
    return _ORIGIN + timedelta(hours=hour)


def _bar(
    moment: datetime,
    *,
    open_: float = 100.0,
    high: float = 110.0,
    low: float = 90.0,
    close: float = 105.0,
    volume: float = 10.0,
    interval: timedelta = BAR_INTERVAL,
) -> Bar:
    return Bar(
        open_time=moment,
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=volume,
        interval=interval,
    )


def _hourly(hour: int) -> Bar:
    """A deterministic synthetic bar whose open price encodes its hour."""
    return _bar(
        _ts(hour),
        open_=100.0 + hour,
        high=110.0 + hour,
        low=90.0 + hour,
        close=105.0 + hour,
        volume=1.0 + hour,
    )


def _series(hours: tuple[int, ...]) -> BarSeries:
    return BarSeries(symbol="TESTUSDT", bars=tuple(_hourly(h) for h in hours))


def test_frozen_interval_matches_protocol() -> None:
    assert BAR_INTERVAL == timedelta(hours=1)
    assert BAR_INTERVAL_LABEL == "1h"


def test_valid_bar_is_accepted() -> None:
    bar = _hourly(0)
    assert bar.open_time == _ORIGIN
    assert bar.close_time == _ts(1)
    assert bar.interval == BAR_INTERVAL


def test_zero_volume_bar_is_accepted() -> None:
    assert _bar(_ORIGIN, volume=0.0).volume == 0.0


def test_flat_bar_is_accepted() -> None:
    bar = _bar(_ORIGIN, open_=50.0, high=50.0, low=50.0, close=50.0)
    assert bar.high == bar.low == 50.0


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(BarSemanticsError, match="naive"):
        _bar(datetime(2024, 1, 1))


def test_non_utc_offset_is_rejected() -> None:
    moment = datetime(2024, 1, 1, tzinfo=timezone(timedelta(hours=2)))
    with pytest.raises(BarSemanticsError, match="zero UTC offset"):
        _bar(moment)


def test_zero_offset_timezone_is_normalised_to_utc() -> None:
    moment = datetime(2024, 1, 1, tzinfo=timezone(timedelta(0), "GMT"))
    bar = _bar(moment)
    assert moment.tzinfo is not UTC
    assert bar.open_time == _ORIGIN
    assert bar.open_time.tzinfo is UTC


def test_require_utc_reports_the_field_name() -> None:
    with pytest.raises(BarSemanticsError, match="decision_time"):
        require_utc(datetime(2024, 1, 1), field_name="decision_time")


def test_unaligned_open_time_is_rejected() -> None:
    with pytest.raises(BarSemanticsError, match="not aligned"):
        _bar(datetime(2024, 1, 1, 0, 30, tzinfo=UTC))


def test_non_positive_interval_is_rejected() -> None:
    with pytest.raises(BarSemanticsError, match="interval must be positive"):
        _bar(_ORIGIN, interval=timedelta(0))


@pytest.mark.parametrize("price", [0.0, -1.0, float("nan"), float("inf")])
def test_invalid_open_price_is_rejected(price: float) -> None:
    with pytest.raises(BarSemanticsError, match="open must be"):
        _bar(_ORIGIN, open_=price)


@pytest.mark.parametrize("volume", [-0.5, float("nan"), float("inf")])
def test_invalid_volume_is_rejected(volume: float) -> None:
    with pytest.raises(BarSemanticsError, match="volume must be"):
        _bar(_ORIGIN, volume=volume)


def test_high_below_close_is_rejected() -> None:
    with pytest.raises(BarSemanticsError, match="high"):
        _bar(_ORIGIN, high=104.0, close=105.0)


def test_high_below_low_is_rejected() -> None:
    with pytest.raises(BarSemanticsError, match="high"):
        _bar(_ORIGIN, open_=95.0, high=94.0, low=96.0, close=95.0)


def test_low_above_open_is_rejected() -> None:
    with pytest.raises(BarSemanticsError, match="low"):
        _bar(_ORIGIN, open_=100.0, high=110.0, low=101.0, close=105.0)


def test_series_accepts_complete_hourly_bars() -> None:
    series = contiguous_bar_series("TESTUSDT", [_hourly(h) for h in range(4)])
    assert len(series) == 4
    assert series.start == _ORIGIN
    assert series.end == _ts(4)
    assert series.is_contiguous
    assert series.missing_open_times() == ()
    assert series.bar_at(_ts(2)).open == 102.0
    assert series.index_of(_ts(3)) == 3


def test_empty_series_is_rejected() -> None:
    with pytest.raises(BarSemanticsError, match="at least one bar"):
        BarSeries(symbol="TESTUSDT", bars=())


def test_empty_symbol_is_rejected() -> None:
    with pytest.raises(BarSemanticsError, match="symbol"):
        BarSeries(symbol="", bars=(_hourly(0),))


def test_duplicate_open_times_are_rejected() -> None:
    with pytest.raises(BarSemanticsError, match="duplicate open_time"):
        _series((0, 1, 1, 2))


def test_unsorted_bars_are_rejected() -> None:
    with pytest.raises(BarSemanticsError, match="strictly increase"):
        _series((0, 2, 1, 3))


def test_mixed_intervals_are_rejected() -> None:
    bars = (_hourly(0), _bar(_ts(1), interval=timedelta(minutes=30)))
    with pytest.raises(BarSemanticsError, match="has interval"):
        BarSeries(symbol="TESTUSDT", bars=bars)


def test_gap_is_reported_and_never_filled() -> None:
    series = _series((0, 1, 4, 5))
    assert not series.is_contiguous
    assert series.missing_open_times() == (_ts(2), _ts(3))
    assert len(series) == 4
    with pytest.raises(BarSemanticsError, match="missing 2 interval"):
        series.require_contiguous()


def test_contiguous_constructor_rejects_a_gap() -> None:
    with pytest.raises(BarSemanticsError, match="missing 1 interval"):
        contiguous_bar_series("TESTUSDT", [_hourly(0), _hourly(2)])


def test_unknown_open_time_is_rejected() -> None:
    series = _series((0, 1, 2))
    with pytest.raises(BarSemanticsError, match="no bar with open_time"):
        series.bar_at(_ts(9))


def test_decision_at_close_executes_at_next_open() -> None:
    series = _series((0, 1, 2))
    decision_bar = series.bar_at(_ts(1))
    point = series.baseline_execution(decision_bar.close_time)
    assert decision_bar.close_time == _ts(2)
    assert point.decision_time == _ts(2)
    assert point.execution_time == _ts(2)
    assert point.execution_price == series.bar_at(_ts(2)).open
    assert point.execution_price == 102.0
    assert point.execution_price != decision_bar.close


def test_every_decision_uses_only_the_following_bar_open() -> None:
    series = contiguous_bar_series("TESTUSDT", [_hourly(h) for h in range(5)])
    for hour in range(4):
        point = series.baseline_execution(series.bars[hour].close_time)
        assert point.execution_price == series.bars[hour + 1].open


def test_final_bar_close_is_not_executable() -> None:
    series = _series((0, 1, 2))
    with pytest.raises(BarSemanticsError, match="final bar close"):
        series.baseline_execution(_ts(3))


def test_execution_across_a_gap_is_rejected() -> None:
    series = _series((0, 1, 4))
    with pytest.raises(BarSemanticsError, match=r"open\(t\+1\) is missing"):
        series.baseline_execution(_ts(2))


def test_execution_rejects_a_naive_decision_time() -> None:
    series = _series((0, 1, 2))
    with pytest.raises(BarSemanticsError, match="decision_time"):
        series.baseline_execution(datetime(2024, 1, 1, 1))


def test_construction_is_deterministic() -> None:
    first = _series((0, 1, 2))
    second = _series((0, 1, 2))
    assert first == second
    assert first.missing_open_times() == second.missing_open_times()
    left = first.baseline_execution(_ts(1))
    right = second.baseline_execution(_ts(1))
    assert left == right
