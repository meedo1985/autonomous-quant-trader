# Fable review of the broadened DSR method design rev1 at `6481f28` — SOUND WITH FIXES

Date: 2026-10-03. Anthropic-family review for R19-2; run in parallel with,
and without sight of, `SOL_REVIEW_6481F28.md`.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`); prompt
  `REVIEW_PROMPT_R1.md` (committed `773e30e`), prefix FB1.
- Model metadata: self-reported by the reviewer as `claude-fable-5-1`; the
  launch requested the `fable` model. Not independently verified through
  provider metadata.
- Findings: FB1-1..FB1-3 BLOCKER; FB1-4..FB1-10, FB1-12..FB1-17 NON-BLOCKING;
  FB1-11 QUESTION. Nothing is decided by this record; no finding is repaired
  here.

Below is the reviewer's final message, verbatim.

---

# Fable review FB1: broadened DSR method design, revision 1

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family (observed model ID). AI reviewer, no authority; closes no D-row, accepts no method.
**Commit reviewed:** `6481f28` (`DESIGN.md` diff to HEAD `773e30e` empty). Read-only; `SOL_REVIEW_*.md` not read; no edits, no network; calculations in-memory only (`.venv/Scripts/python.exe -B -`), shown in §2.
**Verdict: SOUND WITH FIXES.** The core idea — common day-index resampling of trial returns recentred to zero mean — is sound. Three blockers (FB1-1..FB1-3) must be fixed or put to the owner before B-1/B-2 are decided and before D-19 is designed. Skill verdict: `REVISION_REQUIRED`.

## 1. Answers

**Q1 — validity and failure points.** Valid for fixed K as T grows; not uniformly in finite samples. Recentring bias: none for the mean (under circular wrapping the resampled mean has expectation exactly the sample mean; §2(b)). MC error at B = 2000 is negligible (z moves about ±0.03–0.04 near z ≈ 2). Real failures: the block-length rule (FB1-1, FB1-4, FB1-5, FB1-15) and sparse columns (FB1-6). Infinite fourth moment is less dangerous than §5 says: at the recentred null the Sharpe is a self-normalised mean, which needs only finite variance (`UNVERIFIED_EXTERNAL_ASSUMPTION`, Giné–Götze–Mason type). The real exposure is the block-length input `psi`, whose `u²` term needs finite fourth moments when S ≠ 0 (FB1-5). High-dimensional validity of the bootstrap max at K = 80, T = 365 is `UNVERIFIED_EXTERNAL_ASSUMPTION`.

**Q2 — §1 defects.** AS-1: removed as T → ∞; in finite samples S0 shrinks by √f (FB1-1). AS-2: removed only by dropping the lifetime count, which collides with Constitution §9 (FB1-3). AS-3/P-7: old refusals gone but new ones appear (FB1-6, FB1-7); the 1% is still unshown. Serial dependence: addressed, with a downward bias growing with L/T (FB1-1). Heavy tails: addressed for D; remain in the block-length input (FB1-5).

**Q3 — D-16/D-17.** Statistically sound within a cycle under P18-0, agreeing with FR4-13 (`d18-proposal/FABLE_REVIEW_10BB125.md:87`). Conflicts with the uncited Constitution §9 line 106 (FB1-3). Lost: the only mechanism that raises the bar across eligible cycles; P(at least one lucky cycle) = 1 − 0.95^m: 9.75% at m = 2, 14.26% at m = 3, 22.6% at m = 5 (FB1-12).

**Q4 — B-3.** Within D-18, but for a different reason than given (FB1-10).

**Q5 — availability.** Ordered and fail-closed; not consistent with P18-3, which needs D for every trial (FB1-2), nor with the `U_ops`/`U_proc` split of P18-7 (FB1-7). `L <= T/4` can never fire (FB1-4). `T_min = 365` has no supporting calculation.

**Q6 — §3/§5 gaps:** FB1-12, FB1-14, FB1-16, FB1-17.

## 2. Calculations

**(a) Downward bias of the bootstrap variance, iid data.** Circular stationary bootstrap with restart probability p = 1/L, exact expectation in `Fraction`: `E[Var*(√T·mean*)]/σ² = (T−1)/T − (2/T)·Σ_{k=1}^{T−1}(1−k/T)(1−p)^k`, using E C(0) = σ²(T−1)/T and E C(k) = −σ²/T for k ≥ 1.

| T | L | E[Var*]/σ² | ratio f to L = 1 | false-pass at z = 1.96, K = 1 |
|---|---|---|---|---|
| 365 | 1 | 0.997260 | 1.000 | 2.500% |
| 365 | 5 | 0.975643 | 0.978 | 2.627% |
| 365 | 20 | 0.898855 | 0.901 | 3.139% |
| 365 | 58 (cap) | 0.734475 | 0.736 | **4.628%** |
| 1247 | 106 (cap) | 0.845109 | 0.846 | 3.573% |

Last column first-order: the variance ratio carried over to D.

**(b) Discriminating check.** N = 5, L = 2, x = (3, −1, 4, 1, −5): formula `6169/1000`; brute-force enumeration of all resampling paths `6169/1000` (equal); the wrong, non-circular treatment gives `40677/5000`. Resampled mean equals sample mean exactly (True). Naive 1 − L/T would give 0.841 at T = 365, L = 58, against the exact 0.734.

**(c) Cap makes the T/4 rule dead.** Cap `min(n, ceil(min(3√n, n/3)))` (`statistics.py:375`) exceeds T/4 only for 16 ≤ T ≤ 147; it is 58 at T = 365 and 106 at T = 1247.

**(d) MC error at B = 2000.** Relative SD of `var_b` √(2/1999) = 0.0316, of √D 0.0158; MC SD of S0 at most about 1/√2000 = 0.022 nominee SDs.

**(e) The z null distribution differs by cell.** K = 1: P(z ≥ 1.96) = 2.5%. K = 2 independent Gaussian: P(max − E max ≥ 1.96) = 1 − Φ(1.96 + 1/√π)² = 1.156%.

**(f) Sparse column.** A column exactly zero except one contiguous run of 18 days, T = 365. Exact dynamic programme for a replicate that never touches the run (column zero variance):

| L | P(one replicate all zero) | P(≥ 1 of 2000) |
|---|---|---|
| 1 | 9.6e-9 | 1.9e-5 |
| 5 | 0.0109 | ≈1 |
| 20 | 0.134 | ≈1 |
| 58 | 0.201 | ≈1 |

## 3. Findings

| ID | Severity | Location | Scenario and evidence | Proposed disposition |
|---|---|---|---|---|
| FB1-1 | BLOCKER | §2.3 "the largest is the conservative choice" | False: a longer L shrinks bootstrap variance by O(L/T) (§2(a)), lowering both D and S0. One long-memory column among iid columns forces L = 58 at T = 365, biasing every column's variance down by ~26.5%; a K = 1-type nominee then passes ~4.6% at 1.96 instead of 2.5%. Anti-conservative and data-dependent. | Withdraw the claim; make realised L/T a covariate of the cell classifier and a calibrated support boundary; consider per-column L or a smaller cap. Design choice, not mine. |
| FB1-2 | BLOCKER | §2.4 D only for `J_f*`; §2.6 rule 6 | Decided P18-3 (`PROPOSAL.md:283-284`) needs "for each [trial]: … finite positive D … finite pre-Φ z", and P18-4 nominates only "On `A_f`". Defining D only through the nominee makes availability depend on nomination, which depends on availability: circular. | Compute `D_j = (T−1)·var_b(S*_{b,j})` and `z_j` for every column (no extra resampling); check all in rule 6. |
| FB1-3 | BLOCKER | §3 D-16/D-17 | Uncited controlling clause: Constitution §9 line 106 "If no frozen effective-count method exists, raw count is used"; lines 67 and 104 "lifetime trial counts persist" / "Lifetime family accounting persists". The predecessor `d16-d17-proposal/PROPOSAL_PACKET.md:69` relied on line 106. No count in the score therefore needs a Constitution §4 amendment of §9, not only a protocol change. Whether "persist" allows "recorded only" is the owner's reading. | Cite 106, 104, 67; add §9 to O18-7's amendment scope; present to the owner with B-1/B-2. |
| FB1-4 | NON-BLOCKING | §2.6 rule 4 `L > T/4` | Never fires for T ≥ 148 (§2(c)); for long memory the 3√T cap truncates silently, with no reason code. | Delete or replace; record cap-binding as a support boundary. |
| FB1-5 | NON-BLOCKING | §2.3 block length from `psi = u − (S/2)(u²−1)` | The bootstrap works at the recentred null, where the influence is `u`. `psi` at sample S has infinite variance under infinite fourth moment, making L noisy; the max over K amplifies it, feeding FB1-1. | Use the null influence `u`, or justify `psi`. |
| FB1-6 | NON-BLOCKING | §2.6 rule 5 | In §2(f)'s sparse case the family is unavailable almost surely for L ≥ 5, counting against `U_proc`. Exact-zero E-DIFF days could arise when a candidate's long state copies the vol-target benchmark (line 107 sizing); whether the engine produces them is UNVERIFIED. | Add a D-19 cell or a declaration-time screen. |
| FB1-7 | NON-BLOCKING | §2.6 "All six are U_proc" | Rule 2 (T < T_min) is known before declaration: it belongs to declaration refusal / eligibility (O18-4, P18-0), not `U_proc`, else it fails 100% in its cell. An infrastructure-caused missing day is `U_ops` under P18-7's precedence (`PROPOSAL.md:345-349`). | Reclassify both. |
| FB1-8 | NON-BLOCKING | §2.3 seeds; §6 "reuses existing code" | `ReplicateStream` rejects any purpose but `"paired_sharpe_ci"` (`statistics.py` ~466), needs a single `trial_seed_hex`; the family seed is undefined (protocol line 266 defines per-trial seeds only). The convention hash ties it to `IMPLEMENTATION_CONVENTIONS.md`; I-10 requires regenerated reference vectors. | Define a declaration-fixed family seed; state the convention and code changes. |
| FB1-9 | NON-BLOCKING | §2.2, §2.4 arithmetic | P18-4/P18-6 require exact implementation–reference agreement; summation and variance algorithms over 2000 × K floats are unspecified. "Mean exactly zero" is false in binary64. | Specify `fsum` and the variance algorithm; reword "exactly". |
| FB1-10 | NON-BLOCKING | §4 B-3 | Right answer, weaker reason: within D-18 because O18-2 (`PROPOSAL.md:410-411`) leaves "equation, count and dispersion" to the broadened method; the line-92-vs-91 argument is not the strongest basis. Disclose: D is now the null variance rather than at observed S, and since T−1 cancels exactly, z = (S − S0)/sd_b. | Restate; disclose both to the owner. |
| FB1-11 | QUESTION | §2.4, P18-6 | The z null distribution differs by cell (§2(e)), so one global `z_crit` is set by the K = 1 / duplicate cell, costing power in large families. Would D = (T−1)·var_b(M*) be within D-18? | Owner/statistician question. |
| FB1-12 | NON-BLOCKING | §3 cross-cycle default | "Report only" is an AI default on open item O18-3, an error-budget question; it belongs in the §4 table. Cycles are not exactly independent (shared regimes, possible re-declaration). | Add as a B-row. |
| FB1-13 | NON-BLOCKING | §1, §3 citations | (i) "Constitution §5, line 12": line 12 is §0 Definitions; the §5 lifetime clause is line 67. (ii) "protocol line 207" for the 168-hour horizon: 207 is the embargo rule; horizons at line 109. (iii) "DEC-02 lines 88–91, 113–115" lies outside DEC-02's heading (36–49) — **inherited** from the decided `PROPOSAL.md:401`, not new. | Correct (i), (ii); (iii) owner's call. |
| FB1-14 | NON-BLOCKING | §4 B-4 "might make calibration trivial" | Overstated: a bootstrap p-value has the same L/T distortion. | Reword. |
| FB1-15 | NON-BLOCKING | §2.3 max over columns | Not monotone in K: declaring one extra long-autocorrelation column can raise L, shrinking the nominee's D and S0 and raising z — a lever at declaration time; bears on FR4-13's UNVERIFIED monotonicity. | Disclose; add a calibration cell, or per-column L. |
| FB1-16 | NON-BLOCKING | §5 | Missing calibration items: realised L/T, heterogeneous dependence across columns, sparse columns, K non-monotonicity, D for every trial. | Add to the D-19 grid. |
| FB1-17 | NON-BLOCKING | §6 cost | One replication ≈ 2000 × 80 × 365 ≈ 5.8e7 day-ops per family; at ~10⁴ replications per cell ≈ 5.8e11 per cell. "Trivial" holds only at run time. | Carry into the D-19 compute gate. |

Unrepaired: all. FB1-3, FB1-10, FB1-11, FB1-12 are owner/statistician decisions.

## 4. Protocol items

Applied: 1 (topic search of the Constitution found §9 line 106), 2, 4, 5 (the "duplicates add nothing" claim and the largest-L argument checked against the rest of the design), 6, 8, 9, 11, 13, 14. Item 12: each attribution cites a line (FR4-13 at `FABLE_REVIEW_10BB125.md:87`; AS-1..AS-3 at `ASTRA_REVIEW_597DDC8.md:302-304`). Item 3 N/A (no hashes recorded; LF in index and worktree, `eol=lf` attribute). Item 7 N/A (no verifier for this design). §16 (item 13) governs the later build; correctly stated; not unmet now.

## 5. Remaining decisions; not authorised

Owner, after both reviews: B-1/B-2 including the §9 amendment (FB1-3); B-3 (FB1-10); FB1-11; the cross-cycle budget (FB1-12). Not authorised: accepting or activating the method; frozen edits; building code (needs the owner's separate go-ahead plus §16 different-model and human PR review); calibration runs; confirmation or lockbox access; promotion; trading.

## 6. Plain-language summary for the owner

1. The new idea — re-shuffling your own strategies' returns to measure how lucky the best one could look — is sound in principle.
2. It handles copied strategies and single-strategy families that the old formula refused to score.
3. But one rule claimed to be "safe" (using the longest block length) actually makes passing by luck easier, up to about double.
4. That must be fixed or tested before calibration.
5. The formula must compute its spread number for every strategy, not just the winner, to match the D-18 rule you decided.
6. Dropping the "count every attempt ever" number conflicts with a Constitution sentence (§9), so it needs a formal amendment you would author.
7. Without that count, the chance of a lucky pass grows over several cycles (about 14% after three); you should decide that knowingly.
8. Nothing is accepted or activated; promotion stays blocked.
