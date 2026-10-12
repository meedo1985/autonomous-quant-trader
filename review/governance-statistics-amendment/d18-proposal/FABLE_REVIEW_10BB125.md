# Fable re-review of the D-18 proposal revision 4 at `10bb125` — SOUND WITH FIXES

Date: 2026-10-03. Fourth-round re-review by the Anthropic family for R19-2
(`../d19-recommendation/OWNER_STEP0_DECISION.md`); requested by the owner
("ok wait for both reviews"), in parallel with the Sol High re-review and
without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`); prompt
  `REVIEW_PROMPT_10BB125.md` (committed `8fba42c`), prefix FR4.
- Model metadata: self-reported by the reviewer as `claude-fable-5-1`; the
  launch requested the `fable` model. Not independently verified through
  provider metadata.
- Findings: FR4-1..FR4-15, all NON-BLOCKING; no blocker. Binding verdict
  `KEEP_BLOCKED` for D-18 (method under O18-2 does not exist; owner decision
  pending). Nothing is decided by this record; no finding is repaired here.

Below is the reviewer's final message, verbatim.

---

# Fable re-review of D-18 proposal revision 4 at `10bb125`

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family — the model metadata my session reported; not checked against provider metadata.
**Commit reviewed:** `10bb125` (HEAD `8fba42c` adds only `REVIEW_PROMPT_10BB125.md`; `git diff --stat 10bb125 8fba42c`).
**Verdict: SOUND WITH FIXES.** Within one eligible cycle the bound holds: P18-0 (only unseen data can promote) removes the cross-cycle failure FR3-1; the shared pick and the 1% scope were re-asked; `F ⊆ E` survives everything I tried. No new blocker. Fourteen non-blocking findings remain, on the frozen-text routes and outcomes P18-0 needs, owner-facing framing, an availability policy the author chose without asking the owner, and calibration-contract gaps. Binding verdict: `KEEP_BLOCKED` for D-18 — the method on which `z_crit` will be calibrated does not exist yet (O18-2), and the owner's decision is pending.
Read-only: no edits, commits, pushes or network; no confirmation or lockbox data. `SOL_REVIEW_10BB125.md` not read.

## Answers

**Q1 — event identity: correct.** `E_f = A_f ∩ {z_{J_f*} ≥ z_crit}`, `J_f* = argmax(S_j, −id_j)`. Each trial's own `D` and `T` enter only its `z`; nomination uses only `S` and ids. Ties are broken by declared id; non-finite values fail `A_f` before nomination. The cited formula is right: `METHOD_CANDIDATE.md:92` is the pre-Φ argument and `:91` is `D`. The event is still not "some trial passes", as revision 4 says; the two-trial counterexample in `SOL_REVIEW_8FF7316.md:53–58` stands. One drafting gap remains (FR4-7).

**Q2 — `P(false promotion) ≤ P(E)`: correct as a set inclusion under any probability law.** P18-0 adds one more conjunct (eligibility); an ineligible cycle has `F = ∅`. Mixed nulls: no number claimed, correctly (O18-1). Unavailable trials fail closed. PBO and other family-level gates are extra conjuncts. Limits of the numerical bound: per eligible cycle, at the preregistered confidence, over qualifying cells only (§3, FR3-10); across the seen/unseen boundary it also assumes no serial dependence between the windows (FR4-12).

**Q3 — frozen conflicts.** No rule contradicts a non-amendable frozen requirement; the §4 label and §16 promotion-gate scope are correct. Not cited or not handled: Constitution §7 line 81 (second sentence), line 83, §0 line 20, §7a line 88 (FR4-2); §5 line 61 with protocol line 194's trigger (FR4-5); §5 line 63 and protocol line 195 for ineligible and no-result cycles (FR4-4). `configuration_selection` (line 251), plateau and PBO are compatible, as in revision 3.

**Q4 — O18-1..O18-8 complete? No.** Option C also needs: a total `A_f` (FR4-7); joint-cell or allocation rules for the whole-cycle 1% (FR4-8); the scope of the operational no-result rate (FR4-8); a seen/fresh boundary gap (FR4-12); the lifetime-N covariate under P18-0 (FR4-13); a rerun decision (FR4-6); availability outside the global null (FR4-15).

**Q5 — top Sharpe, no fallback: still defensible.** Benefits: smallest DSR-stage event (`E_S ⊆ E_DSR`); matches the max-Sharpe model behind `S0`, the PBO ranking (line 240) and the DEC-02 baseline (`DSR_CALIBRATION_RECONCILIATION.md:78–79`); downstream gates and lockbox applied once. Costs: a family is lost when the runner-up would pass (DSR, plateau or interval); a heavy-tailed top trial is penalised through its own `D`; selected-point gates remain post-selection; the global `z_crit` is pinned by the worst cell, so wide independent families are over-protected. New in revision 4: under P18-0 every lost family costs a fresh data window, which may take a year or more to accrue (FR4-3), raising the price of no fallback. Alternatives: top-DSR — more DSR-stage power, larger null event, needs its own `z_crit`; fallback to "any trial passes all gates" — DSR stage becomes `E_DSR`, downstream gates run up to `|J_f|` times with uncontrolled multiplicity, frozen two-read lockbox limit still applies. Option sweep: no new finding favours one rule; all apply equally to every nomination rule.

## Status of revision-3 findings

| ID | Revision 4 |
|---|---|
| FR3-1 | Resolved by the owner's P18-0, within eligible cycles. Residuals FR4-1..FR4-4, FR4-12, FR4-13. |
| FR3-2 | Resolved as decision framing (round 4 Q2 re-asked; O18-2); feasibility deferred to the broadened method. Option text overstates broadening (FR4-11). |
| FR3-3 | Resolved (P18-6). |
| FR3-4 | Worst cell recorded (§0, O18-4). The claim it was re-asked is false (FR4-10). The "lower bound" label is specific to the current method (FR4-9). |
| FR3-5 | Resolved (P18-3, P18-6). |
| FR3-6 | Deferred to the amendment (P18-2, O18-7); concrete residual FR4-5. |
| FR3-7 | Resolved by the author's rerun ban, not put to the owner (FR4-6). |
| FR3-8 | Resolved (§2 cites O18-6, PBO). |
| FR3-9 | Resolved (`HUMAN_DECISION_MATRIX.md:79` reads "`D-18` require `D-16`"). |
| FR3-10 | Resolved (§3). |
| SR3-1 | Resolved by the re-ask (round 4 Q3); residual FR4-5. |
| SR3-2 | Resolved in text; calibration cannot generate governance no-picks (FR4-8). |
| SR3-3 | Resolved; residuals FR4-7, FR4-14. |
| SR3-4 | Resolved (one global `z_crit`, development/held-out split); classifier residual FR4-8. |
| SR3-5 | Resolved (owner chose whole cycle); joint-cell residual FR4-8. |
| SR3-6 | Resolved. |

## Calculations

All in memory, `.venv/Scripts/python.exe -B -`, deterministic quadrature, no sampling. Large-T Gaussian, Sharpes in standard-error units, `N=2`, actual-sample `V` with the `K−1` denominator, `z* = U/2 + (1/2 − A(2)/√2)|W|`. Approximations, not calibration.

1. **Worst cell at N=2.** `A(2) = 0.5197553`. At ρ = 0.9, c = 1.645: P = **5.0714%** (reproduces Astra's committed 5.07138%). At c = 1.96 the maximum over ρ is 2.5692% at ρ ≈ 0.975; a 2.5% cap needs c ≈ **1.9716** (agrees with FR3's 1.97153 to grid precision). Discriminating: the same cell at c = 1.645 gives **5.523%** with the `K` denominator for `V`, and **6.813%** with no penalty (`S0 = 0`); the number is method-specific (FR4-9).
2. **No reruns, 162 declared trials.** P(any crash) = 1 − (1−p)^162: 1.607% at p = 10⁻⁴; 14.96% at 10⁻³; 80.4% at 10⁻². The 1% target needs p ≤ 6.20×10⁻⁵ (FR4-6).
3. **Fresh-window length.** Fallback ESS 120 effective decisions (lines 244, 290) at a 168-hour horizon needs 120 × ceil(168/24) = 840 daily decisions ≈ **27.6 months** (FR4-3). Fallback rule only; the primary Newey-West ESS was not computed.
4. **Monotonicity.** `∂z/∂A(N) = −√V·√(T−1)/√D ≤ 0`, and `A` increases for N ≥ 2, so with data fixed `z` falls as N rises (exact; FR4-13).

## Findings

| ID | Severity | Location | Scenario and evidence | Proposed disposition |
|---|---|---|---|---|
| FR4-1 | NON-BLOCKING | P18-0 | The operational test is narrower than its title and the owner's option: "never seen" is tested only as no **per-trial** confirmation metric "returned to research"; it omits family-level output (report.md, gate outcomes, nominee identity; §7a line 92) and does not freeze eligibility at declaration. "Never seen" is operational only — BTC public price history is known to everyone. | Restate: no evaluation output of any kind computed on any part of the window by any process before declaration; record eligibility in the hashed declaration. |
| FR4-2 | NON-BLOCKING (citations missed by topic) | P18-0, O18-7 | Uncited frozen clauses govern creating a fresh window: Constitution §7 line 81 (second sentence) "Lockbox boundary only moves forward"; §7 line 83, exploration/confirmation boundary moves "only between cycles and only forward"; §0 line 20 "Lockbox = future data"; §7a line 88, the sandbox mounts exploration only. Data after 2026-08-31 belongs to no v1 partition. The frozen-compatible route to fresh confirmation is an **unexposed** lockbox segment rolling forward; P18-0 makes exposed lockbox data permanently ineligible, so every lockbox read burns that segment for later promotion. O18-7 lists only protocol 65–67. | Cite these; the amendment assigns new data to a partition at ingest (off the sandbox) and states whether §0 or §7 changes. |
| FR4-3 | NON-BLOCKING (decision framing) | §0 round 4 Q1 option text | No scale is given: "promotion after cycle 1 waits for fresh data". The fallback ESS at a 168-hour horizon alone needs ≈27.6 months (calc 3); complete 3-month blocks (line 282) and a fresh lockbox span add to that; DSR power scales with √(T−1). Each failed family consumes a whole window. | Show the owner the order of magnitude before the D-18 decision. |
| FR4-4 | NON-BLOCKING (extends FR-2, `FABLE_REVIEW_690FA97.md:35,:56`) | P18-0, P18-2 vs Constitution §5 line 63, protocol 195 | Ineligible and no-result cycles have no matching outcome: a research-only cycle ending at day 180, or one where both families are `UNAVAILABLE`, would be recorded `NO_EDGE_FOUND` though nothing was tested — an outcome tied to the deployable-baseline path (§11 lines 113–116). | The amendment maps these to an outcome; a new outcome changes §5. |
| FR4-5 | NON-BLOCKING | P18-2 vs protocol 194, Constitution §5 line 61 | Trials count from `EVALUATION_STARTED` (P18-1; §9 line 102). With 81 declared per family, `all_family_trial_budgets_exhausted` fires when the 162nd trial *starts*, so the cycle ends before the pick and every full-budget cycle becomes "no result". §5 line 61 (uncited) forbids simply removing the trigger. | Redefine budget exhaustion as completion of the declared plan; cite §5 line 61. |
| FR4-6 | NON-BLOCKING (FR3-7 residual; disposition at `FABLE_REVIEW_8FF7316.md:82` was "Owner/amendment") | P18-1 "rerun" | The rerun ban is the author's choice, not put to the owner. It buys no error control: rerunning a crashed trial with the same declared hash and the deterministic seed (line 266), before any of its output is returned, reproduces the same result. Its cost is large (calc 2) and synthetic calibration will not show it. | Ask the owner: allow one rerun only if no output was returned and the budget allows (§9 line 102, line 292); otherwise keep the ban. |
| FR4-7 | NON-BLOCKING | P18-3 vs P18-1 | `A_f` is not total: it lists numerical conditions only. P18-1 calls a hash-mismatched evaluation a "technical failure" without saying `A_f` fails; a mismatched non-nominee with finite `S` could enter `V` — evaluating a near-copy of the top trial shrinks `V`, lowers `S0` and raises `z*`. Whether a crashed trial counts as "finished" for the P18-2 trigger is unclear. | Add to `A_f`: every declared trial started, completed exactly once, with a matching hash; define the trigger accordingly. |
| FR4-8 | NON-BLOCKING | P18-7, O18-4, §0 round 4 Q4 | (a) A null-generator calibration cannot produce no-picks from protocol revisions, invalidations, day-180 truncation or real infrastructure crashes; those components are zero there, yet the option text reads as a certified real-world limit. (b) The classifier maps *each family* to a cell, but a cycle-wide bound needs joint (pair) cells or an allocation (e.g. 0.5% per family). Whether ineligible cycles count is unclear. | State that calibration certifies only procedure-internal no-results and the operational rate is monitored; D-19 chooses joint cells or an allocation; exclude ineligible cycles explicitly. |
| FR4-9 | NON-BLOCKING | P18-6 "Known lower bound: about 1.972" | Method-dependent: it holds for the current candidate (actual `V`, `K−1` denominator, raw N=2). The owner chose to broaden the method; the same cell moves to 5.52% or 6.81% under other `V` or `S0` treatments (calc 1). Model-independent only if the method sets `S0 = 0` at N=1: c ≥ 1.95996 (AS-3 unresolved). | Relabel "for the current candidate, in the large-T Gaussian model". |
| FR4-10 | NON-BLOCKING (false self-description) | §0, paragraph after round 3 | "Round 4 re-asked both consequences" is false: round 4 Q2 re-asks the round-3 Q4 consequence, but no round-4 question re-asks the round-3 Q3 correction (worst cell, ~1.972). FR3-4 allowed this ("the owner may re-confirm", `FABLE_REVIEW_8FF7316.md:79`), but the sentence is false. | Correct the sentence, or ask the owner. |
| FR4-11 | NON-BLOCKING (framing) | §0 round 4 Q2 "Broaden the method" | "The guarantee would then cover real data" overstates: by §3 (FR3-10) a real cycle is covered only if a qualifying cell dominates it. Broadening enlarges the qualifying set; it does not guarantee coverage of real data. | Record the correction; the owner may re-confirm. |
| FR4-12 | NON-BLOCKING (magnitude UNVERIFIED) | P18-0 | No seen/fresh boundary gap: with serial dependence and overlapping labels up to 168 hours, luck-selected noise at the end of the seen window carries into the first fresh days. The purge rule (line 205) applies only inside validation folds. | Require a purge and embargo gap ≥ `max(label_horizon, embargo)` (line 207); add a calibration cell. |
| FR4-13 | NON-BLOCKING (input to D-16/D-17) | P18-0 with `OWNER_CHOICE_CANDIDATE_COUNT.md` | Under P18-0 the selection event in an eligible cycle runs over the `|J_f|` fresh-window trials only, and `z` falls as N rises (calc 4), so the worst case is `N_lifetime = |J_f|`. The lifetime count adds no error control to the per-cycle claim; it costs power and, under the current method, availability. Research-only cycles keep raising N for every later eligible cycle. The cross-cycle lifetime bound (O18-3) is still not provided. | Show the owner before D-16/D-17 and before any research-only cycle; calibration may treat N as a covariate with worst case `|J_f|`; monotonicity of the broadened method in N is UNVERIFIED. |
| FR4-14 | NON-BLOCKING (consequence of `SOL_REVIEW_8FF7316.md:33`) | P18-1 `1 ≤ |J_f|` | Both families must declare in every cycle; a cycle researching one family cannot start, inviting token declarations that inflate N (FR4-13) and no-result exposure. | Owner question: allow `|J_f| = 0` (family not declared, `E_f = ∅`, excluded from the no-result target). |
| FR4-15 | NON-BLOCKING | P18-7 | Availability is bounded only under the global null; a method often unavailable when a real edge exists would still qualify. | D-19 reports availability in power and mixed-null cells. |

## Verification protocol items run

1 (citations both ways): all cited lines resolve as claimed (protocol 65–67, 74, 90–91, 96, 192–195, 231, 235, 240, 251, 270–292, 300; Constitution §0 line 13, §7 line 81, §7a line 92, §9 line 102; `METHOD_CANDIDATE.md:92,96`; DEC-02 70–72, 88–91, 113–115, 118–119; `HUMAN_DECISION_MATRIX.md:65,79`; Astra :208). Search by topic found uncited governing clauses: §0 line 20, §5 lines 61 and 63, §7 lines 81 and 83, §7a line 88, §11, protocol 205, 244, 266, 282, 290. 2 (referents): FR3-8, FR3-9 fixed; FR4-10 found. 3 (bytes): no hashes recorded; `PROPOSAL.md` `i/lf w/lf attr/text eol=lf`, 0 CR bytes. 4 (discriminating reproduction): calc 1, 5.071% vs 5.523% and 6.813%. 5 (sweep): FR4 findings apply to every nomination rule. 6 (right answer, wrong reason): P18-0's conclusion endorsed within a cycle; its operational test too narrow (FR4-1). 7 (tooling): frozen-hash verifier not applicable — `git diff --stat 10bb125 HEAD` over frozen paths empty; `8ff7316..8fba42c` touches only the d18 folder; tests/lint N/A for Markdown. 8 (exact arithmetic): monotonicity is an exact derivative; calc 2 used `Fraction` for p. 9: nothing repaired; every disposition is a proposal. 10 (self-descriptions): FR4-10. 11 (inherited): FR4-4 extends FR-2; FR4-6 is FR3-7's residual; FR4-9 relabels FR3-4's figure. 12 (attribution): every attribution cites file and line. 13 (§16 scope): correctly applied.

**Remaining owner/statistician decisions:** rerun policy (FR4-6) and family opt-out (FR4-14); how fresh windows are created and assigned to partitions, and outcome labels for ineligible and no-result cycles (FR4-2, FR4-4); re-confirming the framing in FR4-3, FR4-10, FR4-11; the D-16/D-17 count given FR4-13; whether to decide D-18 before the broadened method exists.
**Still not authorized:** closing D-18; any amendment or frozen edit; a calibration engine or simulation; governed trials; confirmation or lockbox access; promotion; deployment; trading.

## Plain-language summary for the owner

1. Within one cycle on fresh data, the safety logic now holds; I found no new blocking problem.
2. "Only unseen data can promote" works, but fresh data may take a year or more to collect for some strategies.
3. Each lockbox check uses up that data for later promotions, and the frozen rules decide how new data can enter.
4. The "count every attempt ever made" rule no longer adds safety under this design; it only lowers your chance of finding an edge.
5. Banning reruns of crashed tests adds no safety, but one crash can void a whole family's result; that is your call.
6. The 1% "no result" limit can only be tested for the method itself, not for real-world crashes or cancelled cycles.
7. A few descriptions shown to you claimed slightly more than is true; they should be corrected and you may re-confirm.
8. Nothing is accepted or activated; D-18 stays blocked until you decide and the broadened method exists.
