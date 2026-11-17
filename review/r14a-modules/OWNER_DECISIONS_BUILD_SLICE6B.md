# Owner decisions on the slice 6b build deviations (PR #84)

- Date: 2026-11-17. The owner answered in Claude Code's question dialog, one question per
  item (wording in `DEVIATIONS_SLICE6B_REV16.md` §1), choosing "Accept" each time:

| ID | Item | Owner's answer |
|---|---|---|
| B1-D-1 | Capture record schema v2 (the archive digest covers the stored, possibly gzip, bytes) | Accept |
| B1-D-2 | `protocol_hash` in the declaration key set, with the exact field forms | Accept |
| B6F-D-1 | `qualification_checks` also in `prepare`, before any read (bounds moved before the lock, superseding B5A-R-2) | Accept |
| B6F-D-2 | A `cpcv_report` error recorded as C-14 UNAVAILABLE `C14_ERROR:<type>`; the look continues | Accept |

- Recorded by Claude Opus 5.5 (`claude-opus-5-5`). These are the owner's decisions, not an
  AI approval. Still open: F-9 and F-10 (wording route), the pre-signing items, the S4/SPEC
  wording for each accepted item, and the owner's §16 approval and merge of PR #84 itself.

## Owner §16 PR review of PR #84 (2026-11-17)

Asked in Claude Code's question dialog what he checked before the merge, the owner chose
the option worded: "I read DEVIATIONS_SLICE6B_REV16.md and the PR description, decided the
4 items, and accept the AI reviews (Astra, Fable) for the code itself; I approve the
merge." He then instructed "merge". CI at the PR head: `calibration-tests`, `checks`,
`runbook-dry-run` pass; `calibration-launcher` inconclusive (AMD EPYC OpenBLAS segfault,
same on `main` at `809cd45`). Recorded by Claude Opus 5.5 as the owner's human review, not
an AI approval.
