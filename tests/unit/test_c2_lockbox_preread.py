"""R-14a lockbox module, slice 2: pre-read checks (DESIGN §6.3; Annex D
§D-1.8 item 2, §D-3.5, §D-2.2 P-4; tests §D-3.8 A1a, A1b, A7, A5).
Synthetic data only."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import replace
from typing import Any

import pytest

from aqt.core.preregistration import trial_seed
from calibration import c2_lockbox as lb
from calibration import screen
from calibration.seeds import cj, sha


def _h(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


SIGNAL_SRC = b"def s(row, params, state):\n    return 1.0\n"
OVERLAY_SRC = b"def o(target, market, state):\n    return target\n"
TRIAL: dict[str, Any] = {
    "trial_id": "t007",
    "family": "trend",
    "signal": "trial_signal:s",
    "signal_sha256": hashlib.sha256(SIGNAL_SRC).hexdigest(),
    "overlay": None,
    "overlay_sha256": None,
    "s_inputs": ["ema_dist_72", "rv_168"],
    "tau": "0.60",
    "sigma": "EWMA_168h",
    "g11_class": "signal_timed",
    "model": None,
    "horizon_hours": 72,
    "parameter_point": {"span": 72},
    "grid": {"span": [24, 72, 168]},
    "warmup_hours": 4800,
}
SIGNED = lb.Signed(
    protocol_hash=_h("protocol"),
    lockbox_module_sha256=_h("lockbox-module"),
    confirmation_module_sha256=_h("confirmation-module"),
    engine_commit="eeaa7282e3b7c87790c162d679016c290d5f4ea5",
    screen_object_sha256=_h("screen"),
    image_digest="sha256:" + _h("image"),
)
HYPOTHESIS = _h("hypothesis")
FAMILY_SEED = _h("family-seed")
MANIFEST = _h("manifest")
TRIAL_INDEX = 3
DECLARATION: dict[str, Any] = {
    "cycle_id": "C2",
    "trials": [
        {"family": "trend", "trial_id": "t007", "hypothesis_hash": HYPOTHESIS,
         "configuration_hash": screen.trial_sha256(TRIAL), "trial_index": TRIAL_INDEX},
        {"family": "trend", "trial_id": "t008", "hypothesis_hash": HYPOTHESIS,
         "configuration_hash": "c" * 64, "trial_index": 4},
    ],
}  # fmt: skip
FORECAST = lb.forecast(lb.reference_d()[:40], _h("x"), lb.REFERENCE_WINDOW)


def _artifact() -> dict[str, Any]:
    seed_l266 = trial_seed(
        protocol_hash=SIGNED.protocol_hash,
        hypothesis_hash=HYPOTHESIS,
        trial_index=TRIAL_INDEX,
    )
    return {
        "cycle_id": "C2",
        "family": "trend",
        "nominee": {
            "trial_id": "t007",
            "configuration_hash": screen.trial_sha256(TRIAL),
            "hypothesis_hash": HYPOTHESIS,
            "protocol_hash": SIGNED.protocol_hash,
            "trial_index": TRIAL_INDEX,
            "seed_l266": seed_l266,
            "estimator_seed_policy": "L266_MOD_2_31",
            "estimator_seed": screen.estimator_seed(seed_l266),
        },
        "source": {
            "window_id": lb.REFERENCE_WINDOW,
            "n": 40,
            "d_sha256": _h("d"),
            "evaluation_record_sha256": _h("record"),
        },
        "block": {
            "psi_sha256": _h("psi"),
            "value": lb.hexf(FORECAST.block.value or 1.0),
            "raw": None,
            "clipping": None,
        },
        "stream": {
            "seed_hex": sha({"family_seed": FAMILY_SEED, "trial_id": "t007"}),
            "seed_source": "R13_TRIAL_SEED",
            "purpose": "lockbox_prediction",
            "asset": "BTCUSDT",
            "cost": "1.0",
            "m": 457,
            "attempts": 2000,
        },
        "replicates_sorted": [lb.hexf(x) for x in sorted(FORECAST.replicates)],
        "q": lb.hexf(FORECAST.q),
        "code": {
            "lockbox_module_sha256": SIGNED.lockbox_module_sha256,
            "confirmation_module_sha256": SIGNED.confirmation_module_sha256,
            "engine_commit": SIGNED.engine_commit,
            "screen_object_sha256": SIGNED.screen_object_sha256,
        },
    }


def _case(
    artifact: dict[str, Any] | None = None,
    trial: dict[str, Any] | None = None,
    extra: dict[str, bytes] | None = None,
) -> dict[str, Any]:
    a = _artifact() if artifact is None else artifact
    t = TRIAL if trial is None else trial
    trial_bytes = cj(t)
    files = {hashlib.sha256(b).hexdigest(): b for b in (trial_bytes, SIGNAL_SRC)}
    items = [
        {"kind": "trial", "sha256": hashlib.sha256(trial_bytes).hexdigest(),
         "size": len(trial_bytes)},
        {"kind": "signal", "sha256": hashlib.sha256(SIGNAL_SRC).hexdigest(),
         "size": len(SIGNAL_SRC)},
    ]  # fmt: skip
    for kind, b in (extra or {}).items():
        files[hashlib.sha256(b).hexdigest()] = b
        items.append(
            {"kind": kind, "sha256": hashlib.sha256(b).hexdigest(), "size": len(b)}
        )
    raw = cj(a)
    return {
        "request": lb.Request(
            cycle_id="C2",
            family="trend",
            nominee_trial_id="t007",
            hypothesis_hash=HYPOTHESIS,
            configuration_hash=screen.trial_sha256(TRIAL),
            prediction_artifact_sha256=hashlib.sha256(raw).hexdigest(),
            family_seed=FAMILY_SEED,
            seed_l266=trial_seed(
                protocol_hash=SIGNED.protocol_hash,
                hypothesis_hash=HYPOTHESIS,
                trial_index=TRIAL_INDEX,
            ),
            manifest_sha256=MANIFEST,
            trial_index=TRIAL_INDEX,
        ),
        "signed": SIGNED,
        "declaration": cj(DECLARATION),
        "declaration_sha256": hashlib.sha256(cj(DECLARATION)).hexdigest(),
        "artifact_bytes": raw,
        "artifacts_ledger": {"items": items},
        "files": files,
        "manifest_sha256": MANIFEST,
        "image_digest": SIGNED.image_digest,
        "startup": {
            "result": "PASS",
            "lockbox_module_sha256": SIGNED.lockbox_module_sha256,
            "image_digest": SIGNED.image_digest,
        },
    }


def _check(case: dict[str, Any]) -> str:
    return lb.pre_read_check(**case)


def _mutated(path: str, value: object) -> dict[str, Any]:
    a = _artifact()
    *outer, last = path.split(".")
    target = a
    for k in outer:
        target = target[k]
    target[last] = value
    return _case(a)


def test_valid_passes() -> None:
    assert _check(_case()) == "PASS"


def test_artifact_missing() -> None:
    c = _case()
    assert _check({**c, "artifact_bytes": None}) == "ARTIFACT_NOT_FOUND"
    files = dict(c["files"])
    files.pop(c["artifacts_ledger"]["items"][1]["sha256"])
    assert _check({**c, "files": files}) == "ARTIFACT_NOT_FOUND"


@pytest.mark.parametrize("index", [0, 1])
def test_a1a_flipped_byte_each_kind(index: int) -> None:
    c = _case()
    key = c["artifacts_ledger"]["items"][index]["sha256"]
    raw = bytearray(c["files"][key])
    raw[3] ^= 1
    assert _check({**c, "files": {**c["files"], key: bytes(raw)}}) == (
        "ARTIFACT_HASH_MISMATCH"
    )


def test_prediction_artifact_flipped_byte() -> None:
    c = _case()
    raw = bytearray(c["artifact_bytes"])
    raw[10] ^= 1
    assert _check({**c, "artifact_bytes": bytes(raw)}) == "ARTIFACT_HASH_MISMATCH"


def test_python_source_is_never_parsed_as_json() -> None:
    # the signal file is not JSON; only the trial object is parsed
    with pytest.raises(ValueError):
        json.loads(SIGNAL_SRC)
    assert _check(_case()) == "PASS"
    c = _case()
    c["artifacts_ledger"]["items"][0]["kind"] = "signal"  # no trial object left
    assert _check(c) == "IDENTITY_MISMATCH"


def test_trial_and_code_items() -> None:
    other = {**TRIAL, "tau": "0.40"}  # a different configuration hash
    assert _check(_case(trial=other)) == "IDENTITY_MISMATCH"
    assert _check(_case(extra={"overlay": OVERLAY_SRC})) == "IDENTITY_MISMATCH"


def test_noncanonical_artifact_bytes() -> None:
    c = _case()
    raw = json.dumps(_artifact(), indent=1, sort_keys=True).encode()
    req = replace(
        c["request"], prediction_artifact_sha256=hashlib.sha256(raw).hexdigest()
    )
    assert _check({**c, "artifact_bytes": raw, "request": req}) == (
        "PREDICTION_ARTIFACT_INVALID"
    )


def test_artifact_shape() -> None:
    a = _artifact()
    del a["block"]["raw"]
    assert _check(_case(a)) == "PREDICTION_ARTIFACT_INVALID"


@pytest.mark.parametrize(
    ("path", "value"),
    [
        ("nominee.estimator_seed_policy", "SHA256_LOW31"),  # the other policy
        ("nominee.estimator_seed", 12345),
        ("nominee.seed_l266", _h("other")),
        ("nominee.trial_index", 4),
        ("nominee.protocol_hash", _h("other")),
        ("stream.seed_hex", sha({"family_seed": _h("x"), "trial_id": "t007"})),
        ("stream.seed_source", "LINE_266"),  # A7: a differing seed_source
        ("stream.purpose", "paired_sharpe_ci"),
        ("stream.m", 456),
        ("stream.attempts", 2000.0),
        ("code.lockbox_module_sha256", _h("other")),
        ("code.screen_object_sha256", _h("other")),
        ("cycle_id", "C3"),
    ],
)
def test_identity_mismatches(path: str, value: object) -> None:
    assert _check(_mutated(path, value)) == "IDENTITY_MISMATCH"


def test_manifest_mismatch() -> None:
    assert _check({**_case(), "manifest_sha256": _h("other")}) == "IDENTITY_MISMATCH"


def test_a1b_seed_mapping_to_zero_is_accepted() -> None:
    zero = "0" * 56 + "80000000"  # int(...) = 2**31, so the estimator seed is 0
    assert screen.estimator_seed(zero) == 0
    a = _artifact()
    a["nominee"]["seed_l266"] = zero
    a["nominee"]["estimator_seed"] = 0
    c = _case(a)
    c["request"] = replace(c["request"], seed_l266=zero)
    assert _check(c) == "PASS"


@pytest.mark.parametrize("seed", ["A" * 64, "0" * 63, "", 7])
def test_malformed_request_seed_l266_refused(seed: object) -> None:
    # R14L5-S-2: the sealing record's seed is checked, never trusted
    c = _case()
    c["request"] = replace(c["request"], seed_l266=seed)
    assert _check(c) == "IDENTITY_MISMATCH"


def test_seed_l266_is_the_requests_never_re_derived() -> None:
    # R14L5-S-2 (owner decision (a)): request and artifact agree on a seed
    # that is not the preregistration derivation; the module does not derive
    seed = _h("sealed-seed")
    a = _artifact()
    a["nominee"].update(seed_l266=seed, estimator_seed=screen.estimator_seed(seed))
    c = _case(a)
    c["request"] = replace(c["request"], seed_l266=seed)
    assert _check(c) == "PASS"
    assert not hasattr(lb, "trial_seed")


def test_a1b_re_derivation_vector() -> None:
    seed = trial_seed(protocol_hash="1" * 64, hypothesis_hash="2" * 64, trial_index=0)
    assert screen.estimator_seed(seed) == int(seed, 16) % 2**31


def test_a7_seed_hex_vector() -> None:
    assert (
        sha({"family_seed": "f" * 64, "trial_id": "t1"})
        == hashlib.sha256(
            b'{"family_seed":"' + b"f" * 64 + b'","trial_id":"t1"}'
        ).hexdigest()
    )


def test_p4() -> None:
    reps = _artifact()["replicates_sorted"]
    assert _check(_mutated("replicates_sorted", reps[:-1])) == (
        "PREDICTION_ARTIFACT_INVALID"
    )
    swapped = copy.copy(reps)
    swapped[0], swapped[-1] = swapped[-1], swapped[0]
    assert _check(_mutated("replicates_sorted", swapped)) == (
        "PREDICTION_ARTIFACT_INVALID"
    )
    inf = [lb.hexf(float("inf")) if i == 1999 else x for i, x in enumerate(reps)]
    assert _check(_mutated("replicates_sorted", inf)) == "PREDICTION_ARTIFACT_INVALID"
    off = lb.hexf(lb.unhexf(_artifact()["q"]) * (1 + 2**-52))
    assert _check(_mutated("q", off)) == "PREDICTION_ARTIFACT_INVALID"
    assert _check(_mutated("q", "not-hex")) == "PREDICTION_ARTIFACT_INVALID"


def test_image_and_startup() -> None:
    c = _case()
    assert _check({**c, "image_digest": "sha256:" + _h("other")}) == "IMAGE_MISMATCH"
    assert _check({**c, "startup": None}) == "REFERENCE_VECTOR_MISMATCH"
    for change in (
        {"result": "REFERENCE_VECTOR_MISMATCH"},
        {"lockbox_module_sha256": _h("other")},
        {"image_digest": "sha256:" + _h("other")},
    ):
        startup = {**c["startup"], **change}
        assert _check({**c, "startup": startup}) == "REFERENCE_VECTOR_MISMATCH"


def test_coherent_wrong_trial_index_refused() -> None:
    # R14L-S-1: index 4 with both seeds recomputed for it and the artifact
    # hash recomputed: self-consistent, but not the trial record's index 3
    a = _artifact()
    seed = trial_seed(
        protocol_hash=SIGNED.protocol_hash, hypothesis_hash=HYPOTHESIS, trial_index=4
    )
    a["nominee"].update(
        trial_index=4, seed_l266=seed, estimator_seed=screen.estimator_seed(seed)
    )
    assert _check(_case(a)) == "IDENTITY_MISMATCH"


@pytest.mark.parametrize(
    ("field", "value"),
    [("sha256", []), ("sha256", "A" * 64), ("size", True), ("size", "12"),
     ("kind", ["trial"])],
)  # fmt: skip
def test_malformed_ledger_item_is_a_reason_code(field: str, value: object) -> None:
    # R14L-S-5: a recorded Q2b code, never an uncaught TypeError
    c = _case()
    c["artifacts_ledger"]["items"][1][field] = value
    assert _check(c) == "IDENTITY_MISMATCH"


def test_request_and_artifact_coherently_wrong_index_refused() -> None:
    # R14L2-S-1, Sol's scenario: request and artifact both say 4 with the
    # seeds and hash recomputed; the posted declaration says 3
    a = _artifact()
    seed = trial_seed(
        protocol_hash=SIGNED.protocol_hash, hypothesis_hash=HYPOTHESIS, trial_index=4
    )
    a["nominee"].update(
        trial_index=4, seed_l266=seed, estimator_seed=screen.estimator_seed(seed)
    )
    c = _case(a)
    c["request"] = replace(c["request"], trial_index=4, seed_l266=seed)
    assert _check(c) == "IDENTITY_MISMATCH"


@pytest.mark.parametrize(
    "change",
    [
        lambda d: d.update(cycle_id="C3"),
        lambda d: d["trials"].pop(0),  # no entry for the nominee
        lambda d: d["trials"].append(dict(d["trials"][0])),  # two entries
        lambda d: d["trials"][0].update(trial_index=True),
        lambda d: d["trials"][0].update(family="vol"),
        lambda d: d["trials"][0].update(hypothesis_hash="0" * 64),
        lambda d: d.update(trials="t007"),
    ],
)
def test_declared_entry_binds_the_nominee(change: Any) -> None:
    # a different but correctly hashed declaration: refused on content
    declaration = copy.deepcopy(DECLARATION)
    change(declaration)
    raw = cj(declaration)
    c = {**_case(), "declaration": raw}
    c["declaration_sha256"] = hashlib.sha256(raw).hexdigest()
    assert _check(c) == "IDENTITY_MISMATCH"


def test_declaration_changed_after_start_refused() -> None:
    # R14L3-S-1, Sol's probe: the verified hash is kept, the bytes changed
    # (index 3 -> 4) and request and artifact made coherent with index 4
    declaration = copy.deepcopy(DECLARATION)
    declaration["trials"][0]["trial_index"] = 4
    a = _artifact()
    seed = trial_seed(
        protocol_hash=SIGNED.protocol_hash, hypothesis_hash=HYPOTHESIS, trial_index=4
    )
    a["nominee"].update(
        trial_index=4, seed_l266=seed, estimator_seed=screen.estimator_seed(seed)
    )
    c = _case(a)
    c["request"] = replace(c["request"], trial_index=4, seed_l266=seed)
    c["declaration"] = cj(declaration)  # declaration_sha256 still the verified one
    assert _check(c) == "IDENTITY_MISMATCH"
