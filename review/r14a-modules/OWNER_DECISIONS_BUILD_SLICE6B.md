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
