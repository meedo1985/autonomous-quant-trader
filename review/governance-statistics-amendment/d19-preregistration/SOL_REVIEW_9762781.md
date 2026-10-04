# Sol review BS3 of the D-19 preregistration §13 rev 7d at `9762781`: SOUND WITH FIXES

Date: 2026-10-04. R19-2 independent statistical narrow re-review, run with Codex CLI (`codex exec`, model requested `gpt-5.6-sol`, reasoning effort high), read-only. The drafter is Claude Opus 5.5. The reviewer's final report is reproduced below unchanged.

---

**Model identity:** OpenAI Codex, GPT-5 family; no finer serving-model identifier is exposed in this session.  
**Commit reviewed:** `976278111d4e5ee43578d52effa8a3a1922a0b70` (`docs/d19-recommendation`)  
**Verdict:** **SOUND WITH FIXES**

Not every BF2/BS2 finding is fully resolved. The two-hash ordering, chain heads, explicit overrides, C2-only/A-B7 treatment, O18-4 owner-answer requirement, classifier arithmetic, and reference-suite rules are repaired. BF2-1 and BF2-2/BS2-4 retain issues.

- **BS3-1 — MAJOR — §13 item 6, lines 524, 545, 547.**  
  **Problem:** CPU model is part of the frozen runtime identity; chunks require exact identity equality; yet chunks may count after the CPU model changes. These rules cannot all hold and conflict with P18-6/A-V1’s frozen-runtime contract.  
  **Evidence:** A model change necessarily changes the stated identity even when dispatch features and vectors match.  
  **Fix:** Make any CPU-model change stop new work until the complete frozen identity is restored; alternatively, an owner-decided runtime contract must move CPU model outside the equality identity. Record microcode as host provenance.

- **BS3-2 — MAJOR — §13 item 3, line 486.**  
  **Problem:** The demotion table is labelled as a *cell* probability, but it is `P[Binomial(12000,p) ≥ 3]` for one `U_G` test. QJ has two family `U_G` tests, and DSR availability is another demotion route.  
  **Evidence:** At `p=5×10⁻⁵`, the single-test probability is `0.02311`; for two QJ tests the union is between `0.02311` and `0.04622` (`0.04569` if independent), before DSR demotion.  
  **Fix:** Relabel the table per-`U_G` test and disclose QJ union bounds plus the separate DSR contribution.

- **BS3-3 — MAJOR — §13 item 6, line 556.**  
  **Problem:** The fixed “about 300” add-on is not justified when the number of 40k escapes is data-dependent.  
  **Evidence:** Each ordinary escape adds `20,000×4.5s ≈ 25` laptop-core-hours, about 50 for QJ; twelve ordinary escapes already consume the entire 300 before threshold and reported-only work.  
  **Fix:** State the estimate parametrically—base plus approximately 25 hours per ordinary escape and 50 per QJ escape—and provide re-pilot scenarios.

Numerical check passed: `τ_G(40k)=0.000451236`, critical count 32 at both `M=322` and `340`; development passes with at most two events. Escape changes each affected test’s `N_i` to 40k but does not add tests to `M`. At 40k, error critical count is 883; DSR is 97/96 for `M=322/340`. The escape and held-out logic are statistically valid.

No other conflict found with O18-4, P18-1…P18-7, A-B7, A-U1, or U-1. Withdrawing A-B7-EQ is sound for a C2-only object. O18-4’s unequal-`T` removal remains inactive until the separately recorded affirmative owner answer. The unresolved runtime contradiction reaches P18-6/A-V1.

`git diff --check` passed. No network or `data/` contents were accessed. This read-only response is not yet the committed review record required by repository policy.

Most of rev 7d is repaired, and the 40k escape works statistically.  
Do not accept it until the host-change rule and demotion-risk disclosure are corrected.  
The runtime estimate must show how many escaped cells it assumes.
