"""Slice 6b part 2: read-free input checks (DESIGN_SLICE6B rev 16 §2, §2.1)."""

from __future__ import annotations

import base64
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from calibration import c2_confirmation as c
from calibration.seeds import cj, sha

# Bitcoin mainnet headers of heights 0..6 (public; fetched 2026-11-15 from
# blockstream.info and self-verifying: the links and the genesis hash below must hold)
MAINNET = [bytes.fromhex(h) for h in (
    "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c",
    "010000006fe28c0ab6f1b372c1a6a246ae63f74f931e8365e15a089c68d6190000000000982051fd1e4ba744bbbe680e1fee14677ba1a3c3540bf7b1cdb606e857233e0e61bc6649ffff001d01e36299",
    "010000004860eb18bf1b1620e37e9490fc8a427514416fd75159ab86688e9a8300000000d5fdcc541e25de1c7a5addedf24858b8bb665c9f36ef744ee42c316022c90f9bb0bc6649ffff001d08d2bd61",
    "01000000bddd99ccfda39da1b108ce1a5d70038d0a967bacb68b6b63065f626a0000000044f672226090d85db9a9f2fbfe5f0f9609b387af7be5b7fbb7a1767c831c9e995dbe6649ffff001d05e0ed6d",
    "010000004944469562ae1c2c74d9a535e00b6f3e40ffbad4f2fda3895501b582000000007a06ea98cd40ba2e3288262b28638cec5337c1456aaf5eedc8e9e5a20f062bdf8cc16649ffff001d2bfee0a9",
    "0100000085144a84488ea88d221c8bd6c059da090e88f8a2c99690ee55dbba4e00000000e11c48fecdd9e72510ca84f023370c9a38bf91ac5cae88019bee94d24528526344c36649ffff001d1d03e477",
    "01000000fc33f596f822a0a1951ffdbf2a897b095636ad871707bf5d3162729b00000000379dfb96a5ea8c81700ea4ac6b97ae9a9312b2d4301a29580e924ee6761a2520adc46649ffff001d189c4c97",
)]  # fmt: skip
GENESIS = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
BLOCK5 = "000000009b7262315dbf071787ad3656097b892abffd1f95a1a022f896f533fc"


def _acceptance(block_hash: str = GENESIS, height: int = 1) -> tuple[bytes, str]:
    record = cj({"block_hash": block_hash, "height": height})
    return record, hashlib.sha256(record).hexdigest()


def test_headers_check_known_answer_mainnet_0_to_5() -> None:
    record, digest = _acceptance()
    got = c.headers_check(record, digest, MAINNET[:6])
    assert got.height == 1
    assert got.cycle_start == datetime(2009, 1, 3, 18, 15, 5, tzinfo=UTC)  # genesis
    assert got.tip_block_hash == BLOCK5
    assert got.tip_time == datetime.fromtimestamp(0x4966C344, UTC)
    assert got.headers_sha256 == hashlib.sha256(b"".join(MAINNET[:6])).hexdigest()


def test_headers_check_refuses_another_acceptance_record() -> None:
    record, _ = _acceptance()
    with pytest.raises(c.CycleError, match="not the one start verified"):
        c.headers_check(record, "0" * 64, MAINNET[:6])


def test_headers_check_refuses_headers_of_another_block() -> None:
    record, digest = _acceptance()
    with pytest.raises(c.CycleError, match="includes the post"):
        c.headers_check(record, digest, MAINNET[1:7])  # a valid chain, one block later


@pytest.mark.parametrize("headers", [
    MAINNET[:5], MAINNET[:7], [*MAINNET[:5], MAINNET[5][:79]],
    [*MAINNET[:5], bytearray(MAINNET[5])],
])  # fmt: skip
def test_headers_check_refuses_wrong_count_or_size(headers: list[bytes]) -> None:
    record, digest = _acceptance()
    with pytest.raises(c.CycleError, match="exactly 6 headers"):
        c.headers_check(record, digest, headers)


def test_headers_check_refuses_a_broken_link() -> None:
    record, digest = _acceptance()
    swapped = [*MAINNET[:3], MAINNET[4], MAINNET[3], MAINNET[5]]
    with pytest.raises(c.CycleError, match=r"headers\[3\] does not follow"):
        c.headers_check(record, digest, swapped)
    altered = bytearray(MAINNET[2])
    altered[76] ^= 1  # nonce: headers[2]'s hash changes, so headers[3] no longer links
    with pytest.raises(c.CycleError, match=r"headers\[3\]"):
        c.headers_check(record, digest, [*MAINNET[:2], bytes(altered), *MAINNET[3:6]])


def test_headers_check_link_uses_internal_byte_order() -> None:
    """A link written in display order (reversed) must not pass."""
    record, digest = _acceptance()
    flipped = bytearray(MAINNET[1])
    flipped[4:36] = flipped[4:36][::-1]
    with pytest.raises(c.CycleError, match=r"headers\[1\]"):
        c.headers_check(record, digest, [MAINNET[0], bytes(flipped), *MAINNET[2:6]])


# --- capture record (§2.1, schema v2 per VERIFY_CAPTURE_DIGEST_2026-11-15.md) --------

# Internet Archive capture of https://blockstream.info/api/block-height/0 at
# 20260905161311: the exact 69 gzip bytes of its `id_` fetch and its CDX digest
KNOWN_PAYLOAD = bytes.fromhex(
    "1f8b080000000000040335c1c901c0200804c096387485725602fd97e02b33223fcd0f882c89"
    "cd56ec70edf43573e0ec051a517aecfae88530aa0df300854028b040000000"
)
KNOWN_DIGEST = "NNVZIO5QLFHVIRULV75YOBX7EKNQDJMI"
TIP_TIME = datetime(2026, 9, 5, 17, 0, tzinfo=UTC)
ACC = "a" * 64


def _tip(height: int = -5, tip: str = GENESIS) -> c.Headers:
    """Headers whose h+5 is block 0, the known capture's height."""
    return c.Headers(height=height, cycle_start=TIP_TIME, tip_block_hash=tip,
                     tip_time=TIP_TIME, headers_sha256="0" * 64)  # fmt: skip


def _capture(**change: object) -> bytes:
    r = {
        "schema": c.CAPTURE_SCHEMA,
        "url": "https://blockstream.info/api/block-height/0",
        "timestamp": "20260905161311",
        "status": "200",
        "digest": KNOWN_DIGEST,
        "payload": base64.b64encode(KNOWN_PAYLOAD).decode(),
        "content_encoding": "gzip",
        "body": GENESIS,
        "acceptance_record_sha256": ACC,
        **change,
    }
    return cj(r)


def test_capture_known_answer_real_archive_capture() -> None:
    record = _capture()
    got = c.check_capture_record(record, _tip(), ACC)
    assert got.timestamp == "20260905161311"
    assert got.record_sha256 == hashlib.sha256(record).hexdigest()
    assert got.before_tip_window is False  # 16:13 is within 2 h before 17:00


def test_capture_before_tip_window_is_a_diagnostic_not_a_refusal() -> None:
    late_tip = c.Headers(height=-5, cycle_start=TIP_TIME, tip_block_hash=GENESIS,
                         tip_time=datetime(2026, 9, 5, 18, 14, tzinfo=UTC),
                         headers_sha256="0" * 64)  # fmt: skip
    assert c.check_capture_record(_capture(), late_tip, ACC).before_tip_window is True


def test_capture_mempool_url_and_identity_encoding_pass() -> None:
    raw = GENESIS.encode()
    digest = base64.b32encode(hashlib.sha1(raw).digest()).decode()
    record = _capture(url="https://mempool.space/api/block-height/0",
                      content_encoding="identity", digest=digest,
                      payload=base64.b64encode(raw).decode())  # fmt: skip
    assert c.check_capture_record(record, _tip(), ACC).timestamp == "20260905161311"


def test_capture_digest_of_the_body_alone_is_refused() -> None:
    """Rev 16 item 3 as written (digest of the body) must not pass for gzip."""
    body_digest = base64.b32encode(hashlib.sha1(GENESIS.encode()).digest()).decode()
    with pytest.raises(c.CycleError, match="CDX digest"):
        c.check_capture_record(_capture(digest=body_digest), _tip(), ACC)


@pytest.mark.parametrize(("change", "match"), [
    ({"url": "https://blockstream.info/api/block-height/1"}, "qualifying URL"),
    ({"url": "http://blockstream.info/api/block-height/0"}, "qualifying URL"),
    ({"url": "https://web.archive.org/web/20260905161311/https://blockstream.info/api/block-height/0"},
     "qualifying URL"),
    ({"timestamp": "2026090516131"}, "14 CDX digits"),
    ({"timestamp": "20261305161311"}, "14 CDX digits"),
    ({"timestamp": 20260905161311}, "14 CDX digits"),
    ({"status": 200}, "status"),
    ({"status": "302"}, "status"),
    ({"payload": "not base64!"}, "base64"),
    ({"payload": base64.b64encode(KNOWN_PAYLOAD).decode() + "\n"}, "base64"),
    ({"content_encoding": "br"}, "not supported"),
    ({"content_encoding": "identity"}, "decoded payload"),
    ({"body": GENESIS + "\n"}, "decoded payload"),
    ({"body": None}, "decoded payload"),
    ({"acceptance_record_sha256": "b" * 64}, "another acceptance record"),
    ({"schema": "aqt.c2.capture_record.v1"}, "schema"),
])  # fmt: skip
def test_capture_refusals(change: dict[str, object], match: str) -> None:
    with pytest.raises(c.CycleError, match=match):
        c.check_capture_record(_capture(**change), _tip(), ACC)


def test_capture_body_must_be_the_tip_hash() -> None:
    with pytest.raises(c.CycleError, match="tip block hash"):
        c.check_capture_record(_capture(), _tip(tip=BLOCK5), ACC)


def test_capture_corrupt_gzip_is_refused() -> None:
    bad = KNOWN_PAYLOAD[:-6] + b"\x00" * 6  # crc/length broken
    digest = base64.b32encode(hashlib.sha1(bad).digest()).decode()
    with pytest.raises(c.CycleError, match="gzip"):
        c.check_capture_record(
            _capture(payload=base64.b64encode(bad).decode(), digest=digest), _tip(), ACC
        )


def test_capture_record_must_be_canonical_with_exact_fields() -> None:
    record = _capture()
    with pytest.raises(c.CycleError, match="canonical schema"):
        c.check_capture_record(record + b" ", _tip(), ACC)
    with pytest.raises(c.CycleError, match="canonical schema"):
        c.check_capture_record(cj({**json.loads(record), "extra": 1}), _tip(), ACC)
    with pytest.raises(c.CycleError, match="not JSON"):
        c.check_capture_record(b"{", _tip(), ACC)


# --- qualification re-read and classifier thresholds (§2, §8) ------------------------


def _row(digest: str) -> bytes:
    return f'qualification_object_sha256: "{digest}"\n'.encode()


def _object(tmp_path: Path, files: dict[str, bytes]) -> str:
    for name, data in files.items():
        (tmp_path / name).write_bytes(data)
    manifest = {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}
    (tmp_path / "manifest.json").write_bytes(json.dumps(manifest).encode())
    return sha(manifest)


def test_qualification_report_reads_the_signed_object(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from calibration import qobj

    digest = _object(tmp_path, {"choices.json": b"{}", "definition.json": b"{}"})
    seen: list[dict[str, bytes]] = []

    def read(f: dict[str, bytes]) -> tuple[dict[str, int], dict[str, Any]]:
        seen.append(f)
        return {"r": 1}, {}

    monkeypatch.setattr(qobj, "read", read)
    protocol = _row(digest)
    assert c.qualification_report(tmp_path, protocol) == {"r": 1}
    assert seen == [{"choices.json": b"{}", "definition.json": b"{}"}]
    with pytest.raises(c.CycleError, match="not the signed one"):
        c.qualification_report(tmp_path, _row("0" * 64))
    other = f'screen_object_sha256: "{digest}"\n'.encode()  # R14D6B9-F-1: not this row
    with pytest.raises(c.ChainError, match="qualification_object_sha256"):
        c.qualification_report(tmp_path, other)
    (tmp_path / "choices.json").write_bytes(b"{ }")
    with pytest.raises(c.CycleError, match="choices.json does not match"):
        c.qualification_report(tmp_path, protocol)


def test_qualification_report_turns_a_read_refusal_into_a_cycle_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from calibration import qobj

    digest = _object(tmp_path, {"choices.json": b"{}"})

    def refuse(f: dict[str, bytes]) -> Any:
        raise ValueError("not a qualification run")

    monkeypatch.setattr(qobj, "read", refuse)
    with pytest.raises(c.CycleError, match="not a qualification run"):
        c.qualification_report(tmp_path, _row(digest))


def test_classifier_bounds_pools_like_d19_heldout() -> None:
    from calibration import classifier, reduce

    names_up = sorted(classifier.UPPER)
    names_lo = sorted(classifier.LOWER)
    frozen = {
        "upper": {"K": "4", "T": "900", **{n: "1.5" for n in names_up}},
        "lower": {"K": "4", "T": "900", **{n: "-1.5" for n in names_lo}},
    }
    report = {"final_thresholds": {"T=900": frozen}}
    pool = tuple({n: float(v) for n, v in frozen[s].items()} for s in frozen)
    expected = reduce.for_k(pool, 3)  # type: ignore[arg-type]
    assert c.classifier_bounds(report, 900, 3) == expected
    with pytest.raises(c.CycleError, match="T=901"):
        c.classifier_bounds(report, 901, 3)
    frozen["upper"] = {"K": "4", "T": "900"}  # its tails missing
    with pytest.raises(c.CycleError, match="classifier thresholds"):
        c.classifier_bounds(report, 900, 3)
