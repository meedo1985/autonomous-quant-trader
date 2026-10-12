# Owner decision: D-19 preregistration accepted; Q-1; build and pilot go-ahead

**Date:** 2026-10-04
**Authority:** The owner decided this in a Claude Code session. Claude Opus 5.5 (`claude-opus-5-5`) asked the questions and recorded the answers.

## Decided object

`PREREGISTRATION.md` revision 6, commit `e1e4e7e`.

## Reviews (R19-2)

| Round | Fable | Sol |
|---|---|---|
| 1 | DF1 `f54e84e` | DS1 `90029a4` |
| 2 | DF2 `552af72` | DS2 `169985e` |
| 3 | DF3 `2c2b11b` | DS3 `807ee4a` |
| 4 | DF4 `c26e59e` | DS4 `c518e94` |
| 5 | DF5 `df65001` (READY WITH FIXES; no further round needed) | DS5 `e1e4e7e` |
| 6 | — | DS6 `0ac488d` (**READY**, no findings) |

Owner decision U-1 was taken during these rounds, at `8e04dd8`. **No human statistician reviewed this** (R19-2). That makes the review weaker, and it is disclosed.

## Exchange (verbatim)

### Question 1

> "Accept the D-19 calibration plan (revision 6, commit e1e4e7e)? It fixes in writing, before any result exists, how the 'is this edge just luck?' test will itself be tested by simulation: about 380 scenarios; a no-edge strategy may wrongly pass at most 2.5% per family; checks that depend only on returns may give 'no result' at most 1% per cycle; a pass/fail rule with no re-tuning; failure means promotion stays blocked. Reviewed by Fable and Sol through six rounds. No human statistician checked it (weaker, disclosed)."

**Options:**
- "Accept (Recommended)": "The plan is frozen as written. Nothing is built or run by this; that is the next question."
- "Not yet": "Keep it as a proposal; nothing changes."

**Answer:** **"Accept (Recommended)"**

### Question 2

> "Q-1: Before the final calibration test runs, the frozen calibration settings' fingerprint is published once in a Bitcoin transaction (same rules you approved for O-6a, separate key per attempt, at most 2 attempts). This stops anyone re-rolling the final test until it passes. Cost: two Bitcoin network fees per attempt plus any withdrawal fee, paid only when that point is reached (after the build and development runs)."

**Options:**
- "Bitcoin post (Recommended)": "As specified in the plan §4. You make the key, fund it, and post at the freeze, like O-6a."
- "Keep blocked": "Decide later; the final test cannot run until this is decided."

**Answer:** **"Bitcoin post (Recommended)"**

### Question 3

> "Separately (your 2026-10-02 rule needs your go-ahead for any build): may I build the calibration engine and run a small MEASURED PILOT on this computer? The pilot only measures speed and cost (largest cell, a median cell, one joint cell, the threshold run, one screen and one mapping run on exploration data). It produces no certification and no trading result. The build is protected code, so it goes through a different-model review and your PR review before merge. The full run is a later decision after you see the measured cost."

**Options:**
- "Yes, build + pilot (Recommended)": "Build the engine on a branch, review it, run the pilot locally, then report measured cost before any full run."
- "Not now": "Stop at the accepted plan; nothing is built."

**Answer:** **"Yes, build + pilot (Recommended)"**

## Effect

1. **The preregistration text is accepted (rev 6, `e1e4e7e`).** Its claim, cells, rules and acceptance rule are frozen before any result exists.
   - **Completing acceptance.** §4 says `A_Q1`, `F_Q1`, `D_Q1`, `A_Q2` and `F_Q2` are fixed "at the preregistration's acceptance", but these keys and coins do not exist yet. Acceptance is therefore completed by a committed record of those values, made by the owner **before the development phase starts**, and so before any qualification post.
   - **No development run without that record.** Development (§5) may not start until the record exists. This keeps the purpose of the rule: no key can be chosen after any held-out-relevant information exists.
2. **Q-1 (Bitcoin post).** The qualification-object commitment channel is the one specified in §4: O-6a SPEC rev 5 by substitution, with prefix `AQTQ1`, one key and coin per attempt, and at most two attempts. `<<OWNER Q-1>>` is resolved.
3. **Build and measured pilot are authorized (R19-1, R19-2).**
   - **What may be built.** The calibration engine, on a branch.
   - **How it merges.** It is protected code under §16, so it needs a different-model review and the owner's PR review before merge.
   - **What the pilot is for.** It runs on this computer and only measures speed and cost, on the §10 items. It produces no certification result.
   - **What is not authorized.** The threshold run in full, the development phase, the held-out phase, and any rented compute. Each needs a later owner decision, after the measured cost is reported.

## Not changed by this decision

- D-11..D-13 and D-20 remain open.
- Nothing is activated.
- No frozen file and no `HUMAN_DECISION_MATRIX.md` is edited.
- No cycle, trial, confirmation or lockbox access, promotion, deployment or trading is authorized.
