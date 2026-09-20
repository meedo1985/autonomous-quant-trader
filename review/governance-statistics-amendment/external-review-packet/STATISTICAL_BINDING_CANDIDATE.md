# Statistical binding candidate — paired delta-Sharpe

**Status:** `UNSIGNED PROPOSAL — NO SCIENTIFIC OR GOVERNANCE APPROVAL`
**Companion to:** `README.md` (scope), `TECHNICAL_APPENDIX.md` (proofs),
`REVIEWER_DECISION_FORM.md` (response)

## 1. Authority and status of every input

Nothing below may be promoted in status because it is implemented, committed, or
independently reviewed by an AI.

| Item | Source | Authority | Status |
| --- | --- | --- | --- |
| Constitution v1.0 amendment rule, cycle rule, §16 protected components | `docs/RESEARCH_CONSTITUTION.md` §4, §5, §16 | Frozen, binding on owner, humans, AIs and software (§3) | Settled |
| Protocol v1.0 clause wording and thresholds | `protocols/protocol_v1.yaml` (`status: "FROZEN"`, `cycle_id: "C1"`) | Frozen | Settled |
| Daily-observation, Sharpe, influence, bootstrap and interval conventions | `review/task12/IMPLEMENTATION_CONVENTIONS.md` | Owner-approved for **inactive** implementation only (`review/task12/OWNER_DECISION.md`) | Accepted inactive implementation fact; not governance-active |
| `paired_sharpe_improvement`, `difference_series_sharpe` | `src/aqt/metrics/statistics.py` (`PairedSharpeStatistics`, lines 208–234) | Implementation of the above | Inactive; computes no governed result |
| C1 never started; DSR diagnostic-only; ETH stays at 1.0x | `review/governance-statistics-amendment/OWNER_DECISION.md` (2026-09-15) | Owner decision | Settled as owner choices; not scientific acceptance |
| Narrow DSR calibration deferred | `review/governance-statistics-amendment/OWNER_DSR_DEFER_DECISION.md` (2026-09-18) | Owner decision | Controlling; DSR gate unsatisfied, promotion blocked |
| Estimator semantics, versioned artifacts, PBO ranking, lockbox estimand | `DRAFT_AMENDMENT_PROPOSAL.md` | AI proposal | Unaccepted proposal |
| Joint-leg lockbox prediction `joint_daily_delta_sharpe_prediction.v1` | `LOCKBOX_PREDICTION_PROPOSAL.md` | AI proposal | Unaccepted proposal; conflicts with frozen wording (§5, row 12) |
| Conventional DSR candidate `aqt.dsr.iid_raw_count.proposal.v1` | `DSR_METHOD_PREREGISTRATION_DRAFT.md` | AI proposal | Unaccepted, uncalibrated, deferred |
| 148-cell calibration grid | `CALIBRATION_PREREGISTRATION_DRAFT.md` | AI proposal | Historical; explicitly **not executable** (DEC-01) |
| B1–B5 | `ASTRA_REVIEW.md` | Independent AI review finding | Open |
| DEC-01, DEC-02, DEC-03 | `DSR_CALIBRATION_RECONCILIATION.md` | Unsigned decision record | Open; human acceptance pending |
| Consumer audit and prior sign-off | `review/estimand-disambiguation/PAIRED_SHARPE_USAGE_RECORD.md`, `REVIEW_ADJUDICATION.md` | Unsigned proposal, reviewed by `gpt-6-astra` and `claude-fable-5-1` | Proposal; two non-blocking corrections applied |

## 2. Data model common to every estimand

- **Observation unit.** One complete UTC day comprising exactly 24 contiguous,
  non-overlapping accepted one-hour holding segments. Partial, missing,
  duplicated, irregular, non-finite, or misaligned days are rejected without
  repair (`IMPLEMENTATION_CONVENTIONS.md` §"Daily observations and Sharpe").
- **Leg return.** `r_t = day_close_equity_t / day_open_equity_t - 1`, dimensionless,
  computed for each leg **before** any subtraction. Candidate and benchmark paths
  must share symbol, cost multiplier, timestamps, and boundaries.
- **Comparison benchmark.** `VOL_TARGET_BUY_AND_HOLD`, the single predeclared
  comparator for every eligibility, robustness, DSR/PBO, null, and lockbox
  comparison (`protocol_v1.yaml:24–27`).
- **Risk-free rate.** Zero.
- **Variance.** Sample variance, denominator `n - 1`. Zero variance, fewer than
  two observations, or non-finite arithmetic yields *unavailable*; no epsilon
  floor, trimming, or rounding repair is permitted.
- **Annualization.** `A = sqrt(365)` applied to the daily Sharpe. Daily returns
  are never annualized before Sharpe.

## 3. Symbols, formulas, and units

| Symbol | Name | Formula | Input | Output unit |
| --- | --- | --- | --- | --- |
| `c`, `b` | Candidate and benchmark daily return legs | — | Aligned complete UTC days | Dimensionless |
| `d` | Paired difference series | `d_t = c_t - b_t` | Both legs | Dimensionless |
| `n` | Source length | Count of aligned valid daily pairs | — | Days |
| `m` | Lockbox target length | `(L1 - L0) / 24h` over a prebound half-open window | Calendar, bound before target read | Days |
| `S(x)` | Daily Sharpe | `mean(x) / sd(x)`, `sd` with denominator `n-1` | One series | Dimensionless |
| `Ŝ(x)` | Scaled daily Sharpe | `A * S(x)`, `A = sqrt(365)` | One series | Annualized-Sharpe units |
| **`E-IMPROV`** | **Paired Sharpe improvement** | `Ŝ(c) - Ŝ(b)` | **Both legs** | Annualized-Sharpe units |
| **`E-DIFF`** | **Paired difference-series Sharpe** | `Ŝ(c - b) = Ŝ(d)` | **Difference series only** | Annualized-Sharpe units |
| `T` | Daily observations per trial column | — | — | Days |
| `N_cycle`, `N_lifetime`, `K` | Counted current-cycle attempts, lifetime attempts, usable complete current-cycle vectors | — | — | Counts |
| `V` | Cross-trial Sharpe dispersion | `sum((S_j - mean(S))^2) / (K - 1)` | Trial Sharpes | Dimensionless |
| `DSR` | Deflated Sharpe score | Proposal only; see `DSR_METHOD_PREREGISTRATION_DRAFT.md` | Unannualized daily difference columns | Probability in `[0,1]` |
| `T_m` | Lockbox prediction statistic (proposal) | `sqrt(365) * (S(candidate) - S(benchmark))` over `m` days | **Both legs** over the target path | Annualized-Sharpe units |
| `phi` | PBO estimate | Logit-rank frequency over `12,870` oriented 8/8 splits of 16 blocks | Trial matrix + ranking metric | Fraction in `[0,1]` |

In code, `E-IMPROV` is `PairedSharpeStatistics.paired_sharpe_improvement` and
`E-DIFF` is the `.scaled` field of `PairedSharpeStatistics.difference_series_sharpe`
(`src/aqt/metrics/statistics.py:208–234`). Both are `None` when unavailable.

## 4. Consumers and producers

**Producers.** `E-IMPROV` requires both legs. `E-DIFF` requires only `d`, and is
therefore computable whenever `E-IMPROV` is, but not conversely.

**Consumers.** The frozen protocol requests a paired Sharpe-like statistic in
**thirteen** distinct clause groups. They are enumerated once, as rows 1–13 of the
canonical decision object in §5, and every count elsewhere in this packet refers
to those row numbers.

Of the thirteen, **two** (rows 1–2) name the paired *difference series*
explicitly, and the remaining **eleven** (rows 3–13) request the quantity the
protocol calls "paired delta-Sharpe". To keep the literal count auditable: eight
of those eleven rows contain the literal token `paired_delta_sharpe` or
"delta-Sharpe" in `protocols/protocol_v1.yaml` (rows 3, 4, 6, 8, 9, 10, 11, 12, at
lines 43, 78, 85, 91, 137, 140, 221, 240, 264, 279, 283), and three refer to the
same quantity without using that exact token (row 5 via
`btc_min_sharpe_delta_ci_lower_bound`, line 275; row 7 via `paired_fold_win_rate`,
lines 280–282; row 13 via the two delay hard gates, lines 284–285, which name no
statistic at all). No clause in either group defines an estimator.

**Interval versus point statistic.** `promotion.paired_confidence_interval`
requests a two-sided 90% interval; every other clause requests a point statistic, a
sign, a percentile of a path distribution, or a prediction quantile. These are not
interchangeable, and a binding for one does not bind another.

## 5. Canonical decision object — the thirteen consumer rows

This section is the single normative enumeration for this packet. Every count,
queue name, and status label used in `README.md`, `TECHNICAL_APPENDIX.md`, and
`REVIEWER_DECISION_FORM.md` resolves to a row number here. Where any other
sentence in the packet appears to conflict with this table, **this table
governs**.

**Status labels.** **Settled** = explicit frozen wording fixes the input.
**Interpretive** = frozen text is silent on the estimator; a statistician could
supply one without contradicting v1.0. **Amendment-required** = the requested
statistic is not computable from the frozen stored input, so any binding changes
frozen text. **Undefined** = the clause does not yet name a pass statistic at all.

**Queue assignment.** Rows 1–2 are **settled** and are not queued; they are
confirmed, not decided. The **eleven remaining rows, 3–13**, are partitioned into
three disjoint queues with no row in more than one:

- **Queue I — interpretive (rows 3, 4, 5, 6, 7; five rows).** A statistician may
  later supply an estimator without contradicting v1.0.
- **Queue II — amendment-required (rows 8, 9, 10; three rows).** A statistic is
  named but is not computable from the frozen stored input, so any binding
  changes frozen text and requires the Constitution §4 process.
- **Queue III — undefined (rows 11, 12, 13; three rows).** No pass statistic
  exists to bind, so choosing an estimand does not make the row evaluable.
  Queue III is kept separate from Queue II because it is *information first,
  then governance* (`README.md` §4.1, M4): a statistician must first name a pass
  statistic, and only the resulting text change is a §4 question. Collapsing
  Queue III into Queue II would misstate rows 11–13 as already having a statistic
  that merely cannot be computed.

Counts: `2 settled + 5 Queue I + 3 Queue II + 3 Queue III = 13`; remaining = 11.

| # | Queue | Consumer | Frozen clause (`protocols/protocol_v1.yaml`) | Stored / available input | Statistic requested | Status |
| ---: | :---: | --- | --- | --- | --- | --- |
| 1 | — | DSR input series | `validation.dsr.series` (227–231): "BTC candidate_minus_VOL_TARGET_BUY_AND_HOLD paired OOS return series" | `d` | Score over `d` | **Settled** — difference series. Substituting `E-IMPROV` needs a §4 amendment |
| 2 | — | OOS/IS in-sample definition | `validation.oos_is_ratio.in_sample_definition` (245–248): "training-window Sharpe of the same fixed configuration on the paired-difference series" | `d` | `E-DIFF`-style series Sharpe | **Settled** — difference series; full ratio unimplemented |
| 3 | I | ETH sanity gate | `asset_evaluation.eth_gate` (42–44) and `promotion.eth_sanity_rule` (279): `paired_delta_sharpe_point_estimate > 0` at 1.0x cost | Both legs available at evaluation time | Point statistic, sign | **Interpretive**; ETH 1.0x itself settled (owner, 2026-09-15). Sign flips between estimands — Example B |
| 4 | I | BTC 2x cost stress | `promotion.survive_2x_cost_rule` (283) | Both legs | Point statistic, sign | **Interpretive**; same sign hazard as #3 |
| 5 | I | Paired CI and BTC CI lower bound | `promotion.paired_confidence_interval` (274), `btc_min_sharpe_delta_ci_lower_bound` (275) | Both legs; Task 12 resamples both legs jointly | Two-sided 90% interval, lower endpoint `> 0` strictly | **Interpretive**; the only consumer with an existing inactive estimator, which targets `E-IMPROV` |
| 6 | I | Parameter plateau | `validation.plateau.pass_rule` (263–265): median available-neighbour BTC OOS paired-delta-Sharpe `>= 0.5 *` selected value | Both legs per grid point | Point statistic, ratio comparison | **Interpretive**; the `0.5 *` ratio is scale-sensitive and sign-sensitive, so the estimand materially changes the rule |
| 7 | I | Three-month fold wins | `promotion.paired_fold_win_rate` (280–282), `validation.final_partial_reporting_block` (202–204) | Both legs per complete 3-month block | Point statistic per fold, fraction `>= 0.60` | **Interpretive**, and additionally blocked on fold anchoring, UTC completeness, and minimum days (M5) |
| 8 | II | PBO | `validation.pbo.series_matrix` (237–239) stores a "family trial paired-difference return matrix"; `validation.pbo.ranking_metric` (240) says `paired_delta_sharpe` | Difference matrix only | Ranking metric over trials | **Amendment-required** — the matrix cannot reconstruct `E-IMPROV` (Example A) and the two estimands rank trials oppositely (Example C) |
| 9 | II | Lockbox prediction and pass rule | `lockbox_policy.prediction_interval.construction` (83–86): bootstrap "the confirmation BTC paired-difference series … compute delta-Sharpe per path"; `pass_rule` (90–91) | Difference series per frozen text; both legs per proposal | 5th-percentile prediction quantile plus realized statistic | **Amendment-required** — internally incompatible; a difference path cannot yield a difference of two Sharpes (Astra B4; Example A) |
| 10 | II | Lockbox coarse attestation | `lockbox_policy.attestation_coarse_fields` (77–78): `paired_delta_sharpe_sign` | Whatever #9 produces | Sign only | **Amendment-required**, dependent on #9; a sign from a different statistic may not be substituted (Example B) |
| 11 | III | CPCV diagnostic paths | `validation.cpcv.role` (219–221): median and 5th-percentile path paired-delta-Sharpe | Both legs per path, if implemented | Path point statistics | **Undefined**; diagnostic-only under v1.0, so no promotion consequence today |
| 12 | III | Random-exposure null | `benchmarks.null_models.random_exposure` (134–140): 500 samples, `gate_metric: paired_delta_sharpe_vs_VOL_TARGET_BUY_AND_HOLD`, passing at the 0.95 percentile (`promotion.null_minimum_percentile`, 289) | Both legs per null draw | Percentile event over a null distribution | **Undefined**; the nominated statistic and the exact percentile event are unspecified |
| 13 | III | Feature and execution delay gates | `promotion.feature_delay_hard_gate` (284), `execution_delay_hard_gate` (285), stress bars at 267–268 | Both legs under the stressed configuration | Unspecified | **Undefined**; mandatory gates with no pass statistic named |

Rows 11–13 (Queue III) are *undefined* rather than merely unbound: choosing an
estimand for them does not make them evaluable, because no pass statistic exists
to bind. This is why they are not in Queue II — Queue II rows name a statistic
that the frozen input cannot produce, whereas Queue III rows name none.

## 6. Invariants any accepted binding must preserve

1. `E-IMPROV` and `E-DIFF` remain separately named quantities. Neither is a
   permitted silent substitute for the other.
2. Frozen v1.0 DSR consumes the candidate-minus-comparison return series.
3. No estimand binding by itself resolves the DSR effective trial count, the
   selection or error event, finite-sample behaviour, calibration, or the 0.95
   gate (B1–B3, DEC-02).
4. PBO requires an explicit joint input/ranking contract; the frozen difference
   matrix alone cannot reconstruct `E-IMPROV`.
5. Lockbox use must separately fix source representation, joint-leg resampling,
   prediction length `m` versus source length `n`, the statistic, coverage, the
   information boundary, and the pass rule (B4).
6. Prior-cycle return matrices are never pooled into current-cycle DSR or PBO
   matrices; lifetime trial counts persist (Constitution §5).
7. Unavailable mandatory statistics produce `INDETERMINATE`/`BLOCKED`, never
   `PASS`. `NO_EDGE_FOUND` and `KEEP_BLOCKED` are valid outcomes.
8. Frozen thresholds are untouched by any binding: 2,000 bootstrap attempts, 90%
   paired interval, DSR `>= 0.95`, PBO `<= 0.30`, PBO activation at 20 trials, 16
   partitions, ESS `>= 120`, CPCV at 250 effective decisions, fold-win fraction
   `>= 0.60`, null percentile 0.95, 81 trials per family, ETH at 1.0x, BTC stress
   at 2.0x, exposure in `[0,1]`.
9. An interval, a point estimate, a percentile of a path distribution, and a
   prediction quantile remain distinct objects with distinct interpretations.

## 7. Route comparison

| | R-A: bind `E-IMPROV` universally | R-B: bind `E-DIFF` universally | R-C: clause-specific split | R-D: `KEEP_BLOCKED` (recommended) |
| --- | --- | --- | --- | --- |
| **Scientific assumption** | "Delta-Sharpe" means a difference of two Sharpe ratios everywhere; both legs always retained | "Paired" means the matched difference series everywhere; one series suffices | Each clause's estimand follows from its own stored input and stated purpose | No assumption; the ambiguity is recorded, not resolved |
| **Information required** | Both legs stored for every consumer, including the PBO matrix and the lockbox source | Acceptance that gate #5's existing inactive estimator targets the wrong quantity | M1, M2, M3, M4, M5 (`README.md` §4.1) | None beyond this packet |
| **Works under frozen wording?** | **No.** Contradicts `validation.dsr.series`, `oos_is_ratio.in_sample_definition`, `pbo.series_matrix`, and `lockbox_policy.prediction_interval.construction` | **No.** Contradicts the natural reading of "delta-Sharpe" in `lockbox_policy.pass_rule` and changes the outcome of rows 3, 4 and 6 on admissible data by inverting the sign of the point statistic they test (`TECHNICAL_APPENDIX.md` §3, affected-clause list) | **Partly.** Queue I (rows 3–7) yes; Queue II (rows 8–10) and Queue III (rows 11–13) no | **Yes.** Changes nothing |
| **Governance impact** | Amendment to at least four frozen clauses; new cycle C2 and protocol 1.1 | Amendment; also discards the only implemented inactive estimator | Amendment for Queue II (rows 8–10) and, after a pass statistic is named, Queue III (rows 11–13); Queue I (rows 3–7) is interpretive | None |
| **Falsifying evidence** | Example A (`E-IMPROV` not identified from the frozen PBO/DSR/lockbox input) | Examples B and C (sign and rank reversal versus the improvement reading) | A demonstration that any Queue I clause is in fact input-constrained, or that a Queue II clause is satisfiable without changing frozen text, or that a Queue III clause already names a pass statistic | A demonstration that some single estimand satisfies all thirteen rows of §5 simultaneously |
| **Closes B1–B5?** | No | No | No | No |

R-A and R-B are both refuted by the appendix: neither survives the frozen text.
R-C is the only route to an eventually evaluable protocol, but it cannot be
*adopted* by a reviewer. Stated against the canonical object in §5: of the
thirteen rows, two (1–2) are already settled and five (3–7, Queue I) are
interpretive and so lie within a statistician's reach, while **six** lie outside
it — rows 8–10 (Queue II) require the Constitution §4 process to bind, and rows
11–13 (Queue III) name no pass statistic to bind at all and require information
first and then §4. R-D is therefore the correct present verdict, with the
§4-compliant four-step decision in `README.md` §4 as the narrowest next step.

## 8. Explicitly prohibited next acts

Neither this document nor any reviewer response to it authorizes: authoring,
merging, activating, or self-approving an amendment; starting cycle C2; running a
governed trial; implementing a DSR calibration engine or any simulation;
confirmation-partition or lockbox data access; an eligibility decision; promotion;
deployment; trading; Task 13; or modification of any frozen artifact, sidecar,
`FROZEN_HASHES.json` entry, or existing review record. Constitution §16 requires
different-model **and** human PR review before any later validation-engine,
promotion-gate, governor, executor, lockbox-ACL, or protocol-enforcement code is
merged; an AI review does not satisfy either requirement.
