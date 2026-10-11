"""The D-19 calibration image and launcher (prereg §13 rev 7g item 6; FE-4).
The CI job `calibration-launcher` runs the real launcher end to end."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DEPLOY = ROOT / "deploy" / "calibration"


def test_the_image_is_pinned_and_holds_only_the_locked_numpy() -> None:
    dockerfile = (DEPLOY / "Dockerfile").read_text(encoding="utf-8")
    assert re.search(r"^FROM python:3\.14-slim@sha256:[0-9a-f]{64}$", dockerfile, re.M)
    assert "--require-hashes --only-binary :all:" in dockerfile
    assert re.search(r"^USER d19$", dockerfile, re.M)
    lock = (DEPLOY / "requirements.lock").read_text(encoding="utf-8")
    pins = re.findall(r"^([A-Za-z0-9_.-]+)==(\S+)", lock, re.M)
    assert [name for name, _ in pins] == ["numpy"]
    assert len(re.findall(r"--hash=sha256:[0-9a-f]{64}", lock)) >= 1


def test_the_engine_loads_no_third_party_package_but_numpy() -> None:
    """Otherwise the image would lack it."""
    code = (
        "import importlib, pkgutil, sys\n"
        "sys.path[:0] = ['.', 'src']\n"
        "import calibration\n"
        "for m in pkgutil.iter_modules(calibration.__path__):\n"
        "    importlib.import_module('calibration.' + m.name)\n"
        "import aqt.data.klines, aqt.data.manifest, aqt.data.binance_public\n"
        "names = {n.split('.')[0] for n in sys.modules}\n"
        "print(sorted(names - set(sys.stdlib_module_names)"
        " - {'calibration', 'aqt', '__main__'}))\n"
    )
    done = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True,
                          text=True, check=True)  # fmt: skip
    assert done.stdout.strip() == "['numpy']"


def test_the_launcher_gates_by_the_inspected_image_and_caps_the_run() -> None:
    launcher = (DEPLOY / "d19.sh").read_text(encoding="utf-8")
    # FE-4, FE4-1: one id from the host's inspection, never typed; the same
    # id is both AQT_IMAGE_DIGEST and the image docker starts.
    ids = re.findall(r"^\s*id=(.*)$", launcher, re.M)  # engine() and probe
    assert ids and set(ids) == {
        """$(docker image inspect --format '{{.Id}}' "$(tag)")"""
    }
    run = launcher[launcher.index("    docker run $opts") :]
    run = run[: run.index("\n}")]
    assert '-e AQT_IMAGE_DIGEST="$id"' in run
    assert re.search(r'"\$id" nice -n 19 python', run)
    assert launcher.count("AQT_IMAGE_DIGEST=") == 1
    flags = [
        "--network none",
        "--user 990:990",
        "--read-only",
        "--init",
        '--cgroup-parent "$SLICE"',
        "--memory 2560m",
        '"$APP:/app:ro"',
    ]
    for flag in flags:
        assert flag in run, flag
    assert "/opt/aqt/" not in launcher  # never the forward-paper checkout
    assert "umask 022" in launcher  # FE4-4
    # FE4-2: every start first checks the systemd cap and slice placement.
    assert re.search(r'^\s*capped "\$id"$', launcher, re.M)
    assert "MEMORY_MAX=2684354560" in launcher and 2560 * 2**20 == 2684354560
    slice_ = (DEPLOY / "aqt-d19.slice").read_text(encoding="utf-8")
    assert re.search(r"^MemoryMax=2560M$", slice_, re.M)
    # FE4-5, P18-6: status shows state and counts, never logs or content.
    status = launcher[launcher.index("status)") : launcher.index("stop)")]
    assert "docker logs" not in status and "cat " not in status


@pytest.mark.skipif(shutil.which("sh") is None, reason="no POSIX sh")
def test_the_launcher_is_valid_sh() -> None:
    subprocess.run(["sh", "-n", str(DEPLOY / "d19.sh")], check=True)


def test_the_re_pilot_manifest_is_a_valid_pilot_covering_every_group() -> None:
    """FE-7: one cell of each group Q1-Q5 and QJ, and every cell of the thin
    categories (Q1 clusters, Q2m, QJ); a pilot by its ids and counts (FA-1)."""
    import json

    sys.path[:0] = [str(ROOT), str(ROOT / "src")]
    from calibration import choices, rundef
    from calibration.generator import cells_from_manifest

    manifest = json.loads((DEPLOY / "pilot-cells.json").read_text(encoding="utf-8"))
    cells = cells_from_manifest(manifest)
    assert rundef.run_plan(manifest) == {"threshold": 2000, "dev": 1000}
    laws = {c.law for c in cells}
    assert {"gaussian", "unequal", "mixed_ar", "semi-trend", "semi-vol",
            "semi-joint"} <= laws and laws & set(choices.Q2_LAWS)  # fmt: skip
    assert ("garch", "factor") in {(c.law, c.dependence) for c in cells}  # Q3
    assert ("gaussian", "clusters") in {(c.law, c.dependence) for c in cells}
    assert {c.t for c in cells} == {1247}
    # FE7-1: every cell of each thin category (prereg §13 item 3)
    from calibration import grid

    for law, dep in (("gaussian", "clusters"), ("unequal", "independent"),
                     ("semi-joint", "independent")):  # fmt: skip
        ks = sorted(k for la, de, k in grid.GRID if (la, de) == (law, dep))
        assert sorted(c.k for c in cells if (c.law, c.dependence) == (law, dep)) == ks


def test_the_pilot_checks_count_non_finite_diagnostics_and_compare_stores(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """FE7-5: only threshold diagnostic values, per family for QJ; FE7-2:
    two stores' threshold chains equal or not."""
    import importlib.util
    import json
    import struct

    spec = importlib.util.spec_from_file_location(
        "d19_pilot_checks", ROOT / "scripts" / "d19_pilot_checks.py"
    )
    assert spec is not None and spec.loader is not None
    checks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checks)

    def hx(x: float) -> str:
        return struct.pack(">d", x).hex()

    def chunk(store: Path, cell: str, results: list[object], sha: str) -> None:
        d = store / "threshold" / cell
        d.mkdir(parents=True, exist_ok=True)
        record = {"content_sha256": sha, "results": results}
        (d / "chunk-0000000.json").write_text(json.dumps(record))

    plain = [{"g2": hx(1.0), "K": hx(2.0)}, {"g2": hx(float("nan")), "K": hx(2.0)}]
    qj = [{"trend": {"g2": hx(float("inf"))}, "vol": {"g2": hx(-1.0)}}]
    a, b = tmp_path / "a", tmp_path / "b"
    for store in (a, b):
        chunk(store, "pilot-x", plain, "s1")
        chunk(store, "pilot-qj", qj, "s2")
        (store / "threshold" / ".locks").mkdir()  # the chains' lock files (FA-3)
    assert checks.main(["nonfinite", str(a)]) == 0
    out = capsys.readouterr().out
    assert "pilot-x: 1 non-finite of 4" in out and "pilot-qj: 1 non-finite of 2" in out
    assert "all cells: 2 non-finite of 6" in out
    assert checks.main(["compare", str(a), str(b)]) == 0
    chunk(b, "pilot-x", plain[:1], "s1")
    assert checks.main(["compare", str(a), str(b)]) == 1
    with pytest.raises(SystemExit, match="no threshold chains"):
        checks.main(["nonfinite", str(tmp_path / "empty")])
