# Governance review of the FP3 supplementary acceptance draft (54b0197)

Agent `senior-statistical-governance`, read-only, checkout `aqt-freeze-sheet` at `54b0197`, prompt `FP3_SUPPLEMENTARY_ACCEPTANCE_REVIEW_PROMPT.md`. Model reported by the agent: Claude Fable 5.1 (`claude-fable-5-1`). Received 2026-10-25. Report verbatim below (harness indentation removed). Dispositions: `ADJUDICATION_FP3_SUPPLEMENTARY.md`.

---

**Observed model:** Claude Fable 5.1 (`claude-fable-5-1`). Read-only review of `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch freeze-sheet, head `54b0197`. Not an acceptance or a signature; it activates nothing.

**Verdict: FIX.** Two blockers, both in the wording. The drand facts in the draft are correct.

## Checked myself (calculated, not just read)
- **Preregistration hash:** working tree = index blob = `ffadd2b5…` (eol=lf by attribute), and the value appears in `ACCEPTANCE_RECORD.md`.
- **Source record:** the quicknet `.info.json` hashes to `3e690bc5…` three ways: working tree, `HEAD` blob, and a fresh fetch today from `https://api.drand.sh/<hash>/info`. All three are the same bytes. The file has no line endings (`i/none w/none`), so the recorded value is portable.
- **Rule 2 table vs the stored file:** chain hash, public key (192 hex), scheme `bls-unchained-g1-rfc9380`, period 3 and genesis 1692803367 all match exactly. A key with one character changed does not match.
- **Randomness:** for rounds 1,000,000 and 33,372,977 (fetched from api.drand.sh; round 1,000,000 also from drand.cloudflare.com, identical), `randomness = SHA-256(48 raw signature bytes)` matches. SHA-256 of the hex text does not.
- **Round time:** the served latest round (33,372,977 at Unix time 1792922295) matches genesis + (r−1)·3. The alternative genesis + r·3 would give 33,372,976.

**Not available:** BLS signature verification (no `py_ecc` or `blst` in the venv); how the chain hash is derived from the info fields; any statement from docs.drand.love (its pages load content by JavaScript and returned no text). These stay `UNVERIFIED_EXTERNAL_ASSUMPTION`, including the "League of Entropy mainnet" label; api.drand.sh lists quicknet as one of its 3 chains.

## Against my opinion's §4 step 1
| Element | Status |
|---|---|
| Scope | present, but misdescribed (G2) |
| Chain values and info SHA | correct |
| Round rule | correct |
| Verification rule | present, but loose (G4) |
| **Missing output, judged by existence not retrieval** | **not met (G1)** |
| Attempt 2 after a drand void | correct |
| Permanent halt | correct |
| No-change, prospective and C2 statements | present |

Steps 2–3 (two committed reviews; signed commit pushed before G) are only partly reflected (G3).

## Findings

**FP3S-G1 — BLOCKER — Rule 5 (missing output).**
- **What is wrong:** sentence 1 makes "exists" depend on someone obtaining and recording a verifying output within 7 days; sentence 3 makes "void" depend on no source being able to supply one. These two do not cover every case. Example: the round was published, but nobody recorded a fetch within 7 days; it is then neither shown to exist nor void.
- **Why it matters:**
  - It contradicts the owner's item 3 ("judged by whether it exists, not whether your laptop could fetch it").
  - The window is tight in practice. The round is fixed only at the freeze read, about day 7 after acceptance, and the window ends about day 8, so a laptop offline on that one day decides the case.
  - It can be gamed. Anyone can fetch the published output and run the frozen code privately. If the result is bad, they record no fetch, or simply assert "no source could supply". That gives a void and then a no-change re-post with fresh randomness (Rule 6): a free second draw.
  - O-6a voids before the run are different: they are decided before any randomness is known, or are on-chain facts. Here nothing requires evidence of a void.
- **Partly my fault:** my own wording ("shown to exist") pointed toward an evidence test; the right conclusion (judge by existence) was reached with loose wording.
- **Minimal repair (proposal for the owner):**
  - "The output exists unless, after the 7 days end, no public drand source serves a verifying output for the round. A void needs a record of failed requests to at least two independent public drand endpoints, made after the 7 days, with raw responses and times, committed and pushed before anything else is done for the attempt."
  - "If any public source serves a verifying output when that record is made, there is no void."
  - "A verifying output obtained at any time may be used, because it is unique."

**FP3S-G2 — BLOCKER — Rule 1 (scope statement).** Rule 1 says the record "fixes … what §8 calls the C2 drand chain". Rules 5–7 add what the preregistration does not contain: a new ground for voiding, and a no-change attempt 2 after a drand void (preregistration §4 allows a no-change re-post only after an O-6a void). **Failure:** at the C2 signing, a reviewer reads Rules 5–7 as going beyond the record's own stated scope and sets them aside. **Repair:** "It fixes that chain and adds Rules 5–7, which the preregistration does not contain, as terms of this supplementary acceptance."

**FP3S-G3 — NON-BLOCKING — Header and Rule 10.** Missing: pushing before G (Git commit dates are set by the author, so the claim in Rule 8 that the record came first rests on GitHub's push time), and committing both different-model reviews before adoption (my step 2). **Repair:** in the header, "committed with signature and pushed before step G, after both reviews are committed".

**FP3S-G4 — NON-BLOCKING — Rule 4 (verification).** It does not say:
- that the signature must verify *for that round number*;
- that the hash is over the raw 48 signature bytes, recorded as 64 lowercase hex;
- that the computed value overrides any `randomness` field in a response;
- that the verified output is committed before the held-out run (as DF5-2).

Only one reading reproduces drand's own value (calculated above), and C2 R-7's "randomness field" is the same value for quicknet, so the risk is narrow. **Repair:** add the four clauses.

**FP3S-G5 — NON-BLOCKING — Rule 3 (inherited from prereg §8 / O-6a §5).** `T_Qn` is a 14-digit UTC CDX timestamp, but the formula works in Unix seconds; the conversion is never stated. Worked example: T = 20261101000000 gives 1793491200; T+24h = 1793577600, which is exactly the scheduled time of round 33,591,412. "At or after" picks that round; a strict "after" would pick 33,591,413. **Repair:** "T_Qn read as UTC and converted to Unix seconds; +24h = +86400 s".

**FP3S-G6 — NON-BLOCKING — Rule 8.** "Nobody can know any future round's output" overstates: it holds only under drand's threshold assumption (no colluding group of operators at or above the threshold). **Repair:** add that qualifier.

**FP3S-G7 — NON-BLOCKING — reviewer notes.** The notes call Rule 5's evidence test "a new owner choice". The owner chose "existence", so the evidence test is an AI drafting choice until adopted. **Repair:** label it as an AI proposal and point to G1.

**FP3S-G8 — QUESTION — facts not verified.** BLS verification, the chain-hash derivation and the "mainnet" label are unverified. **Proposal:** before G, the pinned tool (FP3-R5) verifies a historical quicknet round, including a negative test with a changed signature, and its result is committed.

## Authority
Nothing in the draft claims to amend, activate or sign. The status header and Rule 1 ("not a §4 amendment") are accurate. Rule 9 is a commitment the owner makes about his own future use; it cannot bind the C2 amendment and does not claim to, which matches my opinion. The route still rests on judgement, not express text (GOV-FP3-3 stands).

## Decisions left to the owner
The final wording, especially the void criterion in G1; adopting and signing the record, then pushing it.

## Not authorised
Step G, the post, any edit or commit made for the owner, amendment, activation, acceptance, changes to frozen files or hashes, merge, cycle start, promotion, trading.

Not checked: the Codex review (run separately), BLS cryptography, the drand docs text. Risk: until G1 is fixed, a drand void can be used as a free second draw.
