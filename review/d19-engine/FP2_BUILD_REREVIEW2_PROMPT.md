# Independent adversarial re-review 2: FP2 repair at 05321c5

You are an independent adversarial reviewer (read-only), not an authority;
the owner's §16 PR review is separate. Your re-review of `421e3b3`
(`review/d19-engine/ASTRA_FP2_BUILD_REREVIEW_421E3B3.md`) found FP2R-R1.
The adjudication is included below, and the repair is `git diff 7a55cf0 05321c5`
(included below).

Check: (1) is FP2R-R1 resolved, and with it FP2-R2 (a); (2) does the
executable test really exercise the launcher's own lines and would it catch
a regression; (3) any new defect. New findings get IDs `FP2R2-R1`, ... with
severity, place, failure scenario and repair. Then a verdict: ACCEPT or FIX.
FP2-R2 (b) (the sheet's install procedure, PR #76) stays open by design;
do not count it against this build.

Local checks at 05321c5 (Windows laptop, venv Python 3.14.7, Git for Windows sh):
`pytest tests/unit/test_d19_deploy.py tests/unit/test_calibration_qobj.py`
38 passed; the new test fails in its two failed-command cases against the
421e3b3 launcher; `ruff check .` passed; `ruff format --check .` 177
formatted; `lint-imports` 7 kept; `sh -n deploy/calibration/d19.sh` ok. CI not yet run.

## Adjudication

# Adjudication: Astra re-review of the FP2 repairs at 421e3b3

Review record: `ASTRA_FP2_BUILD_REREVIEW_421E3B3.md` (gpt-6-astra, high, read-only; verdict FIX).
Adjudicated by Claude Opus 5.5 (the implementer), 2026-10-24.

| ID | Severity | Adjudication | Repair |
|---|---|---|---|
| FP2R-R1 | MAJOR | **Accepted.** `[ -z "$(cmd)" ]` passes when `cmd` fails with no output, so a `git status` or `find` that could not inspect the build checkout was taken as "unmodified" and "root-only". (`rev-parse` was not affected: a failure gives an empty string, which differs from the commit, so it refuses.) | The output of each is captured first, a failure refuses (`cannot inspect ...`), then the output is tested. New executable test `test_freeze_refuses_a_build_checkout_it_cannot_verify`: runs the freeze block's checks, extracted from `d19.sh`, under `sh` with shell functions standing in for `git` and `find`, for a failed status, a failed find, a modified tree, an unsafe path, and a clean checkout. Against the 421e3b3 launcher it fails in the two failed-command cases; against the repair all five pass. |

Dispositions carried forward:

- FP2-R1: resolved (reviewer).
- FP2-R2 (a): resolved by the above, pending re-review.
- FP2-R2 (b): open. The sheet's install procedure goes in PR #76 before step G.
- Wording taken from the reviewer: "nothing written" for a failed fetch means **no qualification object published**; the disposable clone `/var/lib/aqt-d19/freeze-root` may change. The build checkout is called "root-owned", not "read-only", since `git status` may refresh its index.
- The pre-existing `! sudo sh d19.sh clean-check` line in CI: still not repaired, and not counted as a verified negative test.

## The repair diff

```diff
diff --git a/deploy/calibration/d19.sh b/deploy/calibration/d19.sh
index eba3478..68db707 100644
--- a/deploy/calibration/d19.sh
+++ b/deploy/calibration/d19.sh
@@ -331,10 +331,13 @@ freeze)  # FP2, §4 freeze-order step 5: the qualification object qobj-1. The
         { echo "usage: d19.sh freeze <full build commit>" >&2; exit 1; }
     [ "$(git -C "$BUILD" rev-parse --verify HEAD)" = "$commit" ] ||
         { echo "refused: $BUILD is not at $commit" >&2; exit 1; }
-    [ -z "$(git -C "$BUILD" status --porcelain --untracked-files=all)" ] ||
-        { echo "refused: $BUILD differs from its commit" >&2; exit 1; }
-    [ -z "$(find "$BUILD" \( ! -user 0 -o -perm /022 \) -print -quit)" ] ||
-        { echo "refused: $BUILD is writable by others than root" >&2; exit 1; }
+    # FP2R-R1: a failed inspection refuses; its empty output is no "clean"
+    changed=$(git -C "$BUILD" status --porcelain --untracked-files=all) ||
+        { echo "refused: cannot inspect $BUILD" >&2; exit 1; }
+    [ -z "$changed" ] || { echo "refused: $BUILD differs from its commit" >&2; exit 1; }
+    unsafe=$(find "$BUILD" \( ! -user 0 -o -perm /022 \) -print -quit) ||
+        { echo "refused: cannot inspect the permissions of $BUILD" >&2; exit 1; }
+    [ -z "$unsafe" ] || { echo "refused: $BUILD is writable by others than root" >&2; exit 1; }
     echo "build checkout $commit, unmodified"
     rm -rf "$WORK/freeze-root"
     # --no-hardlinks: the chown below must not reach the build checkout's objects
diff --git a/tests/unit/test_d19_deploy.py b/tests/unit/test_d19_deploy.py
index 43fe5f9..4e0f770 100644
--- a/tests/unit/test_d19_deploy.py
+++ b/tests/unit/test_d19_deploy.py
@@ -131,6 +131,43 @@ def test_the_launcher_is_valid_sh() -> None:
     subprocess.run(["sh", "-n", str(DEPLOY / "d19.sh")], check=True)
 
 
+@pytest.mark.skipif(shutil.which("sh") is None, reason="no POSIX sh")
+@pytest.mark.parametrize(
+    ("status", "find", "refusal"),
+    [
+        ("fail", "ok", "cannot inspect"),  # FP2R-R1: no output, failed
+        ("ok", "fail", "cannot inspect the permissions"),
+        ("dirty", "ok", "differs from its commit"),
+        ("ok", "unsafe", "writable by others"),
+        ("ok", "ok", None),
+    ],
+)
+def test_freeze_refuses_a_build_checkout_it_cannot_verify(
+    status: str, find: str, refusal: str | None
+) -> None:
+    """FP2-R2, FP2R-R1: the freeze block's checkout checks, run under sh
+    with shell functions standing in for git and find."""
+    launcher = (DEPLOY / "d19.sh").read_text(encoding="utf-8")
+    start = launcher.index("    commit=${2:-}")
+    checks = launcher[start : launcher.index('    echo "build checkout', start)]
+    sha = "a" * 40
+    stubs = (
+        f'git() {{ case "$3" in rev-parse) echo {sha} ;;\n'
+        f"  status) case {status} in fail) return 128 ;;\n"
+        '    dirty) echo " M x" ;; esac ;;\n'
+        "  esac; }\n"
+        f"find() {{ case {find} in fail) return 1 ;; unsafe) echo /b/x ;; esac; }}\n"
+    )
+    script = f"set -eu\n{stubs}BUILD=/b\n{checks}echo PASSED\n"
+    done = subprocess.run(["sh", "-c", script, "d19.sh", "freeze", sha],
+                          capture_output=True, text=True, check=False)  # fmt: skip
+    if refusal is None:
+        assert done.returncode == 0 and done.stdout.strip() == "PASSED", done.stderr
+    else:
+        assert done.returncode == 1 and refusal in done.stderr, done.stderr
+        assert "PASSED" not in done.stdout
+
+
 def test_the_re_pilot_manifest_is_a_valid_pilot_covering_every_group() -> None:
     """FE-7: one cell of each group Q1-Q5 and QJ, and every cell of the thin
     categories (Q1 clusters, Q2m, QJ); a pilot by its ids and counts (FA-1)."""
```
