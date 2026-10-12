"""The qualification object of preregistration §4, with §13 rev 7g item 6
(freeze order step 5).

The object is a directory of files and `manifest.json`, the SHA-256 of
each file; `qualification_object_sha256` is the SHA-256 of the canonical
manifest (`cj`). `build` refuses, writing nothing, unless:

- every threshold and development chain verifies and its head equals the
  head in `choices.json`, and `choices.json` is byte-identical to a fresh
  `d19_choose.py choose` of the same chains (BO-4: the final cells and
  thresholds come only from the complete chains and the fixed rules);
- the run definition is a qualification run whose preregistration hash
  equals the bytes of the preregistration supplied;
- the method qualifies (§5 step 6) with no margin flag (I1-6);
- the run definition's bytes were committed, at `definition_commit`, before
  the threshold run started (S16-2; the start time is the owner's recorded
  `d19.sh status` line);
- every §4 source file exists, including the §3.6 mapping and the §7.2
  screen (BO-4).

Added for S16-4: per chain, the SHA-256 of the list of its chunks' host
provenance, in chain order. Added for §3.6: each final qualifying cell's
own per-tail order statistics (`cell_thresholds.json`)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from calibration import chunks, generator, reduce, rundef
from calibration.seeds import cj, sha

# object file -> source (§4 contents). ENGINE files come from the run's
# pinned checkout, whose code hash the start gate checks (BO-3); LATER files
# (mapping, screen) are built before the freeze in a later checkout
# (owner decision on the build order, BO-4).
ENGINE = {
    "generator.py": "calibration/generator.py",
    "binomial.py": "calibration/binomial.py",
    "choices_rules.py": "calibration/choices.py",
    "requirements.lock": "deploy/calibration/requirements.lock",
    "Dockerfile": "deploy/calibration/Dockerfile",
}
LATER = {
    "preregistration.md": "review/governance-statistics-amendment/"
    "d19-preregistration/PREREGISTRATION.md",
    "mapping.py": "calibration/mapping.py",
    "screen.py": "calibration/screen.py",
}
NAMESPACES = ("threshold", "dev")


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=True
    ).stdout


def committed_before(
    root: Path, commit: str, path: str, data: bytes, started: datetime
) -> int:
    """S16-2: the committer time of `commit`, which must hold `data` at
    `path` and be earlier than `started` (timezone-aware). ValueError
    otherwise."""
    if started.tzinfo is None:
        raise ValueError("the threshold start time needs a time zone")
    try:
        held = _git(root, "show", f"{commit}:{path}")
        when = int(_git(root, "show", "-s", "--format=%ct", commit))
    except subprocess.CalledProcessError as error:
        raise ValueError(f"S16-2: {commit}:{path} not found") from error
    if held != data:
        raise ValueError(f"S16-2: {commit}:{path} is not this run definition")
    if when >= started.timestamp():
        raise ValueError("S16-2: the run definition was committed after the start")
    return when


def host_sha256(chain: chunks.Chain) -> str:
    """S16-4: the hash of the chain's host provenance list, in chain order."""
    return sha(chunks.hosts(chain))


def manifest_sha256(manifest: dict[str, str]) -> str:
    return hashlib.sha256(cj(manifest)).hexdigest()


def _choose(root: Path, definition: Path, store: Path) -> bytes:
    """A fresh `d19_choose.py choose` of the store (its start gate included)."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "choices.json"
        script = root / "scripts" / "d19_choose.py"
        done = subprocess.run(
            [sys.executable, "-B", str(script), "choose", "--definition",
             str(definition), "--store", str(store), "--out", str(out)],
            capture_output=True, text=True, check=False,
        )  # fmt: skip
        if done.returncode != 0:
            raise ValueError(f"choose failed: {done.stderr.strip()}")
        return out.read_bytes()


def build(
    *,
    root: Path,
    run_root: Path,
    definition: Path,
    definition_repo_path: str,
    definition_commit: str,
    threshold_started: datetime,
    store: Path,
    choices_json: Path,
    exploration_manifest: Path,
    out: Path,
) -> str:
    """Write the object into the empty directory `out`; returns
    `qualification_object_sha256`. `run_root` is the run's pinned checkout
    (its start gate must pass, so the choose and the engine files are the
    run's); `root` is the checkout holding the later files. Refuses
    (ValueError) before writing."""
    data = definition.read_bytes()
    defn = rundef.load(definition)
    if defn["cell_manifest"].get("purpose") != "qualification":
        raise ValueError("not a qualification run")
    prereg = (root / LATER["preregistration.md"]).read_bytes()
    if hashlib.sha256(prereg).hexdigest() != defn["prereg_sha256"]:
        raise ValueError("the preregistration is not the run definition's")
    sources = {n: run_root / s for n, s in ENGINE.items()}
    sources |= {n: root / s for n, s in LATER.items()}
    missing = [str(p) for p in sources.values() if not p.is_file()]
    if missing:
        raise ValueError(f"§4 sources missing: {missing}")
    explore = exploration_manifest.read_bytes()
    if (
        json.loads(explore).get("manifest_sha256")
        != defn["exploration_manifest_sha256"]
    ):
        raise ValueError("the exploration manifest is not the run definition's")

    chosen = choices_json.read_bytes()
    if _choose(run_root, definition, store) != chosen:
        raise ValueError("choices.json is not a fresh choose of these chains")
    report: dict[str, Any] = json.loads(chosen)
    if not (report["qualifies"] is True and report["margin_ok"] is True):
        raise ValueError("the method does not qualify (§5 step 6)")
    committed = committed_before(
        root, definition_commit, definition_repo_path, data, threshold_started
    )

    gating = defn["gating"]  # every chunk carries the run's gating
    cells = generator.cells_from_manifest(defn["cell_manifest"])
    binding = rundef.definition_sha256(defn)
    plan = rundef.run_plan(defn["cell_manifest"])
    hosts: dict[str, str] = {}
    own: dict[str, object] = {}
    for c in cells:
        for ns in NAMESPACES:
            chain = chunks.Chain(store / ns / c.cell_id, binding, ns, c.cell_id,
                                 plan[ns], gating, host={})  # fmt: skip
            if chunks.verify(chain) != report["chain_heads"][f"{ns}/{c.cell_id}"]:
                raise ValueError(f"{ns}/{c.cell_id}: chain head differs from choices")
            hosts[f"{ns}/{c.cell_id}"] = host_sha256(chain)
        names = [c.cell_id]
        if c.law == "semi-joint":
            names = [f"{c.cell_id}/{f}" for f in reduce.FAMILIES]
        threshold = chunks.Chain(store / "threshold" / c.cell_id, binding,
                                 "threshold", c.cell_id, plan["threshold"],
                                 gating, host={})  # fmt: skip
        sets = reduce.cell_thresholds(threshold, c.law == "semi-joint")
        for name, (upper, lower) in zip(names, sets, strict=True):
            if report["cells"][name]["status"] == "qualifying":
                own[name] = {
                    "upper": {k: v.hex() for k, v in upper.items()},
                    "lower": {k: v.hex() for k, v in lower.items()},
                }

    freeze = {
        "definition_sha256": binding,
        "definition_commit": definition_commit,
        "definition_committed_unix": committed,
        "threshold_started": threshold_started.isoformat(),
        "host_provenance_sha256": hosts,
        "alpha_s": generator.ALPHA_S.hex(),
        "allocation": {
            c: r["held_out"]
            for c, r in report["cells"].items()
            if r["status"] == "qualifying"
        },  # fmt: skip
    }
    files = {
        "definition.json": data,
        "choices.json": chosen,
        "exploration_manifest.json": explore,
        "cell_thresholds.json": cj(own),
        "freeze.json": cj(freeze),
        **{name: path.read_bytes() for name, path in sources.items()},
    }
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise ValueError(f"{out} is not empty")
    manifest = {n: hashlib.sha256(b).hexdigest() for n, b in sorted(files.items())}
    for name, content in files.items():
        (out / name).write_bytes(content)
    (out / "manifest.json").write_bytes(cj(manifest))
    return manifest_sha256(manifest)
