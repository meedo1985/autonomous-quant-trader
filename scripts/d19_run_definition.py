"""D-19 run definition (prereg §13 rev 7g item 6), run by the owner on the
calibration machine inside the pinned image.

  record --out PATH --prereg-commit C --prereg-file FILE --engine-commit C
         --cell-manifest FILE --seed-spec FILE --exploration-manifest FILE
      Measure this machine's gating identity and write the run definition;
      prints its SHA-256. The engine commit must be this checkout's HEAD with
      no uncommitted change. The image digest comes from AQT_IMAGE_DIGEST,
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
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"  # method V pinned runtime (VS1-4)
os.environ["OPENBLAS_CORETYPE"] = "Haswell"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # the top-level `calibration` package

from calibration import rundef  # noqa: E402


def _checkout_problem(commit: str) -> str | None:
    """Why this checkout is not exactly `commit` (FE-1), or None."""

    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                              text=True, check=True).stdout.strip()  # fmt: skip

    try:
        head, dirty = git("rev-parse", "HEAD"), git("status", "--porcelain")
    except (OSError, subprocess.CalledProcessError) as error:
        return f"cannot read the checkout with git: {error}"
    if head != commit:
        return f"engine commit {commit} is not this checkout's HEAD {head}"
    if dirty:
        return "the checkout has uncommitted changes"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="D-19 run definition")
    sub = parser.add_subparsers(dest="command", required=True)
    record = sub.add_parser("record")
    record.add_argument("--out", type=Path, required=True)
    record.add_argument("--prereg-commit", required=True)
    record.add_argument("--prereg-file", type=Path, required=True)
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
        defn = rundef.build(
            prereg_commit=args.prereg_commit,
            prereg_sha256=hashlib.sha256(args.prereg_file.read_bytes()).hexdigest(),
            engine_commit=args.engine_commit,
            generator_code_sha256=rundef.generator_sha256(ROOT),
            cell_manifest=json.loads(args.cell_manifest.read_bytes()),
            seed_spec=json.loads(args.seed_spec.read_bytes()),
            image_digest=digest,
            exploration_manifest_sha256=hashlib.sha256(
                args.exploration_manifest.read_bytes()
            ).hexdigest(),
        )
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
