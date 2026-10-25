# Independent adversarial re-review: FP2 repairs at 421e3b3

You are an independent adversarial reviewer (read-only), not an authority;
the owner's §16 PR review is separate. Your first review of `3d6d8ef`
(`review/d19-engine/ASTRA_FP2_BUILD_REVIEW_3D6D8EF.md`) found FP2-R1 and
FP2-R2. The implementer's adjudication is
`review/d19-engine/ADJUDICATION_FP2_BUILD_3D6D8EF.md` (included below), and
the repairs are `git diff efe2370 421e3b3` (included below).

Check: (1) is each finding resolved, or, for FP2-R2 part (b), correctly
deferred to the sheet change (PR #76) as an open precondition; (2) do the
repairs introduce any new defect (shell under `set -eu` and dash, the
`find ... -perm /022` and ownership check, `git status` as root, the CI
`if cmd; then exit 1; fi` checks); (3) are the items marked "not repaired"
acceptable as disclosed. New findings get IDs `FP2R-R1`, `FP2R-R2`, ...
with severity, place, failure scenario and repair. Then a verdict: ACCEPT or FIX.

Local checks at 421e3b3 (Windows laptop, venv Python 3.14.7):
`pytest tests/unit/test_d19_deploy.py tests/unit/test_calibration_qobj.py`
33 passed; `ruff check .` passed; `ruff format --check .` 177 formatted;
`lint-imports` 7 kept; `sh -n deploy/calibration/d19.sh` ok. CI not yet run.

## Adjudication

# Adjudication: Astra review of FP2 at 3d6d8ef

Review record: `ASTRA_FP2_BUILD_REVIEW_3D6D8EF.md` (gpt-6-astra, high, read-only; verdict FIX).
Adjudicated by Claude Opus 5.5 (the implementer), 2026-10-24.

| ID | Severity | Adjudication | Repair |
|---|---|---|---|
| FP2-R1 | MAJOR | **Accepted.** `certify` checked for an existing report before `engine()` took the lock, so a second invocation could pass the check, wait, and then truncate the first one's report. `freeze` had the same order; there `qobj.build` refuses an existing `out` itself, so no object could be overwritten, but the order is fixed the same way. | `lock` now comes first in `certify` and `freeze`; the existence checks run under it. Test: in both blocks a `lock` line precedes the existence check (`test_d19_deploy.py`). |
| FP2-R2 | MAJOR | **Accepted in two parts.** (a) Launcher: `freeze` used whatever `HEAD` the build checkout had. (b) Sheet: the install-and-verify procedure for `/opt/aqt-d19/build` is not written. | (a) `freeze <full build commit>`: refuses unless `/opt/aqt-d19/build` is at exactly that commit, `git status --porcelain --untracked-files=all` is empty, and nothing in it is owned by a non-root user or writable by group or others; it prints the verified commit. CI checks a wrong commit is refused. (b) Written in `FREEZE_HELDOUT.md` (PR #76) after this build is accepted: the clone and checkout lines, the full-commit check of both checkouts (`/opt/aqt-d19/app` at `eeaa728`), ownership and origin, and the recorded evidence, before step G. Open until that sheet change is made. |

Reviewer remarks taken without a finding ID:

- BUILD-1 (network for `freeze`) accepted by the reviewer under the trusted-code assumption, with its scope stated: the whole freeze container, bridge mode, not limited to the Git remote. Kept as is; the sheet will say so.
- Sheet wording: "read-only checkout ... as `root`" becomes "a root-owned build checkout, and a disposable uid-990 clone of it as `root`". With the FP2-R2 (b) sheet change.
- BO-4 for `screen.py`: the reviewer accepts the named record as the final closure of the cumulative S1-S8 review chain, not as a standalone review of the whole file. Kept; this reading is stated here.
- The CI dry run refuses the pilot definition before the remote fetch, so CI does not exercise `ls-remote`/`fetch` from inside the container. **Not repaired**: exercising it needs a qualification definition and qualifying choices in CI. The fetch is first exercised on the server at step G; a failure there refuses with nothing written (`committed_before` raises before staging) and can be rerun.

Found while repairing, outside the findings: the CI negative checks written as `! cmd` cannot fail a `bash -e` step. The two added in this change are rewritten as `if cmd; then exit 1; fi`. The pre-existing `! sudo sh d19.sh clean-check` line has the same weakness; **not repaired here** (outside this task's scope), disclosed for a later change.

## The repair diff

```diff
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 41d8c59..7e77a09 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -228,13 +228,15 @@ jobs:
           # code) and refuses this pilot run, leaving no object
           sudo git clone --quiet /tmp/app.bundle /opt/aqt-d19/build
           sudo git -C /opt/aqt-d19/build checkout --quiet "$COMMIT"
-          out=$(sudo sh d19.sh freeze 2>&1) && exit 1
+          # (`! cmd` would not fail this step under bash -e)
+          if sudo sh d19.sh freeze "$(printf '%040d' 0)"; then exit 1; fi  # FP2-R2: not the build's commit
+          out=$(sudo sh d19.sh freeze "$COMMIT" 2>&1) && exit 1
           echo "$out" | tee /tmp/freeze
           grep -q "^refused: ValueError: not a qualification run" /tmp/freeze
           sudo test ! -e /var/lib/aqt-d19/qobj-1
           test -z "$(sudo find /opt/aqt-d19/build -not -user 0 -print -quit)"
           sudo sh d19.sh heldout-status
-          ! sudo sh d19.sh certify 1 "$(printf '%064d' 0)"  # no object: refused
+          if sudo sh d19.sh certify 1 "$(printf '%064d' 0)"; then exit 1; fi  # no object: refused
           sudo sh d19.sh nonfinite | tee /tmp/nonfinite
           grep -q "^all cells: 0 non-finite of" /tmp/nonfinite
           sudo sh d19.sh clean-check | tee /tmp/clean
diff --git a/deploy/calibration/d19.sh b/deploy/calibration/d19.sh
index 1b1e5d7..eba3478 100644
--- a/deploy/calibration/d19.sh
+++ b/deploy/calibration/d19.sh
@@ -22,7 +22,7 @@
 #   sudo sh d19.sh screen-pilot
 #   sudo sh d19.sh screen-status
 #   sudo sh d19.sh screen-summary
-#   sudo sh d19.sh freeze
+#   sudo sh d19.sh freeze <build commit>
 #   sudo sh d19.sh heldout <attempt> <posted hash> <round> <randomness>
 #   sudo sh d19.sh heldout-status
 #   sudo sh d19.sh certify <attempt> <posted hash>
@@ -322,9 +322,20 @@ failcheck)  # FR2-2, FE7-7: kill one worker; the run must stop, none survive
 freeze)  # FP2, §4 freeze-order step 5: the qualification object qobj-1. The
     # run's checkout is run_root; root is a fresh clone of the build checkout,
     # owned by uid 990 because build fetches the live remote into it (QO-2)
+    lock  # QO-6: no run going, so the store is quiescent; FP2-R1: checks after it
     [ ! -e "$WORK/qobj-1" ] || { echo "refused: $WORK/qobj-1 exists" >&2; exit 1; }
-    lock  # QO-6: no run going, so the store is quiescent
-    commit=$(git -C "$BUILD" rev-parse --verify HEAD)
+    # FP2-R2: the build checkout is exactly the reviewed, merged commit the
+    # owner names, unmodified, and writable by root only
+    commit=${2:-}
+    printf '%s' "$commit" | grep -qxE '[0-9a-f]{40}' ||
+        { echo "usage: d19.sh freeze <full build commit>" >&2; exit 1; }
+    [ "$(git -C "$BUILD" rev-parse --verify HEAD)" = "$commit" ] ||
+        { echo "refused: $BUILD is not at $commit" >&2; exit 1; }
+    [ -z "$(git -C "$BUILD" status --porcelain --untracked-files=all)" ] ||
+        { echo "refused: $BUILD differs from its commit" >&2; exit 1; }
+    [ -z "$(find "$BUILD" \( ! -user 0 -o -perm /022 \) -print -quit)" ] ||
+        { echo "refused: $BUILD is writable by others than root" >&2; exit 1; }
+    echo "build checkout $commit, unmodified"
     rm -rf "$WORK/freeze-root"
     # --no-hardlinks: the chown below must not reach the build checkout's objects
     git clone --quiet --no-hardlinks --no-checkout "$BUILD" "$WORK/freeze-root"
@@ -362,6 +373,7 @@ certify)  # FP2, §6: attempt <n>'s final reduction, once; exit 0 accepted, 2 no
     case "${2:-}" in 1 | 2) ;; *) echo "usage: d19.sh certify <1|2> <posted hash>" >&2; exit 1 ;; esac
     [ $# = 3 ] || { echo "usage: d19.sh certify <1|2> <posted hash>" >&2; exit 1; }
     out=certify-v$2.json
+    lock  # FP2-R1: the check and the write under one lock
     [ ! -e "$WORK/$out" ] || { echo "refused: $WORK/$out exists" >&2; exit 1; }
     rc=0
     engine --rm -- d19_heldout.py certify --object qobj-1 --posted "$3" \
diff --git a/tests/unit/test_d19_deploy.py b/tests/unit/test_d19_deploy.py
index c1100bd..43fe5f9 100644
--- a/tests/unit/test_d19_deploy.py
+++ b/tests/unit/test_d19_deploy.py
@@ -73,6 +73,15 @@ def test_the_launcher_gates_by_the_inspected_image_and_caps_the_run() -> None:
     freeze = launcher[launcher.index("freeze)") : launcher.index("heldout)")]
     assert re.search(r"^\s*NET=bridge  #", freeze, re.M)
     assert "--no-hardlinks" in freeze  # its chown must not reach $BUILD
+    # FP2-R1: each existence check runs under the lock; FP2-R2: freeze
+    # names the build commit and refuses a modified or writable checkout
+    certify = launcher[launcher.index("certify)") : launcher.index("\n*)")]
+    for block, made in ((freeze, "qobj-1"), (certify, "$out")):
+        head = block[: block.index(f'[ ! -e "$WORK/{made}" ]')]
+        assert re.search(r"^\s*lock\b", head, re.M)
+    checks = ('HEAD)" = "$commit"', "status --porcelain", "-perm /022")
+    for check in checks:
+        assert check in freeze, check
     flags = [
         '--network "$NET"',
         "--user 990:990",
```
