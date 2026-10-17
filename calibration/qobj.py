"""The qualification object of preregistration §4, with §13 rev 7g item 6
(freeze order step 5).

The object is a directory of files and `manifest.json`, the SHA-256 of
each file; `qualification_object_sha256` is the SHA-256 of the canonical
manifest (`cj`). `build` refuses, publishing nothing, unless:

- every threshold and development chain verifies, before and after the
  object's contents are taken (QO-6), with the heads in `choices.json`, and
  `choices.json` is byte-identical to a fresh `d19_choose.py choose` run in
  the run's pinned checkout (BO-3, BO-4, QO-3): the final cells, the
  thresholds, every unit's own order statistics and `alpha_s` come only
  from the complete chains, the fixed rules and the pinned engine;
- the run definition is a qualification run at the prescribed counts
  (QO-1) whose preregistration hash equals the preregistration supplied;
- the method qualifies (§5 step 6) with no margin flag (I1-6), and the
  report holds every §4 result item (QO-4);
- the run definition's bytes were committed, at `definition_commit`, before
  the recorded threshold start, and that commit is on a remote branch
  (S16-2, QO-2). Both times are attestations: the committer time and the
  owner's recorded `d19.sh status` start. A public timestamp of the
  definition hash before the run would be stronger evidence;
- every later file (mapping, screen, held-out runner) is listed in the
  committed freeze-review record with its SHA-256 and an existing review
  record (BO-4, QO-5).

Added for S16-4: per chain, the SHA-256 of the list of its chunks' host
provenance, in chain order. The object is written to a staging directory
and renamed into place only when complete (QO-7)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from calibration import chunks, generator, rundef
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
    "heldout.py": "scripts/d19_heldout.py",
}
REVIEWED = ("mapping.py", "screen.py", "heldout.py")  # BO-4, QO-5
FREEZE_REVIEWS = "review/d19-engine/FREEZE_REVIEWS.json"
# §4 result items choose must report (QO-4)
REPORT = ("cells", "m", "tests", "targets", "family_block_rule", "z_crit",
          "final_thresholds", "cell_bounds", "alpha_s", "chain_heads")  # fmt: skip
NAMESPACES = ("threshold", "dev")


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=True
    ).stdout


def _on_remote(root: Path, commit: str, remote: str) -> bool:
    """Whether a branch of the live `remote` contains `commit` (QO-2: its
    refs are listed from the remote itself, then fetched, not read from
    local tracking refs)."""
    lines = _git(root, "ls-remote", "--heads", remote).decode().splitlines()
    _git(root, "fetch", "-q", remote, *(ln.split()[1] for ln in lines))
    return any(
        subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor", commit,
             ln.split()[0]], capture_output=True, check=False,
        ).returncode == 0
        for ln in lines
    )  # fmt: skip


def committed_before(
    root: Path,
    commit: str,
    path: str,
    data: bytes,
    started: datetime,
    remote: str = "origin",
) -> int:
    """S16-2: the committer time of `commit`, which must hold `data` at
    `path`, be on a remote branch and be earlier than `started`
    (timezone-aware). ValueError otherwise."""
    if started.tzinfo is None:
        raise ValueError("the threshold start time needs a time zone")
    try:
        held = _git(root, "show", f"{commit}:{path}")
        when = int(_git(root, "show", "-s", "--format=%ct", commit))
    except subprocess.CalledProcessError as error:
        raise ValueError(f"S16-2: {commit}:{path} not found") from error
    if held != data:
        raise ValueError(f"S16-2: {commit}:{path} is not this run definition")
    try:
        on_remote = _on_remote(root, commit, remote)
    except subprocess.CalledProcessError as error:
        raise ValueError(f"S16-2: cannot read the remote {remote}") from error
    if not on_remote:
        raise ValueError(f"S16-2: {commit} is on no branch of {remote} (QO-2)")
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


def _chains(defn: dict[str, Any], store: Path) -> dict[str, chunks.Chain]:
    counts = defn["cell_manifest"]["replications"]
    binding = rundef.definition_sha256(defn)
    return {
        f"{ns}/{c.cell_id}": chunks.Chain(store / ns / c.cell_id, binding, ns,
                                          c.cell_id, counts[ns], defn["gating"],
                                          host={})
        for c in generator.cells_from_manifest(defn["cell_manifest"])
        for ns in NAMESPACES
    }  # fmt: skip


def _heads(chains: dict[str, chunks.Chain], expected: dict[str, str]) -> None:
    for key, chain in chains.items():
        if chunks.verify(chain) != expected.get(key):
            raise ValueError(f"{key}: chain head differs from choices")


def _committed(root: Path, path: str) -> bytes | None:
    """The regular file `path` as committed at HEAD in `root`, or None
    (QO-5): a directory, a symbolic link, a missing path or an empty name is
    not a committed file (QOR2-2, QOR3-1: git stores a link as a blob too,
    so the tree entry's mode is checked)."""
    entry = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "HEAD", "--", f":(literal){path}"],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    lines = entry.stdout.splitlines()
    if not path or entry.returncode != 0 or len(lines) != 1:
        return None
    meta, _, name = lines[0].partition("\t")
    fields = meta.split()
    if name != path or len(fields) != 3:  # QOR4-1: exactly this path
        return None
    mode, kind, obj = fields
    if kind != "blob" or mode not in ("100644", "100755"):
        return None
    return _git(root, "cat-file", "blob", obj)


def _reviewed(root: Path, files: dict[str, bytes]) -> None:
    """BO-4, QO-5: each later file, as committed at HEAD, is in the committed
    freeze-review record with its SHA-256 and a committed review record."""
    for name, path in LATER.items():
        if _committed(root, path) != files[name]:
            raise ValueError(f"QO-5: {path} is not committed as it stands")
    raw = _committed(root, FREEZE_REVIEWS)
    record = json.loads(raw) if raw is not None else {}
    for name in REVIEWED:
        entry = record.get(name, {})
        if entry.get("sha256") != hashlib.sha256(files[name]).hexdigest():
            raise ValueError(f"BO-4: {name} is not the reviewed version")
        if _committed(root, str(entry.get("record", ""))) is None:
            raise ValueError(f"BO-4: {name} has no committed review record")


def read(files: dict[str, bytes]) -> tuple[dict[str, Any], dict[str, Any]]:
    """S16SR-1: what a reader can re-check of `build`'s refusals from the
    object's own (manifest-checked) files, without the run's store: exactly
    the built file set, a qualification run at the prescribed counts, the
    preregistration and exploration manifest the definition names, every §4
    report item with M tests of the cell manifest, one known status per unit,
    a qualifying method, and the freeze's definition hash and allocation.
    Returns (choices report, definition); ValueError otherwise."""
    from calibration import choices, reduce  # noqa: PLC0415

    built = set(ENGINE) | set(LATER)
    built |= {"definition.json", "choices.json", "exploration_manifest.json"}
    if set(files) != built | {"freeze.json"}:
        raise ValueError("the object's files are not the qualification object's")
    defn: dict[str, Any] = json.loads(files["definition.json"])
    manifest_ = defn["cell_manifest"]
    if manifest_.get("purpose") != "qualification":
        raise ValueError("not a qualification run")
    if manifest_.get("replications") != rundef.PRESCRIBED:
        raise ValueError(f"not the prescribed counts {rundef.PRESCRIBED}")
    prereg = hashlib.sha256(files["preregistration.md"]).hexdigest()
    if prereg != defn["prereg_sha256"]:
        raise ValueError("the preregistration is not the run definition's")
    explore = json.loads(files["exploration_manifest.json"])
    if explore.get("manifest_sha256") != defn["exploration_manifest_sha256"]:
        raise ValueError("the exploration manifest is not the run definition's")
    report: dict[str, Any] = json.loads(files["choices.json"])
    if absent := [k for k in REPORT if k not in report]:
        raise ValueError(f"choices.json lacks §4 items: {absent}")
    cells = generator.cells_from_manifest(manifest_)
    tests = choices.test_manifest([(c.cell_id, c.law) for c in cells])
    if report["tests"] != tests or report["m"] != len(tests):
        raise ValueError("the test manifest is not the cell manifest's")
    units = {
        u
        for c in cells
        for u in (
            [f"{c.cell_id}/{f}" for f in reduce.FAMILIES]
            if c.law == "semi-joint"
            else [c.cell_id]
        )
    }
    statuses = ("qualifying", "demoted_availability", "demoted_cap")  # choices.py
    if set(report["cells"]) != units or any(
        r.get("status") not in statuses for r in report["cells"].values()
    ):
        raise ValueError("choices.json needs one known status per manifest unit")
    if not (report.get("qualifies") is True and report.get("margin_ok") is True):
        raise ValueError("the method does not qualify (§5 step 6)")
    freeze = json.loads(files["freeze.json"])
    final = {
        u: r["held_out"]
        for u, r in report["cells"].items()
        if r["status"] == "qualifying"
    }
    if freeze.get("definition_sha256") != rundef.definition_sha256(defn):
        raise ValueError("the freeze is not the run definition's")
    if freeze.get("allocation") != final or set(final.values()) - set(choices.HELD_OUT):
        raise ValueError("the allocation is not the final cells' 20k/40k")
    return report, defn


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
    remote: str = "origin",
) -> str:
    """Write the object to the new directory `out`; returns
    `qualification_object_sha256`. `run_root` is the run's pinned checkout
    (its start gate must pass, so the choose and the engine files are the
    run's); `root` is the checkout holding the later files. Refuses
    (ValueError) with nothing at `out`."""
    stage = out.with_name(out.name + ".partial")
    if out.exists() or stage.exists():
        raise ValueError(f"{out} or its staging directory already exists")
    data = definition.read_bytes()
    defn = rundef.load(definition)
    manifest_ = defn["cell_manifest"]
    if manifest_.get("purpose") != "qualification":
        raise ValueError("not a qualification run")
    if manifest_.get("replications") != rundef.PRESCRIBED:  # QO-1
        raise ValueError(f"not the prescribed counts {rundef.PRESCRIBED}")
    sources = {n: run_root / s for n, s in ENGINE.items()}
    sources |= {n: root / s for n, s in LATER.items()}
    missing = [str(p) for p in sources.values() if not p.is_file()]
    if missing:
        raise ValueError(f"§4 sources missing: {missing}")
    files = {name: path.read_bytes() for name, path in sources.items()}
    prereg = files["preregistration.md"]
    if hashlib.sha256(prereg).hexdigest() != defn["prereg_sha256"]:
        raise ValueError("the preregistration is not the run definition's")
    _reviewed(root, files)
    explore = exploration_manifest.read_bytes()
    recorded = defn["exploration_manifest_sha256"]
    if json.loads(explore).get("manifest_sha256") != recorded:
        raise ValueError("the exploration manifest is not the run definition's")

    chosen = choices_json.read_bytes()
    report: dict[str, Any] = json.loads(chosen)
    if absent := [k for k in REPORT if k not in report]:
        raise ValueError(f"choices.json lacks §4 items: {absent}")
    if len(report["tests"]) != report["m"]:
        raise ValueError("the test manifest does not hold M tests")
    chains = _chains(defn, store)
    _heads(chains, report["chain_heads"])
    if _choose(run_root, definition, store) != chosen:
        raise ValueError("choices.json is not a fresh choose of these chains")
    if not (report["qualifies"] is True and report["margin_ok"] is True):
        raise ValueError("the method does not qualify (§5 step 6)")
    committed = committed_before(
        root, definition_commit, definition_repo_path, data, threshold_started, remote
    )
    hosts = {key: host_sha256(chain) for key, chain in chains.items()}

    freeze = {
        "definition_sha256": rundef.definition_sha256(defn),
        "definition_commit": definition_commit,
        "definition_committed_unix": committed,
        "threshold_started": threshold_started.isoformat(),
        "host_provenance_sha256": hosts,
        "allocation": {
            c: r["held_out"]
            for c, r in report["cells"].items()
            if r["status"] == "qualifying"
        },  # fmt: skip
    }
    files |= {
        "definition.json": data,
        "choices.json": chosen,
        "exploration_manifest.json": explore,
        "freeze.json": cj(freeze),
    }
    manifest = {n: hashlib.sha256(b).hexdigest() for n, b in sorted(files.items())}
    stage.mkdir(parents=True)
    for name, content in files.items():
        (stage / name).write_bytes(content)
    (stage / "manifest.json").write_bytes(cj(manifest))
    for name, digest in manifest.items():  # QO-7: verify, then publish
        if hashlib.sha256((stage / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"staged {name} does not match its hash")
    # QO-6: the chains and their host lists, unchanged since they were read,
    # just before publishing. The freeze needs a stopped run (a quiescent
    # store); a change after this check is outside what a reader can see.
    _heads(chains, report["chain_heads"])
    if hosts != {key: host_sha256(chain) for key, chain in chains.items()}:
        raise ValueError("host provenance changed during the build")
    stage.rename(out)
    return manifest_sha256(manifest)
