"""The §7.2 screen (`calibration/screen.py`), on synthetic data only."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

from aqt.data.bars import Bar, BarSeries
from calibration import screen
from calibration.seeds import sha

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


def _source(n: int = 400) -> screen.HourlySource:
    return screen.joint_bars(
        [
            _series("BTCUSDT", list(range(n)), 1.0),
            _series("ETHUSDT", list(range(n)), 0.1),
        ]
    )


def test_joint_rows_are_the_common_hours_in_time_order() -> None:
    joint = screen.joint_bars(
        [_series("BTCUSDT", [0, 1, 2, 4], 1.0), _series("ETHUSDT", [0, 2, 3, 4], 0.1)]
    )
    bars = joint.bars
    assert list(joint.hour - joint.hour[0]) == [0, 2, 4]
    assert bars.shape == (3, 2, 5)
    assert list(bars[:, 0, screen.VOLUME]) == [10.0, 12.0, 14.0]  # hours 0, 2, 4
    with pytest.raises(ValueError, match="in that order"):
        screen.joint_bars(
            [_series("ETHUSDT", [0, 1], 1.0), _series("BTCUSDT", [0, 1], 1.0)]
        )


def test_reconstruction_chains_opens_and_keeps_each_bars_offsets() -> None:
    src = _source(10).bars
    path = screen.reconstruct(src, np.ones(10))
    assert np.allclose(path[0, :, screen.OPEN], src[0, :, screen.OPEN])
    assert np.allclose(path[1:, :, screen.OPEN], path[:-1, :, screen.CLOSE])
    for k in (screen.HIGH, screen.LOW, screen.CLOSE):
        assert np.allclose(
            path[..., k] / path[..., screen.OPEN], src[..., k] / src[..., screen.OPEN]
        )
    assert np.array_equal(path[..., screen.VOLUME], src[..., screen.VOLUME])


def test_sign_minus_one_mirrors_high_low_and_close() -> None:
    src = _source(4).bars
    signs = np.array([1.0, -1.0, -1.0, 1.0])
    path = screen.reconstruct(src, signs)
    rel = path / path[..., screen.OPEN : screen.OPEN + 1]
    src_rel = src / src[..., screen.OPEN : screen.OPEN + 1]
    assert np.allclose(rel[1, :, screen.HIGH], 1 / src_rel[1, :, screen.LOW])
    assert np.allclose(rel[1, :, screen.LOW], 1 / src_rel[1, :, screen.HIGH])
    assert np.allclose(rel[2, :, screen.CLOSE], 1 / src_rel[2, :, screen.CLOSE])
    assert np.allclose(rel[3, :, screen.CLOSE], src_rel[3, :, screen.CLOSE])


def test_a_block_never_continues_across_a_missing_hour_or_the_end() -> None:
    # S1-R1: hours 0..9 and 11..19 (hour 10 missing for ETH); mean block
    # huge, so every restart is a forced one
    src = screen.joint_bars(
        [
            _series("BTCUSDT", list(range(20)), 1.0),
            _series("ETHUSDT", [h for h in range(20) if h != 10], 0.1),
        ]
    )
    rng = np.random.default_rng(7)
    rows = screen.hourly_indices(rng, src.hour, 5000, 10**9)
    steps = np.diff(rows)
    gap_row = int(np.flatnonzero(np.diff(src.hour) != 1)[0])  # last row before the gap
    after_gap = rows[1:][rows[:-1] == gap_row]
    after_end = rows[1:][rows[:-1] == len(src.hour) - 1]
    assert after_gap.size and after_end.size
    # restarts: uniform over 19 rows, so the next row only by chance
    assert np.mean(after_gap == gap_row + 1) < 0.2 and np.unique(after_gap).size > 10
    assert np.unique(after_end).size > 10
    # without a forced restart, a block runs on
    assert np.all(steps[(rows[:-1] != gap_row) & (rows[:-1] != len(src.hour) - 1)] == 1)


def test_a_path_that_overflows_or_underflows_is_unavailable() -> None:
    # S1-R2: a bar with close 100x open, repeated with sign +1, overflows exp
    bar = np.array([[1.0, 101.0, 1.0, 100.0, 1.0]] * 2)
    sampled = np.repeat(bar[None], 200, axis=0)
    with np.errstate(over="ignore"), pytest.raises(screen.PathUnavailable):
        screen.reconstruct(sampled, np.ones(200))
    with np.errstate(under="ignore"), pytest.raises(screen.PathUnavailable):
        screen.reconstruct(sampled, -np.ones(200))


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
    on the pinned numpy; the float path is exact only on the pinned image
    (SP-6), so here it is compared to 1e-12."""
    src = _source()
    seed = screen.screen_seed("00" * 32)
    draws = hashlib.sha256()
    for p in range(screen.N_PATHS):
        rows, signs = screen.path_draws(src.hour, seed, p, 1000)
        draws.update(rows.astype("<i8").tobytes() + signs.astype("<f8").tobytes())
    assert draws.hexdigest() == REF_DRAWS
    first = screen.null_path(src, seed, 0, 1000)[0, 0]
    assert np.allclose(first, REF_FIRST_BAR, rtol=1e-12, atol=0)


REF_DRAWS = "a9d32c99ac15ab1c8b722b9d09f7b78359b5c3a54cf4297936c81aa47389907a"
REF_FIRST_BAR = [
    477.0044407262295,
    486.5445295407542,
    462.69430750444246,
    481.77429699875876,
    387.0,
]


# --- S3: the trial interface ---------------------------------------------


def _trial(**change: object) -> dict[str, object]:
    t: dict[str, object] = {
        "trial_id": "t000",
        "family": "trend",
        "signal": "calibration.seeds:sha",
        "signal_sha256": "a" * 64,
        "overlay": None,
        "overlay_sha256": None,
        "s_inputs": ["ema_dist_72", "rv_168"],
        "tau": "0.60",
        "sigma": "EWMA_168h",
        "g11_class": "signal_timed",
        "model": None,
        "horizon_hours": 72,
        "parameter_point": {"span": 72},
        "grid": {"span": [24, 72, 168]},
        "warmup_hours": 4800,
    }
    t.update(change)
    return t


def test_the_falsifier_rejects_sigma_hat_and_its_identical_feature_in_s_inputs() -> (
    None
):
    # REG (A), D-20 B5: the identity mapping's falsifier test
    with pytest.raises(screen.TrialError, match="ewma_vol_168h"):
        screen.check_trial(_trial(s_inputs=["ema_dist_72", "ewma_vol_168h"]))
    with pytest.raises(screen.TrialError, match="sigma_hat"):
        screen.check_trial(_trial(s_inputs=["sigma_hat"]))
    vol = {"family": "vol", "sigma": "EWMA_72h"}
    with pytest.raises(screen.TrialError, match="sigma_hat"):
        screen.check_trial(_trial(**vol, s_inputs=["sigma_hat"]))
    # not identical to the sizing estimator: allowed (REG (A) disclosure)
    screen.check_trial(_trial(**vol, s_inputs=["ewma_vol_168h"]))
    screen.check_trial(_trial(s_inputs=["rv_24", "rv_720", "atr_24"]))


def test_s_inputs_are_frozen_features_or_the_trials_own_model() -> None:
    model = {"id": "m1", "class": "ridge", "params": {"alpha": "1.0"}}
    screen.check_trial(_trial(model=model, s_inputs=["model:m1", "ret_24h"]))
    for bad in (["model:m2"], ["volume"], ["ret_24h", "ret_24h"], "ret_24h"):
        with pytest.raises(screen.TrialError):
            screen.check_trial(_trial(model=model, s_inputs=bad))
    with pytest.raises(screen.TrialError):
        screen.check_trial(_trial(s_inputs=["model:m1"]))  # no model declared


@pytest.mark.parametrize(
    "change",
    [
        {"tau": 0.6},
        {"tau": "0.50"},
        {"sigma": "EWMA_72h"},  # only the vol family may choose
        {"family": "vol", "sigma": "EWMA_100h"},
        {"g11_class": "other"},
        {"model": {"id": "m", "class": "mlp", "params": {}}},
        {"model": {"id": "m", "class": "ridge", "params": {"alpha": 1.5}}},
        {"horizon_hours": 48},
        {"horizon_hours": True},
        {"warmup_hours": -1},
        {"parameter_point": {"span": 96}},  # not in the grid
        {"grid": {"span": [24, 72, 72]}},
        {"grid": {"other": [1]}},
        {"signal": "no_colon"},
        {"signal_sha256": "A" * 64},
        {"overlay_sha256": "b" * 64},  # without an overlay
        {"trial_id": ""},
    ],
)
def test_declarations_outside_the_interface_are_refused(
    change: dict[str, object],
) -> None:
    with pytest.raises(screen.TrialError):
        screen.check_trial(_trial(**change))


def test_a_trial_has_exactly_the_interface_fields() -> None:
    t = _trial()
    t["extra"] = 1
    with pytest.raises(screen.TrialError, match="exactly"):
        screen.check_trial(t)
    del t["extra"], t["warmup_hours"]
    with pytest.raises(screen.TrialError, match="exactly"):
        screen.check_trial(t)


def test_the_set_hash_is_ordered_bounded_and_unique() -> None:
    a, b = _trial(), _trial(trial_id="t001", tau="0.40")
    h = screen.trial_set_sha256([a, b])
    assert h == sha({"trials": [screen.trial_sha256(a), screen.trial_sha256(b)]})
    assert h != screen.trial_set_sha256([b, a])
    with pytest.raises(screen.TrialError):
        screen.trial_set_sha256([a, _trial(tau="0.40")])  # repeated trial_id
    with pytest.raises(screen.TrialError):
        screen.trial_set_sha256([])
    many = [_trial(trial_id=f"t{i:03d}") for i in range(screen.MAX_TRIALS + 1)]
    with pytest.raises(screen.TrialError):
        screen.trial_set_sha256(many)


def test_code_loads_only_from_the_declared_source() -> None:
    from calibration import seeds

    good = hashlib.sha256(Path(seeds.__file__).read_bytes()).hexdigest()
    assert screen.load("calibration.seeds:sha", good) is seeds.sha
    with pytest.raises(screen.TrialError, match="declared source"):
        screen.load("calibration.seeds:sha", "0" * 64)
    with pytest.raises(screen.TrialError, match="not a function"):
        screen.load("calibration.seeds:nothing", good)


def test_the_signal_sees_only_its_declared_inputs() -> None:
    available = {n: np.zeros(3) for n in ("ema_dist_72", "rv_168", "ewma_vol_168h")}
    got = screen.signal_inputs(_trial(), available)
    assert set(got) == {"ema_dist_72", "rv_168"}
    with pytest.raises(screen.TrialError, match="not available"):
        screen.signal_inputs(_trial(s_inputs=["ret_1h"]), available)


def test_a_constant_signal_trial_must_be_constant() -> None:
    const = _trial(g11_class="constant_signal")
    assert not screen.class_mismatch(const, np.full(5, 0.3))
    assert screen.class_mismatch(const, np.array([0.3, 0.3, 0.4]))
    assert not screen.class_mismatch(_trial(), np.array([0.3, 0.4]))
