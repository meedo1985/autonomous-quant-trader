"""Evaluation-attempt counting tests. Synthetic records only, no real data."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from aqt.core.attempts import (
    ATTEMPT_OUTCOME_RECORD_TYPE,
    ATTEMPT_STARTED_RECORD_TYPE,
    OUTCOME_ABORTED,
    OUTCOME_COMPLETED,
    OUTCOME_FAILED,
    PARTITION_CONFIRMATION,
    PARTITION_EXPLORATION,
    PARTITION_TRAINING,
    AttemptCounts,
    AttemptError,
    attempt_counts,
    finish_attempt,
    recorded_attempts,
    start_attempt,
    started_attempt_ids,
)
from aqt.core.ledger import LedgerEntry, read_entries, verify_ledger

_HYPOTHESIS_HASH = "c" * 64
_OTHER_HYPOTHESIS_HASH = "d" * 64
_PROTOCOL_HASH = "a" * 64
_MOMENT = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
_FAMILY = "family-one"
_CYCLE = "C1"


def _start(
    path: Path,
    attempt_id: str,
    *,
    family: str = _FAMILY,
    cycle: str = _CYCLE,
    partition: str = PARTITION_TRAINING,
    hypothesis_hash: str = _HYPOTHESIS_HASH,
    trial_index: int = 0,
    symbols: tuple[str, ...] = ("BTC", "ETH"),
) -> LedgerEntry | None:
    return start_attempt(
        path,
        attempt_id=attempt_id,
        family=family,
        cycle=cycle,
        partition=partition,
        hypothesis_hash=hypothesis_hash,
        protocol_hash=_PROTOCOL_HASH,
        trial_index=trial_index,
        symbols=symbols,
        recorded_at_utc=_MOMENT,
    )


def _counts(path: Path, *, family: str = _FAMILY, cycle: str = _CYCLE) -> AttemptCounts:
    return attempt_counts(read_entries(path), family=family, cycle=cycle)


# ---------------------------------------------------------------------------
# The property the mechanism exists for
# ---------------------------------------------------------------------------


def test_attempt_counts_even_when_evaluation_raises(tmp_path: Path) -> None:
    """Constitution section 9: aborted evaluated runs count, all failures count.

    The attempt is recorded before evaluation begins, so an exception raised
    inside the evaluation body cannot remove it from the count.
    """
    ledger = tmp_path / "ledger.jsonl"

    with pytest.raises(RuntimeError):
        _start(ledger, "attempt-0001")
        raise RuntimeError("evaluation blew up after the record was written")

    assert _counts(ledger).cycle_attempts == 1


def test_attempt_with_no_outcome_counts_like_a_completed_one(tmp_path: Path) -> None:
    """A process that dies before writing an outcome still leaves the attempt."""
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-crashed")
    _start(ledger, "attempt-finished")
    finish_attempt(
        ledger,
        attempt_id="attempt-finished",
        outcome=OUTCOME_COMPLETED,
        recorded_at_utc=_MOMENT,
    )

    assert _counts(ledger).cycle_attempts == 2


@pytest.mark.parametrize(
    "outcome", [OUTCOME_COMPLETED, OUTCOME_FAILED, OUTCOME_ABORTED]
)
def test_no_outcome_can_annul_an_attempt(tmp_path: Path, outcome: str) -> None:
    """Counting reads started records only; an outcome never decrements."""
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001")
    before = _counts(ledger).cycle_attempts

    finish_attempt(
        ledger, attempt_id="attempt-0001", outcome=outcome, recorded_at_utc=_MOMENT
    )

    assert _counts(ledger).cycle_attempts == before == 1


# ---------------------------------------------------------------------------
# Redelivery, reruns, joint legs
# ---------------------------------------------------------------------------


def test_redelivery_of_the_same_attempt_id_adds_nothing(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    first = _start(ledger, "attempt-0001")
    again = _start(ledger, "attempt-0001")

    assert first is not None
    assert again is None
    assert _counts(ledger).cycle_attempts == 1
    assert len(recorded_attempts(read_entries(ledger))) == 1


def test_a_rerun_of_the_same_trial_point_is_a_new_attempt(tmp_path: Path) -> None:
    """Two occasions, one trial point: two attempts, one distinct point."""
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001", trial_index=7)
    _start(ledger, "attempt-0002", trial_index=7)

    counts = _counts(ledger)
    assert counts.cycle_attempts == 2
    assert counts.distinct_trial_points == 1


def test_joint_legs_are_one_attempt(tmp_path: Path) -> None:
    """protocol_v1.yaml:178-180 - ETH sanity does not double the trial count."""
    ledger = tmp_path / "ledger.jsonl"
    entry = _start(ledger, "attempt-0001", symbols=("ETH", "BTC"))

    assert entry is not None
    assert entry.payload["symbols"] == ["BTC", "ETH"]
    assert _counts(ledger).cycle_attempts == 1


def test_distinct_points_never_exceeds_attempts(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    for index, identifier in enumerate(["run-0001", "run-0002", "run-0003"]):
        _start(ledger, identifier, trial_index=index % 2)

    counts = _counts(ledger)
    assert counts.distinct_trial_points == 2
    assert counts.distinct_trial_points <= counts.cycle_attempts == 3


# ---------------------------------------------------------------------------
# Exploration, cycles, families
# ---------------------------------------------------------------------------


def test_exploration_is_excluded_but_reported(tmp_path: Path) -> None:
    """Section 9: exploration is not a registered trial."""
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001", partition=PARTITION_TRAINING)
    _start(ledger, "explore-0001", partition=PARTITION_EXPLORATION)
    _start(ledger, "explore-0002", partition=PARTITION_EXPLORATION)

    counts = _counts(ledger)
    assert counts.cycle_attempts == 1
    assert counts.lifetime_attempts == 1
    assert counts.excluded_exploration_attempts == 2


def test_lifetime_persists_across_cycles(tmp_path: Path) -> None:
    """Section 9: lifetime family accounting persists."""
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "c1-attempt-1", cycle="C1")
    _start(ledger, "c2-attempt-1", cycle="C2")
    _start(ledger, "c2-attempt-2", cycle="C2")

    second = _counts(ledger, cycle="C2")
    assert second.cycle_attempts == 2
    assert second.lifetime_attempts == 3


def test_counts_are_scoped_to_one_family(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "fam-a-0001", family="family-one")
    _start(ledger, "fam-b-0001", family="family-two")

    assert _counts(ledger, family="family-one").lifetime_attempts == 1
    assert _counts(ledger, family="family-two").lifetime_attempts == 1


def test_confirmation_partition_counts(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001", partition=PARTITION_CONFIRMATION)

    assert _counts(ledger).cycle_attempts == 1


def test_empty_ledger_counts_zero(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "other-family", family="family-two")

    counts = _counts(ledger)
    assert counts.cycle_attempts == 0
    assert counts.lifetime_attempts == 0
    assert counts.distinct_trial_points == 0


# ---------------------------------------------------------------------------
# Ledger integrity and record shape
# ---------------------------------------------------------------------------


def test_records_land_in_a_verifiable_chain(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001")
    finish_attempt(
        ledger,
        attempt_id="attempt-0001",
        outcome=OUTCOME_FAILED,
        reason_code="INVALID_SERIES",
        recorded_at_utc=_MOMENT,
    )

    verification = verify_ledger(ledger)
    assert verification.intact, verification.problem
    verification.require_intact()

    entries = read_entries(ledger)
    assert [entry.record_type for entry in entries] == [
        ATTEMPT_STARTED_RECORD_TYPE,
        ATTEMPT_OUTCOME_RECORD_TYPE,
    ]
    assert entries[1].payload["reason_code"] == "INVALID_SERIES"


def test_started_attempt_ids_round_trips(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001")
    _start(ledger, "attempt-0002")

    assert started_attempt_ids(read_entries(ledger)) == {"attempt-0001", "attempt-0002"}


# ---------------------------------------------------------------------------
# Rejections
# ---------------------------------------------------------------------------


def test_outcome_without_a_start_is_refused(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"

    with pytest.raises(AttemptError, match="no recorded start"):
        finish_attempt(
            ledger,
            attempt_id="never-started",
            outcome=OUTCOME_COMPLETED,
            recorded_at_utc=_MOMENT,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("attempt_id", "short"),
        ("attempt_id", "has spaces in it"),
        ("family", ""),
        ("cycle", ""),
        ("partition", "lockbox"),
        ("hypothesis_hash", "C" * 64),
        ("hypothesis_hash", "abc"),
        ("trial_index", -1),
        ("trial_index", True),
        ("symbols", ()),
        ("symbols", ("BTC", "BTC")),
        ("symbols", "BTC"),
    ],
)
def test_malformed_fields_are_refused(
    tmp_path: Path, field: str, value: object
) -> None:
    ledger = tmp_path / "ledger.jsonl"
    kwargs: dict[str, object] = {
        "attempt_id": "attempt-0001",
        "family": _FAMILY,
        "cycle": _CYCLE,
        "partition": PARTITION_TRAINING,
        "hypothesis_hash": _HYPOTHESIS_HASH,
        "protocol_hash": _PROTOCOL_HASH,
        "trial_index": 0,
        "symbols": ("BTC",),
        "recorded_at_utc": _MOMENT,
    }
    kwargs[field] = value

    with pytest.raises(AttemptError):
        start_attempt(ledger, **kwargs)  # type: ignore[arg-type]

    assert not ledger.exists() or _counts(ledger).cycle_attempts == 0


def test_unknown_outcome_is_refused(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001")

    with pytest.raises(AttemptError, match="outcome must be one of"):
        finish_attempt(
            ledger,
            attempt_id="attempt-0001",
            outcome="cancelled",
            recorded_at_utc=_MOMENT,
        )
