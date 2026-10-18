<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-18. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a15039-2672-77d1-809e-b81f71493cb5. Tokens used: 31,403. Packet built from full-run-sheet fc59645 (git show only): prompt FULL_RUN_SHEET_REVIEW_PROMPT.md, FULL_RUN.md, PILOT_FE7.md, d19.sh, OWNER_DECISION_BUILD_ORDER.md, OWNER_DECISION_FE7_GO_AHEAD.md, d19_run.py lines 1-40 and 280-340, rundef.py lines 205-280, grid.py lines 85-105, build_manifests.py lines 20-32. -->

# Sol review of the D-19 full-run sheet at fc59645

## Review (final message, verbatim)

**Verdict: FIX.** The launcher commands are broadly consistent with `d19.sh`, but the sheet does not yet establish a safe start and resume procedure for a qualification run. This review is based on the supplied excerpts; the full preregistration text was not available for an independent line by line check of §4.

- **FS-1 — Complete the preconditions.** P1 lists funding and three fixed values, while the go-ahead decision also requires the complete key record **A_Q1…F_Q2**, the accepted preregistration hash, and **T_C2**. The build-order decision is expressly conditional on its independent review being recorded. Put those checks, plus the owner’s §16 PR review of P3, ahead of step C. P3 should confirm that the merged admission change implements the reviewed “build by the freeze” decision.

- **FS-2 — Make step S safe to repeat and stop on failure.** The `mv` loop can overwrite an existing `*.repilot-e39b23d` target. Its final `ls` can also make the shell command succeed after a failed move. Require absent destination names and fail on each move. Check both `status` and `screen-status`, and confirm the D-19 slice is idle *before* moving records; `status` alone reports only `aqt-d19`.

- **FS-3 — Verify the bindings before `run threshold`.** The temporary clone’s `rev-parse` does not verify the installed `/opt/aqt-d19/app` checkout. Check its full HEAD, the installed qualifying cell list against the fixed T_C2 and prescribed counts, and the definition’s accepted preregistration hash and engine commit. After the definition is committed, verify that the repository blob is byte identical to `/var/lib/aqt-d19/definition.json` before step D. Receiving a commit ID alone does not establish that relationship; Git commit time alone is also insufficient evidence of ordering for S16-2.

- **FS-4 — Separate failure reporting from resumption.** The error block places `docker logs` and `run threshold` together even though resumption is conditional on the log being read. Stop after collecting the exit state and logs. Resume only after the failure is assessed and the same definition, engine and image are confirmed; collect logs before `run` removes the old container. State the equivalent rule for `dev`.

- **FS-5 — Add measurable run checks.** With 500 replications per chunk, each qualifying cell needs **600 threshold chunks** and **24 development chunks**. Require a row for every expected cell ID, including cells with no chunks yet, and no unexpected rows; `status` only prints chains that have written chunks. Run `memwatch` during each namespace and record its peak alongside the forward-paper service check. Weekly checks should include forward paper as well as D-19 status.

`manifests` has the stated write-once behavior, and the launcher separates its checkout and work directory from forward paper. The fixes above concern the qualification gate, stored record handling, and evidence that the committed definition is the one actually run.

## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-18)

| ID | Decision | Repair |
|---|---|---|
| FS-1 | Agree | P1 is the complete key record (A, F with outpoint/amount/height and OF1-3, D); P3 requires Sol and owner §16 review and the build-order reading; P4 records that the build-order independent review exists (`SOL6_BUILD_ORDER_REVIEW_D321147.md`); P5 records `T_C2 = 1240`. |
| FS-2 | Agree | Step S first checks `status`, `screen-status` and the slice processes; each move refuses an existing destination and stops on failure. |
| FS-3 | Agree | The installed checkout's full HEAD is checked; the cell list is hash-compared; the definition is checked for prereg hash, engine commit, manifest and image; the committed blob is hash-compared with the server file before step D. Commit time is stated as weak evidence, with the freeze checks deciding. |
| FS-4 | Agree | On an error: collect `status` and `docker logs`, stop; resume only after assessment and an unchanged definition, engine and image. The same rule is stated for `dev`. |
| FS-5 | Agree | 600 threshold and 24 dev chunks per cell, 104 cells; completion is checked by counting full chains; weekly checks include forward paper; `memwatch` runs in each namespace. Missing cells are found by comparing the listed ids with the expected 104 (`status` lists only started chains). |

No finding is left unrepaired.
