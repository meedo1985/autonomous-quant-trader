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
