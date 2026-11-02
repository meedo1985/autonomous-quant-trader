"""R-14a lockbox module, slice 3b-1: the start chain and the loader (DESIGN
§4; R-14a item 2; O-6a SPEC §3). Synthetic data only."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from calibration import c2_lockbox as lb
from calibration.seeds import cj, sha

ROOT = Path(__file__).resolve().parents[2]
F_TXID = hashlib.sha256(b"funding").hexdigest()


def _v(n: int) -> bytes:
    assert n < 0xFD
    return bytes([n])


def _tx(
    outputs: list[tuple[int, bytes]],
    spends: tuple[str, int] = (F_TXID, 1),
    segwit: bool = True,
    tail: bytes = b"",
) -> bytes:
    txin = bytes.fromhex(spends[0])[::-1] + spends[1].to_bytes(4, "little")
    txin += _v(0) + b"\xff\xff\xff\xff"
    outs = b"".join(v.to_bytes(8, "little") + _v(len(s)) + s for v, s in outputs)
    body = _v(1) + txin + _v(len(outputs)) + outs
    witness = _v(2) + _v(3) + b"sig" + _v(3) + b"key" if segwit else b""
    head = (2).to_bytes(4, "little") + (b"\x00\x01" if segwit else b"")
    return head + body + witness + b"\x00\x00\x00\x00" + tail


def _post(declaration_sha256: str, **kw: Any) -> bytes:
    script = lb.POST_SCRIPT_PREFIX + bytes.fromhex(declaration_sha256)
    change = b"\x00\x14" + b"\x11" * 20  # P2WPKH
    return _tx([(0, script), (900, change)], **kw)


MODULES = {"lockbox_module_sha256": b"lockbox", "confirmation_module_sha256": b"conf"}


def _protocol(**rows: str) -> bytes:
    values = {
        "outpoint_F": f"{F_TXID}:1",
        **{k: hashlib.sha256(v).hexdigest() for k, v in MODULES.items()},
        **rows,
    }
    lines = ["protocol: c2", *(f'  {k}: "{v}"' for k, v in values.items() if v)]
    return ("\n".join(lines) + "\n").encode()


def _chain(**over: Any) -> dict[str, Any]:
    protocol = over.pop("protocol", _protocol())
    declaration = over.pop(
        "declaration", cj({"protocol_hash": hashlib.sha256(protocol).hexdigest()})
    )
    args = {
        "acceptance_record": b"record",
        "post_raw_tx": _post(hashlib.sha256(declaration).hexdigest()),
        "declaration": declaration,
        "protocol": protocol,
        "modules": dict(MODULES),
    }
    args.update(over)
    return args


# --- the post ------------------------------------------------------------


@pytest.mark.parametrize("segwit", [True, False])
def test_parse_tx(segwit: bool) -> None:
    raw = _post("ab" * 32, segwit=segwit)
    inputs, outputs = lb.parse_tx(raw)
    assert inputs == [(F_TXID, 1)]
    assert [v for v, _ in outputs] == [0, 900]
    with pytest.raises(lb.ChainError):
        lb.parse_tx(raw + b"\x00")  # trailing bytes
    with pytest.raises(lb.ChainError):
        lb.parse_tx(raw[:-6])


def test_txid_excludes_the_witness() -> None:
    segwit, legacy = _post("ab" * 32), _post("ab" * 32, segwit=False)
    dsha = hashlib.sha256(hashlib.sha256(legacy).digest()).digest()[::-1].hex()
    assert lb.txid(segwit) == lb.txid(legacy) == dsha
    wtxid = hashlib.sha256(hashlib.sha256(segwit).digest()).digest()[::-1].hex()
    assert lb.txid(segwit) != wtxid
    assert lb.verify_chain(**_chain())["post_txid"] == lb.txid(_chain()["post_raw_tx"])


def test_well_formed_post() -> None:
    assert lb.post_declaration_sha256(_post("ab" * 32), f"{F_TXID}:1") == "ab" * 32


@pytest.mark.parametrize(
    "raw",
    [
        _post("ab" * 32, spends=(F_TXID, 0)),  # does not spend F
        _tx([(0, lb.POST_SCRIPT_PREFIX + b"\xab" * 32)] * 2),  # two OP_RETURNs
        _tx([(1, lb.POST_SCRIPT_PREFIX + b"\xab" * 32)]),  # value not 0
        _tx([(0, bytes.fromhex("6a25") + b"AQTQ1" + b"\xab" * 32)]),  # prefix
        _tx([(0, lb.POST_SCRIPT_PREFIX + b"\xab" * 31)]),  # 38-byte script
        _tx([(900, b"\x00\x14" + b"\x11" * 20)]),  # no OP_RETURN
    ],
)
def test_malformed_posts_refused(raw: bytes) -> None:
    with pytest.raises(lb.ChainError):
        lb.post_declaration_sha256(raw, f"{F_TXID}:1")


# --- the chain -------------------------------------------------------------


def test_valid_chain_logs_every_link() -> None:
    args = _chain()
    log = lb.verify_chain(**args)
    assert log["declaration_sha256"] == hashlib.sha256(args["declaration"]).hexdigest()
    assert log["protocol_hash"] == hashlib.sha256(args["protocol"]).hexdigest()
    assert log["lockbox_module_sha256"] == hashlib.sha256(b"lockbox").hexdigest()
    assert log["acceptance_record_sha256"] == hashlib.sha256(b"record").hexdigest()


def test_each_broken_link_refuses() -> None:
    good = _chain()
    other_decl = cj({"protocol_hash": "0" * 64})
    cases: list[dict[str, Any]] = [
        {"post_raw_tx": _post(hashlib.sha256(other_decl).hexdigest())},  # post
        {"declaration": json.dumps(json.loads(good["declaration"]), indent=1).encode()},
        {"declaration": other_decl},  # protocol_hash differs
        {"protocol": _protocol(lockbox_module_sha256="")},  # row missing
        {"protocol": _protocol() + b'  lockbox_module_sha256: "' + b"0" * 64 + b'"\n'},
        {"protocol": _protocol(outpoint_F="")},  # no F row
        {"modules": {**MODULES, "lockbox_module_sha256": b"swapped"}},
        {"modules": {"lockbox_module_sha256": b"lockbox"}},
        {"modules": {**MODULES, "third": b"x"}},
    ]
    for case in cases:
        args = {**good, **case}
        if "protocol" in case or "declaration" in case:
            args = _chain(**case)
        with pytest.raises(lb.ChainError):
            lb.verify_chain(**args)


def test_unquoted_row_refused() -> None:
    with pytest.raises(lb.ChainError):
        lb.protocol_row(b"  outpoint_F: abc\n", "outpoint_F")


# --- the loader ----------------------------------------------------------


def test_load_verified_executes_the_hashed_bytes(tmp_path: Path) -> None:
    path = tmp_path / "lb_probe.py"
    path.write_bytes(b"VALUE = 1\n")
    digest = hashlib.sha256(b"VALUE = 1\n").hexdigest()
    module = lb.load_verified("lb_probe", path, digest)
    path.write_bytes(b"VALUE = 2\n")  # swapped after the check
    assert module.VALUE == 1 and module.__spec__ is not None
    assert str(module.__spec__.origin).endswith("lb_probe.py")
    with pytest.raises(lb.ChainError):
        lb.load_verified("lb_probe_2", path, digest)
    del sys.modules["lb_probe"]


def test_valid_start_passes_the_frozen_bytecode_check(tmp_path: Path) -> None:
    # a fresh process, as at a real start: caching off, empty prefix, then the
    # frozen rundef.bytecode_problem() with a calibration module loaded by
    # load_verified (R14D3-S-1)
    source = b"VALUE = 7\n"
    path = tmp_path / "c2_probe.py"
    path.write_bytes(source)
    prefix = tmp_path / "pycache"
    prefix.mkdir()
    code = f"""
import sys
sys.dont_write_bytecode = True
sys.pycache_prefix = {str(prefix)!r}
sys.path[:0] = [{str(ROOT)!r}, {str(ROOT / "src")!r}]
from calibration import c2_lockbox as lb, rundef
assert rundef.bytecode_problem() is None, rundef.bytecode_problem()
m = lb.load_verified("calibration.c2_probe", __import__("pathlib").Path({str(path)!r}),
                     {hashlib.sha256(source).hexdigest()!r})
assert m.VALUE == 7
assert rundef.bytecode_problem() is None, rundef.bytecode_problem()
print("ok")
"""
    out = subprocess.run(
        [sys.executable, "-I", "-c", code], capture_output=True, text=True, check=False
    )
    assert out.stdout.strip() == "ok", out.stderr


# --- the code check ------------------------------------------------------


def test_verify_code_extends_reviewed_by_exactly_the_modules(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from calibration import mapping, qobj, screen

    files = {"mapping.py": b"m", "screen.py": b"s", "definition.json": b"{}"}
    for name, data in files.items():
        (tmp_path / name).write_bytes(data)
    manifest = {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}
    (tmp_path / "manifest.json").write_bytes(json.dumps(manifest).encode())
    seen: dict[str, Any] = {}
    monkeypatch.setattr(qobj, "read", lambda f: (None, {"engine_commit": "x"}))
    monkeypatch.setattr(
        screen, "check_screen_code", lambda d, r, reviewed: seen.update(reviewed)
    )
    monkeypatch.setattr(mapping, "check_runtime", lambda d: None)
    modules = {
        "calibration/c2_lockbox.py": b"a",
        "calibration/c2_confirmation.py": b"b",
    }
    lb.verify_code(tmp_path, sha(manifest), ROOT, modules)
    assert seen == {
        "calibration/mapping.py": b"m",
        "calibration/screen.py": b"s",
        **modules,
    }
    with pytest.raises(lb.ChainError):
        lb.verify_code(tmp_path, "0" * 64, ROOT, modules)
    with pytest.raises(lb.ChainError):
        lb.verify_code(tmp_path, sha(manifest), ROOT, {**modules, "x.py": b"c"})
    (tmp_path / "screen.py").write_bytes(b"tampered")
    with pytest.raises(lb.ChainError):
        lb.verify_code(tmp_path, sha(manifest), ROOT, modules)
