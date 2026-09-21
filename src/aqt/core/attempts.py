"""Durable evaluation-attempt records, written before evaluation begins.

`docs/RESEARCH_CONSTITUTION.md` section 9 fixes when a trial counts:

    Count when evaluation begins; aborted evaluated runs count.
    All failures count. Lifetime family accounting persists.
    Exploration is not a registered trial because it is confined to
    exploration data.

`aqt.core.preregistration` records a trial *point* — an identity derived from a
hypothesis hash and a position in a preregistered grid. That is a different
fact from an *attempt*, which is one occasion on which evaluation actually
began. One trial point may be attempted several times; section 9 counts each
occasion, including the ones that failed.

Why the record is written first
-------------------------------
The attempt count is an input to the deflated Sharpe ratio hurdle
`S0 = sqrt(V) * A(N)`, where `A(N)` is the expected maximum of `N` standard
normals. `A` is increasing in `N`, so an undercounted `N` lowers the hurdle, and
a lowered hurdle promotes noise. The counting error that matters is therefore
the *missing* attempt, not the mistaken one.

`protocols/protocol_v1.yaml` lines 227-233 fix the DSR series, the
`minimum: 0.95` gate, the effective-count method and its fallback; they do not
state the equation, and an earlier revision of this docstring cited them as
though they did (finding F-7). The equation is Bailey and Lopez de Prado (2014)
as recorded in
`review/governance-statistics-amendment/DSR_METHOD_PREREGISTRATION_DRAFT.md`,
which is an unaccepted draft: treat the specific functional form as an external
assumption rather than as frozen text. What this module depends on is only that
the hurdle is non-decreasing in the trial count, which holds for the maximum of
`N` draws regardless of the form eventually accepted.

Attempts go missing when the count depends on someone remembering to record a
run that crashed, or that was abandoned once its equity curve looked wrong.
This module removes that dependency: `start_attempt` writes a durable
`EVALUATION_STARTED` record *before* evaluation reads data or computes
anything, and the count is taken from those records alone. An attempt that
crashes one line later is already counted. Nothing this module does can be
undone by a later failure, because nothing it counts is written afterwards.

An outcome record may follow and is useful for diagnosis, but no count in this
module reads it. A started attempt with no outcome counts exactly as much as a
completed one.

Redelivery, reruns, and joint legs
----------------------------------
`attempt_id` is supplied by the caller and identifies one occasion. Recording
the same `attempt_id` twice, with the same payload, is redelivery of one event
and adds no attempt; a different payload under the same identifier is refused
rather than dropped; each genuinely new occasion needs a new identifier.

The redelivery check is **not atomic**. It reads the ledger before
`append_entry` takes its exclusive lock, so two processes starting the same
`attempt_id` at the same moment can both append (finding F-3). The resulting
error is an over-count, which raises the hurdle and is therefore the safe
direction, but a caller must not treat a `None` return as a lock: it means
"already recorded", not "no one else is running this".

`protocols/protocol_v1.yaml` lines 178-180 make BTC and ETH one joint trial, so
one attempt carries the whole symbol set and counts once. Splitting the legs
across two `attempt_id`s would count two, which this module cannot detect and
cannot prevent; it over-counts, so it fails in the safe direction.

Partitions
----------
`protocols/protocol_v1.yaml` lines 64-66 define exactly three partitions:
`exploration`, `confirmation`, and `lockbox`. Section 9 excludes exploration
from registered trials, so exploration attempts are recorded for audit and
counted separately. The lockbox stage is a separate one-shot evaluation that
section 9 does not address, so it is also counted separately and merged into
nothing. The partition is a required field, and an unrecognized one is refused,
so an exclusion is always stated rather than assumed.

A caller supplies the label, and section 9's criterion is a fact about the data
mounted rather than about the label — so a caller that mislabels a confirmation
run as exploration lowers `N`. This module cannot detect that (finding F-5).
Whoever mounts the partition should set the label, not the research caller.

Boundary
--------
This module records facts and counts records. It does not decide whether an
attempt may begin, does not compare any count against a `trial_accounting`
budget, does not compute or bind an effective trial count, does not read
confirmation or lockbox data, and holds no eligibility meaning. Which count
enters `A(N)`, and whether an effective-count method applies to it, are open
governance decisions (`review/governance-statistics-amendment/`
`v1.1-method-candidate/HUMAN_DECISION_MATRIX.md` rows `D-16` and `D-17`); this
module deliberately supplies the raw counts separately and merges none of them.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Final

from aqt.core.ledger import LedgerEntry, append_entry, read_entries

__all__ = [
    "ATTEMPT_OUTCOME_RECORD_TYPE",
    "ATTEMPT_STARTED_RECORD_TYPE",
    "OUTCOME_ABORTED",
    "OUTCOME_COMPLETED",
    "OUTCOME_FAILED",
    "PARTITION_CONFIRMATION",
    "PARTITION_EXPLORATION",
    "PARTITION_LOCKBOX",
    "AttemptCounts",
    "AttemptError",
    "attempt_counts",
    "finish_attempt",
    "recorded_attempts",
    "start_attempt",
    "started_attempt_ids",
]

ATTEMPT_STARTED_RECORD_TYPE: Final[str] = "aqt.evaluation.attempt_started.v1"
ATTEMPT_OUTCOME_RECORD_TYPE: Final[str] = "aqt.evaluation.attempt_outcome.v1"

# The frozen vocabulary, and only it: `protocols/protocol_v1.yaml` lines 64-66
# define exactly these three partitions. An earlier revision of this module also
# defined a `training` partition, which appears nowhere in the frozen corpus as a
# partition name; line 68 `exploration_may_enter_training_folds` is a fold rule.
# Inventing a fourth partition here would have let a caller label an attempt with
# a name no frozen text recognizes (finding F-5).
PARTITION_EXPLORATION: Final[str] = "exploration"
PARTITION_CONFIRMATION: Final[str] = "confirmation"
PARTITION_LOCKBOX: Final[str] = "lockbox"

_PARTITIONS: Final[frozenset[str]] = frozenset(
    {PARTITION_EXPLORATION, PARTITION_CONFIRMATION, PARTITION_LOCKBOX}
)

# Constitution section 9 excludes exploration from registered trials, and says
# nothing about the lockbox stage, which is a separate one-shot evaluation rather
# than a family trial. Counting it as a family trial, or not counting it, are both
# decisions this module is not entitled to make, so `lockbox` is reported in its
# own field and merged into nothing. Which, if any, of these counts enters `A(N)`
# remains decision `D-17`.
_COUNTED_PARTITIONS: Final[frozenset[str]] = frozenset({PARTITION_CONFIRMATION})

OUTCOME_COMPLETED: Final[str] = "completed"
OUTCOME_FAILED: Final[str] = "failed"
OUTCOME_ABORTED: Final[str] = "aborted"

_OUTCOMES: Final[frozenset[str]] = frozenset(
    {OUTCOME_COMPLETED, OUTCOME_FAILED, OUTCOME_ABORTED}
)

_ATTEMPT_ID_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\A[A-Za-z0-9][A-Za-z0-9._:-]{7,127}\Z"
)
_SHA256_PATTERN: Final[re.Pattern[str]] = re.compile(r"\A[0-9a-f]{64}\Z")


class AttemptError(ValueError):
    """An attempt record is malformed, or contradicts one already recorded."""


def _require_text(value: object, name: str) -> str:
    """Require non-empty text with no surrounding whitespace.

    `aqt.core.ledger._require_text` rejects padded text, and an earlier revision
    of this module did not, so `"family-one "` and `"family-one"` were two
    families and a lifetime count silently split between them (finding F-4).
    Case is left significant rather than folded, because folding would merge
    families a caller meant to keep apart; drift is refused, not repaired.
    """
    if not isinstance(value, str) or not value.strip():
        raise AttemptError(f"{name} must be a non-empty string, got {value!r}")
    if value != value.strip():
        raise AttemptError(
            f"{name} must not have leading or trailing whitespace, got {value!r}"
        )
    return value


def _require_sha256(value: object, name: str) -> str:
    text = _require_text(value, name)
    if not _SHA256_PATTERN.fullmatch(text):
        raise AttemptError(f"{name} must be 64 lowercase hex characters, got {text!r}")
    return text


def _require_attempt_id(value: object) -> str:
    text = _require_text(value, "attempt_id")
    if not _ATTEMPT_ID_PATTERN.fullmatch(text):
        raise AttemptError(
            "attempt_id must be 8 to 128 characters of letters, digits, dot, "
            f"colon, hyphen, or underscore, starting alphanumeric, got {text!r}"
        )
    return text


def _require_choice(value: object, allowed: frozenset[str], name: str) -> str:
    text = _require_text(value, name)
    if text not in allowed:
        raise AttemptError(f"{name} must be one of {sorted(allowed)!r}, got {text!r}")
    return text


def _require_trial_index(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AttemptError(f"trial_index must be a non-negative integer, got {value!r}")
    return value


def _require_symbols(value: object) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, Iterable):
        raise AttemptError(f"symbols must be a sequence of strings, got {value!r}")
    symbols = tuple(_require_text(item, "symbol") for item in value)
    if not symbols:
        raise AttemptError("symbols must name at least one symbol")
    if len(set(symbols)) != len(symbols):
        raise AttemptError(f"symbols must be distinct, got {symbols!r}")
    # protocol_v1.yaml:178-180 - BTC and ETH are one joint trial, so the whole
    # symbol set belongs to a single attempt and is stored in a fixed order.
    return tuple(sorted(symbols))


_ATTEMPT_FIELDS: Final[tuple[str, ...]] = (
    "attempt_id",
    "family",
    "cycle",
    "partition",
    "hypothesis_hash",
    "protocol_hash",
    "trial_index",
    "symbols",
)


def _validated_attempt(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Re-validate a stored started record, raising on anything unrecognized.

    Counting must fail closed. An earlier revision filtered on partition and
    family membership, so a started record with an unknown partition or a
    missing field matched no filter and disappeared from every count while
    remaining in the ledger — a recorded attempt that was counted nowhere
    (finding F-2). Reading is therefore strict: a record this module cannot
    interpret stops the count rather than being skipped, because a count that
    silently omits an attempt is worse than no count at all.
    """
    unknown = set(payload) - set(_ATTEMPT_FIELDS)
    if unknown:
        raise AttemptError(
            f"started record has unrecognized field(s) {sorted(unknown)!r}; "
            "refusing to count a record this version cannot interpret"
        )
    missing = [field for field in _ATTEMPT_FIELDS if field not in payload]
    if missing:
        raise AttemptError(
            f"started record is missing field(s) {missing!r}: {payload!r}"
        )
    symbols = payload["symbols"]
    if not isinstance(symbols, list):
        raise AttemptError(f"symbols must be a list, got {symbols!r}")
    return {
        "attempt_id": _require_attempt_id(payload["attempt_id"]),
        "family": _require_text(payload["family"], "family"),
        "cycle": _require_text(payload["cycle"], "cycle"),
        "partition": _require_choice(payload["partition"], _PARTITIONS, "partition"),
        "hypothesis_hash": _require_sha256(
            payload["hypothesis_hash"], "hypothesis_hash"
        ),
        "protocol_hash": _require_sha256(payload["protocol_hash"], "protocol_hash"),
        "trial_index": _require_trial_index(payload["trial_index"]),
        "symbols": list(_require_symbols(symbols)),
    }


def recorded_attempts(entries: Iterable[LedgerEntry]) -> tuple[dict[str, Any], ...]:
    """Return the `EVALUATION_STARTED` payloads, in ledger order, unvalidated."""
    return tuple(
        entry.payload
        for entry in entries
        if entry.record_type == ATTEMPT_STARTED_RECORD_TYPE
    )


def started_attempt_ids(entries: Iterable[LedgerEntry]) -> frozenset[str]:
    """Return every `attempt_id` already recorded as started."""
    return frozenset(
        str(payload["attempt_id"]) for payload in recorded_attempts(entries)
    )


def start_attempt(
    ledger_path: Path | str,
    *,
    attempt_id: str,
    family: str,
    cycle: str,
    partition: str,
    hypothesis_hash: str,
    protocol_hash: str,
    trial_index: int,
    symbols: Iterable[str],
    recorded_at_utc: datetime | None = None,
) -> LedgerEntry | None:
    """Record that evaluation is about to begin, and return the entry.

    Call this **before** evaluation reads data or computes anything. The
    attempt is counted from the moment this returns, so a failure, an abort, or
    a crash at any later point leaves the attempt counted, which is what
    Constitution section 9 requires.

    Returns `None` when this exact attempt is already recorded — the same
    `attempt_id` with a byte-identical payload. That is event redelivery, not a
    new attempt, and it adds nothing to the ledger. A genuine rerun of the same
    trial point is a new occasion and needs its own `attempt_id`.

    Raises `AttemptError` when the `attempt_id` is already recorded with a
    *different* payload. An earlier revision returned `None` for that case too,
    which silently discarded a real attempt whenever an identifier collided or a
    caller keyed identifiers by trial point rather than by occasion — the missing
    attempt this module exists to prevent (finding F-1). A collision is a caller
    bug, and the safe response is to refuse rather than to drop or to guess.

    Raises `LedgerError`, not `AttemptError`, when the ledger itself is damaged:
    a torn trailing write or an altered historical entry stops the append and
    leaves the file exactly as found. Counting is then unavailable until a human
    repairs it, which is the intended behaviour — an unreadable ledger must not
    silently read as zero attempts.

    Recording an attempt is not permission to run one.
    """
    target = Path(ledger_path)
    payload: dict[str, Any] = {
        "attempt_id": _require_attempt_id(attempt_id),
        "family": _require_text(family, "family"),
        "cycle": _require_text(cycle, "cycle"),
        "partition": _require_choice(partition, _PARTITIONS, "partition"),
        "hypothesis_hash": _require_sha256(hypothesis_hash, "hypothesis_hash"),
        "protocol_hash": _require_sha256(protocol_hash, "protocol_hash"),
        "trial_index": _require_trial_index(trial_index),
        "symbols": list(_require_symbols(symbols)),
    }

    existing = read_entries(target) if target.is_file() else ()
    for recorded in recorded_attempts(existing):
        if recorded.get("attempt_id") != payload["attempt_id"]:
            continue
        if _validated_attempt(recorded) == payload:
            return None
        raise AttemptError(
            f"attempt_id {payload['attempt_id']!r} is already recorded with a "
            "different payload; a new occasion needs its own attempt_id. "
            f"recorded={recorded!r} offered={payload!r}"
        )

    return append_entry(
        target,
        record_type=ATTEMPT_STARTED_RECORD_TYPE,
        payload=payload,
        recorded_at_utc=recorded_at_utc,
    )


def finish_attempt(
    ledger_path: Path | str,
    *,
    attempt_id: str,
    outcome: str,
    reason_code: str | None = None,
    recorded_at_utc: datetime | None = None,
) -> LedgerEntry:
    """Record how an attempt ended. No count in this module reads this record.

    An outcome is diagnostic. It cannot decrement, cancel, or annul the attempt
    it refers to, because section 9 counts aborted and failed runs equally.
    Writing an outcome for an `attempt_id` that was never started is an error,
    since it would describe an occasion the ledger has no record of beginning.
    """
    target = Path(ledger_path)
    identifier = _require_attempt_id(attempt_id)
    resolved = _require_choice(outcome, _OUTCOMES, "outcome")

    existing = read_entries(target) if target.is_file() else ()
    if identifier not in started_attempt_ids(existing):
        raise AttemptError(
            f"attempt_id {identifier!r} has no recorded start; an outcome cannot "
            "be recorded for an attempt that never began"
        )

    payload: dict[str, Any] = {"attempt_id": identifier, "outcome": resolved}
    if reason_code is not None:
        payload["reason_code"] = _require_text(reason_code, "reason_code")

    return append_entry(
        target,
        record_type=ATTEMPT_OUTCOME_RECORD_TYPE,
        payload=payload,
        recorded_at_utc=recorded_at_utc,
    )


@dataclass(frozen=True, slots=True)
class AttemptCounts:
    """Attempt arithmetic for one family. Counts are never merged.

    `cycle_attempts` counts attempts recorded in one named cycle.
    `lifetime_attempts` counts every counted attempt in the ledger for the
    family, across cycles, because section 9 makes lifetime family accounting
    persist. `distinct_trial_points` counts unique
    `(hypothesis_hash, trial_index)` pairs attempted in the named cycle, and is
    always less than or equal to `cycle_attempts`.

    `excluded_exploration_attempts` counts this family's exploration attempts
    **in the named cycle**, which section 9 excludes from registered trials and
    which enter none of the counts above. `lockbox_attempts` counts this
    family's lockbox attempts in the named cycle. Both are reported so that an
    exclusion is visible rather than silent, and neither is merged into
    anything: section 9 excludes exploration explicitly and says nothing about
    the lockbox stage, so treating a lockbox evaluation as a family trial is a
    decision this module does not make.

    Every count here is scoped to the named cycle except `lifetime_attempts`,
    which spans cycles because section 9 makes lifetime family accounting
    persist — and which spans only the ledger file it is given.

    Which of these enters `A(N)` is decision `D-17` and is not settled here.
    None of these is an effective trial count; that is `D-16`, and Constitution
    section 9 line 106 — "If no frozen effective-count method exists, raw count
    is used" — is the frozen clause that makes these raw counts load-bearing
    until `D-16` is closed. `K`, the count of usable complete difference
    vectors, is a property of evaluation results rather than of attempts and is
    deliberately not computed by this module.
    """

    family: str
    cycle: str
    cycle_attempts: int
    lifetime_attempts: int
    distinct_trial_points: int
    excluded_exploration_attempts: int
    lockbox_attempts: int


def attempt_counts(
    entries: Iterable[LedgerEntry], *, family: str, cycle: str
) -> AttemptCounts:
    """Count recorded attempts for one family. Read-side arithmetic only.

    Counts come from `EVALUATION_STARTED` records alone. Outcome records are
    not consulted, so an attempt that crashed before writing one still counts.

    Every started record in `entries` is re-validated first, whatever family it
    belongs to, and `AttemptError` is raised if any one of them cannot be
    interpreted. Counting fails closed: a ledger holding a record this version
    does not understand yields an error, never a count that quietly omits it.
    """
    wanted_family = _require_text(family, "family")
    wanted_cycle = _require_text(cycle, "cycle")

    validated = [_validated_attempt(payload) for payload in recorded_attempts(entries)]
    payloads = [payload for payload in validated if payload["family"] == wanted_family]

    counted = [
        payload for payload in payloads if payload["partition"] in _COUNTED_PARTITIONS
    ]
    in_cycle = [payload for payload in counted if payload["cycle"] == wanted_cycle]
    points = {
        (payload["hypothesis_hash"], payload["trial_index"]) for payload in in_cycle
    }

    def _in_cycle_with(partition: str) -> int:
        return sum(
            1
            for payload in payloads
            if payload["partition"] == partition and payload["cycle"] == wanted_cycle
        )

    return AttemptCounts(
        family=wanted_family,
        cycle=wanted_cycle,
        cycle_attempts=len(in_cycle),
        lifetime_attempts=len(counted),
        distinct_trial_points=len(points),
        excluded_exploration_attempts=_in_cycle_with(PARTITION_EXPLORATION),
        lockbox_attempts=_in_cycle_with(PARTITION_LOCKBOX),
    )
