"""D-19 run definition (prereg §13 rev 7g item 6), run by the owner on the
calibration machine inside the pinned image.

  record --out PATH --prereg-commit C --engine-commit C
         --cell-manifest FILE --seed-spec FILE --exploration-manifest FILE
      Measure this machine's gating identity and write the run definition;
      prints its SHA-256. The engine code must equal the engine commit (this
      checkout's HEAD) file by file; the preregistration is read from its
      commit. The image digest comes from AQT_IMAGE_DIGEST,
      which the launcher takes from `docker inspect` on the host (FE-4).
  check --definition PATH
      The start gate: run on every start and resume before any chunk.

Synthetic data only; computes no calibration result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"  # method V pinned runtime (VS1-4)
os.environ["OPENBLAS_CORETYPE"] = "Haswell"
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]  # this checkout's code only (RR-2)
# No cached bytecode is read or written: every module runs from its source
# (R6-1; `rundef.bytecode_problem` checks this in the start gate).
sys.dont_write_bytecode = True
sys.pycache_prefix = tempfile.mkdtemp(prefix="d19-no-bytecode-")

from calibration import rundef  # noqa: E402

PREREG_PATH = (
    "review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md"
)


def _git(*args: str) -> bytes:
    """Git without replacement objects (R4-2): `refs/replace` can never stand
    a different tree in for the commit ID that is recorded."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    # No GIT_DIR/GIT_WORK_TREE/... override can point at another repository (R6-2).
    return subprocess.run(["git", "--no-replace-objects", "-C", str(ROOT), *args],
                          capture_output=True, check=True, env=env).stdout  # fmt: skip


def _head() -> str:
    return _git("rev-parse", "--verify", "HEAD^{commit}").decode().strip()


def _checkout_problem(commit: str) -> str | None:
    """Why the engine code here is not exactly `commit`, or None. Compared
    file by file with the commit's own blobs, not through `git status`, so
    index flags and ignore rules cannot hide a change (FE-1, RR-3)."""
    try:
        head = _head()  # one captured ID for every read (R4-2)
        listed = _git("ls-tree", "-r", "--name-only", head, "--", *rundef.CODE_DIRS)
        committed = {
            rel: rundef.canonical_sha256(_git("show", f"{head}:{rel}"))
            for rel in listed.decode().splitlines()
            if rundef.is_code(rel)
        }
    except (OSError, subprocess.CalledProcessError) as error:
        return f"cannot read the checkout with git: {error}"
    if head != commit:
        return f"engine commit {commit} is not this checkout's HEAD {head}"
    present = rundef.code_inventory(ROOT)
    if present != committed:
        differ = sorted(set(present) ^ set(committed)) or sorted(
            rel for rel in present if present[rel] != committed[rel]
        )
        return f"engine code differs from HEAD: {differ[:5]}"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="D-19 run definition")
    sub = parser.add_subparsers(dest="command", required=True)
    record = sub.add_parser("record")
    record.add_argument("--out", type=Path, required=True)
    record.add_argument("--prereg-commit", required=True)
    record.add_argument("--engine-commit", required=True)
    record.add_argument("--cell-manifest", type=Path, required=True)
    record.add_argument("--seed-spec", type=Path, required=True)
    record.add_argument("--exploration-manifest", type=Path, required=True)
    check = sub.add_parser("check")
    check.add_argument("--definition", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "record":
        digest = os.environ.get(rundef.IMAGE_DIGEST_ENV)
        if not digest:
            print(f"{rundef.IMAGE_DIGEST_ENV} is not set", file=sys.stderr)
            return 1
        if (problem := _checkout_problem(args.engine_commit)) is not None:
            print(problem, file=sys.stderr)
            return 1
        try:
            prereg_id = (  # the full commit ID, never a moving name (R3-1)
                _git("rev-parse", "--verify", f"{args.prereg_commit}^{{commit}}")
                .decode()
                .strip()
            )
            prereg = _git("show", f"{prereg_id}:{PREREG_PATH}")
        except (OSError, subprocess.CalledProcessError):
            print(f"cannot read {PREREG_PATH} at {args.prereg_commit}", file=sys.stderr)
            return 1
        code_hash = rundef.generator_sha256(ROOT)
        defn = rundef.build(
            prereg_commit=prereg_id,
            prereg_sha256=hashlib.sha256(prereg).hexdigest(),
            engine_commit=args.engine_commit,
            generator_code_sha256=code_hash,
            cell_manifest=json.loads(args.cell_manifest.read_bytes()),
            seed_spec=json.loads(args.seed_spec.read_bytes()),
            image_digest=digest,
            exploration_manifest_sha256=hashlib.sha256(
                args.exploration_manifest.read_bytes()
            ).hexdigest(),
        )
        # Re-check just before writing (R4-2, R5-2): HEAD, and every engine
        # file against that commit and against the hash being recorded.
        problem = _checkout_problem(args.engine_commit)
        if problem is not None or rundef.generator_sha256(ROOT) != code_hash:
            print(
                f"changed while recording; nothing written: {problem}", file=sys.stderr
            )
            return 1
        rundef.write(args.out, defn)
        print(rundef.definition_sha256(defn))
        return 0
    defn = rundef.load(args.definition)
    try:
        rundef.start_gate(defn, ROOT)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1
    print(f"start gate passed: {rundef.definition_sha256(defn)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
