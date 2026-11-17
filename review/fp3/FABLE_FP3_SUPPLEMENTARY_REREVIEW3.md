# Governance re-review 3 of the FP3 supplementary acceptance draft, revision 4 (802be05)

Agent `senior-statistical-governance`, read-only, checkout `aqt-freeze-sheet` at `aabeae8`, prompt `FP3_SUPPLEMENTARY_REREVIEW3_PROMPT.md`. Model reported by the agent: Claude Fable 5.1 (`claude-fable-5-1`). Received 2026-10-25. Report verbatim below (harness indentation removed).

---

**Observed model:** Claude Fable 5.1 (`claude-fable-5-1`). Read-only re-review of `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch freeze-sheet, HEAD `aabeae8` (working tree clean; draft unchanged since `802be05`). Independent reviewer, not an authority: the owner adopts and signs; nothing here is an acceptance, signature or activation.

**Verdict: ACCEPT.** No blocker. Two non-blocking findings below are worth settling before adoption, but neither stops it.

## 1. Fidelity to the owner's choices
- **R3-strong (item 4):** the status block keeps all four conditions (two committed reviews each ending in ACCEPT; owner adoption; his own signed, UTC-dated commit; push before G).
- **quicknet (item 2):** Rule 2 is unchanged; I matched it against the source record and live endpoints earlier this session.
- **No time limit (item 7):** Rule 5 says the run waits for the unique output from any source, at any time, with no void, failure or substitute round. Rule 6 matches item 7 (if the chain stops, the attempt waits for a new formal decision).
- **Superseded items:** items 3, 5 and 6 are correctly dropped; their rules are withdrawn, and Rule 1 now says "Rules 5 and 6".

## 2. Soundness and consistency
- **Rule 5 cannot be gamed through outcome choice.** The output is unique (BLS uniqueness is an `UNVERIFIED_EXTERNAL_ASSUMPTION`, standard for the scheme), and with no void for a missing output there is nothing left to choose.
- **This removes the problem behind FP3S3-G1/G2 and Codex R1–R3**, which all rested on needing proof of *when* drand published. I agree with the adjudication that they now have no subject. FP3S3-G5 is fixed (header "Revision 4").
- **Preregistration §4 "Timing"** already makes the run wait for "the publication of the drand round"; Rule 5 adds no new condition, only removes a time limit.
- **Other §4 rules are untouched:** O-6a voids and failures, DF5-1 keys, D_Q2 and the §8 anchor are unchanged.
- **Sheet:** step K still has the 7-day stop. It defers to "the rule FP3 settles", and the Notes list its update. This is non-binding, and the sheet is not usable before G anyway.
- **C2:** the Notes keep the C2 draft's own 7-day rule for C2 and confine this rule to D-19.

## 3. Earlier resolved findings
All still resolved: verification (round number, raw 48 bytes, computed value overrides the response, committed before the run); the round rule and T_Qn conversion; the scope statement; the prospective claim with the threshold qualifier; the binding conditions.

## 4. Findings

**FP3S4-G1 — NON-BLOCKING — Rule 6.**
- **Defect:** "released" is undefined (void, failed, or what follows?). "Under the Constitution's rules" does not say which kind of act (an owner acceptance as in R3, or a §4 amendment). The guard "made while no output for the attempt's round exists" requires proving a negative at a given time, which is the same proof that three review rounds showed cannot be obtained cleanly from outside.
- **Failure:** the chain halts and a release is decided; later it emerges that a relay had served round r before the decision. The release's validity then turns on proving when that happened.
- **Why it does not block:** any release needs a future formal decision, which will itself be reviewed; under the guard the decision is blind to the outcome; and a lie requires a live chain, whose public endpoints would show latest ≥ r at the time.
- **Proposal (owner decision; I am not changing his choice):** state now that a release counts the attempt as *failed* (namespace burned, key used, any further attempt needs a recorded change, §4 step 7). A release then gains nothing over running and failing, so the timing proof is no longer needed. Otherwise keep the guard and accept this residual explicitly.

**FP3S4-G2 — NON-BLOCKING, inherited (preregistration §4 DF5-2; not a defect of this draft).**
- **Defect:** nothing bounds the time between obtaining and committing the output and starting the held-out run. During that gap, someone who knows the output could look for an O-6a earlier-capture invalidation; found before the start, that gives a void and a no-change re-post.
- **Why it is narrow:** the earlier capture must already exist at the Internet Archive and must give a different round. Rule 5 does not widen the gap, because the wait ends when the output is obtained.
- **Repair belongs in the sheet's step K/L rewrite, not this record:** for example, the run starts within a fixed period after the output is committed, and the DF5-2 check is committed at the same moment.

## Decisions left to the owner
FP3S4-G1 (release as failure-equivalent, or keep the guard and accept the residual); the final wording, adoption, signed commit and push before G.

## Not authorised
Step G, the post, any edit or commit, amendment, activation, acceptance, frozen-file or hash changes, merge, cycle start, promotion, trading.

**Not checked:** Codex re-review 3; BLS cryptography (no library available). I did not re-fetch drand endpoints this round, because Rules 2 and 4 are unchanged since I verified them.

**Risk:** my ACCEPT covers the text only. Before G, the pinned verification tool must verify a historical quicknet round, including a negative test with a changed signature, and that result must be committed.
