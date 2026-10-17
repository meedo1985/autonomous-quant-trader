"""Declared-strategy screen of the D-19 preregistration §7.2 (A-U1).

Build slices (`review/d19-engine/SCREEN_PLAN.md`): S1, the `n_S = 30`
simulated null hourly BTC/ETH paths; S3, the trial interface; S5, the G-11
shifts; S4b, trial runs and G-3, G-5, G-6, G-7 (on `aqt.backtest.
event_contract` and `aqt.features.columns`); S4c, G-8; S5b, the G-11 runs;
S6, the walk-forward models and G-14; S7, the driver. All of it is in this
file, which the qualification object binds by
its bytes (DRAFT R-8, qobj `LATER`); everything it imports must be
engine-commit code (`SCREEN_PLAN.md` section 3).

§7.2 "Paths", read as follows (readings SP-n, for review):
- SP-1 Source rows: the exploration-partition 1h bars of BTCUSDT and
  ETHUSDT, read only through `build_exploration_manifest`, joined on
  `open_time`; an hour missing for either symbol is left out, never filled
  (Constitution §6). Each row carries only its own offsets from its own
  open, so no price is read across a left-out hour.
- SP-2 Bootstrap (S1-R1): the stationary bootstrap of
  `semi.stationary_indices` over the joint rows, mean block 168 h, from the
  `"market"` stream, with one change: a block never continues across a
  left-out hour or the end of the source. Where the next row is not the
  next clock hour (or there is none), the step restarts at a uniform row
  instead, so a block is always consecutive clock hours. Draw order: one
  uniform start, then per hour one uniform test and, on a restart (by the
  test or forced), one uniform index. Signs: `semi.block_signs`, mean 24 h,
  from the `"sign"` stream, one sign per row shared by both symbols.
- SP-3 Streams: path `p` uses seed `SHA256(cj({"path": p, "screen_seed":
  <hex>}))` (no `trial_id` key, so it never equals a C-10 null-stream trial
  seed), and `seeds.stream` of it with the names above. `screen_seed` is
  §7.2's `SHA256(cj({"stream": "screen", "trial_set_sha256": <hex>}))`.
- SP-4 Reconstruction (DS4-5, DF4-4): per symbol, `h, l, c = ln(H/O),
  ln(L/O), ln(C/O)` of the sampled bar, `(-l, -h, -c)` under sign -1; the
  first open is the first sampled bar's open, each later open the previous
  new close; volume as sampled. Computed in log space: `ln C_i = ln O_0 +
  sum_{j<=i} c_j`.
- SP-5 Length: the caller passes the hour count (C2 window plus the trials'
  declared warm-up); the trial set fixes both.
- SP-6 Reference vectors (S1-R3): the draws (rows, signs) come from numpy
  `Generator` methods, which numpy does not keep stable across versions;
  they are reproducible on the pinned numpy 2.5.3 and frozen in the unit
  test, which detects a change. The reconstructed floats use `log`/`exp`,
  so their bit-exact vector belongs to the pinned-image check (slice S7),
  as the engine's own reference vectors do (`rundef.reference_vectors`).
- SP-7 Unavailable path (S1-R2): a path with any non-finite or non-positive
  price (exp overflow or underflow over a long one-signed stretch) is
  refused with `PathUnavailable`; the driver records it, never repairs it.
"""

from __future__ import annotations

import ast
import builtins
import hashlib
import importlib
import importlib.util
import json
import math
import os
import random
import sys
import time
import types
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import numpy as np

import aqt.metrics.statistics as st
from aqt.backtest.costs import (
    BPS_PER_UNIT,
    CostModelError,
    ewma_hourly_volatility_bps_series,
    hourly_log_returns_bps,
)
from aqt.backtest.event_contract import (
    EventContractError,
    EventResult,
    run_event_contract,
)
from aqt.benchmarks.canonical import CanonicalBenchmarkError, vol_target_exposure
from aqt.data.bars import Bar, BarSeries
from aqt.data.klines import EXPLORATION, build_exploration_manifest
from aqt.features.columns import feature_columns
from aqt.features.factory import (
    FEATURE_NAMES,
    REQUIRED_HISTORY_BARS,
    FeatureFactoryError,
)
from aqt.metrics.descriptive import _max_drawdown
from calibration import gap, grid
from calibration.seeds import sha, stream
from calibration.semi import SYMBOLS, block_signs

N_PATHS = 30  # n_S
MEAN_BLOCK_HOURS = 168
SIGN_BLOCK_HOURS = 24
OPEN, HIGH, LOW, CLOSE, VOLUME = range(5)


class PathUnavailable(ValueError):
    """SP-7: a reconstructed path is not finite and positive."""


@dataclass(frozen=True)
class HourlySource:
    """Joint rows: `bars[i, s]` = (open, high, low, close, volume) of symbol
    `SYMBOLS[s]` at clock hour `hour[i]` (hours since the epoch); identity
    for the object (§7.2)."""

    bars: np.ndarray
    hour: np.ndarray
    identity: dict[str, object]


def joint_bars(series: list[BarSeries]) -> HourlySource:
    """SP-1: rows x symbols x OHLCV over the hours present in every series,
    in time order (identity left empty)."""
    if [s.symbol for s in series] != list(SYMBOLS):
        raise ValueError(f"need the series of {SYMBOLS} in that order")
    by_time = [{b.open_time: b for b in s.bars} for s in series]
    common = sorted(set(by_time[0]).intersection(*by_time[1:]))
    if len(common) < 2:
        raise ValueError("fewer than two common hours")
    bars = np.array(
        [
            [
                (b.open, b.high, b.low, b.close, b.volume)
                for b in (m[t] for m in by_time)
            ]
            for t in common
        ],
        dtype=float,
    )
    hour = np.array([int(t.timestamp()) // 3600 for t in common], dtype=np.int64)
    return HourlySource(bars, hour, {})


def load_hourly_source(raw_root: Path) -> HourlySource:
    builds = [build_exploration_manifest(EXPLORATION, s, raw_root) for s in SYMBOLS]
    joint = joint_bars([b.series for b in builds])
    bars = joint.bars
    identity: dict[str, object] = {
        "manifest_sha256": {
            s: b.manifest.manifest_sha256 for s, b in zip(SYMBOLS, builds, strict=True)
        },
        "bars_sha256": hashlib.sha256(
            np.ascontiguousarray(bars, "<f8").tobytes()
        ).hexdigest(),
        "hours_sha256": hashlib.sha256(joint.hour.astype("<i8").tobytes()).hexdigest(),
        "rows": len(bars),
    }
    return HourlySource(bars, joint.hour, identity)


def screen_seed(trial_set_sha256: str) -> str:
    return sha({"stream": "screen", "trial_set_sha256": trial_set_sha256})


def path_seed(seed: str, p: int) -> str:
    return sha({"path": p, "screen_seed": seed})


def reconstruct(sampled: np.ndarray, signs: np.ndarray) -> np.ndarray:
    """SP-4: chain the sampled bars (rows x symbols x OHLCV) into one path."""
    o = sampled[..., OPEN]
    hi, lo, c = (np.log(sampled[..., k] / o) for k in (HIGH, LOW, CLOSE))
    flip = (signs < 0)[:, None]
    hi, lo, c = np.where(flip, -lo, hi), np.where(flip, -hi, lo), np.where(flip, -c, c)
    # each close is fl(log_open + c), the same addition as high and low, so
    # the source bar's OHLC order survives rounding (S8 pilot: high < close)
    log_close = np.cumsum(np.vstack([np.log(o[0])[None], c]), axis=0)[1:]
    log_open = np.vstack([np.log(o[0])[None], log_close[:-1]])
    out = np.empty_like(sampled)
    out[..., OPEN] = np.exp(log_open)
    out[..., HIGH] = np.exp(log_open + hi)
    out[..., LOW] = np.exp(log_open + lo)
    out[..., CLOSE] = np.exp(log_close)
    out[..., VOLUME] = sampled[..., VOLUME]
    prices = out[..., :VOLUME]
    if not (np.all(np.isfinite(prices)) and np.all(prices > 0)):
        raise PathUnavailable("path has a non-finite or non-positive price")
    return out


def hourly_indices(
    rng: np.random.Generator, hour: np.ndarray, n: int, mean_block: int
) -> np.ndarray:
    """SP-2: stationary bootstrap rows whose blocks are consecutive hours."""
    out = np.empty(n, dtype=np.int64)
    out[0] = rng.integers(len(hour))
    for i in range(1, n):
        prev = out[i - 1]
        nxt = prev + 1
        if (
            rng.random() < 1 / mean_block
            or nxt == len(hour)
            or hour[nxt] != hour[prev] + 1
        ):
            out[i] = rng.integers(len(hour))
        else:
            out[i] = nxt
    return out


def path_draws(
    hour: np.ndarray, seed: str, p: int, hours: int
) -> tuple[np.ndarray, np.ndarray]:
    """SP-2, SP-3: the source rows and signs of screen path `p`."""
    if not 0 <= p < N_PATHS or hours < 1:
        raise ValueError(f"need 0 <= p < {N_PATHS} and hours >= 1")
    s = path_seed(seed, p)
    rows = hourly_indices(stream(s, "market"), hour, hours, MEAN_BLOCK_HOURS)
    return rows, block_signs(stream(s, "sign"), hours, SIGN_BLOCK_HOURS)


def null_path(source: HourlySource, seed: str, p: int, hours: int) -> np.ndarray:
    """Screen path `p`: hours x symbols x OHLCV; `PathUnavailable` (SP-7)."""
    rows, signs = path_draws(source.hour, seed, p, hours)
    with np.errstate(over="ignore", under="ignore"):
        return reconstruct(source.bars[rows], signs)


# --- S3: the trial interface (Annex C C-10 (1)-(2), C-12 (1), C-8) ---------
#
# Readings TI-n (proposed, for review):
# - TI-1 A trial is a canonical-JSON object with exactly the fields of
#   `TRIAL_FIELDS`; decimals are strings, as in `aqt.core.preregistration`
#   (`tau` one of "0.40", "0.60", "0.80"); every mapping key is a non-empty
#   string (S3-R5). `trial_sha256` is `sha` of it and `trial_set_sha256` is
#   `sha({"trials": [trial_sha256, ...]})` in declared order, which is the
#   §7.2 seed input. A set has 1 to 20 trials (§13 rev 7g item 1) with
#   distinct `trial_id`s.
# - TI-2 (S3-R1, S3R-R1) `signal` and `overlay` name code as
#   "module:function", where `module` is a top-level module (no package, so
#   no `__init__` runs), with the SHA-256 of its source file. The module is
#   self-contained: it may import only the modules `math` and `numpy`
#   themselves, as `import math` / `import numpy [as np]`, no submodule
#   and no `from ... import` (S3R4-R1, S3R5-R1; bound by the image digest),
#   and it may not name, as a name or an attribute, `__import__`,
#   `importlib`, `exec`, `eval`, `compile`, `open`, `__builtins__`, numpy's
#   file input and output or its tool submodules (`load`, `save`,
#   `loadtxt`, `fromfile`, `memmap`, `lib`, `f2py`, `testing`, ...;
#   S3R2-R1). `check_trial` already refuses a dotted module (S3R2-R2).
#   `load` checks the rest on the hashed bytes, then compiles exactly those
#   bytes into a fresh module that is never put in `sys.modules`, whose
#   builtins are only `CODE_BUILTINS` (pure computation: no `input`, `open`,
#   `print`, `getattr`, `globals`, `breakpoint`, ...; class definitions are
#   allowed, S3R4-R2) and whose `__import__` admits only `math` and `numpy`
#   themselves (S3R3-R1, S3R4-R1). So everything a trial's code
#   can run is either its hashed file or the image. Disclosed: a deliberate
#   evasion (for example through attribute tricks on objects numpy hands
#   back) is a false declaration, not something these checks can rule out.
#   The signal is called once per hour as `signal(row, params, state)`
#   (RN-3): `row` holds only its `s_inputs` (C-10 (1)) for that hour, name
#   -> value, `params` is `signal_params`: `parameter_point` without `tau`,
#   `sigma` and the `model.` dimensions (S3-R2), and `state` is the trial's
#   own dict, fresh for each run.
# - TI-3 `s_inputs` entries are frozen feature names (`FEATURE_NAMES`) or
#   "model:<id>" of the trial's own declared model. Never allowed:
#   "sigma_hat" (the sizing estimator's output) and, for a trial sized by
#   EWMA_168h, the identical frozen feature `ewma_vol_168h` (REG (A), D-20
#   B5). Every other volatility feature stays allowed.
# - TI-4 (S3-R4) `family` is "trend" or "vol", the two families the D-19
#   calibration covers (`calibration/rules.py` FAMILIES). There is no fixed-
#   size class (C-10 (1), REG (A)). `sigma` is "EWMA_168h", or in the vol
#   family one of the protocol's allowed volatility-family estimators.
# - TI-5 (S3-R3) `model` is null or {"id", "class", "params", "target",
#   "features"} (S6a: `features` lists the model's frozen input features,
#   checked like `s_inputs`, owner decision WF-4; `params` and every grid
#   value of a `model.<name>` dimension must be on the class's allowlist,
#   WF-5)
#   with `class` in the cycle's allowed classes (DRAFT §2.5, unchanged v1.0
#   value) and `target` "vol_scaled_target" or, required for and only for
#   "logistic" (protocol `logistic_use`), "sign_of_vol_scaled_target". Both
#   model the vol-scaled target of l.103-105 at the trial's horizon, so
#   G-14 applies to every model trial and is a frozen N/A without a model
#   (`g14_applies`). Owner decision 2026-10-16 (S3R-R3,
#   `OWNER_DECISION_S3R_R3_G14_SIGN_MODELS.md`): C-12 (1) covers the sign
#   target, so G-14 is mandatory for logistic trials too. Class-specific
#   limits are checked in slice S6.
# - TI-6 (S3-R2) `horizon_hours` is one of 24, 72, 168; `warmup_hours` >=
#   0; `parameter_point` maps names to scalars, and `grid` maps the same
#   names to value lists containing the point; G-8 reads its neighbours
#   there and runs them through the same `params` and top-level fields.
#   `tau` and `sigma` are grid dimensions only under those names: when
#   present, the point must equal the top-level field and every grid value
#   must be allowed for it. A model hyperparameter is a grid dimension only
#   as "model.<name>" (S3R-R2): `<name>` must be in `model.params` with the
#   point's value, compared with its JSON type (`True` is not `1`; S3R2-R3),
#   and a plain point name may not equal a `model.params`
#   key. `model_params` gives the fit's parameters with the point's
#   `model.` values, so a G-8 neighbour changes the fit, never the signal.
# - TI-7 `g11_class` "constant_signal" is checked in every run (C-10 (2)):
#   `class_mismatch` is true when `s` is not identical at every hour.
# - TI-8 (S3-R6) The overlay may only keep the target or set it to 0
#   (C-10 (1)); the runner checks every output with `overlay_violation`.

TRIAL_FIELDS = (
    "trial_id", "family", "signal", "signal_sha256", "overlay", "overlay_sha256",
    "s_inputs", "tau", "sigma", "g11_class", "model", "horizon_hours",
    "parameter_point", "grid", "warmup_hours",
)  # fmt: skip
MAX_TRIALS = 20
FAMILIES = ("trend", "vol")
TAUS = ("0.40", "0.60", "0.80")
DEFAULT_SIGMA = "EWMA_168h"
VOL_SIGMAS = ("EWMA_72h", "EWMA_168h", "EWMA_336h", "HAR_RV", "GARCH_1_1")
MODEL_CLASSES = ("linear", "ridge", "lasso", "elastic_net", "logistic", "lightgbm")
MODEL_TARGETS = ("vol_scaled_target", "sign_of_vol_scaled_target")
HORIZONS_HOURS = (24, 72, 168)
G11_CLASSES = ("signal_timed", "constant_signal")
SIGMA_HAT = "sigma_hat"
SIGMA_IDENTICAL_FEATURE = {"EWMA_168h": "ewma_vol_168h"}
SIZING_DIMENSIONS = ("tau", "sigma")
MODEL_DIMENSION = "model."
CODE_IMPORTS = ("math", "numpy")
# TI-2 (S3R3-R1): the builtins trial code runs with (pure computation)
CODE_BUILTINS = (
    "abs", "all", "any", "bool", "dict", "divmod", "enumerate", "filter",
    "float", "frozenset", "int", "isinstance", "len", "list", "map", "max",
    "min", "pow", "range", "reversed", "round", "set", "slice", "sorted",
    "str", "sum", "tuple", "zip", "True", "False", "None",
    "__build_class__", "object", "staticmethod", "property",
    "ArithmeticError", "Exception", "IndexError", "KeyError",
    "OverflowError", "TypeError", "ValueError", "ZeroDivisionError",
)  # fmt: skip
CODE_FORBIDDEN_NAMES = (
    "__import__", "importlib", "exec", "eval", "compile", "open", "__builtins__",
    # numpy file input and output (S3R2-R1)
    "load", "save", "savez", "savez_compressed", "loadtxt", "savetxt",
    "genfromtxt", "fromfile", "tofile", "fromregex", "memmap", "DataSource",
    "lib", "ctypeslib",
    # numpy submodules and helpers that can read files or run tools (S3R5-R1)
    "f2py", "testing", "rec", "ma", "dump", "dumps", "loads", "show_config",
    "show_runtime", "info",
)  # fmt: skip
_HEX = frozenset("0123456789abcdef")


class TrialError(ValueError):
    """A declaration the screen refuses; the set cannot be declared."""


def _scalar(value: object, name: str) -> None:
    if value is not None and type(value) not in (bool, int, str):
        raise TrialError(f"{name}: scalars only (decimals as strings), got {value!r}")


def _code_ref(value: object, name: str) -> None:
    parts = value.split(":") if isinstance(value, str) else []
    if len(parts) != 2 or not all(x.isidentifier() for x in parts):
        raise TrialError(f"{name} must be 'module:function', top-level, got {value!r}")


def _sha256_hex(value: object, name: str) -> None:
    if not (isinstance(value, str) and len(value) == 64 and set(value) <= _HEX):
        raise TrialError(f"{name} must be a lowercase SHA-256 hex digest")


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TrialError(f"{name} must be a non-empty string")


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TrialError(f"{name} must be a mapping")
    for k in value:
        _text(k, f"{name} key")
    return value


def _typed(value: object) -> tuple[str, object]:
    return type(value).__name__, value


def check_trial(trial: dict[str, Any]) -> None:
    """TI-1..TI-6: refuse (TrialError) any declaration outside the interface."""
    if not isinstance(trial, dict) or set(trial) != set(TRIAL_FIELDS):
        raise TrialError(f"fields must be exactly {TRIAL_FIELDS}")
    _text(trial["trial_id"], "trial_id")
    if trial["family"] not in FAMILIES:
        raise TrialError(f"family must be one of {FAMILIES}")
    _code_ref(trial["signal"], "signal")
    _sha256_hex(trial["signal_sha256"], "signal_sha256")
    if trial["overlay"] is None:
        if trial["overlay_sha256"] is not None:
            raise TrialError("overlay_sha256 without an overlay")
    else:
        _code_ref(trial["overlay"], "overlay")
        _sha256_hex(trial["overlay_sha256"], "overlay_sha256")
    if trial["tau"] not in TAUS:
        raise TrialError(f"tau must be one of {TAUS}")
    sigmas = allowed_sigmas(trial)
    if trial["sigma"] not in sigmas:
        raise TrialError(f"sigma must be one of {sigmas} in family {trial['family']}")
    if trial["g11_class"] not in G11_CLASSES:
        raise TrialError(f"g11_class must be one of {G11_CLASSES}")
    model = trial["model"]
    if model is not None:
        model = _mapping(model, "model")
        if set(model) != {"id", "class", "params", "target", "features"}:
            raise TrialError(
                "model must be null or {id, class, params, target, features}"
            )
        _text(model["id"], "model id")
        if model["class"] not in MODEL_CLASSES:
            raise TrialError(f"model class must be one of {MODEL_CLASSES}")
        if model["target"] not in MODEL_TARGETS:
            raise TrialError(f"model target must be one of {MODEL_TARGETS}")
        if (model["class"] == "logistic") != (model["target"] == MODEL_TARGETS[1]):
            raise TrialError(
                "logistic needs, and only logistic may use, the sign target"
            )
        for k, v in _mapping(model["params"], "model params").items():
            _scalar(v, f"model params {k}")
            check_model_param(model["class"], k, v)
        check_model_features(trial)
        w = trial["warmup_hours"]
        if type(w) is int and w < MODEL_WARMUP_HOURS:  # S6A-R1, S6AR-R1, WF-2
            raise TrialError(
                f"a model trial needs warmup_hours >= {MODEL_WARMUP_HOURS}"
            )
    h = trial["horizon_hours"]
    if type(h) is not int or h not in HORIZONS_HOURS:
        raise TrialError(f"horizon_hours must be one of {HORIZONS_HOURS}")
    w = trial["warmup_hours"]
    if type(w) is not int or w < 0:
        raise TrialError("warmup_hours must be an integer >= 0")
    point = _mapping(trial["parameter_point"], "parameter_point")
    grid = _mapping(trial["grid"], "grid")
    if set(point) != set(grid):
        raise TrialError("parameter_point and grid must map the same names")
    for k, v in point.items():
        _scalar(v, f"parameter_point {k}")
        values = grid[k]
        if not isinstance(values, list) or not values:
            raise TrialError(f"grid {k} must be a non-empty list")
        for x in values:
            _scalar(x, f"grid {k}")
        keys = [(type(x).__name__, x) for x in values]
        if len(set(keys)) != len(keys) or (type(v).__name__, v) not in keys:
            raise TrialError(f"grid {k} must hold distinct values including the point")
    allowed = {"tau": TAUS, "sigma": sigmas}
    for k in SIZING_DIMENSIONS:
        if k in point and (point[k] != trial[k] or not set(grid[k]) <= set(allowed[k])):
            raise TrialError(f"grid {k} must hold allowed values, the point = {k}")
    model_keys = set(model["params"]) if model is not None else set()
    for k, v in point.items():
        if k in model_keys:
            raise TrialError(f"parameter_point {k} is a model param: use model.{k}")
        if k.startswith(MODEL_DIMENSION):
            name = k[len(MODEL_DIMENSION) :]
            if name not in model_keys or _typed(model["params"][name]) != _typed(v):
                raise TrialError(f"{k} must be a model param with the point's value")
            for x in grid[k]:
                check_model_param(model["class"], name, x)
    check_s_inputs(trial)


def allowed_sigmas(trial: dict[str, Any]) -> tuple[str, ...]:
    return VOL_SIGMAS if trial["family"] == "vol" else (DEFAULT_SIGMA,)


def check_s_inputs(trial: dict[str, Any]) -> None:
    """TI-3 (REG (A), D-20 B5): the identity mapping's enforcement."""
    names = trial["s_inputs"]
    if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
        raise TrialError("s_inputs must be a list of names")
    if len(set(names)) != len(names):
        raise TrialError("s_inputs repeats a name")
    model = trial["model"]
    own_model = {f"model:{model['id']}"} if isinstance(model, dict) else set()
    banned = {SIGMA_HAT, SIGMA_IDENTICAL_FEATURE.get(trial["sigma"], SIGMA_HAT)}
    for n in names:
        if n in banned:
            raise TrialError(
                f"s_inputs may not contain {n!r} (sized by {trial['sigma']})"
            )
        if n not in FEATURE_NAMES and n not in own_model:
            raise TrialError(
                f"s_inputs {n!r} is not a frozen feature or the trial's model"
            )


def trial_sha256(trial: dict[str, Any]) -> str:
    check_trial(trial)
    return sha(trial)


def trial_set_sha256(trials: list[dict[str, Any]]) -> str:
    """TI-1: the §7.2 seed input."""
    if not 1 <= len(trials) <= MAX_TRIALS:
        raise TrialError(f"a trial set has 1 to {MAX_TRIALS} trials")
    hashes = [trial_sha256(t) for t in trials]
    if len({t["trial_id"] for t in trials}) != len(trials):
        raise TrialError("trial_ids repeat")
    return sha({"trials": hashes})


def g14_applies(trial: dict[str, Any]) -> bool:
    """TI-5: G-14 is mandatory for a model trial, a frozen N/A otherwise."""
    return trial["model"] is not None


def signal_params(trial: dict[str, Any]) -> dict[str, Any]:
    """TI-2: what the signal receives besides its inputs."""
    point: dict[str, Any] = trial["parameter_point"]
    return {
        k: v
        for k, v in point.items()
        if k not in SIZING_DIMENSIONS and not k.startswith(MODEL_DIMENSION)
    }


def model_params(trial: dict[str, Any]) -> dict[str, Any]:
    """TI-6: the fit's parameters, with the point's `model.` values."""
    point: dict[str, Any] = trial["parameter_point"]
    fit = dict(trial["model"]["params"])
    for k, v in point.items():
        if k.startswith(MODEL_DIMENSION):
            fit[k[len(MODEL_DIMENSION) :]] = v
    return fit


def check_code(source: bytes, name: str) -> None:
    """TI-2: a self-contained module importing only `CODE_IMPORTS`."""
    try:
        tree = ast.parse(source, name)
    except SyntaxError as e:
        raise TrialError(f"{name} does not parse: {e}") from e
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                raise TrialError(f"{name}: relative import")
            if node.module != "__future__":  # S3R5-R1: no from-import at all
                raise TrialError(
                    f"{name} imports from {node.module}; only 'import math' and"
                    " 'import numpy' are allowed"
                )
            roots = []
        else:
            roots = []
        bad = [r for r in roots if r not in CODE_IMPORTS and r != "__future__"]
        if bad:
            raise TrialError(f"{name} imports {bad}; only {CODE_IMPORTS} allowed")
        ident = node.id if isinstance(node, ast.Name) else getattr(node, "attr", None)
        if ident in CODE_FORBIDDEN_NAMES:
            raise TrialError(f"{name} uses {ident}")


def _code_import(
    name: str,
    globals: Mapping[str, object] | None = None,
    locals: Mapping[str, object] | None = None,
    fromlist: Sequence[str] = (),
    level: int = 0,
) -> types.ModuleType:
    """TI-2: the only import trial code gets."""
    if level or name not in (*CODE_IMPORTS, "__future__"):
        raise ImportError(f"trial code may import only {CODE_IMPORTS}, not {name}")
    if fromlist and name != "__future__":  # S3R5-R1: from numpy import f2py
        raise ImportError(f"trial code may not import names from {name}")
    return builtins.__import__(name, globals, locals, fromlist, level)


def _code_builtins() -> dict[str, object]:
    out: dict[str, object] = {n: getattr(builtins, n) for n in CODE_BUILTINS}
    out["__import__"] = _code_import
    return out


def load(ref: str, sha256: str) -> Callable[..., Any]:
    """TI-2: compile exactly the hashed source into a fresh, unregistered
    module and return its function."""
    module_name, function = ref.split(":")
    if not module_name.isidentifier():
        raise TrialError(f"{module_name} must be a top-level module")
    spec = importlib.util.find_spec(module_name)
    if spec is None or spec.origin is None or not spec.origin.endswith(".py"):
        raise TrialError(f"no Python source for {module_name}")
    source = Path(spec.origin).read_bytes()
    if hashlib.sha256(source).hexdigest() != sha256:
        raise TrialError(f"{module_name} is not the declared source")
    check_code(source, module_name)
    module = types.ModuleType(module_name)
    module.__file__ = spec.origin
    module.__dict__["__builtins__"] = _code_builtins()
    exec(compile(source, spec.origin, "exec"), module.__dict__)  # noqa: S102
    fn: object = module.__dict__.get(function)
    if not callable(fn):
        raise TrialError(f"{ref} is not a function")
    return fn


def signal_inputs(
    trial: dict[str, Any], available: Mapping[str, np.ndarray]
) -> dict[str, np.ndarray]:
    """TI-2: exactly the declared `s_inputs`, nothing else."""
    missing = [n for n in trial["s_inputs"] if n not in available]
    if missing:
        raise TrialError(f"declared inputs not available: {missing}")
    return {n: available[n] for n in trial["s_inputs"]}


def class_mismatch(trial: dict[str, Any], s: np.ndarray) -> bool:
    """TI-7: a constant_signal trial whose s is not identical at every hour."""
    return trial["g11_class"] == "constant_signal" and bool(np.any(s != s[0]))


def overlay_violation(target: np.ndarray, out: np.ndarray) -> bool:
    """TI-8: an overlay output that is neither the target nor 0, hour by hour."""
    return out.shape != target.shape or bool(np.any((out != target) & (out != 0)))


# --- S5: G-11 shifts (Annex C C-10 (3), D-20 B3, B6) ------------------------
#
# Readings GS-n (proposed, for review):
# - GS-1 Inside the screen the null-stream trial seed is
#   `SHA256(cj({"path": p, "screen_seed": <hex>, "trial_id": <id>}))`
#   (`screen_trial_seed`, C-10 (3) "Inside the D-19 screen"), and
#   `evaluation_window_id` is the C2 cycle's C-0 window id, which the
#   declaration fixes and the caller passes as its canonical
#   `["<w0>","<w1>"]` string.
# - GS-2 `g11_seed` is the SHA-256 of `json.dumps([SEED_DOMAIN,
#   trial_seed_hex, CONVENTION_DOCUMENT_SHA256, "random_exposure_null",
#   "BTCUSDT", "1.0", evaluation_window_id, 500], separators=(",", ":"),
#   ensure_ascii=False)`, with `SEED_DOMAIN` and the convention hash taken
#   from `aqt.metrics.statistics` (the R-8 bound module); "1.0" is a string,
#   as the annex writes it.
# - GS-3 One CPython `random.Random`, seeded with the seed's 256-bit
#   integer; `_draw(n)` is `bootstrap_indices`' rejection sampling on
#   `getrandbits(n.bit_length())`; with `P = [m, ..., T - m]`, for i = 0..499,
#   `j = i + _draw(len(P) - i)`, swap `P[i]`, `P[j]`, `k_i = P[i]`.
# - GS-4 `m = max(g, 30)`; the gate is available only if `T - 2m >= 499`
#   (then `P` has at least 500 values); otherwise `GateUnavailable` with
#   reason `INSUFFICIENT_SHIFT_RANGE`. `T` and `g` are whole days.
# - GS-5 Reference vectors (frozen in the unit test, exact on every CPython:
#   Mersenne Twister and integer seeding are stable): the first 10 `k_i` and
#   `g11_shifts_sha256` = `sha({"k": [k_0, ..., k_499]})` for fixed inputs.

G11_DRAWS = 500
G11_FLOOR_DAYS = 30
G11_PURPOSE = "random_exposure_null"
G11_ASSET = "BTCUSDT"
G11_COST = "1.0"


class GateUnavailable(Exception):
    """A screened gate cannot be computed; `reason` is its cause code."""

    def __init__(self, gate: str, reason: str) -> None:
        super().__init__(f"{gate} UNAVAILABLE: {reason}")
        self.gate = gate
        self.reason = reason


def screen_trial_seed(seed: str, p: int, trial_id: str) -> str:
    """GS-1: the null-stream trial seed of trial `trial_id` on path `p`."""
    return sha({"path": p, "screen_seed": seed, "trial_id": trial_id})


def g11_seed(trial_seed_hex: str, window_id: str) -> str:
    """GS-2."""
    material = json.dumps(
        [
            st.SEED_DOMAIN,
            trial_seed_hex,
            st.CONVENTION_DOCUMENT_SHA256,
            G11_PURPOSE,
            G11_ASSET,
            G11_COST,
            window_id,
            G11_DRAWS,
        ],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _draw(generator: random.Random, n: int) -> int:
    """GS-3: `bootstrap_indices`' uniform draw in [0, n)."""
    drawn = generator.getrandbits(n.bit_length())
    while drawn >= n:
        drawn = generator.getrandbits(n.bit_length())
    return drawn


def g11_shifts(
    trial_seed_hex: str, window_id: str, t_days: int, g_days: int
) -> list[int]:
    """GS-3, GS-4: the 500 day shifts `k_i`, or `GateUnavailable`."""
    m = max(g_days, G11_FLOOR_DAYS)
    if t_days - 2 * m < G11_DRAWS - 1:
        raise GateUnavailable("G-11", "INSUFFICIENT_SHIFT_RANGE")
    seed = g11_seed(trial_seed_hex, window_id)
    generator = random.Random(int.from_bytes(bytes.fromhex(seed), "big"))
    pool = list(range(m, t_days - m + 1))
    for i in range(G11_DRAWS):
        j = i + _draw(generator, len(pool) - i)
        pool[i], pool[j] = pool[j], pool[i]
    return pool[:G11_DRAWS]


def g11_shifts_sha256(shifts: list[int]) -> str:
    """GS-5."""
    return sha({"k": shifts})


# --- S4b: trial runs on a screen path; G-3, G-5, G-6, G-7 -------------------
#
# Readings RN-n (proposed, for review):
# - RN-1 A screen path has `warmup_hours + window_hours + 1` hours: the last
#   window decision's segment needs one more open (C-6 (1)). Bar `i` opens
#   at `w0 + (i - warmup_hours)` hours, so instant `warmup_hours` is `w0`.
# - RN-2 The decision at instant `j` reads the feature row of decision bar
#   `j - 1` (`feature_columns`, bit-identical to `compute_features`). The
#   sizing estimator `EWMA_168h` is that row's `ewma_vol_168h`, the same
#   number as the canonical estimator by construction (canonical
#   `annualized_forecast_volatility`). The other protocol estimators have no
#   bound hourly definition yet: a trial sized by one of them is refused
#   (`SIGMA_UNBOUND`) until one is bound.
# - RN-3 Per hour: `s = signal(row, params, state)` with `row` holding only
#   the trial's `s_inputs` for this hour; `target = clip(s * tau /
#   sigma_hat, 0, 1)`; then `overlay(target, market, state)` with `market`
#   every feature and the close for this hour. Trial code is loaded afresh
#   for every run (fresh module globals) and gets fresh state dicts, so no
#   run sees another run's rows (S4B-R1). Each hour, before trial code is
#   called, every value it will receive and `sigma_hat` must be finite, and
#   `sigma_hat` positive (`INVALID_SERIES`; C-7 (2) for the lagged run,
#   input integrity otherwise; S4B-R4; disclosed: the overlay receives every
#   feature, so a non-finite feature it does not read still counts). Then
#   `s` must be finite and >= 0 (`INVALID_SERIES`, `NEGATIVE_SIGNAL`, C-10
#   (1); S4B-R2), the pre-clip product finite, trial code must not raise
#   (`TRIAL_CODE_ERROR`), and the overlay must return the target or 0
#   (`OVERLAY_VIOLATION`, TI-8).
# - RN-3a (S4B-R3) A `constant_signal` trial's `s` is compared with its first
#   value at every hour of every run (`class_mismatch`); a mismatch in any run
#   makes G-11 `CLASS_MISMATCH` (C-10 (2)). Each run's `s` series is kept for
#   the G-11 draws (slice S5 runs).
# - RN-4 The benchmark leg is `vol_target_exposure(ewma_vol_168h)` of the
#   same row, run under the same cost multiplier and delay as the candidate,
#   and never feature-lagged (C-0, C-5, C-7).
# - RN-5 Daily returns: equity at each 00:00 instant of the window (initial
#   equity 1 at `w0`), one return per complete UTC day; E-IMPROV is
#   `paired_sharpe_statistics(candidate, benchmark).paired_sharpe_improvement`
#   (R-8 code); `None` makes the statistic unavailable with its reason.
#   `DD` uses each leg's hourly equity path over the window (`max_drawdown`'s
#   rule, `descriptive._max_drawdown`); net return is final equity - 1.
# - RN-6 Gates, screened for availability only (§7.2): G-3 on the ETH
#   baseline run; G-5 on the BTC run with both legs at 2x; G-7 on the BTC run
#   with both legs delayed one instant; G-6 on the BTC run whose candidate
#   reads the row of bar `j - 2` (its inputs at `t - 1h`) for `s`, the sizing
#   estimator and the overlay, with the benchmark not lagged (C-7 (2)). Each
#   of G-5..G-7 also needs G-3. Model trials run since slice S6b (MR-n).
#   `screen_gates` reports availability only; PASS or FAIL is not part of
#   the screen's outcome (§7.2 "Outcome").
# - RN-7 Null paths carry synthetic timestamps, so the frozen 10 bps fee
#   fallback applies (`fees=None`).

GATES_S4B = ("G-3", "G-5", "G-6", "G-7")
STRESS_COST = 2.0

# --- S4c: G-8 (Annex C C-8) -------------------------------------------------
#
# Readings PL-n (proposed, for review):
# - PL-1 (owner decision 2026-10-17, `OWNER_DECISION_G8_RULE_SETTINGS.md`)
#   The ordered numeric tunable dimensions are the trial's grid dimensions
#   other than `tau` and `sigma` (structural: vol target and the categorical
#   sizing estimator; the horizon is not a grid dimension) whose grid values
#   are all numeric: an `int` (not `bool`) or a decimal string, with at
#   least two values. Signal parameters and `model.<name>` parameters both
#   count. A single-value grid entry is a fixed constant, not a tuned
#   dimension (S4C-R3: it has no neighbour and was not chosen among
#   alternatives; reading it as a boundary would make every fixed constant a
#   G-8 FAIL).
# - PL-2 Values are ordered by their exact decimal value; a +/-1-step
#   neighbour is the adjacent value in that order, present in the grid. The
#   neighbour runs change one dimension at a time, through the same
#   `signal_params` / `model_params` path as the selected point (TI-6).
# - PL-3 The screen needs availability only (§7.2): G-8 is `N/A` (`NA`, a
#   frozen N/A, not unavailability) without such a dimension (C-8 step 1),
#   decided before anything else, so a trial still `MODEL_PENDING` or
#   `SIGMA_UNBOUND` gets it too (S4C-R1); and `UNAVAILABLE` if the selected
#   point's or any present neighbour's BTC E-IMPROV, on the baseline run,
#   cannot be computed or is not finite (C-8 step 2, with the cause of the
#   first failing run; S4C-R2). C-8 steps 3 and 4 (FAIL / PASS) are
#   not part of the screen's outcome.
# - PL-4 Gate results in `screen_gates`: `None` available, `NA` frozen N/A,
#   any other string the unavailability reason.

NA = "N/A"
GATES_S4 = (*GATES_S4B, "G-8")
GATES = (*GATES_S4, "G-11", "G-14")

# --- S5b: G-11 runs (Annex C C-10 (4)-(7)) ----------------------------------
#
# Readings GR-n (proposed, for review):
# - GR-1 The candidate's BTC baseline run (lag 0, 1x, no delay) gives its `s`
#   series over the window's `24T` hours (`T` = window days) and its
#   E-IMPROV against the benchmark leg, which every draw shares (C-10 (5)).
# - GR-2 Draw `i` with shift `k_i` days (S5 `g11_shifts`, with `g` the C2
#   gap the declaration fixes, passed in as `g_days`): `s'_h =
#   s_((h + 24 k_i) mod 24T)`; `target_h = overlay(clip(s'_h * tau /
#   sigma_hat_h, 0, 1))` with `sigma_hat_h` and the overlay's market row at
#   the real hour, the overlay loaded afresh (fresh state and globals); then
#   the C-6 baseline run from `w0`, flat, unset clock (C-10 (4)).
# - GR-3 Availability (C-10 (6)): the candidate's run must be available (its
#   `s`, `sigma_hat`, products and overlay are checked there, RN-3), the
#   shift range must exist (`INSUFFICIENT_SHIFT_RANGE`), and every draw's
#   E-IMPROV must exist; the first failure's reason is reported. Whole days
#   are guaranteed by `screen_gates`' window check. `constant_signal`
#   trials are a frozen N/A, unless a run finds their `s` not constant
#   (`CLASS_MISMATCH`, C-10 (2)). PASS (476 of 500 strictly below) is not
#   computed.


def _decimal(value: object) -> Decimal | None:
    if type(value) is int:
        return Decimal(value)
    if isinstance(value, str):
        try:
            d = Decimal(value)
        except InvalidOperation:
            return None
        return d if d.is_finite() else None
    return None


def plateau_dimensions(trial: dict[str, Any]) -> dict[str, list[Any]]:
    """PL-1, PL-2: each ordered numeric tunable dimension's grid, in order."""
    out = {}
    for name, values in trial["grid"].items():
        if name in SIZING_DIMENSIONS:
            continue
        maybe = [_decimal(v) for v in values]
        keys = [k for k in maybe if k is not None]
        if len(keys) == len(values) >= 2:
            if len(set(keys)) != len(keys):  # e.g. 1 and "1.0": no order
                raise TrialError(f"grid {name} repeats a number")
            ranked = sorted(range(len(values)), key=keys.__getitem__)
            out[name] = [values[i] for i in ranked]
    return out


def plateau_neighbours(trial: dict[str, Any]) -> list[dict[str, Any]]:
    """PL-2: the trials at every present +/-1-step neighbour."""
    out = []
    point = trial["parameter_point"]
    for name, ordered in plateau_dimensions(trial).items():
        i = next(k for k, v in enumerate(ordered) if _typed(v) == _typed(point[name]))
        for j in (i - 1, i + 1):
            if 0 <= j < len(ordered):
                moved = dict(point)
                moved[name] = ordered[j]
                if name.startswith(MODEL_DIMENSION):
                    model = dict(trial["model"])
                    model["params"] = {
                        **model["params"],
                        name[len(MODEL_DIMENSION) :]: ordered[j],
                    }
                    out.append({**trial, "parameter_point": moved, "model": model})
                else:
                    out.append({**trial, "parameter_point": moved})
    return out


class RunUnavailable(Exception):
    """A run, or the statistic on it, cannot be computed; `reason` says why."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def path_series(path: np.ndarray, s: int, start: datetime) -> BarSeries:
    """RN-1: symbol `s` of a screen path as an hourly series from `start`."""
    rows = path[:, s]
    return BarSeries(
        SYMBOLS[s],
        tuple(
            Bar(
                start + timedelta(hours=i),
                float(rows[i][OPEN]),
                float(rows[i][HIGH]),
                float(rows[i][LOW]),
                float(rows[i][CLOSE]),
                float(rows[i][VOLUME]),
            )
            for i in range(len(rows))
        ),
    )


def leg_targets(
    trial: dict[str, Any],
    signal: Callable[..., Any],
    overlay: Callable[..., Any] | None,
    columns: Mapping[str, tuple[float, ...]],
    first: int,
    closes: Sequence[float],
    j0: int,
    n: int,
    lag: int,
) -> tuple[list[float], list[float]]:
    """RN-2, RN-3: the candidate's targets and `s` at instants `j0 .. j0 + n
    - 1`, reading the row of bar `j - 1 - lag`."""
    tau = float(trial["tau"])
    params = signal_params(trial)
    s_state: dict[str, Any] = {}
    o_state: dict[str, Any] = {}
    names = trial["s_inputs"]
    out: list[float] = []
    signals: list[float] = []
    for j in range(j0, j0 + n):
        k = j - 1 - lag - first
        if k < 0:
            raise RunUnavailable("INSUFFICIENT_WARMUP")
        sigma_hat = columns["ewma_vol_168h"][k]
        row = {m: columns[m][k] for m in names}
        if not all(map(math.isfinite, row.values())):
            raise RunUnavailable("INVALID_SERIES")
        if not math.isfinite(sigma_hat) or sigma_hat <= 0:
            raise RunUnavailable("INVALID_SERIES")
        try:
            s = float(signal(row, params, s_state))
        except Exception as e:  # trial code: any failure is unavailability
            raise RunUnavailable("TRIAL_CODE_ERROR") from e
        if not math.isfinite(s):
            raise RunUnavailable("INVALID_SERIES")
        if s < 0:
            raise RunUnavailable("NEGATIVE_SIGNAL")
        signals.append(s)
        product = s * tau / sigma_hat
        if not math.isfinite(product):
            raise RunUnavailable("INVALID_SERIES")
        target = min(1.0, max(0.0, product))
        if overlay is not None:
            market = {m: columns[m][k] for m in FEATURE_NAMES}
            market["close"] = closes[j - 1 - lag]
            if not all(map(math.isfinite, market.values())):
                raise RunUnavailable("INVALID_SERIES")
            try:
                kept = float(overlay(target, market, o_state))
            except Exception as e:
                raise RunUnavailable("TRIAL_CODE_ERROR") from e
            if kept not in (target, 0.0):
                raise RunUnavailable("OVERLAY_VIOLATION")
            target = kept
        out.append(target)
    return out, signals


def g11_targets(
    trial: dict[str, Any],
    overlay: Callable[..., Any] | None,
    signals: Sequence[float],
    columns: Mapping[str, tuple[float, ...]],
    first: int,
    closes: Sequence[float],
    j0: int,
    n: int,
    shift_days: int,
) -> list[float]:
    """GR-2: the targets of the G-11 draw with shift `shift_days`."""
    tau = float(trial["tau"])
    state: dict[str, Any] = {}
    out = []
    for i in range(n):
        k = j0 + i - 1 - first
        sigma_hat = columns["ewma_vol_168h"][k]
        product = signals[(i + 24 * shift_days) % n] * tau / sigma_hat
        if not math.isfinite(product):
            raise RunUnavailable("INVALID_SERIES")
        target = min(1.0, max(0.0, product))
        if overlay is not None:
            market = {m: columns[m][k] for m in FEATURE_NAMES}
            market["close"] = closes[j0 + i - 1]
            try:
                kept = float(overlay(target, market, state))
            except Exception as e:
                raise RunUnavailable("TRIAL_CODE_ERROR") from e
            if kept not in (target, 0.0):
                raise RunUnavailable("OVERLAY_VIOLATION")
            target = kept
        out.append(target)
    return out


def benchmark_targets(
    columns: Mapping[str, tuple[float, ...]], first: int, j0: int, n: int
) -> list[float]:
    """RN-4."""
    try:
        return [
            vol_target_exposure(columns["ewma_vol_168h"][j - 1 - first])
            for j in range(j0, j0 + n)
        ]
    except (CanonicalBenchmarkError, IndexError) as e:
        raise RunUnavailable("BENCHMARK_INVALID") from e


def daily_returns(result: EventResult) -> list[float]:
    """RN-5: one return per complete UTC day, from 00:00 to 00:00."""
    marks = [1.0, *result.equity[23::24]]
    return [b / a - 1.0 for a, b in zip(marks, marks[1:], strict=False)]


def leg_stats(candidate: EventResult, benchmark: EventResult) -> dict[str, float]:
    """RN-5: E-IMPROV, the drawdown difference and the candidate's net return."""
    paired = st.paired_sharpe_statistics(
        daily_returns(candidate), daily_returns(benchmark)
    )
    improvement = paired.paired_sharpe_improvement
    if improvement is None or not math.isfinite(improvement):  # S4C-R2
        raise RunUnavailable(paired.reason or "E_IMPROV_UNAVAILABLE")
    mdd = [_max_drawdown((1.0, *r.equity)) for r in (candidate, benchmark)]
    return {
        "e_improv": improvement,
        "dd_excess": mdd[0] - mdd[1],
        "net_return": candidate.final_equity - 1.0,
    }


def screen_gates(
    trial: dict[str, Any],
    path: np.ndarray,
    w0: datetime,
    window_hours: int,
    trial_seed: str | None = None,
    window_id: str | None = None,
    g_days: int | None = None,
) -> dict[str, str | None]:
    """RN-6, PL-4, G14-n: each gate's result on one path. G-14 (a model
    trial) needs the null-stream `trial_seed` and the C2 `window_id`
    (G14-1)."""
    check_trial(trial)
    warmup = trial["warmup_hours"]
    if window_hours < 48 or window_hours % 24 or len(path) != warmup + window_hours + 1:
        raise TrialError("path length must be warmup + whole window days + 1 hour")
    g8_na = {} if plateau_dimensions(trial) else {"G-8": NA}  # PL-3, S4C-R1
    if trial["model"] is not None and warmup < model_warmup_hours(w0):  # MR-4
        raise TrialError(
            f"a model trial needs warmup_hours >= {model_warmup_hours(w0)}"
        )
    g14_na = {} if g14_applies(trial) else {"G-14": NA}  # C-12 (1)
    g11_na = {"G-11": NA} if trial["g11_class"] == "constant_signal" else {}
    if not g14_na and (trial_seed is None or window_id is None):
        raise TrialError("G-14 needs the trial seed and the window id (G14-1)")
    if not g11_na and (trial_seed is None or window_id is None or g_days is None):
        raise TrialError("G-11 needs the trial seed, the window id and g (GR-2)")
    if trial["sigma"] != DEFAULT_SIGMA:
        return {
            **dict.fromkeys(GATES, "SIGMA_UNBOUND"),
            **g8_na,
            **g11_na,
            **g14_na,
        }
    start = w0 - timedelta(hours=warmup)
    prepared: dict[int, tuple[BarSeries, int, dict[str, tuple[float, ...]]]] = {}
    emissions: dict[tuple[int, int, str], list[float]] = {}

    sigmas: dict[int, tuple[float, ...]] = {}

    def prepare(s: int) -> tuple[BarSeries, int, dict[str, tuple[float, ...]]]:
        if s not in prepared:  # features and cost volatility once per symbol
            series = path_series(path, s, start)
            try:
                prepared[s] = (series, *feature_columns(series))
                sigmas[s] = ewma_hourly_volatility_bps_series(
                    hourly_log_returns_bps(series)
                )
            except (FeatureFactoryError, CostModelError) as e:
                raise RunUnavailable("FEATURES_UNAVAILABLE") from e
        return prepared[s]

    def inputs(
        s: int, lag: int, at: dict[str, Any]
    ) -> tuple[BarSeries, int, dict[str, tuple[float, ...]]]:
        series, first, columns = prepare(s)
        if at["model"] is not None:  # MR-1..MR-3
            key = (s, lag, json.dumps(model_params(at), sort_keys=True))
            if key not in emissions:
                emissions[key] = model_column(
                    at, series, first, columns, warmup, window_hours, lag
                )
            columns = {**columns, f"model:{at['model']['id']}": tuple(emissions[key])}
        return series, first, columns

    def contract(
        series: BarSeries, s: int, targets: list[float], **kw: Any
    ) -> EventResult:
        try:
            return run_event_contract(
                series, targets, warmup, sigma_bps=sigmas[s], **kw
            )
        except (EventContractError, CostModelError) as e:
            raise RunUnavailable("RUN_INVALID") from e

    def run(
        s: int,
        cost: float = 1.0,
        delay: int = 0,
        lag: int = 0,
        at: dict[str, Any] = trial,
    ) -> dict[str, float]:
        series, first, columns = inputs(s, lag, at)
        closes = [b.close for b in series.bars]
        signal = load(at["signal"], at["signal_sha256"])  # fresh per run
        overlay = (
            None if at["overlay"] is None else load(at["overlay"], at["overlay_sha256"])
        )
        candidate, signals = leg_targets(
            at, signal, overlay, columns, first, closes, warmup, window_hours, lag
        )
        if class_mismatch(at, np.asarray(signals)):
            mismatched.append(s)
        legs = [
            contract(series, s, targets, stress_multiplier=cost, delay=delay)
            for targets in (
                candidate,
                benchmark_targets(columns, first, warmup, window_hours),
            )
        ]
        return leg_stats(*legs)

    def g11_check(seed: Any, wid: Any, g: Any) -> None:
        """GR-1..GR-3."""
        series, first, columns = inputs(0, 0, trial)
        closes = [b.close for b in series.bars]
        signal = load(trial["signal"], trial["signal_sha256"])
        overlay = (
            None
            if trial["overlay"] is None
            else load(trial["overlay"], trial["overlay_sha256"])
        )
        candidate, signals = leg_targets(
            trial, signal, overlay, columns, first, closes, warmup, window_hours, 0
        )
        bench = contract(
            series, 0, benchmark_targets(columns, first, warmup, window_hours)
        )
        leg_stats(contract(series, 0, candidate), bench)
        try:
            shifts = g11_shifts(seed, wid, window_hours // 24, g)
        except GateUnavailable as e:
            raise RunUnavailable(e.reason) from e
        for k in shifts:
            fresh = (
                None
                if trial["overlay"] is None
                else load(trial["overlay"], trial["overlay_sha256"])
            )
            targets = g11_targets(
                trial, fresh, signals, columns, first, closes, warmup, window_hours, k
            )
            leg_stats(contract(series, 0, targets), bench)

    def g14_check(seed: Any, wid: Any) -> None:
        """G14-3..G14-5: the nominee's and every draw's IC must exist."""
        series, first, columns = prepare(0)
        bars = series.bars
        hours = trial["horizon_hours"]
        w1 = w0 + timedelta(hours=window_hours)
        pipelines = [None, *((seed, wid, d) for d in range(G14_DRAWS))]
        window: list[int] = []
        ys: list[float] = []
        for draw in pipelines:
            window, preds = walk_forward(
                trial, series, first, columns, warmup, window_hours, 0, draw
            )
            keep = [
                i
                for i, j in enumerate(window)
                if bars[j].open_time + timedelta(hours=hours) < w1
            ]
            if not ys:
                sigma = ewma_hourly_volatility_bps_series(
                    hourly_log_returns_bps(series)
                )
                ys = labels(series, sigma, [window[i] for i in keep], hours)
            spearman_ic([preds[i] for i in keep], ys)

    mismatched: list[int] = []
    out: dict[str, str | None] = {}
    try:
        run(1)
        out["G-3"] = None
    except RunUnavailable as e:
        out["G-3"] = e.reason
    for gate, kwargs in (
        ("G-5", {"cost": STRESS_COST}),
        ("G-6", {"lag": 1}),
        ("G-7", {"delay": 1}),
    ):
        try:
            run(0, **kwargs)
            out[gate] = None if out["G-3"] is None else f"G-3:{out['G-3']}"
        except RunUnavailable as e:
            out[gate] = e.reason
    if g8_na:
        out.update(g8_na)
    else:
        try:
            for at in (trial, *plateau_neighbours(trial)):
                run(0, at=at)
            out["G-8"] = None
        except RunUnavailable as e:
            out["G-8"] = e.reason
    if g11_na:
        out.update(g11_na)
    else:
        try:
            g11_check(trial_seed, window_id, g_days)
            out["G-11"] = None
        except RunUnavailable as e:
            out["G-11"] = e.reason
    if g14_na:
        out.update(g14_na)
    else:
        try:
            g14_check(trial_seed, window_id)
            out["G-14"] = None
        except RunUnavailable as e:
            out["G-14"] = e.reason
    if mismatched:
        out["G-11"] = "CLASS_MISMATCH"
    return out


# --- S6a: walk-forward pieces (SCREEN_S6_DESIGN.md revision 4) -------------
#
# WF-1 labels, WF-2 schedule, WF-3 purge and embargo, WF-4 model features,
# WF-5 classes and the parameter allowlist. The model libraries are imported
# only inside `build_model`, so importing this module loads numpy alone
# (tests/unit/test_d19_deploy.py).

TRAINING_MONTHS = 24  # l.198
# S6A-R1: the most hours 24 calendar months can span (731 days, with a leap
# day) plus the feature history: a model trial's least declarable warm-up
MODEL_WARMUP_HOURS = 731 * 24 + REQUIRED_HISTORY_BARS
REFIT_DAYS = 30  # l.199-200
EMBARGO_LAG_FACTOR = 4  # l.212: max lag 4 * horizon in daily steps
# WF-5: per class, declarable name -> (kind, low, high, low_inclusive)
PARAM_RULES: dict[str, dict[str, tuple[str, int | None, int | None, bool]]] = {
    "linear": {"fit_intercept": ("bool", None, None, True)},
    "ridge": {
        "alpha": ("dec", 0, None, False),
        "fit_intercept": ("bool", None, None, True),
    },
    "lasso": {
        "alpha": ("dec", 0, None, False),
        "fit_intercept": ("bool", None, None, True),
    },
    "elastic_net": {
        "alpha": ("dec", 0, None, False),
        "l1_ratio": ("dec", 0, 1, True),
        "fit_intercept": ("bool", None, None, True),
    },
    "logistic": {
        "C": ("dec", 0, None, False),
        "fit_intercept": ("bool", None, None, True),
    },
    "lightgbm": {
        "n_estimators": ("int", 1, 300, True),
        "max_depth": ("int", 1, 3, True),
        "num_leaves": ("int", 2, 8, True),
        "min_child_samples": ("int", 1, None, True),
        "reg_alpha": ("dec", 0, None, True),
        "reg_lambda": ("dec", 0, None, True),
    },
}


def check_model_param(cls: str, name: str, value: object) -> None:
    """WF-5: refuse a parameter outside the class's allowlist or range."""
    rule = PARAM_RULES[cls].get(name)
    if rule is None:
        raise TrialError(f"{cls} does not accept parameter {name!r}")
    kind, low, high, low_inclusive = rule
    if kind == "bool":
        if type(value) is not bool:
            raise TrialError(f"{cls}.{name} must be a boolean")
        return
    if kind == "int":
        if type(value) is not int:
            raise TrialError(f"{cls}.{name} must be an integer")
        parsed: Decimal | None = Decimal(value)
    else:
        parsed = _decimal(value) if isinstance(value, str) else None
    if parsed is None:
        raise TrialError(f"{cls}.{name} must be a decimal string")
    number = parsed
    if low is not None and (number < low or (number == low and not low_inclusive)):
        raise TrialError(f"{cls}.{name} = {value!r} is below its range")
    if high is not None and number > high:
        raise TrialError(f"{cls}.{name} = {value!r} is above its range")


def check_model_features(trial: dict[str, Any]) -> None:
    """WF-4 (owner decision): the model's features obey the `s_inputs` ban."""
    names = trial["model"]["features"]
    if not isinstance(names, list) or not names:
        raise TrialError("model features must be a non-empty list")
    if not all(isinstance(n, str) for n in names):  # S6A-R4
        raise TrialError("model features must be names")
    if len(set(names)) != len(names):
        raise TrialError("model features repeat a name")
    banned = {SIGMA_HAT, SIGMA_IDENTICAL_FEATURE.get(trial["sigma"], SIGMA_HAT)}
    for n in names:
        if n in banned:
            raise TrialError(f"model features may not contain {n!r}")
        if n not in FEATURE_NAMES:
            raise TrialError(f"model feature {n!r} is not a frozen feature")


def months_before(t: datetime, months: int) -> datetime:
    """WF-2: `t` minus calendar months, same day and time, clamped to the
    month's last day."""
    total = t.year * 12 + (t.month - 1) - months
    year, month = divmod(total, 12)
    month += 1
    last = (date(year + month // 12, month % 12 + 1, 1) - timedelta(days=1)).day
    return t.replace(year=year, month=month, day=min(t.day, last))


def refit_instants(w0: datetime, w1: datetime) -> list[datetime]:
    """WF-2: `w0 + 30k` days while before `w1`."""
    out = []
    r = w0
    while r < w1:
        out.append(r)
        r += timedelta(days=REFIT_DAYS)
    return out


def labels(
    series: BarSeries, sigma_bps: Sequence[float], instants: Sequence[int], hours: int
) -> list[float]:
    """WF-1: `y_t` at each decision instant index `j` (bar `j` opens at `t`):
    `log(close[j - 1 + H] / close[j - 1]) / (sigma_t * sqrt(H))`, sigma_t
    the cost-model EWMA hourly volatility through the close at `t`
    (`sigma_bps[j - 3] / 1e4`, as `costs.trade_cost` and `gap.py` G-2)."""
    bars = series.bars
    out = []
    for j in instants:
        if j < 3 or j - 1 + hours >= len(bars):  # S6A-R3: no wrap-around index
            raise RunUnavailable("INSUFFICIENT_HISTORY")
        sigma = sigma_bps[j - 3] / BPS_PER_UNIT
        if not sigma > 0 or not math.isfinite(sigma):
            raise RunUnavailable("INVALID_SERIES")
        y = math.log(bars[j - 1 + hours].close / bars[j - 1].close) / (
            sigma * math.sqrt(hours)
        )
        if not math.isfinite(y):
            raise RunUnavailable("INVALID_SERIES")
        out.append(y)
    return out


def embargo_days(daily_labels: Sequence[float | None], horizon_days: int) -> int:
    """WF-3: `max(H_days, cutoff)`, the cutoff by `gap.py`'s ACF rule on the
    window's original candidate labels as a calendar-day sequence (`None` for
    a day without a candidate, so lags are calendar lags; S6A-R2), lags up to
    4 * H_days."""
    max_lag = EMBARGO_LAG_FACTOR * horizon_days
    values = list(daily_labels)
    present = [v for v in values if v is not None]
    if len(present) <= max_lag or len(set(present)) < 2:
        raise RunUnavailable("EMBARGO_UNDEFINED")
    lag = gap.cutoff(gap.acf(values, max_lag), len(present))
    return max(horizon_days, lag)


def training_rows(
    decisions: Sequence[datetime],
    ys: Sequence[float],
    refit: datetime,
    hours: int,
) -> list[int]:
    """WF-2, WF-3: positions (into `decisions`) of the rows retained for the
    fit at `refit`: inside `[refit - 24 months, refit)`, label realised by the
    refit (`t + H <= refit`), then `t + E days <= refit`."""
    start = months_before(refit, TRAINING_MONTHS)
    horizon = timedelta(hours=hours)
    candidates = [
        i
        for i, t in enumerate(decisions)
        if start <= t < refit and t + horizon <= refit
    ]
    if not candidates:
        raise RunUnavailable("TRAINING_ROWS")
    by_day = {decisions[i].date(): ys[i] for i in candidates}
    first_day = decisions[candidates[0]].date()
    span = (decisions[candidates[-1]].date() - first_day).days + 1
    daily = [by_day.get(first_day + timedelta(days=d)) for d in range(span)]
    e = embargo_days(daily, hours // 24)
    return [i for i in candidates if decisions[i] + timedelta(days=e) <= refit]


def build_model(cls: str, params: Mapping[str, Any], seed: int) -> Any:
    """WF-5: the one library pipeline of `cls`, with `params` (already
    checked) and the model seed."""
    p: dict[str, Any] = {
        k: float(v) if isinstance(v, str) else v for k, v in params.items()
    }
    if cls == "lightgbm":
        import lightgbm

        return lightgbm.LGBMRegressor(
            objective="regression",
            learning_rate=0.05,
            deterministic=True,
            num_threads=1,
            force_col_wise=True,
            verbose=-1,
            seed=seed,
            **p,
        )
    from sklearn import linear_model  # type: ignore[import-untyped]
    from sklearn.pipeline import make_pipeline  # type: ignore[import-untyped]
    from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]

    estimator: Any
    if cls == "linear":
        estimator = linear_model.LinearRegression(**p)
    elif cls == "ridge":
        estimator = linear_model.Ridge(random_state=seed, **p)
    elif cls == "lasso":
        estimator = linear_model.Lasso(
            max_iter=10000, selection="cyclic", random_state=seed, **p
        )
    elif cls == "elastic_net":
        estimator = linear_model.ElasticNet(
            max_iter=10000, selection="cyclic", random_state=seed, **p
        )
    elif cls == "logistic":
        estimator = linear_model.LogisticRegression(
            l1_ratio=0.0, solver="lbfgs", max_iter=10000, random_state=seed, **p
        )
    else:
        raise TrialError(f"unknown model class {cls!r}")
    return make_pipeline(StandardScaler(), estimator)


def predict(model: Any, cls: str, x: np.ndarray) -> np.ndarray:
    """WF-7: the logistic score is `predict_proba[:, 1]`; else `predict`."""
    if cls == "logistic":
        return np.asarray(model.predict_proba(x)[:, 1], dtype=float)
    return np.asarray(model.predict(x), dtype=float)


def fit_target(cls: str, ys: Sequence[float]) -> np.ndarray:
    """WF-1 (owner decision S6D-R6): logistic class 1 iff y > 0."""
    y = np.asarray(ys, dtype=float)
    return (y > 0).astype(int) if cls == "logistic" else y


# --- S6b: model trials in the screen runs -----------------------------------
#
# Readings MR-n (proposed, for review), on top of the READY S6 design:
# - MR-1 (owner decision 2026-10-17, `OWNER_DECISION_MR1_ETH_OWN_FIT.md`)
#   Every run of a model trial, on either symbol, runs the trial's whole
#   walk-forward on that symbol's own rows; the ETH run (G-3) fits on ETH.
#   G-14's rows stay BTC only (C-12 (2)).
# - MR-2 The nominee's fits use model seed 0. Every allowed configuration
#   (WF-5) is deterministic: the linear family has no randomness, LightGBM runs
#   without bagging or feature subsampling, so the seed cannot change a fit;
#   it is passed for completeness. G-14's null draws use their own seeds
#   (C-12 (5), slice S6c).
# - MR-3 Emissions (WF-6): at every 00:00 window decision (S6B-R1: also
#   those whose label is not yet realised; only training needs realised
#   labels) the latest fit predicts from that decision's feature row,
#   under G-6 the row one hour earlier; the signal's `model:<id>` input at
#   instant `j` is the latest emission at or before `j`. Cost multiplier and
#   execution delay do not change emissions, so G-5 and G-7 reuse the
#   baseline's.
# - MR-4 A model trial whose declared warm-up cannot hold its first training
#   window (24 months before `w0`) plus the feature history is refused at
#   declaration (`TrialError`), as the design says (WF-2). The feature
#   history is exactly `REQUIRED_HISTORY_BARS`: the first training decision
#   `j` reads row `j - 1`, which needs `j - 1 >= REQUIRED_HISTORY_BARS - 1`
#   (S6B-R3; the design's "+ 1" is corrected to this).


def model_warmup_hours(w0: datetime) -> int:
    """MR-4: the least warm-up a model trial needs on a path starting at `w0`."""
    back = w0 - months_before(w0, TRAINING_MONTHS)
    return int(back / timedelta(hours=1)) + REQUIRED_HISTORY_BARS


def walk_forward(
    trial: dict[str, Any],
    series: BarSeries,
    first: int,
    columns: Mapping[str, tuple[float, ...]],
    j0: int,
    n: int,
    lag: int,
    draw: tuple[str, str, int] | None = None,
) -> tuple[list[int], list[float]]:
    """MR-1..MR-3, G14-3: the model's prediction at every 00:00 window
    decision instant (S6B-R1: inference covers the whole window; training
    uses the rows whose label is realised by the refit). `draw` is
    `(trial_seed_hex, window_id, d)` for a G-14 null pipeline."""
    model = trial["model"]
    cls, hours = model["class"], trial["horizon_hours"]
    bars = series.bars
    try:
        sigma_bps = ewma_hourly_volatility_bps_series(hourly_log_returns_bps(series))
    except CostModelError as e:
        raise RunUnavailable("INVALID_SERIES") from e
    train = [
        j
        for j in range(first + 1, len(bars) - hours + 1)
        if bars[j].open_time.hour == 0
    ]
    times = [bars[j].open_time for j in train]
    ys = labels(series, sigma_bps, train, hours)
    names = model["features"]

    def row(k: int) -> list[float]:
        values = [columns[f][k] for f in names]
        if not all(map(math.isfinite, values)):
            raise RunUnavailable("INVALID_SERIES")
        return values

    x = np.array([row(j - 1 - first) for j in train], dtype=float)
    target = fit_target(cls, ys)
    params = model_params(trial)
    w0, w1 = bars[j0].open_time, bars[j0].open_time + timedelta(hours=n)
    window = [j for j in range(j0, j0 + n) if bars[j].open_time.hour == 0]
    refits = refit_instants(w0, w1)
    out: list[float] = []
    for k, r in enumerate(refits):
        until = refits[k + 1] if k + 1 < len(refits) else w1
        rows = training_rows(times, ys, r, hours)
        if len(rows) < 2:
            raise RunUnavailable("TRAINING_ROWS")
        fit_y, seed = target[rows], 0
        if draw is not None:  # G14-3: circular shift within the window
            offset, seed = g14_draw(
                draw[0], draw[1], draw[2], k, len(rows), hours // 24
            )
            fit_y = np.roll(fit_y, -offset)  # label[(r + offset) mod n_w]
        due = [j for j in window if r <= bars[j].open_time < until]
        try:
            fitted = build_model(cls, params, seed=seed)
            fitted.fit(x[rows], fit_y)
            if due:
                xs = np.array([row(j - 1 - lag - first) for j in due], dtype=float)
                out.extend(float(v) for v in predict(fitted, cls, xs))
        except RunUnavailable:
            raise
        except Exception as e:  # any library failure is unavailability
            raise RunUnavailable("MODEL_FIT_ERROR") from e
    return window, out


def model_column(
    trial: dict[str, Any],
    series: BarSeries,
    first: int,
    columns: Mapping[str, tuple[float, ...]],
    j0: int,
    n: int,
    lag: int,
) -> list[float]:
    """MR-3: the hourly `model:<id>` input, indexed like a feature column
    read at lag `lag` (position `j - 1 - lag - first` for instant `j`); each
    emission held to the next 00:00; NaN outside the window."""
    window, preds = walk_forward(trial, series, first, columns, j0, n, lag)
    out = [math.nan] * len(columns[trial["model"]["features"][0]])
    for j, y in zip(window, preds, strict=True):
        for jj in range(j, min(j + 24, j0 + n)):
            out[jj - 1 - lag - first] = y
    return out


# --- S6c: G-14 (Annex C C-12; design WF-7, WF-8) ----------------------------
#
# Readings G14-n (proposed, for review):
# - G14-1 Stream (C-12 (5), "built as in C-10 (3) with purpose
#   "shuffled_labels_null" and trailing indices d, w in place of 500"): the
#   seed is the SHA-256 of `json.dumps([SEED_DOMAIN, trial_seed_hex,
#   CONVENTION_DOCUMENT_SHA256, "shuffled_labels_null", "BTCUSDT", "1.0",
#   evaluation_window_id, d, w], separators=(",", ":"), ensure_ascii=False)`;
#   one `random.Random` per (d, w); `offset = h + draw(n_w - 2h + 1)`, then
#   `model_seed = getrandbits(31)`; `h = horizon_days`. Inside the screen the
#   trial seed is `screen_trial_seed` (S5 GS-1) and the window id the C2
#   window's (GS-1), both passed in by the driver.
# - G14-2 `NO_SHIFT_RANGE` iff a window has `n_w < 2h` (S6D-R4).
# - G14-3 Draw d: in every window, the retained rows' fit labels are the
#   original ones circularly shifted (`label[(r + offset) mod n_w]`, rows in
#   time order; the embargo stays the one computed from original labels,
#   WF-3); the whole pipeline is refit with `model_seed`; the OOS predictions
#   of that window's decisions are kept. For logistic trials the classes are
#   shifted (the class of a shifted label is the shifted class).
# - G14-4 IC (WF-7): one pooled Spearman IC per pipeline, midranks of the
#   predictions against midranks of the continuous target, over the BTC
#   baseline's 00:00 window decisions with `t + H < w1`. A non-finite
#   prediction or target is `NONFINITE_IC_INPUT` (S6C-R1), a constant one
#   `CONSTANT_IC_INPUT`; any fit failure `MODEL_FIT_ERROR`.
# - G14-5 The screen needs availability: the nominee and all 500 draws must
#   each give an IC. PASS (at least 476 strictly below) is not computed.

G14_DRAWS = 500
G14_PURPOSE = "shuffled_labels_null"


def g14_draw(
    trial_seed_hex: str, window_id: str, d: int, w: int, n_w: int, h: int
) -> tuple[int, int]:
    """G14-1, G14-2: `(offset, model_seed)` of draw `d` in window `w`."""
    if n_w < 2 * h:
        raise RunUnavailable("NO_SHIFT_RANGE")
    material = json.dumps(
        [
            st.SEED_DOMAIN,
            trial_seed_hex,
            st.CONVENTION_DOCUMENT_SHA256,
            G14_PURPOSE,
            G11_ASSET,
            G11_COST,
            window_id,
            d,
            w,
        ],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    seed = hashlib.sha256(material.encode("utf-8")).hexdigest()
    generator = random.Random(int.from_bytes(bytes.fromhex(seed), "big"))
    offset = h + _draw(generator, n_w - 2 * h + 1)
    return offset, generator.getrandbits(31)


def g14_grid_sha256(
    trial_seed_hex: str, window_id: str, sizes: Sequence[int], h: int
) -> str:
    """WF-8: the full `d x w` grid's hash, `d`-major."""
    grid = [
        [d, w, *g14_draw(trial_seed_hex, window_id, d, w, n, h)]
        for d in range(G14_DRAWS)
        for w, n in enumerate(sizes)
    ]
    return sha({"grid": grid})


def midranks(values: Sequence[float]) -> np.ndarray:
    """Average ranks (1-based), ties sharing their mean rank."""
    v = np.asarray(values, dtype=float)
    order = np.argsort(v, kind="mergesort")
    ranks = np.empty(len(v))
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman_ic(predictions: Sequence[float], targets: Sequence[float]) -> float:
    """G14-4: the Pearson correlation of the midranks."""
    if not all(map(math.isfinite, [*predictions, *targets])):  # S6C-R1
        raise RunUnavailable("NONFINITE_IC_INPUT")
    if len(set(predictions)) < 2 or len(set(targets)) < 2:
        raise RunUnavailable("CONSTANT_IC_INPUT")
    a, b = midranks(predictions), midranks(targets)
    a, b = a - a.mean(), b - b.mean()
    ic = float((a * b).sum() / math.sqrt((a * a).sum() * (b * b).sum()))
    if not math.isfinite(ic):
        raise RunUnavailable("CONSTANT_IC_INPUT")
    return ic


# --- S7: the screen driver (prereg §7.2 "Runs", "Outcome", "Seed") ---------
#
# Readings DR-n (proposed, for review):
# - DR-1 One path per index `p`, `max(warmup) + window_hours + 1` hours long
#   (§7.2 "Length": the C2 window plus the trials' declared warm-up). A trial
#   with a shorter warm-up runs on the path's last `warmup + window_hours + 1`
#   hours, so every trial's window is the same stretch of the path.
# - DR-2 Trial `t` on path `p` runs `screen_gates` with the null-stream seed
#   `screen_trial_seed(screen_seed, p, trial_id)` (GS-1), the C2 window id and
#   `g` the declaration fixes. Every (trial, path) result is recorded.
# - DR-3 A path that cannot be built (`PathUnavailable`, SP-7) makes every
#   gate of every trial on it `PATH_UNAVAILABLE`. A declaration the
#   interface refuses (`TrialError`), including trial code that does not load
#   from its declared bytes, refuses the whole screen before any run: every
#   trial's code is loaded and checked first (S7-R6).
# - DR-4 A declaration's outcome is `VALID` iff every recorded gate result is
#   available or a frozen N/A; otherwise `INVALID` (P18-1). No `m` is spent.
# - DR-5 The record holds the inputs and their hashes, every run's gate
#   results, the screen's reference vectors and `screen_sha256`, this file's
#   bytes; a declaration record adds the outcome and the posted
#   `qualification_object_sha256` (S7-R3). `record_sha256 = sha(record)` goes
#   into the declaration (§7.2 "Every screen run is recorded and listed").
# - DR-6 Only `declare` makes a declaration record (S7-R3). It first checks
#   the qualification object as `mapping.py` MP-3/MP-4 does, every file of its
#   manifest included (S7-R7): the posted hash, the run definition's engine
#   commit and runtime, and every loaded `calibration`/`aqt` module equal to
#   that commit's, except `mapping.py` and this file, which must equal the
#   object's copies (so `aqt.backtest.event_contract` and
#   `aqt.features.columns` must be in the engine commit, SCREEN_PLAN section
#   3). Then (S7-R2, S7R-R2) its inputs are not the caller's: the window and
#   `g` are the C2 constants the engine fixes (`grid.T_C2 = 1247 - g`,
#   prereg §3.1; `w0` = 2022-01-01 + g, DRAFT `partitions.confirmation.
#   start`), and the bars are rebuilt from the exploration archives, whose
#   manifests must be the run definition's (`exploration_source`). And
#   (S7-R4) the screen's reference vectors must equal those frozen in this
#   file; the float path's vector is frozen from the pinned
#   image (slice S8) and, until then, `declare` refuses.
# - DR-7 `run_screen` alone makes a measurement record (prereg §10's pilot,
#   "one screen of a 20-trial set"): per-run seconds, an availability summary,
#   `measurement_only`, and no outcome (S7-R5); the CLI's pilot needs exactly
#   20 trials and prints `MEASUREMENT`.
# - DR-8 `workers` processes run the (trial, path) jobs; each worker gets the
#   repository and `src` first on its import path and the trial-code
#   directory last, so trial code can never shadow an engine or image module
#   (S7-R1). The record lists runs in job order (path-major).

SCREEN_SELF = "calibration/screen.py"
# DR-6 (S7-R2): the C2 window and gap the engine fixes
C2_G_DAYS = 1247 - grid.T_C2  # prereg §3.1
C2_W0 = datetime(2022, 1, 1, tzinfo=UTC) + timedelta(days=C2_G_DAYS)
C2_WINDOW_DAYS = grid.T_C2
C2_WINDOW_ID = json.dumps(
    [
        C2_W0.strftime("%Y-%m-%dT%H:%M:%SZ"),
        (C2_W0 + timedelta(days=C2_WINDOW_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    ],
    separators=(",", ":"),
)
# DR-6 (S7-R4): the screen's frozen reference vectors; "paths" (floats) is
# frozen from the pinned image by slice S8, and `declare` refuses until then
FROZEN_REFERENCE_VECTORS: dict[str, str | None] = {
    "paths": None,
    "g11": "a63398708b99fbd5f0f5c8cee5f497ae79fab2a2b1bfee0c53577fac82bce911",
    "g14": "5eb80b73256d75d628a4562ec04631b090eea5efcf461ff9148a04b5b4f8d643",
}


def screen_reference_vectors() -> dict[str, str]:
    """SP-6, GS-5, WF-8: the screen's reference vectors on fixed synthetic
    input; bit-exact only on the pinned image (the float path)."""
    hours = np.arange(400, dtype=np.int64)
    bars = np.array(
        [
            [
                [
                    100 + i + 0.5 * math.sin(i),
                    103 + i,
                    97 + i,
                    100 + i + math.cos(i),
                    10.0,
                ]
            ]
            * 2
            for i in range(400)
        ],
        dtype=float,
    )
    source = HourlySource(bars, hours, {})
    seed = screen_seed("00" * 32)
    paths = b"".join(
        np.ascontiguousarray(null_path(source, seed, p, 1000), "<f8").tobytes()
        for p in range(N_PATHS)
    )
    window = '["2022-01-01T00:00:00Z","2025-06-01T00:00:00Z"]'
    return {
        "paths": hashlib.sha256(paths).hexdigest(),
        "g11": g11_shifts_sha256(g11_shifts("ab" * 32, window, 1247, 30)),
        "g14": g14_grid_sha256("ab" * 32, window, (120, 365), 7),
    }


def check_object(obj: Path, posted_sha256: str, root: Path) -> dict[str, Any]:
    """DR-6: the posted qualification object (every manifest file, S7-R7),
    its engine code and runtime; returns its run definition."""
    from calibration import mapping

    manifest = json.loads((obj / "manifest.json").read_bytes())
    if sha(manifest) != posted_sha256:
        raise ValueError("the qualification object is not the posted one")
    files = {}
    for name, digest in manifest.items():
        data = (obj / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError(f"{name} does not match the object's manifest")
        files[name] = data
    for name in ("definition.json", "mapping.py", "screen.py"):
        if name not in files:
            raise ValueError(f"the object has no {name}")
    defn: dict[str, Any] = json.loads(files["definition.json"])
    check_screen_code(
        defn,
        root,
        {
            "calibration/mapping.py": files["mapping.py"],
            SCREEN_SELF: files["screen.py"],
        },
    )
    mapping.check_runtime(defn)
    return defn


def check_screen_code(
    defn: dict[str, Any], root: Path, reviewed: Mapping[str, bytes]
) -> None:
    """DR-6: the engine commit holds the run's recorded code, and every loaded
    engine module is that commit's or, for the reviewed files, the object's."""
    from calibration import mapping, rundef

    commit = defn["engine_commit"]
    try:
        names = mapping._git(root, "ls-tree", "-r", "--name-only", commit).decode()
        inventory = {
            rel: rundef.canonical_sha256(mapping._git(root, "show", f"{commit}:{rel}"))
            for rel in sorted(names.splitlines())
            if rundef.is_code(rel)
        }
    except Exception as error:
        raise ValueError(f"engine commit {commit} not readable") from error
    if sha(inventory) != defn["generator_sha256"]:
        raise ValueError("the engine commit is not the run's recorded code")
    if problem := rundef.bytecode_problem():
        raise ValueError(problem)
    for rel, data in reviewed.items():
        inventory[rel] = rundef.canonical_sha256(data)
    for rel, path in mapping.loaded().items():
        if rundef.canonical_sha256(path.read_bytes()) != inventory.get(rel):
            raise ValueError(f"the loaded {rel} is not the run's")


def screen_job(
    source: HourlySource,
    seed: str,
    trial: dict[str, Any],
    p: int,
    hours: int,
    w0: datetime,
    window_hours: int,
    window_id: str,
    g_days: int,
) -> dict[str, Any]:
    """DR-1..DR-3: one trial on one path."""
    started = time.perf_counter()
    try:
        path = null_path(source, seed, p, hours)
    except PathUnavailable:
        gates: dict[str, str | None] = dict.fromkeys(GATES, "PATH_UNAVAILABLE")
    else:
        own = trial["warmup_hours"] + window_hours + 1
        gates = screen_gates(
            trial,
            path[len(path) - own :],
            w0,
            window_hours,
            screen_trial_seed(seed, p, trial["trial_id"]),
            window_id,
            g_days,
        )
    return {
        "trial_id": trial["trial_id"],
        "path": p,
        "gates": gates,
        "seconds": time.perf_counter() - started,
    }


def _extend_path(engine: Sequence[str], code: Sequence[str]) -> None:
    """DR-8: the engine first and the trial code last on the import path, an
    earlier entry of a trial-code directory moved to the end (S7R-R1); run in
    the parent and in every worker (spawn and forkserver children do not
    inherit the parent's paths)."""
    placed = {os.path.realpath(p) for p in [*engine, *code]}
    # S7R-R1: compare resolved directories, so no alias or other spelling of
    # the trial-code directory stays ahead of site-packages
    sys.path[:] = [p for p in sys.path if os.path.realpath(p or ".") not in placed]
    sys.path[:0] = list(engine)
    sys.path.extend(code)


def _paths(code_dir: Path | None) -> tuple[list[str], list[str]]:
    root = Path(__file__).resolve().parents[1]
    return [str(root), str(root / "src")], (
        [] if code_dir is None else [str(code_dir.resolve())]
    )


def run_screen(
    trials: list[dict[str, Any]],
    source: HourlySource,
    w0: datetime,
    window_hours: int,
    window_id: str,
    g_days: int,
    workers: int = 2,
    code_dir: Path | None = None,
) -> dict[str, Any]:
    """DR-1..DR-3, DR-5, DR-7: the measurement record of `trials`."""
    set_sha = trial_set_sha256(trials)  # refuses an invalid declaration (DR-3)
    engine, code = _paths(code_dir)
    _extend_path(engine, code)  # S7R-R3: the parent loads trial code too
    for t in trials:  # S7-R6: every trial's code loads from its bytes first
        load(t["signal"], t["signal_sha256"])
        if t["overlay"] is not None:
            load(t["overlay"], t["overlay_sha256"])
    seed = screen_seed(set_sha)
    hours = max(t["warmup_hours"] for t in trials) + window_hours + 1
    jobs = [(t, p) for p in range(N_PATHS) for t in trials]
    args = (seed, hours, w0, window_hours, window_id, g_days)
    if workers == 1:
        runs = [screen_job(source, seed, t, p, *args[1:]) for t, p in jobs]
    else:
        # imported here: at module import it registers __mp_main__, and the
        # engine's import test allows numpy alone (test_d19_deploy.py)
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(
            max_workers=workers, initializer=_extend_path, initargs=(engine, code)
        ) as pool:
            futures = [
                pool.submit(screen_job, source, seed, t, p, *args[1:]) for t, p in jobs
            ]
            runs = [f.result() for f in futures]
    available = all(v is None or v == NA for r in runs for v in r["gates"].values())
    return {
        "screen_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "trial_set_sha256": set_sha,
        "trials": [trial_sha256(t) for t in trials],
        "screen_seed": seed,
        "source": source.identity,
        "w0": w0.isoformat(),
        "window_hours": window_hours,
        "window_id": window_id,
        "g_days": g_days,
        "path_hours": hours,
        "reference_vectors": screen_reference_vectors(),
        "runs": runs,
        "availability": "ALL_AVAILABLE" if available else "SOME_UNAVAILABLE",
        "measurement_only": "screen measurement (prereg §10): not a declaration",
    }


def declare(
    trials: list[dict[str, Any]],
    raw_root: Path,
    obj: Path,
    posted_sha256: str,
    root: Path,
    workers: int = 2,
    code_dir: Path | None = None,
) -> dict[str, Any]:
    """DR-4..DR-6: the screen record a declaration lists, or ValueError. The
    bars are rebuilt here from the exploration archives (each checked
    against its sidecar by `build_exploration_manifest`), never taken from
    the caller (S7R-R2)."""
    defn = check_object(obj, posted_sha256, root)
    source = load_hourly_source(raw_root)
    vectors = screen_reference_vectors()
    if any(v is None for v in FROZEN_REFERENCE_VECTORS.values()):
        raise ValueError("the screen's float reference vector is not frozen yet (S8)")
    if vectors != FROZEN_REFERENCE_VECTORS:
        raise ValueError("the screen's reference vectors differ from the frozen ones")
    recorded = (defn.get("exploration_source") or {}).get("manifest_sha256")
    if source.identity["manifest_sha256"] != recorded:
        raise ValueError("the exploration bars are not the run definition's")
    record = run_screen(
        trials,
        source,
        C2_W0,
        C2_WINDOW_DAYS * 24,
        C2_WINDOW_ID,
        C2_G_DAYS,
        workers=workers,
        code_dir=code_dir,
    )
    for r in record["runs"]:
        del r["seconds"]  # timing is measurement evidence, not declared
    del record["measurement_only"]
    record["qualification_object_sha256"] = posted_sha256
    record["outcome"] = (
        "VALID" if record.pop("availability") == "ALL_AVAILABLE" else "INVALID"
    )
    return record
