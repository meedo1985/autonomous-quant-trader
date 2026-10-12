# Sol High review of the D-14/D-15 proposal rev2 at `c872066` — UNSOUND

Date: 2026-10-03. This is the OpenAI-family review for R19-2. It ran in parallel with the Fable review and without sight of it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a10274-8d4b-7e13-a055-2bfeccc46109`;
  tokens used 84,037; exit 0. (The reviewer's self-report names only "GPT-5"; the CLI header
  is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R2.md` (committed `c872066`) with `{{PREFIX}}` = `SN2`
  (substituted file SHA-256 `0ceb24f563dd5528a6f8c48111d45402e7c1cffd00a5b4fe64806ac5cc0d8c85`).
- The reviewer's final message follows, verbatim:

---

Model: **GPT-5, OpenAI GPT family**; no finer runtime model ID is exposed to me.  
Commit reviewed: **`c872066503185ca0acdd1d16399d1930b10260b3`**; the target has no uncommitted diff.  
Verdict: **UNSOUND** — both D-14 and D-15 should remain blocked.

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| SN2-1 | BLOCKER | `PROPOSAL.md` §1.1–1.2, especially lines 61–72 | Ratio shifting fixes benchmark-volatility misalignment only when the candidate is proportional to the benchmark. A volatility-family candidate using a different estimator can still beat its shifts without directional skill because the shift destroys that estimator’s current-date volatility alignment. | Exact check A: with `b=a=1/σ`, the old full-exposure shift gives Sharpe² `25/43`, while ratio shifting keeps Sharpe² `1`, so the revision-1 example is fixed. Exact check B: let `b=1/4`, `a=1/(2σ)`, `σ=[1,1,2,2]×2`, and standardized returns `z=[2,0]×4`. The candidate has Sharpe² `1`; its two-step ratio shift has `a'=[1/4,1/4,1/2,1/2]×2` and Sharpe² `25/43`. Algebraically, shifting `a/b` does not preserve candidate-specific sizing unless the candidate/benchmark estimator ratio is time-invariant. Constitution §12 classifies volatility management as de-risking, not alpha. | Remove the claim that the null breaks “only” timing. Either use current-date candidate sizing with a shifted pre-sizing signal, specify separate family constructions, or ask the owner explicitly whether alternative-estimator alignment is to count as timing skill. Keep D-14 blocked meanwhile. |
| SN2-2 | BLOCKER | §1.2 lines 43–81 | Clipping means the shifted effective ratios, mean target exposure, and turnover are not preserved; consequently “preserve the candidate’s exposure pattern relative to the benchmark” is not an accurate replacement for “match.” | Four daily blocks: `b=[1,1/2,1,1/2]`, `a=[1/2,1,1/2,1]`, hence `r=[1/2,2,1/2,2]`. A one-day shift requests `[2,1/4,2,1/4]`; clipping produces `[1,1/4,1,1/4]`. The effective ratios, mean exposure, and turnover all differ from the candidate’s. Bands, minimum hold, price-driven exposure drift, and the circular wrap add further differences. The “constant multiple” statement is valid only when multiplication does not clip. | Replace “match” with exact normative language naming the conditioned object—for example, the declared hourly **pre-clip target-ratio sequence**—and explicitly state that realized mean exposure and turnover are not matched. If matching remains required, define target versus realized quantities, units, tolerances, and rejection/unavailability behavior. |
| SN2-3 | BLOCKER | §1.2 and §1.6 | The construction and availability contract are not numerically or operationally complete. | `b_h>0` is insufficient: a tiny finite `b_h` can make `a_h/b_h` overflow; clipping can then turn infinity into a finite target, evading the final-statistic check. “Same initial state” does not identify held exposure, risk-increase clock, pending orders, or warm-up state. The wrap creates an artificial interior transition, and the backtester can transform identical target-ratio multisets into materially different realized paths. | Require finite `a`, `b`, `r`, and the pre-clip product; define safe arithmetic or a minimum admissible `b`; define complete initial/warm-up state and missing-bar behavior; define the wrap transition; and enumerate all unavailability reason codes. |
| SN2-4 | NON-BLOCKING | §1.3, §1.5 | The integer-shift and rank formulas are correct, but two surrounding claims need correction. | For `D=T−2m`, the formula yields 500 distinct integer shifts iff `D≥499`; at `D=498` there are 499 unique values, and at `D=499` exactly 500. Requiring 476 strictly lower null values corresponds, for 501 genuinely exchangeable continuous values, to `25/501≈4.99%`; ties correctly count against passing. But the deterministic, truncated set of shifts is not thereby exchangeable. Also N-1 did not bind `T≥840`; D-19’s `T_min` remains open. | Retain the formulas. Describe `25/501` only as the hypothetical exchangeable-rank calculation, not a property of this shift design. Replace the N-1 statement with the actual C2/D-19 dependency. |
| SN2-5 | BLOCKER | §2.1 lines 134–148 | The execution-delay rules admit different implementations and can suppress all fills. | A close(t) decision is due at open(t+2). The next decision at close(t+1) occurs at the same timestamp as open(t+2). If replacement is processed first, hourly decisions can perpetually cancel pending fills; if the due fill is processed first, they cannot. The draft also does not say whether unchanged targets create orders, what state band tests use while an order is pending, or whether a canceled increase resets the decision-time hold clock. Frozen wording measures from the last **risk increase**, not an unfilled decision. | Specify the timestamp event order, what creates an order, replacement eligibility, pending-target state, clock updates for filled/canceled actions, start-of-window pending state, and candidate/benchmark symmetry. Prefer the actual-fill clock unless an amendment expressly changes “last risk increase.” |
| SN2-6 | BLOCKER | §2.2 and §2.4 | Feature delay is directionally described but not executable at state and boundary cases. | “Value computed one bar earlier” can mean cached `F(t−1)` or recomputation with a cutoff at close(t−1); these differ for rolling state, scheduled refits, and missing observations. The first eligible decision may require data outside the window. Missing/nonfinite lagged inputs, model state, exposure state used by bands, and retraining-time information are not fully governed. A finite final statistic does not resolve an invalid intermediate input. | Define the exact information cutoff, rolling-state transition, permitted warm-up history, first-bar behavior, model/refit state, unlagged non-market state, and fail-closed reason codes separately for candidate and benchmark. |
| SN2-7 | BLOCKER | §2.3 and §5 question 5 | One bundled, recommendation-weighted question does not correctly resolve benchmark treatment for three different stresses. | Constitution §10 strongly supports equal comparison semantics for cost and execution, but it does not itself define the new stressed estimand. Feature delay is not among its enumerated terms, and lagging the benchmark’s volatility estimator changes the comparator rather than merely its execution. Calling every unstressed-benchmark option a departure from §10 overstates the frozen text. D-02 fixed G-5’s estimand, not these stress semantics. | Ask separately for G-5, G-6, and G-7. For each, name both legs, the exact stressed inputs, the resulting estimand, and whether the objective is relative robustness or degradation against a fixed baseline. Present §10 as evidence, not as having already decided the answer. |
| SN2-8 | NON-BLOCKING | §3 | The workload table is useful but not internally consistent as a run inventory. | From-scratch G-11 needs 500 null backtests plus one candidate and one benchmark run: 502. If candidate and benchmark are cached, its marginal count is 500. The stated 501 mixes those conventions. G-6/G-7’s eight and G-5’s four are correct gross per-nominee counts under identical stress, before caching. Feature recomputation/inference and null construction are omitted from workload. | Label counts as gross or marginal, add the benchmark or mark it cached, and record reusable work across nominees/families/cells separately from feature, inference, and refit costs. |
| SN2-9 | BLOCKER | §5 | The owner questions remain incomplete and non-neutral. | Q1 bundles null object with an undefined “match” amendment and recommends ratio shifting despite SN2-1. Q4 bundles two incomplete temporal contracts. Q5 bundles three distinguishable stresses and says §10 favors one answer. Q6 offers an unexplained `0.5` degradation threshold and depends on unresolved O-7. Availability, initialization, clipping, and family-specific treatment are absent. | Split construction, matching semantics, family treatment, numerical domain, execution contract, feature contract, and each benchmark-stress decision. Make D-15’s drawdown wording conditional on O-7 and treat any degradation threshold as a separate statistical choice. |

### Direct answers

1. **Ratio null:** It removes revision 1’s benchmark-sizing defect for benchmark-proportional candidates, as the exact `1` versus `25/43` check shows. It does not remove candidate-specific volatility-estimator misalignment. Clipping, tiny denominators, initial/warm-up state, the artificial wrap transition, bands, and minimum hold all create additional mismatch. Rewording “match” is necessary if ratio shifting is chosen, but the proposed informal wording is insufficient and partly false.

2. **Shifts and pass rule:** The distinct-shift boundary `T−2m≥499`, floor formula, 476 count, and tie rule are mathematically correct. The whole availability condition is not exact because numeric-domain, data/state, and intermediate-validity conditions are missing. The `25/501` result is only conditional on genuine exchangeability, which this deterministic shift set does not establish.

3. **Delay contracts and benchmark:** Neither delay contract is yet executable. The execution contract lacks decisive event ordering and state transitions; the feature contract lacks a precise information/state boundary. Treating both comparison legs identically is a strong reading for G-5 and G-7, but §10 does not automatically settle G-6 or justify bundling all three.

4. **Workload and questions:** The workload correctly recognizes D-19’s dominant costs but miscounts G-11 and omits important computational work. The owner questions are more separated than revision 1 but remain materially bundled and recommendation-biased.

### Revision-1 finding dispositions

| Finding | Status | One-line disposition |
|---|---|---|
| FN1-1 | PARTLY | Benchmark-proportional vol alignment is fixed, but alternative-estimator alignment remains confounded with timing. |
| FN1-2 | RESOLVED | The shifted object is now explicitly the complete hourly ratio path shifted by whole days. |
| FN1-3 | RESOLVED | The draft correctly says type-7 and rank rules are not nested. |
| FN1-4 | RESOLVED | The 476 alternative, `25/501` calculation, tie rule, and N-2 consistency are stated. |
| FN1-5 | PARTLY | Benchmark treatment is exposed, but the three stresses are improperly bundled and §10 is overstated. |
| FN1-6 | PARTLY | Several feature categories are enumerated, but the cutoff, rolling state, boundary, and invalid-input behavior remain open. |
| FN1-7 | PARTLY | A clock is selected, but decision-time accounting conflicts with unfilled/canceled orders and the frozen “last risk increase” event. |
| FN1-8 | PARTLY | D-19 multiplication is recognized, but the run inventory and non-backtest work remain incomplete. |
| FN1-9 | RESOLVED | Section 4 now states the correct conditional limitation rather than the erroneous constant-exposure example. |
| FN1-10 | RESOLVED | Deterministic shifts remove the proposed new RNG stream and its D-20 dependency. |
| FN1-11 | RESOLVED | `E-IMPROV` is correctly presented as a fresh D-14 choice. |
| FN1-12 | RESOLVED | O-7, N-2, and the shared G-5 benchmark dependency are recorded. |
| FN1-13 | PARTLY | Questions are split further, but material choices remain bundled or recommendation-weighted. |
| FN1-14 | PARTLY | The 30-day floor and embargo/ACF-derived `g` help, but no ratio-path persistence criterion establishes that near shifts are non-reproducing. |
| SN1-1 | PARTLY | Realized mismatch is admitted, but the proposed replacement for “match” is not precise and clipping defeats its stated preservation claim. |
| SN1-2 | PARTLY | Integer-shift uniqueness and endpoints are fixed; behaviorally identical paths and the full availability domain are not. |
| SN1-3 | RESOLVED | D-14’s estimand is explicitly a new owner choice. |
| SN1-4 | RESOLVED | Plus-one, rank-475, type-7, and ties are correctly distinguished. |
| SN1-5 | PARTLY | Pending and end-boundary rules were added, but timestamp ordering, order creation, initial state, and state transitions remain ambiguous. |
| SN1-6 | RESOLVED | Survival versus bounded degradation is expressly presented, including the large-degradation consequence. |
| SN1-7 | RESOLVED | The proposal now describes the null as conditional on the exposure pattern rather than validating that pattern. |
| SN1-8 | PARTLY | The expanded workload is directionally correct but G-11 is miscounted and computational scope remains incomplete. |
| SN1-9 | PARTLY | Six questions replace two, but several still bundle unresolved constructions and are not neutral. |

This AI review closes no D-row and accepts no method. Under the repository rule, it does not complete the R19-2 record until an authorized party saves and commits it with all findings and dispositions.

The new ratio idea fixes the simplest old volatility-sizing failure, but not the same problem for strategies using a different volatility estimator.  
Clipping and trading rules mean the null copies do not actually match the candidate’s exposure or turnover.  
The shift count and 476-of-500 arithmetic are correct, but the proposed availability rules are incomplete.  
The delay tests still leave enough timing and state ambiguity for two programmers to produce different results.  
Keep D-14 and D-15 blocked, revise the proposal, and submit the separated choices for another two-model review.