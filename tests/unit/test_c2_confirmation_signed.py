"""Slice 6b build B4a: the signed C2 rows (DESIGN_SLICE6B rev 16 §7)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from calibration import c2_confirmation as cf

# drand's published chain info (FP3 files of 2026-10-25, `origin/freeze-sheet`
# review/fp3/drand-info-2026-10-25/<hash>.info.json): public values only
QUICKNET = {
    "public_key": "83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c"
    "8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf8"
    "09bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a",
    "period": 3, "genesis_time": 1692803367,
    "group_hash": "f477d5c89f21a17c863a7f937c6a6d15859414d2be09cd448d4279af331c5d3e",
    "beacon_id": "quicknet",
}  # fmt: skip
QUICKNET_HASH = "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"
DEFAULT = {
    "public_key": "868f005eb8e6e4ca0a47c8a77ceaa5309a47978a7c71bc5cce96366b5d7a5699"
    "37c529eeda66c7293784a9402801af31",
    "period": 30, "genesis_time": 1595431050,
    "group_hash": "176f93498eac9ca337150b46d21dd58673ea4e3581185f869672e59fa4cb390a",
    "beacon_id": "default",
}  # fmt: skip
DEFAULT_HASH = "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce"
EVMNET = {
    "public_key": "07e1d1d335df83fa98462005690372c643340060d205306a9aa8106b6bd0b382"
    "0557ec32c2ad488e4d4f6008f89a346f18492092ccc0d594610de2732c8b808f0095685ae3a85b"
    "a243747b1b2f426049010f6b73a0cf1d389351d5aaaa1047f6297d3a4f9749b33eb2d904c9d9eb"
    "f17224150ddd7abd7567a9bec6c74480ee0b",
    "period": 3, "genesis_time": 1727521075,
    "group_hash": "cd7ad2f0e0cce5d8c288f2dd016ffe7bc8dc88dbb229b3da2b6ad736490dfed6",
    "beacon_id": "evmnet",
}  # fmt: skip
EVMNET_HASH = "04f1e9062b8a81f848fded9c12306733282b2727ecced50032187751166ec8c3"

ROWS = {
    "drand_public_key": QUICKNET["public_key"],
    "drand_genesis_time": "1692803367",
    "drand_period": "3",
    "drand_group_hash": QUICKNET["group_hash"],
    "drand_beacon_id": "quicknet",
    "drand_chain_hash": QUICKNET_HASH,
    "drand_scheme": cf.SCHEME,
    "confirmation_start": "2022-01-31T00:00:00Z",
    "confirmation_end": "2025-05-31T23:59:59Z",
    "t_min": "365",
    "g_days": "30",
    "z_crit": "2.345",
    "family_block_rule": "largest",
    "canonical_benchmark_sha256": "b" * 64,
}


def protocol(**change: str | None) -> bytes:
    rows = {**ROWS, **change}
    lines = ['schema: "aqt.c2.v1"']
    lines += [f'  {k}: "{v}"' for k, v in rows.items() if v is not None]
    return "\n".join(lines).encode()


@pytest.mark.parametrize(
    ("info", "want"),
    [(QUICKNET, QUICKNET_HASH), (DEFAULT, DEFAULT_HASH), (EVMNET, EVMNET_HASH)],
)
def test_drand_chain_hash_known_answers(info: dict[str, object], want: str) -> None:
    assert cf.drand_chain_hash(**info) == want  # type: ignore[arg-type]


def test_signed_rows_parse_exactly() -> None:
    s = cf.signed_c2(protocol())
    assert s.chain == cf.Chain(QUICKNET["public_key"], 1692803367, 3, cf.SCHEME)  # type: ignore[arg-type]
    assert s.chain_hash == QUICKNET_HASH
    assert s.confirmation_start == datetime(2022, 1, 31, tzinfo=UTC)
    assert s.confirmation_end == cf.V1_CONFIRMATION_END
    assert (s.t_min, s.g_days, s.z_crit) == (365, 30, "2.345")
    assert s.family_block_rule == "largest"
    assert dict(s.rows) == ROWS


@pytest.mark.parametrize(
    ("change", "match"),
    [
        ({"t_min": None}, "t_min is not exactly one row"),
        ({"t_min": "0365"}, "t_min row is not an integer"),
        ({"t_min": "+365"}, "t_min row is not an integer"),
        ({"t_min": " 365"}, "t_min row is not an integer"),
        ({"t_min": "٣٦٥"}, "t_min row is not an integer"),  # Arabic-Indic digits
        ({"g_days": "-1"}, "g_days row is not an integer"),
        ({"drand_period": "0"}, "drand_period row is not an integer"),
        ({"drand_period": str(2**32)}, "drand_period row is not an integer"),
        ({"drand_genesis_time": str(2**63)}, "drand_genesis_time row is not"),
        ({"confirmation_start": "2022-1-31T00:00:00Z"}, "confirmation_start row"),
        ({"confirmation_end": "2025-05-31 23:59:59"}, "confirmation_end row"),
        ({"drand_chain_hash": QUICKNET_HASH.upper()}, "drand_chain_hash row is not"),
        ({"drand_public_key": QUICKNET["public_key"][:96]}, "drand_public_key row"),  # type: ignore[index]
        ({"drand_group_hash": "f" * 63}, "drand_group_hash row"),
        ({"canonical_benchmark_sha256": "x" * 64}, "canonical_benchmark_sha256"),
        ({"drand_beacon_id": "Quick net"}, "drand_beacon_id row"),
        ({"drand_scheme": "pedersen-bls-chained"}, "drand_scheme row"),
        ({"z_crit": "nan"}, "z_crit row"),
        ({"z_crit": "1e3"}, "z_crit row"),
        ({"z_crit": "02.3"}, "z_crit row"),
        ({"family_block_rule": "mean"}, "family_block_rule row"),
        ({"drand_chain_hash": DEFAULT_HASH}, "do not hash to drand_chain_hash"),
        ({"drand_beacon_id": "default"}, "do not hash to drand_chain_hash"),
        ({"drand_group_hash": "0" * 64}, "do not hash to drand_chain_hash"),
        ({"drand_genesis_time": "1692803368"}, "do not hash to drand_chain_hash"),
    ],
)
def test_signed_row_refusals(change: dict[str, str | None], match: str) -> None:
    with pytest.raises(cf.CycleError, match=match):
        cf.signed_c2(protocol(**change))


def test_a_repeated_row_is_refused() -> None:
    raw = protocol() + b'\n  g_days: "30"'
    with pytest.raises(cf.CycleError, match="g_days is not exactly one row"):
        cf.signed_c2(raw)
