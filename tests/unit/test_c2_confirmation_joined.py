"""Fable R14B6F-F-1 and F-5: one joined test of slice 6b. The real producers
feed the real consumers: `prepare` (real `signed_c2`, `headers_check`,
`check_capture_record`, `qualification_checks`, `install_code`, `derive_seeds`
with the public quicknet round 1,000,000), `evaluate_trial` for every
declared trial (real `run_trial`, `check_read`, `trial_path`, `trial_result`)
and `evaluate_look` (real `open_look`, `nominate`, `seal_family`).

Stated stand-ins, nothing else: `nominee_gates` and `cpcv_report` (the frozen
gate code, allowed by F-1); `qobj.read` (the qualification object's own
format, tested in test_calibration_qobj.py) returns a report; G-13's
benchmark spec file is absent at this commit (B5B-D-1), so
`benchmark_spec_sha256` is patched to the signed value; `persist` records;
`Started` is built by hand (`start` has its own tests; the Store's launch
route, R14B6F-F-8); method V's runtime check is marked passed (A-V1). Bars
and headers are synthetic or public; the window is shrunk to T = 30 days by
the signed g row."""

from __future__ import annotations

import base64
import hashlib
import itertools
import json
import shutil
import sys
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import test_c2_confirmation_inputs as ti
import test_c2_confirmation_seeds as sd
import test_c2_confirmation_signed as sg
import test_calibration_screen as ts

from aqt.core import attempts
from aqt.core.ledger import GENESIS_HASH, read_entries
from aqt.data import manifest as dm
from calibration import c2_confirmation as cf
from calibration import classifier, dsr, qobj, screen
from calibration.seeds import cj
from calibration.semi import SYMBOLS

H = timedelta(hours=1)
P = "1" * 64  # protocol hash
T_DAYS = 30  # == ts.WINDOW_H / 24, the screen fixture's path length
WARMUP = 4800  # ts._trial's warm-up
EXTRA = 10  # exploration bars before the cut: served, never used
W0 = cf.V1_CONFIRMATION_END + timedelta(seconds=1) - T_DAYS * cf.DAY
G_DAYS = (W0 - cf.V1_CONFIRMATION_START).days
END = W0 + T_DAYS * cf.DAY
FIRST = W0 - (WARMUP + EXTRA) * H
SPLIT = W0 - 100 * H  # the warm-up reaches back into exploration
CYCLE = "C2-0001"
HYP = "ab" * 32
Z_CRIT = "0"
BENCHMARK = "b" * 64
# long below the 72 h EMA: on this synthetic path the nominee's real G-9 z is
# then >= 0, so both families reach status (a)
SIGNAL = (
    b"def s(row, params, state):\n    return 1.0 if row['ema_dist_72'] < 0 else 0.0\n"
)
_names = itertools.count()


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    saved = list(sys.path)
    cf.load_line266()
    monkeypatch.setattr(dsr, "_V_VERIFIED", True)
    monkeypatch.setattr(cf, "benchmark_spec_sha256", lambda root=None: BENCHMARK)
    yield
    sys.path[:] = saved


def _bars() -> tuple[Any, dict[tuple[str, str], Any]]:
    """A composite over exploration [FIRST, SPLIT), confirmation [SPLIT, END)
    and a sealed lockbox; the whole partitions `read` serves."""
    rows = ts._screen_path(WARMUP + EXTRA)[:-1]
    k = (SPLIT - FIRST) // H
    served: dict[tuple[str, str], Any] = {}
    parts: list[Any] = []
    snap = dm.available("f" * 64, FIRST)
    for s, sym in enumerate(SYMBOLS):
        for part, lo, hi, chunk in (
            ("exploration", FIRST, SPLIT, rows[:k]),
            ("confirmation", SPLIT, END, rows[k:]),
        ):
            series = screen.path_series(chunk, s, lo)
            served[(part, sym)] = series
            parts.append(dm.build_partition_manifest(
                partition=part, series=series,
                raw_artifacts=(dm.RawArtifact(name=f"{part}.csv", content=b"x"),),
                parser_code_sha256="e" * 64, window_start_utc=lo,
                window_end_exclusive_utc=hi, fees=snap, exchange_filters=snap,
                symbol_status=snap,
            ))  # fmt: skip
        parts.append(dm.sealed_partition_reference(
            partition="lockbox", symbol=sym, interval_label="1h",
            window_start_utc=END, window_end_exclusive_utc=END + 1000 * H,
            manifest_sha256="d" * 64))  # fmt: skip
    comp = dm.build_composite_manifest(cycle_id=CYCLE, protocol_sha256=P,
                                       partitions=parts)  # fmt: skip
    return comp, served


def _qualification(tmp: Path) -> str:
    """A qualification object directory; returns its manifest hash."""
    frozen = {
        "upper": {"K": "2", "T": str(T_DAYS)} | dict.fromkeys(classifier.UPPER, "1e9"),
        "lower": {"K": "2", "T": str(T_DAYS)} | dict.fromkeys(classifier.LOWER, "-1e9"),
    }
    report = {"z_crit": Z_CRIT, "family_block_rule": "largest",
              "final_thresholds": {f"T={T_DAYS}": frozen}}  # fmt: skip
    tmp.mkdir()
    return ti._object(tmp, {"choices.json": cj(report)})


class World:
    """One cycle: a trend and a vol trial, their code, screen record,
    declaration, signed C2, the public header chain and a capture record."""

    def __init__(self, tmp: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self.monkeypatch = monkeypatch

        def read_object(files: dict[str, bytes]) -> tuple[dict[str, Any], dict]:
            return json.loads(files["choices.json"]), {}

        monkeypatch.setattr(qobj, "read", read_object)
        self.object_dir = tmp / "qobj"
        object_sha256 = _qualification(self.object_dir)
        self.ledger = tmp / "ledger.jsonl"
        digest = hashlib.sha256(SIGNAL).hexdigest()
        self.code = {digest: SIGNAL}
        module = f"c2joined_sig_{next(_names)}"
        self.objs: dict[str, dict[str, Any]] = {
            tid: ts._trial(
                trial_id=tid, family=fam, signal=f"{module}:s", signal_sha256=digest
            )  # fmt: skip
            for tid, fam in (("tr1", "trend"), ("vo1", "vol"))
        }
        trials = list(self.objs.values())
        self.screen_record = cj({
            "trial_set_sha256": screen.trial_set_sha256(trials),
            "qualification_object_sha256": object_sha256,
            "outcome": "SCREEN_AVAILABLE",
        })  # fmt: skip
        self.composite, self.served = _bars()
        self.reads = 0
        decl = {
            "protocol_hash": P,
            "cycle_id": CYCLE,
            "trials": [
                {
                    "family": o["family"],
                    "trial_id": i,
                    "hypothesis_hash": HYP,
                    "configuration_hash": screen.trial_sha256(o),
                    "trial_index": n,
                }
                for n, (i, o) in enumerate(self.objs.items())
            ],  # fmt: skip
            "data_manifest_sha256": self.composite.manifest_sha256,
            "last_seen": "2021-12-01T00:00:00Z",
            "embargo_days": G_DAYS,
            "ledger_anchor": {"head_hash": GENESIS_HASH, "entry_count": 0},
            "screen_record_sha256": hashlib.sha256(self.screen_record).hexdigest(),
        }
        protocol = sg.protocol(
            confirmation_start=cf._time(W0), g_days=str(G_DAYS), t_min=str(T_DAYS),
            z_crit=Z_CRIT, canonical_benchmark_sha256=BENCHMARK,
        ) + f'\n  qualification_object_sha256: "{object_sha256}"'.encode()  # fmt: skip
        # public mainnet headers 0..5 (the post's block is height 0) and a
        # capture of h+5 whose time fixes the known quicknet round
        self.acceptance, acc_sha = ti._acceptance(ti.GENESIS, 0)
        body = ti.BLOCK5.encode()
        self.capture = cj({
            "schema": cf.CAPTURE_SCHEMA,
            "url": "https://mempool.space/api/block-height/5",
            "timestamp": sd._cdx_for_round(sd.REAL.round),
            "status": "200",
            "digest": base64.b32encode(hashlib.sha1(body).digest()).decode(),
            "payload": base64.b64encode(body).decode(),
            "content_encoding": "identity",
            "body": ti.BLOCK5,
            "acceptance_record_sha256": acc_sha,
        })  # fmt: skip
        self.started = cf.Started(
            protocol_hash=P, lockbox_module_sha256="4" * 64,
            confirmation_module_sha256="5" * 64, engine_commit="6" * 40,
            screen_object_sha256="7" * 64, image_digest="sha256:" + "8" * 64,
            protocol=protocol, declaration=cj(decl), declaration_sha256="0" * 64,
            chain_log={"acceptance_record_sha256": acc_sha},
        )  # fmt: skip

    def sources(self, ledger: Path | None = None) -> dict[str, Any]:
        return {
            "ledger_path": ledger or self.ledger, "acceptance_record": self.acceptance,
            "headers": ti.MAINNET[:6], "beacon": sd.REAL,
            "capture_record": self.capture, "object_dir": self.object_dir,
            "screen_record": self.screen_record, "trial_objects": self.objs,
            "code_files": self.code,
        }  # fmt: skip

    def read(self) -> tuple[Any, dict[tuple[str, str], Any]]:
        self.reads += 1
        return self.composite, dict(self.served)

    def run_trials(self) -> dict[str, dict[str, Any]]:
        """The runner's start, then the real `evaluate_trial`, per trial."""
        out = {}
        for n, (tid, o) in enumerate(self.objs.items()):
            aid = f"attempt-{tid}"
            attempts.start_attempt(
                self.ledger, attempt_id=aid, family=o["family"], hypothesis_hash=HYP,
                trial_index=n, symbols=["BTCUSDT"], cycle=CYCLE,
                partition="confirmation", protocol_hash=P,
            )  # fmt: skip
            out[tid] = cf.evaluate_trial(self.started, self.sources(), tid, aid,
                                         self.read)  # fmt: skip
        # B6FR-A-1: the look clock is fixed (F-5 needs one instant for both
        # looks) and never before the ledger's last entry, whatever the date
        look = datetime.now(UTC).replace(microsecond=0) + timedelta(seconds=1)
        self.monkeypatch.setattr(cf, "_now", lambda: look)
        return out


class Recorders:
    """`nominee_gates` (every gate PASS or its frozen N/A), `cpcv_report` and
    `persist`, each recording what it was given."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, cpcv: str = "x") -> None:
        self.gates: list[tuple[Any, ...]] = []
        self.cpcv: list[tuple[Any, ...]] = []
        self.persisted: list[tuple[bytes, bytes, dict[str, bytes]]] = []

        def nominee_gates(*a: Any) -> dict[str, cf.Gate]:
            self.gates.append(a)
            return {g: cf.Gate(cf.NA if g in cf.NA_GATES else cf.PASS)
                    for g in cf.NOMINEE_GATES}  # fmt: skip

        def cpcv_report(*a: Any) -> dict[str, Any]:
            self.cpcv.append(a)
            return {"role": cf.CPCV_ROLE, "status": "recorded", "mark": cpcv}

        monkeypatch.setattr(cf, "nominee_gates", nominee_gates)
        monkeypatch.setattr(cf, "cpcv_report", cpcv_report)

    def persist(self, evaluation: bytes, sealing: bytes,
                artifacts: dict[str, bytes]) -> None:  # fmt: skip
        self.persisted.append((evaluation, sealing, artifacts))


def test_the_real_producers_feed_the_real_consumers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    w = World(tmp_path, monkeypatch)
    rec = Recorders(monkeypatch)
    payloads = w.run_trials()
    assert w.reads == 2
    inputs = cf.prepare(w.started, w.sources())
    for tid, p in payloads.items():
        assert p["d"] is not None and p["reason"] is None
        assert {k: p[k] for k in inputs.expected(tid)} == inputs.expected(tid)

    evaluation, sealing, artifacts = cf.evaluate_look(w.started, w.sources(), w.read,
                                                      rec.persist)  # fmt: skip
    assert w.reads == 3  # one read for the look
    # each result entry is accepted at the look
    for tid, p in payloads.items():
        fam = evaluation["families"][p["family"]]
        assert fam["states"] == {tid: "completed"}
        assert fam["A_f"] is True and fam["nominee"] == tid
    assert evaluation["trials"] == {
        tid: hashlib.sha256(cj(p)).hexdigest() for tid, p in payloads.items()
    }
    # the look evaluated the trial stage's path: each nominee's gates got it
    for args in rec.gates:
        trial, path = args[0], args[1]
        assert len(path) == trial["warmup_hours"] + T_DAYS * 24 + 1
    for f, fam in evaluation["families"].items():
        assert fam["outcome"] == "PROCEEDS_TO_LOCKBOX", (f, fam["gates"]["G-9"])
    # status (a), and its d is the d the trial stage hashed before the look
    assert {f: e["status"] for f, e in sealing["families"].items()} == {
        "trend": "a",
        "vol": "a",
    }, sealing
    for f, artifact in artifacts.items():
        tid = sealing["families"][f]["nominee_trial_id"]
        assert artifact["source"]["d_sha256"] == payloads[tid]["d_sha256"]
        assert sealing["families"][f]["prediction_artifact_sha256"] == (
            hashlib.sha256(cj(artifact)).hexdigest()
        )
    # persisted exactly, then the closing entry names both records' hashes
    [(ev_bytes, seal_bytes, art_bytes)] = rec.persisted
    assert ev_bytes == cj(evaluation) and seal_bytes == cj(sealing)
    assert art_bytes == {f: cj(a) for f, a in artifacts.items()}
    last = read_entries(w.ledger)[-1]
    assert last.record_type == cf.CLOSING_ENTRY
    assert last.payload == cf.closing_entry(
        CYCLE,
        hashlib.sha256(ev_bytes).hexdigest(),
        hashlib.sha256(seal_bytes).hexdigest(),
    )


def _without(x: Any, *keys: str) -> Any:
    """`x` with every mapping key in `keys` dropped, at any depth."""
    if isinstance(x, dict):
        return {k: _without(v, *keys) for k, v in x.items() if k not in keys}
    if isinstance(x, list):
        return [_without(v, *keys) for v in x]
    return x


def test_cpcv_reaches_nothing_but_its_own_field(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F-5: the same ledger looked at twice with two different C-14 reports
    gives records that differ only in `cpcv` and the hashes covering it."""
    w = World(tmp_path, monkeypatch)
    w.run_trials()
    copy = tmp_path / "copy.jsonl"
    shutil.copyfile(w.ledger, copy)
    got = []
    for ledger, mark in ((w.ledger, "one"), (copy, "two")):
        rec = Recorders(monkeypatch, cpcv=mark)
        got.append(cf.evaluate_look(w.started, w.sources(ledger), w.read, rec.persist))
    (ev1, seal1, art1), (ev2, seal2, art2) = got
    assert ev1 != ev2  # the reports did differ
    covering = ("cpcv", "evaluation_record_sha256", "prediction_artifact_sha256")
    assert _without(ev1, *covering) == _without(ev2, *covering)
    assert _without(seal1, *covering) == _without(seal2, *covering)
    assert _without(art1, *covering) == _without(art2, *covering)
    assert set(art1) == set(art2) == {"trend", "vol"}
    assert all(a["source"]["d_sha256"] for a in art1.values())
