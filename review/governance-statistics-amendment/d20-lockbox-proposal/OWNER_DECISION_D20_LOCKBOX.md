# Owner decision: D-20 lockbox bindings (option C, release on request; Q2-Q5)

**Decision by:** the owner, in the Claude Code session on 2026-10-31, answering nine questions in three forms (QC1, QC2, QC3, Q7; then Q2(i), Q2(ii), Q3, Q4; then Q5).
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). The AI made no decision.
**Basis:** `OWNER_QUESTIONS_OPTION_C_DRAFT.md` at 35df0fd, which holds the full questions. Option C is `OPTION_C_PROPOSAL_REV2.md` + `_REV3.md` + `_REV4.md` (at 5599056) + `_REV5.md` (erratum, a3c57f6), on top of `PROPOSAL_REV8.md`'s reading side. Q2-Q5 come from `PROPOSAL_REV4.md` §3 as amended by `PROPOSAL_REV5.md` §3. The R19-2 re-checks of C4 by gpt-6-sol and gpt-6-astra are `SOL_OPTION_C4_REVIEW_5599056.md` and `ASTRA_OPTION_C4_REVIEW_5599056.md`. Both are ACCEPT WITH NOTES with 0 BLOCKER.
**Disclosed before the decision:** the sheet's status said that both C4 re-checks found no blocker, and that their three wording notes (D20C4-S-1, D20C4-A-1..2) are fixed in the text-only C5 erratum, which changes no question. C5 itself was not re-reviewed. Per R19-2, no human statistician reviewed any of it.
**How the questions were asked:** each option label was shortened to fit the form. Each option carried a one-line summary of the sheet text, and each question carried a short summary of its "What it means" text. The mapping below names the sheet option each answer selects.

## Answers (option labels chosen, verbatim)

1. **QC1 (release on request): "Release on request (Recommended)".** Sheet option "Switch to release on request (Recommended)". The D-12 rule changes listed under QC1 go into C2: the daily posting timetable and the uptime-counted 72 hours are replaced, and the signer's checks are reworded.
2. **QC2 (detail rules): "Adopt (Recommended)".** Sheet option "Adopt (Recommended)". This does not settle D11-15 or S4 (who handles incidents).
3. **QC3 (timing and refusal hints): "Accept exception (Recommended)".** Sheet option "Accept the exception (Recommended)". This is the proposed Constitution §7 row in C4 item 4, signed in C2 after human review.
4. **Q7 (when a save counts): "Accept draft rule (Recommended)".** Sheet option "Accept the draft rule (Recommended)". A save counts at the clock check under the lock, and "done" is shown only once the save is on disk. C2 writes this meaning into the D-12 rules "finished before the deadline" and "attested by day 255".
5. **Q2(i) (start): "Start flat (Recommended)".** Sheet option "Strategy and benchmark start with no position; each pays its entry cost at its first permitted entry (Recommended)".
6. **Q2(ii) (end): "Last hour's close (Recommended)".** Sheet option "Use the last hour's own closing price (Recommended)". Time-sensitive: it must be done before the freeze (step G).
7. **Q3 (forecast seed): "Post-protected seed (Recommended)".** Sheet option "The post-protected seed, as for G-1 (Recommended)".
8. **Q4 (where the lockbox code lives): "Separate module (Recommended)".** Sheet option "One separate reviewed lockbox module, its fingerprint in the signed C2, with a narrow R-14 exception (Recommended)".
9. **Q5 (strategy fit seed): "Protocol seed (Recommended)".** Sheet option "The protocol's seed, turned into an ordinary number in a fixed way (Recommended)". Time-sensitive: it must be done before the freeze.

## Recorded meaning

- **D-20 is decided as option C with the recommended option on every question.** Nothing binds yet. Every item binds only through the owner's signed C2 amendment, after the required human review (Constitution formal process, §16 for protected components).
- **Carried forward as conditions (not decided here):**
  - **Before the freeze (step G):** one reviewed `screen.py` change carrying the Q2(ii) confirmation-run end and the Q5 estimator seed, made in the same change. The freeze must be built from the commit that contains it. If the freeze comes first, C2 stays blocked until a formal amendment.
  - **Before signing C2:** build and review the separate lockbox module (Q4), and put its fingerprint in C2.
  - **The signed C2 must carry:** the option C rows, including the D-12 changes from QC1; the QC3 Constitution §7 row (C4 item 4); the Q7 meaning; the Q3 seed row; the Q4 R-14 exception; and any Q5 row that is needed.
  - **Still open:** S4 (channel, clock, reconciliation, governance actions, and who handles incidents and what they may see; if that person is the owner, a separate Constitution question comes first), and D11-15.
  - **§16 review** of each build: the lockbox store, publisher, signer and access tooling.
