# Fable re-review of the D-18 proposal revision 3 at `8ff7316` — UNSOUND as written

Date: 2026-10-03. Third-round re-review by the Anthropic family for R19-2
(`../d19-recommendation/OWNER_STEP0_DECISION.md`); requested by the owner
("yes start both reviews"), in parallel with the Sol High re-review and
without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`); prompt
  `REVIEW_PROMPT_8FF7316.md` (committed `29232f1`), prefix FR3.
- Model metadata: self-reported by the reviewer as `claude-fable-5-1`; the
  launch requested the `fable` model. Not independently verified through
  provider metadata.
- Findings: FR3-1 BLOCKER; FR3-2 BLOCKER (decision framing; fails closed);
  FR3-3..FR3-10 NON-BLOCKING. Nothing is decided by this record; no finding is
  repaired here. The owner decides.

Below is the reviewer's final message, verbatim.

---

# Fable re-review of D-18 proposal revision 3 at `8ff7316`

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family — the model metadata the session reported; not checked against provider metadata.
**Commit reviewed:** `8ff7316` (HEAD `29232f1` adds only `REVIEW_PROMPT_8FF7316.md`; `git diff --stat 8ff7316 HEAD`).
**Verdict: UNSOUND as written.** Within a single cycle, the declared trial set and shared pick fix the two rev-2 blockers. Two new blockers remain: the per-cycle bound in §3 does not hold from cycle 2 on, because later cycles reuse the same confirmation data (FR3-1); and the 1% availability ceiling cannot be met on the cell grid that O18-4 itself requires (FR3-2). Binding verdict: `REVISION_REQUIRED`; D-18 stays `KEEP_BLOCKED`.
Read-only: nothing edited, committed or pushed; no network; no confirmation or lockbox data. `SOL_REVIEW_8FF7316.md` was not read (not in the index when the folder was listed).

## Answers

**Q1 — event identity.** Correct within a cycle. Only the nominee's `D` and `T` enter `z_f*`; per-trial denominators affect neither the nomination nor `S0`. Ties are broken by declared id. `D = (1 − gS/2)² + (k − 1 − g²)S²/4 ≥ 0` by Pearson's inequality. But `D = 0` is possible: exactly, the series {1/8 ×9, 9/8 ×1} gives `g = 8/3`, `k = 73/9 = 1 + g²`, `S_T = 3/4`, `D = 0`; with the n−1 Sharpe the same series gives `D = 0.00263`, so `z` is huge but finite. P18-3 tests "finite … DSR statistic", and Φ(+∞) = 1.0 is finite, so the finiteness test must apply to `z` (FR3-5).

**Q2 — `P(false promotion) ≤ P(E)`.** As a set inclusion, `F_f ⊆ E_f` holds for any probability law: under mixed nulls (O18-1 rightly claims no number), with unavailable trials (`A_f` is a conjunct), and with PBO and other family-level gates (extra conjuncts). The researcher actions still possible — not starting declared trials, a protocol revision, an invalidation — can only shrink `E`, so they cannot inflate the per-cycle event. What fails is the calibrated per-cycle number from cycle 2 on (FR3-1). The number is also a confidence statement over qualifying cells, not a fact about the realised cycle (FR3-10).

**Q3 — frozen conflicts.** No proposed rule contradicts a non-amendable frozen requirement; the §4 amendment label is correct and the §16 (promotion gate) scope is correctly applied. Not yet covered: the shared pick at day 180 coincides with the frozen calendar termination (protocol lines 193–194), after which come the nominee's gates, the lockbox read and the 72-hour attestation (line 300); and `candidate_promoted` ends the cycle even with two nominees. Both need explicit amendment text (FR3-6).

**Q4 — O18 complete?** No. Missing: cross-cycle reuse of confirmation data (FR3-1); qualifying versus challenge cells against the reason-code contract (FR3-2); the procedure for choosing and certifying `z_crit` (FR3-3); the binding worst cell (FR3-4); the numeric contract for `z` (FR3-5); the window between pick and promotion (FR3-6); how reruns map to declared trials (FR3-7).

**Q5 — "Top Sharpe, no fallback".** Still a defensible candidate. Benefits: smallest DSR-stage event (`E_S ⊆ E_DSR`); matches the max-Sharpe model behind `S0` and the PBO ranking; applies the downstream gates and lockbox once per family. Costs: loses a family whose runner-up would pass; penalises a heavy-tailed top trial through its own `D`; leaves the selected-point CI, null percentile and plateau as post-selection quantities; under the "every cell" minimax, `z_crit` is pinned near or above 1.97 by the N=2 high-ρ cell, where the `S0` deflation does little, so the rule becomes in effect a ~2-sigma test on the top-Sharpe trial. Alternatives: top-DSR has more DSR-stage power and a larger null event; fallback to "any trial passes all gates" applies downstream gates up to |J_f| times with uncontrolled multiplicity. Swept across options: FR3-1 defeats all three rules equally (it acts through `S0`, not the nomination), so it favours no alternative.

## Status of revision-2 findings

| ID | Rev 3 |
|---|---|
| FR2-1 | Resolved within a cycle (P18-1); reappears across cycles (FR3-1). |
| FR2-2 | Resolved: re-asked, owner chose a stricter bar; option-text residual (FR3-4). |
| FR2-3 | Resolved (0.025, DEC-02 revision noted, joint generator in O18-4). |
| FR2-4 | Resolved as a rule (P18-7); feasibility residual (FR3-2). |
| FR2-5, FR2-6 | Resolved (§3 para 3; §3 para 2). |
| FR2-7 | Partly: §2 cites the wrong O-item (FR3-8). |
| FR2-8 | Resolved. |
| FR2-9 | Partly: `EVALUATION_STARTED` adopted; reruns unresolved (FR3-7). |
| FR2-10 | Resolved for nominee identity and technical invalidation; the pass decision needs the same rule (FR3-5). |
| FR2-11, FR2-12 | Resolved. |
| FR2-13 | Resolved as a record; fidelity to what the owner actually saw cannot be verified. |
| SR2-1 | Resolved for `E`; processing after the pick is not total (FR3-6). |
| SR2-2 | Resolved (z versus `z_crit`); residual in FR3-5. |
| SR2-3 | Resolved as a rule; infeasible on the stated grid (FR3-2, O18-2). |
| SR2-4 | Partly: cell list conflicts with DEC-02 (FR3-2). |
| SR2-5, SR2-6 | Resolved. |
| SR2-7 | Resolved by the owner's equal-split direction (pending decision). |
| SR2-8 | Carried in O18-5 to the amendment; acceptable. |

## Calculations

All in memory (`.venv/Scripts/python.exe -B -`), deterministic quadrature, no sampling. Model: iid Gaussian null trial Sharpes in standard-error units, large T (D ≈ 1). A(2) = 0.519755, A(81) = 2.455554, A(83) = 2.464336. Approximations, not calibration.

1. **Cross-cycle (FR3-1).** Cycle 1 evaluates 81 null trials. Cycle 2, on the same confirmation data, declares cycle 1's top two trials with lifetime N = 83: `z* = X(1) − (A(83)/√2)·(X(1) − X(2))`, integrated over the top-two order-statistic density `81·80·φ(x1)φ(x2)Φ(x2)^79`. P = **34.21%** at c = 1.96; 65.35% at 1.645. With count 2: 82.17% at c = 1.96. Declaring the top trial plus a near-duplicate sibling (V → 0) gives `1 − (39/40)^81 = 0.87136` exactly (Fraction). Discriminating: a fixed-design N=2 iid cell gives 0.579% at c = 1.96. A 2-D grid cross-check gives 33.93% with 0.99575 mass, in agreement.
2. **Worst cell (FR3-4).** Astra's actual-V N=2 model (`ASTRA_REVIEW_597DDC8.md:183–192`) reproduces 5.071376% at ρ = 0.9, c = 1.645, and 1.8487% at ρ = 0. At c = 1.96 the maximum over ρ is **2.5694%** at ρ ≈ 0.975, so a 2.5% cap needs c ≥ **1.97153**, before any Monte Carlo margin, finite-T or tail effects.
3. **Union:** `1 − (39/40)² = 79/1600 = 0.049375` under independence; the `≤ 0.05` bound is Boole's inequality.

## Findings

| ID | Severity | Location | Scenario and evidence | Proposed disposition |
|---|---|---|---|---|
| FR3-1 | BLOCKER | §3 "J_f is fixed before any result exists", P18-1, P18-7, O18-3 | In cycles ≥ 2, results already exist on the same confirmation data: partitions are fixed (protocol 65–67), exposed lockbox data rolls into confirmation (line 96; Constitution §7 line 81), and the sandbox has seen `metrics.json` (§7a line 92). A cycle-2 declaration of cycle 1's best trials is a fixed design only nominally. P_0(E) reaches 34% (top two, lifetime count) or 87% (top plus near-duplicate) against 0.58% for the fixed-design cell (calc 1). The lifetime count does not help: `S0 = √V_current·A(N)`, and V_current can be made near zero (Astra line 220 shows the same non-identifiability). Trilemma: under the current support, cycle ≥ 2 is `UNSUPPORTED_LIFETIME_HISTORY`, so availability is 0 and the 1% ceiling fails (O18-2); broadening the support breaks error control; omitting history cells from the grid certifies the per-cycle claim only for the first cycle. Distinct from O18-3 (lifetime accumulation): here the per-cycle bound itself fails. New in rev 3's justification; not raised before (grep of the d18 folder). | Owner decides: (a) restrict the claim to the first cycle on unseen confirmation data, stated; (b) a lineage and re-declaration rule (near-equivalents can evade it); (c) blind per-trial confirmation metrics across cycles (§7a amendment); (d) a history-aware dispersion (§5 line 67 forbids pooling; amendment). |
| FR3-2 | BLOCKER (decision framing; fails closed) | P18-7, O18-4, §0 R3-Q4 | The owner was told 1% is "the limit already proposed in earlier records (DEC-02)", but DEC-02 proposed it only over 16 independent-Gaussian equal-count cells (`DSR_CALIBRATION_RECONCILIATION.md:70–72, 87`). DEC-02 classes duplicates, dependence, heavy tails and lifetime mismatch as non-qualifying challenge cells (lines 88–91), and identical trial vectors return `UNSUPPORTED_DESIGN` (113–115). O18-4 makes those cells qualifying without citing this. In a duplicate cell availability is 0%, so no method qualifies. Realistic: with the 1.0 exposure cap (line 62), high `vol_target` siblings can produce identical series. | Re-ask the owner with this consequence: (a) broaden the support (statistical-spec change; Astra AS-3/P-7); (b) move those cells to challenge or unsupported status, refused at declaration where detectable; (c) a different ceiling. Revise the DEC-02 classification explicitly. |
| FR3-3 | NON-BLOCKING | P18-6 "set by the calibration" | Choosing `z_crit` from the same replications that certify it biases the upper bound; DEC-02 was designed to verify a fixed threshold. | D-19: choose `z_crit` on development replications only or analytically; certify on held-out replications at the frozen value; on failure no re-tuning against the same held-out set (DEC-02 lines 136–138). |
| FR3-4 | NON-BLOCKING (partly inherited from `FABLE_REVIEW_FFBEDAD.md:80, 87`) | §0 R3-Q3 option text | "Very similar strategies: ~4.25%" understates: the committed Astra figure for N=2 at ρ = 0.9 is 5.07%, above the one-strategy 5%, and at 1.96 the maximum is 2.569% (calc 2). The chosen option survives; the "exclude hard cases" description was incomplete (two-strategy families also exceed). FR2-2 cited only the 81-trial plug-in figure. | Record the corrected worst cell; the owner may re-confirm. |
| FR3-5 | NON-BLOCKING | P18-3, P18-6 | "Finite DSR statistic" admits Φ(+∞) = 1; `D = 0` occurs exactly for two-point series (Q1). Reconciliation lines 118–119 require exact agreement on the old `score ≥ 0.95` decision, but rev 3 extends it only to nominee identity. | Test finite `z` and `D > 0`; restate exact agreement for `z ≥ z_crit`; fix the decimal-to-binary64 parse of `z_crit`. |
| FR3-6 | NON-BLOCKING | P18-2 vs protocol 192–195, 300 | A day-180 pick coincides with the cycle's calendar termination, so the nominee cannot be promoted within the cycle; with two nominees the first promotion ends the cycle; with |J_f| < 81 the cycle idles until day 180. The bound is unaffected. | The amendment defines a post-pick window, the order of the two nominees, and termination on pick completion. |
| FR3-7 | NON-BLOCKING (FR2-9 residual) | P18-1 vs `METHOD_CANDIDATE.md:105–113`, protocol 292 | A rerun is a new attempt. P18-1 forbids "replaced" without saying whether rerunning a crashed declared trial is allowed; with |J_f| = 81 a rerun exceeds the hard-stop budget. | Owner/amendment: map attempts to declared trials. |
| FR3-8 | NON-BLOCKING (new in rev 3) | §2 "PBO alignment in O18-7" | O18-7 is the amendment scope; PBO is O18-6. Stale referent from renumbering. | Fix the referent. |
| FR3-9 | NON-BLOCKING (inherited from rev 2 O18-9) | O18-8 | `:65` carries `STAT`; "D-18 requires D-16" is at `HUMAN_DECISION_MATRIX.md:79`. | Cite line 79. |
| FR3-10 | NON-BLOCKING | §3 "≤ 0.05" | The bound holds with the preregistered simultaneous confidence, over qualifying cells. The realised design's correlation and tails are unknown at declaration, so covering the actual cycle rests on a domination assumption. | Reword §3. |

## Verification protocol items run

1 (citations both ways): found uncited DEC-02 lines 70–72, 88–91, 113–115; Astra 183–192, 220; protocol 62, 65–67, 96, 300; Constitution §7 line 81. 2 (referents): found FR3-8 and FR3-9; other citations resolve as claimed (§0 line 13, §9 line 102, protocol 74/231/235/240/251/287/192–195, `METHOD_CANDIDATE.md:96`, Astra 208, reconciliation 118–119, "Fable Example 3"). 3 (bytes): no hashes recorded; all d18 files `i/lf w/lf attr/text eol=lf`; PROPOSAL.md has 0 CR bytes. 4 (discriminating reproduction): calc 1 (34.2% vs 0.58%); calc 2 reproduces Astra's 5.07138%. 5 (sweep across options): FR3-1 applies to all three rules. 6 (right answer, wrong reason): §3's conclusion holds within a cycle, but its reason "before any result exists" is false for cycles ≥ 2. 7 (tooling): frozen-hash verifier not applicable — `git diff --stat ffbedad HEAD` over docs/protocols/schemas/specs/FROZEN_HASHES.json is empty; tests and lint N/A for Markdown. 8 (exact arithmetic): 79/1600; 1 − (39/40)^81; D = 0 in Fraction. 11 (inherited): FR3-4, FR3-9. 12 (attribution): every attribution cites its line. 13 (§16 scope): correctly applied.

**Remaining owner/statistician decisions:** FR3-1 (a–d); FR3-2 (a–c); the D-19 procedure for choosing and certifying `z_crit`; amendment text for the post-pick window and reruns; deciding D-18 before D-16.
**Still not authorized:** closing D-18; any amendment or frozen edit; a calibration engine or simulation; governed trials; confirmation or lockbox access; promotion; deployment; trading.

## Plain-language summary for the owner

1. Within one cycle the fixes work: declaring every strategy up front and picking once removes the "stop after a lucky one" problem.
2. But later cycles test on the same historical data the researchers have already seen.
3. In cycle 2 someone could re-declare cycle 1's luckiest strategies, and the noise-pass chance jumps from about 0.6% to between 34% and 87% in a simple model.
4. Counting all past attempts does not prevent this, because of how the penalty is computed.
5. You need to choose a protection for later cycles, or accept that the guarantee covers only the first cycle on unseen data.
6. The 1% "almost never unavailable" limit cannot be met on the test cases the proposal itself lists, because identical strategies are currently refused by design.
7. The hardest case for the stricter bar is two very similar strategies, not one; the bar needs to be about 1.97 rather than 1.96, before safety margins.
8. Nothing is accepted or activated; these go to you and the other reviewer before you decide D-18.
