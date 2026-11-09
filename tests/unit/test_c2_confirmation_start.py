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
    "breakage", ["module_swapped", "declaration", "protocol", "acceptance"]
)
def test_a_broken_chain_link_refuses_before_line_266_loads(
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
    else:
        inputs["acceptance_record"] = b"{}"
    with pytest.raises(cf.ChainError):
        cf.start(**inputs)
    assert line266 == []


@pytest.mark.parametrize("breakage", ["image", "engine", "code"])
def test_a_failure_after_line_266_loads_clears_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, breakage: str
) -> None:
    inputs = _start_inputs(tmp_path)
    engine = "f" * 40 if breakage == "engine" else "e" * 40

    def verify_code(*_: Any) -> Any:
        if breakage == "code":
            raise cf.ChainError("the qualification object is not the posted one")
        return {"engine_commit": engine}

    if breakage == "image":
        inputs["image_digest"] = "sha256:" + "2" * 64
    monkeypatch.setattr(cf, "verify_code", verify_code)
    with pytest.raises(cf.ChainError):
        cf.start(**inputs)
    assert cf._TRIAL_SEED is None  # no seed derivation after a refused start


def test_the_code_check_runs_after_line_266_is_loaded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # R14S6A-S-1: R-14's loaded-module inventory must see line 266's modules
    seen: list[tuple[bool, bool]] = []

    def verify_code(*_: Any) -> Any:
        seen.append(
            (cf._TRIAL_SEED is not None, "aqt.core.preregistration" in sys.modules)
        )
        return {"engine_commit": "e" * 40}

    monkeypatch.setattr(cf, "_TRIAL_SEED", None)
    monkeypatch.setattr(cf, "verify_code", verify_code)
    cf.start(**_start_inputs(tmp_path))
    assert seen == [(True, True)]


def test_in_a_fresh_process_line_266_is_loaded_before_the_code_check(
    tmp_path: Path,
) -> None:
    # R14S6A-S-1, as at a real start: preregistration is not yet imported
    code = f"""
import hashlib, pathlib, sys
sys.path[:0] = [{str(ROOT)!r}, {str(ROOT / "src")!r}]
from calibration import c2_confirmation as cf
from calibration.seeds import cj
from tests.unit.test_c2_lockbox_chain import F_TXID, _acceptance, _post
assert "aqt.core.preregistration" not in sys.modules
root = pathlib.Path({str(tmp_path)!r})
files = {{"lockbox_module_sha256": b"L = 1\\n",
          "confirmation_module_sha256": b"C = 1\\n"}}
for row, data in files.items():
    (root / cf.MODULE_PATHS[row]).parent.mkdir(parents=True, exist_ok=True)
    (root / cf.MODULE_PATHS[row]).write_bytes(data)
values = {{"outpoint_F": F_TXID + ":1",
          **{{r: hashlib.sha256(d).hexdigest() for r, d in files.items()}},
          "engine_commit": "e" * 40, "screen_object_sha256": "5" * 64,
          "qualification_object_sha256": "9" * 64,
          "image_digest": "sha256:" + "1" * 64}}
protocol = "".join(f'  {{k}}: "{{v}}"\\n' for k, v in values.items()).encode()
declaration = cj({{"protocol_hash": hashlib.sha256(protocol).hexdigest()}})
post = _post(hashlib.sha256(declaration).hexdigest())
seen = []
def verify_code(*a):
    seen.append("aqt.core.preregistration" in sys.modules)
    return {{"engine_commit": "e" * 40}}
cf.verify_code = verify_code
cf.start(root=root, obj=root / "obj", acceptance_record=_acceptance(post),
         post_raw_tx=post, declaration=declaration, protocol=protocol,
         image_digest="sha256:" + "1" * 64)
assert seen == [True], seen
assert "jsonschema" not in sys.modules  # the placeholders are gone again
print("ok")
"""
    out = subprocess.run(
        [sys.executable, "-I", "-c", code], capture_output=True, text=True, check=False
    )
    assert out.stdout.strip() == "ok", out.stderr


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


# --- R14S6A-S-2: the loader executes the hashed bytes, and the refusals ---------


@pytest.mark.parametrize("module", [cf, lb], ids=["confirmation", "lockbox"])
def test_a_file_swapped_after_the_hash_is_not_what_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, module: Any
) -> None:
    # DESIGN §4: the file is replaced on disk between the hash check and
    # execution; a loader that read the file again (exec_module) would run B
    path = tmp_path / "c2_swap_probe.py"
    path.write_bytes(b"VALUE = 'A'\n")
    digest = hashlib.sha256(b"VALUE = 'A'\n").hexdigest()
    real = compile

    def swapping(source: Any, filename: str, mode: str) -> Any:
        path.write_bytes(b"VALUE = 'B'\n")  # after the read and the hash
        return real(source, filename, mode)

    monkeypatch.setattr(module, "compile", swapping, raising=False)
    name = f"c2_swap_probe_{module.__name__.rsplit('.', 1)[-1]}"
    try:
        loaded = module.load_verified(name, path, digest)
        assert loaded.VALUE == "A"
        assert path.read_bytes() == b"VALUE = 'B'\n"
    finally:
        sys.modules.pop(name, None)


def _fresh(code: str, prefix: Path) -> str:
    script = f"""
import pathlib, sys
sys.dont_write_bytecode = True
sys.pycache_prefix = {str(prefix)!r}
sys.path[:0] = [{str(ROOT)!r}, {str(ROOT / "src")!r}]
from calibration import c2_confirmation as cf, rundef
{code}
"""
    out = subprocess.run(
        [sys.executable, "-I", "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert not out.stderr.strip() or "Traceback" not in out.stderr, out.stderr
    return out.stdout.strip()


def test_a_non_empty_bytecode_cache_is_refused(tmp_path: Path) -> None:
    prefix = tmp_path / "pycache"
    (prefix / "x").mkdir(parents=True)
    (prefix / "x" / "stale.cpython-314.pyc").write_bytes(b"\0" * 16)
    assert _fresh("print(rundef.bytecode_problem())", prefix) == (
        "the bytecode cache directory is not empty"
    )


def test_a_module_run_from_a_planted_pyc_is_refused(tmp_path: Path) -> None:
    prefix = tmp_path / "pycache"
    prefix.mkdir()
    pyc = tmp_path / "planted.pyc"
    code = f"""
import importlib.machinery, importlib.util, marshal
body = marshal.dumps(compile("V = 1", "p", "exec"))
data = importlib.util.MAGIC_NUMBER + bytes(12) + body
pathlib.Path({str(pyc)!r}).write_bytes(data)
loader = importlib.machinery.SourcelessFileLoader(
    "calibration.c2_planted", {str(pyc)!r})
spec = importlib.util.spec_from_loader("calibration.c2_planted", loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)
sys.modules["calibration.c2_planted"] = m
print(rundef.bytecode_problem())
"""
    assert (
        _fresh(code, prefix) == "calibration.c2_planted was not loaded from its source"
    )


def test_verify_code_refuses_a_third_loaded_module(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # DESIGN §4 (c): the two module files are the only additions; an extra
    # loaded calibration module whose bytes are not the engine's is refused by
    # the frozen check_screen_code through cf.verify_code
    import json

    from calibration import mapping, qobj, rundef, screen
    from calibration.seeds import sha

    files = {"mapping.py": b"m", "screen.py": b"s", "definition.json": b"{}"}
    for name, data in files.items():
        (tmp_path / name).write_bytes(data)
    manifest = {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}
    (tmp_path / "manifest.json").write_bytes(json.dumps(manifest).encode())
    engine = {"calibration/engine.py": b"E = 1\n"}
    inventory = {k: rundef.canonical_sha256(v) for k, v in engine.items()}
    defn = {"engine_commit": "e" * 40, "generator_sha256": sha(inventory)}
    monkeypatch.setattr(qobj, "read", lambda f: (None, defn))
    monkeypatch.setattr(mapping, "check_runtime", lambda d: None)
    monkeypatch.setattr(rundef, "bytecode_problem", lambda: None)  # tested above

    def git(root: Path, *args: str) -> bytes:
        if args[0] == "ls-tree":
            return "\n".join(engine).encode()
        return engine[args[-1].split(":", 1)[1]]

    monkeypatch.setattr(mapping, "_git", git)
    modules = {
        "calibration/c2_lockbox.py": b"L\n",
        "calibration/c2_confirmation.py": b"C\n",
    }
    disk = {}
    for rel, data in {**engine, **modules, "calibration/c2_extra.py": b"X\n"}.items():
        disk[rel] = tmp_path / rel.replace("/", "_")
        disk[rel].write_bytes(data)
    loaded = {rel: disk[rel] for rel in [*engine, *modules]}
    monkeypatch.setattr(mapping, "loaded", lambda: loaded)
    assert cf.verify_code(tmp_path, sha(manifest), ROOT, modules) == defn
    loaded["calibration/c2_extra.py"] = disk["calibration/c2_extra.py"]
    with pytest.raises(ValueError, match="the loaded calibration/c2_extra.py"):
        cf.verify_code(tmp_path, sha(manifest), ROOT, modules)
    assert screen.check_screen_code is not None
