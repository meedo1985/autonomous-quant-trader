"""D-19 semi-empirical market, library-independent parts (prereg §3.4,
engine item 2b). Synthetic bars inside the exploration window only."""

from __future__ import annotations

import math
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from aqt.data.bars import Bar, BarSeries
from aqt.data.klines import WINDOW_END_EXCLUSIVE, WINDOW_START
from calibration import generator, semi

HOUR = timedelta(hours=1)
START = datetime(2018, 1, 1, tzinfo=UTC)  # inside the exploration window
DAYS = 6
END = START + timedelta(days=DAYS)


def _day(n: int) -> date:
    return (START + timedelta(days=n)).date()


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


BTC = _series("BTCUSDT", skip=range(50, 52))  # day 2 incomplete
ETH = _series("ETHUSDT")


def test_daily_closes_keep_only_complete_days() -> None:
    closes = semi.daily_closes(BTC)
    assert sorted(closes) == [_day(d) for d in (0, 1, 3, 4, 5)]
    assert closes[_day(0)] == BTC.bars[23].close  # the 23:00 bar


@pytest.mark.parametrize(
    ("skip", "kept", "left_out"),
    [
        (range(50, 52), (1, 4, 5), (2, 3)),  # interior: day 2 and its successor
        (range(0, 1), (2, 3, 4, 5), (1,)),  # leading: day 0 incomplete
        (range(5 * 24 + 23, 6 * 24), (1, 2, 3, 4), (5,)),  # trailing: day 5
    ],
)
def test_joint_returns_list_every_left_out_return_day(
    skip: range, kept: tuple[int, ...], left_out: tuple[int, ...]
) -> None:
    btc = _series("BTCUSDT", skip=skip)
    returns, out = semi.joint_returns([btc, ETH], START, END)
    closes = [semi.daily_closes(s) for s in (btc, ETH)]
    raw = np.array([[c[_day(d)] / c[_day(d - 1)] - 1 for c in closes] for d in kept])
    np.testing.assert_allclose(returns, raw - raw.mean(axis=0), rtol=0, atol=1e-15)
    assert out == tuple(_day(d) for d in left_out)
    assert len(returns) + len(out) == DAYS - 1  # every return day accounted


@pytest.mark.parametrize(
    ("series", "start", "end"),
    [
        ([ETH, BTC], START, END),  # symbol order
        ([BTC, ETH], START + HOUR, END),  # not a whole UTC day
        ([BTC, ETH], START.replace(tzinfo=None), END),  # naive
        ([BTC, ETH], START, START + timedelta(days=1)),  # no return day
    ],
)
def test_joint_returns_refuse_a_bad_window_or_order(
    series: list[BarSeries], start: datetime, end: datetime
) -> None:
    with pytest.raises(ValueError):
        semi.joint_returns(series, start, end)


def test_exploration_returns_read_only_through_the_exploration_builder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The only reader is `klines.build_exploration_manifest` (it refuses
    other partitions before reading and keeps only in-window bars; see
    test_klines); the window is the protocol's exploration window."""
    calls = []

    def build(partition: str, symbol: str, root: Path) -> SimpleNamespace:
        calls.append((partition, symbol, root))
        series = {"BTCUSDT": BTC, "ETHUSDT": ETH}[symbol]
        return SimpleNamespace(
            series=series, manifest=SimpleNamespace(manifest_sha256=symbol + "-hash")
        )

    monkeypatch.setattr(semi, "build_exploration_manifest", build)
    root = Path("raw")
    returns, hashes, left_out = semi.exploration_returns(root)
    assert calls == [("exploration", s, root) for s in semi.SYMBOLS]
    assert hashes == ("BTCUSDT-hash", "ETHUSDT-hash")
    return_days = (WINDOW_END_EXCLUSIVE - WINDOW_START).days - 1
    assert returns.shape == (3, 2) and len(left_out) == return_days - 3


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
    """The algebra only: X = s (e - e^b) r with one sign per day for all
    columns, C = b + X, the warm-up days dropped. It reuses the helpers, so
    their draws are checked by the tests below, not here."""
    source = np.random.default_rng(4).normal(0, 0.03, (500, 2))
    source -= source.mean(axis=0)

    def exposures(path: np.ndarray) -> np.ndarray:
        level = np.concatenate([[0.0], np.cumsum(path[:-1, 0])])  # rows < t
        trend = (level > 0).astype(float)
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


def test_pinned_draws_of_the_bootstrap_and_the_signs() -> None:
    """Fixed-seed vectors; a change of numpy's streams or of the draw order
    changes them (independent of the reconstruction tests above)."""
    got = semi.stationary_indices(np.random.default_rng(1), 50, 12, 4)
    assert got.tolist() == [23, 24, 25, 26, 27, 28, 29, 30, 31, 43, 44, 45]
    signs = semi.block_signs(np.random.default_rng(3), 12, 4)
    assert signs.tolist() == [1, 1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1]


class _Scripted:
    """A generator whose uniforms and geometric lengths are given."""

    def __init__(self, uniforms: list[float], lengths: list[int]) -> None:
        self.uniforms, self.lengths = uniforms, lengths
        self.calls: list[str] = []

    def random(self) -> float:
        self.calls.append("random")
        return self.uniforms.pop(0)

    def geometric(self, p: float) -> int:
        self.calls.append(f"geometric({p})")
        return self.lengths.pop(0)


def test_block_signs_draw_sign_then_length_per_block() -> None:
    """Blocks of lengths 2, 3, 1, 4 with signs +, +, -, + (the second
    boundary keeps the sign); the last block is cut at n."""
    rng = _Scripted([0.1, 0.3, 0.7, 0.2], [2, 3, 1, 4])
    signs = semi.block_signs(rng, 8, 20)  # type: ignore[arg-type]
    assert signs.tolist() == [1, 1, 1, 1, 1, -1, 1, 1]
    assert rng.calls == ["random", "geometric(0.05)"] * 4


def test_benchmark_exposure_equals_the_loop_it_replaced() -> None:
    """The loop as it stood in `generate` at 5664f0c, copied verbatim."""
    r = np.random.default_rng(7).standard_t(5, 400) * 0.035
    t = len(r)
    decay = 0.5 ** (1 / 7)
    var_hat, e = generator.SIGMA**2, np.empty(t)
    for i in range(t):
        e[i] = min(1.0, 0.40 / (np.sqrt(var_hat) * np.sqrt(365)))
        var_hat = decay * var_hat + (1 - decay) * r[i] ** 2
    np.testing.assert_array_equal(generator.benchmark_exposure(r), e)
