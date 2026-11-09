"""R-14a confirmation module, slice 4a: seeds (DESIGN §5.1; DRAFT R-7, R-13,
seed_disclosure; protocol line 266). Synthetic data, plus one public drand
quicknet beacon as a real vector for the randomness = SHA-256(signature) link."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

import pytest
import test_calibration_screen as ts  # the screen tests' trial fixture

from aqt.core import preregistration
from calibration import c2_confirmation as cf
from calibration import screen

# drand quicknet (api.drand.sh .../info and .../public/1000000, fetched 2026-11-09)
QUICKNET = cf.Chain(
    public_key="83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c"
    "8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf8"
    "09bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a",
    genesis_time=1692803367,
    period=3,
)
REAL = cf.Beacon(
    round=1_000_000,
    randomness="b22aad4794f7451896f7a371aa46106fd84d919f3f569acd5b2fddf1d1440af3",
    signature="83ad29e4c409f9470fc2ef02f90214df49e02b441a1a241a82d622d9f608ef98"
    "fd8b11a029f1bee9d9e83b45088abe72",
)
H = hashlib.sha256(b"protocol").hexdigest()
MANIFEST = hashlib.sha256(b"manifest").hexdigest()


def _accept(key: str, beacon: cf.Beacon) -> bool:
    return True


def _cdx_for_round(r: int, chain: cf.Chain = QUICKNET) -> str:
    """A capture time exactly 24 h before round r's scheduled time."""
    t = chain.genesis_time + (r - 1) * chain.period - 86_400
    return datetime.fromtimestamp(t, UTC).strftime("%Y%m%d%H%M%S")


def _declared() -> dict[str, list[dict[str, Any]]]:
    return {
        f: [ts._trial(trial_id=f"t{i:03d}", family=f) for i in range(n)]
        for f, n in (("trend", 2), ("vol", 1))
    }


def _records(
    declared: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    return {
        f: [
            {
                "trial_id": t["trial_id"],
                "hypothesis_hash": hashlib.sha256(
                    f"{f}{t['trial_id']}".encode()
                ).hexdigest(),
                "configuration_hash": screen.trial_sha256(t),
                "trial_index": i,
            }
            for i, t in enumerate(trials)
        ]
        for f, trials in declared.items()
    }


def _derive(**over: Any) -> dict[str, Any]:
    declared = over.pop("declared", _declared())
    args: dict[str, Any] = {
        "declared": declared,
        "records": _records(declared),
        "protocol_hash": H,
        "cycle_id": "C2",
        "window_id": '["2025-01-01T00:00:00Z","2026-01-01T00:00:00Z"]',
        "data_manifest_hash": MANIFEST,
        "beacon": REAL,
        "capture_cdx": _cdx_for_round(REAL.round),
        "chain": QUICKNET,
        "verify": _accept,
        "line266": preregistration.trial_seed,  # the frozen function (R-8)
    }
    args.update(over)
    return cf.derive_seeds(**args)


# --- round and beacon -----------------------------------------------------------


def test_round_is_the_first_at_or_after_capture_plus_24h() -> None:
    assert cf.beacon_round(_cdx_for_round(1_000_000), QUICKNET) == 1_000_000
    one_later = datetime.strptime(_cdx_for_round(1_000_000), "%Y%m%d%H%M%S")
    one_later = one_later.replace(second=one_later.second + 1)
    assert cf.beacon_round(one_later.strftime("%Y%m%d%H%M%S"), QUICKNET) == 1_000_001
    assert cf.beacon_round("20200101000000", QUICKNET) == 1  # before genesis
    for bad in ("2026110900000", "2026-11-09T00", "20261332000000", 20261109000000):
        with pytest.raises(cf.SeedError):
            cf.beacon_round(bad, QUICKNET)  # type: ignore[arg-type]
    with pytest.raises(cf.SeedError, match="period"):
        cf.beacon_round("20261109000000", cf.Chain("ab", 1, 0))


def test_real_quicknet_beacon_passes_the_local_checks() -> None:
    # drand's randomness is SHA-256 of the signature: true for the published vector
    cf.check_beacon(REAL, REAL.round, QUICKNET, _accept)


@pytest.mark.parametrize(
    ("beacon", "match"),
    [
        (cf.Beacon(999_999, REAL.randomness, REAL.signature), "fixed round"),
        (cf.Beacon(True, REAL.randomness, REAL.signature), "fixed round"),  # bool
        (cf.Beacon(REAL.round, "0" * 64, REAL.signature), "SHA-256 of its signature"),
        (
            cf.Beacon(REAL.round, REAL.randomness.upper(), REAL.signature),
            "lowercase hex",
        ),
        (cf.Beacon(REAL.round, REAL.randomness, REAL.signature + "0"), "lowercase hex"),
    ],
)
def test_beacon_refusals(beacon: cf.Beacon, match: str) -> None:
    with pytest.raises(cf.SeedError, match=match):
        cf.check_beacon(beacon, REAL.round, QUICKNET, _accept)


def test_signature_must_verify_and_verifier_errors_fail_closed() -> None:
    with pytest.raises(cf.SeedError, match="does not verify"):
        cf.check_beacon(REAL, REAL.round, QUICKNET, lambda k, b: False)
    with pytest.raises(cf.SeedError, match="does not verify"):
        cf.check_beacon(REAL, REAL.round, QUICKNET, lambda k, b: 1)  # type: ignore[arg-type,return-value]

    def boom(key: str, beacon: cf.Beacon) -> bool:
        raise RuntimeError("library missing")

    with pytest.raises(cf.SeedError, match="verification failed: RuntimeError"):
        cf.check_beacon(REAL, REAL.round, QUICKNET, boom)
    seen: list[tuple[str, cf.Beacon]] = []

    def spy(key: str, beacon: cf.Beacon) -> bool:
        seen.append((key, beacon))
        return True

    cf.check_beacon(REAL, REAL.round, QUICKNET, spy)
    assert seen == [(QUICKNET.public_key, REAL)]  # the chain key, never a caller's


# --- R-7 and Annex B §2.4 encodings -----------------------------------------------


def test_family_seed_is_the_named_object_encoding() -> None:
    a = "a" * 64
    expected_bytes = (
        '{"annex_b_seed":"' + a + '","beacon_randomness":"' + REAL.randomness
        + '","round":1000000}'
    ).encode()  # fmt: skip
    assert cf.beacon_family_seed(a, REAL) == hashlib.sha256(expected_bytes).hexdigest()
    with pytest.raises(cf.SeedError):
        cf.beacon_family_seed("A" * 64, REAL)
    with pytest.raises(cf.SeedError):
        cf.beacon_family_seed(a, cf.Beacon(0, REAL.randomness, REAL.signature))


def test_annex_b_seed_matches_an_independent_encoding_and_keeps_trial_order() -> None:
    keys = ("trial_id", "hypothesis_hash", "configuration_hash")
    trials = [
        {"trial_id": "t001", "hypothesis_hash": "1" * 64,
         "configuration_hash": "2" * 64, "trial_index": 5},
        {"trial_id": "t000", "hypothesis_hash": "3" * 64,
         "configuration_hash": "4" * 64, "trial_index": 0},
    ]  # fmt: skip
    kw = dict(protocol_hash=H, family="trend", cycle_id="C2", window_id="w",
              data_manifest_hash=MANIFEST)  # fmt: skip
    obj = {
        "cycle_id": "C2",
        "data_manifest_hash": MANIFEST,
        "family_id": "trend",
        "protocol_hash": H,
        "trials": [{k: t[k] for k in keys} for t in trials],
        "window_id": "w",
    }  # fmt: skip
    raw = json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    assert cf.annex_b_seed(trials=trials, **kw) == hashlib.sha256(raw).hexdigest()
    assert cf.annex_b_seed(trials=trials[::-1], **kw) != cf.annex_b_seed(
        trials=trials, **kw
    )


# --- the whole derivation -------------------------------------------------------


def test_derive_seeds_records_every_seed_with_its_provenance() -> None:
    rec = _derive()
    assert rec["beacon"] == {
        "chain_public_key": QUICKNET.public_key,
        "capture_cdx": _cdx_for_round(REAL.round),
        "round": REAL.round,
        "randomness": REAL.randomness,
        "signature": REAL.signature,
    }
    declared = _declared()
    records = _records(declared)
    for family, fam in rec["families"].items():
        annex_b = cf.annex_b_seed(
            protocol_hash=H, family=family, cycle_id="C2",
            window_id='["2025-01-01T00:00:00Z","2026-01-01T00:00:00Z"]',
            data_manifest_hash=MANIFEST, trials=records[family],
        )  # fmt: skip
        assert fam["annex_b_seed"] == annex_b
        assert fam["family_seed"] == cf.beacon_family_seed(annex_b, REAL)
        assert list(fam["trials"]) == [r["trial_id"] for r in records[family]]
        for r in records[family]:
            t = fam["trials"][r["trial_id"]]
            r13 = (
                '{"family_seed":"' + fam["family_seed"] + '","trial_id":"'
                + r["trial_id"] + '"}'
            ).encode()  # fmt: skip
            assert t["trial_seed"] == hashlib.sha256(r13).hexdigest()  # R14S4-S note
            assert t["seed_l266"] == preregistration.trial_seed(
                protocol_hash=H, hypothesis_hash=r["hypothesis_hash"],
                trial_index=r["trial_index"],
            )  # fmt: skip
            assert t["estimator_seed"] == int(t["seed_l266"], 16) % 2**31
            assert t["estimator_seed_policy"] == "L266_MOD_2_31"
    assert (
        rec["families"]["trend"]["family_seed"] != rec["families"]["vol"]["family_seed"]
    )


def test_a_different_beacon_gives_different_family_seeds() -> None:
    sig = "ab" * 48
    other = cf.Beacon(REAL.round, hashlib.sha256(bytes.fromhex(sig)).hexdigest(), sig)
    assert (
        _derive(beacon=other)["families"]["trend"]["family_seed"]
        != _derive()["families"]["trend"]["family_seed"]
    )


def test_estimator_seed_zero_is_kept() -> None:
    # A1b: a seed mapping to 0 is legitimate; the record keeps the policy, not a 0-test
    zero = format(2**31 * 7, "064x")
    assert screen.estimator_seed(zero) == 0
    rec = _derive(line266=lambda **kw: zero)  # through the full derivation
    t = rec["families"]["trend"]["trials"]["t000"]
    assert (t["seed_l266"], t["estimator_seed"]) == (zero, 0)


def test_duplicate_trial_id_is_refused_not_dropped() -> None:
    declared = _declared()
    declared["trend"][1] = ts._trial(trial_id="t000", family="trend", horizon_hours=24)
    records = _records(declared)
    assert records["trend"][0]["trial_index"] != records["trend"][1]["trial_index"]
    with pytest.raises(cf.SeedError, match="trial_id must be distinct"):
        _derive(declared=declared, records=records)


def _broken_records(change: Any) -> dict[str, list[dict[str, Any]]]:
    declared = _declared()
    records = _records(declared)
    change(records)
    return records


@pytest.mark.parametrize(
    ("change", "match"),
    [
        (lambda r: r["trend"].reverse(), "in order"),
        (lambda r: r["trend"].pop(), "in order"),
        (lambda r: r.pop("vol"), "declared families"),
        (lambda r: r["trend"][0].update(trial_index=1), "distinct"),
        (lambda r: r["trend"][0].update(trial_index=True), "distinct"),
        (lambda r: r["trend"][0].update(trial_index=-1), "distinct"),
        (lambda r: r["trend"][0].update(hypothesis_hash="x" * 64), "hypothesis_hash"),
        (
            lambda r: r["trend"][0].update(configuration_hash="0" * 64),
            "configuration_hash",
        ),
        (lambda r: r["trend"][0].update(extra=1), "fields"),
    ],
)
def test_record_refusals(change: Any, match: str) -> None:
    with pytest.raises(cf.SeedError, match=match):
        _derive(records=_broken_records(change))


def test_seed_failures_refuse_the_whole_evaluation() -> None:
    with pytest.raises(cf.SeedError, match="does not verify"):
        _derive(verify=lambda k, b: False)
    with pytest.raises(cf.SeedError, match="fixed round"):
        _derive(capture_cdx=_cdx_for_round(REAL.round + 1))
    with pytest.raises(cf.SeedError, match="64 lowercase hex"):
        _derive(protocol_hash="z" * 64)
    assert issubclass(cf.SeedError, cf.CycleError)


def test_line266_is_the_frozen_function_and_bad_output_fails_closed() -> None:
    def broken(**kw: Any) -> str:
        raise RuntimeError("jsonschema missing")

    with pytest.raises(cf.SeedError, match="line-266 seed failed: RuntimeError"):
        _derive(line266=broken)
    with pytest.raises(cf.SeedError, match="line-266 seed is not 64"):
        _derive(line266=lambda **kw: "A" * 64)


def test_the_module_does_not_import_preregistration() -> None:
    # aqt.core.preregistration imports jsonschema, absent from the pinned image
    # (test_d19_deploy); the module must stay importable there (LG4-6)
    import ast
    from pathlib import Path

    tree = ast.parse(Path(cf.__file__).read_text(encoding="utf-8"))
    names = {
        a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names
    }
    names |= {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert not any("preregistration" in n for n in names)
