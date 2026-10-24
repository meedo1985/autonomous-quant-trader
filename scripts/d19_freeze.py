"""D-19 freeze (prereg §4 freeze-order step 5; FREEZE_HELDOUT.md FP2),
started by the owner's launcher (`d19.sh freeze`) inside the pinned image.

  --run-root DIR --root DIR --definition PATH --definition-repo-path PATH
  --definition-commit SHA --threshold-started TIME --store DIR
  --choices PATH --exploration-manifest PATH --out DIR

Calls `calibration.qobj.build` and prints `qualification_object_sha256`, or
refuses with nothing at `--out`. The `calibration` package is the run's
pinned checkout's (`--run-root`), as is the fresh `choose` that `build`
compares with `choices.json`; `--root` is the build checkout that holds the
later files and the freeze-review record. `build` reads the definition
commit's branches from the live remote (QO-2), so this is the one D-19
engine command the launcher starts with network.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="D-19 qualification object")
    for name in ("--run-root", "--root", "--definition", "--store", "--choices",
                 "--exploration-manifest", "--out"):  # fmt: skip
        parser.add_argument(name, type=Path, required=True)
    for name in (
        "--definition-repo-path",
        "--definition-commit",
        "--threshold-started",
    ):
        parser.add_argument(name, required=True)
    args = parser.parse_args(argv)
    run_root = args.run_root.resolve()
    sys.path[:0] = [str(run_root), str(run_root / "src")]  # the run's code only
    try:
        from calibration import qobj  # noqa: PLC0415

        digest = qobj.build(
            root=args.root.resolve(),
            run_root=run_root,
            definition=args.definition,
            definition_repo_path=args.definition_repo_path,
            definition_commit=args.definition_commit,
            # docker's nanoseconds: fromisoformat keeps 6 digits (an earlier
            # time, so a stricter committed-before check)
            threshold_started=datetime.fromisoformat(args.threshold_started),
            store=args.store,
            choices_json=args.choices,
            exploration_manifest=args.exploration_manifest,
            out=args.out,
        )
    except Exception as error:  # noqa: BLE001 - any failure refuses, nothing published
        print(f"refused: {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(f"qualification_object_sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
