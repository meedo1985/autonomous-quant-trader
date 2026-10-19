<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-18. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a1503c-41c0-75a2-aa91-8473988e8c3a. Tokens used: 22,324. Packet built from full-run-sheet b626e2a (git show only): prompt FULL_RUN_SHEET_REREVIEW_PROMPT.md, SOL6_FULL_RUN_SHEET_FC59645.md, FULL_RUN.md, d19.sh status and memwatch. -->

# Sol re-review of the D-19 full-run sheet at b626e2a

## Review (final message, verbatim)

**Verdict: FIX.** FS-1, FS-3 and FS-4 are addressed in the revised sheet. FS-2 and FS-5 remain open. I also found one new command-order defect.

| Finding | Result |
|---|---|
| FS-1 | **Closed.** The sheet now names the full key record, accepted hash, `T_C2`, build-order review and owner §16 review as preconditions. |
| FS-2 | **Open.** In step S, either `break` leaves the shell block running through `ls`, which can return success after a refused or failed move. The written `STOP` instruction helps the operator, but the command still does not fail as requested. Make the block return nonzero on either condition. |
| FS-3 | **Closed.** The sheet checks the installed HEAD and cell-list copy, calls for definition-field review, and compares the committed bytes with the server file before D. |
| FS-4 | **Closed.** Logs are collected before a separate assessment and resume decision, including for `dev`. |
| FS-5 | **Open.** The weekly commands send only a count and the first three `status` lines, which omit the cell rows. There is no list to compare with the 104 expected IDs. The completion checks likewise accept any 104 rows with the target count, even if an expected ID is missing and an unexpected ID takes its place. Send the full chain rows and compare their IDs with the installed qualification list for each namespace. |

**FSR-1 — Guard the grouped commands in A and C.** Step A prints `ok` when the backup path is free, but an occupied path does not stop the following `sudo mv`; `mv` can place `app` *inside* an existing directory. Later failures, including `checkout` or `install`, also do not stop `build`. In C, a `manifests` refusal does not stop `install` and `record` if the block is pasted. Make these blocks fail immediately at each required check. The general instruction to stop on errors cannot interrupt commands already submitted together.

This is a review of the supplied sheet and launcher excerpt; I did not execute the run.

## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-18)

| ID | Decision | Repair |
|---|---|---|
| FS-2 | Agree | Step S runs in a subshell that exits 1 on an existing destination or a failed move, so `ls` cannot mask it. |
| FS-5 | Agree | The weekly check sends the whole `status`; completion is my id-by-id comparison with the hash-checked 104-id list, with no other row; a row count alone is stated as insufficient. |
| FSR-1 | Agree | The sheet says to run every line alone, never a block. The move in A runs only if the backup path is free; checkout and `manifests` print an `ok:` line only on success, and the next line is run only after it. |

No finding is left unrepaired.
