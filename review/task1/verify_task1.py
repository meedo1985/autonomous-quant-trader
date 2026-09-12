"""One-off Task 1 evidence checks; never imported by the runtime package."""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "review/task1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def governance() -> None:
    baseline = json.loads((REVIEW / "protected-before.json").read_text())
    expected = {entry["path"]: entry["sha256"] for entry in baseline}
    inventory = {
        p.relative_to(ROOT).as_posix()
        for area in ("docs", "protocols", "schemas", "specs")
        for p in (ROOT / area).rglob("*")
        if p.is_file() and p != ROOT / "docs/README.md"
    } | {"FROZEN_HASHES.json", "FROZEN_HASHES.json.sha256"}
    assert len(expected) == 28 and inventory == set(expected)
    for path, sha256 in expected.items():
        assert digest(ROOT / path) == sha256, path
    before = json.loads((REVIEW / "pre-task-files.json").read_text())
    for path, sha256 in before.items():
        if path != "README.md":
            assert digest(ROOT / path) == sha256, path
    for path in sorted(inventory):
        if path.endswith(".sha256"):
            sidecar = ROOT / path
            sha256, filename = sidecar.read_text().strip().split(maxsplit=1)
            assert filename == sidecar.stem
            assert digest(sidecar.with_suffix("")) == sha256, path

    constitution = (ROOT / "docs/RESEARCH_CONSTITUTION.md").read_text(encoding="utf-8")
    pattern = r"(\*\*Content hash:\*\* `)([0-9a-f]{64})(`)"
    matches = re.findall(pattern, constitution)
    assert len(matches) == 1
    canonical = re.sub(pattern, r"\1\3", constitution)
    content_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert content_hash == matches[0][1]
    manifest = json.loads((ROOT / "FROZEN_HASHES.json").read_text())
    assert manifest["release"] == "v1.0" and manifest["status"] == "FROZEN"
    assert manifest["constitution_content_hash"] == content_hash
    bindings = {
        "protocol_file_sha256": "protocols/protocol_v1.yaml",
        "cost_model_sha256": "specs/COST_MODEL_v1.md",
        "feature_factory_sha256": "specs/FEATURE_FACTORY_v1.md",
        "benchmark_set_sha256": "specs/CANONICAL_BENCHMARKS_v1.md",
        "backtester_spec_sha256": "specs/BACKTESTER_SPEC_v1.md",
        "threat_model_sha256": "docs/THREAT_MODEL_v1.md",
        "hash_canonicalization_spec_sha256": "schemas/HASH_CANONICALIZATION_v1.md",
    }
    for field, path in bindings.items():
        assert manifest[field] == digest(ROOT / path), field
    protocol = yaml.safe_load((ROOT / "protocols/protocol_v1.yaml").read_text())
    assert protocol["constitution_hash"] == content_hash
    for key in (
        "cost_model",
        "feature_factory",
        "benchmark_set",
        "backtester_spec",
        "threat_model",
        "hash_canonicalization_spec",
    ):
        assert protocol[key + "_hash"] == manifest[key + "_sha256"], key
    assert protocol["feature_factory"]["hash"] == protocol["feature_factory_hash"]
    assert protocol["cost_model"]["hash"] == protocol["cost_model_hash"]
    assert (
        protocol["benchmarks"]["benchmark_set_hash"] == protocol["benchmark_set_hash"]
    )
    assert manifest["hash_canonicalization_spec_sha256"] in constitution

    schemas = sorted((ROOT / "schemas").glob("*.schema.json"))
    assert len(schemas) == 5
    for path in schemas:
        schema = json.loads(path.read_text())
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        Draft202012Validator.check_schema(schema)
    schema = json.loads((ROOT / "schemas/protocol.schema.json").read_text())
    validator = Draft202012Validator(schema)
    validator.validate(protocol)
    assert list(validator.iter_errors({}))
    assert list(validator.iter_errors({**protocol, "status": "UNFROZEN"}))
    print(
        "PASS: 28 protected bytes/inventory; all existing untracked work; 14 sidecars"
    )
    print(
        f"PASS: Constitution canonical hash {content_hash}; manifest/protocol bindings"
    )
    print("PASS: five Draft 2020-12 schemas; protocol instance; two rejection controls")


def configuration() -> None:
    hooks = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
    excluded = re.compile(hooks["exclude"])
    baseline = json.loads((REVIEW / "protected-before.json").read_text())
    assert all(excluded.search(entry["path"]) for entry in baseline)
    for path in ("docs/README.md", "src/aqt/core/paths.py", "README.md"):
        assert not excluded.search(path), path
    assert excluded.search("any/future.sha256")
    ignored = subprocess.run(
        ["git", "check-ignore", "--no-index", ".env", ".env.local", ".env.example"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert ignored.returncode == 0
    assert set(ignored.stdout.splitlines()) == {".env", ".env.local"}
    # BaseLoader preserves GitHub's YAML key 'on' as text, unlike YAML 1.1 booleans.
    ci = yaml.load(
        (ROOT / ".github/workflows/ci.yml").read_text(), Loader=yaml.BaseLoader
    )
    assert set(ci["on"]) == {"pull_request", "push"}
    assert ci["on"]["push"]["branches"] == ["main"]
    assert "continue-on-error" not in (ROOT / ".github/workflows/ci.yml").read_text()
    runs = [step["run"] for step in ci["jobs"]["checks"]["steps"] if "run" in step]
    assert runs == [
        'python -m pip install -e ".[dev]"',
        "ruff format --check .",
        "ruff check .",
        "mypy src",
        "python -m pytest",
        "lint-imports",
    ]
    print("PASS: frozen hook exclusions, README inclusion, env ignore exception, CI")


def boundaries() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text())
    edges = set()
    for contract in config["tool"]["importlinter"]["contracts"]:
        assert contract["type"] == "forbidden"
        assert contract["allow_indirect_imports"] is False
        assert not contract.get("ignore_imports")
        for source in contract["source_modules"]:
            for target in contract["forbidden_modules"]:
                edges.add((source, target))
    required = {
        ("aqt.research", "aqt.governor"),
        ("aqt.research", "aqt.execution"),
        ("aqt.research", "aqt.lockbox_eval"),
        ("aqt.governor", "aqt.execution"),
        ("aqt.governor", "aqt.models"),
        ("aqt.execution", "aqt.models"),
        *(
            (f"aqt.{p}", "aqt.research")
            for p in ("allocation", "governor", "execution", "monitoring")
        ),
    }
    assert required <= edges
    results = []
    # Disposable copies only. No import probes ever enter the user's source tree.
    for source, target in sorted(required):
        for indirect in (False, True):
            with tempfile.TemporaryDirectory(prefix="aqt-task1-import-") as temporary:
                probe = Path(temporary)
                shutil.copytree(
                    ROOT / "src",
                    probe / "src",
                    ignore=shutil.ignore_patterns("__pycache__"),
                )
                shutil.copyfile(ROOT / "pyproject.toml", probe / "pyproject.toml")
                command = [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, 'src'); "
                    "from importlinter.cli import lint_imports_command as run; run()",
                    "--no-cache",
                ]
                control = subprocess.run(
                    command, cwd=probe, capture_output=True, text=True, check=False
                )
                assert control.returncode == 0, control.stdout + control.stderr
                source_path = probe / "src" / source.replace(".", "/") / "probe.py"
                target_path = probe / "src" / target.replace(".", "/") / "probe.py"
                target_path.write_text("", encoding="utf-8")
                if indirect:
                    (probe / "src/aqt/core/bridge.py").write_text(
                        f"import {target}.probe\n", encoding="utf-8"
                    )
                    source_path.write_text("import aqt.core.bridge\n", encoding="utf-8")
                else:
                    source_path.write_text(f"import {target}.probe\n", encoding="utf-8")
                violation = subprocess.run(
                    command, cwd=probe, capture_output=True, text=True, check=False
                )
                assert violation.returncode == 1, violation.stdout + violation.stderr
                assert "BROKEN" in violation.stdout and target in violation.stdout
                results.append(
                    {
                        "source": source,
                        "target": target,
                        "indirect": indirect,
                        "command": command,
                        "cwd": str(probe),
                        "control_exit": control.returncode,
                        "violation_exit": violation.returncode,
                        "output": violation.stdout + violation.stderr,
                    }
                )
    (REVIEW / "boundary-probes.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    print(f"PASS: {len(results)} direct/indirect probes rejected; controls passed")


if __name__ == "__main__":
    governance()
    configuration()
    boundaries()
