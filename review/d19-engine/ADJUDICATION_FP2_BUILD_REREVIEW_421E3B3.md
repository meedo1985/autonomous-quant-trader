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
