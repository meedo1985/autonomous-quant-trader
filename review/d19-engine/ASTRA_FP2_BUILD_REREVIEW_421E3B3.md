<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-24. CLI banner: model gpt-6-astra, reasoning effort high, sandbox read-only, session 01a16e6b-8db4-7de2-8b3a-449ec3ef606a. Tokens used: 86,209. Prompt: review/d19-engine/FP2_BUILD_REREVIEW_PROMPT.md (commit 53cec8a), reviewing 421e3b3. The reviewer's remark "exact runtime model/effort metadata unavailable" refers to its own view; the banner above is the CLI's record. Below: the reviewer's final message, unedited. -->

# Astra re-review of the FP2 repairs at 421e3b3

- FP2-R1 resolved; FP2-R2(a) partially resolved (blocked by FP2R-R1); FP2-R2(b) deferred, open. New: FP2R-R1 (MAJOR). Verdict: FIX.
- Adjudication: `ADJUDICATION_FP2_BUILD_REREVIEW_421E3B3.md`.

---

**Verdict: FIX.** One new MAJOR finding prevents closing FP2-R2(a).

Reviewed the committed `efe2370..421e3b3` changes and connected launcher/freezer code. No files changed.

**FP2R-R1 — MAJOR — Failed checkout checks are accepted as successful.**

**Place:** [deploy/calibration/d19.sh:334](D:/PMP-programs-for-sharawi/autonomous-quant-trader/deploy/calibration/d19.sh:334), including the ownership check at line 336.

**Failure scenario:** Both checks use `[ -z "$(command)" ]`. If the command fails with empty stdout, `[` succeeds. `set -eu` does not propagate that command-substitution failure through the successful test.

A corrupt Git index provides a concrete example: `rev-parse HEAD` succeeds, but `git status` fails. The launcher nevertheless accepts its empty output and prints “unmodified.” A `find` traversal failure with empty stdout similarly bypasses the ownership/permissions check.

**Evidence:** Under Windows Git’s dash, the extracted checks continued and exited **0** when mocked `git status` returned **128**, and when mocked `find` returned **1**. A real-Git reproduction using an empty alternate index printed `fatal: ... index file smaller than expected`, yet the surrounding empty-output check accepted it.

**Repair:** Check command success separately from output:

```sh
build_status=$(git -C "$BUILD" status --porcelain --untracked-files=all) ||
    { echo "refused: cannot inspect $BUILD" >&2; exit 1; }
[ -z "$build_status" ] ||
    { echo "refused: $BUILD differs from its commit" >&2; exit 1; }

unsafe_paths=$(find "$BUILD" \( ! -user 0 -o -perm /022 \) -print -quit) ||
    { echo "refused: cannot inspect $BUILD permissions" >&2; exit 1; }
[ -z "$unsafe_paths" ] ||
    { echo "refused: $BUILD is writable by others than root" >&2; exit 1; }
```

Add executable regression checks for both failed-command cases; the current substring assertions cannot detect this defect.

| Original finding | Disposition |
|---|---|
| **FP2-R1** | **Resolved.** Both existence checks now run after acquiring the shared lock. `LOCKED` makes the subsequent `engine()` lock call harmless, and the lock remains held through certification. |
| **FP2-R2(a)** | **Partially resolved.** Explicit full-SHA selection and comparison are correct. FP2R-R1 blocks acceptance of the clean/protected-checkout guarantee. |
| **FP2-R2(b)** | **Correctly deferred, still open.** PR #76 must supply installation, both full commit identities, origin/ownership verification and recorded evidence before step G. Build acceptance alone cannot close it. |

Other requested checks:

- **Permissions predicate:** GNU `find`’s `/022` tests either group-write or other-write; combined with `! -user 0`, the predicate is correct for the stated ordinary-directory deployment. The defect is ignored command failure.
- **Git status as root:** Acceptable for the intended root-owned checkout. Git can refresh its index, so “root-owned” is accurate; “read-only” would be misleading. This is documented [Git behavior](https://git-scm.com/docs/git-status#_background_refresh).
- **CI negative checks:** Both `if cmd; then exit 1; fi` replacements work. Bash harnesses confirmed unexpected success exits **1**, while expected refusal continues. The retained `out=$(...) && exit 1` form also behaves correctly.
- **Remote-fetch coverage deferred:** Acceptable as disclosed. `committed_before()` runs before staging-directory creation, so fetch failure publishes no qualification object. It can modify the disposable clone; “nothing written” should mean **no qualification object published**.
- **Pre-existing `! clean-check`:** Acceptable as a disclosed, separate follow-up for this bounded repair review. It remains ineffective regression coverage and must not be counted as a verified negative test.
- **BUILD-1 and BO-4:** Their stated trusted-code and cumulative-review interpretations remain acceptable; the promised sheet wording remains outstanding.

Independent validation: exact launcher blob passed `dash -n` via stdin; shell failure reproductions behaved as described; the protected-file diff was empty; all 31 checksum entries across 17 sidecar/manifest files, frozen manifest bindings and Constitution canonical hash matched.

**LOCAL GATE: BLOCKED** by FP2R-R1. Reported pytest/Ruff/import checks were not rerun; Ubuntu Docker/systemd integration and CI remain unverified. This is not §16 owner approval.

Reviewer: Codex; exact runtime model/effort metadata unavailable. Per the read-only instruction, this report was not committed; preserve it before applying repairs.
