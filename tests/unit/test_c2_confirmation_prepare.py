"""Slice 6b build B4b: the read-free steps 2-3 of both entry points
(DESIGN_SLICE6B rev 16 §1, §2). Synthetic inputs only; the BLS, header and
capture checks have their own tests and are replaced here by recorders."""

from __future__ import annotations

import hashlib
import itertools
import sys
import tempfile
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import test_c2_confirmation_signed as sg
import test_calibration_screen as ts

from calibration import c2_confirmation as cf
from calibration import screen
from calibration.seeds import cj

P = "1" * 64
Q = "9" * 64  # the signed qualification_object_sha256
ACC = "a" * 64
SIGNAL = (
    b"def s(row, params, state):\n    return 1.0 if row['ema_dist_72'] > 0 else 0.0\n"
)
_names = itertools.count()


@pytest.fixture(autouse=True)
def _restore_sys_path() -> Iterator[None]:
    saved = list(sys.path)
    yield
    sys.path[:] = saved


def _module() -> str:
    return f"c2prep_sig_{next(_names)}"  # a fresh name: never in sys.modules


class World:
    """A declaration of a trend and a vol trial with their code, screen
    record and signed rows."""

    def __init__(self) -> None:
        digest = hashlib.sha256(SIGNAL).hexdigest()
        self.code: dict[str, bytes] = {digest: SIGNAL}
        self.objs: dict[str, dict[str, Any]] = {
            tid: ts._trial(
                trial_id=tid, family=fam, signal=f"{_module()}:s", signal_sha256=digest
            )  # fmt: skip
            for tid, fam in (("tr1", "trend"), ("vo1", "vol"))
        }
        self.rows: dict[str, str | None] = {}
        self.seal()

    def seal(self, object_sha256: str = Q) -> None:
        """Declaration and screen record for the current trial objects."""
        trials = list(self.objs.values())
        self.screen_record = cj({
            "trial_set_sha256": screen.trial_set_sha256(trials),
            "qualification_object_sha256": object_sha256, "outcome": "SCREEN_AVAILABLE",
        })  # fmt: skip
        self.decl: dict[str, Any] = {
            "protocol_hash": P,
            "cycle_id": "C2-0001",
            "trials": [
                {
                    "family": o["family"],
                    "trial_id": i,
                    "hypothesis_hash": "ab" * 32,
                    "configuration_hash": screen.trial_sha256(o),
                    "trial_index": n,
                }
                for n, (i, o) in enumerate(self.objs.items())
            ],  # fmt: skip
            "data_manifest_sha256": "2" * 64,
            "last_seen": "2021-12-01T00:00:00Z",
            "embargo_days": 30,
            "ledger_anchor": {"head_hash": "3" * 64, "entry_count": 0},
            "screen_record_sha256": hashlib.sha256(self.screen_record).hexdigest(),
        }

    def started(self) -> cf.Started:
        protocol = (
            sg.protocol(**self.rows)
            + f'\n  qualification_object_sha256: "{Q}"'.encode()
        )
        return cf.Started(
            protocol_hash=P, lockbox_module_sha256="4" * 64,
            confirmation_module_sha256="5" * 64, engine_commit="6" * 40,
            screen_object_sha256="7" * 64, image_digest="sha256:" + "8" * 64,
            protocol=protocol, declaration=cj(self.decl), declaration_sha256="0" * 64,
            chain_log={"acceptance_record_sha256": ACC},
        )  # fmt: skip

    def sources(self, **change: Any) -> dict[str, Any]:
        s = {
            "ledger_path": Path("unused.jsonl"), "acceptance_record": b"acc",
            "headers": [b"h"] * 6, "beacon": cf.Beacon(1, "r", "s"),
            "capture_record": b"cap", "object_dir": Path("unused"),
            "screen_record": self.screen_record, "trial_objects": self.objs,
            "code_files": self.code,
        }  # fmt: skip
        s.update(change)
        return s


DAY0 = datetime(2022, 2, 1, tzinfo=UTC)
HEADERS = cf.Headers(height=800000, cycle_start=DAY0, tip_block_hash="b" * 64,
                     tip_time=DAY0, headers_sha256="c" * 64)  # fmt: skip
CAPTURE = cf.Capture(timestamp="20220201020000", record_sha256="d" * 64,
                     before_tip_window=False)  # fmt: skip


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    seen: dict[str, Any] = {}

    def headers_check(record: bytes, sha: str, headers: Any) -> cf.Headers:
        seen["headers"] = (record, sha, headers)
        return HEADERS

    def capture(record: bytes, headers: cf.Headers, sha: str) -> cf.Capture:
        seen["capture"] = (record, headers, sha)
        return CAPTURE

    def derive_seeds(**kw: Any) -> dict[str, Any]:
        seen["seeds"] = kw
        return {"families": {}}

    def qualification_checks(*a: Any) -> Any:
        seen["qualification"] = a
        return {}, {}

    monkeypatch.setattr(cf, "headers_check", headers_check)
    monkeypatch.setattr(cf, "check_capture_record", capture)
    monkeypatch.setattr(cf, "derive_seeds", derive_seeds)
    monkeypatch.setattr(cf, "qualification_checks", qualification_checks)
    return seen


def test_prepare_wires_every_step(calls: dict[str, Any]) -> None:
    w = World()
    got = cf.prepare(w.started(), w.sources())
    assert calls["headers"] == (b"acc", ACC, [b"h"] * 6)
    assert calls["capture"] == (b"cap", HEADERS, ACC)
    w0 = datetime(2022, 1, 31, tzinfo=UTC)  # signed confirmation_start (g = 30)
    t_days = (cf.V1_CONFIRMATION_END - w0).days + 1
    assert (got.w0, got.t_days) == (w0, t_days)
    seeds = calls["seeds"]
    assert seeds["chain"] == cf.signed_c2(w.started().protocol).chain
    assert seeds["capture_cdx"] == CAPTURE.timestamp
    assert seeds["window_id"] == cf.window_id(w0, w0 + t_days * cf.DAY) == got.window_id
    assert (seeds["protocol_hash"], seeds["cycle_id"]) == (P, "C2-0001")
    assert seeds["data_manifest_hash"] == "2" * 64
    assert seeds["records"] == {
        "trend": [{k: w.decl["trials"][0][k] for k in cf._RECORD_FIELDS}],
        "vol": [{k: w.decl["trials"][1][k] for k in cf._RECORD_FIELDS}],
    }
    assert got.trial_of == {("ab" * 32, 0): "tr1", ("ab" * 32, 1): "vo1"}
    names = sorted(p.name for p in got.code_dir.iterdir())
    assert names == sorted(f"{o['signal'].split(':')[0]}.py" for o in w.objs.values())
    assert sys.path[-1] == str(got.code_dir.resolve())  # trial code last


def test_the_sources_must_be_exactly_the_handles(calls: dict[str, Any]) -> None:
    w = World()
    for bad in ({k: v for k, v in w.sources().items() if k != "object_dir"},
                {**w.sources(), "extra": 1}):  # fmt: skip
        with pytest.raises(cf.CycleError, match="exactly the §1 handles"):
            cf.prepare(w.started(), bad)
    assert calls == {}


def _refused(w: World, calls: dict[str, Any], match: str, **src: Any) -> None:
    with pytest.raises(cf.CycleError, match=match):
        cf.prepare(w.started(), w.sources(**src))
    assert "seeds" not in calls and "capture" not in calls  # refused read-free, early


def test_missing_altered_or_extra_code_is_refused_before_the_seeds(
    calls: dict[str, Any],
) -> None:
    w = World()
    digest = next(iter(w.code))
    _refused(w, calls, "not exactly the declared", code_files={})
    _refused(w, calls, "not exactly the declared",
             code_files={**w.code, "f" * 64: b"x"})  # fmt: skip
    _refused(w, calls, "does not hash", code_files={digest: SIGNAL + b"\n"})


def test_code_that_does_not_load_is_refused(calls: dict[str, Any]) -> None:
    for source in (b"def s(row, params, state)\n", b"s = 1\n", b"import os\ns = os\n"):
        w = World()
        digest = hashlib.sha256(source).hexdigest()
        for o in w.objs.values():
            o["signal_sha256"] = digest
        w.seal()
        _refused(w, calls, "does not load", code_files={digest: source})


def test_one_module_name_with_two_sources_is_refused(calls: dict[str, Any]) -> None:
    w = World()
    other = SIGNAL.replace(b"1.0 if", b"0.5 if")
    vo = w.objs["vo1"]
    vo["signal"] = w.objs["tr1"]["signal"]
    vo["signal_sha256"] = hashlib.sha256(other).hexdigest()
    w.seal()
    _refused(w, calls, "two different sources",
             code_files={**w.code, vo["signal_sha256"]: other})  # fmt: skip


def test_the_screen_record_is_checked_against_the_signed_object(
    calls: dict[str, Any],
) -> None:
    w = World()
    w.seal(object_sha256="e" * 64)
    _refused(w, calls, "another qualification object")


def test_the_window_comes_from_the_signed_rows(calls: dict[str, Any]) -> None:
    w = World()
    w.rows = {"g_days": "31", "confirmation_start": "2022-02-01T00:00:00Z"}
    _refused(w, calls, "recorded embargo 30 != bound g 31")
    w = World()
    w.rows = {"t_min": "5000"}
    _refused(w, calls, "T_min = 5000")


def test_a_malformed_signed_row_is_refused(calls: dict[str, Any]) -> None:
    w = World()
    w.rows = {"z_crit": "nan"}
    _refused(w, calls, "z_crit row")


OVERLAY = b"def o(row, params, state, target):\n    return target\n"


def test_an_overlay_is_installed_and_required(calls: dict[str, Any]) -> None:
    w = World()
    digest = hashlib.sha256(OVERLAY).hexdigest()
    w.objs["tr1"].update(overlay=f"{_module()}:o", overlay_sha256=digest)
    w.seal()
    _refused(w, calls, "not exactly the declared")  # overlay code missing
    got = cf.prepare(w.started(), w.sources(code_files={**w.code, digest: OVERLAY}))
    name = w.objs["tr1"]["overlay"].split(":")[0] + ".py"
    assert (got.code_dir / name).read_bytes() == OVERLAY


def test_trial_code_cannot_shadow_an_engine_module(calls: dict[str, Any]) -> None:
    """The code directory is last: `numpy` resolves to the installed package,
    whose source is not the declared one."""
    w = World()
    for o in w.objs.values():
        o["signal"] = "numpy:s"
    w.seal()
    _refused(w, calls, "does not load: TrialError: numpy is not the declared source")


def test_refused_code_bytes_are_never_written(
    calls: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    w = World()
    digest = next(iter(w.code))
    target = tmp_path / "code"
    target.mkdir()
    monkeypatch.setattr(tempfile, "mkdtemp", lambda prefix: str(target))
    _refused(w, calls, "does not hash", code_files={digest: SIGNAL + b"\n"})
    assert list(target.iterdir()) == []


def test_a_failed_header_check_stops_before_every_later_step(
    calls: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    def refuse(*a: Any) -> None:
        raise cf.CycleError("headers refused")

    made: list[str] = []
    monkeypatch.setattr(cf, "headers_check", refuse)
    monkeypatch.setattr(cf, "signed_c2", lambda p: made.append("signed"))
    monkeypatch.setattr(cf, "install_code", lambda *a: made.append("code"))
    w = World()
    with pytest.raises(cf.CycleError, match="headers refused"):
        cf.prepare(w.started(), w.sources())
    assert made == [] and calls == {}


def test_evaluate_trial_with_a_refused_prepare_never_reads(
    calls: dict[str, Any], tmp_path: Path
) -> None:
    """The real `prepare` in front of `evaluate_trial`: wrong code refuses
    before the ledger is even opened and before any protected-data read."""
    w = World()
    digest = next(iter(w.code))

    def read() -> None:
        raise AssertionError("protected data was read")

    src = w.sources(code_files={digest: SIGNAL + b"\n"}, ledger_path=tmp_path / "l")
    with pytest.raises(cf.CycleError, match="does not hash"):
        cf.evaluate_trial(w.started(), src, "tr1", "attempt-a0", read)
    assert not (tmp_path / "l").exists()


def test_the_qualification_checks_run_in_prepare_before_the_code_and_seeds(
    calls: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """R14B6F-F-2: a signed z_crit that is not the object's refuses both entry
    points before any read, not only the look."""
    w = World()
    cf.prepare(w.started(), w.sources())
    obj, protocol, signed, t_days, declared = calls["qualification"]
    assert obj == Path("unused") and protocol == w.started().protocol
    assert signed == cf.signed_c2(protocol) and set(declared) == {"trend", "vol"}

    def refuse(*a: Any) -> None:
        raise cf.CycleError("the signed z_crit is not the qualification object's")

    monkeypatch.setattr(cf, "qualification_checks", refuse)
    monkeypatch.setattr(cf, "install_code", lambda *a: pytest.fail("code installed"))
    calls.clear()

    def read() -> None:
        raise AssertionError("protected data was read")

    src = w.sources(ledger_path=tmp_path / "l")
    with pytest.raises(cf.CycleError, match="z_crit"):
        cf.evaluate_trial(w.started(), src, "tr1", "attempt-a0", read)
    assert "seeds" not in calls and not (tmp_path / "l").exists()


@pytest.mark.parametrize(
    "change",
    [{"engine_commit": "6" * 7}, {"engine_commit": "G" * 40}, {"image_digest": ""},
     {"confirmation_module_sha256": "5" * 63}],
)  # fmt: skip
def test_non_canonical_identity_fields_refuse_before_any_read(
    calls: dict[str, Any], change: dict[str, str]
) -> None:
    """R14B6F-F-3: what the result entry would refuse after the read is
    refused in prepare."""
    import dataclasses

    w = World()
    started = dataclasses.replace(w.started(), **change)
    with pytest.raises(cf.CycleError, match="identity fields are not canonical"):
        cf.prepare(started, w.sources())
    assert "seeds" not in calls
