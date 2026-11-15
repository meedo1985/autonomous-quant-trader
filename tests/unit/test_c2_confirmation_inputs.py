"""Slice 6b part 2: read-free input checks (DESIGN_SLICE6B rev 16 §2, §2.1)."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

import pytest

from calibration import c2_confirmation as c
from calibration.seeds import cj

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
