"""Preregistration identity tests. Synthetic hypotheses only, no real data."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from aqt.core.ledger import LedgerError, read_entries, verify_ledger
from aqt.core.preregistration import (
    HYPOTHESIS_RECORD_TYPE,
    SEED_DOMAIN,
    TRIAL_RECORD_TYPE,
    FamilyTrialCounts,
    PreregistrationError,
    TrialPoint,
    canonical_content_bytes,
    enumerate_trials,
    experiment_record,
    family_trial_counts,
    hypothesis_content_hash,
    hypothesis_trial_indices,
    normalize_content,
    preregister_hypothesis,
    record_hypothesis,
    record_trial,
    recorded_hypotheses,
    seed_material,
    trial_seed,
    verify_hypothesis_content_hash,
)

_PROTOCOL_HASH = "a" * 64
_OTHER_PROTOCOL_HASH = "b" * 64
_HYPOTHESIS_HASH = "c" * 64
_MOMENT = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)

_GRID: dict[str, list[object]] = {
    "vol_target": ["0.40", "0.60", "0.80"],
    "lookback_hours": [168, 336, 720],
}
_HORIZONS: list[object] = [24, 72, 168]


def _content(**overrides: Any) -> dict[str, Any]:
    """A synthetic hypothesis carrying every field the frozen schema requires."""
    content: dict[str, Any] = {
        "hypothesis_id": "H-SYNTHETIC-001",
        "family": "trend",
        "created_by": "ai",
        "target_definition": "log(P[t+H]/P[t]) / (sigma_hourly_t * sqrt(H_hours))",
        "horizon": _HORIZONS,
        "bar_frequency": "1h",
        "decision_frequency": "1d",
        "feature_set_hash": "d" * 64,
        "exposure_mapping": {"rebalance_band_absolute": "0.10"},
        "rebalance_rule": "band 0.10, minimum hold 24h",
        "cost_model_hash": "e" * 64,
        "training_window": {"months": 24},
        "retrain_policy_hash": "f" * 64,
        "parameter_grid": _GRID,
        "protocol_hash": _PROTOCOL_HASH,
        "parent_id": None,
        "notes": "line one\nline two",
    }
    content.update(overrides)
    return content


# ---------------------------------------------------------------------------
# Canonical content identity
# ---------------------------------------------------------------------------


def test_content_hash_is_stable_across_key_order(tmp_path: Path) -> None:
    forward = _content()
    reversed_order = dict(reversed(list(forward.items())))
    assert list(reversed_order) != list(forward)
    assert hypothesis_content_hash(reversed_order) == hypothesis_content_hash(forward)


def test_content_hash_is_stable_across_text_line_endings() -> None:
    lf = _content()
    crlf = _content(
        notes="line one\r\nline two",
        rebalance_rule="band 0.10,\rminimum hold 24h",
    )
    lf_with_cr_free = _content(rebalance_rule="band 0.10,\nminimum hold 24h")

    assert hypothesis_content_hash(crlf) == hypothesis_content_hash(lf_with_cr_free)
    assert hypothesis_content_hash(crlf) != hypothesis_content_hash(lf)
    assert b"\r" not in canonical_content_bytes(crlf)


def test_normalization_rejects_keys_that_collide_once_normalized() -> None:
    with pytest.raises(PreregistrationError, match="collide"):
        normalize_content({"a\r\nb": 1, "a\nb": 2})


def test_content_hash_removes_only_the_self_referential_field() -> None:
    content = _content()
    digest = hypothesis_content_hash(content)
    assert hypothesis_content_hash({**content, "content_hash": digest}) == digest
    assert hypothesis_content_hash({**content, "content_hash": "0" * 64}) == digest

    expected = hashlib.sha256(
        json.dumps(
            {key: content[key] for key in sorted(content)},
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    assert digest == expected


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("hypothesis_id", "H-SYNTHETIC-002"),
        ("family", "volatility"),
        ("created_by", "human"),
        ("horizon", [24, 72]),
        ("feature_set_hash", "9" * 64),
        ("parameter_grid", {"vol_target": ["0.40"]}),
        ("parent_id", "H-SYNTHETIC-000"),
        ("notes", "line one\nline three"),
    ],
)
def test_any_hashed_content_change_changes_identity(field: str, value: Any) -> None:
    assert hypothesis_content_hash(_content(**{field: value})) != (
        hypothesis_content_hash(_content())
    )


def test_preregistration_fills_and_checks_the_self_hash() -> None:
    record = preregister_hypothesis(_content())
    assert record["content_hash"] == hypothesis_content_hash(_content())
    assert verify_hypothesis_content_hash(record) == record["content_hash"]

    assert preregister_hypothesis(_content(content_hash="")) == record
    assert preregister_hypothesis({**_content(), **record}) == record


def test_an_incorrect_supplied_self_hash_is_rejected() -> None:
    with pytest.raises(PreregistrationError, match="does not match"):
        preregister_hypothesis(_content(content_hash="1" * 64))

    tampered = {**preregister_hypothesis(_content()), "family": "volatility"}
    with pytest.raises(PreregistrationError, match="mismatch"):
        verify_hypothesis_content_hash(tampered)
    with pytest.raises(PreregistrationError, match="carries no content_hash"):
        verify_hypothesis_content_hash(_content())


def test_preregistration_requires_the_frozen_schema_fields() -> None:
    incomplete = _content()
    del incomplete["retrain_policy_hash"]
    with pytest.raises(PreregistrationError, match="retrain_policy_hash"):
        preregister_hypothesis(incomplete)

    with pytest.raises(PreregistrationError, match="protocol_hash"):
        preregister_hypothesis(_content(protocol_hash="not-a-hash"))
    with pytest.raises(PreregistrationError, match="family"):
        preregister_hypothesis(_content(family=" "))


def test_floats_never_enter_a_content_hash() -> None:
    with pytest.raises(ValueError, match="float"):
        hypothesis_content_hash(_content(parameter_grid={"vol_target": [0.6]}))


# ---------------------------------------------------------------------------
# Deterministic seeds
# ---------------------------------------------------------------------------


def test_frozen_seed_test_vector() -> None:
    material = seed_material(
        protocol_hash=_PROTOCOL_HASH,
        hypothesis_hash=_HYPOTHESIS_HASH,
        trial_index=7,
    )
    assert material == (
        b'["aqt.trial_seed.v1",'
        b'"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",'
        b'"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",7]'
    )
    assert material.decode("utf-8").startswith(f'["{SEED_DOMAIN}"')
    digest = hashlib.sha256(material).hexdigest()
    assert digest == "a253b333a47d7aa201995a00ee4ee44bf0cd1ef6ea144cbef971ccea6d8cefa0"
    assert (
        trial_seed(
            protocol_hash=_PROTOCOL_HASH,
            hypothesis_hash=_HYPOTHESIS_HASH,
            trial_index=7,
        )
        == digest
    )


def test_each_seed_input_moves_the_seed() -> None:
    base = trial_seed(
        protocol_hash=_PROTOCOL_HASH,
        hypothesis_hash=_HYPOTHESIS_HASH,
        trial_index=0,
    )
    assert base != trial_seed(
        protocol_hash=_OTHER_PROTOCOL_HASH,
        hypothesis_hash=_HYPOTHESIS_HASH,
        trial_index=0,
    )
    assert base != trial_seed(
        protocol_hash=_PROTOCOL_HASH,
        hypothesis_hash="d" * 64,
        trial_index=0,
    )
    assert base != trial_seed(
        protocol_hash=_PROTOCOL_HASH,
        hypothesis_hash=_HYPOTHESIS_HASH,
        trial_index=1,
    )
    assert len(base) == 64 and all(char in "0123456789abcdef" for char in base)


def test_seed_inputs_are_validated() -> None:
    for kwargs, pattern in (
        ({"protocol_hash": "short"}, "protocol_hash"),
        ({"hypothesis_hash": "C" * 64}, "hypothesis_hash"),
        ({"trial_index": -1}, "nonnegative"),
        ({"trial_index": True}, "integer"),
        ({"trial_index": "0"}, "integer"),
    ):
        arguments: dict[str, Any] = {
            "protocol_hash": _PROTOCOL_HASH,
            "hypothesis_hash": _HYPOTHESIS_HASH,
            "trial_index": 0,
        }
        arguments.update(kwargs)
        with pytest.raises(PreregistrationError, match=pattern):
            seed_material(**arguments)


# ---------------------------------------------------------------------------
# Deterministic trial enumeration
# ---------------------------------------------------------------------------


def test_enumeration_is_a_fixed_sorted_product_with_horizons_last() -> None:
    points = enumerate_trials(parameter_grid=_GRID, horizons=_HORIZONS)
    assert len(points) == 3 * 3 * 3
    assert [point.trial_index for point in points] == list(range(27))
    assert points[0] == TrialPoint(
        trial_index=0,
        parameters=(("lookback_hours", 168), ("vol_target", "0.40")),
        horizon=24,
    )
    assert points[1].horizon == 72
    assert points[3].parameters == (("lookback_hours", 168), ("vol_target", "0.60"))
    assert points[9].parameters == (("lookback_hours", 336), ("vol_target", "0.40"))
    assert points[-1] == TrialPoint(
        trial_index=26,
        parameters=(("lookback_hours", 720), ("vol_target", "0.80")),
        horizon=168,
    )
    assert points[0].as_mapping() == {
        "horizon": 24,
        "parameters": {"lookback_hours": 168, "vol_target": "0.40"},
        "trial_index": 0,
    }


def test_enumeration_ignores_the_declaration_order_of_names_only() -> None:
    shuffled = {
        "lookback_hours": _GRID["lookback_hours"],
        "vol_target": _GRID["vol_target"],
    }
    assert list(shuffled) != list(_GRID)
    assert enumerate_trials(parameter_grid=shuffled, horizons=_HORIZONS) == (
        enumerate_trials(parameter_grid=_GRID, horizons=_HORIZONS)
    )

    reordered_values = {**_GRID, "vol_target": ["0.80", "0.60", "0.40"]}
    assert enumerate_trials(parameter_grid=reordered_values, horizons=_HORIZONS) != (
        enumerate_trials(parameter_grid=_GRID, horizons=_HORIZONS)
    )


def test_enumeration_without_tunable_parameters_still_covers_horizons() -> None:
    points = enumerate_trials(parameter_grid={}, horizons=_HORIZONS)
    assert [point.horizon for point in points] == _HORIZONS
    assert all(point.parameters == () for point in points)


@pytest.mark.parametrize(
    ("grid", "horizons", "pattern"),
    [
        ({"a": []}, [24], "at least one value"),
        ({"a": [1, 1]}, [24], "repeats a value"),
        ({"a": [True, True]}, [24], "repeats a value"),
        ({"a": [0.6]}, [24], "float"),
        ({"a": [[1]]}, [24], "unsupported type"),
        ({"a": ["x "]}, [24], "unpadded"),
        ({"a": "abc"}, [24], "must be a list"),
        ({" a": [1]}, [24], "unpadded"),
        ({"a\r\nb": [1]}, [24], "carriage return"),
        ({"a": [1]}, [], "at least one value"),
        ({"a": [1]}, [24, 24], "repeats a value"),
        ({"a": [1]}, [0.5], "float"),
    ],
)
def test_ambiguous_or_noncanonical_grids_are_rejected(
    grid: Any, horizons: Any, pattern: str
) -> None:
    with pytest.raises(PreregistrationError, match=pattern):
        enumerate_trials(parameter_grid=grid, horizons=horizons)


def test_enumeration_rejects_a_non_mapping_grid() -> None:
    with pytest.raises(PreregistrationError, match="must be a mapping"):
        enumerate_trials(parameter_grid=[("a", [1])], horizons=[24])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Experiment records
# ---------------------------------------------------------------------------


def _experiment(**overrides: Any) -> dict[str, object]:
    arguments: dict[str, Any] = {
        "experiment_id": "E-SYNTHETIC-001",
        "hypothesis_hash": _HYPOTHESIS_HASH,
        "protocol_hash": _PROTOCOL_HASH,
        "trial_index": 3,
        "backtester_hash": "1" * 64,
        "data_manifest_hash": "2" * 64,
    }
    arguments.update(overrides)
    return experiment_record(**arguments)


def test_experiment_record_binds_the_derived_seed() -> None:
    record = _experiment()
    assert record["seed"] == trial_seed(
        protocol_hash=_PROTOCOL_HASH,
        hypothesis_hash=_HYPOTHESIS_HASH,
        trial_index=3,
    )
    assert record["protocol_status"] == "FROZEN"
    assert record["trial_index"] == 3
    assert _experiment(trial_index=4)["seed"] != record["seed"]


def test_experiment_record_validates_its_inputs(tmp_path: Path) -> None:
    with pytest.raises(PreregistrationError, match="experiment_id"):
        _experiment(experiment_id="")
    with pytest.raises(PreregistrationError, match="nonnegative"):
        _experiment(trial_index=-1)
    with pytest.raises(PreregistrationError, match="backtester_hash"):
        _experiment(backtester_hash="")

    incomplete = _experiment()
    del incomplete["experiment_id"]
    with pytest.raises(PreregistrationError, match="experiment_id"):
        record_trial(
            tmp_path / "unused.jsonl",
            family="trend",
            experiment=incomplete,
            recorded_at_utc=_MOMENT,
        )


# ---------------------------------------------------------------------------
# Registry records and read-side accounting
# ---------------------------------------------------------------------------


def _registry(tmp_path: Path) -> Path:
    return tmp_path / "registry.jsonl"


def test_recorded_hypothesis_reproduces_its_own_hash(tmp_path: Path) -> None:
    path = _registry(tmp_path)
    entry = record_hypothesis(
        path, _content(notes="line one\r\nline two"), recorded_at_utc=_MOMENT
    )
    assert entry.record_type == HYPOTHESIS_RECORD_TYPE
    assert entry.sequence == 0

    stored = read_entries(path)[0].payload
    assert stored["notes"] == "line one\nline two"
    assert verify_hypothesis_content_hash(stored) == hypothesis_content_hash(_content())
    assert recorded_hypotheses(read_entries(path)) == (stored,)
    assert verify_ledger(path).intact


def test_recorded_trial_carries_a_schema_shaped_experiment(tmp_path: Path) -> None:
    path = _registry(tmp_path)
    record_hypothesis(path, _content(), recorded_at_utc=_MOMENT)
    entry = record_trial(
        path, family="trend", experiment=_experiment(), recorded_at_utc=_MOMENT
    )
    assert entry.record_type == TRIAL_RECORD_TYPE
    assert entry.sequence == 1
    assert entry.payload["family"] == "trend"
    assert entry.payload["experiment"] == _experiment()


def test_recording_a_trial_rechecks_the_seed_and_protocol_status(
    tmp_path: Path,
) -> None:
    path = _registry(tmp_path)
    with pytest.raises(PreregistrationError, match="not the seed derived"):
        record_trial(
            path,
            family="trend",
            experiment={**_experiment(), "seed": 1},
            recorded_at_utc=_MOMENT,
        )
    with pytest.raises(PreregistrationError, match="protocol_status"):
        record_trial(
            path,
            family="trend",
            experiment={**_experiment(), "protocol_status": "DRAFT"},
            recorded_at_utc=_MOMENT,
        )
    with pytest.raises(PreregistrationError, match="family"):
        record_trial(path, family="", experiment=_experiment(), recorded_at_utc=_MOMENT)
    assert not path.exists()


def test_read_side_counts_are_deterministic_facts(tmp_path: Path) -> None:
    path = _registry(tmp_path)
    record_hypothesis(path, _content(), recorded_at_utc=_MOMENT)
    for trial_index in (0, 1, 1):
        record_trial(
            path,
            family="trend",
            experiment=_experiment(trial_index=trial_index),
            recorded_at_utc=_MOMENT,
        )
    record_trial(
        path,
        family="volatility",
        experiment=_experiment(hypothesis_hash="d" * 64, trial_index=0),
        recorded_at_utc=_MOMENT,
    )

    entries = read_entries(path)
    counts = family_trial_counts(entries)
    assert counts == (
        FamilyTrialCounts(family="trend", recorded_trials=3, distinct_trial_points=2),
        FamilyTrialCounts(
            family="volatility", recorded_trials=1, distinct_trial_points=1
        ),
    )
    assert family_trial_counts(entries) == counts
    assert hypothesis_trial_indices(entries, _HYPOTHESIS_HASH) == (0, 1, 1)
    assert hypothesis_trial_indices(entries, "d" * 64) == (0,)
    assert hypothesis_trial_indices(entries, "e" * 64) == ()
    assert family_trial_counts(()) == ()


def test_counts_exceeding_a_protocol_budget_are_still_only_counts(
    tmp_path: Path,
) -> None:
    """Accounting reports facts; the budget stop is not this task's to make."""
    path = _registry(tmp_path)
    record_hypothesis(path, _content(), recorded_at_utc=_MOMENT)
    for trial_index in range(5):
        record_trial(
            path,
            family="trend",
            experiment=_experiment(trial_index=trial_index),
            recorded_at_utc=_MOMENT,
        )
    counts = family_trial_counts(read_entries(path))
    assert counts[0].recorded_trials == 5
    assert verify_ledger(path).entry_count == 6


def test_a_damaged_registry_refuses_further_records(tmp_path: Path) -> None:
    path = _registry(tmp_path)
    record_hypothesis(path, _content(), recorded_at_utc=_MOMENT)
    before = path.read_bytes() + b'{"sequence":1'
    path.write_bytes(before)

    with pytest.raises(LedgerError, match="will not be appended to"):
        record_trial(
            path, family="trend", experiment=_experiment(), recorded_at_utc=_MOMENT
        )
    assert path.read_bytes() == before
