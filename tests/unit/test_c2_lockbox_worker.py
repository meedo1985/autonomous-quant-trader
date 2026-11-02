"""R-14a lockbox module, slice 3b-2: the worker's store calls (DESIGN §6.1,
§6.4, §6.5; Annex D §D-3.4, §D-3.7), against a fake store. Synthetic data
only. The store's own rules (L_store, the time rule, begin_read, crash rows)
are the store build's tests, not these."""

from __future__ import annotations

import hashlib
import math
import sys
from pathlib import Path
from typing import Any

import pytest

from aqt.data.bars import BarSeries
from calibration import c2_lockbox as lb
from calibration.seeds import cj
from tests.unit import test_c2_lockbox_preread as pre

EVALUATION = lb.Evaluation("C2/trend/1", "elig-1", "lbe-1", "seal-1")


class FakeStore:
    def __init__(self, refuse: str | None = None) -> None:
        self.calls: list[tuple[str, Any]] = []
        self.refuse = refuse

    def _log(self, name: str, arg: Any) -> None:
        self.calls.append((name, arg))
        if name == self.refuse:
            raise lb.StoreRefused(name)

    def append_startup(self, record: dict[str, Any]) -> str:
        self._log("append_startup", record)
        return "C2/startup/1"

    def record_pre_read_check(self, record: dict[str, Any]) -> str:
        self._log("record_pre_read_check", record)
        return "check-1"

    def open_read(self, evaluation_id: str) -> lb.ReadSession:
        self._log("open_read", evaluation_id)
        store = self

        class Session:
            def read(self) -> tuple[BarSeries, BarSeries]:
                store._log("read", None)
                raise AssertionError("compute is stubbed in these tests")

        return Session()

    def write_bundle(self, evaluation_id: str, bundle: dict[str, Any]) -> None:
        self._log("write_bundle", bundle)

    def mark_finished(self, evaluation_id: str) -> None:
        self._log("mark_finished", evaluation_id)

    def names(self) -> list[str]:
        return [n for n, _ in self.calls]


@pytest.fixture
def stub(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """compute_twice replaced: the run itself is slice 3a's tests."""
    monkeypatch.setattr(sys, "path", list(sys.path))  # _install_trial_code
    seen: dict[str, Any] = {}

    def compute_twice(
        eid: str,
        trial: dict[str, Any],
        seed: int,
        read: Any,
        q: float,
        reps: list[float],
        capture: dict[str, str],
    ) -> Any:
        seen.update(trial=trial, seed=seed, q=q, reps=reps, capture=capture)
        legs = lb.Legs(
            tuple(0.01 * math.sin(i) + 0.003 for i in range(457)),
            tuple(0.01 * math.cos(2 * i) for i in range(457)),
            0.1,
            0.12,
        )
        return lb.evaluate(eid, legs, legs, q, reps, capture)

    monkeypatch.setattr(lb, "compute_twice", compute_twice)
    return seen


def _run(store: FakeStore, tmp_path: Path, **over: Any) -> str:
    case = pre._case()
    case["startup"] = {**case["startup"], "startup_check_id": "C2/startup/1"}
    case.update(over)
    started = lb.Started(
        case.pop("signed"), case.pop("declaration"), {}, "C2/startup/1"
    )
    return lb.run_evaluation(
        store, evaluation=EVALUATION, started=started, code_dir=tmp_path, **case
    )


def test_record_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    store = FakeStore()
    monkeypatch.setattr(lb, "FROZEN_VECTORS_SHA256", lb.vectors_sha256())
    assert lb.record_startup(store, pre.SIGNED, pre.SIGNED.image_digest) == (
        "C2/startup/1"
    )
    (name, record), = store.calls  # fmt: skip
    assert record == {
        "lockbox_module_sha256": pre.SIGNED.lockbox_module_sha256,
        "image_digest": pre.SIGNED.image_digest,
        "vectors_sha256": lb.vectors_sha256(),
        "result": "PASS",
    }


def test_pass_path_order_and_inputs(stub: dict[str, Any], tmp_path: Path) -> None:
    store = FakeStore()
    result = _run(store, tmp_path)
    assert store.names() == [
        "record_pre_read_check", "open_read", "write_bundle", "mark_finished",
    ]  # fmt: skip
    check = store.calls[0][1]
    assert check["result"] == "PASS" and check["startup_check_id"] == "C2/startup/1"
    assert check["sealing_id"] == "seal-1" and "checked_at" not in check
    bundle = store.calls[2][1]
    assert "operational" not in bundle and result == bundle["result"]
    artifact = pre._artifact()
    assert stub["seed"] == artifact["nominee"]["estimator_seed"]
    assert stub["q"] == lb.unhexf(artifact["q"])
    assert stub["trial"] == pre.TRIAL
    assert stub["capture"]["input_manifest_sha256"] == pre.MANIFEST
    assert (tmp_path / "trial_signal.py").read_bytes() == pre.SIGNAL_SRC


def test_failed_check_is_recorded_and_nothing_is_read(
    stub: dict[str, Any], tmp_path: Path
) -> None:
    store = FakeStore()
    assert _run(store, tmp_path, image_digest="sha256:" + "0" * 64) == "IMAGE_MISMATCH"
    assert store.names() == ["record_pre_read_check"]
    assert store.calls[0][1]["result"] == "IMAGE_MISMATCH"
    assert not stub  # never computed


@pytest.mark.parametrize(
    ("refuse", "calls"),
    [
        ("record_pre_read_check", ["record_pre_read_check"]),  # at or after C
        ("open_read", ["record_pre_read_check", "open_read"]),  # gate refused
        ("write_bundle", ["record_pre_read_check", "open_read", "write_bundle"]),
    ],
)
def test_store_refusal_stops_without_writing(
    stub: dict[str, Any], tmp_path: Path, refuse: str, calls: list[str]
) -> None:
    store = FakeStore(refuse)
    assert _run(store, tmp_path) == "STOPPED"
    assert store.names() == calls


def test_check_names_the_startup_record_it_used(
    stub: dict[str, Any], tmp_path: Path
) -> None:
    store = FakeStore()
    assert _run(store, tmp_path, startup=None) == "REFERENCE_VECTOR_MISMATCH"
    assert store.calls[0][1]["startup_check_id"] is None


def test_late_finish_stops(stub: dict[str, Any], tmp_path: Path) -> None:
    store = FakeStore("mark_finished")
    assert _run(store, tmp_path) == "STOPPED"  # the bundle is late output


def test_refusal_during_the_read_writes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "path", list(sys.path))
    store = FakeStore("read")  # a bar at or after D*
    assert _run(store, tmp_path) == "STOPPED"
    assert "write_bundle" not in store.names()


def test_code_dir_must_be_empty(stub: dict[str, Any], tmp_path: Path) -> None:
    (tmp_path / "planted.py").write_bytes(b"x = 1\n")
    with pytest.raises(lb.LockboxError):
        _run(FakeStore(), tmp_path)


def test_end_to_end_with_the_real_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No stub: the verified trial code is installed and loaded from the code
    directory, the bars are read twice through the session, and the bundle
    is written. The fixture's constant signal equals the benchmark (d = 0),
    so E-DIFF is ZERO_VARIANCE, reached through the whole path."""
    from tests.unit.test_c2_lockbox_run import _bars

    monkeypatch.setattr(sys, "path", list(sys.path))
    market = (_bars("BTCUSDT", 1), _bars("ETHUSDT", 2))
    reads: list[int] = []

    class Store(FakeStore):
        def open_read(self, evaluation_id: str) -> lb.ReadSession:
            self._log("open_read", evaluation_id)

            class Session:
                def read(self) -> tuple[BarSeries, BarSeries]:
                    reads.append(1)
                    return market

            return Session()

    store = Store()
    assert _run(store, tmp_path) == "FAIL"
    assert len(reads) == 2
    bundle = store.calls[2][1]
    assert bundle["reasons"] == ["BTC_EDIFF:ZERO_VARIANCE"]
    # ETH E-IMPROV is exactly 0, so L-4 is a definite false, which outranks
    # the nulls of L-1/L-2 (B4.2 precedence): PERFORMANCE, not TECHNICAL
    assert bundle["conditions"]["L1"] is None and bundle["conditions"]["L4"] is False
    assert bundle["cause_class"] == "PERFORMANCE"
    assert bundle["values"]["mdd_btc_cand"] is not None


# --- start (R14L-S-2) ----------------------------------------------------------


def _start_inputs(tmp_path: Path, **rows: str) -> dict[str, Any]:
    from tests.unit.test_c2_lockbox_chain import F_TXID, _acceptance, _post

    files = {
        "lockbox_module_sha256": b"L = 1\n",
        "confirmation_module_sha256": b"C = 1\n",
    }
    for row, data in files.items():
        path = tmp_path / lb.MODULE_PATHS[row]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    values = {
        "outpoint_F": f"{F_TXID}:1",
        **{row: hashlib.sha256(data).hexdigest() for row, data in files.items()},
        "engine_commit": "e" * 40,
        "screen_object_sha256": "5" * 64,
        "qualification_object_sha256": "9" * 64,
        "image_digest": "sha256:" + "1" * 64,
        **rows,
    }
    protocol = ("\n".join(f'  {k}: "{v}"' for k, v in values.items()) + "\n").encode()
    declaration = cj({"protocol_hash": hashlib.sha256(protocol).hexdigest()})
    post = _post(hashlib.sha256(declaration).hexdigest())
    return {
        "root": tmp_path,
        "obj": tmp_path / "obj",
        "acceptance_record": _acceptance(post),
        "post_raw_tx": post,
        "declaration": declaration,
        "protocol": protocol,
        "image_digest": "sha256:" + "1" * 64,
    }


def test_start_reads_signed_values_from_the_verified_protocol(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: dict[str, Any] = {}

    def verify_code(
        obj: Path, posted: str, root: Path, modules: dict[str, bytes]
    ) -> Any:
        seen.update(posted=posted, modules=modules)
        return {"engine_commit": "e" * 40}

    monkeypatch.setattr(lb, "verify_code", verify_code)
    store = FakeStore()
    started = lb.start(store, **_start_inputs(tmp_path))
    assert started.signed.engine_commit == "e" * 40
    assert started.signed.image_digest == "sha256:" + "1" * 64
    assert (
        started.signed.lockbox_module_sha256 == hashlib.sha256(b"L = 1\n").hexdigest()
    )
    assert seen["posted"] == "9" * 64
    assert set(seen["modules"]) == set(lb.MODULE_PATHS.values())
    assert started.startup_check_id == "C2/startup/1"
    assert store.names() == ["append_startup"]


def test_start_refuses_before_any_append(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(lb, "verify_code", lambda *a: {"engine_commit": "f" * 40})
    store = FakeStore()
    with pytest.raises(lb.ChainError):  # the object's engine is not the signed one
        lb.start(store, **_start_inputs(tmp_path))
    inputs = _start_inputs(tmp_path)
    (tmp_path / "calibration" / "c2_lockbox.py").write_bytes(b"L = 2\n")  # swapped
    with pytest.raises(lb.ChainError):
        lb.start(store, **inputs)
    assert store.names() == []


def test_start_refuses_a_running_image_that_is_not_signed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # R14L2-S-3: no PASS startup record for an unsigned image digest
    monkeypatch.setattr(lb, "verify_code", lambda *a: {"engine_commit": "e" * 40})
    store = FakeStore()
    inputs = {**_start_inputs(tmp_path), "image_digest": "sha256:" + "2" * 64}
    with pytest.raises(lb.ChainError):
        lb.start(store, **inputs)
    assert store.names() == []
