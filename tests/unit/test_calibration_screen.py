"""The §7.2 screen (`calibration/screen.py`), on synthetic data only."""

from __future__ import annotations

import functools
import hashlib
import json
import math
import random
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pytest

import aqt.metrics.statistics as st
from aqt.backtest.event_contract import EventResult
from aqt.data.bars import Bar, BarSeries
from aqt.features.columns import feature_columns
from aqt.features.factory import FEATURE_NAMES
from calibration import gap, screen
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


MODEL = {
    "id": "m",
    "class": "ridge",
    "params": {},
    "target": "vol_scaled_target",
    "features": ["ret_24h", "rv_168"],
}


def _trial(**change: object) -> dict[str, object]:
    if change.get("model") is not None:
        change = {"warmup_hours": screen.MODEL_WARMUP_HOURS, **change}
    t: dict[str, object] = {
        "trial_id": "t000",
        "family": "trend",
        "signal": "trial_signal:s",
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
    model = {
        "id": "m1",
        "class": "ridge",
        "params": {"alpha": "1.0"},
        "target": "vol_scaled_target",
        "features": ["ret_24h"],
    }
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
        {"model": {**MODEL, "class": "mlp"}},
        {"model": {**MODEL, "params": {"alpha": 1.5}}},
        {"model": {**MODEL, "params": {1: "1.0"}}},  # S3-R5
        {"model": {"id": "m", "class": "ridge", "params": {}}},  # no target
        {"model": {**MODEL, "class": "logistic"}},  # S3-R3: needs the sign target
        {"model": {**MODEL, "target": "sign_of_vol_scaled_target"}},
        {"family": "fixed_size"},  # S3-R4
        {"family": "other"},
        {"parameter_point": {1: 72}, "grid": {1: [72]}},  # S3-R5
        {"parameter_point": {"tau": "0.40"}, "grid": {"tau": ["0.40"]}},  # S3-R2
        {"parameter_point": {"tau": "0.60"}, "grid": {"tau": ["0.60", "0.70"]}},
        {
            "parameter_point": {"sigma": "EWMA_168h"},
            "grid": {"sigma": ["HAR_RV", "EWMA_168h"]},  # trend: EWMA_168h only
        },
        {"horizon_hours": 48},
        {"horizon_hours": True},
        {"warmup_hours": -1},
        {"parameter_point": {"span": 96}},  # not in the grid
        {"grid": {"span": [24, 72, 72]}},
        {"grid": {"other": [1]}},
        {"signal": "no_colon"},
        {"signal": "calibration.seeds:sha"},  # S3R2-R2: not top-level
        {"overlay": "pkg.mod:f", "overlay_sha256": "b" * 64},
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


def test_code_runs_from_exactly_the_hashed_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # S3-R1: a module imported earlier and then edited must not be used
    import importlib
    import sys

    src = tmp_path / "s3_trial_signal.py"
    src.write_text("def s(inputs, params):\n    return 1\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    old = importlib.import_module("s3_trial_signal")
    src.write_text("def s(inputs, params):\n    return 2\n", encoding="utf-8")
    new = hashlib.sha256(src.read_bytes()).hexdigest()
    fn = screen.load("s3_trial_signal:s", new)
    assert fn({}, {}) == 2 and old.s({}, {}) == 1
    assert sys.modules["s3_trial_signal"] is old  # the loaded module is not registered
    with pytest.raises(screen.TrialError, match="declared source"):
        screen.load("s3_trial_signal:s", "0" * 64)
    with pytest.raises(screen.TrialError, match="not a function"):
        screen.load("s3_trial_signal:nothing", new)
    del sys.modules["s3_trial_signal"]


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("import os\n", "imports"),
        ("from calibration import seeds\n", "imports"),
        ("from . import x\n", "relative"),
        ("import numpy as np\nimport math\nla = np.linalg\n", None),
        ("import numpy.linalg as la\n", "imports"),  # S3R4-R1: no submodule
        ("from numpy.lib.format import open_memmap\n", "imports"),
        ("x = __import__('os')\n", "uses"),
        ("import numpy as np\nf = np.load\n", "uses"),
        ("g = open\n", "uses"),
        ("from numpy import load\n", "imports"),  # S3R2-R1
        ("from numpy import f2py\n", "imports"),  # S3R5-R1
        ("from math import sqrt\n", "imports"),
        ("from __future__ import annotations\nimport numpy as np\n", None),
        ("import numpy as np\nx = np.f2py\n", "uses"),
        ("import numpy as np\nx = np.testing\n", "uses"),
        ("from numpy import *\n", "import"),
        ("import numpy as np\nx = np.lib.npyio\n", "uses"),
        ("import numpy as np\nx = np.fromfile\n", "uses"),
        ("def s(:\n", "parse"),
    ],
)
def test_trial_code_is_self_contained(code: str, message: str | None) -> None:
    # S3R-R1: only math and numpy; no dynamic import, exec or file access
    if message is None:
        screen.check_code(code.encode(), "m")
    else:
        with pytest.raises(screen.TrialError, match=message):
            screen.check_code(code.encode(), "m")


@pytest.mark.parametrize(
    "body",
    [
        "return float(input())",
        "return print(1)",
        "return getattr(inputs, 'x')",
        "return globals()",
        "return __import__('os')",
        "import os\n    return os",
        "from numpy.lib import format\n    return format",
        "import numpy.linalg\n    return numpy",
        "from numpy import f2py\n    return f2py",
    ],
)
def test_trial_code_runs_with_pure_builtins_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str
) -> None:
    # S3R3-R1: names the static check might miss fail at run time
    src = tmp_path / "s3_pure.py"
    src.write_text(
        f"import math\nimport numpy as np\n\ndef s(inputs, params):\n    {body}\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    try:
        fn = screen.load("s3_pure:s", digest)
    except screen.TrialError:
        return  # refused statically
    with pytest.raises((NameError, ImportError)):
        fn({}, {})


def test_honest_trial_code_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = tmp_path / "s3_honest.py"
    src.write_text(
        "import math\nimport numpy as np\n\n"
        "class Scale:\n"
        "    def __init__(self, k):\n"
        "        self.k = k\n\n"
        "def s(inputs, params):\n"
        "    x = np.asarray(inputs['ema_dist_72'], dtype=float)\n"
        "    k = Scale(math.sqrt(params['k'])).k\n"
        "    return np.maximum(0.0, np.sign(x)) * k\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    fn = screen.load("s3_honest:s", hashlib.sha256(src.read_bytes()).hexdigest())
    out = fn({"ema_dist_72": [-1.0, 2.0]}, {"k": 4})
    assert out.tolist() == [0.0, 2.0]


def test_a_package_module_is_refused() -> None:
    # S3R-R1: a dotted module would run its package __init__ first
    with pytest.raises(screen.TrialError, match="top-level"):
        screen.load("calibration.seeds:sha", "0" * 64)


def test_sizing_dimensions_are_bound_and_kept_from_the_signal() -> None:
    t = _trial(
        parameter_point={"span": 72, "tau": "0.60"},
        grid={"span": [24, 72], "tau": ["0.40", "0.60", "0.80"]},
    )
    screen.check_trial(t)
    assert screen.signal_params(t) == {"span": 72}
    vol = _trial(
        family="vol",
        sigma="HAR_RV",
        parameter_point={"sigma": "HAR_RV"},
        grid={"sigma": ["EWMA_72h", "HAR_RV"]},
    )
    screen.check_trial(vol)
    assert screen.signal_params(vol) == {}
    with pytest.raises(screen.TrialError, match="the point = sigma"):
        screen.check_trial({**vol, "sigma": "EWMA_72h"})  # point != top-level


def test_model_hyperparameters_enter_the_grid_only_as_model_dimensions() -> None:
    # S3R-R2
    model = {**MODEL, "params": {"alpha": "1"}}
    t = _trial(
        model=model,
        parameter_point={"span": 72, "model.alpha": "1"},
        grid={"span": [24, 72], "model.alpha": ["0.1", "1", "10"]},
    )
    screen.check_trial(t)
    assert screen.signal_params(t) == {"span": 72}
    assert screen.model_params(t) == {"alpha": "1"}
    neighbour = {**t, "parameter_point": {"span": 72, "model.alpha": "10"}}
    assert screen.model_params(neighbour) == {"alpha": "10"}
    for point, grid in (
        ({"alpha": "10"}, {"alpha": ["10"]}),  # plain name shadows a model param
        ({"model.alpha": "10"}, {"model.alpha": ["10"]}),  # differs from params
        ({"model.beta": "1"}, {"model.beta": ["1"]}),  # not a model param
    ):
        with pytest.raises(screen.TrialError):
            screen.check_trial(_trial(model=model, parameter_point=point, grid=grid))
    with pytest.raises(screen.TrialError):
        screen.check_trial(
            _trial(parameter_point={"model.alpha": "1"}, grid={"model.alpha": ["1"]})
        )
    flag = {**MODEL, "params": {"fit_intercept": True}}  # S3R2-R3: True is not 1
    with pytest.raises(screen.TrialError):
        screen.check_trial(
            _trial(
                model=flag,
                parameter_point={"model.fit_intercept": 1},
                grid={"model.fit_intercept": [1, 0]},
            )
        )


def test_g14_applies_to_model_trials_only() -> None:
    logit = {**MODEL, "class": "logistic", "target": "sign_of_vol_scaled_target"}
    screen.check_trial(_trial(model=logit))
    assert screen.g14_applies(_trial(model=logit))  # owner decision S3R-R3
    assert screen.g14_applies(_trial(model=MODEL))
    assert not screen.g14_applies(_trial())


def test_the_overlay_may_only_keep_the_target_or_exit() -> None:
    target = np.array([0.3, 0.5, 0.0, 0.7])
    assert not screen.overlay_violation(target, np.array([0.3, 0.0, 0.0, 0.7]))
    assert screen.overlay_violation(target, np.array([0.15, 0.5, 0.0, 0.7]))
    assert screen.overlay_violation(target, np.array([0.3, 0.5, 0.2, 0.7]))
    assert screen.overlay_violation(target, target[:3])


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


# --- S5: G-11 shifts -------------------------------------------------------

WINDOW = '["2022-01-01T00:00:00Z","2025-06-01T00:00:00Z"]'


def test_g11_seed_follows_the_annex_formula() -> None:
    # C-10 (3): json.dumps([SEED_DOMAIN, trial_seed, convention hash,
    # "random_exposure_null", "BTCUSDT", "1.0", window id, 500])
    material = (
        '["aqt.statistics.stream.v1","' + "ab" * 32 + '",'
        '"f3ba9362c5f1512fd24600775df2aa048a7e701c8f40c8cb00e97c2c644f515c",'
        '"random_exposure_null","BTCUSDT","1.0",' + json.dumps(WINDOW) + ",500]"
    )
    assert (
        screen.g11_seed("ab" * 32, WINDOW)
        == hashlib.sha256(material.encode()).hexdigest()
    )


def test_screen_trial_seed_follows_the_annex_formula() -> None:
    # C-10 (3) "Inside the D-19 screen"
    seed = screen.screen_seed("00" * 32)
    cj = '{"path":3,"screen_seed":"' + seed + '","trial_id":"t007"}'
    assert (
        screen.screen_trial_seed(seed, 3, "t007")
        == hashlib.sha256(cj.encode()).hexdigest()
    )


def test_g11_shifts_are_500_distinct_days_inside_the_range() -> None:
    for t_days, g in ((1247, 30), (1247, 45), (1059, 30)):
        k = screen.g11_shifts("cd" * 32, WINDOW, t_days, g)
        m = max(g, 30)
        assert len(k) == 500 == len(set(k))
        assert min(k) >= m and max(k) <= t_days - m
    # the floor: g below 30 uses m = 30
    assert screen.g11_shifts("cd" * 32, WINDOW, 1247, 5) == screen.g11_shifts(
        "cd" * 32, WINDOW, 1247, 30
    )


def test_g11_is_unavailable_below_the_shift_range() -> None:
    # T - 2m >= 499: m = 30 needs T >= 559
    assert len(screen.g11_shifts("cd" * 32, WINDOW, 559, 30)) == 500
    k = screen.g11_shifts("cd" * 32, WINDOW, 559, 30)
    assert sorted(k) == list(range(30, 530))  # every value of P is used
    with pytest.raises(screen.GateUnavailable) as e:
        screen.g11_shifts("cd" * 32, WINDOW, 558, 30)
    assert (e.value.gate, e.value.reason) == ("G-11", "INSUFFICIENT_SHIFT_RANGE")
    # S5-R1: the boundary moves with g (m = 45 needs T >= 589)
    assert len(screen.g11_shifts("cd" * 32, WINDOW, 589, 45)) == 500
    with pytest.raises(screen.GateUnavailable):
        screen.g11_shifts("cd" * 32, WINDOW, 588, 45)


def test_g11_partial_fisher_yates_matches_an_independent_draw() -> None:
    import random

    seed = screen.g11_seed("ef" * 32, WINDOW)
    rng = random.Random(int.from_bytes(bytes.fromhex(seed), "big"))
    pool = list(range(30, 1247 - 30 + 1))
    out = []
    for i in range(500):
        n = len(pool) - i
        while (r := rng.getrandbits(n.bit_length())) >= n:
            pass
        pool[i], pool[i + r] = pool[i + r], pool[i]
        out.append(pool[i])
    assert screen.g11_shifts("ef" * 32, WINDOW, 1247, 30) == out


def test_g11_reference_vectors() -> None:
    """Frozen with screen.py (C-10 (3), GS-5): exact on every CPython."""
    k = screen.g11_shifts("ab" * 32, WINDOW, 1247, 30)
    assert k[:10] == [1008, 180, 1182, 403, 592, 827, 352, 109, 479, 1142]
    assert screen.g11_shifts_sha256(k) == (
        "a63398708b99fbd5f0f5c8cee5f497ae79fab2a2b1bfee0c53577fac82bce911"
    )


# --- S4b: trial runs and G-3, G-5, G-6, G-7 --------------------------------

W0 = datetime(2022, 1, 1, tzinfo=UTC)
WINDOW_H = 24 * 30
NULL_STREAM = (
    screen.screen_trial_seed(screen.screen_seed("33" * 32), 0, "t000"),
    WINDOW,
    30,  # g days
)


def _module(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, code: str
) -> str:
    src = tmp_path / f"{name}.py"
    src.write_text(code, encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    return hashlib.sha256(src.read_bytes()).hexdigest()


TREND = (
    "def s(row, params, state):\n"
    "    assert set(row) == {'ema_dist_168', 'rv_168'}\n"
    "    state['n'] = state.get('n', 0) + 1\n"
    "    return 0.6 if row['ema_dist_168'] > 0 else 0.1\n"
)


def _screen_trial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, code: str = TREND, **change: object
) -> dict[str, object]:
    digest = _module(tmp_path, monkeypatch, "s4b_signal", code)
    fields: dict[str, object] = {
        "signal": "s4b_signal:s",
        "signal_sha256": digest,
        "s_inputs": ["ema_dist_168", "rv_168"],
        "warmup_hours": 4801,
        "parameter_point": {},
        "grid": {},
    }
    return _trial(**{**fields, **change})


def _screen_path(warmup: int = 4801) -> np.ndarray:
    seed = screen.screen_seed("11" * 32)
    return screen.null_path(_source(), seed, 0, warmup + WINDOW_H + 1)


def test_an_honest_trial_has_every_s4b_gate_available(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = _screen_trial(tmp_path, monkeypatch)
    got = screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)
    assert got == {
        **dict.fromkeys(screen.GATES_S4B, None),
        "G-8": screen.NA,
        "G-11": "INSUFFICIENT_SHIFT_RANGE",
        "G-14": screen.NA,
    }


def test_a_flat_candidate_makes_e_improv_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # s = 0 always: zero exposure, zero daily returns, no Sharpe
    code = "def s(row, params, state):\n    return 0.0\n"
    trial = _screen_trial(tmp_path, monkeypatch, code)
    got = screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)
    assert got["G-3"] == "ZERO_VARIANCE"
    assert got["G-5"] == got["G-6"] == got["G-7"] == "ZERO_VARIANCE"


@pytest.mark.parametrize(
    ("code", "reason"),
    [
        ("def s(row, params, state):\n    return float('nan')\n", "INVALID_SERIES"),
        ("def s(row, params, state):\n    return row['ret_1h']\n", "TRIAL_CODE_ERROR"),
        ("def s(row, params, state):\n    return 1 / 0\n", "TRIAL_CODE_ERROR"),
    ],
)
def test_bad_trial_code_makes_every_run_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, code: str, reason: str
) -> None:
    # an undeclared input is simply absent from the row (C-10 (1))
    trial = _screen_trial(tmp_path, monkeypatch, code)
    got = screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)
    assert set(got.values()) == {reason, screen.NA}  # G-8: no dimension


def test_an_overlay_that_rescales_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    o = _module(
        tmp_path, monkeypatch, "s4b_overlay", "def o(t, m, state):\n    return t / 2\n"
    )
    trial = _screen_trial(
        tmp_path, monkeypatch, overlay="s4b_overlay:o", overlay_sha256=o
    )
    got = screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)
    assert set(got.values()) == {"OVERLAY_VIOLATION", screen.NA}
    ok = _module(
        tmp_path,
        monkeypatch,
        "s4b_exit",
        "def o(t, m, state):\n    return 0.0 if m['ret_24h'] < -0.05 else t\n",
    )
    trial = _screen_trial(
        tmp_path, monkeypatch, overlay="s4b_exit:o", overlay_sha256=ok
    )
    assert (
        screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)["G-3"]
        is None
    )


def test_feature_delay_needs_one_more_hour_of_warmup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # decisions read bar j - 1 (needs j0 >= 4800); G-6 reads j - 2
    trial = _screen_trial(tmp_path, monkeypatch, warmup_hours=4800)
    got = screen.screen_gates(trial, _screen_path(4800), W0, WINDOW_H, *NULL_STREAM)
    assert got == {
        "G-3": None,
        "G-5": None,
        "G-6": "INSUFFICIENT_WARMUP",
        "G-7": None,
        "G-8": screen.NA,
        "G-11": "INSUFFICIENT_SHIFT_RANGE",
        "G-14": screen.NA,
    }


def test_model_and_unbound_sizing_trials_wait_for_their_slices(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # MR-4: a model trial's warm-up must hold its first training window
    trial = _screen_trial(
        tmp_path, monkeypatch, model=MODEL, s_inputs=["model:m", "ema_dist_168"]
    )
    with pytest.raises(screen.TrialError, match="model trial needs warmup_hours"):
        screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)
    trial = _screen_trial(tmp_path, monkeypatch, family="vol", sigma="HAR_RV")
    got = screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)
    assert got == {
        **dict.fromkeys(screen.GATES_S4B, "SIGMA_UNBOUND"),
        "G-8": screen.NA,
        "G-11": "SIGMA_UNBOUND",
        "G-14": screen.NA,
    }
    # S4C-R1: with a numeric dimension, G-8 waits like the others
    trial = _screen_trial(
        tmp_path,
        monkeypatch,
        family="vol",
        sigma="HAR_RV",
        parameter_point={"k": 1},
        grid={"k": [1, 2]},
    )
    assert (
        screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)["G-8"]
        == "SIGMA_UNBOUND"
    )


def test_the_lagged_candidate_reads_the_previous_row() -> None:
    # G-6: the row of bar j - 2; the decision without lag reads bar j - 1
    cols = {n: tuple(float(i) for i in range(10)) for n in FEATURE_NAMES}
    cols["ewma_vol_168h"] = (0.5,) * 10
    seen: list[float] = []

    def sig(row: dict[str, float], params: object, state: object) -> float:
        seen.append(row["ema_dist_168"])
        return 0.1

    trial = {**_trial(s_inputs=["ema_dist_168"]), "parameter_point": {}, "grid": {}}
    closes = [1.0] * 12
    screen.leg_targets(trial, sig, None, cols, 2, closes, 5, 2, 0)
    screen.leg_targets(trial, sig, None, cols, 2, closes, 5, 2, 1)
    assert seen == [2.0, 3.0, 1.0, 2.0]  # rows of bars 4, 5 then 3, 4


def test_a_non_finite_input_is_unavailable_even_if_the_signal_ignores_it() -> None:
    # S4B-R4 (C-7 (2)): bar 1's row holds a NaN in a declared input
    cols = {n: tuple(float(i) for i in range(10)) for n in FEATURE_NAMES}
    cols["ewma_vol_168h"] = (0.5,) * 10
    cols["rv_168"] = (1.0, float("nan")) + (1.0,) * 8
    trial = {
        **_trial(s_inputs=["ema_dist_168", "rv_168"]),
        "parameter_point": {},
        "grid": {},
    }

    def sig(row: dict[str, float], params: object, state: object) -> float:
        return 0.1  # never reads rv_168

    closes = [1.0] * 12
    screen.leg_targets(trial, sig, None, cols, 0, closes, 4, 2, 0)  # bars 3, 4
    with pytest.raises(screen.RunUnavailable, match="INVALID_SERIES"):
        screen.leg_targets(trial, sig, None, cols, 0, closes, 2, 2, 0)  # reads bar 1


def test_daily_returns_run_from_midnight_to_midnight() -> None:
    eq = tuple(1.0 + 0.01 * (i // 24) for i in range(1, 49))  # flat within days
    result = EventResult(0, (0.0,) * 48, eq, (), 0)
    got = screen.daily_returns(result)
    assert got == pytest.approx([eq[23] - 1.0, eq[47] / eq[23] - 1.0])


def test_the_path_must_cover_warmup_window_and_one_hour(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = _screen_trial(tmp_path, monkeypatch)
    with pytest.raises(screen.TrialError, match="path length"):
        screen.screen_gates(trial, _screen_path()[:-1], W0, WINDOW_H, *NULL_STREAM)


def test_trial_code_state_never_crosses_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # S4B-R1: a module global counting calls would exceed one window if the
    # module were shared between runs (and could then cache future rows)
    code = (
        "CALLS = []\n"
        "def s(row, params, state):\n"
        f"    if len(CALLS) >= {WINDOW_H}:\n"
        "        raise ValueError('state crossed runs')\n"
        "    CALLS.append(row['ema_dist_168'])\n"
        "    return 0.6 if row['ema_dist_168'] > 0 else 0.1\n"
    )
    trial = _screen_trial(tmp_path, monkeypatch, code)
    got = screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)
    assert got == {
        **dict.fromkeys(screen.GATES_S4B, None),
        "G-8": screen.NA,
        "G-11": "INSUFFICIENT_SHIFT_RANGE",
        "G-14": screen.NA,
    }


def test_a_negative_signal_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # S4B-R2 (C-10 (1)): s >= 0; clipping would hide it
    code = "def s(row, params, state):\n    return row['ema_dist_168']\n"
    trial = _screen_trial(tmp_path, monkeypatch, code)
    got = screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)
    assert set(got.values()) == {"NEGATIVE_SIGNAL", screen.NA}


def test_a_constant_signal_trial_is_checked_every_hour(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # S4B-R3 (C-10 (2))
    trial = _screen_trial(tmp_path, monkeypatch, g11_class="constant_signal")
    got = screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)
    assert got["G-11"] == "CLASS_MISMATCH"
    code = "def s(row, params, state):\n    return 0.5\n"
    trial = _screen_trial(tmp_path, monkeypatch, code, g11_class="constant_signal")
    got = screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)
    assert got["G-11"] == screen.NA and got["G-3"] is None


def test_an_unavailable_eth_check_carries_into_the_btc_gates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # ETH flat: sigma_hat = 0, so the ETH run is unavailable while BTC runs work
    path = _screen_path().copy()
    path[:, 1, :4] = 100.0
    trial = _screen_trial(tmp_path, monkeypatch)
    got = screen.screen_gates(trial, path, W0, WINDOW_H, *NULL_STREAM)
    assert got["G-3"] == "INVALID_SERIES"
    assert got["G-5"] == got["G-6"] == got["G-7"] == "G-3:INVALID_SERIES"


# --- S4c: G-8 --------------------------------------------------------------


def test_plateau_dimensions_are_numeric_non_structural_and_ordered_by_value() -> None:
    # PL-1, PL-2 (owner decision: rule settings count)
    t = _trial(
        family="vol",
        sigma="EWMA_168h",
        model={**MODEL, "params": {"alpha": "1"}},
        parameter_point={
            "k": 72,
            "mode": "a",
            "model.alpha": "1",
            "tau": "0.60",
            "sigma": "EWMA_168h",
        },
        grid={
            "k": [168, 24, 72],
            "mode": ["a", "b"],
            "model.alpha": ["10", "0.1", "1"],
            "tau": ["0.40", "0.60"],
            "sigma": ["EWMA_168h", "HAR_RV"],
        },
    )
    screen.check_trial(t)
    assert screen.plateau_dimensions(t) == {
        "k": [24, 72, 168],
        "model.alpha": ["0.1", "1", "10"],
    }
    with pytest.raises(screen.TrialError, match="repeats a number"):
        screen.plateau_dimensions(
            _trial(parameter_point={"k": 1}, grid={"k": [1, "1.0"]})
        )
    # S4C-R3: a single value is a fixed constant, not a dimension
    assert (
        screen.plateau_dimensions(_trial(parameter_point={"k": 5}, grid={"k": [5]}))
        == {}
    )


def test_plateau_neighbours_move_one_dimension_one_step() -> None:
    t = _trial(
        model={**MODEL, "params": {"alpha": "1"}},
        parameter_point={"k": 24, "model.alpha": "1"},
        grid={"k": [24, 72, 168], "model.alpha": ["0.1", "1", "10"]},
    )
    got = [
        (n["parameter_point"], n["model"]["params"])
        for n in screen.plateau_neighbours(t)
    ]
    assert got == [
        ({"k": 72, "model.alpha": "1"}, {"alpha": "1"}),  # k at the edge: one side
        ({"k": 24, "model.alpha": "0.1"}, {"alpha": "0.1"}),
        ({"k": 24, "model.alpha": "10"}, {"alpha": "10"}),
    ]
    for n in screen.plateau_neighbours(t):
        screen.check_trial(n)  # every neighbour is a valid declaration


PARAM_SIGNAL = (
    "def s(row, params, state):\n"
    "    if params['k'] == 10:\n"
    "        return float('nan')\n"
    "    return 0.6 if row['ema_dist_168'] > params['k'] / 1000 else 0.1\n"
)


def test_g8_runs_the_point_and_every_neighbour(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = _screen_trial(
        tmp_path,
        monkeypatch,
        PARAM_SIGNAL,
        parameter_point={"k": 0},
        grid={"k": [0, 5]},
    )
    assert (
        screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)["G-8"]
        is None
    )
    # the neighbour k = 10 cannot be computed: G-8 unavailable, the point's
    # own gates unaffected
    trial = _screen_trial(
        tmp_path,
        monkeypatch,
        PARAM_SIGNAL,
        parameter_point={"k": 5},
        grid={"k": [0, 5, 10]},
    )
    got = screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)
    assert got["G-8"] == "INVALID_SERIES"
    assert all(got[g] is None for g in screen.GATES_S4B)
    # the selected point itself failing makes every gate unavailable
    trial = _screen_trial(
        tmp_path,
        monkeypatch,
        PARAM_SIGNAL,
        parameter_point={"k": 10},
        grid={"k": [5, 10]},
    )
    got = screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)
    assert set(got.values()) == {"INVALID_SERIES", screen.NA}  # G-14: no model


def test_a_non_finite_e_improv_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    # S4C-R2: C-8 step 2 (defence in depth: the R-8 code returns None today)
    fake = st.PairedSharpeStatistics(
        candidate=st.SharpeResult(2),
        benchmark=st.SharpeResult(2),
        difference_series_sharpe=st.SharpeResult(2),
        paired_sharpe_improvement=float("nan"),
        reason=None,
    )
    monkeypatch.setattr(st, "paired_sharpe_statistics", lambda c, b: fake)
    result = EventResult(0, (0.0,) * 48, tuple(1.0 for _ in range(48)), (), 0)
    with pytest.raises(screen.RunUnavailable, match="E_IMPROV_UNAVAILABLE"):
        screen.leg_stats(result, result)


def test_g8_is_na_without_an_ordered_numeric_dimension(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = _screen_trial(
        tmp_path, monkeypatch, parameter_point={"mode": "a"}, grid={"mode": ["a", "b"]}
    )
    assert (
        screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)["G-8"]
        == screen.NA
    )


# --- S6a: walk-forward pieces ----------------------------------------------


@pytest.mark.parametrize(
    ("cls", "params"),
    [
        ("lightgbm", {"max_depth": -1}),  # S6D-R3: "no limit" is out of range
        ("lightgbm", {"max_depth": 4}),
        ("lightgbm", {"num_leaves": 9}),
        ("lightgbm", {"n_estimators": 301}),
        ("lightgbm", {"min_data_in_leaf": 5}),  # an alias of min_child_samples
        ("lightgbm", {"learning_rate": "0.1"}),  # fixed, not declarable
        ("ridge", {"alpha": "0"}),
        ("ridge", {"alpha": 1}),  # decimals are strings
        ("logistic", {"C": "-1"}),
        ("elastic_net", {"l1_ratio": "1.5"}),
        ("linear", {"fit_intercept": 1}),
        ("linear", {"random_state": 3}),
    ],
)
def test_model_parameters_outside_the_allowlist_are_refused(
    cls: str, params: dict[str, object]
) -> None:
    target = "sign_of_vol_scaled_target" if cls == "logistic" else "vol_scaled_target"
    model = {**MODEL, "class": cls, "params": params, "target": target}
    with pytest.raises(screen.TrialError):
        screen.check_trial(_trial(model=model))


def test_a_model_trial_needs_its_training_window_as_warm_up() -> None:
    # S6A-R1, WF-2: refused at declaration
    with pytest.raises(screen.TrialError, match="model trial needs warmup_hours"):
        screen.check_trial(_trial(model=MODEL, warmup_hours=0))
    screen.check_trial(_trial(model=MODEL, warmup_hours=screen.MODEL_WARMUP_HOURS))


def test_allowed_model_parameters_and_grids_pass() -> None:
    lgbm = {
        **MODEL,
        "class": "lightgbm",
        "params": {"max_depth": 3, "num_leaves": 8, "n_estimators": 300},
    }
    screen.check_trial(_trial(model=lgbm))
    t = _trial(
        model=lgbm,
        parameter_point={"model.max_depth": 3},
        grid={"model.max_depth": [1, 2, 3]},
    )
    screen.check_trial(t)
    with pytest.raises(screen.TrialError, match="above its range"):
        screen.check_trial(
            {**t, "grid": {"model.max_depth": [2, 3, 4]}}  # a neighbour out of range
        )


def test_model_features_obey_the_sizing_ban() -> None:
    # owner decision WF-4; S6A-R4: a non-name is a TrialError, not a TypeError
    cases: list[object] = [
        ["ewma_vol_168h"],
        ["sigma_hat"],
        ["volume"],
        [],
        ["rv_24", "rv_24"],
        [[]],
    ]
    for bad in cases:
        with pytest.raises(screen.TrialError):
            screen.check_trial(_trial(model={**MODEL, "features": bad}))
    vol = {"family": "vol", "sigma": "EWMA_72h"}
    screen.check_trial(_trial(**vol, model={**MODEL, "features": ["ewma_vol_168h"]}))


def test_training_windows_are_calendar_months() -> None:
    # WF-2 (S6D-R2)
    t = datetime(2024, 3, 31, tzinfo=UTC)
    assert screen.months_before(t, 1) == datetime(2024, 2, 29, tzinfo=UTC)
    assert screen.months_before(t, 24) == datetime(2022, 3, 31, tzinfo=UTC)
    assert screen.months_before(datetime(2024, 2, 29, tzinfo=UTC), 12) == datetime(
        2023, 2, 28, tzinfo=UTC
    )
    assert screen.months_before(datetime(2022, 1, 1, tzinfo=UTC), 24) == datetime(
        2020, 1, 1, tzinfo=UTC
    )


def test_refits_every_30_days_from_w0() -> None:
    w0 = datetime(2022, 1, 31, tzinfo=UTC)
    got = screen.refit_instants(w0, w0 + timedelta(days=1247))
    assert len(got) == 42 and got[0] == w0 and got[1] == w0 + timedelta(days=30)


def test_labels_follow_the_protocol_formula() -> None:
    # WF-1: log(P[t+H] / P[t]) / (sigma_t * sqrt(H)), sigma from the cost model
    from aqt.backtest.costs import (
        ewma_hourly_volatility_bps_series,
        hourly_log_returns_bps,
    )

    series = _series("BTCUSDT", list(range(300)), 1.0)
    sigma = ewma_hourly_volatility_bps_series(hourly_log_returns_bps(series))
    got = screen.labels(series, sigma, [100, 124], 24)
    bars = series.bars
    for j, y in zip([100, 124], got, strict=True):
        want = math.log(bars[j - 1 + 24].close / bars[j - 1].close) / (
            sigma[j - 3] / 1e4 * math.sqrt(24)
        )
        assert y == want
    with pytest.raises(screen.RunUnavailable, match="INVALID_SERIES"):
        screen.labels(series, [0.0] * len(sigma), [100], 24)
    # S6A-R3: an instant before sigma exists never wraps to the series' end
    with pytest.raises(screen.RunUnavailable, match="INSUFFICIENT_HISTORY"):
        screen.labels(series, sigma, [2], 24)
    with pytest.raises(screen.RunUnavailable, match="INSUFFICIENT_HISTORY"):
        screen.labels(series, sigma, [290], 24)  # P[t+H] beyond the series


def test_the_embargo_is_the_frozen_acf_cutoff_or_the_horizon() -> None:
    # WF-3 (S6D-R1): the frozen rule (gap.py's ACF cutoff), never below H
    rng = random.Random(4)
    noise = [rng.gauss(0, 1) for _ in range(700)]
    want = max(7, gap.cutoff(gap.acf(list(noise), 28), 700))
    assert screen.embargo_days(noise, 7) == want >= 7
    # S6A-R2: missing calendar days stay as gaps, as in gap.py
    gapped: list[float | None] = [
        v if i % 2 == 0 else None for i, v in enumerate(noise)
    ]
    want = max(1, gap.cutoff(gap.acf(gapped, 4), 350))
    assert screen.embargo_days(gapped, 1) == want
    # strongly persistent labels: the cutoff exceeds the horizon
    walk, x = [], 0.0
    for _ in range(700):
        x = 0.98 * x + rng.gauss(0, 1)
        walk.append(x)
    assert screen.embargo_days(walk, 1) > 1
    with pytest.raises(screen.RunUnavailable, match="EMBARGO_UNDEFINED"):
        screen.embargo_days(noise[:28], 7)  # no more rows than lags


def test_training_rows_follow_the_boundary_example(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # WF-3: E = 12 days, refit at 00:00 on day 100: day 88 kept, day 89 not
    monkeypatch.setattr(screen, "embargo_days", lambda ys, h: 12)
    day0 = datetime(2024, 1, 1, tzinfo=UTC)
    decisions = [day0 + timedelta(days=d) for d in range(101)]
    refit = day0 + timedelta(days=100)
    kept = screen.training_rows(decisions, [0.0] * 101, refit, 168)
    assert kept[-1] == 88 and 89 not in kept
    # the window starts 24 calendar months back (all of these are inside)
    assert kept[0] == 0


def test_every_model_class_fits_reproducibly() -> None:
    # WF-5: one library pipeline per class; same data and seed, same output
    rng = np.random.default_rng(0)
    x = rng.normal(size=(200, 3))
    y = x @ np.array([0.5, -0.2, 0.1]) + rng.normal(scale=0.5, size=200)
    for cls, params in (
        ("linear", {"fit_intercept": True}),
        ("ridge", {"alpha": "1.0"}),
        ("lasso", {"alpha": "0.01"}),
        ("elastic_net", {"alpha": "0.01", "l1_ratio": "0.5"}),
        ("logistic", {"C": "1.0"}),
        ("lightgbm", {"n_estimators": 50, "max_depth": 3, "num_leaves": 8}),
    ):
        target = screen.fit_target(cls, list(y))
        runs = []
        for _ in range(2):
            model = screen.build_model(cls, params, seed=7)
            model.fit(x, target)
            runs.append(screen.predict(model, cls, x))
        assert np.array_equal(runs[0], runs[1]), cls
        assert np.all(np.isfinite(runs[0])), cls
        if cls == "logistic":
            assert np.all((runs[0] >= 0) & (runs[0] <= 1))  # predict_proba[:, 1]


def test_a_zero_target_is_class_not_up() -> None:
    # owner decision S6D-R6
    assert screen.fit_target("logistic", [-0.5, 0.0, 0.5]).tolist() == [0, 0, 1]
    assert screen.fit_target("ridge", [-0.5, 0.0]).tolist() == [-0.5, 0.0]


# --- S6b: model trials -----------------------------------------------------

MODEL_WARMUP = screen.model_warmup_hours(W0)
MODEL_SIGNAL = "def s(row, params, state):\n    return max(0.0, 0.3 + row['model:m'])\n"


@functools.cache
def _long_path() -> np.ndarray:
    seed = screen.screen_seed("22" * 32)
    return screen.null_path(_source(), seed, 0, MODEL_WARMUP + WINDOW_H + 1)


def _model_trial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, **change: object
) -> dict[str, object]:
    fields: dict[str, object] = {
        "model": MODEL,
        "s_inputs": ["model:m"],
        "warmup_hours": MODEL_WARMUP,
        "horizon_hours": 24,
    }
    return _screen_trial(tmp_path, monkeypatch, MODEL_SIGNAL, **{**fields, **change})


def test_a_model_trial_runs_every_s4_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[int, int]] = []
    real = screen.model_column

    def counting(*args: object) -> list[float]:
        calls.append((len(args[1].bars), int(args[-1])))  # type: ignore[attr-defined,call-overload]
        return real(*args)  # type: ignore[arg-type]

    monkeypatch.setattr(screen, "model_column", counting)
    trial = _model_trial(tmp_path, monkeypatch)
    got = screen.screen_gates(trial, _long_path(), W0, WINDOW_H, *NULL_STREAM)
    assert got == {
        **dict.fromkeys(screen.GATES_S4B, None),
        "G-8": screen.NA,
        "G-11": "INSUFFICIENT_SHIFT_RANGE",
        "G-14": None,
    }
    # MR-3: ETH, BTC, and the lagged BTC run; G-5 and G-7 reuse BTC's
    assert sorted(lag for _, lag in calls) == [0, 0, 1]


def test_a_logistic_model_trial_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    logit = {**MODEL, "class": "logistic", "target": "sign_of_vol_scaled_target"}
    trial = _model_trial(tmp_path, monkeypatch, model=logit)
    got = screen.screen_gates(trial, _long_path(), W0, WINDOW_H, *NULL_STREAM)
    assert all(got[g] is None for g in screen.GATES_S4B)


def test_emissions_are_held_until_the_next_midnight() -> None:
    # MR-3 / WF-6: one prediction per 00:00, held for the day; NaN outside
    trial = {**_trial(model=MODEL, s_inputs=["model:m"]), "horizon_hours": 24}
    series = screen.path_series(_long_path(), 0, W0 - timedelta(hours=MODEL_WARMUP))
    first, columns = feature_columns(series)
    col = screen.model_column(trial, series, first, columns, MODEL_WARMUP, WINDOW_H, 0)
    window = [col[j - 1 - first] for j in range(MODEL_WARMUP, MODEL_WARMUP + WINDOW_H)]
    assert all(math.isfinite(v) for v in window)
    days = [window[d * 24 : d * 24 + 24] for d in range(WINDOW_H // 24)]
    assert all(len(set(day)) == 1 for day in days) and len({d[0] for d in days}) > 1
    assert math.isnan(col[MODEL_WARMUP - 2 - first])  # before w0
    lagged = screen.model_column(
        trial, series, first, columns, MODEL_WARMUP, WINDOW_H, 1
    )
    shifted = [
        lagged[j - 2 - first] for j in range(MODEL_WARMUP, MODEL_WARMUP + WINDOW_H)
    ]
    assert shifted != window  # inference re-run on the lagged features


def test_a_failing_fit_is_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken(cls: str, params: object, seed: int) -> object:
        raise ValueError("library failure")

    monkeypatch.setattr(screen, "build_model", broken)
    trial = _model_trial(tmp_path, monkeypatch)
    got = screen.screen_gates(trial, _long_path(), W0, WINDOW_H, *NULL_STREAM)
    assert set(got.values()) == {"MODEL_FIT_ERROR", screen.NA}  # G-8 N/A


@pytest.fixture(autouse=True)
def _fast_g14(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    # every model trial in these tests runs G-14; 3 draws keep them fast
    if "reference_vectors" not in request.node.name:  # frozen at 500 draws
        monkeypatch.setattr(screen, "G14_DRAWS", 3)


# --- S6b repairs and S6c: G-14 ---------------------------------------------


def test_emissions_cover_every_window_decision_at_long_horizons(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # S6B-R1: H = 168 h; the last week's decisions still get predictions
    trial = _model_trial(tmp_path, monkeypatch, horizon_hours=168)
    got = screen.screen_gates(trial, _long_path(), W0, WINDOW_H, *NULL_STREAM)
    assert all(got[g] is None for g in screen.GATES_S4B) and got["G-14"] is None


def test_g6_reinfers_from_exactly_the_previous_hour_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # MR-3 / WF-6: under G-6 the inference rows are the bars closing at
    # t - 1h (row j - 2); training rows are not lagged
    seen: list[np.ndarray] = []
    real = screen.predict

    def spy(model: object, cls: str, x: np.ndarray) -> np.ndarray:
        seen.append(np.array(x))
        return real(model, cls, x)

    monkeypatch.setattr(screen, "predict", spy)
    trial = {**_trial(model=MODEL, s_inputs=["model:m"]), "horizon_hours": 24}
    series = screen.path_series(_long_path(), 0, W0 - timedelta(hours=MODEL_WARMUP))
    first, columns = feature_columns(series)
    window, preds = screen.walk_forward(
        trial, series, first, columns, MODEL_WARMUP, WINDOW_H, 1
    )
    names = MODEL["features"]
    want = np.array([[columns[f][j - 2 - first] for f in names] for j in window])
    assert np.array_equal(np.vstack(seen), want)
    assert len(preds) == len(window) == WINDOW_H // 24


def test_g14_draws_follow_the_annex_stream() -> None:
    # G14-1 (C-12 (5)): json.dumps([..., "shuffled_labels_null", "BTCUSDT",
    # "1.0", window id, d, w])
    import random as _random

    material = (
        '["aqt.statistics.stream.v1","' + "ab" * 32 + '",'
        '"f3ba9362c5f1512fd24600775df2aa048a7e701c8f40c8cb00e97c2c644f515c",'
        '"shuffled_labels_null","BTCUSDT","1.0",' + json.dumps(WINDOW) + ",4,1]"
    )
    seed = hashlib.sha256(material.encode()).hexdigest()
    rng = _random.Random(int.from_bytes(bytes.fromhex(seed), "big"))
    n_w, h = 120, 7
    m = n_w - 2 * h + 1
    while (r := rng.getrandbits(m.bit_length())) >= m:
        pass
    assert screen.g14_draw("ab" * 32, WINDOW, 4, 1, n_w, h) == (
        h + r,
        rng.getrandbits(31),
    )


def test_g14_shift_range_boundary() -> None:
    # G14-2 (S6D-R4): n_w = 2h allows the single offset h; 2h - 1 does not
    offset, _ = screen.g14_draw("ab" * 32, WINDOW, 0, 0, 14, 7)
    assert offset == 7
    with pytest.raises(screen.RunUnavailable, match="NO_SHIFT_RANGE"):
        screen.g14_draw("ab" * 32, WINDOW, 0, 0, 13, 7)


def test_g14_reference_vectors() -> None:
    """Frozen with screen.py (WF-8): n = (120, 365), h = 7."""
    got = [
        screen.g14_draw("ab" * 32, WINDOW, d, w, n, 7)
        for d in (0, 499)
        for w, n in enumerate((120, 365))
    ]
    assert got == REF_G14
    assert screen.g14_grid_sha256("ab" * 32, WINDOW, (120, 365), 7) == REF_G14_GRID
    assert screen.G14_DRAWS == 500  # S6C-R2: production count (tests patch it)


REF_G14 = [(52, 1547148029), (200, 1720495609), (42, 329123030), (302, 1969132963)]
REF_G14_GRID = "5eb80b73256d75d628a4562ec04631b090eea5efcf461ff9148a04b5b4f8d643"


def test_spearman_ic_uses_midranks() -> None:
    # G14-4: ties share their mean rank; IC is the Pearson correlation of ranks
    assert screen.midranks([3.0, 1.0, 3.0, 2.0]).tolist() == [3.5, 1.0, 3.5, 2.0]
    assert screen.spearman_ic([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert screen.spearman_ic([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    with pytest.raises(screen.RunUnavailable, match="CONSTANT_IC_INPUT"):
        screen.spearman_ic([1, 1, 1], [1, 2, 3])
    # S6C-R1: a NaN prediction never ranks into a finite IC
    with pytest.raises(screen.RunUnavailable, match="NONFINITE_IC_INPUT"):
        screen.spearman_ic([1.0, float("nan"), 3.0, 4.0], [1, 2, 3, 4])


def test_a_null_pipeline_shifts_labels_circularly_within_each_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # G14-3: the fit labels of a draw are np.roll(original, -offset)
    seen: list[np.ndarray] = []
    real = screen.build_model

    def spy(cls: str, params: object, seed: int) -> object:
        model = real(cls, params, seed)  # type: ignore[arg-type]
        fit = model.fit

        def recording(x: np.ndarray, y: np.ndarray) -> object:
            seen.append(np.asarray(y).copy())
            return fit(x, y)

        model.fit = recording
        return model

    monkeypatch.setattr(screen, "build_model", spy)
    monkeypatch.setattr(screen, "g14_draw", lambda *a: (8, 1))
    trial = {**_trial(model=MODEL, s_inputs=["model:m"]), "horizon_hours": 24}
    series = screen.path_series(_long_path(), 0, W0 - timedelta(hours=MODEL_WARMUP))
    first, columns = feature_columns(series)
    screen.walk_forward(trial, series, first, columns, MODEL_WARMUP, WINDOW_H, 0)
    screen.walk_forward(
        trial, series, first, columns, MODEL_WARMUP, WINDOW_H, 0, ("ab" * 32, WINDOW, 0)
    )
    original, shifted = seen[0], seen[len(seen) // 2]
    assert np.array_equal(shifted, np.roll(original, -8))


def test_g14_is_na_without_a_model_and_needs_its_seed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = _screen_trial(tmp_path, monkeypatch)
    assert (
        screen.screen_gates(trial, _screen_path(), W0, WINDOW_H, *NULL_STREAM)["G-14"]
        == screen.NA
    )
    with pytest.raises(screen.TrialError, match="trial seed"):
        screen.screen_gates(
            _model_trial(tmp_path, monkeypatch), _long_path(), W0, WINDOW_H
        )


WINDOW_LONG_H = 24 * 61  # three refits: w0, w0 + 30 d, w0 + 60 d


@functools.cache
def _longer_path() -> np.ndarray:
    seed = screen.screen_seed("44" * 32)
    return screen.null_path(_source(), seed, 0, MODEL_WARMUP + WINDOW_LONG_H + 1)


@pytest.mark.parametrize("draws_n", [2, 4])
def test_g14_runs_the_nominee_and_every_draw_in_every_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, draws_n: int
) -> None:
    # S6C-R2: every refit window draws its own (d, w), and G-14 scores the
    # nominee plus exactly G14_DRAWS null pipelines; two counts show the loop
    # follows the constant rather than a hardcoded number
    monkeypatch.setattr(screen, "G14_DRAWS", draws_n)
    draws: list[tuple[int, int]] = []
    real_draw = screen.g14_draw

    def spy_draw(
        seed: str, wid: str, d: int, w: int, n_w: int, h: int
    ) -> tuple[int, int]:
        draws.append((d, w))
        return real_draw(seed, wid, d, w, n_w, h)

    scored: list[list[float]] = []
    real_ic = screen.spearman_ic

    def spy_ic(predictions: list[float], targets: list[float]) -> float:
        scored.append(list(predictions))
        return real_ic(predictions, targets)

    monkeypatch.setattr(screen, "g14_draw", spy_draw)
    monkeypatch.setattr(screen, "spearman_ic", spy_ic)
    trial = _model_trial(tmp_path, monkeypatch)
    got = screen.screen_gates(trial, _longer_path(), W0, WINDOW_LONG_H, *NULL_STREAM)
    assert got["G-14"] is None
    assert sorted(set(draws)) == [(d, w) for d in range(draws_n) for w in range(3)]
    assert len(scored) == 1 + draws_n  # the nominee and every draw
    # the first IC is the nominee's: no draw is taken before it
    nominee = screen.walk_forward(
        trial,
        *_btc_prepared(trial, _longer_path(), WINDOW_LONG_H),
        MODEL_WARMUP,
        WINDOW_LONG_H,
        0,
    )[1]
    assert scored[0] == nominee[: len(scored[0])]


def _btc_prepared(
    trial: dict[str, object], path: np.ndarray, window_h: int
) -> tuple[BarSeries, int, dict[str, tuple[float, ...]]]:
    series = screen.path_series(path, 0, W0 - timedelta(hours=MODEL_WARMUP))
    first, columns = feature_columns(series)
    return series, first, columns


# --- S5b: G-11 runs ----------------------------------------------------------

WINDOW_G11_H = 24 * 559  # T - 2m = 499 with m = 30: the shortest G-11 window


@functools.cache
def _g11_path() -> np.ndarray:
    seed = screen.screen_seed("55" * 32)
    return screen.null_path(_source(), seed, 0, 4801 + WINDOW_G11_H + 1)


def test_g11_runs_every_draw_on_a_long_enough_window(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runs: list[object] = []
    real = screen.g11_targets

    def spy(*a: Any) -> list[float]:
        runs.append(a[-1])
        return real(*a)

    monkeypatch.setattr(screen, "g11_targets", spy)
    trial = _screen_trial(tmp_path, monkeypatch)
    got = screen.screen_gates(trial, _g11_path(), W0, WINDOW_G11_H, *NULL_STREAM)
    assert got["G-11"] is None
    want = screen.g11_shifts(NULL_STREAM[0], WINDOW, 559, 30)
    assert runs == want and len(runs) == 500


def test_g11_rotates_s_by_whole_days_at_the_real_hour() -> None:
    # GR-2: s'_h = s_((h + 24 k) mod 24T); sigma_hat at the real hour
    n = 48
    cols = {name: tuple([1.0] * 60) for name in FEATURE_NAMES}
    cols["ewma_vol_168h"] = tuple([0.5] * 30 + [1.0] * 30)
    signals = [float(i) / 100 for i in range(n)]
    trial = {**_trial(), "tau": "0.40"}
    got = screen.g11_targets(trial, None, signals, cols, 0, [1.0] * 60, 1, n, 1)
    for i, target in enumerate(got):
        sigma = cols["ewma_vol_168h"][i]
        assert target == min(1.0, max(0.0, signals[(i + 24) % n] * 0.4 / sigma))


def test_g11_needs_its_streams_and_is_na_for_constant_signals(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = _screen_trial(tmp_path, monkeypatch)
    with pytest.raises(screen.TrialError, match="G-11 needs"):
        screen.screen_gates(trial, _screen_path(), W0, WINDOW_H)
    code = "def s(row, params, state):\n    return 0.5\n"
    const = _screen_trial(tmp_path, monkeypatch, code, g11_class="constant_signal")
    got = screen.screen_gates(const, _screen_path(), W0, WINDOW_H)  # no stream needed
    assert got["G-11"] == screen.NA


def test_every_g11_draw_is_scored_and_one_bad_draw_makes_it_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # S5B-R1: 500 draw statistics are computed; an unavailable one counts
    state = {"draws": 0, "scored": 0, "fail_at": 0}
    real_targets, real_stats = screen.g11_targets, screen.leg_stats

    def targets(*a: Any) -> list[float]:
        state["draws"] += 1
        return real_targets(*a)

    def stats(*a: Any) -> dict[str, float]:
        if state["draws"]:
            state["scored"] += 1
            if state["draws"] == state["fail_at"]:
                raise screen.RunUnavailable("INJECTED_DRAW")
        return real_stats(*a)

    monkeypatch.setattr(screen, "g11_targets", targets)
    monkeypatch.setattr(screen, "leg_stats", stats)
    trial = _screen_trial(tmp_path, monkeypatch)
    got = screen.screen_gates(trial, _g11_path(), W0, WINDOW_G11_H, *NULL_STREAM)
    assert got["G-11"] is None and state["scored"] == 500
    state.update(draws=0, scored=0, fail_at=250)
    got = screen.screen_gates(trial, _g11_path(), W0, WINDOW_G11_H, *NULL_STREAM)
    assert got["G-11"] == "INJECTED_DRAW" and state["scored"] == 250


def test_a_g11_draw_overlay_sees_the_real_hour_and_starts_fresh() -> None:
    # S5B-R2, S5BR-R1 (C-10 (4)): the overlay reads every market input at the
    # real hour (features vary by hour here) and gets fresh state every draw
    n = 48
    closes = [100.0 + i for i in range(60)]
    cols = {name: tuple(float(i) for i in range(60)) for name in FEATURE_NAMES}
    cols["ewma_vol_168h"] = tuple(0.5 + i / 1000 for i in range(60))  # by hour too
    seen: list[tuple[float, float, int]] = []

    def overlay(
        target: float, market: dict[str, float], state: dict[str, int]
    ) -> float:
        others = {market[f] for f in FEATURE_NAMES if f != "ewma_vol_168h"}
        assert others == {market["ret_1h"]}
        assert market["ewma_vol_168h"] == 0.5 + market["ret_1h"] / 1000  # same row
        seen.append((market["close"], market["ret_1h"], state.get("n", 0)))
        state["n"] = state.get("n", 0) + 1
        return target

    trial = {**_trial(), "tau": "0.40"}
    for shift in (1, 2):
        seen.clear()
        screen.g11_targets(trial, overlay, [0.1] * n, cols, 0, closes, 1, n, shift)
        assert [c for c, _, _ in seen] == closes[0:n]  # bar j0 + i - 1, unshifted
        assert [f for _, f, _ in seen] == [float(i) for i in range(n)]  # its row
        assert [k for _, _, k in seen] == list(range(n))  # state starts at 0


def test_g11_loads_the_overlay_afresh_for_every_draw(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # S5BR-R1: an overlay counting its calls in a module global fails if one
    # loaded instance is reused across draws (or runs)
    code = (
        "CALLS = [0]\n"
        "def o(t, m, state):\n"
        "    CALLS[0] += 1\n"
        f"    if CALLS[0] > {WINDOW_G11_H}:\n"
        "        raise ValueError('reused')\n"
        "    return t\n"
    )
    digest = _module(tmp_path, monkeypatch, "s5b_counting_overlay", code)
    trial = _screen_trial(
        tmp_path, monkeypatch, overlay="s5b_counting_overlay:o", overlay_sha256=digest
    )
    got = screen.screen_gates(trial, _g11_path(), W0, WINDOW_G11_H, *NULL_STREAM)
    assert got["G-11"] is None and got["G-3"] is None


# --- S7: the driver -------------------------------------------------------

CONST = "def s(row, params, state):\n    return 0.5\n"


def _source_for_screen() -> screen.HourlySource:
    src = _source()
    identity: dict[str, object] = {
        "manifest_sha256": {"BTCUSDT": "a" * 64, "ETHUSDT": "b" * 64}
    }
    return screen.HourlySource(src.bars, src.hour, identity)


def _no_seconds(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{k: v for k, v in r.items() if k != "seconds"} for r in runs]


def test_a_measurement_records_every_run_and_no_outcome(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # DR-7 (S7-R5): availability and seconds, never an outcome
    monkeypatch.setattr(screen, "N_PATHS", 2)  # production: 30
    valid = _screen_trial(tmp_path, monkeypatch, CONST, g11_class="constant_signal")
    record = screen.run_screen(
        [valid], _source_for_screen(), W0, WINDOW_H, WINDOW, 30, workers=1
    )
    assert record["availability"] == "ALL_AVAILABLE" and "outcome" not in record
    assert [(r["trial_id"], r["path"]) for r in record["runs"]] == [
        ("t000", 0),
        ("t000", 1),
    ]
    assert all("seconds" in r for r in record["runs"]) and "measurement_only" in record
    assert record["trial_set_sha256"] == screen.trial_set_sha256([valid])
    assert record["screen_seed"] == screen.screen_seed(record["trial_set_sha256"])
    assert set(record["reference_vectors"]) == {"paths", "g11", "g14"}
    # a signal-timed trial on a 30-day window: G-11 has no shift range
    timed = {**valid, "trial_id": "t001", "g11_class": "signal_timed"}
    record = screen.run_screen(
        [valid, timed], _source_for_screen(), W0, WINDOW_H, WINDOW, 30, workers=1
    )
    assert record["availability"] == "SOME_UNAVAILABLE"


def test_every_trial_runs_on_the_end_of_the_shared_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # DR-1: one path per index, trials with less warm-up use its last hours
    monkeypatch.setattr(screen, "N_PATHS", 1)
    seen: list[tuple[str, int, str]] = []
    real = screen.screen_gates

    def spy(trial: dict[str, Any], path: np.ndarray, *a: Any) -> dict[str, Any]:
        seen.append((trial["trial_id"], len(path), a[2]))
        return real(trial, path, *a)

    monkeypatch.setattr(screen, "screen_gates", spy)
    short = _screen_trial(tmp_path, monkeypatch, CONST, g11_class="constant_signal")
    long = {**short, "trial_id": "t001", "warmup_hours": 4900}
    record = screen.run_screen(
        [short, long], _source_for_screen(), W0, WINDOW_H, WINDOW, 30, workers=1
    )
    assert record["path_hours"] == 4900 + WINDOW_H + 1
    seed = record["screen_seed"]
    assert seen == [
        ("t000", 4801 + WINDOW_H + 1, screen.screen_trial_seed(seed, 0, "t000")),
        ("t001", 4900 + WINDOW_H + 1, screen.screen_trial_seed(seed, 0, "t001")),
    ]


def test_an_unbuildable_path_and_refusals_before_any_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # DR-3, S7-R6
    monkeypatch.setattr(screen, "N_PATHS", 1)
    real = screen.null_path

    def broken(source: Any, seed: str, p: int, hours: int) -> np.ndarray:
        if hours == 1000:  # the reference vectors' fixed path still builds
            return real(source, seed, p, hours)
        raise screen.PathUnavailable("overflow")

    monkeypatch.setattr(screen, "null_path", broken)
    trial = _screen_trial(tmp_path, monkeypatch, CONST, g11_class="constant_signal")
    record = screen.run_screen(
        [trial], _source_for_screen(), W0, WINDOW_H, WINDOW, 30, workers=1
    )
    assert set(record["runs"][0]["gates"].values()) == {"PATH_UNAVAILABLE"}
    assert record["availability"] == "SOME_UNAVAILABLE"
    with pytest.raises(screen.TrialError):
        screen.run_screen(
            [{**trial, "tau": "0.5"}], _source_for_screen(), W0, WINDOW_H, WINDOW, 30
        )
    # S7-R6: a later trial's stale code hash refuses the screen before a run
    jobs: list[object] = []
    monkeypatch.setattr(screen, "screen_job", lambda *a: jobs.append(a))
    stale = {**trial, "trial_id": "t001", "signal_sha256": "0" * 64}
    with pytest.raises(screen.TrialError, match="declared source"):
        screen.run_screen(
            [trial, stale], _source_for_screen(), W0, WINDOW_H, WINDOW, 30, workers=1
        )
    assert jobs == []


def test_two_worker_processes_give_the_same_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # DR-8: workers import the engine and the trial code from the parent's paths
    monkeypatch.setattr(screen, "N_PATHS", 2)
    trial = _screen_trial(tmp_path, monkeypatch, CONST, g11_class="constant_signal")
    one = screen.run_screen(
        [trial], _source_for_screen(), W0, WINDOW_H, WINDOW, 30, workers=1
    )
    two = screen.run_screen(
        [trial],
        _source_for_screen(),
        W0,
        WINDOW_H,
        WINDOW,
        30,
        workers=2,
        code_dir=tmp_path,
    )
    assert _no_seconds(two["runs"]) == _no_seconds(one["runs"])


def test_workers_search_trial_code_last(monkeypatch: pytest.MonkeyPatch) -> None:
    # S7-R1, S7R-R1: trial code never shadows an engine or image module, even
    # if it was already early on the path (PYTHONPATH)
    monkeypatch.setattr(sys, "path", ["/trials", "/site-packages", "/repo"])
    screen._extend_path(["/repo", "/repo/src"], ["/trials"])
    assert sys.path == ["/repo", "/repo/src", "/site-packages", "/trials"]


def test_run_screen_finds_trial_code_from_code_dir_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # S7R-R3: the parent loads trial code from code_dir before any worker
    monkeypatch.setattr(screen, "N_PATHS", 1)
    code = tmp_path / "code"
    code.mkdir()
    (code / "s7_only_here.py").write_text(CONST, encoding="utf-8")
    digest = hashlib.sha256((code / "s7_only_here.py").read_bytes()).hexdigest()
    trial = {
        **_trial(
            signal="s7_only_here:s",
            signal_sha256=digest,
            s_inputs=["ema_dist_168"],
            warmup_hours=4801,
            g11_class="constant_signal",
        ),
        "parameter_point": {},
        "grid": {},
    }
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != str(code)])
    record = screen.run_screen(
        [trial],
        _source_for_screen(),
        W0,
        WINDOW_H,
        WINDOW,
        30,
        workers=1,
        code_dir=code,
    )
    assert record["availability"] == "ALL_AVAILABLE"


def test_the_screen_reference_vectors_are_frozen_where_exact() -> None:
    # S7-R4: g11 and g14 are exact everywhere; the float path waits for S8
    got = screen.screen_reference_vectors()
    assert got["g11"] == screen.FROZEN_REFERENCE_VECTORS["g11"]
    assert got["g14"] == screen.FROZEN_REFERENCE_VECTORS["g14"]
    assert screen.FROZEN_REFERENCE_VECTORS["paths"] is None


def test_c2_constants_follow_the_engine() -> None:
    # S7-R2: T_C2 = 1247 - g, w0 = 2022-01-01 + g
    assert screen.C2_G_DAYS == 7 and screen.C2_WINDOW_DAYS == 1240
    assert screen.C2_W0 == datetime(2022, 1, 8, tzinfo=UTC)
    assert screen.C2_WINDOW_ID == '["2022-01-08T00:00:00Z","2025-06-01T00:00:00Z"]'


def _declarable(
    monkeypatch: pytest.MonkeyPatch, defn: dict[str, Any], src: screen.HourlySource
) -> None:
    monkeypatch.setattr(screen, "check_object", lambda obj, posted, root: defn)
    # S7R-R2: declare rebuilds the bars itself from the raw root
    monkeypatch.setattr(screen, "load_hourly_source", lambda root: src)
    monkeypatch.setattr(screen, "N_PATHS", 1)
    monkeypatch.setattr(screen, "C2_W0", W0)
    monkeypatch.setattr(screen, "C2_WINDOW_DAYS", WINDOW_H // 24)
    monkeypatch.setattr(screen, "C2_WINDOW_ID", WINDOW)
    monkeypatch.setattr(screen, "C2_G_DAYS", 30)


def test_a_declaration_record_needs_the_checks_and_names_the_object(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # DR-6 (S7-R2, S7-R3, S7-R4)
    src = _source_for_screen()
    defn = {"exploration_source": {"manifest_sha256": src.identity["manifest_sha256"]}}
    _declarable(monkeypatch, defn, src)
    trial = _screen_trial(tmp_path, monkeypatch, CONST, g11_class="constant_signal")
    with pytest.raises(ValueError, match="not frozen yet"):
        screen.declare([trial], tmp_path, tmp_path, "f" * 64, tmp_path, workers=1)
    monkeypatch.setattr(
        screen, "FROZEN_REFERENCE_VECTORS", screen.screen_reference_vectors()
    )
    record = screen.declare([trial], tmp_path, tmp_path, "f" * 64, tmp_path, workers=1)
    assert record["outcome"] == "VALID"
    assert record["qualification_object_sha256"] == "f" * 64
    assert "measurement_only" not in record and "availability" not in record
    assert all("seconds" not in r for r in record["runs"])
    assert (record["w0"], record["window_hours"]) == (W0.isoformat(), WINDOW_H)
    # other exploration bars than the run definition's: refused
    other = screen.HourlySource(
        src.bars, src.hour, {"manifest_sha256": {"BTCUSDT": "c" * 64}}
    )
    monkeypatch.setattr(screen, "load_hourly_source", lambda root: other)
    with pytest.raises(ValueError, match="exploration bars"):
        screen.declare([trial], tmp_path, tmp_path, "f" * 64, tmp_path, workers=1)
    monkeypatch.setattr(screen, "load_hourly_source", lambda root: src)
    # changed reference vectors: refused
    monkeypatch.setattr(
        screen, "FROZEN_REFERENCE_VECTORS", {"paths": "x", "g11": "y", "g14": "z"}
    )
    with pytest.raises(ValueError, match="differ from the frozen"):
        screen.declare([trial], tmp_path, tmp_path, "f" * 64, tmp_path, workers=1)


def test_check_object_verifies_every_manifest_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # S7-R7: choices.json and every other listed file, not three of them
    from calibration import mapping

    files = {
        "definition.json": b"{}",
        "mapping.py": b"m",
        "screen.py": b"s",
        "choices.json": b"c",
    }
    for name, data in files.items():
        (tmp_path / name).write_bytes(data)
    manifest = {n: hashlib.sha256(d).hexdigest() for n, d in files.items()}
    (tmp_path / "manifest.json").write_bytes(json.dumps(manifest).encode())
    monkeypatch.setattr(screen, "check_screen_code", lambda *a: None)
    monkeypatch.setattr(mapping, "check_runtime", lambda defn: None)
    assert screen.check_object(tmp_path, sha(manifest), tmp_path) == {}
    (tmp_path / "choices.json").write_bytes(b"changed")
    with pytest.raises(ValueError, match="choices.json"):
        screen.check_object(tmp_path, sha(manifest), tmp_path)
    with pytest.raises(ValueError, match="posted"):
        screen.check_object(tmp_path, "0" * 64, tmp_path)


def test_the_cli_pilot_needs_twenty_trials_and_never_overwrites(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # S7-R5, S7-R8
    import importlib.util as iu

    spec = iu.spec_from_file_location(
        "d19_screen_cli", Path(__file__).parents[2] / "scripts" / "d19_screen.py"
    )
    assert spec is not None and spec.loader is not None
    cli = iu.module_from_spec(spec)
    spec.loader.exec_module(cli)
    trials = tmp_path / "trials.json"
    trials.write_text(json.dumps([_trial()]), encoding="utf-8")
    base = ["--trials", str(trials), "--trial-code", str(tmp_path)]
    with pytest.raises(SystemExit) as e:
        cli.main(
            ["pilot", *base, "--raw-root", str(tmp_path), "--out", str(tmp_path / "r")]
        )
    assert e.value.code == 2  # argparse error: not a 20-trial set
    out = tmp_path / "exists.json"
    out.write_bytes(b"keep")
    monkeypatch.setattr(cli.screen, "MAX_TRIALS", 1)
    monkeypatch.setattr(
        cli.screen, "load_hourly_source", lambda root: _source_for_screen()
    )
    ran: list[object] = []

    def fake_run(*a: Any, **k: Any) -> dict[str, int]:
        ran.append(a)
        return {"x": 1}

    monkeypatch.setattr(cli.screen, "run_screen", fake_run)
    with pytest.raises(FileExistsError):
        cli.main(["pilot", *base, "--raw-root", str(tmp_path), "--out", str(out)])
    assert out.read_bytes() == b"keep" and ran == []  # S7R-R4: refused before work
    # a failing screen leaves no reserved file behind
    monkeypatch.setattr(cli.screen, "run_screen", lambda *a, **k: 1 / 0)
    fresh = tmp_path / "fresh.json"
    with pytest.raises(ZeroDivisionError):
        cli.main(["pilot", *base, "--raw-root", str(tmp_path), "--out", str(fresh)])
    assert not fresh.exists()
