# D-20 lockbox bindings, option C: release on request (revision C5, erratum; delta on C4)

**Author:** Claude Opus 5.5 (`claude-opus-5-5`, this session's environment metadata), main Claude Code session, 2026-10-31. This is AI drafting, not an authority. I propose and check bindings. I cannot decide, accept, activate or amend anything.

**Status: INACTIVE PROPOSAL.** Nothing frozen has changed. No row binds until the owner decides and signs the C2 §4 amendment. No human statistician has reviewed it.

**Owner direction (2026-10-31):** "let contenue", which continues the recorded plan: fold the C4 re-check notes into a C5 erratum, then go to the owner questions. **This is a text-only erratum.** No record type, lock, operation, role, rule or owner question is added or changed.

**Answers** (both read in full):
- `SOL_OPTION_C4_REVIEW_5599056.md` (gpt-6-sol): ACCEPT WITH NOTES, D20C4-S-1;
- `ASTRA_OPTION_C4_REVIEW_5599056.md` (gpt-6-astra): ACCEPT WITH NOTES, D20C4-A-1..2.

Neither reviewer found a blocker. Both say C2+C3+C4 is ready for the owner questions.

**How to read it:** a **delta on `OPTION_C_PROPOSAL_REV4.md`**. Each item names the text it replaces. Everything else stands.

**VERDICT: `AMENDMENT_REQUIRED`.**

## 1a. Dispositions

| ID | Disposition | Repair |
|---|---|---|
| **D20C4-S-1** (NON-BLOCKING; T-S6 "identical shape") | **Accepted.** | item 1 |
| **D20C4-A-1** (NON-BLOCKING; T-S2 and T-S1 replacement assertions) | **Accepted.** | item 2 |
| **D20C4-A-2** (NON-BLOCKING; rev 8 "One lock" inventory names removed calls) | **Accepted.** | item 3 |

## 1. Replacements

**Item 1. T-S6 (replaces C3 §1.10a's T-S6 row; D20C4-S-1).** The release entry `{evaluation_id, result, commitment, released_at}` (C2 §1.3) and the RESULT delivery file `{evaluation_id, result, released_at}` (C4 item 2) are different records. They do not have one shape. The row becomes:

> "Each of the two record types, the release entry and the RESULT delivery file, has one fixed shape for every FAIL cause: crash, deadline, technical and performance FAIL. For a given evaluation, neither record's bytes depend on which cause produced the FAIL. Their shared fields `evaluation_id`, `result` and `released_at` agree." (TC-6)

**Item 2. T-S2 and T-S1 (replaces C4 item 6, rows 1 and 4; D20C4-A-1).** `release` reads the clock **after it acquires `L_store`**, not when it is called (C2 §1.3). A call that waits on the lock can therefore pass `R_0` while it waits. Also, a call that waits for an append still answers by its own return contract. For example, `sign_permit` correctly refuses when there is no released PASS and no RESULT delivery.

| C4 item 6 row | Becomes |
|---|---|
| T-S2 | "a concurrent `release` whose clock reading under `L_store` is before `R_0` is refused (`STOPPED`, logged) and shows nothing; one whose reading under `L_store` is at or after `R_0` waits for the finish's hold and then shows its result". The test fixes the clock on each side of `R_0` while the call holds the lock, so it does not depend on when the call was made. T-S2's clock advance past `R_0` stands. |
| T-S1 | "each concurrent reader-row, `release`, `sign_permit` and `begin_read` call waits until the append is durable, then answers from the durable state by its own return contract; none answers from state from before the append". |

**Item 3. Rev 8 "One lock" inventory (replaces the list in rev 8 l.75, "The store takes it for: … steps 2-4 of `mark_finished`"; D20C4-A-2).** The list becomes:

> "The store takes it for: `begin_read` (including the `R_0` recovery lookup), rejection appends, `release`, `record_delivery`, `sign_permit`, revision and invalidation appends, reader rows; `verify_replay`, reconciliation, startup; the read gate's entitlement check; and **steps 2-4 of `mark_finished`** (with C2 step 2a)."

`state`, `guard_state` and `insert_release` no longer exist (C2 §1.10, which replaces rev 8 B1 and rev 6 l.113). The rest of that paragraph stands. `NOT_YET` takes no lock (C2 §1.2 item 1). As Astra notes, rev 8 l.99's `visible_from` is an internal insert timestamp that C4's projection withholds from the reader. It is not a reader visibility rule, and nothing here changes it.

## 2. Findings, remaining, unauthorised, self-check

**New findings** (continuing):
- **D20L-101 NON-BLOCKING (applied; item 1).** T-S6 claimed one shape for two different records (D20C4-S-1).
- **D20L-102 NON-BLOCKING (applied; item 2).** The T-S2 and T-S1 assertions were keyed to the call, not to the under-lock check or return contracts (D20C4-A-1).
- **D20L-103 NON-BLOCKING (applied; item 3).** The rev 8 lock inventory named removed calls (D20C4-A-2).

**Remaining:** as C2 §5. No further re-check is planned for this text-only erratum, because both C4 reviewers already accepted the mechanism and asked only for these wording fixes. If the owner wants one, it is a re-check of C5.

**Unauthorised:** as C2. `KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.

**Self-check:**
- one file written in this step;
- all 3 C4 findings answered (S-1, A-1, A-2);
- new findings D20L-101..103, no gaps;
- no new record type, lock, operation, role or rule; owner questions unchanged.
