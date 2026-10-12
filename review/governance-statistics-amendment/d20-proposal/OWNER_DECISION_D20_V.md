# Owner decision: D-20 (partial), method V for the DSR replicate Sharpes; compute route

**Date:** 2026-10-04
**Authority:** The owner decided in a Claude Code session. Claude Opus 5.5 (`claude-opus-5-5`) asked the questions and recorded the answers.

## Decided object

`V_BINDING.md` revision 3, commit `309f75b`. The engine that implements it is on branch `d19-calibration-engine`, commit `8650603`.

**Reviews (R19-2):**

| Reviewer | Review | Commit | Verdict |
|---|---|---|---|
| Fable | VF1 | `df2bad4` | SOUND WITH FIXES |
| Fable | VF2 | `fe9b0bc` | READY WITH FIXES |
| Sol | VS1 | `a39fc39` | SOUND WITH FIXES |
| Sol | VS2 | `8ab8d78` | NOT READY |
| Sol | VS3 | `b4ab0f0` | READY WITH FIXES, non-blocking |

The VS3 fixes are applied in `8650603`.

## Exchange (verbatim)

### Question 1

> "Adopt method V for the inside-the-bootstrap Sharpe of the DSR test? This (1) reads one sentence of Annex B as covering only the averages across the 2,000 replicates, not each replicate's Sharpe — if you disagree, it is a change to Annex B; (2) makes V, run on one pinned computer setup with automatic checks, the official calculation for both calibration and real evaluation (if that setup can't be recreated later, the result is void and must be requalified); (3) makes frozen test cases the reference for exact agreement, with the original calculation also run and reported on every real evaluation; if they disagree, V's result counts and the difference is disclosed. V can give slightly different numbers or availability than the original method in rare near-degenerate cases. Reviewed: Fable (2 rounds) and Sol (3 rounds), last verdicts 'ready with fixes', fixes applied."

| Option | Description shown |
|---|---|
| "(A) Adopt V (Recommended)" | "The full calibration is then about 12,000 CPU-hours (measured on mains power; the laptop is currently on battery, which roughly halves its speed)." |
| "(B) Keep original calculation" | "Measured ~65 s per simulated run at the largest scenario: tens of thousands of CPU-hours, so a much larger rented-compute budget or a far longer local run." |
| "Keep blocked" | "Decide later; the calibration cannot run until this is decided." |

**Answer:** **"(A) Adopt V (Recommended)"**

### Question 2

> "If V is adopted: how should the ~12,000 CPU-hour calibration be run? (No money is spent by this answer.)"

| Option | Description shown |
|---|---|
| "Get a rental quote first (Recommended)" | "I prepare an exact plan and price for renting cloud computers (~1 week), you then approve or refuse the spend. Nothing is rented without your explicit OK." |
| "Run on this laptop" | "About 3 months of continuous running on mains power; the laptop's 8 GB memory may interrupt runs and it will be busy the whole time. No money." |
| "Decide later" | "Stop after recording the V decision; no run planned yet." |

**Answer:** **"Get a rental quote first (Recommended)"**

## Effect

1. **D-20, in part.** The DSR replicate Sharpes `S*_{b,j}` and `S°_{b,j}` (Annex B §2.3) are computed by **method V**, as defined in `V_BINDING.md` rev 3 §1. V is bound by the code hash of `_replicates_v` and by the pinned runtime identity recorded in the D-19 qualification object. The rest of D-20 stays open.
2. **Annex B §2.3 clarification.** The `fsum`/two-pass sentence governs `S0` and `var_b`. It goes into the amendment as a new R-row.
3. **P18-6 reference contract (clause A-V1).** The reference is the frozen reference vectors. The Task 12 numerics are also computed and reported on every real evaluation. If the two disagree, V governs and the difference is disclosed.
4. **Runtime.** V refuses to run until the frozen runtime identity has been checked. If that runtime cannot be recreated, the result is void and must be requalified.
5. **Compute route.** A rental plan with a price is prepared for the owner's approval. **Nothing is rented, and no money is spent, without the owner's explicit approval of that plan.**

## Not changed by this decision

- The rest of D-20, and D-11..D-13, stay open.
- Nothing is activated.
- No frozen file and no `HUMAN_DECISION_MATRIX.md` is edited.
- No calibration run, cycle, trial, data access, deployment or trading is authorized.
