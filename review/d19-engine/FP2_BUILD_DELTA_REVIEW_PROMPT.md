# Independent adversarial delta review: FP2 changes after ACCEPT (05321c5 -> ff1af4c, sheet 9afbb80)

You are an independent adversarial reviewer (read-only), not an authority;
the owner's §16 PR review is separate. Your re-review 2 of `05321c5`
(`review/d19-engine/` record committed in 500f1ff) was ACCEPT. Since then:

- 9b6f5e4: CI runs `chmod -R go-w` on the build checkout, as sheet step G0 does.
- 9575aa2: the root-only refusal names the offending path (`ls -ld`).
- 3982746: freeze inspects the build checkout with `git --no-optional-locks status`.
  Cause found in CI: a plain `git status` rewrote `.git/index`, and under the
  runner's default ACL on /opt the new index came out world-writable, which
  the root-only check then refused.
- ff1af4c: owner-requested ponytail-review follow-ups: the CI find output is
  captured so a failed find fails the step; a comment re-wrapped; the
  heldout/certify argument-count and chain checks merged into one `case`.
- Sheet PR #76, 9afbb80: step G0 uses the same `--no-optional-locks status`.

Check: (1) does any change weaken FP2-R1, FP2-R2 (a) or FP2R-R1 (the freeze
checks, the lock, a failed inspection refusing); (2) is `--no-optional-locks`
sufficient, i.e. can freeze's own commands still write to the build checkout;
(3) are the merged `case "$#:${2:-}"` checks exactly equivalent to the two
checks they replace for every argument count; (4) can `$(ls -ld "$unsafe")`
in the refusal mislead or fail; (5) any new defect. New findings get IDs
`FP2D-R1`, ... with severity, place, failure scenario and repair. Then a
verdict: ACCEPT or FIX. FP2-R2 (b) (the sheet install procedure) is handled
in PR #76; judge only whether 9afbb80 matches the launcher.

Local checks at ff1af4c (Windows laptop, venv Python 3.14.7, Git for Windows sh):
`pytest tests/unit/test_d19_deploy.py tests/unit/test_calibration_qobj.py`
38 passed; `ruff check .` passed; `ruff format --check .` 177 formatted;
`lint-imports` 7 kept, 0 broken; `sh -n deploy/calibration/d19.sh` ok.
CI run 40109500979 on ff1af4c: checks, runbook-dry-run, calibration-tests,
calibration-launcher all pass (launcher on a re-run: the first attempt hit
the known AMD EPYC 9V74 probe segfault, inconclusive; the re-run on EPYC 7763
passed, including the freeze / heldout-status / certify steps).

## The PR #77 delta (`git diff 05321c5 ff1af4c`)

```diff
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 7e77a09..d07db17 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -228,13 +228,16 @@ jobs:
           # code) and refuses this pilot run, leaving no object
           sudo git clone --quiet /tmp/app.bundle /opt/aqt-d19/build
           sudo git -C /opt/aqt-d19/build checkout --quiet "$COMMIT"
+          sudo chmod -R go-w /opt/aqt-d19/build  # as FREEZE_HELDOUT.md step G0
           # (`! cmd` would not fail this step under bash -e)
           if sudo sh d19.sh freeze "$(printf '%040d' 0)"; then exit 1; fi  # FP2-R2: not the build's commit
           out=$(sudo sh d19.sh freeze "$COMMIT" 2>&1) && exit 1
           echo "$out" | tee /tmp/freeze
           grep -q "^refused: ValueError: not a qualification run" /tmp/freeze
           sudo test ! -e /var/lib/aqt-d19/qobj-1
-          test -z "$(sudo find /opt/aqt-d19/build -not -user 0 -print -quit)"
+          # a failed find fails the step (bash -e), never reads as "none"
+          bad=$(sudo find /opt/aqt-d19/build -not -user 0 -print -quit)
+          test -z "$bad"
           sudo sh d19.sh heldout-status
           if sudo sh d19.sh certify 1 "$(printf '%064d' 0)"; then exit 1; fi  # no object: refused
           sudo sh d19.sh nonfinite | tee /tmp/nonfinite
diff --git a/deploy/calibration/d19.sh b/deploy/calibration/d19.sh
index 68db707..ca70882 100644
--- a/deploy/calibration/d19.sh
+++ b/deploy/calibration/d19.sh
@@ -29,8 +29,9 @@
 #
 # Every engine process runs in the pinned image, as uid 990, without network
 # (except `freeze`, which reads the live remote, QO-2), at `nice 19`, inside
-# aqt-d19.slice (systemd MemoryMax 2560M, checked before every start), with the engine's own read-only checkout at /app (never the
-# forward-paper one). The image is started by the id that `docker image
+# aqt-d19.slice (systemd MemoryMax 2560M, checked before every start),
+# with the engine's own read-only checkout at /app (never the forward-paper
+# one). The image is started by the id that `docker image
 # inspect` reports here, and the same id is AQT_IMAGE_DIGEST: never typed
 # (FE-4, FE4-1). The driver runs exactly 2 workers (scripts/d19_run.py,
 # WORKERS).
@@ -332,12 +333,15 @@ freeze)  # FP2, §4 freeze-order step 5: the qualification object qobj-1. The
     [ "$(git -C "$BUILD" rev-parse --verify HEAD)" = "$commit" ] ||
         { echo "refused: $BUILD is not at $commit" >&2; exit 1; }
     # FP2R-R1: a failed inspection refuses; its empty output is no "clean"
-    changed=$(git -C "$BUILD" status --porcelain --untracked-files=all) ||
+    # --no-optional-locks: a plain status may rewrite .git/index, and under
+    # a default ACL the new index came out world-writable (CI, 9575aa2)
+    changed=$(git -C "$BUILD" --no-optional-locks status --porcelain --untracked-files=all) ||
         { echo "refused: cannot inspect $BUILD" >&2; exit 1; }
     [ -z "$changed" ] || { echo "refused: $BUILD differs from its commit" >&2; exit 1; }
     unsafe=$(find "$BUILD" \( ! -user 0 -o -perm /022 \) -print -quit) ||
         { echo "refused: cannot inspect the permissions of $BUILD" >&2; exit 1; }
-    [ -z "$unsafe" ] || { echo "refused: $BUILD is writable by others than root" >&2; exit 1; }
+    [ -z "$unsafe" ] ||
+        { echo "refused: $BUILD is writable by others than root: $(ls -ld "$unsafe")" >&2; exit 1; }
     echo "build checkout $commit, unmodified"
     rm -rf "$WORK/freeze-root"
     # --no-hardlinks: the chown below must not reach the build checkout's objects
@@ -355,8 +359,7 @@ freeze)  # FP2, §4 freeze-order step 5: the qualification object qobj-1. The
     ;;
 heldout)  # FP2, §4 step 6: attempt <n>'s held-out run; it prints chain heads
     # only (P18-6), and a restart resumes
-    case "${2:-}" in 1 | 2) ;; *) echo "usage: d19.sh heldout <1|2> <posted hash> <round> <randomness>" >&2; exit 1 ;; esac
-    [ $# = 5 ] || { echo "usage: d19.sh heldout <1|2> <posted hash> <round> <randomness>" >&2; exit 1; }
+    case "$#:${2:-}" in 5:1 | 5:2) ;; *) echo "usage: d19.sh heldout <1|2> <posted hash> <round> <randomness>" >&2; exit 1 ;; esac
     lock
     docker rm "$NAME-heldout" >/dev/null 2>&1 || true
     engine -d --name "$NAME-heldout" -- d19_heldout.py run --object qobj-1 \
@@ -373,8 +376,7 @@ heldout-status)  # P18-6: state, times and chunks per chain; nothing else
         sort -k2
     ;;
 certify)  # FP2, §6: attempt <n>'s final reduction, once; exit 0 accepted, 2 not
-    case "${2:-}" in 1 | 2) ;; *) echo "usage: d19.sh certify <1|2> <posted hash>" >&2; exit 1 ;; esac
-    [ $# = 3 ] || { echo "usage: d19.sh certify <1|2> <posted hash>" >&2; exit 1; }
+    case "$#:${2:-}" in 3:1 | 3:2) ;; *) echo "usage: d19.sh certify <1|2> <posted hash>" >&2; exit 1 ;; esac
     out=certify-v$2.json
     lock  # FP2-R1: the check and the write under one lock
     [ ! -e "$WORK/$out" ] || { echo "refused: $WORK/$out exists" >&2; exit 1; }
diff --git a/review/d19-engine/ASTRA_FP2_BUILD_REREVIEW2_05321C5.md b/review/d19-engine/ASTRA_FP2_BUILD_REREVIEW2_05321C5.md
new file mode 100644
index 0000000..30483a6
--- /dev/null
+++ b/review/d19-engine/ASTRA_FP2_BUILD_REREVIEW2_05321C5.md
@@ -0,0 +1,37 @@
+<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-24. CLI banner: model gpt-6-astra, reasoning effort high, sandbox read-only, session 01a16e73-185a-7e13-904a-b603411a1a51. Tokens used: 85,786. Prompt: review/d19-engine/FP2_BUILD_REREVIEW2_PROMPT.md (commit 9d6f04b), reviewing 05321c5. The reviewer's remark "exact runtime model/effort metadata unavailable" refers to its own view; the banner above is the CLI's record. Below: the reviewer's final message, unedited. -->
+
+# Astra re-review 2 of the FP2 repair at 05321c5
+
+- FP2R-R1 resolved; FP2-R2 (a) resolved; FP2-R2 (b) open by design (sheet, PR #76). No new findings. Verdict: ACCEPT.
+
+---
+
+**Verdict: ACCEPT** for the bounded repair at `05321c5`. No new findings.
+
+- **FP2R-R1 resolved; FP2-R2(a) resolved.** In [d19.sh:335](D:/PMP-programs-for-sharawi/autonomous-quant-trader/deploy/calibration/d19.sh:335), each assignment preserves the inspection command’s exit status, and `||` explicitly refuses failure. Only successful inspections reach the output checks. Both refusals occur before deleting or creating the disposable clone.
+- **The regression test exercises the launcher’s own lines.** [test_d19_deploy.py:150](D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_d19_deploy.py:150) extracts the actual checkout checks and executes them under `sh`. The argument placement correctly supplies `freeze` as `$1` and the SHA as `$2`; the Git stub correctly dispatches on `$3`.
+- **Regression sensitivity independently confirmed.** Running the unchanged test function against each committed launcher blob produced:
+
+| Case | `05321c5` | `421e3b3` |
+|---|---|---|
+| Failed status, empty output | PASS | FAIL |
+| Failed find, empty output | PASS | FAIL |
+| Dirty checkout | PASS | PASS |
+| Unsafe permissions | PASS | PASS |
+| Clean checkout | PASS | PASS |
+
+The refusal assertions require exit **1**, the relevant diagnostic, and no `PASSED` sentinel. The clean case prevents an unconditional refusal from passing. This is valid regression coverage for FP2R-R1; it does not exercise the full freeze operation or real filesystem permissions.
+
+Independent validation:
+
+- Targeted pytest with `-B --capture=sys -p no:cacheprovider`: **6 passed**, including shell syntax.
+- `rtk proxy .venv/Scripts/ruff.exe check --no-cache .`: **passed**.
+- `rtk proxy .venv/Scripts/ruff.exe format --check --no-cache .`: **177 formatted**.
+- Protected-file commit diff: **empty**. Verified **28 trusted baseline files**, **31 checksum entries**, Constitution self-hash and manifest bindings.
+- Working tree remained unchanged. Current HEAD adds only the review prompt beyond `05321c5`.
+
+**FP2-R2(b) remains open by design**, excluded from this verdict. The pre-existing CI `! clean-check` remains unverified negative coverage.
+
+**Validation limitation:** the independent import-linter attempt printed “Access is denied”; I do not count it as passing. The supplied 38-test result and seven kept contracts remain author-reported; CI and Docker/systemd integration were not independently verified. Thus this code-review ACCEPT does not certify the complete local gate or replace §16 owner review.
+
+Reviewer: Codex; exact runtime model/effort metadata unavailable. Per your read-only instruction, this report is uncommitted and still needs preservation under the repository’s review-record rule.
diff --git a/review/d19-engine/FP2_BUILD_REREVIEW2_PROMPT.md b/review/d19-engine/FP2_BUILD_REREVIEW2_PROMPT.md
new file mode 100644
index 0000000..abae1c7
--- /dev/null
+++ b/review/d19-engine/FP2_BUILD_REREVIEW2_PROMPT.md
@@ -0,0 +1,114 @@
+# Independent adversarial re-review 2: FP2 repair at 05321c5
+
+You are an independent adversarial reviewer (read-only), not an authority;
+the owner's §16 PR review is separate. Your re-review of `421e3b3`
+(`review/d19-engine/ASTRA_FP2_BUILD_REREVIEW_421E3B3.md`) found FP2R-R1.
+The adjudication is included below, and the repair is `git diff 7a55cf0 05321c5`
+(included below).
+
+Check: (1) is FP2R-R1 resolved, and with it FP2-R2 (a); (2) does the
+executable test really exercise the launcher's own lines and would it catch
+a regression; (3) any new defect. New findings get IDs `FP2R2-R1`, ... with
+severity, place, failure scenario and repair. Then a verdict: ACCEPT or FIX.
+FP2-R2 (b) (the sheet's install procedure, PR #76) stays open by design;
+do not count it against this build.
+
+Local checks at 05321c5 (Windows laptop, venv Python 3.14.7, Git for Windows sh):
+`pytest tests/unit/test_d19_deploy.py tests/unit/test_calibration_qobj.py`
+38 passed; the new test fails in its two failed-command cases against the
+421e3b3 launcher; `ruff check .` passed; `ruff format --check .` 177
+formatted; `lint-imports` 7 kept; `sh -n deploy/calibration/d19.sh` ok. CI not yet run.
+
+## Adjudication
+
+# Adjudication: Astra re-review of the FP2 repairs at 421e3b3
+
+Review record: `ASTRA_FP2_BUILD_REREVIEW_421E3B3.md` (gpt-6-astra, high, read-only; verdict FIX).
+Adjudicated by Claude Opus 5.5 (the implementer), 2026-10-24.
+
+| ID | Severity | Adjudication | Repair |
+|---|---|---|---|
+| FP2R-R1 | MAJOR | **Accepted.** `[ -z "$(cmd)" ]` passes when `cmd` fails with no output, so a `git status` or `find` that could not inspect the build checkout was taken as "unmodified" and "root-only". (`rev-parse` was not affected: a failure gives an empty string, which differs from the commit, so it refuses.) | The output of each is captured first, a failure refuses (`cannot inspect ...`), then the output is tested. New executable test `test_freeze_refuses_a_build_checkout_it_cannot_verify`: runs the freeze block's checks, extracted from `d19.sh`, under `sh` with shell functions standing in for `git` and `find`, for a failed status, a failed find, a modified tree, an unsafe path, and a clean checkout. Against the 421e3b3 launcher it fails in the two failed-command cases; against the repair all five pass. |
+
+Dispositions carried forward:
+
+- FP2-R1: resolved (reviewer).
+- FP2-R2 (a): resolved by the above, pending re-review.
+- FP2-R2 (b): open. The sheet's install procedure goes in PR #76 before step G.
+- Wording taken from the reviewer: "nothing written" for a failed fetch means **no qualification object published**; the disposable clone `/var/lib/aqt-d19/freeze-root` may change. The build checkout is called "root-owned", not "read-only", since `git status` may refresh its index.
+- The pre-existing `! sudo sh d19.sh clean-check` line in CI: still not repaired, and not counted as a verified negative test.
+
+## The repair diff
+
+```diff
+diff --git a/deploy/calibration/d19.sh b/deploy/calibration/d19.sh
+index eba3478..68db707 100644
+--- a/deploy/calibration/d19.sh
++++ b/deploy/calibration/d19.sh
+@@ -331,10 +331,13 @@ freeze)  # FP2, §4 freeze-order step 5: the qualification object qobj-1. The
+         { echo "usage: d19.sh freeze <full build commit>" >&2; exit 1; }
+     [ "$(git -C "$BUILD" rev-parse --verify HEAD)" = "$commit" ] ||
+         { echo "refused: $BUILD is not at $commit" >&2; exit 1; }
+-    [ -z "$(git -C "$BUILD" status --porcelain --untracked-files=all)" ] ||
+-        { echo "refused: $BUILD differs from its commit" >&2; exit 1; }
+-    [ -z "$(find "$BUILD" \( ! -user 0 -o -perm /022 \) -print -quit)" ] ||
+-        { echo "refused: $BUILD is writable by others than root" >&2; exit 1; }
++    # FP2R-R1: a failed inspection refuses; its empty output is no "clean"
++    changed=$(git -C "$BUILD" status --porcelain --untracked-files=all) ||
++        { echo "refused: cannot inspect $BUILD" >&2; exit 1; }
++    [ -z "$changed" ] || { echo "refused: $BUILD differs from its commit" >&2; exit 1; }
++    unsafe=$(find "$BUILD" \( ! -user 0 -o -perm /022 \) -print -quit) ||
++        { echo "refused: cannot inspect the permissions of $BUILD" >&2; exit 1; }
++    [ -z "$unsafe" ] || { echo "refused: $BUILD is writable by others than root" >&2; exit 1; }
+     echo "build checkout $commit, unmodified"
+     rm -rf "$WORK/freeze-root"
+     # --no-hardlinks: the chown below must not reach the build checkout's objects
+diff --git a/tests/unit/test_d19_deploy.py b/tests/unit/test_d19_deploy.py
+index 43fe5f9..4e0f770 100644
+--- a/tests/unit/test_d19_deploy.py
++++ b/tests/unit/test_d19_deploy.py
+@@ -131,6 +131,43 @@ def test_the_launcher_is_valid_sh() -> None:
+     subprocess.run(["sh", "-n", str(DEPLOY / "d19.sh")], check=True)
+ 
+ 
++@pytest.mark.skipif(shutil.which("sh") is None, reason="no POSIX sh")
++@pytest.mark.parametrize(
++    ("status", "find", "refusal"),
++    [
++        ("fail", "ok", "cannot inspect"),  # FP2R-R1: no output, failed
++        ("ok", "fail", "cannot inspect the permissions"),
++        ("dirty", "ok", "differs from its commit"),
++        ("ok", "unsafe", "writable by others"),
++        ("ok", "ok", None),
++    ],
++)
++def test_freeze_refuses_a_build_checkout_it_cannot_verify(
++    status: str, find: str, refusal: str | None
++) -> None:
++    """FP2-R2, FP2R-R1: the freeze block's checkout checks, run under sh
++    with shell functions standing in for git and find."""
++    launcher = (DEPLOY / "d19.sh").read_text(encoding="utf-8")
++    start = launcher.index("    commit=${2:-}")
++    checks = launcher[start : launcher.index('    echo "build checkout', start)]
++    sha = "a" * 40
++    stubs = (
++        f'git() {{ case "$3" in rev-parse) echo {sha} ;;\n'
++        f"  status) case {status} in fail) return 128 ;;\n"
++        '    dirty) echo " M x" ;; esac ;;\n'
++        "  esac; }\n"
++        f"find() {{ case {find} in fail) return 1 ;; unsafe) echo /b/x ;; esac; }}\n"
++    )
++    script = f"set -eu\n{stubs}BUILD=/b\n{checks}echo PASSED\n"
++    done = subprocess.run(["sh", "-c", script, "d19.sh", "freeze", sha],
++                          capture_output=True, text=True, check=False)  # fmt: skip
++    if refusal is None:
++        assert done.returncode == 0 and done.stdout.strip() == "PASSED", done.stderr
++    else:
++        assert done.returncode == 1 and refusal in done.stderr, done.stderr
++        assert "PASSED" not in done.stdout
++
++
+ def test_the_re_pilot_manifest_is_a_valid_pilot_covering_every_group() -> None:
+     """FE-7: one cell of each group Q1-Q5 and QJ, and every cell of the thin
+     categories (Q1 clusters, Q2m, QJ); a pilot by its ids and counts (FA-1)."""
+```
diff --git a/tests/unit/test_d19_deploy.py b/tests/unit/test_d19_deploy.py
index 4e0f770..eb4ac3d 100644
--- a/tests/unit/test_d19_deploy.py
+++ b/tests/unit/test_d19_deploy.py
@@ -79,7 +79,12 @@ def test_the_launcher_gates_by_the_inspected_image_and_caps_the_run() -> None:
     for block, made in ((freeze, "qobj-1"), (certify, "$out")):
         head = block[: block.index(f'[ ! -e "$WORK/{made}" ]')]
         assert re.search(r"^\s*lock\b", head, re.M)
-    checks = ('HEAD)" = "$commit"', "status --porcelain", "-perm /022")
+    # --no-optional-locks: the check must not rewrite the index it inspects
+    checks = (
+        'HEAD)" = "$commit"',
+        "--no-optional-locks status --porcelain",
+        "-perm /022",
+    )
     for check in checks:
         assert check in freeze, check
     flags = [
@@ -152,8 +157,8 @@ def test_freeze_refuses_a_build_checkout_it_cannot_verify(
     checks = launcher[start : launcher.index('    echo "build checkout', start)]
     sha = "a" * 40
     stubs = (
-        f'git() {{ case "$3" in rev-parse) echo {sha} ;;\n'
-        f"  status) case {status} in fail) return 128 ;;\n"
+        f'git() {{ case "$*" in *rev-parse*) echo {sha} ;;\n'
+        f"  *status*) case {status} in fail) return 128 ;;\n"
         '    dirty) echo " M x" ;; esac ;;\n'
         "  esac; }\n"
         f"find() {{ case {find} in fail) return 1 ;; unsafe) echo /b/x ;; esac; }}\n"
```

## The sheet delta (`git show 9afbb80`)

```diff
diff --git a/deploy/calibration/FREEZE_HELDOUT.md b/deploy/calibration/FREEZE_HELDOUT.md
index 263bc2e..2ff3074 100644
--- a/deploy/calibration/FREEZE_HELDOUT.md
+++ b/deploy/calibration/FREEZE_HELDOUT.md
@@ -35,7 +35,7 @@ sudo chmod -R go-w /opt/aqt-d19/build
 sudo git -C /opt/aqt-d19/build rev-parse HEAD
 sudo git -C /opt/aqt-d19/app rev-parse HEAD
 sudo git -C /opt/aqt-d19/build remote get-url origin
-sudo git -C /opt/aqt-d19/build status --porcelain --untracked-files=all
+sudo git -C /opt/aqt-d19/build --no-optional-locks status --porcelain --untracked-files=all
 sudo find /opt/aqt-d19/build \( ! -user 0 -o -perm /022 \) -print -quit
 ```
 
```
