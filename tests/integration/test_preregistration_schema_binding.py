"""Preregistration records against the unmodified frozen Draft 2020-12 schemas.

The schemas are read byte-for-byte from `schemas/` and validated as schemas
before anything is checked against them, so a record can never pass because a
schema was relaxed. Every hypothesis here is synthetic, the ledger is a pytest
temporary file, and nothing binds a real cycle or starts a trial.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from aqt.core.ledger import read_entries, verify_ledger
from aqt.core.paths import REPOSITORY_ROOT
from aqt.core.preregistration import (
    enumerate_trials,
    experiment_record,
    family_trial_counts,
    hypothesis_trial_indices,
    preregister_hypothesis,
    record_hypothesis,
    record_trial,
    trial_seed,
    verify_hypothesis_content_hash,
)

_MOMENT = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
_FAMILY = "trend"
_GRID: dict[str, list[object]] = {
    "lookback_hours": [168, 336],
    "vol_target": ["0.40", "0.60", "0.80"],
}
_HORIZONS: list[object] = [24, 72, 168]


def _frozen_protocol_hash() -> str:
    frozen = json.loads((REPOSITORY_ROOT / "FROZEN_HASHES.json").read_text("utf-8"))
    protocol_hash: str = frozen["protocol_file_sha256"]
    return protocol_hash


def _validator(name: str) -> Draft202012Validator:
    schema = json.loads((REPOSITORY_ROOT / "schemas" / name).read_text("utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _hypothesis_content() -> dict[str, object]:
    return {
        "hypothesis_id": "H-SYNTHETIC-TASK10",
        "family": _FAMILY,
        "created_by": "ai",
        "target_definition": "log(P[t+H]/P[t]) / (sigma_hourly_t * sqrt(H_hours))",
        "horizon": _HORIZONS,
        "bar_frequency": "1h",
        "decision_frequency": "1d",
        "feature_set_hash": "c8a0ea027de04889ff90ca6a89ad1096a335ee9c368fea8"
        "cb138b85dbbe30348",
        "exposure_mapping": {"rebalance_band_absolute": "0.10"},
        "rebalance_rule": "band 0.10\r\nminimum hold 24h",
        "cost_model_hash": "3f5e62ab2df26f360f3ca13d2db379e95a1e52b25dc3d2c"
        "8f2683878b49327ae",
        "training_window": {"months": 24},
        "retrain_policy_hash": "7" * 64,
        "parameter_grid": _GRID,
        "protocol_hash": _frozen_protocol_hash(),
        "parent_id": None,
    }


@pytest.fixture
def registry(tmp_path: Path) -> Path:
    return tmp_path / "registry.jsonl"


def test_preregistered_hypothesis_validates_against_the_frozen_schema() -> None:
    record = preregister_hypothesis(_hypothesis_content())
    _validator("hypothesis.schema.json").validate(record)
    assert record["rebalance_rule"] == "band 0.10\nminimum hold 24h"
    assert verify_hypothesis_content_hash(record) == record["content_hash"]


def test_full_preregistration_round_trip_through_the_ledger(registry: Path) -> None:
    hypothesis_validator = _validator("hypothesis.schema.json")
    experiment_validator = _validator("experiment.schema.json")

    content = preregister_hypothesis(_hypothesis_content())
    hypothesis_hash = str(content["content_hash"])
    protocol_hash = str(content["protocol_hash"])
    record_hypothesis(registry, content, recorded_at_utc=_MOMENT)

    points = enumerate_trials(parameter_grid=_GRID, horizons=_HORIZONS)
    assert len(points) == 2 * 3 * 3
    for point in points:
        record = experiment_record(
            experiment_id=f"E-SYNTHETIC-TASK10-{point.trial_index:03d}",
            hypothesis_hash=hypothesis_hash,
            protocol_hash=protocol_hash,
            trial_index=point.trial_index,
            backtester_hash="1" * 64,
            data_manifest_hash="2" * 64,
        )
        experiment_validator.validate(record)
        assert record["seed"] == trial_seed(
            protocol_hash=protocol_hash,
            hypothesis_hash=hypothesis_hash,
            trial_index=point.trial_index,
        )
        record_trial(
            registry, family=_FAMILY, experiment=record, recorded_at_utc=_MOMENT
        )

    report = verify_ledger(registry)
    assert (report.intact, report.entry_count) == (True, 1 + len(points))

    entries = read_entries(registry)
    stored_hypothesis = entries[0].payload
    hypothesis_validator.validate(stored_hypothesis)
    assert verify_hypothesis_content_hash(stored_hypothesis) == hypothesis_hash

    seeds = set()
    for entry in entries[1:]:
        experiment = entry.payload["experiment"]
        experiment_validator.validate(experiment)
        seeds.add(experiment["seed"])
    assert len(seeds) == len(points)

    assert hypothesis_trial_indices(entries, hypothesis_hash) == tuple(
        range(len(points))
    )
    counts = family_trial_counts(entries)
    assert [(item.family, item.recorded_trials) for item in counts] == [
        (_FAMILY, len(points))
    ]
    assert counts[0].distinct_trial_points == len(points)
