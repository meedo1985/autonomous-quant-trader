"""Evaluation-attempt counting tests. Synthetic records only, no real data."""

from __future__ import annotations

import subprocess
import sys
import textwrap
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
    PARTITION_LOCKBOX,
    AttemptCounts,
    AttemptError,
    attempt_counts,
    finish_attempt,
    recorded_attempts,
    start_attempt,
    started_attempt_ids,
)
from aqt.core.ledger import (
    LedgerEntry,
    LedgerError,
    append_entry,
    read_entries,
    verify_ledger,
)

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
    partition: str = PARTITION_CONFIRMATION,
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

    An in-process exception after `start_attempt` returns. This is the weakest
    form of the property and cannot fail once the call has returned; the real
    test of durability is `test_attempt_survives_process_death` below, which the
    section 16 review supplied after observing that this test alone proved
    nothing (finding F-10).
    """
    ledger = tmp_path / "ledger.jsonl"

    with pytest.raises(RuntimeError):
        _start(ledger, "attempt-0001")
        raise RuntimeError("evaluation blew up after the record was written")

    assert _counts(ledger).cycle_attempts == 1


def test_attempt_survives_process_death(tmp_path: Path) -> None:
    """The durability claim, tested by actually killing a process.

    A child records an attempt and then calls `os._exit`, which runs no
    finalizers, flushes no buffers, and unwinds no stack. If the record were not
    durable at the moment `start_attempt` returned, the parent would count zero.
    """
    ledger = tmp_path / "ledger.jsonl"
    script = textwrap.dedent(
        f"""
        import os
        from aqt.core.attempts import PARTITION_CONFIRMATION, start_attempt

        start_attempt(
            {str(ledger)!r},
            attempt_id="attempt-killed",
            family={_FAMILY!r},
            cycle={_CYCLE!r},
            partition=PARTITION_CONFIRMATION,
            hypothesis_hash={_HYPOTHESIS_HASH!r},
            protocol_hash={_PROTOCOL_HASH!r},
            trial_index=0,
            symbols=("BTC", "ETH"),
        )
        os._exit(1)
        """
    )

    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True
    )

    assert result.returncode == 1, result.stderr
    assert _counts(ledger).cycle_attempts == 1
    assert verify_ledger(ledger).intact


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
    _start(ledger, "attempt-0001", partition=PARTITION_CONFIRMATION)
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
        ("partition", "training"),
        ("partition", "TRAINING"),
        ("family", "family-one "),
        ("cycle", " C1"),
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
        "partition": PARTITION_CONFIRMATION,
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


# ---------------------------------------------------------------------------
# Repairs from the section 16 different-model review
# ---------------------------------------------------------------------------


def test_contradicting_redelivery_is_refused_not_dropped(tmp_path: Path) -> None:
    """F-1: a colliding attempt_id must raise, never silently lose the attempt."""
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001", family="family-one")

    with pytest.raises(AttemptError, match="already recorded with a different"):
        _start(ledger, "attempt-0001", family="family-two", cycle="C2")

    assert _counts(ledger, family="family-one").lifetime_attempts == 1


def test_identical_redelivery_is_still_idempotent(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    assert _start(ledger, "attempt-0001") is not None
    assert _start(ledger, "attempt-0001") is None
    assert _counts(ledger).cycle_attempts == 1


def test_unrecognized_started_record_stops_the_count(tmp_path: Path) -> None:
    """F-2: counting fails closed rather than silently omitting a record."""
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001")
    append_entry(
        ledger,
        record_type=ATTEMPT_STARTED_RECORD_TYPE,
        payload={
            "attempt_id": "attempt-0002",
            "family": _FAMILY,
            "cycle": _CYCLE,
            "partition": "some-future-partition",
            "hypothesis_hash": _HYPOTHESIS_HASH,
            "protocol_hash": _PROTOCOL_HASH,
            "trial_index": 0,
            "symbols": ["BTC"],
        },
        recorded_at_utc=_MOMENT,
    )

    with pytest.raises(AttemptError, match="partition must be one of"):
        _counts(ledger)


def test_started_record_missing_a_field_stops_the_count(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    append_entry(
        ledger,
        record_type=ATTEMPT_STARTED_RECORD_TYPE,
        payload={"attempt_id": "attempt-0002", "family": _FAMILY},
        recorded_at_utc=_MOMENT,
    )

    with pytest.raises(AttemptError, match="missing field"):
        _counts(ledger)


def test_unknown_extra_field_stops_the_count(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    entry = _start(ledger, "attempt-0001")
    assert entry is not None
    append_entry(
        ledger,
        record_type=ATTEMPT_STARTED_RECORD_TYPE,
        payload={**entry.payload, "attempt_id": "attempt-0002", "extra": "field"},
        recorded_at_utc=_MOMENT,
    )

    with pytest.raises(AttemptError, match="unrecognized field"):
        _counts(ledger)


def test_another_familys_bad_record_also_stops_the_count(tmp_path: Path) -> None:
    """Validation precedes the family filter, so no family hides another's damage."""
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001", family="family-one")
    append_entry(
        ledger,
        record_type=ATTEMPT_STARTED_RECORD_TYPE,
        payload={"attempt_id": "attempt-0002", "family": "family-two"},
        recorded_at_utc=_MOMENT,
    )

    with pytest.raises(AttemptError):
        _counts(ledger, family="family-one")


def test_lockbox_attempts_are_counted_separately(tmp_path: Path) -> None:
    """Section 9 excludes exploration and is silent on lockbox; neither is merged."""
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001", partition=PARTITION_CONFIRMATION)
    _start(ledger, "lockbox-0001", partition=PARTITION_LOCKBOX)
    _start(ledger, "explore-0001", partition=PARTITION_EXPLORATION)

    counts = _counts(ledger)
    assert counts.cycle_attempts == 1
    assert counts.lifetime_attempts == 1
    assert counts.lockbox_attempts == 1
    assert counts.excluded_exploration_attempts == 1


def test_padded_identifiers_are_refused(tmp_path: Path) -> None:
    """F-4: drift is refused rather than silently splitting a lifetime count."""
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001", family="family-one")

    with pytest.raises(AttemptError, match="whitespace"):
        _start(ledger, "attempt-0002", family="family-one ")

    assert _counts(ledger, family="family-one").lifetime_attempts == 1


def test_excluded_exploration_is_cycle_scoped(tmp_path: Path) -> None:
    """F-9: the docstring now states this scope; the test pins it."""
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "explore-0001", partition=PARTITION_EXPLORATION, cycle="C0")

    assert _counts(ledger, cycle="C1").excluded_exploration_attempts == 0
    assert _counts(ledger, cycle="C0").excluded_exploration_attempts == 1


def test_damaged_ledger_refuses_rather_than_reading_as_zero(tmp_path: Path) -> None:
    """An unreadable ledger must never count as no attempts."""
    ledger = tmp_path / "ledger.jsonl"
    _start(ledger, "attempt-0001")
    ledger.write_bytes(ledger.read_bytes()[:-10])

    with pytest.raises(LedgerError):
        _start(ledger, "attempt-0002")
    with pytest.raises(LedgerError):
        read_entries(ledger)
