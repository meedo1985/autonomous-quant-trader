"""D-19 semi-empirical market, library-independent parts (prereg §3.4,
engine item 2b). Synthetic bars inside the exploration window only."""

from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from aqt.data.bars import Bar, BarSeries
from aqt.data.manifest import (
    Gap,
    PartitionManifest,
    RawArtifact,
    build_partition_manifest,
    unavailable,
)
from calibration import generator, semi

HOUR = timedelta(hours=1)
START = datetime(2018, 1, 1, tzinfo=UTC)  # inside the exploration window
DAYS = 6


def _series(symbol: str, skip: range = range(0)) -> BarSeries:
    bars = []
    for i in range(DAYS * 24):
        if i in skip:
            continue
        close = 100.0 * math.exp(
            0.01 * math.sin(i / 5.0) + (2 if symbol == "ETHUSDT" else 1) * i * 1e-3
        )
        bars.append(Bar(open_time=START + i * HOUR, open=close, high=close * 1.001,
                        low=close * 0.999, close=close, volume=1.0))  # fmt: skip
    return BarSeries(symbol=symbol, bars=tuple(bars))


def _manifest(series: BarSeries, partition: str = "exploration") -> PartitionManifest:
    end = START + DAYS * 24 * HOUR
    present = {b.open_time for b in series.bars}
    gaps = [Gap(START + i * HOUR, START + (i + 1) * HOUR)
            for i in range(DAYS * 24) if START + i * HOUR not in present]  # fmt: skip
    return build_partition_manifest(
        partition=partition, series=series,
        raw_artifacts=[RawArtifact("synthetic.zip", b"synthetic")],
        parser_code_sha256="0" * 64, window_start_utc=START,
        window_end_exclusive_utc=end, fees=unavailable("synthetic"),
        exchange_filters=unavailable("synthetic"),
        symbol_status=unavailable("synthetic"), gaps=gaps,
    )  # fmt: skip


BTC = _series("BTCUSDT", skip=range(50, 52))  # day 2 incomplete
ETH = _series("ETHUSDT")
SERIES = {"BTCUSDT": BTC, "ETHUSDT": ETH}


def test_daily_closes_keep_only_complete_days() -> None:
    closes = semi.daily_closes(BTC)
    assert sorted(closes) == [
        (START + timedelta(days=d)).date() for d in (0, 1, 3, 4, 5)
    ]
    day0 = closes[START.date()]
    assert day0 == BTC.bars[23].close  # the 23:00 bar


def test_exploration_returns_are_joint_complete_and_demeaned() -> None:
    manifests = {s: _manifest(SERIES[s]) for s in semi.SYMBOLS}
    returns, left_out = semi.exploration_returns(manifests, lambda m: SERIES[m.symbol])
    # days 1..5 have a predecessor; day 2 (incomplete) and day 3 (its
    # predecessor incomplete) are left out: days 1, 4, 5 remain
    assert returns.shape == (3, 2)
    np.testing.assert_allclose(returns.mean(axis=0), 0, atol=1e-15)
    assert left_out == 5 - 3


@pytest.mark.parametrize("bad", ["partition", "symbol", "window", "missing"])
def test_non_exploration_data_is_refused_before_it_is_read(bad: str) -> None:
    manifests = {s: _manifest(SERIES[s]) for s in semi.SYMBOLS}
    if bad == "partition":
        manifests["BTCUSDT"] = _manifest(BTC, partition="confirmation")
    elif bad == "symbol":
        manifests["BTCUSDT"] = manifests["ETHUSDT"]
    elif bad == "window":
        early = START.replace(year=2017, month=1)
        manifests["BTCUSDT"] = _replace_window(manifests["BTCUSDT"], early)
    else:
        del manifests["ETHUSDT"]

    def never(_: PartitionManifest) -> BarSeries:
        raise AssertionError("data was read")

    with pytest.raises(ValueError):
        semi.exploration_returns(manifests, never)


def _replace_window(manifest: PartitionManifest, start: datetime) -> PartitionManifest:
    import dataclasses

    return dataclasses.replace(manifest, window_start_utc=start)


def test_the_stationary_bootstrap_draw_order_and_mean_block() -> None:
    got = semi.stationary_indices(np.random.default_rng(1), 50, 6, 20)
    rng = np.random.default_rng(1)
    expected = [int(rng.integers(50))]
    for _ in range(5):
        expected.append(int(rng.integers(50)) if rng.random() < 1 / 20
                        else (expected[-1] + 1) % 50)  # fmt: skip
    assert got.tolist() == expected
    long = semi.stationary_indices(np.random.default_rng(2), 10_000, 400_000, 20)
    restarts = int(
        np.count_nonzero(np.diff(long) != 1) - np.count_nonzero(np.diff(long) == -9_999)
    )
    assert 400_000 / (restarts + 1) == pytest.approx(20, rel=0.05)


def test_block_signs_are_fair_start_at_day_0_and_have_mean_block_20() -> None:
    rng = np.random.default_rng(3)
    first_sign = 1.0 if np.random.default_rng(3).random() < 0.5 else -1.0
    signs = semi.block_signs(rng, 400_000, 20)
    assert signs[0] == first_sign and set(np.unique(signs)) <= {-1.0, 1.0}
    changes = int(np.count_nonzero(np.diff(signs)))
    # a change happens at a block boundary with probability 1/2
    assert 400_000 / (2 * changes) == pytest.approx(20, rel=0.05)
    assert abs(float(signs.mean())) < 0.03


def test_a_replication_flips_every_column_by_one_shared_sign() -> None:
    """X = s (e - e^b) r with one sign per day for all columns, C = b + X,
    and the warm-up days dropped."""
    source = np.random.default_rng(4).normal(0, 0.03, (500, 2))
    source -= source.mean(axis=0)

    def exposures(path: np.ndarray) -> np.ndarray:
        trend = (np.cumsum(path[:, 0]) > 0).astype(float)
        return np.column_stack([trend, np.full(len(path), 0.5), 1 - trend])

    t, warmup = 300, 50
    legs = semi.semi_empirical(source, exposures, np.random.default_rng(5),
                               np.random.default_rng(6), t, warmup)  # fmt: skip
    path = source[
        semi.stationary_indices(np.random.default_rng(5), 500, t + warmup, 20)
    ]
    e = exposures(path)[warmup:]
    r = path[warmup:, 0]
    e_b = generator.benchmark_exposure(path[:, 0])[warmup:]
    signs = semi.block_signs(np.random.default_rng(6), t, 20)
    np.testing.assert_array_equal(
        legs.x, signs[:, None] * (e - e_b[:, None]) * r[:, None]
    )
    np.testing.assert_array_equal(legs.benchmark, e_b * r)
    np.testing.assert_array_equal(legs.candidates, legs.benchmark[:, None] + legs.x)


def test_exposures_must_cover_every_path_day() -> None:
    source = np.zeros((20, 2))
    with pytest.raises(ValueError, match="one row per path day"):
        semi.semi_empirical(
            source,
            lambda p: np.ones((len(p) - 1, 1)),
            np.random.default_rng(0),
            np.random.default_rng(0),
            5,
            2,
        )
