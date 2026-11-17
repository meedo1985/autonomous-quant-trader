# Owner decision: R-14a (exception for the lockbox and confirmation modules)

**Decision by:** the owner, in the Claude Code session on 2026-10-31, answering one question in one form.
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). The AI made no decision.
**Basis:** `PROPOSAL_REV2.md` (f1be832) and `PROPOSAL_REV3.md` (erratum, 36ecee3), on the background in rev 1 `PROPOSAL.md` §0.

**Reviews (R19-2, two families):**
- rev 1: `SOL_REVIEW_23300C4.md` and `ASTRA_REVIEW_23300C4.md`, both FIX;
- rev 2: `SOL_RECHECK_F1BE832.md` and `ASTRA_RECHECK_F1BE832.md`, both ACCEPT WITH NOTES with 0 BLOCKER.

**Disclosed before the decision:**
- both re-checks found no blocker;
- the three notes were applied in the rev 3 erratum, which was not re-reviewed;
- no human statistician reviewed this.

**Earlier direction:** the owner's answer to PFS-S-1, "Exception like Q4 (Recommended)" (rev 1 §0).

**How the question was asked:** the form summarised R-14a. It said that two later files may be used in C2 (the lockbox module and the confirmation runner), each one reviewed file with its hash in the signed C2. It said the row changes code placement only, not data access; that each file follows a written input-to-record contract, so nothing is silently dropped or re-paired; and that the confirmation runner checks the beacon seeds itself. It stated the cost:
- the two files are frozen later than the Bitcoin-posted object;
- some statistics code, such as the lockbox bootstrap, is not covered by that post;
- public prices or a code mistake could still affect a result, and review and tests reduce that risk without guaranteeing against it.

## Answer (option label chosen, verbatim)

**"Adopt R-14a (Recommended)".** The option's summary read: "Binds only through your signed C2 after human review. Both modules must be built, with contracts and tests, before you sign C2. The freeze doesn't wait for them."

The options not chosen were "Freeze all code first" and "Keep blocked".

## Recorded meaning

- **R-14a is decided as rev 2 with the rev 3 erratum.** It replaces D-20 Q4's separate "narrow R-14 exception" with one row covering both modules. It binds only as a row of the owner's signed C2, after the required human review.
- **Conditions carried forward:**
  - **Before signing C2:**
    - build both modules, each with its input-to-record contract (item 5, including rev 3's allocation of A7's confirmation-side work), consumer-boundary tests, an independent review and the owner's §16 PR review;
    - put their hashes in the signed C2 protocol bytes (item 2 as amended);
    - write the R-8 extension (item 8).
  - **Before step G:** the pre-freeze `screen.py` change (Q2(ii), Q5) on branch `pre-freeze-screen-q2-q5`, as already required.
  - **Unchanged:** D-11's and Constitution §7/§7a's access rules, and S4.
