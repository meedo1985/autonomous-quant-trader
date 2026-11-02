"""R-14a lockbox module (Annex D; review/r14a-modules/DESIGN.md §6, §7.1).

Slices 1-2 of the build, pure functions only (no store, no data read, no
clock): the A4 forecast generator, the A5 reference vectors, the A6 adapter,
the L-1..L-4 pass rule, the `aqt.lockbox.sealed_bundle.v1` body and the
pre-read checks (§6.3). The load-and-verify start (DESIGN §4), the store
calls and the read are a later slice. Nothing here binds until its SHA-256
is a row of the signed C2 (R-14a item 1); until then it is a draft under
review.

R-14a item 3: imports only engine-commit modules, the object's `screen.py`,
the standard library and pinned image libraries; never the confirmation
module. Item 4: frozen functions are called, not re-implemented; A4's
lockbox stream (no frozen function for m != n) is implemented here exactly
as Annex D §D-3.4 states it.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import struct
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, fields
from datetime import UTC, datetime, timedelta
from typing import Any

import aqt.metrics.statistics as st
from aqt.backtest.event_contract import EventContractError, EventResult
from aqt.core.preregistration import PreregistrationError, trial_seed
from aqt.data.bars import BarSeries
from aqt.metrics.descriptive import _max_drawdown
from calibration import screen
from calibration.seeds import cj, sha

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
    manifest_sha256: str  # the cycle's data-manifest hash


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
            and item["kind"] in ARTIFACT_KINDS,
            "IDENTITY_MISMATCH",
        )
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
    try:
        seed_l266 = trial_seed(
            protocol_hash=signed.protocol_hash,
            hypothesis_hash=request.hypothesis_hash,
            trial_index=n["trial_index"],
        )
        estimator = screen.estimator_seed(seed_l266)
    except (PreregistrationError, screen.TrialError):
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


def pre_read_check(
    *,
    request: Request,
    signed: Signed,
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
