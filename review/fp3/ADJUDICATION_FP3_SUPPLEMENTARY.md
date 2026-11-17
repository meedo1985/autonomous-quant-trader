# Adjudication: reviews of the FP3 supplementary acceptance draft (54b0197)

Records: `FABLE_FP3_SUPPLEMENTARY_REVIEW.md` (claude-fable-5-1, FIX, FP3S-G1..G8) and `SOL_FP3_SUPPLEMENTARY_REVIEW.md` (gpt-6-sol, FIX, FP3S-R1..R4). Adjudicated by Claude Opus 5.5 (the drafter), 2026-10-25. Repairs: draft revision 2.

| ID | Sev | Disposition | Repair in revision 2 |
|---|---|---|---|
| FP3S-G1 / FP3S-R1 | blocker | **Accepted** (both reviewers, same defect): "exists" was tied to a timely fetch, "void" to an unprovable negative, with a gap between them and a free-second-draw incentive. | Rule 5: an output obtained from any source at any time is used; void only by a committed and pushed void check after cutoff `C` (scheduled time + 604,800 s) at two or more independent endpoints, final only after a second check at least 24 h later; a later-shown false void counts as failed. Labelled as an AI drafting proposal. |
| FP3S-R2 | major | **Accepted.** | Rule 4: copies of this round from any source are allowed; Rule 5 forbids only a substitute beacon, chain or randomness source. |
| FP3S-G2 | blocker | **Accepted.** | Rule 1: fixes the chain **and adds Rules 5-7** as terms of this supplementary acceptance. |
| FP3S-G3 / FP3S-R3 | non-blocking / major | **Accepted.** | Status block: four conditions before G (two committed reviews ending in ACCEPT, named; owner adoption; owner's own signed, UTC-dated commit; push, with GitHub's push time as timing evidence). Rule 10 says "pushed before step G". |
| FP3S-G4 | non-blocking | **Accepted.** | Rule 4: verifies for that round number; SHA-256 over the raw 48 signature bytes, 64 lowercase hex; computed value overrides any `randomness` field; verified output committed before the run. |
| FP3S-G5 | non-blocking | **Accepted.** | Rule 3: `T_Qn` read as UTC, converted to Unix seconds; +86,400 s; "at or after" includes an exact match; round time formula. |
| FP3S-G6 / FP3S-R4 | non-blocking / minor | **Accepted.** | Rule 8: the checkable timing claim (no object, no post, no `T_Qn`, no selected round at push time) plus drand's threshold assumption. |
| FP3S-G7 | non-blocking | **Accepted.** | Notes: Rule 5's procedure labelled an AI drafting proposal. |
| FP3S-G8 | question | **Accepted as a pre-G condition.** | Notes: the pinned tool verifies a historical quicknet round with a negative test, result committed, before G. |

Also: Rule 2 no longer calls quicknet "League of Entropy mainnet" (unverified label, FP3S-G8); it says "served as one of the mainnet chains at `api.drand.sh`".
