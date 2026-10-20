# Review prompt: DR2-1 pin of the accepted D-19 preregistration hash

You are an independent adversarial reviewer working read-only, not an authority. This is a §16 review: the change unlocks qualification runs in `calibration/rundef.py` (DR2-1). Everything is attached: the acceptance commit `53489db` diff and the pin diff.

Check:
1. **Acceptance (`53489db`):** `PREREGISTRATION.md` §4 changes only by replacing `<<ACCEPTANCE: A_Q1, F_Q1, D_Q1, A_Q2, F_Q2>>` with the recorded values; nothing else in the preregistration moved. The values match `ACCEPTANCE_RECORD.md` §1 and `KEY_RECORD_DRAFT.md` (addresses, outpoints, amounts, heights, `D_Q1` = 1,000,000). `D_Q2` is not fixed (DF5-3). The record's checks cover OF1-3 and the owner's answers are recorded verbatim. If you can reach mempool.space or blockstream.info, confirm each address has one funding output and no spend; if not, say so.
2. **Pin:** `ACCEPTED_PREREG_SHA256` equals SHA-256 of `git show 53489db:review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md` (verify it yourself). The hash is of the committed blob, the same bytes `rundef` reads with `git show` (line endings cannot differ).
3. **Guard:** with the pin set, `run_plan` admits a qualification run only for that hash and still refuses `None` and any other hash; no other path admits a qualification run. The new test fails on any later edit to the committed preregistration.
4. **Order:** FULL_RUN.md P1-P3 are satisfied by these two commits plus the merged #66 engine change; nothing in the sheet is now skipped.

Out of scope: the engine itself (reviewed in #66), the frozen v1.0 artifacts.

Verdict ACCEPT or FIX. Findings get stable IDs PIN-Rn with severity, file:line and a concrete failure scenario.
