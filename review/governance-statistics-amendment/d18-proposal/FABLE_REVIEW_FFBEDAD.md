# Fable re-review of the D-18 proposal revision 2 at `ffbedad` — UNSOUND as written

Date: 2026-10-03. Re-review by the Anthropic family for R19-2
(`../d19-recommendation/OWNER_STEP0_DECISION.md`); requested by the owner
("start fable too"), in parallel with the Sol High re-review and without
sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`); prompt
  `REVIEW_PROMPT_FFBEDAD.md` (committed `cb116c6`), prefix FR2.
- Model metadata: self-reported by the reviewer as `claude-fable-5-1`; the
  launch requested the `fable` model. Not independently verified through
  provider metadata.
- Findings: FR2-1 BLOCKER; FR2-2 BLOCKER (decision framing); FR2-3..FR2-12
  NON-BLOCKING; FR2-13 QUESTION. Nothing is decided by this record; no finding
  is repaired here. The owner decides.

Below is the reviewer's final message, verbatim.

---

# Fable re-review of the D-18 proposal revision 2 at `ffbedad`

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family — the model metadata this session observed; not verified through provider metadata.
**Commit reviewed:** `ffbedad` (HEAD `cb116c6` adds only `REVIEW_PROMPT_FFBEDAD.md`; checked with `git diff --stat ffbedad HEAD`).
**Verdict: UNSOUND as written.** The §3 inclusion `F ⊆ E` is correct. But "one look" does not fix the trial set, so no fixed-design calibration measures `P_0(E)` (FR2-1). Separately, the whole-cycle 5% target cannot be met at the frozen 0.95 threshold in cells that are already known (FR2-2). Binding verdict: `REVISION_REQUIRED`; D-18 stays `KEEP_BLOCKED`.
Read-only: nothing edited, committed or pushed; no network; no confirmation or lockbox data. The only Sol record read was `SOL_REVIEW_690FA97.md`.

## Answers

**Q1 — event identity.** Rev 2 no longer claims the rev-1 identity. With top-Sharpe nomination, `{DSR(J_S) ≥ .95}` is a different event from `{max DSR ≥ .95}`; §3 says so correctly, and `E_S ⊆ E_DSR` holds on `A_f`. Ranking on the pre-Φ Sharpe removes the Φ-saturation and NaN-order defects (FR-8). Per-trial denominators `D_j` now affect only the nominee's own score, not the nomination. Residual: floating near-ties (FR2-10).

**Q2 — `P(false promotion) ≤ P(E)`.** As a set inclusion for a given realised `J_f`, it holds. It survives PBO and other family-level gates (extra conjuncts), unavailable trials (`A_f` is a conjunct), and mixed nulls under the same probability law; O18-1 now correctly claims no mixed-null number. It fails as a *calibrated* claim because `J_f` is chosen adaptively (FR2-1). It is also trivially satisfiable through unavailability (FR2-4). The top-Sharpe versus top-DSR comparison holds for the DSR stage only (FR2-5).

**Q3 — frozen conflict.** P18-3 narrows line 251. P18-4 uses fewer lockbox reads than the line-74 ceiling, which is permitted (Sol, `SOL_REVIEW_690FA97.md:36`); line 296 and Constitution §7 line 85 are consistent. P18-5 adds a new calibration clause. The §4 label (O18-8) is correct, and its §16 claim is correctly scoped: Constitution §16 enumerates "promotion gate" (lines 147–149). Lines 192–195 need no change now that P18-4 says frozen `cycle_termination` governs; listing them is harmless. PBO consistency depends on D-08 (FR2-7). If FR2-2 is resolved by raising the threshold, `dsr.minimum` and `promotion.dsr_minimum` (lines 231, 287) join the amendment scope.

**Q4 — O18-1..O18-9 not complete.** Missing: adaptive trial-set size (FR2-1); feasibility of the whole-cycle tolerance at 0.95 (FR2-2); D-19 ownership of 0.05, the DEC-02 per-cell inconsistency, and a two-family joint generator with cross-family dependence (FR2-3); an availability acceptance rule bound with the error rule (FR2-4); the D-08 dependency (FR2-7); the estimand that defines "false" (FR2-8); the attempt-based definition of `J_f` (FR2-9); nominee-identity agreement and technical invalidation (FR2-10).

**Q5 — "top Sharpe, no fallback", plainly.** Benefits: strictest DSR-stage rule (`E_S ⊆ E_DSR`); matches the expected-maximum-Sharpe model behind `S0` (`METHOD_CANDIDATE.md:90–99`) and the DEC-02 baseline's selection rule (`DSR_CALIBRATION_RECONCILIATION.md:78–79`), so baseline cells apply directly; with fixed `J_f`, one well-defined calibration target. Costs: a family fails when its top-Sharpe trial fails while another would pass DSR (Fable Example 3) or any downstream gate; the plateau boundary rule (line 264) rejects nominees on a grid edge — under an exchangeable null with three ordered model points the arg-max is on an edge with probability 2/3 (exchangeability; not calibrated); requiring every trial's DSR adds unavailability (FR2-12). Alternatives: top-DSR, no fallback — more power, larger null event `E_DSR`, departs from the `S0` motivation; fallback with "any trial passes all gates" — DSR-stage bound becomes `E_DSR`, downstream gates are applied up to |J_f| times so their multiplicity is uncontrolled; lockbox reads stay capped at 2 (line 74), but the owner has set the replacement read to "never".

## Status of earlier findings

| ID | Status in rev 2 |
|---|---|
| FR-1 | Partly resolved: the look time is fixed, but stop-when-ahead returns through registration (FR2-1). |
| FR-2 | Resolved as a definition (`E = E_trend ∪ E_vol`); feasibility open (FR2-2). |
| FR-3 | Resolved by owner direction "never use" plus O18-8 scope; needs the amendment. |
| FR-4 | Resolved in text (§3 para 2). Whether the owner saw the corrected comparison is unverifiable (FR2-13). |
| FR-5 | Resolved for `S0`; for PBO, conditional on D-08 (FR2-7). |
| FR-6 | Resolved (O18-1). |
| FR-7 | Resolved as a definition (P18-2, P18-5); the permanent-unavailability consequence remains (O18-2) and leads to a degenerate pass (FR2-4). |
| FR-8 | Resolved. |
| FR-9 | Resolved. |
| FR-10 | Deferred to the amendment text (O18-6); acceptable. |
| FR-11 | Resolved; Astra line 208 verified: "Per-family accounting does not establish a cross-family or lifetime false-pass bound." |
| FR-12 | Carried (O18-5); stated reason now outdated (FR2-11). |
| FR-13, FR-14 | Carried to the owner (O18-9). |
| SR-1 | Resolved. |
| SR-2 | Resolved. |
| SR-3 | Partly resolved: scope fixed; `J_f` adaptive (FR2-1). |
| SR-4 | Partly resolved: key fixed; near-ties and technical invalidation remain (FR2-10). |
| SR-5 | Resolved (P18-4 last sentence, O18-7). |
| SR-6 | Resolved by the switch to top-Sharpe. |

## Calculations

All deterministic, in memory (`.venv/Scripts/python.exe -B -`), no sampling. They use the `RECOMMENDATION.md` R19-5 model: iid or equicorrelated Gaussian trial Sharpes in standard-error units, √V replaced by its expected value, `z = 1.6448536`, `A(27) = 2.029601`, `A(54) = 2.305645`, `A(81) = 2.455554`. Approximations, not calibration.

1. **Adaptive stopping (FR2-1).** With `c_n = A(n) + z` increasing in `n`, the event ∪ₙ{M_n ≥ c_n} has complement ∏ⱼ Φ(c_j).

   | Trial set | `P_0(E_f)` |
   |---|---|
   | Fixed N = 27 / 54 / 81 | 0.32% / 0.21% / 0.17% |
   | Stop at hypothesis blocks {27, 54, 81} | 0.48% |
   | Stop at any n from 2 to 81 | 3.86% |
   | Stop at any n from 1 to 81 | 8.67% |

   Discriminating: fixed-design and adaptive numbers differ by up to 52×.

2. **N = 1 (FR2-2).** `S0 = 0` (single-attempt branch, `METHOD_CANDIDATE.md:171`), so `P_0 = 1 − Φ(z) = 0.05` asymptotically. N = 2 with actual V: `max − S0 = 0.70711·U + 0.18735·|W|`, giving `P_0 = 1.85%`. Correlation: for ρ = 0, 0.3, 0.6, 0.9, 0.99 → 0.167%, 0.774%, 2.251%, 4.245%, 4.907%, reproducing R19-5 (`RECOMMENDATION.md:127–139`). Per-family 2.5% therefore fails in the N = 1 cell and for ρ ≳ 0.65. Union (exact `Fraction`): independent families at p = 1/20 give `1 − (19/20)² = 39/400 = 0.0975`; with `P(E_t) = P(E_v) = p`, the union is ≤ p only if the events coincide almost surely.

## Findings

| ID | Severity | Location | Scenario and evidence | Proposed disposition |
|---|---|---|---|---|
| FR2-1 | BLOCKER | P18-1, P18-5 | The look time is fixed but `J_f` ("every trial … registered … by that look") is not. The sandbox receives `metrics.json` from confirmation (Constitution §7a line 92); hypotheses can be registered during the cycle (§8; budget up to three, protocol lines 184–189). A research process that stops registering after a good result and waits for day 180 realises ∪ₙ E_n, not a fixed-N cell: calc 1 gives up to 8.67% against 0.17%. Stopping below 20 trials also switches PBO off (line 235). No misconduct is needed; ordinary "stop when found" behaviour suffices. The owner's "Once, at a fixed time" direction is defeated in substance. | Owner decides: (a) preregister the family's complete trial set before its first evaluation; (b) blind per-trial confirmation metrics until the look (narrows §7a; amendment); or (c) calibrate the union over every permitted stopping point. |
| FR2-2 | BLOCKER (decision framing) | §0 "Whole cycle", P18-5, O18-4 | O18-4 calls feasibility "for calibration", but it is already known to fail in some cells: N = 1 gives ≈5%, ρ = 0.9 gives 4.25% per family (calc 2; R19-5 is committed but uncited by O18-4). Grid siblings differing only in `vol_target` plausibly sit in high-ρ cells (reasoning, not computed). Under "every preregistered no-edge scenario" (`RECOMMENDATION.md:86`), whole-cycle 5% at 0.95 can pass only by excluding those cells. The owner chose "Whole cycle" without being told. | Re-ask the owner with the consequence: (a) whole cycle with a stricter per-family threshold (amends lines 231, 287; D-19); (b) per-family tolerance (cycle ≈ up to 9.75%); (c) restrict the supported designs. |
| FR2-3 | NON-BLOCKING | P18-5 | "P_0(E) ≤ 0.05" is a tolerance owned by D-19 ("[owner sets, e.g. 0.05]", `RECOMMENDATION.md:86`; Sol `SOL_REVIEW_690FA97.md:108`). The DEC-02 baseline has `U_error ≤ 0.05` per family cell (`DSR_CALIBRATION_RECONCILIATION.md:87`), which conflicts with the 0.025 route. The union route needs a joint two-family generator; both families share the BTC benchmark and its days. | Label 0.05/0.025 as D-19 content decided jointly; note the DEC-02 record needs revision; add the joint generator to O18-5. |
| FR2-4 | NON-BLOCKING | P18-5, O18-2 | Unavailable replications are non-events. If `A_f` fails permanently (O18-2), `P_0(E) = 0 ≤ 0.05` and the calibration "passes" vacuously. At 60% unavailability, the conditional `P_0(E \| A_f)` can be 2.5× the unconditional figure. | Bind the availability acceptance rule (DEC-02 proposes ≤ 1%) with the error rule; report `P_0(E \| A_f)`. |
| FR2-5 | NON-BLOCKING | §3 para 3 | "Passes no more null families" holds only for the DSR stage. Counterexample: top-Sharpe X has DSR 0.96 and passes every gate; Y has DSR 0.97 but is on a plateau boundary. Top-Sharpe promotes X; top-DSR nominates Y and promotes nothing. The full false-promotion events are not nested, nor is power. | Restate as DSR stage only. |
| FR2-6 | NON-BLOCKING (inherited from `FABLE_REVIEW_690FA97.md:39`) | §3 para 2 | "Each keeps its single-test meaning" is overstated: the nominee is the arg-max of Sharpe on the same confirmation data used by the CI, null percentile and plateau, so their nominal levels do not hold given selection. Only the lockbox, on fresh data, keeps single-test meaning. | Replace with "no fallback adds no further multiplicity across nominations". |
| FR2-7 | NON-BLOCKING | O18-7 | Line 240's `paired_delta_sharpe` matches E-DIFF nomination only if D-08 adopts E-DIFF. D-08 is PROPOSED and amendment-required (`METHOD_CANDIDATE.md:57`). Under the E-IMPROV reading, Lemma L-1 means PBO ranks by the candidate's own Sharpe. | Make O18-7 conditional on D-08. |
| FR2-8 | NON-BLOCKING | P18-3, §3, O18-1 | Name the key as E-DIFF, unannualized daily `S` (`METHOD_CANDIDATE.md:96`). "Every promotion is false" and O18-1's "non-positive true mean" must say *E-DIFF* mean, because the CI gate is proposed on E-IMPROV (D-03) and the two can differ in sign. | Add the estimand identifiers. |
| FR2-9 | NON-BLOCKING | P18-1 | "Registered" does not match Constitution §0 line 13 and §9 line 102 ("counted when evaluation begins"); a grid registered but not started by day 180 is ambiguous. | Define `J_f` as `EVALUATION_STARTED` attempts (`METHOD_CANDIDATE.md:105`). |
| FR2-10 | NON-BLOCKING (SR-4 residual) | P18-3, P18-4 | "Full precision" leaves summation order unfixed, so Sharpes within one ulp can nominate different trials in reference and implementation. A technical failure during the nominee's gates or lockbox read is unaddressed. | Extend the exact-agreement rule (reconciliation lines 118–119) to nominee identity; bind technical invalidation. |
| FR2-11 | NON-BLOCKING | O18-5 | The stated reason ("top-Sharpe and top-DSR coincide") no longer applies after the switch. The real reason is that `P_0(E_S)` depends strongly on ρ and tails (calc 2). | Restate the reason. |
| FR2-12 | NON-BLOCKING | P18-2 | Only the nominee's DSR and the dispersion `V` are used, yet one non-nominee's unavailable DSR blocks the family. | Owner's choice: keep (matches DEC-02) and state the cost. |
| FR2-13 | QUESTION | §0 | Rev 1 recorded the option descriptions shown to the owner; rev 2 records only labels. Whether FR-4's disposition (giving the owner the corrected comparison) was carried out, and how the "5% noise limit" was described, cannot be verified. | Record the descriptions shown. |

## Verification protocol items run

1 (citations both ways): found uncited clauses — §7a line 92, §8, §0 line 13, R19-5, `RECOMMENDATION.md:86`, DEC-02 lines 78–87, line 235, D-08. 2 (referents): matrix line 65, Astra line 208, AS-3/P-7, "Fable Example 3", and the finding tags in P18/O18 point where claimed. 3 (bytes): the proposal records no hashes; all six files are `i/lf w/lf attr/text eol=lf`. 4 (discriminating reproduction): calcs 1 and 2 show fixed versus adaptive treatments differing; calc 2 reproduces R19-5. 5 (sweep arguments across options): FR2-5, FR2-7. 6 (right answer, wrong reason): FR2-5, FR2-6, FR2-11. 7 (tooling): frozen-hash verifier not applicable; `690fa97..HEAD` touches only `d18-proposal/`. 8 (exact arithmetic): 39/400. 10 (self-descriptions): the proposal's history line and review verdicts are true. 11 (inherited): FR2-6; the rest new or newly exposed. 12 (attribution): each attribution to another review cites its line. 13 (§16 scope): correctly applied by O18-8.

**Remaining owner decisions:** how to fix `J_f` against adaptive registration (FR2-1); tolerance scope given 0.95 is infeasible in some cells (FR2-2, D-19); availability acceptance rule (FR2-4); D-08, which O18-7 depends on; technical invalidation of the nominee's gates; deciding D-18 before D-16 (O18-9).
**Still not authorized:** closing D-18; any amendment or frozen edit; a calibration engine or simulation; governed trials; confirmation or lockbox access; promotion; deployment; trading.

## Plain-language summary for the owner

1. The core logic holds: a no-edge strategy can be promoted only if the one nominated strategy passes the DSR check.
2. But "pick once, at a fixed time" is not enough on its own.
3. Researchers see each strategy's results during the cycle, so they can stop adding strategies after a lucky one.
4. Stopping early makes luck pass far more often: up to about 9% instead of 0.2% in a simple model.
5. Fix this by declaring every strategy of a family up front, or by hiding results until the pick.
6. A 5% limit for the whole cycle cannot be met at the current 0.95 bar when strategies are very similar, or when a family has only one strategy.
7. Meeting it would need a stricter bar or a separate limit per family — your decision, made deliberately.
8. Nothing here is accepted or activated; these points go to you and the other reviewer before you decide D-18.
