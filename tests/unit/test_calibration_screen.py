"""The §7.2 screen (`calibration/screen.py`), on synthetic data only."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from aqt.data.bars import Bar, BarSeries
from calibration import screen

START = datetime(2020, 1, 1, tzinfo=UTC)


def _series(symbol: str, hours: list[int], scale: float) -> BarSeries:
    bars = []
    for i in hours:
        o = scale * (100 + i + 0.5 * np.sin(i))
        bars.append(
            Bar(
                START + timedelta(hours=i),
                o,
                o * 1.02,
                o * 0.97,
                o * (1 + 0.01 * np.cos(i)),
                10.0 + i,
            )
        )
    return BarSeries(symbol, tuple(bars))


def _source(n: int = 400) -> np.ndarray:
    return screen.joint_bars(
        [
            _series("BTCUSDT", list(range(n)), 1.0),
            _series("ETHUSDT", list(range(n)), 0.1),
        ]
    )


def test_joint_rows_are_the_common_hours_in_time_order() -> None:
    bars = screen.joint_bars(
        [_series("BTCUSDT", [0, 1, 2, 4], 1.0), _series("ETHUSDT", [0, 2, 3, 4], 0.1)]
    )
    assert bars.shape == (3, 2, 5)
    assert list(bars[:, 0, screen.VOLUME]) == [10.0, 12.0, 14.0]  # hours 0, 2, 4
    with pytest.raises(ValueError, match="in that order"):
        screen.joint_bars(
            [_series("ETHUSDT", [0, 1], 1.0), _series("BTCUSDT", [0, 1], 1.0)]
        )


def test_reconstruction_chains_opens_and_keeps_each_bars_offsets() -> None:
    src = _source(10)
    path = screen.reconstruct(src, np.ones(10))
    assert np.allclose(path[0, :, screen.OPEN], src[0, :, screen.OPEN])
    assert np.allclose(path[1:, :, screen.OPEN], path[:-1, :, screen.CLOSE])
    for k in (screen.HIGH, screen.LOW, screen.CLOSE):
        assert np.allclose(
            path[..., k] / path[..., screen.OPEN], src[..., k] / src[..., screen.OPEN]
        )
    assert np.array_equal(path[..., screen.VOLUME], src[..., screen.VOLUME])


def test_sign_minus_one_mirrors_high_low_and_close() -> None:
    src = _source(4)
    signs = np.array([1.0, -1.0, -1.0, 1.0])
    path = screen.reconstruct(src, signs)
    rel = path / path[..., screen.OPEN : screen.OPEN + 1]
    src_rel = src / src[..., screen.OPEN : screen.OPEN + 1]
    assert np.allclose(rel[1, :, screen.HIGH], 1 / src_rel[1, :, screen.LOW])
    assert np.allclose(rel[1, :, screen.LOW], 1 / src_rel[1, :, screen.HIGH])
    assert np.allclose(rel[2, :, screen.CLOSE], 1 / src_rel[2, :, screen.CLOSE])
    assert np.allclose(rel[3, :, screen.CLOSE], src_rel[3, :, screen.CLOSE])


def test_a_null_path_is_valid_ohlc_with_one_sign_for_both_symbols() -> None:
    src = _source()
    seed = screen.screen_seed("ab" * 32)
    path = screen.null_path(src, seed, 0, 2000)
    assert path.shape == (2000, 2, 5) and np.all(np.isfinite(path))
    o, h, lo, c = (path[..., k] for k in range(4))
    assert np.all(lo <= np.minimum(o, c)) and np.all(np.maximum(o, c) <= h)
    # every source bar has high = 1.02 open, so a bar is unflipped iff its
    # high offset is ln 1.02; one shared sign means BTC and ETH agree
    h_btc = np.isclose(np.log(h[:, 0] / o[:, 0]), np.log(1.02))
    h_eth = np.isclose(np.log(h[:, 1] / o[:, 1]), np.log(1.02))
    assert np.array_equal(h_btc, h_eth) and h_btc.any() and (~h_btc).any()


def test_paths_differ_by_index_and_are_reproducible() -> None:
    src = _source()
    seed = screen.screen_seed("cd" * 32)
    a, b = screen.null_path(src, seed, 0, 500), screen.null_path(src, seed, 1, 500)
    assert not np.array_equal(a, b)
    assert np.array_equal(a, screen.null_path(src, seed, 0, 500))
    assert screen.path_seed(seed, 0) != screen.path_seed(seed, 1)
    with pytest.raises(ValueError):
        screen.null_path(src, seed, screen.N_PATHS, 10)


def test_seeds_follow_the_preregistered_formula() -> None:
    # §7.2: SHA256(cj({"stream": "screen", "trial_set_sha256": <hex>}))
    cj = b'{"stream":"screen","trial_set_sha256":"' + b"ab" * 32 + b'"}'
    assert screen.screen_seed("ab" * 32) == hashlib.sha256(cj).hexdigest()


def test_reference_vectors() -> None:
    """Frozen with screen.py (SCREEN_PLAN S1): a change here is a change to
    the screen's paths and needs review. The draws (rows, signs) are exact
    on every platform; the float path is exact only on the pinned image
    (SP-6), so here it is compared to 1e-12."""
    src = _source()
    seed = screen.screen_seed("00" * 32)
    draws = hashlib.sha256()
    for p in range(screen.N_PATHS):
        rows, signs = screen.path_draws(len(src), seed, p, 1000)
        draws.update(rows.astype("<i8").tobytes() + signs.astype("<f8").tobytes())
    assert draws.hexdigest() == REF_DRAWS
    first = screen.null_path(src, seed, 0, 1000)[0, 0]
    assert np.allclose(first, REF_FIRST_BAR, rtol=1e-12, atol=0)


REF_DRAWS = "a01ffb5c087a485243faca07f449cd5e46f700328ea4091578776aa4fc198080"
REF_FIRST_BAR = [
    477.0044407262295,
    486.5445295407542,
    462.69430750444246,
    481.77429699875876,
    387.0,
]
