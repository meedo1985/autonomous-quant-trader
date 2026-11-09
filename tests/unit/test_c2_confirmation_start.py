"""R-14a confirmation module, slice 6a: the start chain and loader (DESIGN §4,
§5.2 step 1). The chain is the lockbox module's, copied text for text (no
cross-import); `start` verifies everything and loads line 266 before any
protected read. Synthetic data only."""

from __future__ import annotations

import hashlib
import inspect
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from calibration import c2_confirmation as cf
from calibration import c2_lockbox as lb
from tests.unit.test_c2_lockbox_worker import _start_inputs

ROOT = Path(__file__).resolve().parents[2]
BEGIN = "# --- the start chain and the loader (DESIGN §4; R-14a item 2)"
CODE = ("ChainError", "_varint", "parse_tx", "txid", "post_declaration_sha256",
        "check_acceptance", "protocol_row", "verify_chain", "load_verified",
        "verify_code")  # fmt: skip
CONSTANTS = ("POST_SCRIPT_PREFIX", "MODULE_ROWS", "MODULE_PATHS", "SIGNED_ROWS",
             "ACCEPTANCE_SCHEMA", "ACCEPTANCE_FIELDS", "MIN_CONFIRMATIONS",
             "_HEX")  # fmt: skip


def _section(path: Path, end: str) -> str:
    text = path.read_text(encoding="utf-8")
    return text[text.index(BEGIN) : text.index(end)].rstrip()


# --- DESIGN §4: one sequence, two identical copies -------------------------------


def test_the_chain_section_is_the_lockbox_text() -> None:
    ours = _section(ROOT / "calibration/c2_confirmation.py", "# --- Slice 6a")
    theirs = _section(ROOT / "calibration/c2_lockbox.py", "# --- the worker's store")
    assert ours == theirs  # comments included: a one-sided edit fails here


@pytest.mark.parametrize("name", CODE)
def test_each_copied_function_is_the_lockbox_source(name: str) -> None:
    assert inspect.getsource(getattr(cf, name)) == inspect.getsource(getattr(lb, name))


@pytest.mark.parametrize("name", CONSTANTS)
def test_each_copied_constant_is_the_lockbox_value(name: str) -> None:
    assert getattr(cf, name) == getattr(lb, name)


def test_the_copies_do_not_import_each_other() -> None:
    # R-14a item 3: no cross-import in either direction
    for path, other in (("calibration/c2_confirmation.py", "c2_lockbox"),
                        ("calibration/c2_lockbox.py", "c2_confirmation")):  # fmt: skip
        assert other not in (ROOT / path).read_text(encoding="utf-8").replace(
            f"calibration/{other}.py", ""
        )  # only the MODULE_PATHS path string names the other file


# --- ST-1: start ------------------------------------------------------------------


@pytest.fixture
def code_ok(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    seen: dict[str, Any] = {}

    def verify_code(obj: Path, posted: str, root: Path, modules: Any) -> Any:
        seen.update(posted=posted, modules=modules)
        return {"engine_commit": "e" * 40}

    monkeypatch.setattr(cf, "verify_code", verify_code)
    return seen


@pytest.fixture
def line266(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    calls: list[str] = []
    monkeypatch.setattr(cf, "load_line266", lambda: calls.append("loaded"))
    return calls


def test_start_verifies_then_loads_line_266(
    tmp_path: Path, code_ok: dict[str, Any], line266: list[str]
) -> None:
    inputs = _start_inputs(tmp_path)
    started = cf.start(**inputs)
    assert line266 == ["loaded"]
    assert started.engine_commit == "e" * 40
    assert started.image_digest == "sha256:" + "1" * 64
    assert started.screen_object_sha256 == "5" * 64
    assert started.lockbox_module_sha256 == hashlib.sha256(b"L = 1\n").hexdigest()
    assert started.confirmation_module_sha256 == hashlib.sha256(b"C = 1\n").hexdigest()
    assert started.protocol_hash == hashlib.sha256(inputs["protocol"]).hexdigest()
    assert started.protocol == inputs["protocol"]
    assert started.declaration == inputs["declaration"]
    assert code_ok["posted"] == "9" * 64
    assert code_ok["modules"] == {
        "calibration/c2_lockbox.py": b"L = 1\n",
        "calibration/c2_confirmation.py": b"C = 1\n",
    }
    with pytest.raises(TypeError):
        started.chain_log["protocol_hash"] = "0" * 64  # type: ignore[index]
    with pytest.raises(AttributeError):
        started.engine_commit = "f" * 40  # type: ignore[misc]


@pytest.mark.parametrize(
    "breakage",
    ["module_swapped", "declaration", "protocol", "acceptance", "image", "engine"],
)
def test_a_broken_link_refuses_before_line_266_loads(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    code_ok: dict[str, Any],
    line266: list[str],
    breakage: str,
) -> None:
    inputs = _start_inputs(tmp_path)
    if breakage == "module_swapped":
        (tmp_path / "calibration/c2_confirmation.py").write_bytes(b"C = 2\n")
    elif breakage == "declaration":
        inputs["declaration"] += b" "
    elif breakage == "protocol":
        inputs["protocol"] += b"# edited\n"
    elif breakage == "acceptance":
        inputs["acceptance_record"] = b"{}"
    elif breakage == "image":
        inputs["image_digest"] = "sha256:" + "2" * 64
    else:
        monkeypatch.setattr(cf, "verify_code", lambda *a: {"engine_commit": "f" * 40})
    with pytest.raises(cf.ChainError):
        cf.start(**inputs)
    assert line266 == []


def test_line_266_failing_to_load_refuses_the_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, code_ok: dict[str, Any]
) -> None:
    def broken() -> None:
        raise ImportError("jsonschema placeholder")

    monkeypatch.setattr(cf, "load_line266", broken)
    with pytest.raises(cf.SeedError, match="line 266 did not load: ImportError"):
        cf.start(**_start_inputs(tmp_path))


def test_start_really_loads_line_266(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, code_ok: dict[str, Any]
) -> None:
    monkeypatch.setattr(cf, "_TRIAL_SEED", None)
    cf.start(**_start_inputs(tmp_path))
    assert cf._TRIAL_SEED is not None  # derive_seeds and sealing can now run


# --- the frozen bytecode check with both real modules loaded by this route -------


def test_both_modules_loaded_verified_pass_the_frozen_bytecode_check(
    tmp_path: Path,
) -> None:
    # DESIGN §4 test (R14D3-S-1): a fresh process, caching off, an empty
    # prefix; the real confirmation file loaded by the lockbox's
    # load_verified, then the real lockbox file by the confirmation's copy
    prefix = tmp_path / "pycache"
    prefix.mkdir()
    conf, lock = (
        ROOT / "calibration/c2_confirmation.py",
        ROOT / "calibration/c2_lockbox.py",
    )
    code = f"""
import pathlib, sys
sys.dont_write_bytecode = True
sys.pycache_prefix = {str(prefix)!r}
sys.path[:0] = [{str(ROOT)!r}, {str(ROOT / "src")!r}]
from calibration import c2_lockbox as lb, rundef
cf = lb.load_verified("calibration.c2_confirmation", pathlib.Path({str(conf)!r}),
                      {hashlib.sha256(conf.read_bytes()).hexdigest()!r})
lb2 = cf.load_verified("calibration.c2_lockbox", pathlib.Path({str(lock)!r}),
                       {hashlib.sha256(lock.read_bytes()).hexdigest()!r})
assert sys.modules["calibration.c2_confirmation"] is cf
assert sys.modules["calibration.c2_lockbox"] is lb2
assert cf.start.__code__.co_filename.endswith("c2_confirmation.py")
assert rundef.bytecode_problem() is None, rundef.bytecode_problem()
print("ok")
"""
    out = subprocess.run(
        [sys.executable, "-I", "-c", code], capture_output=True, text=True, check=False
    )
    assert out.stdout.strip() == "ok", out.stderr
