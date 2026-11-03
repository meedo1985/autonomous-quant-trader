"""R-14a lockbox module (Annex D; review/r14a-modules/DESIGN.md §6, §7.1).

The lockbox_eval worker (slices 1-3b-2 of the build; the store, publisher
and signer are separate builds): the A4 forecast generator, the A5
reference vectors, the A6 adapter, the L-1..L-4 pass rule, the
`aqt.lockbox.sealed_bundle.v1` body, the pre-read checks (§6.3), the
lockbox run, read and computed twice (§6.4), the start chain and loader
(DESIGN §4), and the worker's store calls (§6.5). Nothing here binds until
its SHA-256 is a row of the signed C2 (R-14a item 1); until then it is a
draft under review.

R-14a item 3: imports only engine-commit modules, the object's `screen.py`,
the standard library and pinned image libraries; never the confirmation
module. Item 4: frozen functions are called, not re-implemented; A4's
lockbox stream (no frozen function for m != n) is implemented here exactly
as Annex D §D-3.4 states it.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import random
import struct
import sys
import types
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, fields
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Protocol

import numpy as np

import aqt.metrics.statistics as st
from aqt.backtest.costs import (
    ewma_hourly_volatility_bps_series,
    hourly_log_returns_bps,
)
from aqt.backtest.event_contract import (
    EventContractError,
    EventResult,
    run_event_contract,
)
from aqt.data.bars import BarSeries
from aqt.features.columns import feature_columns
from aqt.metrics.descriptive import _max_drawdown
from calibration import screen
from calibration.seeds import cj, sha
from calibration.semi import SYMBOLS

# Annex D §D-1.1, §D-1.8
L0 = datetime(2025, 6, 1, tzinfo=UTC)
L1 = datetime(2026, 9, 1, tzinfo=UTC)
S_PRE = datetime(2022, 11, 13, tzinfo=UTC)
M_DAYS = 457
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
ATTEMPTS = st.BOOTSTRAP_ATTEMPTS  # 2,000 (§D-1.4)
QUANTILE = 0.05
UPSIDE_QUANTILE = 0.95
MDD_LIMIT = 0.05  # L-3, L-4 (Annex C C-3)

# §D-3.2 lockbox prediction stream
PURPOSE = "lockbox_prediction"
ASSET = "BTCUSDT"
COST = "1.0"
SEED_SOURCE = "R13_TRIAL_SEED"

BUNDLE_SCHEMA = "aqt.lockbox.sealed_bundle.v1"
SCOPES = ("BTC_EDIFF", "BTC_MDD", "ETH_EIMPROV", "ETH_MDD", "RUN", "DEADLINE")
CODES = (
    "INSUFFICIENT_OBSERVATIONS",
    "ZERO_VARIANCE",
    "NONFINITE_RESULT",
    "NONPOSITIVE_LONG_RUN_VARIANCE",
    "DAYS_INCOMPLETE",
    "NONFINITE_EQUITY",
    "RUN_FAILED",
    "NOT_FINISHED_BY_D_W",
)
_HEX = frozenset("0123456789abcdef")


class LockboxError(ValueError):
    """A refused input or an unavailable computation; `code` says which."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


# --- shared encodings (§D-3.1a) ---------------------------------------------


def hexf(x: float) -> str:
    return struct.pack(">d", x).hex()


def unhexf(s: object) -> float:
    if not isinstance(s, str) or len(s) != 16 or not set(s) <= _HEX:
        raise LockboxError("PREDICTION_ARTIFACT_INVALID", f"not hexf: {s!r}")
    value: float = struct.unpack(">d", bytes.fromhex(s))[0]
    return value


def _time(t: datetime) -> str:
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def window_id(w0: datetime, w1: datetime) -> str:
    """The canonical `["<w0>","<w1>"]` (§D-3.2)."""
    return json.dumps([_time(w0), _time(w1)], separators=(",", ":"))


# --- A4: the lockbox prediction stream and the forecast (§D-3.4) -------------


def seed_material(seed_hex: str, window: str, replicate: int) -> bytes:
    """IMPLEMENTATION_CONVENTIONS l.84-94's layout with purpose
    `lockbox_prediction` and `output_length` 457 (§D-3.4)."""
    # ReplicateStream is not touched (§D-3.4); building one only reuses its
    # identity checks (seed hex, convention hash, asset, cost, window).
    st.ReplicateStream(seed_hex, st.CONVENTION_DOCUMENT_SHA256, ASSET, COST, window)
    if isinstance(replicate, bool) or not 0 <= replicate < ATTEMPTS:
        raise LockboxError("INVALID_ARGUMENT", "replicate index must be 0..1999")
    return json.dumps(
        [
            st.SEED_DOMAIN,
            seed_hex,
            st.CONVENTION_DOCUMENT_SHA256,
            PURPOSE,
            ASSET,
            COST,
            window,
            M_DAYS,
            replicate,
        ],
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def replicate_indices(
    seed_hex: str, window: str, n: int, block: float, replicate: int
) -> tuple[int, ...]:
    """457 indices over `[0, n)` in `bootstrap_indices`' draw order."""
    if not 1 <= block <= n:
        raise LockboxError("INVALID_ARGUMENT", "block must lie in [1, n]")
    digest = hashlib.sha256(seed_material(seed_hex, window, replicate)).digest()
    generator = random.Random(int.from_bytes(digest, "big"))
    indices = [st._uniform_index(generator, n)]
    for _ in range(1, M_DAYS):
        indices.append(
            st._uniform_index(generator, n)
            if generator.random() < 1 / block
            else (indices[-1] + 1) % n
        )
    return tuple(indices)


@dataclass(frozen=True)
class Forecast:
    psi: tuple[float, ...]
    block: st.BlockLength
    indices: tuple[tuple[int, ...], ...]
    replicates: tuple[float, ...]  # in replicate order r = 0..1999
    q: float


def forecast(d: Sequence[float], seed_hex: str, window: str) -> Forecast:
    """ψ, b, the 2,000 replicates and q (§D-1.3, §D-1.4, §D-3.4), with
    §D-1.6 items 1-4 as refusals."""
    values = tuple(float(x) for x in d)
    n = len(values)
    if n < 16:
        raise LockboxError("INSUFFICIENT_OBSERVATIONS", "source n < 16")
    s = st.sharpe(values)
    if s.reason is not None:
        raise LockboxError(s.reason, "source E-DIFF")
    try:
        psi = st._influence(values, s)
    except (ArithmeticError, ValueError) as e:
        raise LockboxError("NONFINITE_RESULT", "psi") from e
    block = st.block_length(psi)
    if block.reason is not None or block.value is None:
        raise LockboxError(block.reason or "NONFINITE_RESULT", "block length")
    if not 1 <= block.value <= n:
        raise LockboxError("NONFINITE_RESULT", "block length outside [1, n]")
    indices = tuple(
        replicate_indices(seed_hex, window, n, block.value, r) for r in range(ATTEMPTS)
    )
    replicates = []
    for idx in indices:  # all attempts, in order; none dropped or replaced
        t = st.sharpe([values[i] for i in idx]).scaled
        if t is None or not math.isfinite(t):
            raise LockboxError("NONFINITE_RESULT", "a replicate is unavailable")
        replicates.append(t)
    q = st.type_seven_quantile(replicates, QUANTILE)
    if not math.isfinite(q):
        raise LockboxError("NONFINITE_RESULT", "q")
    return Forecast(psi, block, indices, tuple(replicates), q)


# --- A5: reference vectors (§D-3.4) -----------------------------------------


def _floats_sha256(values: Sequence[float]) -> str:
    return hashlib.sha256(b"".join(struct.pack(">d", x) for x in values)).hexdigest()


def _field(value: object) -> object:
    # [DESIGN] "every BlockLength field (hexf)": floats as hexf; ints, bools,
    # strings and None as themselves (an int is not a float to encode).
    return hexf(value) if isinstance(value, float) else value


def reference_d() -> tuple[float, ...]:
    """The published synthetic `d` [DESIGN]: 120 days of AR(1), coefficient
    0.6, from a fixed stdlib seed, so b is neither degenerate nor 1."""
    generator = random.Random(20251101)
    out, x = [], 0.0
    for _ in range(120):
        x = 0.6 * x + generator.gauss(0.0005, 0.01)
        out.append(x)
    return tuple(out)


REFERENCE_SEED_HEX = hashlib.sha256(b"aqt.lockbox.reference_vectors.v1").hexdigest()
REFERENCE_WINDOW = window_id(
    datetime(2023, 1, 1, tzinfo=UTC), datetime(2023, 5, 1, tzinfo=UTC)
)
# Frozen with the code review (§D-3.4): SHA-256 of cj(reference_vectors()) on
# the qualified image. A different value at startup is REFERENCE_VECTOR_MISMATCH.
FROZEN_VECTORS_SHA256: str | None = None


def reference_vectors() -> dict[str, Any]:
    d = reference_d()
    f = forecast(d, REFERENCE_SEED_HEX, REFERENCE_WINDOW)
    sequences = b"".join(struct.pack(">I", i) for idx in f.indices for i in idx)
    return {
        "d_sha256": _floats_sha256(d),
        "psi_sha256": _floats_sha256(f.psi),
        "block": {x.name: _field(getattr(f.block, x.name)) for x in fields(f.block)},
        "first_indices": {
            "0": list(f.indices[0][:10]),
            "1999": list(f.indices[-1][:10]),
        },
        "indices_sha256": hashlib.sha256(sequences).hexdigest(),
        "replicates_sha256": _floats_sha256(f.replicates),
        "q": hexf(f.q),
    }


def vectors_sha256() -> str:
    return hashlib.sha256(cj(reference_vectors())).hexdigest()


def startup_result() -> tuple[str, str]:
    """(vectors_sha256, PASS | REFERENCE_VECTOR_MISMATCH) for the store's
    `aqt.lockbox.startup.v1` (§D-3.4)."""
    got = vectors_sha256()
    ok = FROZEN_VECTORS_SHA256 is not None and got == FROZEN_VECTORS_SHA256
    return got, "PASS" if ok else "REFERENCE_VECTOR_MISMATCH"


# --- A6: the adapter (§D-3.3; DESIGN §7.1) ----------------------------------


@dataclass(frozen=True)
class Legs:
    """One asset's paired legs after the adapter: daily returns and MDD."""

    candidate: tuple[float, ...]
    benchmark: tuple[float, ...]
    mdd_candidate: float
    mdd_benchmark: float


def _check_leg(
    series: BarSeries, result: EventResult, asset: str, start: datetime, days: int
) -> None:
    hours = 24 * days
    if series.symbol != asset or series.interval != HOUR:
        raise LockboxError("DAYS_INCOMPLETE", "asset or interval")
    # every run hour and the derived terminal bar (confirmation_path) present
    # at start + i h; BarSeries itself does not enforce completeness
    if result.start < 0 or len(series.bars) < result.start + hours + 1:
        raise LockboxError("DAYS_INCOMPLETE", "series too short")
    if any(
        series.bars[result.start + i].open_time != start + i * HOUR
        for i in range(hours + 1)
    ):
        raise LockboxError("DAYS_INCOMPLETE", "hourly instants")
    if len(result.equity) != hours:
        raise LockboxError("DAYS_INCOMPLETE", "equity length")
    if not all(math.isfinite(e) and e > 0 for e in result.equity):
        raise LockboxError("NONFINITE_EQUITY")


def adapt(
    series: BarSeries,
    candidate: EventResult,
    benchmark_series: BarSeries,
    benchmark: EventResult,
    asset: str,
    start: datetime = L0,
    days: int = M_DAYS,
) -> Legs:
    """Annex D A6: both legs on the same series and start, the asset, the
    hourly instants, the length and finite positive equity; then
    `screen.daily_returns` and `_max_drawdown((1.0, *equity))`. Asset,
    series, start, interval and length failures are DAYS_INCOMPLETE
    [DESIGN reading of "a failure gives DAYS_INCOMPLETE or NONFINITE_EQUITY"]."""
    if series != benchmark_series or candidate.start != benchmark.start:
        raise LockboxError("DAYS_INCOMPLETE", "legs not on the same series/start")
    for result in (candidate, benchmark):
        _check_leg(series, result, asset, start, days)
    c, b = screen.daily_returns(candidate), screen.daily_returns(benchmark)
    if len(c) != days or len(b) != days:
        raise LockboxError("DAYS_INCOMPLETE", "daily returns")
    return Legs(
        tuple(c),
        tuple(b),
        _max_drawdown((1.0, *candidate.equity)),
        _max_drawdown((1.0, *benchmark.equity)),
    )


def run_legs(run: Callable[[], Legs]) -> Legs | str:
    """Runner error mapping (§D-3.3): the adapter's own code; an equity
    EventContractError → NONFINITE_EQUITY; any other error → RUN_FAILED."""
    try:
        return run()
    except LockboxError as e:
        if e.code in ("DAYS_INCOMPLETE", "NONFINITE_EQUITY"):
            return e.code
        return "RUN_FAILED"
    except EventContractError as e:
        # shortcut: classified by message (event_contract.py l.177, l.212 are
        # the equity raises); upgrade if the engine gains an error code
        return "NONFINITE_EQUITY" if "equity" in str(e) else "RUN_FAILED"
    except Exception:  # any other runner failure is technical (§D-3.3)
        return "RUN_FAILED"


# --- L-1..L-4 and the bundle (§D-1.5, §D-2.1, §D-2.2, §D-3.7 B4.2) ----------


def _cmp(f: Callable[..., bool], *xs: float | None) -> bool | None:
    return None if any(x is None for x in xs) else f(*xs)


def _and3(a: bool | None, b: bool | None) -> bool | None:
    if a is False or b is False:
        return False
    return None if a is None or b is None else True


def conditions(v: dict[str, float | None]) -> dict[str, bool | None]:
    """Atomic comparisons, each null iff one of its own inputs is null."""
    return {
        "L1": _cmp(lambda t, q: t >= q, v["t_l"], v["q"]),
        "L2": _cmp(lambda t: t > 0.0, v["t_l"]),
        "L3": _cmp(
            lambda c, b: c - b <= MDD_LIMIT, v["mdd_btc_cand"], v["mdd_btc_bench"]
        ),
        "L4": _and3(
            _cmp(lambda e: e > 0.0, v["eth_e_improv"]),
            _cmp(
                lambda c, b: c - b <= MDD_LIMIT, v["mdd_eth_cand"], v["mdd_eth_bench"]
            ),
        ),
    }


def upside(t_l: float | None, replicates_sorted: Sequence[float]) -> dict[str, Any]:
    """P-4 (§D-2.2): sealed only, not a gate."""
    if t_l is None or not math.isfinite(t_l):
        return {"status": "NOT_COMPUTED", "k": None, "exceeds_p95": None,
                "reason": "T_L_UNAVAILABLE"}  # fmt: skip
    return {
        "status": "COMPUTED",
        "k": sum(1 for x in replicates_sorted if x < t_l),
        "exceeds_p95": t_l > st.type_seven_quantile(replicates_sorted, UPSIDE_QUANTILE),
        "reason": None,
    }


def assemble(
    evaluation_id: str,
    values: dict[str, float | None],
    reasons: Sequence[str],
    upside_record: dict[str, Any],
    capture: dict[str, str],
) -> dict[str, Any]:
    """The RESULT bundle without `operational` (the store fills it, §D-3.7)."""
    for r in reasons:
        scope, _, code = r.partition(":")
        if scope not in SCOPES or code not in CODES:
            raise LockboxError("INVALID_ARGUMENT", f"reason {r!r}")
    cond = conditions(values)
    if any(c is False for c in cond.values()):
        result, cause = "FAIL", "PERFORMANCE"
    elif any(c is None for c in cond.values()):
        result, cause = "FAIL", "TECHNICAL"
    else:
        result, cause = "PASS", None
        t_l = values["t_l"]
        # P-2: the attestation fields must read (positive, true, true)
        if t_l is None or not (t_l > 0.0 and cond["L1"] and cond["L3"]):
            result, cause = "FAIL", "TECHNICAL"
    return {
        "schema": BUNDLE_SCHEMA,
        "evaluation_id": evaluation_id,
        "kind": "RESULT",
        "result": result,
        "cause_class": cause,
        "values": {k: None if x is None else hexf(x) for k, x in values.items()},
        "conditions": cond,
        "reasons": sorted(set(reasons)),
        "upside": upside_record,
        "capture": dict(capture),
    }


VALUE_KEYS = ("t_l", "q", "mdd_btc_cand", "mdd_btc_bench", "eth_e_improv",
              "mdd_eth_cand", "mdd_eth_bench")  # fmt: skip
CAPTURE_KEYS = ("engine_commit", "image_digest", "input_manifest_sha256",
                "lockbox_module_sha256", "prediction_artifact_sha256")  # fmt: skip


def evaluate(
    evaluation_id: str,
    btc: Legs | str,
    eth: Legs | str,
    q: float,
    replicates_sorted: Sequence[float],
    capture: dict[str, str],
) -> dict[str, Any]:
    """L-1..L-4 with §D-1.6 availability. `btc`/`eth` are the adapted legs or
    the RUN reason code; a failed BTC run nulls L-1..L-3, a failed ETH run
    L-4, independently."""
    if set(capture) != set(CAPTURE_KEYS):
        raise LockboxError("INVALID_ARGUMENT", "capture fields")
    v: dict[str, float | None] = dict.fromkeys(VALUE_KEYS)
    v["q"] = q
    reasons: list[str] = []

    def mdd(legs: Legs, scope: str, prefix: str) -> None:
        for key, x in (("cand", legs.mdd_candidate), ("bench", legs.mdd_benchmark)):
            if math.isfinite(x):
                v[f"{prefix}_{key}"] = x
            else:
                reasons.append(f"{scope}:NONFINITE_RESULT")

    if isinstance(btc, str):
        reasons.append(f"RUN:{btc}")
    else:
        d = st.paired_sharpe_statistics(btc.candidate, btc.benchmark)
        e = d.difference_series_sharpe
        if e.reason is None and e.scaled is not None:
            v["t_l"] = e.scaled
        else:
            reasons.append(f"BTC_EDIFF:{e.reason or 'NONFINITE_RESULT'}")
        mdd(btc, "BTC_MDD", "mdd_btc")
    if isinstance(eth, str):
        reasons.append(f"RUN:{eth}")
    else:
        p = st.paired_sharpe_statistics(eth.candidate, eth.benchmark)
        if p.paired_sharpe_improvement is not None and p.reason is None:
            v["eth_e_improv"] = p.paired_sharpe_improvement
        else:
            reasons.append(f"ETH_EIMPROV:{p.reason or 'NONFINITE_RESULT'}")
        mdd(eth, "ETH_MDD", "mdd_eth")
    return assemble(
        evaluation_id, v, reasons, upside(v["t_l"], replicates_sorted), capture
    )


# --- pre-read checks (DESIGN §6.3; Annex D §D-1.8 item 2, §D-3.5, §D-2.2 P-4) --

POLICY = "L266_MOD_2_31"
ARTIFACT_KINDS = ("trial", "signal", "overlay")  # [DESIGN] A1a item kinds
_ARTIFACT_SHAPE: dict[str, frozenset[str] | None] = {
    "cycle_id": None,
    "family": None,
    "nominee": frozenset(
        {
            "trial_id",
            "configuration_hash",
            "hypothesis_hash",
            "protocol_hash",
            "trial_index",
            "seed_l266",
            "estimator_seed_policy",
            "estimator_seed",
        }
    ),  # fmt: skip
    "source": frozenset({"window_id", "n", "d_sha256", "evaluation_record_sha256"}),
    "block": frozenset({"psi_sha256", "value", "raw", "clipping"}),
    "stream": frozenset(
        {"seed_hex", "seed_source", "purpose", "asset", "cost", "m", "attempts"}
    ),
    "replicates_sorted": None,
    "q": None,
    "code": frozenset(
        {
            "lockbox_module_sha256",
            "confirmation_module_sha256",
            "engine_commit",
            "screen_object_sha256",
        }
    ),  # fmt: skip
}


@dataclass(frozen=True)
class Signed:
    """Values the signed C2 protocol bytes fix (read from them, never from a
    caller, by the start check of a later slice)."""

    protocol_hash: str
    lockbox_module_sha256: str
    confirmation_module_sha256: str
    engine_commit: str
    screen_object_sha256: str
    image_digest: str


@dataclass(frozen=True)
class Request:
    """The identifiers handed over (§D-1.8 item 1) and the sealing entry."""

    cycle_id: str
    family: str
    nominee_trial_id: str
    hypothesis_hash: str
    configuration_hash: str
    prediction_artifact_sha256: str  # from aqt.lockbox.sealing.v1
    family_seed: str  # R-7, from the governing records
    # line 266, from the sealing record after the confirmation module's item-7
    # verification; never derived here (R14L5-S-2, OWNER_DECISION_R14L5_S2.md)
    seed_l266: str
    manifest_sha256: str  # the cycle's data-manifest hash
    trial_index: int  # from the nominee's immutable C2 trial record (§D-3.2)


class _Refused(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _need(ok: bool, code: str) -> None:
    if not ok:
        raise _Refused(code)


def _check_items(ledger: Mapping[str, Any], files: Mapping[str, bytes]) -> bytes:
    """A1a: every item of `aqt.c2.artifacts.v1` present with its hash and size;
    returns the trial object's bytes. Only the trial object is parsed as JSON."""
    items = ledger.get("items") if isinstance(ledger, Mapping) else None
    if not isinstance(items, list) or not items:
        raise _Refused("IDENTITY_MISMATCH")
    trial_bytes: bytes | None = None
    for item in items:
        _need(
            isinstance(item, Mapping)
            and set(item) == {"kind", "sha256", "size"}
            and isinstance(item["kind"], str)
            and item["kind"] in ARTIFACT_KINDS
            and isinstance(item["sha256"], str)
            and len(item["sha256"]) == 64
            and set(item["sha256"]) <= _HEX
            and type(item["size"]) is int,
            "IDENTITY_MISMATCH",
        )  # R14L-S-5: types checked before the lookup
        raw = files.get(item["sha256"])
        if raw is None:
            raise _Refused("ARTIFACT_NOT_FOUND")
        _need(
            hashlib.sha256(raw).hexdigest() == item["sha256"]
            and len(raw) == item["size"],
            "ARTIFACT_HASH_MISMATCH",
        )
        if item["kind"] == "trial":
            _need(trial_bytes is None, "IDENTITY_MISMATCH")
            trial_bytes = raw
    if trial_bytes is None:
        raise _Refused("IDENTITY_MISMATCH")
    return trial_bytes


def _check_trial(
    trial_bytes: bytes, ledger: Mapping[str, Any], request: Request
) -> None:
    try:
        trial = json.loads(trial_bytes)
        configuration_hash = screen.trial_sha256(trial)
    except (ValueError, screen.TrialError):
        raise _Refused("IDENTITY_MISMATCH") from None
    items = {(i["kind"], i["sha256"]) for i in ledger["items"]}
    wanted = {("signal", trial["signal_sha256"])}
    if trial["overlay"] is not None:
        wanted.add(("overlay", trial["overlay_sha256"]))
    code_items = {i for i in items if i[0] != "trial"}
    _need(
        configuration_hash == request.configuration_hash
        and trial["trial_id"] == request.nominee_trial_id
        and trial["family"] == request.family
        and code_items == wanted,  # the trial object and exactly its code
        "IDENTITY_MISMATCH",
    )


def _check_shape(artifact: object) -> dict[str, Any]:
    if not isinstance(artifact, dict) or set(artifact) != set(_ARTIFACT_SHAPE):
        raise _Refused("PREDICTION_ARTIFACT_INVALID")
    for key, inner in _ARTIFACT_SHAPE.items():
        if inner is not None:
            _need(
                isinstance(artifact[key], dict) and set(artifact[key]) == inner,
                "PREDICTION_ARTIFACT_INVALID",
            )
    return artifact


def _check_identity(a: dict[str, Any], request: Request, signed: Signed) -> None:
    """A1b, A7 and the signed values; any difference is IDENTITY_MISMATCH."""
    n, s, c = a["nominee"], a["stream"], a["code"]
    # the index is the trial record's, never the artifact's own (R14L-S-1)
    _need(
        type(n["trial_index"]) is int and n["trial_index"] == request.trial_index,
        "IDENTITY_MISMATCH",
    )
    seed_l266 = request.seed_l266
    try:
        estimator = screen.estimator_seed(seed_l266)
    except screen.TrialError:
        raise _Refused("IDENTITY_MISMATCH") from None
    seed_hex = sha({"family_seed": request.family_seed, "trial_id": n["trial_id"]})
    _need(
        a["cycle_id"] == request.cycle_id
        and a["family"] == request.family
        and n["trial_id"] == request.nominee_trial_id
        and n["configuration_hash"] == request.configuration_hash
        and n["hypothesis_hash"] == request.hypothesis_hash
        and n["protocol_hash"] == signed.protocol_hash
        and n["seed_l266"] == seed_l266
        and n["estimator_seed_policy"] == POLICY  # never a test on the value 0
        and type(n["estimator_seed"]) is int
        and n["estimator_seed"] == estimator
        and s["seed_hex"] == seed_hex
        and s["seed_source"] == SEED_SOURCE
        and (s["purpose"], s["asset"], s["cost"]) == (PURPOSE, ASSET, COST)
        and type(s["m"]) is int
        and s["m"] == M_DAYS
        and type(s["attempts"]) is int
        and s["attempts"] == ATTEMPTS
        and c
        == {
            "lockbox_module_sha256": signed.lockbox_module_sha256,
            "confirmation_module_sha256": signed.confirmation_module_sha256,
            "engine_commit": signed.engine_commit,
            "screen_object_sha256": signed.screen_object_sha256,
        },
        "IDENTITY_MISMATCH",
    )


def _check_p4(a: dict[str, Any]) -> None:
    """P-4: 2,000 finite ascending replicates; type-7 at p = 1/20 returns q."""
    reps = a["replicates_sorted"]
    if not isinstance(reps, list) or len(reps) != ATTEMPTS:
        raise _Refused("PREDICTION_ARTIFACT_INVALID")
    try:
        values = [unhexf(x) for x in reps]
        q = unhexf(a["q"])
    except LockboxError:
        raise _Refused("PREDICTION_ARTIFACT_INVALID") from None
    _need(
        all(math.isfinite(x) for x in values)
        and all(x <= y for x, y in zip(values, values[1:], strict=False))
        and st.type_seven_quantile(values, QUANTILE) == q,
        "PREDICTION_ARTIFACT_INVALID",
    )


def _check_declared(request: Request, declaration_bytes: bytes, sha256: str) -> None:
    """R14L2-S-1: the nominee's cycle, family, hashes and trial index must be
    the posted declaration's entry for it, the only trial record the chain
    has verified. [DESIGN] declaration layout, to be bound in the S4 text:
    top-level `cycle_id` and `trials`, a list of
    `{family, trial_id, hypothesis_hash, configuration_hash, trial_index}`.
    R14L3-S-1: the declaration arrives as the verified bytes and the hash the
    chain checked, both immutable; it is re-hashed and parsed here, so a
    handoff changed after `start()` is refused."""
    if hashlib.sha256(declaration_bytes).hexdigest() != sha256:
        raise _Refused("IDENTITY_MISMATCH")
    try:
        declaration = json.loads(declaration_bytes)
    except ValueError:
        raise _Refused("IDENTITY_MISMATCH") from None
    if not isinstance(declaration, dict):
        raise _Refused("IDENTITY_MISMATCH")
    trials = declaration.get("trials")
    if not isinstance(trials, list):
        raise _Refused("IDENTITY_MISMATCH")
    entries = [
        t
        for t in trials
        if isinstance(t, Mapping) and t.get("trial_id") == request.nominee_trial_id
    ]
    _need(
        declaration.get("cycle_id") == request.cycle_id and len(entries) == 1,
        "IDENTITY_MISMATCH",
    )
    entry = entries[0]
    _need(
        entry.get("family") == request.family
        and entry.get("hypothesis_hash") == request.hypothesis_hash
        and entry.get("configuration_hash") == request.configuration_hash
        and type(entry.get("trial_index")) is int
        and entry.get("trial_index") == request.trial_index,
        "IDENTITY_MISMATCH",
    )


def pre_read_check(
    *,
    request: Request,
    signed: Signed,
    declaration: bytes,
    declaration_sha256: str,
    artifact_bytes: bytes | None,
    artifacts_ledger: Mapping[str, Any],
    files: Mapping[str, bytes],
    manifest_sha256: str,
    image_digest: str,
    startup: Mapping[str, Any] | None,
) -> str:
    """PASS or the Q2b reason code, before any lockbox byte is read. Order
    [DESIGN]: presence, hashes, identities, the artifact's P-4 content, the
    image, the startup record; the first failure is the code returned."""
    try:
        if artifact_bytes is None:
            raise _Refused("ARTIFACT_NOT_FOUND")
        trial_bytes = _check_items(artifacts_ledger, files)
        _check_declared(request, declaration, declaration_sha256)
        _need(
            hashlib.sha256(artifact_bytes).hexdigest()
            == request.prediction_artifact_sha256,
            "ARTIFACT_HASH_MISMATCH",
        )
        try:
            artifact = json.loads(artifact_bytes)
            canonical = cj(artifact)
        except ValueError:
            raise _Refused("PREDICTION_ARTIFACT_INVALID") from None
        # artifact_sha256 = SHA256(cj(artifact)): the stored bytes are canonical
        _need(canonical == artifact_bytes, "PREDICTION_ARTIFACT_INVALID")
        _check_trial(trial_bytes, artifacts_ledger, request)
        a = _check_shape(artifact)
        _check_identity(a, request, signed)
        _need(manifest_sha256 == request.manifest_sha256, "IDENTITY_MISMATCH")
        _check_p4(a)
        _need(image_digest == signed.image_digest, "IMAGE_MISMATCH")
        _need(
            startup is not None
            and startup.get("result") == "PASS"
            and startup.get("lockbox_module_sha256") == signed.lockbox_module_sha256
            and startup.get("image_digest") == image_digest,
            "REFERENCE_VECTOR_MISMATCH",
        )
    except _Refused as r:
        return r.code
    return "PASS"


# --- the lockbox run (DESIGN §6.4, §7.1; Annex D §D-1.8 items 3-6, §D-3.3) ---
#
# screen.py has no public "run a trial on real bars" function: its run is a
# closure inside screen_gates. This glue calls the same frozen pieces in the
# same order (path_series, feature_columns, the cost volatility,
# model_column, load, leg_targets, benchmark_targets, run_event_contract)
# with w0 = L0, the warm-up from S_pre and the nominee's estimator seed. It is
# post-freeze glue (Annex D §D-3.1 accepted residual): review it as such.

RUN_HOURS = int((L1 - L0) / HOUR)  # 10,968
WARMUP_HOURS = int((L0 - S_PRE) / HOUR)  # the history part, S_pre .. L0
READ_HOURS = WARMUP_HOURS + RUN_HOURS  # bars with open_time in [S_pre, L1)


def check_read(series: BarSeries, asset: str) -> None:
    """§7.1 C-T: the served bars are exactly `[S_pre, L1)` hourly, ascending,
    each once, before `path_series` rebuilds times from row positions
    (`screen.py` l.911). Anything else refuses; nothing is filled or dropped."""
    if series.symbol != asset or series.interval != HOUR:
        raise LockboxError("DAYS_INCOMPLETE", "asset or interval")
    bars = series.bars
    if len(bars) != READ_HOURS or any(
        b.open_time != S_PRE + i * HOUR for i, b in enumerate(bars)
    ):
        raise LockboxError("DAYS_INCOMPLETE", "bars are not exactly [S_pre, L1)")


def run_asset(
    trial: dict[str, Any], bars: BarSeries, symbol: int, estimator_seed: int
) -> Legs:
    """The nominee's 1x baseline pair on one asset over `[L0, L1)`: both legs
    flat at L0 with equity 1.0 (run_event_contract's start, R-14d), the
    final close by `confirmation_path`, then the A6 adapter. Depends only on
    this asset's bars, so BTC and ETH fail independently (§D-1.6, §D-3.3)."""
    asset = SYMBOLS[symbol]
    check_read(bars, asset)
    # rows (hours, symbols, OHLCV) as confirmation_path takes them; only this
    # asset's slot is filled with real bars and only it is read (path_series
    # reads column `symbol`; each symbol's terminal row is its own last close)
    row = [[b.open, b.high, b.low, b.close, b.volume] for b in bars.bars]
    rows = [[r, r] for r in row]
    path = screen.confirmation_path(np.asarray(rows, dtype=float))
    series = screen.path_series(path, symbol, S_PRE)
    first, columns = feature_columns(series)
    sigma = ewma_hourly_volatility_bps_series(hourly_log_returns_bps(series))
    if trial["model"] is not None:  # rule-based nominees skip fitting
        column = screen.model_column(
            trial, series, first, columns, WARMUP_HOURS, RUN_HOURS, 0,
            model_seed=estimator_seed,
        )  # fmt: skip
        columns = {**columns, f"model:{trial['model']['id']}": tuple(column)}
    closes = [b.close for b in series.bars]
    signal = screen.load(trial["signal"], trial["signal_sha256"])
    overlay = (
        None
        if trial["overlay"] is None
        else screen.load(trial["overlay"], trial["overlay_sha256"])
    )
    candidate, _ = screen.leg_targets(
        trial, signal, overlay, columns, first, closes, WARMUP_HOURS, RUN_HOURS, 0
    )
    benchmark = screen.benchmark_targets(columns, first, WARMUP_HOURS, RUN_HOURS)
    legs = [
        run_event_contract(series, targets, WARMUP_HOURS, sigma_bps=sigma)
        for targets in (candidate, benchmark)
    ]
    return adapt(series, legs[0], series, legs[1], asset, L0, M_DAYS)


def compute(
    evaluation_id: str,
    trial: dict[str, Any],
    estimator_seed: int,
    read: Callable[[], tuple[BarSeries, BarSeries]],
    q: float,
    replicates_sorted: Sequence[float],
    capture: dict[str, str],
) -> dict[str, Any]:
    """One read and compute: BTC (L-1..L-3) and ETH (L-4), each failing
    independently (§D-3.3)."""
    screen.check_trial(trial)
    if type(estimator_seed) is not int or not 0 <= estimator_seed < 2**31:
        raise LockboxError("INVALID_ARGUMENT", "estimator_seed")
    btc_bars, eth_bars = read()
    btc = run_legs(lambda: run_asset(trial, btc_bars, 0, estimator_seed))
    eth = run_legs(lambda: run_asset(trial, eth_bars, 1, estimator_seed))
    return evaluate(evaluation_id, btc, eth, q, replicates_sorted, capture)


def compute_twice(
    evaluation_id: str,
    trial: dict[str, Any],
    estimator_seed: int,
    read: Callable[[], tuple[BarSeries, BarSeries]],
    q: float,
    replicates_sorted: Sequence[float],
    capture: dict[str, str],
) -> dict[str, Any]:
    """§D-1.8 item 6: read and compute twice; the bundles must be identical.
    This checks determinism only. A difference is a technical FAIL, recorded
    as RUN:RUN_FAILED on both assets [DESIGN: the reason list has no
    determinism code]."""
    args = (evaluation_id, trial, estimator_seed, read, q, replicates_sorted, capture)
    first, second = compute(*args), compute(*args)
    if cj(first) == cj(second):
        return first
    return evaluate(
        evaluation_id, "RUN_FAILED", "RUN_FAILED", q, replicates_sorted, capture
    )


# --- the start chain and the loader (DESIGN §4; R-14a item 2) ----------------
#
# Format bindings the S4 text does not fix yet, chosen here and to be stated
# in the signed C2 [DESIGN; pre-signing item]:
# - the signed protocol bytes carry each of `lockbox_module_sha256`,
#   `confirmation_module_sha256` and `outpoint_F` exactly once, on its own
#   line as `<name>: "<value>"` (any indentation), replacing the
#   <<BUILD>>/<<SIGNING>> markers; `outpoint_F` is `<txid hex>:<vout>`;
# - the C2 declaration is canonical JSON (cj) with a top-level
#   `protocol_hash`.
# What this chain cannot verify: that the post is *accepted* (6
# confirmations, first post, no later post; O-6a SPEC §3-§5). That needs a
# validating node and is the frozen acceptance record's; the chain checks
# that record's transaction is well formed, spends F and names this
# declaration, and logs the record's hash.

POST_SCRIPT_PREFIX = bytes.fromhex("6a25") + b"AQTC2"
MODULE_ROWS = ("lockbox_module_sha256", "confirmation_module_sha256")
MODULE_PATHS = {  # DESIGN §5, §6
    "lockbox_module_sha256": "calibration/c2_lockbox.py",
    "confirmation_module_sha256": "calibration/c2_confirmation.py",
}
# further signed-C2 rows `start` reads [DESIGN; to be bound in the S4 text]
SIGNED_ROWS = (
    "engine_commit",
    "screen_object_sha256",
    "qualification_object_sha256",
    "image_digest",
)


class ChainError(ValueError):
    """A broken or unverifiable step of the start chain; nothing is read."""


def _varint(raw: bytes, i: int) -> tuple[int, int]:
    first = raw[i]
    if first < 0xFD:
        return first, i + 1
    width = {0xFD: 2, 0xFE: 4, 0xFF: 8}[first]
    return int.from_bytes(raw[i + 1 : i + 1 + width], "little"), i + 1 + width


def parse_tx(raw: bytes) -> tuple[list[tuple[str, int]], list[tuple[int, bytes]]]:
    """A Bitcoin transaction's spent outpoints (display txid hex, vout) and
    its outputs (value in satoshi, scriptPubKey). Legacy or segwit."""
    try:
        i = 4  # version
        segwit = raw[i] == 0 and raw[i + 1] == 1
        if segwit:
            i += 2
        count, i = _varint(raw, i)
        inputs = []
        for _ in range(count):
            txid = raw[i : i + 32][::-1].hex()
            vout = int.from_bytes(raw[i + 32 : i + 36], "little")
            length, i = _varint(raw, i + 36)
            i += length + 4  # scriptSig, sequence
            inputs.append((txid, vout))
        count, i = _varint(raw, i)
        outputs = []
        for _ in range(count):
            value = int.from_bytes(raw[i : i + 8], "little")
            length, i = _varint(raw, i + 8)
            outputs.append((value, raw[i : i + length]))
            i += length
        if segwit:
            for _ in inputs:
                items, i = _varint(raw, i)
                for _ in range(items):
                    length, i = _varint(raw, i)
                    i += length
        if i + 4 != len(raw) or not inputs or not outputs:
            raise ChainError("transaction bytes do not parse exactly")
    except (IndexError, KeyError) as e:
        raise ChainError("transaction bytes do not parse") from e
    return inputs, outputs


def txid(raw: bytes) -> str:
    """The display txid: double SHA-256 of the serialization without the
    segwit marker, flag and witnesses (the wtxid would include them)."""
    parse_tx(raw)  # refuses bytes that do not parse exactly
    base = raw
    if raw[4] == 0 and raw[5] == 1:
        i, end = 6, 0
        count, i = _varint(raw, i)
        for _ in range(count):
            length, i = _varint(raw, i + 36)
            i += length + 4
        count, i = _varint(raw, i)
        for _ in range(count):
            length, i = _varint(raw, i + 8)
            i += length
        end = i
        base = raw[:4] + raw[6:end] + raw[-4:]
    return hashlib.sha256(hashlib.sha256(base).digest()).digest()[::-1].hex()


def post_declaration_sha256(raw_tx: bytes, outpoint: str) -> str:
    """O-6a SPEC §3 well-formed post: spends F; exactly one OP_RETURN output,
    value 0, scriptPubKey exactly `6a25 'AQTC2' <32 bytes>`."""
    inputs, outputs = parse_tx(raw_tx)
    txid, _, vout = outpoint.partition(":")
    if not vout.isdigit() or (txid, int(vout)) not in inputs:
        raise ChainError("the post does not spend the bound coin F")
    returns = [(v, s) for v, s in outputs if s[:1] == b"\x6a"]
    if len(returns) != 1:
        raise ChainError("the post needs exactly one OP_RETURN output")
    value, script = returns[0]
    if value != 0 or len(script) != 39 or script[:7] != POST_SCRIPT_PREFIX:
        raise ChainError("the OP_RETURN output is not the AQTC2 message")
    return script[7:].hex()


ACCEPTANCE_SCHEMA = "aqt.c2.post_acceptance.v1"
ACCEPTANCE_FIELDS = frozenset(
    {"schema", "txid", "raw_tx", "block_hash", "height", "confirmations",
     "first_post"}
)  # fmt: skip
MIN_CONFIRMATIONS = 6  # O-6a SPEC §5, DRAFT seed_disclosure first_post_rule


def check_acceptance(record: bytes, post_raw_tx: bytes) -> None:
    """R14L-S-3: the frozen acceptance record [DESIGN schema] must name this
    very post, as the first post, at 6 or more confirmations, with a
    well-formed block hash and height. What the module cannot check is that
    the record is true: that needs the validating node and the explorers of
    O-6a SPEC §4. Who vouches for the record, and how its provenance is
    verified before `start()`, is an open owner decision (R14L2-S-2); the
    record's hash is logged for §27."""
    try:
        acceptance = json.loads(record)
        canonical = cj(acceptance)
    except ValueError as e:
        raise ChainError("the acceptance record is not JSON") from e
    if (
        canonical != record
        or not isinstance(acceptance, dict)
        or set(acceptance) != ACCEPTANCE_FIELDS
    ):
        raise ChainError("the acceptance record is not the canonical schema")
    confirmations = acceptance["confirmations"]
    if (
        acceptance["schema"] != ACCEPTANCE_SCHEMA
        or acceptance["raw_tx"] != post_raw_tx.hex()
        or acceptance["txid"] != txid(post_raw_tx)
        or acceptance["first_post"] is not True
        or not isinstance(acceptance["block_hash"], str)
        or len(acceptance["block_hash"]) != 64
        or not set(acceptance["block_hash"]) <= _HEX
        or type(acceptance["height"]) is not int
        or acceptance["height"] <= 0
        or type(confirmations) is not int
        or confirmations < MIN_CONFIRMATIONS
    ):
        raise ChainError("the acceptance record does not accept this post")


def protocol_row(protocol: bytes, name: str) -> str:
    """The value of `<name>: "<value>"`, which must occur exactly once."""
    text = protocol.decode("utf-8")
    hits = [
        line.strip()[len(name) + 2 :]
        for line in text.splitlines()
        if line.strip().startswith(f"{name}: ")
    ]
    if len(hits) != 1:
        raise ChainError(f"{name} is not exactly one row of the signed C2")
    value = hits[0]
    if len(value) < 2 or value[0] != '"' or value[-1] != '"':
        raise ChainError(f"{name} row is not a quoted value")
    return value[1:-1]


def verify_chain(
    *,
    acceptance_record: bytes,
    post_raw_tx: bytes,
    declaration: bytes,
    protocol: bytes,
    modules: Mapping[str, bytes],
) -> dict[str, str]:
    """R-14a item 2, in order: the accepted post → the declaration bytes
    matching its declaration_sha256 → the declaration's protocol_hash → the
    complete signed C2 bytes hashing to it, with both module rows → the
    module bytes (`modules` maps each row name to the exact bytes that will
    be compiled). Raises ChainError at the first broken step; returns the
    log to record (Constitution §27)."""
    check_acceptance(acceptance_record, post_raw_tx)
    # F is read from the protocol bytes, which are themselves verified two
    # steps on; any failure anywhere refuses the whole chain
    posted = post_declaration_sha256(post_raw_tx, protocol_row(protocol, "outpoint_F"))
    declaration_sha256 = hashlib.sha256(declaration).hexdigest()
    if declaration_sha256 != posted:
        raise ChainError("the declaration is not the posted one")
    try:
        decl = json.loads(declaration)
        canonical = cj(decl)
    except ValueError as e:
        raise ChainError("the declaration is not JSON") from e
    if canonical != declaration or not isinstance(decl, dict):
        raise ChainError("the declaration is not canonical JSON")
    protocol_hash = decl.get("protocol_hash")
    if hashlib.sha256(protocol).hexdigest() != protocol_hash:
        raise ChainError("the protocol bytes do not hash to protocol_hash")
    log = {
        "acceptance_record_sha256": hashlib.sha256(acceptance_record).hexdigest(),
        "post_txid": txid(post_raw_tx),
        "declaration_sha256": declaration_sha256,
        "protocol_hash": protocol_hash,
    }
    if set(modules) != set(MODULE_ROWS):
        raise ChainError("exactly the two R-14a modules must be verified")
    for name in MODULE_ROWS:
        signed = protocol_row(protocol, name)
        if hashlib.sha256(modules[name]).hexdigest() != signed:
            raise ChainError(f"the loaded {name} bytes are not the signed ones")
        log[name] = signed
    return log


def load_verified(name: str, path: Path, sha256: str) -> types.ModuleType:
    """DESIGN §4 step 5: read the file once, hash those bytes, refuse on a
    mismatch, compile and execute exactly those bytes into a module whose
    spec names the `.py` source (so `rundef.bytecode_problem` passes,
    R14D3-S-1); the loader's exec_module never runs, so the file is not
    read again."""
    source = path.read_bytes()
    if hashlib.sha256(source).hexdigest() != sha256:
        raise ChainError(f"{path} is not the signed module")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None:
        raise ChainError(f"no module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    code = compile(source, str(path), "exec")
    sys.modules[name] = module
    try:
        exec(code, module.__dict__)  # noqa: S102 - the hashed bytes only
    except BaseException:
        del sys.modules[name]
        raise
    return module


def verify_code(
    obj: Path, posted_sha256: str, root: Path, modules: Mapping[str, bytes]
) -> dict[str, Any]:
    """DESIGN §4 code check: `screen.check_object`'s steps, with
    `check_screen_code`'s reviewed map extended by exactly the two signed
    module files (`modules` maps repository path to the verified bytes).
    R-14's two checks are otherwise unchanged; a third extra module is
    still refused."""
    from calibration import mapping, qobj

    if set(modules) != set(MODULE_PATHS.values()):  # R14L-S-4
        raise ChainError("exactly the two named R-14a module files")
    manifest = json.loads((obj / "manifest.json").read_bytes())
    if sha(manifest) != posted_sha256:
        raise ChainError("the qualification object is not the posted one")
    files = {}
    for name, digest in manifest.items():
        data = (obj / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ChainError(f"{name} does not match the object's manifest")
        files[name] = data
    _, defn = qobj.read(files)
    screen.check_screen_code(
        defn,
        root,
        {
            "calibration/mapping.py": files["mapping.py"],
            screen.SCREEN_SELF: files["screen.py"],
            **modules,
        },
    )
    mapping.check_runtime(defn)
    return defn


# --- the worker's store calls (DESIGN §6.1, §6.4, §6.5; Annex D §D-3.7) ------
#
# The store, publisher and signer are separate builds (§D-3.9). This is only
# the lockbox_eval worker's side: it never authorises its own read, never
# holds L_store, and never fills `operational`. The store enforces C and D*
# (the time rule); a refusal is StoreRefused and the worker stops without
# writing, so the DEFAULT bundle sealed at begin_read stands.


class StoreRefused(Exception):
    """The store refused a call (deadline, cap, gate, entitlement)."""


class ReadSession(Protocol):
    def read(self) -> tuple[BarSeries, BarSeries]:
        """BTC and ETH 1h bars over [S_pre, L1), each bar under the store's D*
        start check; raises StoreRefused once D* is reached."""
        ...


class Store(Protocol):
    """The store build's obligations this worker relies on (R14L4-S-3,
    R14L5-S-1; Annex D §D-3.7), to be tested in that build. `begin_read` step
    4 refuses unless sealing records exist for every declared family, this
    family is status (a) for this nominee and artifact, every identity field
    of the check record (`aqt.lockbox.pre_read_check.v1`) equals the sealing
    record (`aqt.lockbox.sealing.v1`) and the request, and the check's
    `startup_check_id` names a `PASS` startup record for the same module hash
    and image. With no check record or differing identities it refuses,
    writes nothing and logs an incident; a check record whose result is a
    reason code appends a rejection entry and grants no read (R14L6-S-1).
    The artifact bytes and the artifacts ledger it hands over are
    the sealed and `aqt.c2.artifacts.v1` records. The read gate serves only
    bars under the cycle's data-manifest hash, which the store takes from its
    own governing cycle record, never from the request or this worker (a
    request hash that differs is refused). `family_seed` and `seed_l266`
    come from the sealing record, written only after the confirmation module
    verified them (R-14a item 7; owner decision R14L5-S-2). The
    worker re-checks what it can (§6.3) but cannot authenticate these
    records itself."""

    def append_startup(self, record: dict[str, Any]) -> str:
        """Append aqt.lockbox.startup.v1; returns startup_check_id."""
        ...

    def record_pre_read_check(self, record: dict[str, Any]) -> str:
        """Seal aqt.lockbox.pre_read_check.v1 (deadline C; at most one per
        evaluation); the store adds check_id and checked_at."""
        ...

    def open_read(self, evaluation_id: str) -> ReadSession:
        """The read gate: only after begin_read's entry is durable, its
        DEFAULT verifies and a PASS startup record exists (§D-3.7)."""
        ...

    def write_bundle(self, evaluation_id: str, bundle: dict[str, Any]) -> None:
        """Seal the RESULT bundle; the store adds operational and commits."""
        ...

    def mark_finished(self, evaluation_id: str) -> None:
        """Count the finish if before D* (§D-3.7 mark_finished)."""
        ...


@dataclass(frozen=True)
class Evaluation:
    """The evaluation's record identifiers (§D-3.7 pre-read check record)."""

    evaluation_id: str
    eligibility_result_id: str
    lockbox_evaluation_id: str
    sealing_id: str


@dataclass(frozen=True)
class Started:
    """What `start` verified; `run_evaluation` takes only this (R14L-S-2)."""

    signed: Signed
    declaration: bytes  # the verified, posted declaration bytes (R14L3-S-1)
    declaration_sha256: str  # as the chain verified it against the post
    chain_log: Mapping[str, str]  # read-only view
    startup_check_id: str


def start(
    store: Store,
    *,
    root: Path,
    obj: Path,
    acceptance_record: bytes,
    post_raw_tx: bytes,
    declaration: bytes,
    protocol: bytes,
    image_digest: str,
) -> Started:
    """DESIGN §4 and §6.1, before any protected-data read: the start chain
    over the two module files as they are on disk, the signed values read
    from the verified protocol bytes (never from a caller), the code check,
    then the startup record. Any failure raises ChainError and nothing is
    appended. That the *running* bytes are these files is the launch
    route's to establish (LG-8, R14D3-S-2): this function cannot run before
    the module that contains it."""
    files = {row: (root / path).read_bytes() for row, path in MODULE_PATHS.items()}
    log = verify_chain(
        acceptance_record=acceptance_record,
        post_raw_tx=post_raw_tx,
        declaration=declaration,
        protocol=protocol,
        modules=files,
    )
    rows = {name: protocol_row(protocol, name) for name in SIGNED_ROWS}
    signed = Signed(
        protocol_hash=log["protocol_hash"],
        lockbox_module_sha256=log["lockbox_module_sha256"],
        confirmation_module_sha256=log["confirmation_module_sha256"],
        engine_commit=rows["engine_commit"],
        screen_object_sha256=rows["screen_object_sha256"],
        image_digest=rows["image_digest"],
    )
    defn = verify_code(
        obj,
        rows["qualification_object_sha256"],
        root,
        {MODULE_PATHS[row]: data for row, data in files.items()},
    )
    if defn.get("engine_commit") != signed.engine_commit:
        raise ChainError("the object's engine commit is not the signed one")
    if image_digest != signed.image_digest:  # R14L2-S-3: before any append
        raise ChainError("the running image is not the signed one")
    startup_check_id = record_startup(store, signed, image_digest)
    return Started(
        signed,
        bytes(declaration),
        log["declaration_sha256"],
        types.MappingProxyType(dict(log)),
        startup_check_id,
    )


def record_startup(store: Store, signed: Signed, image_digest: str) -> str:
    """§6.1 / §D-3.4: once per process start, after the start chain:
    recompute the A5 vectors and ask the store to append the record."""
    vectors, result = startup_result()
    return store.append_startup(
        {
            "lockbox_module_sha256": signed.lockbox_module_sha256,
            "image_digest": image_digest,
            "vectors_sha256": vectors,
            "result": result,
        }
    )


def _install_trial_code(
    trial: dict[str, Any], files: Mapping[str, bytes], code_dir: Path
) -> None:
    """Write the nominee's signal and overlay sources (verified by the
    pre-read check) as `<module>.py` into an empty directory placed last on
    the import path, as the screen's driver does (`screen._extend_path`);
    `screen.load` hashes them again before executing."""
    if any(code_dir.iterdir()):
        raise LockboxError("INVALID_ARGUMENT", "the code directory is not empty")
    for ref, digest in ((trial["signal"], trial["signal_sha256"]),
                        (trial["overlay"], trial["overlay_sha256"])):  # fmt: skip
        if ref is not None:
            (code_dir / f"{ref.split(':')[0]}.py").write_bytes(files[digest])
    engine, code = screen._paths(code_dir)
    screen._extend_path(engine, code)


def run_evaluation(
    store: Store,
    *,
    evaluation: Evaluation,
    started: Started,
    request: Request,
    artifact_bytes: bytes | None,
    artifacts_ledger: Mapping[str, Any],
    files: Mapping[str, bytes],
    manifest_sha256: str,
    startup: Mapping[str, Any] | None,
    code_dir: Path,
) -> str:
    """§6.3-§6.5 in order. Returns what happened: the pre-read reason code,
    "STOPPED" (a store refusal; nothing written), or the bundle's result.

    The inputs that are not `started`'s are the store's records (§D-3.7);
    the bindings only the store can make are its obligations, listed on
    `Store` (R14L4-S-3)."""
    signed = started.signed
    image_digest = signed.image_digest  # start() refused any other image
    # R14L4-S-1: one immutable snapshot, checked and then computed from, so
    # nothing the check approved can be swapped before the run
    artifacts_ledger = copy.deepcopy(dict(artifacts_ledger))
    files = {k: bytes(v) for k, v in files.items()}
    artifact_bytes = None if artifact_bytes is None else bytes(artifact_bytes)
    # R14L4-S-2: only this process's own startup record counts
    if startup is not None and (
        startup.get("startup_check_id") != started.startup_check_id
    ):
        startup = None
    result = pre_read_check(
        request=request,
        signed=signed,
        declaration=started.declaration,
        declaration_sha256=started.declaration_sha256,
        artifact_bytes=artifact_bytes,
        artifacts_ledger=artifacts_ledger,
        files=files,
        manifest_sha256=manifest_sha256,
        image_digest=image_digest,
        startup=startup,
    )
    try:
        store.record_pre_read_check(
            {
                "evaluation_id": evaluation.evaluation_id,
                "family": request.family,
                "nominee_trial_id": request.nominee_trial_id,
                "prediction_artifact_sha256": request.prediction_artifact_sha256,
                "eligibility_result_id": evaluation.eligibility_result_id,
                "lockbox_evaluation_id": evaluation.lockbox_evaluation_id,
                "sealing_id": evaluation.sealing_id,
                # the id of the very record the check used, never a caller's
                "startup_check_id": None
                if startup is None
                else startup.get("startup_check_id"),
                "lockbox_module_sha256": signed.lockbox_module_sha256,
                "image_digest": image_digest,
                "result": result,
            }
        )
        if result != "PASS":
            return result  # nothing read; the segment is not EXPOSED
        assert artifact_bytes is not None
        artifact = json.loads(artifact_bytes)
        trial = json.loads(_check_items(artifacts_ledger, files))
        _install_trial_code(trial, files, code_dir)
        session = store.open_read(evaluation.evaluation_id)
        bundle = compute_twice(
            evaluation.evaluation_id,
            trial,
            artifact["nominee"]["estimator_seed"],
            session.read,
            unhexf(artifact["q"]),
            [unhexf(x) for x in artifact["replicates_sorted"]],
            {
                "engine_commit": signed.engine_commit,
                "image_digest": image_digest,
                "input_manifest_sha256": manifest_sha256,
                "lockbox_module_sha256": signed.lockbox_module_sha256,
                "prediction_artifact_sha256": request.prediction_artifact_sha256,
            },
        )
        store.write_bundle(evaluation.evaluation_id, bundle)
        store.mark_finished(evaluation.evaluation_id)
    except StoreRefused:
        return "STOPPED"
    return str(bundle["result"])
