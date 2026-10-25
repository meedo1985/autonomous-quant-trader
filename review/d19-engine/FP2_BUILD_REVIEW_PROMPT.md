# Independent adversarial review: FP2, the freeze and held-out launcher commands

You are an independent adversarial reviewer (read-only). You are not an
authority and you cannot approve a merge; the owner's §16 PR review is
separate. Report findings with stable IDs `FP2-R1`, `FP2-R2`, ... each with
severity (BLOCKER / MAJOR / MINOR), the exact place, a concrete failure
scenario, and a proposed repair. Then a verdict: ACCEPT or FIX.

## What to review

Commit `3d6d8ef` on branch `fp2-freeze-launcher` (base `main` `6cd20c8`):
`git diff 6cd20c8 3d6d8ef`, included below. It builds precondition FP2 of the
DRAFT sheet `deploy/calibration/FREEZE_HELDOUT.md` (branch `freeze-sheet`,
PR #76; read it with `git show freeze-sheet:deploy/calibration/FREEZE_HELDOUT.md`):

- `d19.sh freeze`: runs `calibration.qobj.build` (unchanged, `calibration/qobj.py`)
  in the pinned image through the launcher's `engine()`, with the run's
  engine checkout `/opt/aqt-d19/app` (commit `eeaa728`, the threshold and
  development runs' engine) as `run_root`, and a fresh uid-990 clone of a
  second, root-owned build checkout `/opt/aqt-d19/build` (the merged build
  commit) as `root`. `build` fetches the live remote into `root` (QO-2), so
  this is the one engine command started with network (`--network bridge`,
  BUILD-1, a deliberate exception: please judge it).
- `d19.sh heldout <1|2> <posted> <round> <randomness>`, `heldout-status`,
  `certify <1|2> <posted>`: run `scripts/d19_heldout.py` (unchanged) from
  `/app`. `git diff eeaa728 main` touches only `src/aqt/core/deployment.py`,
  so `calibration/`, `scripts/d19_heldout.py` and `scripts/d19_run.py` are
  byte-identical between the run's checkout and main; the object's
  `heldout.py` and `mapping.py` (from `root`) therefore equal the code that
  runs (HO-1).
- `review/d19-engine/FREEZE_REVIEWS.json`: the record `qobj._reviewed` reads
  (BO-4, QO-5): SHA-256 of the committed blobs of `calibration/mapping.py`
  (last changed `0ccf5ef`), `calibration/screen.py` (`f3e3313`),
  `scripts/d19_heldout.py` (`226137a`), each with the Sol ACCEPT record of
  that version. Note: `screen.py`'s review is cumulative over slices S1-S8;
  the record named is the last ACCEPT, of the S8 paths-freeze repair
  `f3e3313`. Judge whether that is a sufficient record for BO-4.
- New `scripts/d19_freeze.py` (CLI over `qobj.build`), tests, and a CI
  dry-run step in the `calibration-launcher` job (the pilot definition must
  be refused with no object written).
- Fixed values in `d19.sh`: `DEFINITION_COMMIT=461ebacb...` (committer time
  1792493569 = 2026-10-20T10:52:49Z) and `THRESHOLD_STARTED=
  2026-10-20T11:00:15.164071663Z` (docker StartedAt, from
  `review/d19-engine/THRESHOLD_RUN_FINISHED_EVIDENCE.md`); Python's
  `fromisoformat` keeps 6 fractional digits (truncation: an earlier start,
  a stricter committed-before check).

Governing text: prereg §4 (object, freeze order steps 5-7), §6, §8, §13 rev
7g items 3 and 6 (P18-6: no held-out content before certify);
`calibration/qobj.py` docstring (QO-1..QO-7, BO-3, BO-4, S16-2);
`scripts/d19_heldout.py` docstring (HO-1..HO-4).

## Questions to answer

1. Can `freeze` publish an object that `qobj.read` or §4 would reject, or
   that is built from anything other than the run's pinned code and the
   merged build commit? Can the clone/chown step touch the build checkout or
   anything outside `/var/lib/aqt-d19`?
2. Is network for `freeze` only, and is it bounded enough? Can any other
   command get network (including through the owner's environment)?
3. Can `heldout`, `heldout-status` or `certify` show held-out event content
   before `certify` (P18-6), run concurrently with another D-19 run, or
   overwrite evidence?
4. Shell correctness under `set -eu` and `sh` (dash): argument checks, exit
   codes (certify's 0/2 passthrough with the report printed), quoting.
5. Anything the FREEZE_HELDOUT.md sheet's FP2 text promises that this build
   does not deliver, or the reverse (the sheet will be updated after this
   review: `heldout` and `certify` now take the posted hash).

## Local checks (Windows laptop, project venv, Python 3.14.7)

- `pytest tests/unit/test_calibration_qobj.py tests/unit/test_d19_deploy.py`: 33 passed
- `ruff check .`: all checks passed; `ruff format --check .`: 177 files formatted
- `lint-imports`: 7 kept, 0 broken
- `sh -n deploy/calibration/d19.sh`: ok
- `mypy src`: unchanged; `mypy tests/unit/test_calibration_qobj.py` shows the
  same 3 errors before and after this change (lines 75, 123, 431, pre-existing)
- Not run here: the CI `calibration-launcher` job (needs Docker and systemd);
  the full calibration suite (laptop memory).

## The diff

```diff
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 4feb191..41d8c59 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -224,6 +224,17 @@ jobs:
           test "$(sudo docker wait aqt-d19)" = 0 || { sudo docker logs aqt-d19; exit 1; }
           sudo sh d19.sh choose
           sudo test -s /var/lib/aqt-d19/choices.json
+          # FP2: freeze starts (build clone, network, its script, the run's
+          # code) and refuses this pilot run, leaving no object
+          sudo git clone --quiet /tmp/app.bundle /opt/aqt-d19/build
+          sudo git -C /opt/aqt-d19/build checkout --quiet "$COMMIT"
+          out=$(sudo sh d19.sh freeze 2>&1) && exit 1
+          echo "$out" | tee /tmp/freeze
+          grep -q "^refused: ValueError: not a qualification run" /tmp/freeze
+          sudo test ! -e /var/lib/aqt-d19/qobj-1
+          test -z "$(sudo find /opt/aqt-d19/build -not -user 0 -print -quit)"
+          sudo sh d19.sh heldout-status
+          ! sudo sh d19.sh certify 1 "$(printf '%064d' 0)"  # no object: refused
           sudo sh d19.sh nonfinite | tee /tmp/nonfinite
           grep -q "^all cells: 0 non-finite of" /tmp/nonfinite
           sudo sh d19.sh clean-check | tee /tmp/clean
diff --git a/deploy/calibration/d19.sh b/deploy/calibration/d19.sh
index 53c0aaf..1b1e5d7 100644
--- a/deploy/calibration/d19.sh
+++ b/deploy/calibration/d19.sh
@@ -22,10 +22,14 @@
 #   sudo sh d19.sh screen-pilot
 #   sudo sh d19.sh screen-status
 #   sudo sh d19.sh screen-summary
+#   sudo sh d19.sh freeze
+#   sudo sh d19.sh heldout <attempt> <posted hash> <round> <randomness>
+#   sudo sh d19.sh heldout-status
+#   sudo sh d19.sh certify <attempt> <posted hash>
 #
-# Every engine process runs in the pinned image, as uid 990, without network,
-# at `nice 19`, inside aqt-d19.slice (systemd MemoryMax 2560M, checked before
-# every start), with the engine's own read-only checkout at /app (never the
+# Every engine process runs in the pinned image, as uid 990, without network
+# (except `freeze`, which reads the live remote, QO-2), at `nice 19`, inside
+# aqt-d19.slice (systemd MemoryMax 2560M, checked before every start), with the engine's own read-only checkout at /app (never the
 # forward-paper one). The image is started by the id that `docker image
 # inspect` reports here, and the same id is AQT_IMAGE_DIGEST: never typed
 # (FE-4, FE4-1). The driver runs exactly 2 workers (scripts/d19_run.py,
@@ -37,6 +41,14 @@ WORK=/var/lib/aqt-d19
 NAME=aqt-d19
 SLICE=aqt-d19.slice
 MEMORY_MAX=2684354560  # 2560M in bytes, as systemd reports it
+NET=none  # only `freeze` changes it (BUILD-1)
+# FP2: the build checkout holding this launcher and the later files; the
+# engine checkout $APP stays at the run's commit
+BUILD=/opt/aqt-d19/build
+# the threshold run's definition commit (FULL_RUN.md step C) and docker's
+# recorded start (THRESHOLD_RUN_FINISHED_EVIDENCE.md)
+DEFINITION_COMMIT=461ebacb4751e1bb5294471a460bdb8549f395b6
+THRESHOLD_STARTED=2026-10-20T11:00:15.164071663Z
 
 tag() { echo "aqt-d19:$(git -C "$APP" rev-parse --verify HEAD)"; }
 
@@ -105,13 +117,14 @@ engine() {  # engine [docker run options...] -- <script> [arguments...]
     shift
     script=$1
     shift
+    case $script in /*) ;; *) script=/app/scripts/$script ;; esac
     # --init: python is not PID 1, so `stop` (SIGTERM) ends it at once.
     # shellcheck disable=SC2086  # $opts is a list of plain flags
-    docker run $opts --label "$LABEL" --init --user 990:990 --network none --read-only \
+    docker run $opts --label "$LABEL" --init --user 990:990 --network "$NET" --read-only \
         --tmpfs /tmp --cgroup-parent "$SLICE" --memory 2560m \
         -e AQT_IMAGE_DIGEST="$id" -e HOME=/tmp \
         -v "$APP:/app:ro" -v "$WORK:/work" -w /work \
-        "$id" nice -n 19 python "/app/scripts/$script" "$@"
+        "$id" nice -n 19 python "$script" "$@"
 }
 
 case "${1:-}" in
@@ -306,8 +319,58 @@ failcheck)  # FR2-2, FE7-7: kill one worker; the run must stop, none survive
     echo "PASS: the run stopped (exit $code) and no worker outlived it"
     docker logs --tail 3 "$NAME" 2>&1
     ;;
+freeze)  # FP2, §4 freeze-order step 5: the qualification object qobj-1. The
+    # run's checkout is run_root; root is a fresh clone of the build checkout,
+    # owned by uid 990 because build fetches the live remote into it (QO-2)
+    [ ! -e "$WORK/qobj-1" ] || { echo "refused: $WORK/qobj-1 exists" >&2; exit 1; }
+    lock  # QO-6: no run going, so the store is quiescent
+    commit=$(git -C "$BUILD" rev-parse --verify HEAD)
+    rm -rf "$WORK/freeze-root"
+    # --no-hardlinks: the chown below must not reach the build checkout's objects
+    git clone --quiet --no-hardlinks --no-checkout "$BUILD" "$WORK/freeze-root"
+    git -C "$WORK/freeze-root" checkout --quiet "$commit"
+    git -C "$WORK/freeze-root" remote set-url origin "$(git -C "$BUILD" remote get-url origin)"
+    chown -R 990:990 "$WORK/freeze-root"
+    NET=bridge  # BUILD-1: the one engine command with network
+    engine --rm -- /work/freeze-root/scripts/d19_freeze.py --run-root /app \
+        --root freeze-root --definition definition.json \
+        --definition-repo-path deploy/calibration/runs/qualification-definition.json \
+        --definition-commit "$DEFINITION_COMMIT" --threshold-started "$THRESHOLD_STARTED" \
+        --store store --choices choices.json \
+        --exploration-manifest manifests/exploration-BTCUSDT-1h.json --out qobj-1
+    ;;
+heldout)  # FP2, §4 step 6: attempt <n>'s held-out run; it prints chain heads
+    # only (P18-6), and a restart resumes
+    case "${2:-}" in 1 | 2) ;; *) echo "usage: d19.sh heldout <1|2> <posted hash> <round> <randomness>" >&2; exit 1 ;; esac
+    [ $# = 5 ] || { echo "usage: d19.sh heldout <1|2> <posted hash> <round> <randomness>" >&2; exit 1; }
+    lock
+    docker rm "$NAME-heldout" >/dev/null 2>&1 || true
+    engine -d --name "$NAME-heldout" -- d19_heldout.py run --object qobj-1 \
+        --posted "$3" --attempt "$2" --round "$4" --randomness "$5" \
+        --store heldout --raw-root raw
+    echo "Started. Progress: sudo sh d19.sh heldout-status"
+    ;;
+heldout-status)  # P18-6: state, times and chunks per chain; nothing else
+    docker ps -a --filter "name=^$NAME-heldout\$" --format '{{.Status}}'
+    docker inspect -f 'started {{.State.StartedAt}} finished {{.State.FinishedAt}} exit {{.State.ExitCode}}' \
+        "$NAME-heldout" 2>/dev/null || true
+    find "$WORK/heldout" -name 'chunk-*.json' 2>/dev/null |
+        awk -F/ '{ n[$(NF-2) "/" $(NF-1)]++ } END { for (c in n) print n[c], c }' |
+        sort -k2
+    ;;
+certify)  # FP2, §6: attempt <n>'s final reduction, once; exit 0 accepted, 2 not
+    case "${2:-}" in 1 | 2) ;; *) echo "usage: d19.sh certify <1|2> <posted hash>" >&2; exit 1 ;; esac
+    [ $# = 3 ] || { echo "usage: d19.sh certify <1|2> <posted hash>" >&2; exit 1; }
+    out=certify-v$2.json
+    [ ! -e "$WORK/$out" ] || { echo "refused: $WORK/$out exists" >&2; exit 1; }
+    rc=0
+    engine --rm -- d19_heldout.py certify --object qobj-1 --posted "$3" \
+        --attempt "$2" --store heldout --out "$out" || rc=$?
+    [ ! -e "$WORK/$out" ] || cat "$WORK/$out"
+    exit "$rc"
+    ;;
 *)
-    sed -n '2,21p' "$0"
+    sed -n '2,28p' "$0"
     exit 1
     ;;
 esac
diff --git a/review/d19-engine/FREEZE_REVIEWS.json b/review/d19-engine/FREEZE_REVIEWS.json
new file mode 100644
index 0000000..c6745aa
--- /dev/null
+++ b/review/d19-engine/FREEZE_REVIEWS.json
@@ -0,0 +1,14 @@
+{
+  "heldout.py": {
+    "record": "review/d19-engine/SOL6_HELDOUT_REREVIEW2_226137A.md",
+    "sha256": "0c484d1ce4cf8176fc7f1c154c82f3b674b329d63fa20c12cc9f0411881301ff"
+  },
+  "mapping.py": {
+    "record": "review/d19-engine/SOL6_MAPPING_REREVIEW2_0CCF5EF.md",
+    "sha256": "f8d8264527818beebe5d2304d3057a172b609397e276f566e7c1f64e88a6de37"
+  },
+  "screen.py": {
+    "record": "review/d19-engine/SOL6_SCREEN_S8_FREEZE_REREVIEW3_FE0D77D.md",
+    "sha256": "8b89432b5486f26cc95c94d8e7fd6c407d9dd3fd00e7b4bd02d1680d205b6cc7"
+  }
+}
diff --git a/scripts/d19_freeze.py b/scripts/d19_freeze.py
new file mode 100644
index 0000000..847959e
--- /dev/null
+++ b/scripts/d19_freeze.py
@@ -0,0 +1,64 @@
+"""D-19 freeze (prereg §4 freeze-order step 5; FREEZE_HELDOUT.md FP2),
+started by the owner's launcher (`d19.sh freeze`) inside the pinned image.
+
+  --run-root DIR --root DIR --definition PATH --definition-repo-path PATH
+  --definition-commit SHA --threshold-started TIME --store DIR
+  --choices PATH --exploration-manifest PATH --out DIR
+
+Calls `calibration.qobj.build` and prints `qualification_object_sha256`, or
+refuses with nothing at `--out`. The `calibration` package is the run's
+pinned checkout's (`--run-root`), as is the fresh `choose` that `build`
+compares with `choices.json`; `--root` is the build checkout that holds the
+later files and the freeze-review record. `build` reads the definition
+commit's branches from the live remote (QO-2), so this is the one D-19
+engine command the launcher starts with network.
+"""
+
+from __future__ import annotations
+
+import argparse
+import sys
+from datetime import datetime
+from pathlib import Path
+
+
+def main(argv: list[str] | None = None) -> int:
+    parser = argparse.ArgumentParser(description="D-19 qualification object")
+    for name in ("--run-root", "--root", "--definition", "--store", "--choices",
+                 "--exploration-manifest", "--out"):  # fmt: skip
+        parser.add_argument(name, type=Path, required=True)
+    for name in (
+        "--definition-repo-path",
+        "--definition-commit",
+        "--threshold-started",
+    ):
+        parser.add_argument(name, required=True)
+    args = parser.parse_args(argv)
+    run_root = args.run_root.resolve()
+    sys.path[:0] = [str(run_root), str(run_root / "src")]  # the run's code only
+    try:
+        from calibration import qobj  # noqa: PLC0415
+
+        digest = qobj.build(
+            root=args.root.resolve(),
+            run_root=run_root,
+            definition=args.definition,
+            definition_repo_path=args.definition_repo_path,
+            definition_commit=args.definition_commit,
+            # docker's nanoseconds: fromisoformat keeps 6 digits (an earlier
+            # time, so a stricter committed-before check)
+            threshold_started=datetime.fromisoformat(args.threshold_started),
+            store=args.store,
+            choices_json=args.choices,
+            exploration_manifest=args.exploration_manifest,
+            out=args.out,
+        )
+    except Exception as error:  # noqa: BLE001 - any failure refuses, nothing published
+        print(f"refused: {type(error).__name__}: {error}", file=sys.stderr)
+        return 1
+    print(f"qualification_object_sha256 {digest}")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/tests/unit/test_calibration_qobj.py b/tests/unit/test_calibration_qobj.py
index df8bde1..b306016 100644
--- a/tests/unit/test_calibration_qobj.py
+++ b/tests/unit/test_calibration_qobj.py
@@ -4,10 +4,13 @@ chains only."""
 from __future__ import annotations
 
 import hashlib
+import importlib.util
 import json
 import subprocess
+import sys
 from datetime import UTC, datetime, timedelta
 from pathlib import Path
+from typing import Any
 
 import pytest
 
@@ -148,6 +151,7 @@ def fakes(monkeypatch: pytest.MonkeyPatch) -> None:
     """Small prescribed counts, so the synthetic chains stay small, and a
     stand-in for the fresh choose (it must equal choices.json), which runs
     the start gate of a real pinned checkout."""
+    monkeypatch.setattr(sys, "path", list(sys.path))  # d19_freeze prepends run_root
     monkeypatch.setattr(rundef, "PRESCRIBED", {"threshold": 3, "dev": 2})
     monkeypatch.setattr(
         qobj, "_choose", lambda r, d, s: (d.parent / "choices.json").read_bytes()
@@ -438,3 +442,57 @@ def test_a_host_change_during_staging_is_refused(
     with pytest.raises(ValueError, match="host provenance changed"):
         qobj.build(**kwargs)
     assert not kwargs["out"].exists()
+
+
+ROOT = Path(__file__).resolve().parents[2]
+_spec = importlib.util.spec_from_file_location(
+    "d19_freeze_under_test", ROOT / "scripts" / "d19_freeze.py"
+)
+assert _spec is not None and _spec.loader is not None
+freeze_cli = importlib.util.module_from_spec(_spec)
+_spec.loader.exec_module(freeze_cli)
+
+
+def _cli_args(kwargs: dict[str, Any], started: str) -> list[str]:
+    names = {"choices_json": "--choices", "threshold_started": "--threshold-started"}
+    return [
+        a
+        for k, v in kwargs.items()
+        for a in (names.get(k, "--" + k.replace("_", "-")),
+                  started if k == "threshold_started" else str(v))
+    ]  # fmt: skip
+
+
+def test_the_freeze_command_prints_the_object_hash(  # FP2
+    tmp_path: Path, fakes: None, capsys: pytest.CaptureFixture[str]
+) -> None:
+    kwargs = _setup(tmp_path)
+    # docker's nanosecond form, as the launcher passes it
+    started = kwargs["threshold_started"].strftime("%Y-%m-%dT%H:%M:%S.%f123Z")
+    assert freeze_cli.main(_cli_args(kwargs, started)) == 0
+    manifest = json.loads((kwargs["out"] / "manifest.json").read_bytes())
+    assert capsys.readouterr().out == (
+        f"qualification_object_sha256 {qobj.manifest_sha256(manifest)}\n"
+    )
+    freeze = json.loads((kwargs["out"] / "freeze.json").read_bytes())
+    assert freeze["threshold_started"] == started[:26] + "+00:00"
+
+
+def test_the_freeze_command_refuses_without_publishing(  # FP2
+    tmp_path: Path, fakes: None, capsys: pytest.CaptureFixture[str]
+) -> None:
+    kwargs = _setup(tmp_path)
+    kwargs["definition_commit"] = "0" * 40
+    assert (
+        freeze_cli.main(_cli_args(kwargs, kwargs["threshold_started"].isoformat())) == 1
+    )
+    assert capsys.readouterr().err.startswith("refused: ValueError: S16-2")
+    assert not kwargs["out"].exists()
+
+
+def test_the_committed_freeze_review_record_covers_the_later_files() -> None:
+    """BO-4, QO-5: the record build reads names each later file as committed
+    here, with a committed review record; a later edit needs a new review."""
+    files = {n: qobj._committed(ROOT, p) for n, p in qobj.LATER.items()}
+    assert None not in files.values()
+    qobj._reviewed(ROOT, files)  # type: ignore[arg-type]
diff --git a/tests/unit/test_d19_deploy.py b/tests/unit/test_d19_deploy.py
index 4882016..c1100bd 100644
--- a/tests/unit/test_d19_deploy.py
+++ b/tests/unit/test_d19_deploy.py
@@ -68,8 +68,13 @@ def test_the_launcher_gates_by_the_inspected_image_and_caps_the_run() -> None:
     assert '-e AQT_IMAGE_DIGEST="$id"' in run
     assert re.search(r'"\$id" nice -n 19 python', run)
     assert launcher.count("AQT_IMAGE_DIGEST=") == 1
+    # BUILD-1: no network, except freeze, which reads the live remote (QO-2)
+    assert re.findall(r"^\s*NET=(\S+)", launcher, re.M) == ["none", "bridge"]
+    freeze = launcher[launcher.index("freeze)") : launcher.index("heldout)")]
+    assert re.search(r"^\s*NET=bridge  #", freeze, re.M)
+    assert "--no-hardlinks" in freeze  # its chown must not reach $BUILD
     flags = [
-        "--network none",
+        '--network "$NET"',
         "--user 990:990",
         "--read-only",
         "--init",
@@ -103,6 +108,9 @@ def test_the_launcher_gates_by_the_inspected_image_and_caps_the_run() -> None:
     probe = launcher[launcher.index("probe)") : launcher.index("copy-raw)")]
     assert re.search(r"^\s*lock\b", probe, re.M)
     assert "flock -n 9" in launcher
+    # P18-6: heldout-status shows state and counts, never logs or content
+    held = launcher[launcher.index("heldout-status)") : launcher.index("certify)")]
+    assert "docker logs" not in held and "cat " not in held
     # S8R2-R3: stop attempts every container before failing
     stop = launcher[launcher.index("stop)") : launcher.index("screen-pilot)")]
     loop = stop[stop.index("for id") : stop.index("done")]
```
