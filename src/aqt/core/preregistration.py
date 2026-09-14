"""Deterministic identity for preregistered hypotheses and trial records.

`docs/RESEARCH_CONSTITUTION.md` section 8 makes a hypothesis immutable after
preregistration and identified by a hash computed under section 27 and
`schemas/HASH_CANONICALIZATION_v1.md`. Section 9 counts trials, and
`protocols/protocol_v1.yaml` fixes the seed policy as
`SHA256(protocol_hash, hypothesis_hash, trial_index)`. This module implements
those identity rules and writes the resulting records to the tamper-evident
ledger in `aqt.core.ledger`.

Canonical content identity
--------------------------
Hypothesis content is canonicalized before hashing: mapping keys are sorted
recursively, list order is preserved, and CRLF and lone CR inside string values
are normalized to LF, so the same preregistration text checked out on Windows
and on Linux has the same identity. The self-referential `content_hash` field
is removed before hashing, matching the convention Task 9 accepted for
`manifest_sha256` and `environment_sha256`. The registration timestamp lives in
the ledger envelope and therefore never moves the content identity.

Canonical JSON rejects every floating-point value, so preregistered parameter
values and horizons must be `null`, a boolean, an integer, or a string. An
exact decimal such as the protocol's `0.60` vol target is preregistered as the
string `"0.60"`, which has one unambiguous byte representation; a binary
float's decimal repr does not.

Trial enumeration
-----------------
A grid enumerates as the Cartesian product of the parameter names in sorted
order, each value list in its preregistered order, followed by the horizons in
their preregistered order. The position in that fixed enumeration is the trial
index, which is scoped to one hypothesis.

Boundary
--------
This module records facts. It does not decide whether a trial may begin, does
not compare counts against `trial_accounting` budgets, does not accept or bind
a protocol, data-manifest, or backtester hash, and reads no confirmation or
lockbox data. `family_trial_counts` is arithmetic over recorded entries and
carries no eligibility meaning.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Any, Final

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from jsonschema.exceptions import (  # type: ignore[import-untyped]
    SchemaError,
    ValidationError,
)

from aqt.core.ledger import LedgerEntry, append_entry
from aqt.core.paths import REPOSITORY_ROOT
from aqt.data.manifest import canonical_json_bytes

__all__ = [
    "CONTENT_HASH_FIELD",
    "EXPERIMENT_SCHEMA_PATH",
    "HYPOTHESIS_RECORD_TYPE",
    "HYPOTHESIS_SCHEMA_PATH",
    "PROTOCOL_STATUS_FROZEN",
    "SEED_DOMAIN",
    "TRIAL_RECORD_TYPE",
    "FamilyTrialCounts",
    "PreregistrationError",
    "TrialPoint",
    "canonical_content_bytes",
    "enumerate_trials",
    "experiment_record",
    "family_trial_counts",
    "hypothesis_content_hash",
    "hypothesis_trial_indices",
    "normalize_content",
    "preregister_hypothesis",
    "record_hypothesis",
    "record_trial",
    "recorded_hypotheses",
    "seed_material",
    "trial_seed",
    "verify_hypothesis_content_hash",
]

CONTENT_HASH_FIELD: Final[str] = "content_hash"

HYPOTHESIS_SCHEMA_PATH: Final[Path] = (
    REPOSITORY_ROOT / "schemas" / "hypothesis.schema.json"
)
EXPERIMENT_SCHEMA_PATH: Final[Path] = (
    REPOSITORY_ROOT / "schemas" / "experiment.schema.json"
)

HYPOTHESIS_RECORD_TYPE: Final[str] = "aqt.preregistration.hypothesis.v1"
TRIAL_RECORD_TYPE: Final[str] = "aqt.preregistration.trial.v1"

SEED_DOMAIN: Final[str] = "aqt.trial_seed.v1"
"""Domain separator; without it a digest could be replayed from another use."""

PROTOCOL_STATUS_FROZEN: Final[str] = "FROZEN"

_HEX64: Final[str] = "0123456789abcdef"
_SCALAR_TYPES: Final[tuple[type, ...]] = (bool, int, str)


class PreregistrationError(ValueError):
    """Raised when preregistration input violates the identity rules."""


def _require_sha256(value: object, name: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in _HEX64 for char in value)
    ):
        raise PreregistrationError(
            f"{name} must be a lowercase 64-hex SHA-256, got {value!r}"
        )
    return value


def _require_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise PreregistrationError(
            f"{name} must be a non-empty unpadded string, got {value!r}"
        )
    return value


def _require_trial_index(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise PreregistrationError(f"trial_index must be an integer, got {value!r}")
    if value < 0:
        raise PreregistrationError(f"trial_index must be nonnegative, got {value}")
    return value


# ---------------------------------------------------------------------------
# Canonical content
# ---------------------------------------------------------------------------


def _normalize(value: object, path: str) -> Any:
    """Normalize line endings inside strings; leave everything else alone.

    Unsupported types are passed through so that `canonical_json_bytes` raises
    the single frozen error message for them.
    """
    if isinstance(value, str):
        return value.replace("\r\n", "\n").replace("\r", "\n")
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key in value:
            if not isinstance(key, str):
                raise PreregistrationError(f"{path} has a non-string key {key!r}")
            normalized_key = _normalize(key, path)
            if normalized_key in normalized:
                raise PreregistrationError(
                    f"{path} has two keys that collide once line endings are "
                    f"normalized: {normalized_key!r}"
                )
            normalized[normalized_key] = _normalize(value[key], f"{path}.{key}")
        return normalized
    if isinstance(value, list | tuple):
        return [
            _normalize(item, f"{path}[{index}]") for index, item in enumerate(value)
        ]
    return value


def normalize_content(content: Mapping[str, object]) -> dict[str, Any]:
    """Return `content` with CRLF and lone CR normalized to LF everywhere."""
    if not isinstance(content, Mapping):
        raise PreregistrationError(
            f"hypothesis content must be a mapping, got {type(content).__name__}"
        )
    normalized: dict[str, Any] = _normalize(content, "hypothesis")
    return normalized


def canonical_content_bytes(content: Mapping[str, object]) -> bytes:
    """Return the exact bytes the content hash is taken over."""
    payload = normalize_content(content)
    payload.pop(CONTENT_HASH_FIELD, None)
    return canonical_json_bytes(payload)


def hypothesis_content_hash(content: Mapping[str, object]) -> str:
    """Hash hypothesis content with its self-referential hash removed."""
    return hashlib.sha256(canonical_content_bytes(content)).hexdigest()


def _validate_against_schema(record: Mapping[str, object], schema_path: Path) -> None:
    """Apply the unmodified frozen Draft 2020-12 schema."""
    try:
        schema = json.loads(schema_path.read_text("utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(dict(record))
    except (OSError, json.JSONDecodeError, SchemaError, ValidationError) as error:
        detail = error.message if isinstance(error, ValidationError) else str(error)
        raise PreregistrationError(
            f"record does not validate against {schema_path.name}: {detail}"
        ) from error


def preregister_hypothesis(
    content: Mapping[str, object],
) -> dict[str, Any]:
    """Return the canonical hypothesis with its `content_hash` filled in.

    A supplied `content_hash` is checked, never trusted: an incorrect one is
    rejected rather than overwritten. The completed record is validated against
    the unmodified frozen Draft 2020-12 schema before it is returned.
    """
    normalized = normalize_content(content)
    supplied = normalized.pop(CONTENT_HASH_FIELD, None)
    digest = hashlib.sha256(canonical_json_bytes(normalized)).hexdigest()
    if supplied is not None and supplied != "" and supplied != digest:
        raise PreregistrationError(
            f"supplied content_hash {supplied!r} does not match the canonical "
            f"content hash {digest}"
        )

    _require_text(normalized.get("family"), "family")
    _require_sha256(normalized.get("protocol_hash"), "protocol_hash")
    record = {**normalized, CONTENT_HASH_FIELD: digest}
    _validate_against_schema(record, HYPOTHESIS_SCHEMA_PATH)
    return record


def verify_hypothesis_content_hash(content: Mapping[str, object]) -> str:
    """Recompute a recorded hypothesis hash and return it, or raise."""
    normalized = normalize_content(content)
    recorded = normalized.get(CONTENT_HASH_FIELD)
    if recorded is None:
        raise PreregistrationError("hypothesis content carries no content_hash")
    digest = hypothesis_content_hash(normalized)
    if recorded != digest:
        raise PreregistrationError(
            f"hypothesis content_hash mismatch: recorded {recorded!r}, recomputed "
            f"{digest}"
        )
    return digest


# ---------------------------------------------------------------------------
# Deterministic seeds
# ---------------------------------------------------------------------------


def seed_material(
    *, protocol_hash: str, hypothesis_hash: str, trial_index: int
) -> bytes:
    """Return the exact bytes hashed to derive a trial seed.

    The material is a domain-separated compact canonical JSON array. The array
    form makes the three inputs unambiguous: no concatenation of two different
    input triples can produce the same bytes.
    """
    _require_sha256(protocol_hash, "protocol_hash")
    _require_sha256(hypothesis_hash, "hypothesis_hash")
    index = _require_trial_index(trial_index)
    return json.dumps(
        [SEED_DOMAIN, protocol_hash, hypothesis_hash, index],
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def trial_seed(*, protocol_hash: str, hypothesis_hash: str, trial_index: int) -> str:
    """Derive the protocol's deterministic seed as the full SHA-256 hex digest."""
    return hashlib.sha256(
        seed_material(
            protocol_hash=protocol_hash,
            hypothesis_hash=hypothesis_hash,
            trial_index=trial_index,
        )
    ).hexdigest()


# ---------------------------------------------------------------------------
# Deterministic trial enumeration
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TrialPoint:
    """One enumerated `(parameter_point, horizon)` pair and its index."""

    trial_index: int
    parameters: tuple[tuple[str, object], ...]
    horizon: object

    def as_mapping(self) -> dict[str, object]:
        return {
            "horizon": self.horizon,
            "parameters": dict(self.parameters),
            "trial_index": self.trial_index,
        }


def _require_scalar(value: object, name: str) -> object:
    if value is None:
        return value
    if isinstance(value, float):
        raise PreregistrationError(
            f"{name} is the float {value!r}; canonical JSON rejects floating-point "
            "values, so preregister an exact decimal as a string such as '0.60'"
        )
    if not isinstance(value, _SCALAR_TYPES):
        raise PreregistrationError(
            f"{name} has unsupported type {type(value).__name__}; preregistered "
            "values must be null, a boolean, an integer, or a string"
        )
    if isinstance(value, str):
        _require_text(value, name)
        if value != _normalize(value, name):
            raise PreregistrationError(
                f"{name} contains a carriage return; preregistered values use LF"
            )
    return value


def _require_distinct_values(values: Sequence[object], name: str) -> tuple[object, ...]:
    if not isinstance(values, list | tuple):
        raise PreregistrationError(
            f"{name} must be a list of values, got {type(values).__name__}"
        )
    if not values:
        raise PreregistrationError(f"{name} must declare at least one value")
    checked = tuple(
        _require_scalar(value, f"{name}[{index}]") for index, value in enumerate(values)
    )
    # `True` and `1` are distinct preregistrations even though `True == 1`.
    keys = [(type(value).__name__, value) for value in checked]
    if len(set(keys)) != len(keys):
        raise PreregistrationError(
            f"{name} repeats a value, which makes the trial enumeration ambiguous"
        )
    return checked


def enumerate_trials(
    *,
    parameter_grid: Mapping[str, Sequence[object]],
    horizons: Sequence[object],
) -> tuple[TrialPoint, ...]:
    """Enumerate the preregistered grid in its one fixed order.

    Parameter names are sorted, each value list keeps its preregistered order,
    and the horizons form the final and fastest-varying dimension. The result
    is a tuple whose position is the trial index.
    """
    if not isinstance(parameter_grid, Mapping):
        raise PreregistrationError(
            f"parameter_grid must be a mapping, got {type(parameter_grid).__name__}"
        )
    names: list[str] = []
    for key in parameter_grid:
        name = _require_text(key, "parameter name")
        if name != _normalize(name, "parameter name"):
            raise PreregistrationError(
                f"parameter name {name!r} contains a carriage return"
            )
        names.append(name)
    if len(set(names)) != len(names):
        raise PreregistrationError("parameter_grid repeats a parameter name")

    ordered_names = tuple(sorted(names))
    axes = [
        _require_distinct_values(parameter_grid[name], f"parameter_grid[{name!r}]")
        for name in ordered_names
    ]
    horizon_axis = _require_distinct_values(horizons, "horizons")

    points: list[TrialPoint] = []
    for index, combination in enumerate(product(*axes, horizon_axis)):
        *values, horizon = combination
        points.append(
            TrialPoint(
                trial_index=index,
                parameters=tuple(zip(ordered_names, values, strict=True)),
                horizon=horizon,
            )
        )
    return tuple(points)


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------


def experiment_record(
    *,
    experiment_id: str,
    hypothesis_hash: str,
    protocol_hash: str,
    trial_index: int,
    backtester_hash: str,
    data_manifest_hash: str,
) -> dict[str, object]:
    """Build an experiment record whose seed is derived, not supplied.

    The hashes are recorded exactly as given. Nothing here accepts them,
    checks them against an accepted binding, or grants permission to run.
    """
    _require_text(experiment_id, "experiment_id")
    _require_sha256(hypothesis_hash, "hypothesis_hash")
    _require_sha256(protocol_hash, "protocol_hash")
    index = _require_trial_index(trial_index)
    record: dict[str, object] = {
        "backtester_hash": _require_text(backtester_hash, "backtester_hash"),
        "data_manifest_hash": _require_text(data_manifest_hash, "data_manifest_hash"),
        "experiment_id": experiment_id,
        "hypothesis_hash": hypothesis_hash,
        "protocol_hash": protocol_hash,
        "protocol_status": PROTOCOL_STATUS_FROZEN,
        "seed": trial_seed(
            protocol_hash=protocol_hash,
            hypothesis_hash=hypothesis_hash,
            trial_index=index,
        ),
        "trial_index": index,
    }
    _validate_against_schema(record, EXPERIMENT_SCHEMA_PATH)
    return record


def record_hypothesis(
    ledger_path: Path | str,
    content: Mapping[str, object],
    *,
    recorded_at_utc: datetime | None = None,
) -> LedgerEntry:
    """Append a preregistered hypothesis to the ledger.

    The stored payload is the canonical, line-ending-normalized content, so
    the recorded bytes reproduce the recorded `content_hash` exactly.
    """
    record = preregister_hypothesis(content)
    return append_entry(
        ledger_path,
        record_type=HYPOTHESIS_RECORD_TYPE,
        payload=record,
        recorded_at_utc=recorded_at_utc,
    )


def record_trial(
    ledger_path: Path | str,
    *,
    family: str,
    experiment: Mapping[str, object],
    recorded_at_utc: datetime | None = None,
) -> LedgerEntry:
    """Append one trial record, re-deriving its seed before it is stored.

    `family` is recorded so that read-side accounting can attribute the trial.
    Recording a trial is not permission to run one.
    """
    _require_text(family, "family")
    record = dict(normalize_content(experiment))
    expected = trial_seed(
        protocol_hash=_require_sha256(record.get("protocol_hash"), "protocol_hash"),
        hypothesis_hash=_require_sha256(
            record.get("hypothesis_hash"), "hypothesis_hash"
        ),
        trial_index=_require_trial_index(record.get("trial_index")),
    )
    if record.get("seed") != expected:
        raise PreregistrationError(
            f"experiment seed {record.get('seed')!r} is not the seed derived from "
            f"its protocol hash, hypothesis hash, and trial index ({expected})"
        )
    if record.get("protocol_status") != PROTOCOL_STATUS_FROZEN:
        raise PreregistrationError(
            f"protocol_status must be {PROTOCOL_STATUS_FROZEN!r}, got "
            f"{record.get('protocol_status')!r}"
        )
    _validate_against_schema(record, EXPERIMENT_SCHEMA_PATH)
    return append_entry(
        ledger_path,
        record_type=TRIAL_RECORD_TYPE,
        payload={"experiment": record, "family": family},
        recorded_at_utc=recorded_at_utc,
    )


# ---------------------------------------------------------------------------
# Read-side accounting
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class FamilyTrialCounts:
    """Arithmetic over recorded trial entries for one family.

    `recorded_trials` counts entries, including repeats of the same trial
    point, because Constitution section 9 counts aborted and failed runs.
    `distinct_trial_points` counts unique `(hypothesis_hash, trial_index)`
    pairs. Neither number is compared with any budget here.
    """

    family: str
    recorded_trials: int
    distinct_trial_points: int


def recorded_hypotheses(entries: Iterable[LedgerEntry]) -> tuple[dict[str, Any], ...]:
    """Return the hypothesis payloads in recorded order."""
    return tuple(
        entry.payload
        for entry in entries
        if entry.record_type == HYPOTHESIS_RECORD_TYPE
    )


def _trial_payloads(entries: Iterable[LedgerEntry]) -> list[dict[str, Any]]:
    return [
        entry.payload for entry in entries if entry.record_type == TRIAL_RECORD_TYPE
    ]


def hypothesis_trial_indices(
    entries: Iterable[LedgerEntry], hypothesis_hash: str
) -> tuple[int, ...]:
    """Return the trial indices recorded for one hypothesis, in ledger order."""
    _require_sha256(hypothesis_hash, "hypothesis_hash")
    return tuple(
        int(payload["experiment"]["trial_index"])
        for payload in _trial_payloads(entries)
        if payload["experiment"]["hypothesis_hash"] == hypothesis_hash
    )


def family_trial_counts(
    entries: Iterable[LedgerEntry],
) -> tuple[FamilyTrialCounts, ...]:
    """Count recorded trials per family, sorted by family name.

    This is lifetime accounting in the sense of section 9: it counts what the
    ledger records. It grants nothing and stops nothing.
    """
    recorded: dict[str, int] = {}
    distinct: dict[str, set[tuple[str, int]]] = {}
    for payload in _trial_payloads(entries):
        family = str(payload["family"])
        experiment = payload["experiment"]
        recorded[family] = recorded.get(family, 0) + 1
        distinct.setdefault(family, set()).add(
            (str(experiment["hypothesis_hash"]), int(experiment["trial_index"]))
        )
    return tuple(
        FamilyTrialCounts(
            family=family,
            recorded_trials=recorded[family],
            distinct_trial_points=len(distinct[family]),
        )
        for family in sorted(recorded)
    )
