"""Declared-strategy screen of the D-19 preregistration §7.2 (A-U1).

Build slices (`review/d19-engine/SCREEN_PLAN.md`): S1, the `n_S = 30`
simulated null hourly BTC/ETH paths; S3, the trial interface. Later slices
add the event-contract runs and the seven screened gates to this file, which
the qualification object binds by its bytes (DRAFT R-8, qobj `LATER`); it
imports only engine-commit code.

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
import types
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from aqt.data.bars import BarSeries
from aqt.data.klines import EXPLORATION, build_exploration_manifest
from aqt.features.factory import FEATURE_NAMES
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
    log_close = np.log(o[0]) + np.cumsum(c, axis=0)
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
#   The signal is called as `signal(inputs, params)`: `inputs` holds only
#   its `s_inputs` (C-10 (1)), name -> hourly array, and `params` is
#   `signal_params`: `parameter_point` without `tau`, `sigma` and the
#   `model.` dimensions (S3-R2).
# - TI-3 `s_inputs` entries are frozen feature names (`FEATURE_NAMES`) or
#   "model:<id>" of the trial's own declared model. Never allowed:
#   "sigma_hat" (the sizing estimator's output) and, for a trial sized by
#   EWMA_168h, the identical frozen feature `ewma_vol_168h` (REG (A), D-20
#   B5). Every other volatility feature stays allowed.
# - TI-4 (S3-R4) `family` is "trend" or "vol", the two families the D-19
#   calibration covers (`calibration/rules.py` FAMILIES). There is no fixed-
#   size class (C-10 (1), REG (A)). `sigma` is "EWMA_168h", or in the vol
#   family one of the protocol's allowed volatility-family estimators.
# - TI-5 (S3-R3) `model` is null or {"id", "class", "params", "target"}
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
        if set(model) != {"id", "class", "params", "target"}:
            raise TrialError("model must be null or {id, class, params, target}")
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
