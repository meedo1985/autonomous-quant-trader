# FP3 binding evidence

Recorded by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-25, from GitHub's API and the repository. The AI made no part of the owner's commit.

- **Owner's commit:** `d7720be547ee3fe3957a0ed1f07bab952257d717` on `freeze-sheet`, message "FP3: owner adopts the supplementary acceptance (drand quicknet), signed". It adds only `review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md`, SHA-256 `67b5c16528ca8c1b800005b0efbfaf4bd455a97bcdb53a670a58bd09259c4a7b`. The commit carries an SSH signature.
- **GitHub verification:** `verified: true`, `reason: valid`, `verified_at: 2026-10-25T11:31:07Z`. The signing key is the owner's GitHub SSH signing key "owner signing key", registered 2026-10-25T13:17:25+02:00, `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINRu…`. The owner's private key is protected by a passphrase only he holds.
- **Push time (GitHub activity API):** `2026-10-25T11:31:06Z`, push of `d7720be`.
- **Content:** Rules 1-9 are identical to draft revision 4 (`802be05`). Both different-model reviews of revision 4 end in ACCEPT: `FABLE_FP3_SUPPLEMENTARY_REREVIEW3.md` (claude-fable-5-1) and `SOL_FP3_SUPPLEMENTARY_REREVIEW3.md` (gpt-6-sol).
- **Before G:** step G has not run. No qualification object exists, no `AQTQ1` post has been made, and no `T_Qn` is fixed (FULL_RUN.md step E, the development run, is still running).

The four binding conditions of the draft's status block are met:
1. both reviews committed, each ending in ACCEPT;
2. the owner's adoption;
3. his own signed, dated commit;
4. the push before G.

**FP3 (chain and missing-output rule) is bound**, for D-19 attempts 1 and 2, by `review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md`. The route rests on judgement, not express text (GOV-FP3-3). The C2 signing must ratify it (Rule 8).

Still open before G, outside FP3's binding: the pinned verification tool tested on a historical quicknet round with a negative test, result committed; the sheet's step K updated (the 7-day stop replaced by Rule 5, the drand check separated from the O-6a record, the run-start bound of FP3S4-G2).
