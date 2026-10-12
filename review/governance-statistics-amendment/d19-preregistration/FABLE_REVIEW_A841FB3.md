# Fable re-review DF4 of the D-19 preregistration rev 4 at `a841fb3`: SOUND WITH FIXES

Date: 2026-10-04. This is an R19-2 independent statistical re-review, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

Model: Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family. The drafter, Claude Opus 5.5, is in the same family, so this is only the Claude half of R19-2.
Commit: `a841fb3` (branch `docs/d19-recommendation`). Object: `review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md` rev 4.
Verdict: **SOUND WITH FIXES.** Both DS3 blockers are substantially closed, and no finding below is a BLOCKER. Two MAJOR paper fixes remain:
- the declaration-time "mapping" accepts any design that falls inside a union box spanning all cells at `T_C2`, so it never maps the design to a qualifying cell (DF4-1);
- the AQTQ1 substitution does not say what happens when an O-6a invalidation occurs after the held-out run, and it leaves O-6a's "C2 ends" horizons without a replacement (DF4-2).

## Status of DF3 and DS3

| ID | Status | Note |
|---|---|---|
| DF3-1 | RESOLVED | `K = 2` is restored in Q1 and Q2. QJ shares one market path and its BTC days. The coverage rule is added. Residuals: DF4-1, DF4-3. |
| DF3-2 | RESOLVED | Thresholds are taken over the final cells, per `T`. Acceptance on challenge cells is reported. Residual: DF4-5. |
| DF3-3 | RESOLVED | `T_min` is chosen on availability only, τ uses `M_max`, and the `N_i` rule is exact. Residual: the quoted τ values (DF4-6). |
| DF3-4 | PARTIAL | Each attempt has its own key, coin and deadline; the script is given; fees are per attempt. Attempt void is underdefined: DF4-2. |
| DF3-5 | RESOLVED | Clusters are {1,4}, {5,15} and {20,60}. |
| DF3-6 | RESOLVED | Q5 includes `K = 1`. G-4 is simulated inside `U_G`. The cap rate is the 90% UCB. |
| DF3-7 | RESOLVED | Philox 4×64-10, a big-endian key, counter 0, a pinned numpy version, and 0-based `j` and `rep`. |
| DF3-8 | RESOLVED | The path length is fixed. §12 states that a set is undeclarable if the screen cost is infeasible. |
| DS3-1 | PARTIAL | `K = 2` and a pre-declaration exploration-data step now exist. The step compares the design with a union box over every cell at `T_C2`, so it maps to no qualifying cell: DF4-1. |
| DS3-2 | PARTIAL | The channel is specified by substitution and put to the owner as Q-1. Gaps remain: DF4-2. |
| DS3-3 | RESOLVED | The threshold run covers every candidate cell and stores per-cell order statistics. |
| DS3-4 | RESOLVED | `U_G` is one union event with one Clopper–Pearson (CP) test. G-10 is evaluated on the whole family matrix. |
| DS3-5 | PARTIAL | Most items are fixed. Two remain: the "opposites" Σ is undefined and can be non-PSD, and the hourly path chaining is unspecified (DF4-4). |
| DS3-6 | RESOLVED | The joint figure is a labelled plug-in diagnostic. |

## Answers to the questions

- **Q2 (O18-4).** It is met in substance except for the mapping (DF4-1):
  - one- and two-trial families: yes;
  - high correlation, near-duplicates (ρ = 0.999), exact duplicates and opposites: yes;
  - unequal clusters: yes;
  - unequal `T`: covered by the `T` levels. Annex B §2.1 forces one day index per family, so cross-cell `T` is the only meaning;
  - serial and cross-trial dependence, and heavy tails: yes;
  - the joint generator sharing BTC days: yes (QJ);
  - unequal moments: no designed cell (DF4-3).

  O18-4's "maps each declared family design to a qualifying cell" is not met as written.
- **Q3 (AQTQ1).** The bytes are correct: `41 51 54 51 31`, `6a 25` + 5 + 32 = 39 bytes, inside both relay limits. Separate keys and coins per attempt, the pre-beacon commitment and the per-attempt drand anchor are sound. Fix DF4-2 before the channel goes to the owner as Q-1. The remaining questions are timing and horizon definitions, not design.
- **Q4.** See the findings below. §11's sentence "mapped deterministically to a qualifying cell" overstates until DF4-1 is fixed. After DF4-1..DF4-4, the document is ready for owner acceptance, followed by a measured pilot. A narrow re-check of those edits is enough; a full re-review is not needed.

## New findings

| ID | Sev | Location | Problem | Evidence | Fix |
|---|---|---|---|---|---|
| DF4-1 | MAJOR | §3.5 step 2, §3.6 "Mapping", §11; adjudication row DS3-1 | **The mapping compares the design with a union box, not with a cell.** The frozen thresholds are per `T` level and are the extreme over **all** final qualifying cells, pooled over every `K`, law and dependence level. §3.6 accepts a design if each diagnostic is inside those thresholds. So the design is checked against the marginal extremes of the union of all cells. A design that combines heavy tails, high correlation, serial dependence and `K = 80` is accepted even though no cell has that combination. No cell id is identified. The adjudication says "envelope of the qualifying cells at its `(K, T)`", but the text says "per `T` level", so the two disagree. | O18-4: "maps each declared family design to a qualifying cell". §3.5 line 186; §3.6 line 199. | Keep the pooled thresholds for the **window classifier**. Its per-cell refusal bound still holds, because the pooled threshold is at or beyond each cell's own order statistic. For the **declaration mapping**, accept if and only if there is at least one final qualifying cell `c` with `K_c = K` and `T_c = T_C2` whose **own** stored per-tail order statistics contain every diagnostic. Record that cell id, or the set of matching cell ids, in the declaration. A design whose law is that cell's law is still accepted with probability about 1 − 9·1.1e-5. Reword §11 to match. |
| DF4-2 | MAJOR | §4 "Channel for `<<OWNER Q-1>>`", §4 step 6, §8 | **The O-6a substitution is incomplete in timing and horizon.** (a) Several O-6a invalidations can occur **after** the held-out run: a later post before "C2 ends", or an earlier capture shown "before C2's evaluation is final" (SPEC §3, §5). Yet "attempt void" is defined as "held-out run not made". If a void after the run reset the attempt, the owner, who holds `A_Q1` until its procedural destruction, could convert a failed attempt 1 into a void and reach attempt 2 without the recorded-change rule. (b) O-6a's horizons "after signing", "before C2 ends" and "before C2's evaluation starts" (the condition on `D`) have no stated substitutes. (c) Step 6 runs the held-out certification once the round is published. Under O-6a, `T_Qn` and the round are frozen only at the freeze read, 7 days after acceptance; the round time `T + 24h` can come before that. (d) It does not say which namespace and object a later attempt uses after a void. (e) `D_Q2` is fixed at acceptance, although attempt 2's timing is unknowable then. | SPEC §3 (first-post rule), §5 (freeze point, earlier-capture rule), §7 (deadline). | (a) An invalidation found before the held-out run starts gives attempt void. One found at or after the start counts as a **failed** attempt: namespace burned, P18-6 applies. (b) Substitute "acceptance of this preregistration" for signing. Substitute "the owner's accept/reject of certification (§12 item 4)" for "C2 ends" and "evaluation final". `D_Qn` must fall above the acceptance height. (c) Run the held-out after the O-6a freeze read **and** the round's publication. (d) After a void, the next attempt may post the same object under `d19-heldout-v{n+1}` with no recorded change required. (e) Allow `D_Q2` to be fixed in the attempt-2 record before its post. |
| DF4-3 | MINOR | §3.2 "Coverage rule" | **The coverage rule cannot be applied mechanically.** No table maps each category to cells. "Unequal moments", meaning heterogeneous column variance, skew or kurtosis, has no designed cell: every agnostic cell gives all columns one law and one scale. Only Q5 covers it, and only incidentally. | §3.2 tables; DSR_CALIBRATION_PLAN line 37 and SR2-4 ("heterogeneous moments"). | Add a category-to-cell table. Either add a Q2 mixed-law cell (for example half t₅ and half Gaussian, with column scales 0.5× and 2×) or map "unequal moments" to Q5 explicitly. |
| DF4-4 | MINOR | §3.1, §3.2 "opposites", "one factor"; §7.2 | **Some generators are still underdefined.** (a) Opposites gives ρ = −0.9 between groups but no within-group ρ. If the within-group ρ is 0, Σ is non-PSD for `K ≥ 5`: minimum eigenvalue −1.205 at `K = 5` and −35.0 at `K = 80`. With a within-group ρ of 0.9 it is PSD, with minimum eigenvalue 0.1. (b) The one-factor Σ (λλ′ + diag(1 − λ²)) and the near-duplicate pairing at odd `K` are implied but not written. (c) The screen does not say how reflected hourly bars chain into a price path: whether each open equals the previous close, and how gaps are handled. | In-memory eigenvalue check (below). | State the within-group ρ (0.9), the factor formula, the pairing (pairs (0,1), (2,3), …, with a leftover column independent), and the open = previous close chaining. |
| DF4-5 | MINOR | §4 steps 3–5, §5 | **The development thresholds are unstated.** Development replications include classifier refusals, but the text does not say which thresholds they use. Presumably it is the all-candidate envelope per `T`. The frozen thresholds are tighter, so held-out refusals can be up to about 1e-4 higher than in development. That is about 10% of τ_DSR. Validity is unaffected, because the held-out uses the frozen thresholds. | §3.5, §5 order. | State that development uses the all-candidate-cell envelope. Note that held-out refusal can exceed development refusal by up to the per-cell tail sum. |
| DF4-6 | MINOR | §5 "Targets", §10 | **The quoted τ and compute figures are stale.** My count at `T_min = 365` is 371 cells and `M_max` = 1,143 tests: Q1 175, Q2 156, Q3 6, Q4 8, Q5 20 and QJ 6 cells; QJ has 8 tests per cell. At `M = 1,143`, τ_G(20k) = 0.000148, not 0.000175. A 22k development run then needs 0 `U_G` events for `N = 20k`. τ_err = 0.01763, τ_DSR = 0.00113 and τ_G(40k) = 0.000415 are unchanged. The compute estimate predates the roughly 30% larger grid and QJ's double cost. | In-memory exact-binomial calculation (below). | Quote the τ values at the actual `M_max`. Mark the 2,000–7,000 core-hour estimate as pre-rev-4, to be replaced by the pilot. Add to the pilot an exploration-data mapping run of the real trend and vol libraries, to measure how often real designs are refused. |

## Commands run

- `git rev-parse HEAD` returned `a841fb3a3b538036cbe2a1058b15666ab5fa8064`. `git diff --stat 59f5f6c a841fb3`.
- `cat`/`sed`/`grep` reads of:
  - `PREREGISTRATION.md` (rev 4, in full);
  - `FABLE_REVIEW_59F5F6C.md`, `SOL_REVIEW_59F5F6C.md` and `ADJUDICATION_59F5F6C.md`;
  - `d18-proposal/PROPOSAL.md` O18-4;
  - `o6a-channel/SPEC.md` §1–§7;
  - Annex B §2.1–§2.2 and Annex A P18-7;
  - the `protocols/protocol_v1.yaml` partitions (the exploration partition is 2017-08-17 to 2021-12-31, about 1,598 days, so `T_C2` days plus warm-up fit);
  - a `grep` for "unequal" across the review records.
- `.venv\Scripts\python.exe -`, in memory, with numpy and standard-library code:
  - the AQTQ1 bytes and script length (39);
  - opposites Σ eigenvalues at `K` ∈ {2, 5, 20, 80}, with within-group ρ of 0 and 0.9;
  - the cell and test count (371 cells, `M` = 1,143);
  - exact-binomial and CP τ at `M` ∈ {1000, 1143} for `N` ∈ {20k, 40k}.
- No files were written, nothing was edited or committed, and no network was used. `data/` and the confirmation and lockbox data were not opened. Tests, lint and type checks are N/A because this is a review of a document only.

## For the owner

1. Revision 4 restores what you required in O18-4: two-strategy families, and a joint simulation of both families on the same Bitcoin days. It also gives the qualification fingerprint its own Bitcoin key for each attempt.
2. Two paper repairs remain. The "does my design fit a tested case" check must test against one tested case at a time, not against a blend of all of them. The fingerprint rules must say that anything that goes wrong after the result is seen counts as a failure, never as a free retry.
3. With those fixed, it is ready for your acceptance and your Q-1 decision. A measured pilot comes before the full run. Nothing has been built or run.
