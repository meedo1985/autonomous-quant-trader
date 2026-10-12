# Fable focused check of the broadened method design rev2 at `020c8d0` — READY

Date: 2026-10-03. Focused check (rev 1 → 2 changes) by the Anthropic family
for R19-2; run in parallel with, and without sight of, `SOL_REVIEW_020C8D0.md`.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`); prompt
  `REVIEW_PROMPT_R2.md` (committed `74f300c`), prefix FB2.
- Model metadata: self-reported by the reviewer as `claude-fable-5-1`; the
  launch requested the `fable` model. Not independently verified through
  provider metadata.
- Findings: FB2-1..FB2-10, all NON-BLOCKING. Nothing is decided by this
  record; no finding is repaired here.

Below is the reviewer's final message, verbatim.

---

# Fable review FB2: broadened DSR method design, revision 2 (focused check of rev 1 → 2)

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family — self-observed model ID, not verified against provider metadata. AI reviewer, no authority; closes no D-row, accepts no method.
**Commit reviewed:** `020c8d0` (`DESIGN.md` identical at HEAD `74f300c`, which adds only `REVIEW_PROMPT_R2.md`). Read-only; `SOL_REVIEW_020C8D0.md` not read; no edits, no network; in-memory calculations only (`.venv/Scripts/python.exe -B -`).
**Verdict: READY** for the owner to decide B-1..B-6; none of the findings below blocks those decisions. FB2-1 should be added to the B-3 row before the owner reads it. Skill verdict: `AMENDMENT_REQUIRED` (B-1 needs a Constitution §9 amendment; the method changes protocol lines 223–233). Nothing becomes binding.

## 1. Revision-1 findings (Q1)

| ID | Status | Reason |
|---|---|---|
| SB1-1 | RESOLVED | `D_j` from uncentred resamples (§2.3); label now correct. Stated reason: see FB2-1. |
| SB1-2 | PARTLY | Supported domain stated (§2.6); enforced only by the cap check (FB2-6); fourth-moment wording contradicts it (FB2-3). |
| SB1-3 | RESOLVED / DEFERRED to D-19 | "Conservative" withdrawn, `T/4` deleted, selector labelled a calibrated heuristic; whether the median candidate holds is new (FB2-4). |
| SB1-4 | PARTLY | Family seed and purpose extension defined, declaration checks inherited; seed form departs from protocol line 266 and canonical encoding unspecified (FB2-7); `T_min` deferred to D-19. |
| SB1-5 | RESOLVED | §3 uses "per eligible cycle, conditional…". |
| SB1-6 | RESOLVED | B-3 restated via O18-2. |
| SB1-7 | RESOLVED | §4 reruns the exact inner algorithm per outer replication. |
| SB1-8 | RESOLVED / DEFERRED to owner (B-5) | Figures checked exactly: union bound 1/10, 3/20, 1/4, 1/2; independence 0.0975, 0.142625, 0.22622, 0.40126. |
| SB1-9 | PARTLY / DEFERRED to D-19 | Missing items listed; the infinite-fourth-moment problem recurs in §2.6 (FB2-3). |
| FB1-1 | RESOLVED / DEFERRED to D-19 | Claim withdrawn; `L/T` a classifier covariate; binding cap a reason code. |
| FB1-2 | RESOLVED | `D_j`, `z_j` for every column; rule 6 checks all, as P18-3 (`PROPOSAL.md:281-284`) requires. |
| FB1-3 | RESOLVED in text / DEFERRED to owner (B-1, B-2, §7) | Citations verified: Constitution line 106 is §9 "raw count is used", 104 is §9, 67 is §5. |
| FB1-4 | RESOLVED | `T/4` deleted; binding cap detectable since `block_length` returns `clipping="UPPER"` when `raw > maximum` (`statistics.py:378`, 433). |
| FB1-5 | PARTLY | Adopted, but its premise was lost when SB1-1 was adopted (FB2-2). |
| FB1-6 | PARTLY | D-19 must include sparse columns, but qualifying versus challenge is not stated (FB2-9). |
| FB1-7 | RESOLVED | `T_min` moved to eligibility; `U_ops` precedence matches P18-7 (`PROPOSAL.md:345-349`); extends P18-0 (FB2-8). |
| FB1-8 | PARTLY | As SB1-4 (FB2-7). |
| FB1-9 | RESOLVED | `fsum`, two-pass variance, index order, "zero up to rounding". |
| FB1-10 | RESOLVED | B-3 rests on O18-2; `T−1` cancellation disclosed in §2.3. |
| FB1-11 | DEFERRED to owner (B-6) | — |
| FB1-12 | RESOLVED / DEFERRED to owner (B-5) | — |
| FB1-13 | RESOLVED (i, ii) / DEFERRED to owner (iii, inherited) | Verified: line 12 is §0; protocol line 109 is `horizons_hours`. |
| FB1-14 | RESOLVED | B-4 reworded. |
| FB1-15 | PARTLY | Disclosed for "largest"; not carried to the median rule or the availability lever (FB2-4, FB2-5). |
| FB1-16 | RESOLVED / DEFERRED to D-19 | Listed in §4. |
| FB1-17 | RESOLVED / DEFERRED to D-19 | 2000·80·365 = 58,400,000 day-ops per family; ×10⁴ = 5.84e11 per cell. |

## 2. Calculations (independent, in memory)

**(a) Identity behind "one index sequence, two uses".** x = (3, −1, 4, 1, −5, 2), mean m = 2/3, one shared index sequence, in `Fraction`: on the same indices `var(X*) == var(Y*)` True and `mean(X*) − mean(Y*) == m` True, so `S*_{b,j} = S°_{b,j} + m_j / sd(Y*_{b,j})` exactly. Discriminating: with a different index sequence for `X*` the variances differ (False). Sharing the index sequence is coherent; rule 5's "in either matrix" is mathematically redundant.

**(b) Median versus largest L with one dependent column.** First-order Gaussian approximation, global null; deterministic quadrature, not a simulation. K = 3 independent columns; A is AR(1) with φ = 0.5 (true variance of `√T·Ŝ` = 3); B, C iid; T = 365. Population PW length for A `((2φ/(1−φ²))²·T)^{1/3}` = 8.66 (cap 58, not binding). Share of A's variance the stationary bootstrap captures: 1/3 at L = 1, 0.556 at L = 2, 0.862 at L = 8.66. False-pass at `z_crit` = 1.96 nominating top `S`: **median rule** (L ≈ 1) **5.73%**; median at L = 2: 2.64%; **largest** (L = 8.66) **1.04%**; all-iid analogue 0.75%.

**(c) Any-column unavailability amplified by K.** For a family no-result rate ≤ 1%, the per-column failure rate must be ≤ `1−0.99^{1/K}`: 1.26e-4 at K = 80; 6.27e-5 if the 1% is split across two families.

## 3. Findings

| ID | Severity | Location | Scenario and evidence | Proposed disposition |
|---|---|---|---|---|
| FB2-1 | NON-BLOCKING | §2.3 bullet 2; §5 B-3 | Right answer, partly wrong reason. Uncentred `D_j` is faithful to the decided `D`, evaluated at observed `S` (`METHOD_CANDIDATE.md:91`), and fixes the label. But the cited example (S = 0.5, z inflated 1.58×) has a nonzero true Sharpe: it concerns power, not `P_0(E_f)`. Under the global null both scales share a limit; they differ at order `T^{-1/2}` by a term ∝ skewness × `Ŝ`, correlated with the pass event; direction of the size effect not derived (`UNVERIFIED`). | In B-3 show the null-scale `D` (rev 1) as the rejected alternative; state the choice is for fidelity to the decided formula and correct labelling; size is settled by calibration cells with positive and negative skew. |
| FB2-2 | NON-BLOCKING | §2.2 "null influence `u_j`"; `ADJUDICATION_6481F28.md:17`, :26-29 | Two accepted fixes are inconsistent. FB1-5 (`FABLE_REVIEW_6481F28.md:79`) rested on "the bootstrap works at the recentred null, where the influence is `u`" — true only while `D` came from recentred resamples. After SB1-1, `D_j` is the observed-law variance, whose influence is `psi`. The adjudication accepted both without noticing. Practical size small: extra variance weight `S²(k−1)/4` ≈ 0.02 at S = 0.1 (daily), k = 9. Inherited from the committed adjudication (protocol item 11), not new in DESIGN. | State that `L` targets the null mean and `D_j` inherits it; add a D-19 check of `D_j` accuracy under the `u`-based `L`. |
| FB2-3 | NON-BLOCKING | §2.6; §2.7 "fat tails" | The SB1-9 contradiction recurs: the domain is "finite variance" yet `D_j` "needs a finite fourth moment", so infinite-fourth-moment laws are qualifying while the method admits instability there. Under the global null `Ŝ = O_p(T^{-1/2})`, so skew/kurtosis terms in `D_j` vanish for finite-variance laws (heuristic; `UNVERIFIED_EXTERNAL_ASSUMPTION` for the bootstrap); the fourth-moment need concerns power. | Reword: finite variance for `P_0`, finite fourth moment for power; or classify infinite-fourth-moment laws as challenge cells. |
| FB2-4 | NON-BLOCKING | §2.2 {largest, median} | The median is anti-conservative for exactly the column most likely to be nominated: a dependent column has larger `Var(Ŝ)`, so is likelier to be nominated, and under the median its `D` captures only part of its dependence — 5.73% vs 1.04% for largest (§2(b)). The development selection criterion and the median for even K are unstated. `bootstrap_indices` accepts a float block length, so no rounding is needed. The FB1-15 lever also applies to the median. | Keep the median only if D-19 includes a single-dependent-column cell; preregister the statistic that chooses largest vs median; define the even-K median. |
| FB2-5 | NON-BLOCKING | §2.5 rules 3–4 "for some column" | One column can make the family unavailable: under the median, one capped or failed column blocks the family though the median would ignore it, contradicting the median's rationale. No-result grows with K (§2(c)): ~1.26e-4 per column at K = 80. A PW failure via `NONPOSITIVE_LONG_RUN_VARIANCE` is possible for negatively autocorrelated `u`. | D-19 reports per-column cap and failure rates by K; consider matching the trigger to the chosen combination rule. |
| FB2-6 | NON-BLOCKING | §2.2 cap; §2.6; §4 | The supported domain is a law-level property checked only through the sample cap. Long memory below the cap, breaks and infinite variance are still scored without calibration guarantee. `BLOCK_LENGTH_CAPPED` is called "outside support" but counted as `U_proc`. O18-2 (`PROPOSAL.md:405-409`) requires a "support classifier" in the method specification before D-19, while §4 defers it to D-19. O18-4 (`PROPOSAL.md:425-426`) refuses designs at declaration, but these are data properties, not declared-design properties. | Relabel the cap as a sample-level `U_proc` refusal; specify the classifier or record that O18-2's ordering is relaxed (owner-visible); disclose the scored-without-guarantee residual. |
| FB2-7 | NON-BLOCKING | §2.4; §7 | The family seed omits `protocol_hash`: the frozen policy is `SHA256(protocol_hash,hypothesis_hash,trial_index)` (protocol line 266), not in §7. Constitution §27 line 194 ("must reproduce from recorded hashes/seeds or are void") uncited (topic search). Canonical serialization (encoding, delimiters, ordering key) unspecified, as are `ReplicateStream`'s `asset` and `cost_multiplier` for DSR. Seed fixed before data exists (P18-0, P18-1), so grinding gains nothing. | Add line 266 to §7, cite §27, specify a JSON canonical form; build-time details. |
| FB2-8 | NON-BLOCKING | §2.5 "cycle ineligible (P18-0)" | `T < T_min` adds a fifth condition to the owner-decided P18-0 (`PROPOSAL.md:190`); in neither §5 nor §7. | List it as a P18-0 extension in §7 or a B-row. |
| FB2-9 | NON-BLOCKING | §2.5 rule 5 | Rev 2 does not decide whether sparse-column families qualify; if qualifying, the method fails `U_proc` there almost surely (FB1 §2(f)); sparsity is a data property, not refusable at declaration. | D-19 or the owner chooses qualifying vs challenge. |
| FB2-10 | NON-BLOCKING | §2.3 "(§2.4 of rev. 1 kept)"; rule 5 | Wrong referent: recentring was rev 1 §2.2 "Null recentring"; rev 1 §2.4 was "The two quantities". Rule 5's "either matrix" is redundant (§2(a)) but harmless. | Correct to §2.2. |

Unrepaired: all ten. FB2-1, FB2-8 bear on owner decisions; FB2-4, FB2-5, FB2-6, FB2-9 are D-19 design or owner choices.

## 4. Protocol items applied

Applied: 1 (topic search found §27 line 194 and protocol line 266), 2 (FB2-10; every P18/O18 referent checked), 4 (§2(a)), 5 (FB1-5 premise against SB1-1 → FB2-2; FB1-15 against the median → FB2-4), 6 (FB2-1), 8, 9, 11 (FB2-2 inherited), 12, 13, 14. Item 3 N/A (DESIGN records no digests; LF in index and worktree, `eol=lf`). Item 7 N/A (no verifier).

## 5. Remaining decisions; not authorized

Owner decides B-1..B-6 including the §9 amendment, and whether FB2-8's addition to P18-0 and FB2-6's relaxation of the O18-2 ordering are acceptable. Not authorized: accepting or activating the method; frozen edits; building code (needs owner go-ahead and §16 different-model and human PR review); calibration runs; confirmation or lockbox access; promotion; trading.

## 6. Plain-language summary for the owner

1. Revision 2 fixed the three serious problems found last time; the design is ready for your B-1..B-6 decisions.
2. The new spread measure is the right one for your decided formula, but its stated reason mostly concerns real edges, not luck; ask that this be stated in B-3.
3. Of the two block-length rules still on offer, "median" can let a lucky strategy pass about twice as often as allowed when one strategy behaves differently from the rest.
4. A few loose ends remain for the calibration plan: seed details, sparse strategies, and how out-of-range data is detected.
5. Nothing is accepted or active; promotion stays blocked.
