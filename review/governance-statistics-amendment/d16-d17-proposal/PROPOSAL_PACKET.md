# D-16 / D-17 proposal packet — record (NON-BINDING, PROPOSAL ONLY)

Date: 2026-10-02. Requested by the owner ("explain D-16/D-17 again and let an
agent do it"), in a Claude Code session with Claude Opus 5.5
(`claude-opus-5-5`), which spawned the agent and wrote this header.

- Agent: the repository's `senior-statistical-governance` agent, run
  read-only in the background. It reports its model as Claude Fable 5.1
  (`claude-fable-5-1`), from its session context; the orchestrator did not
  independently verify that metadata.
- Commit the agent read: `6fa49332d20aad88bd27429ccff7ed350732dd0a` (branch
  `task28-telegram-alerts`; no file under `review/governance-statistics-amendment/`,
  `docs/`, `protocols/` or `src/aqt/core/attempts.py` differs there from `main`).
- Usage reported by the harness: 138,658 tokens, 40 tool uses, about 9.3 min.
- The agent wrote, staged and committed nothing. Its final report follows
  verbatim (the harness's indentation removed).

**This record closes no D-row and accepts nothing.** Both rows are authority
"STAT then §4": a qualified human statistician must answer A/R/X/D, then the
owner may amend under Constitution §4. No finding below (P-1..P-12) has been
repaired; every repair is a proposal for the owner.

---

# Proposal packet for D-16 and D-17 (effective trial count, and which count enters A(N))

**Status: NON-BINDING. PROPOSAL ONLY.** This packet accepts nothing, closes no D-row and amends nothing. Both rows are authority "STAT then §4" (`HUMAN_DECISION_MATRIX.md:63–64`). A qualified human statistician must answer A/R/X/D, and after that the owner may amend under Constitution §4 (`docs/RESEARCH_CONSTITUTION.md:47–50`). An AI cannot do either.

## 1. Identity and what was read

- **Model:** Claude Fable 5.1, model ID `claude-fable-5-1`, taken from the session's system context. Read-only. No files were written, staged or committed.
- **Commit read:** `6fa49332d20aad88bd27429ccff7ed350732dd0a`, branch `task28-telegram-alerts`. The working tree was clean.
- **Calculations:** Python 3.14.7 standard library only, scripts in `%TEMP%`. scipy, numpy and mpmath are not installed, so I wrote a deterministic Simpson quadrature. It matches the closed forms E[M₂] = 1/√π and E[M₃] = 3/(2√π) to about 1e-14. Nothing was simulated.

## 2. Key result: the reason for raw N is not "upper bound"

Repository formula (`METHOD_CANDIDATE.md:89–99`):

- S0 = √V · A(N)
- V = the sample variance of the K trial Sharpe ratios, taken **across trials** (cross-sectional)

Because V is measured across trials, the dependence between trials already lowers V, and so already lowers S0. The following was derived and computed by me.

**Lemma 1 (exact).** Suppose the trial Sharpes are Gaussian, have equal variance σ², have true mean zero, and share one common correlation ρ. This holds for any admissible ρ in [−1/(N−1), 1).

- Write X_j = √(1−ρ)·σ·(e_j − ē) + b·W, with b² = σ²(1+(N−1)ρ)/N.
- Then E[max_j X_j] = √(1−ρ)·σ·E[M_N], where M_N is the maximum of N independent standard normals.
- And E[√V] = √(1−ρ)·σ·c₄(N).
- So E[S0] / E[max] = c₄(N)·A(N) / E[M_N]. This ratio **does not depend on ρ or its sign**.

Computed values of that ratio:

| N | 2 | 3 | 5 | 10 | 12 | 13 | 20 | 27 | 81 | 162 |
|---|---|---|---|---|---|---|---|---|---|---|
| ratio | 0.735 | 0.893 | 0.964 | 0.995 | 0.9989 | 1.0002 | 1.0045 | 1.006 | 1.0068 | 1.0061 |

Two consequences:

- **Raw N is already the mean-correct count for this formula.** It is not an upper bound on some smaller "true" effective count.
- **Any effective count N_eff below N counts the dependence twice.** Example: N = 100, ρ = 0.3. The count that matches E[max] when combined with cross-sectional V is 95.4, for every ρ. Using the curriculum's "true effective N" of 32 gives S0 = 1.75 against a true E[max] of 2.10, which is 17% too low. At ρ = 0.9 it gives 0.25 against 0.79, which is 68% too low.

**Discrimination check.** For a family of 3 clusters × 27 identical trials, the frozen formula gives E[S0] = 1.788σ against E[max] = 0.846σ, which is 2.11× too high (conservative). Two plausible wrong treatments give different numbers: σ·A(81) = 2.456, and √(E V)·A(81) = 2.017. So the match is not an accident of method.

## 3. D-16: which effective-count construct, and what triggers the fallback

### Recommended construct (R-16)

- Use `raw_trial_count` **unconditionally**, together with the cross-sectional V from METHOD_CANDIDATE §3.1.
- Proposed trigger rule T-16: *raw count applies because no frozen effective-count method exists* (Constitution §9 line 106). A statistician can check this in two ways:
  - **(i) Line 232 names a method but defines no function.** On the same matrix (N = 3, ρ = ½, eigenvalues {2, ½, ½}), three standard eigenvalue definitions give three different answers: participation ratio = 2, Nyholt N + 1 − ΣR²/N = 5/2, entropy rank = 2.381 (first two exact by Fraction).
  - **(ii) No function of the correlation spectrum or of R_ij² can be valid for a maximum.** Flipping the sign of a trial changes R to DRD with D = diag(±1). The eigenvalues stay the same. The expected maximum does not, for example for N = 2 when σ is known:
    - E[max] = σ·√((1−ρ)/π), which is exact because max = (X₁+X₂)/2 + |X₁−X₂|/2.
    - ρ = +0.9 gives 0.178σ, and ρ = −0.9 gives 0.778σ.
    - Both matrices have spectrum {1/10, 19/10} and N²/ΣR² = 200/181.
- I propose a §4 amendment of lines 232–233 rather than relying on interpretation alone, so that the frozen primary method stops naming a construct that has been refuted.

### Validity claim, stated exactly

- **VC-1 (exact, holds under any dependence; relative conservatism).** A(N) is strictly increasing for N ≥ 2. Both inverse-normal arguments increase with N, and the weights 1−γ and γ are positive; integers 2 to 2000 were checked. So for fixed S, V > 0, T and D, DSR is strictly decreasing in N. Every eigenvalue count satisfies 1 ≤ N_eff ≤ N, because ΣR_ij² ≥ N. So raw N gives a DSR no higher than any effective-count option.
- **VC-2 (holds under the Lemma 1 assumptions).** Raw N is unbiased in the mean to within +0.7% for **N ≥ 13**. It is **anti-conservative for N ≤ 12**: 26.5% short at N = 2 and 4% short at N = 5. This holds for both positive and negative common correlation.
- **VC-3 (positive versus negative dependence).**
  - *Reading V as the true per-trial null variance σ²:* if every ρ_ij ≥ 0, then E[max] ≤ σE[M_N] ≤ σA(N) for 3 ≤ N ≤ 500. The first inequality is Slepian/Sudakov–Fernique and is UNVERIFIED_EXTERNAL_ASSUMPTION; the second I computed.
  - *Negative correlation breaks this:* at N = 2, ρ = −1, E[max] = 0.798σ, which exceeds both A(2)σ = 0.520σ and the independent-trial value 0.564σ.
  - *Under the frozen cross-sectional V*, negative equicorrelation does not change the bias (Lemma 1). Pairs of exactly opposite trials give 0.735 (one pair), 0.954 (two pairs) and ≥ 1.006 (five or more pairs).
  - **I found no guarantee for the frozen formula that holds under every dependence structure.**

### Assumptions

- Each trial's Sharpe is approximately Gaussian (asymptotic).
- Under the null, true Sharpes are zero and per-trial variances are roughly equal.
- K usable columns are close to N.
- In Bailey and López de Prado, V means the variance across trials. That is UNVERIFIED_EXTERNAL_ASSUMPTION; the repository itself defines V that way at `METHOD_CANDIDATE.md:99`.
- Matching the mean is **not** calibration of the 0.95 gate. That is D-19, which the owner deferred.

### Falsifier

- A dependence structure the frozen grid can produce in which E[max] > E[√V]·A(N) by more than an agreed tolerance at N ≥ 13. Small N is already known to fail.
- A shown non-spectral definition for line 232.
- A showing that V must be the per-trial null variance, in which case negative dependence makes raw N anti-conservative.

### Failure mode

- **Too low** (small N, or adversarial dependence): S0 is too small, noise can pass. This is the direction that loses money.
- **Too high** (clustered trials): a false NO_EDGE_FOUND. That only costs opportunity, and §1 line 27 accepts it.

### Optional small-N guard (R-16b, changes the equation, needs §4)

Use the multiplier max(A(N), E[M_N]/c₄(N)). Values of E[M_N]/c₄(N):

| N | 2 | 3 | 5 | 10 | 12 |
|---|---|---|---|---|---|
| E[M_N]/c₄(N) | 1/√2 = 0.7071 | 0.9549 | 1.2372 | 1.5820 | 1.6666 |

From N = 13 on, A(N) is larger anyway, so the guard only acts at N ≤ 12.

### Options (a) and (c)

Both are unusable. This is consistent with Astra B1 (`ASTRA_REVIEW.md:10–14`) and extends it to **every** eigenvalue definition.

## 4. D-17: which count enters A(N)

### Recommendation (R-17)

**N_lifetime**, defined as:

- the number of attempts on the confirmation partition that have an `EVALUATION_STARTED` record (`attempts.py:464–483`);
- counted per family;
- across all cycles, including failures, evaluated aborts, reruns, and attempts from invalidated cycles.

V comes only from the current cycle's K ≥ 2 usable columns.

### Reasoning

- **Order:** N_lifetime ≥ N_cycle ≥ K; any other ordering is an invalid count (`DSR_METHOD_PREREGISTRATION_DRAFT.md:85`). Since A is increasing, N_lifetime is the most conservative choice.
- **K is ruled out by frozen text.** A trial is counted when its evaluation begins, and failures count (§0 line 13; §9 lines 102–104). `raw_trial_count` (line 233) counts trials, and K counts only usable vectors. Using K would let crashes lower the hurdle, which is the undercount channel PR #6 was built to close.
- **Frozen text that bears on the choice:**
  - §5 line 67: matrices are not pooled, but "lifetime trial counts persist."
  - §5 line 65: invalidation does not void lifetime counts.
  - §9 line 104.
  - protocol line 190: `lifetime_accounting: true`.
  - protocol line 251: "family DSR".
  - None of these says explicitly that the lifetime count enters A(N). I therefore agree with the matrix that this needs STAT then §4.
- **Consequences of each option:**
  - **K:** lowest hurdle, and failures quietly reduce it.
  - **N_cycle:** the count resets every cycle, so re-searching a family in C2 is not deflated.
  - **N_lifetime:** the hurdle rises with every cycle, so a family is eventually closed in practice.
- **C1 effect:** in C1, N_lifetime = N_cycle, provided no earlier confirmation attempt exists (line 20 forbids trials before bindings; I did not inspect the ledger). Choosing now costs nothing numerically in C1 and fixes the conservative direction before results exist (§1 line 31, §4 line 48).

## 5. How much is at stake: the hurdle versus N

Illustrative assumptions:

- T = 1247 days, the length of the confirmation partition (lines 66; 365 + 365 + 366 + 151). The real out-of-sample T depends on the fold design.
- Returns independent, identically distributed and normal, so g = 0, k = 3, D = 1 + S²/2.
- √V = √(v/(T−1)).

The table shows the annualized Sharpe the difference series needs for DSR ≥ 0.95:

| N | 1 | 3 | 10 | 27 (one gridded hypothesis) | 81 (family budget) | 162 (two families) | 243 (three cycles) |
|---|---|---|---|---|---|---|---|
| v = 1 | 0.89 | 1.35 | 1.74 | 1.99 | 2.22 | 2.35 | 2.43 |
| v = 2 | 0.89 | 1.54 | 2.10 | 2.45 | 2.77 | 2.96 | 3.06 |

With T = 730 and v = 1, N = 81 requires 2.91.

What this means:

- **D-16 is where the money is.** If an effective count were to report 3 for an 81-trial family, the hurdle would drop from 2.22 to 1.35.
- **D-17 matters less.** Going from N = 81 to N = 243 adds about 0.2.
- **Expect NO_EDGE_FOUND.** At these levels it is the likely outcome.

## 6. Statistician checklist

Answer each item A/R/X/D. My estimate of total effort is about 3–6 hours, and that estimate is uncertain.

1. In the repository formula, V is the variance across trials (`METHOD_CANDIDATE.md:99`), and that matches the Bailey–López de Prado V.
2. Lemma 1: the bias ratio does not depend on ρ for any admissible equicorrelation.
3. The bias table, using the quadrature check E[M₂] = 1/√π.
4. Line 232 does not determine a function (the values 2, 5/2, 2.381).
5. No eigenvalue or squared-correlation count is valid for maxima (the sign-flip argument).
6. VC-1 monotonicity, and N_eff ≤ N for each candidate definition.
7. Raw count applies through §9 line 106, and §4 is used to retire line 232.
8. Whether to adopt R-16b, or to accept and record the anti-conservatism at N ≤ 12.
9. N_lifetime, rather than N_cycle or K, enters A(N).
10. N counts attempts, not distinct trial points (reruns count).
11. The revisions to the reason codes in finding P-7.
12. The family scope from line 251.

## 7. Findings

- **P-1 NON-BLOCKING.** `METHOD_CANDIDATE.md:140–144` (F-2) says the eigenvalue count and N²/ΣR² are "different functions". The eigenvalue participation ratio (Σλ)²/Σλ² equals N²/ΣR_ij² exactly, because tr R² = ΣR_ij². So the claim holds only for some readings of line 232. This wording originates in that committed file; correcting it is the owner's decision.
- **P-2 BLOCKER** for accepting any effective count. Combined with cross-sectional V it counts the dependence twice (section 2).
- **P-3 QUESTION.** Raw N is anti-conservative for N ≤ 12, so calling it "conservative" without qualification is wrong. It needs R-16b or a recorded acceptance.
- **P-4 NON-BLOCKING.** If V is read as the per-trial null variance, negative dependence defeats raw N. A dependence-free bound exists: E[max] ≤ σ√(2 ln N), derived from the moment-generating function and using only the marginals. Opposite-signed columns are plausible on the frozen vol-target grid {0.40, 0.60, 0.80} against a 0.60 benchmark (lines 127–129), *assuming* exposure is proportional to the vol target. That assumption is unverified against the backtester spec.
- **P-5 NON-BLOCKING.** `.agents/skills/sharpe-selection-statistics/SKILL.md:182–187` calls the inverse-image "true effective N" the right definition for this purpose. Under the repository's V it is anti-conservative (section 2). This is a committed curriculum file, so the correction is the owner's decision.
- **P-6 NON-BLOCKING.** The frozen trial definition excludes K (section 4).
- **P-7 BLOCKER.** The carried-forward reason codes (`DSR_METHOD_PREREGISTRATION_DRAFT.md:89–91`, kept by `METHOD_CANDIDATE.md:161–172`) block results in exactly the cases these rows are about:
  - INCOMPLETE_HISTORY (read literally, K < N_cycle) and UNSUPPORTED_LIFETIME_HISTORY make every case where the D-17 options differ unavailable, so D-17 currently changes no number.
  - UNSUPPORTED_DESIGN ("known dependent") plausibly covers every gridded family.
  - These must be decided together with D-16 and D-17.
- **P-8 QUESTION.** Four scope questions remain:
  - selection across families (two lockbox evaluations per family, line 74);
  - whether lockbox attempts count (`attempts.py:414–421`);
  - attempts versus distinct points;
  - OWNER_REVIEW F-6 (`OWNER_REVIEW.md:64`), which says two code paths each claim to be the §9 count.
- **P-9 NON-BLOCKING.** The dependency runs both ways. N_lifetime with no pooling (§5 line 67) rules out options (a) and (c). The matrix line 78–79 states only "D-17 … require D-16".
- **P-10 NON-BLOCKING, correcting the task's premise.** Closing D-16 and D-17 does not unblock C1. D-18 is still blocking, and the owner's deferral of D-19 keeps governed trials and promotion blocked (`OWNER_DSR_DEFER_DECISION.md:14–18`; matrix line 79).
- **P-11 NON-BLOCKING.** The D-17 row in the matrix omits §5 line 65, §1 line 31 and protocol line 251.
- **P-12 NON-BLOCKING.** Nothing in this packet calibrates the 0.95 threshold.

None of these was repaired, because I am read-only. Every repair is a proposal for the owner.

**Verification protocol items applied:** 1, 2, 4, 5, 6, 8, 9, 11, 12, 13 and 14. Item 3 is N/A because no digests are claimed. Item 7 is N/A because no verifier was run (scipy, numpy and mpmath are absent; the standard-library substitute is validated against the closed forms above). Item 10 is N/A because nothing was written.

## 8. Still open, and where I am unsure

- **D-18:** under a selection rule other than taking the maximum, the deflation is mis-targeted.
- **D-19:** deferred by the owner; the 0.95 threshold has no calibrated meaning.
- **Whether the frozen grid's dependence is within Lemma 1's model.** I did not establish this.
- **Heterogeneous trial variances and serial dependence** are not analysed here.
- **External theorems and definitions** I rely on (Slepian/Sudakov–Fernique, the Nyholt and entropy-rank formulas, the Bailey–López de Prado definition of V) are UNVERIFIED_EXTERNAL_ASSUMPTION. Their formulas are stated explicitly above so they can be checked as written.

## Verdict

**KEEP_BLOCKED.** R-16 and R-17 are offered as candidates for a statistician to decide on. Decisions still needed:

- STAT: A/R/X/D on D-16, D-17, R-16b and the reason codes in P-7.
- Owner: the §4 amendment, the D-19 deferral, and the curriculum and METHOD_CANDIDATE corrections in P-1 and P-5.

**Still unauthorized:** any edit to frozen artifacts; binding N into a gate (that would need §16 review of `attempts.py`); a calibration engine; simulation; Task 13; governed trials; confirmation or lockbox access; promotion; deployment; trading.

Files referenced:
- `D:\PMP-programs-for-sharawi\autonomous-quant-trader\review\governance-statistics-amendment\v1.1-method-candidate\HUMAN_DECISION_MATRIX.md`
- `...\v1.1-method-candidate\METHOD_CANDIDATE.md`
- `...\governance-statistics-amendment\DSR_METHOD_PREREGISTRATION_DRAFT.md`
- `...\governance-statistics-amendment\OWNER_DSR_DEFER_DECISION.md`
- `D:\PMP-programs-for-sharawi\autonomous-quant-trader\.agents\skills\sharpe-selection-statistics\SKILL.md`
- `D:\PMP-programs-for-sharawi\autonomous-quant-trader\src\aqt\core\attempts.py`
- `D:\PMP-programs-for-sharawi\autonomous-quant-trader\protocols\protocol_v1.yaml`
- `D:\PMP-programs-for-sharawi\autonomous-quant-trader\docs\RESEARCH_CONSTITUTION.md`
