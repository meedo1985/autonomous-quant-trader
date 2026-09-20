# Technical appendix — deterministic worked examples

**Status:** `REVIEW EVIDENCE ONLY — NOT AN ACCEPTED NUMERICAL REFERENCE`
**Companion to:** `STATISTICAL_BINDING_CANDIDATE.md`

## 0. Method, scope, and verification status

Every example below is a closed-form derivation over exact rational inputs. The
return vectors are synthetic four- and three-day sequences chosen to make the
arithmetic checkable by hand; they are **not** market data, not calibration
evidence, not coverage evidence, and not a test suite. They establish
*qualitative* facts — non-identifiability, sign disagreement, rank reversal,
selection-event non-equivalence — which are invariant to the particular numbers.

Conventions are those of `review/task12/IMPLEMENTATION_CONVENTIONS.md`: complete
UTC-day observations, each leg compounded before subtraction, zero risk-free rate,
sample variance with denominator `n - 1`, and `A = sqrt(365)`.

**Verification status, stated plainly.** These derivations were produced
analytically while preparing this packet; no code was executed in the preparing
session, so they carry **no** independent machine verification of their own.
Exact values are given in closed form precisely so a reviewer can confirm each in
one line of exact arithmetic. The one previously published example (§6) *was*
independently reproduced by two models and is cited, not recomputed.

Decimal values are descriptive and rounded; the exact radical expressions are the
claims. No decimal below is a frozen tolerance.

Reference constants: `sqrt(3) = 1.7320508076`, `sqrt(365) = 19.1049731745`,
`sqrt(1095) = sqrt(365)*sqrt(3) = 33.0907842682`.

## 1. The four quantities, kept separate

These are four different objects. The appendix treats each only where it applies,
and the examples below show that conflating any two of them changes results.

| Quantity | What it is | Input it consumes | Output | Frozen consumer | Status |
| --- | --- | --- | --- | --- | --- |
| **`E-IMPROV`** — paired Sharpe improvement | Difference of two annualized Sharpe ratios, `Ŝ(c) - Ŝ(b)` | **Both** daily legs | Annualized-Sharpe units, any sign | None settled; the Task 12 interval targets it | Implemented but inactive |
| **`E-DIFF`** — paired difference-series Sharpe | Annualized Sharpe of the single series `c - b` | The difference series `d` only | Annualized-Sharpe units, any sign | `validation.dsr.series`, `validation.oos_is_ratio.in_sample_definition` | Input settled by frozen text |
| **DSR** — deflated Sharpe score | A selection-corrected probability-scaled score over one *unannualized* daily difference column, given trial counts and cross-trial Sharpe dispersion | Difference columns, counts `N_cycle`/`N_lifetime`/`K`, dispersion `V` | Score in `[0,1]`, gated at `>= 0.95` | `validation.dsr` | No accepted equation; diagnostic-only; deferred |
| **PBO** — probability of backtest overfitting | Frequency, over `12,870` oriented 8/8 splits of 16 chronological blocks, that the IS-best trial lands in the lower half of the OOS ranking | A **trial × time matrix** plus a **ranking metric** | Fraction in `[0,1]`, gated at `<= 0.30` | `validation.pbo` | Input settled, ranking metric unresolved |

DSR and PBO are *not* estimands of the same kind as `E-IMPROV` and `E-DIFF`: they
are procedures that consume a Sharpe-like statistic and a selection structure.
A binding of "paired delta-Sharpe" therefore does not define DSR or PBO; it only
fixes one of their inputs.

## 2. Example A — `E-IMPROV` is not identifiable from the difference series

**Claim.** Two admissible leg pairs can share an identical difference series `d`
— and even identical benchmark Sharpe ratios — while their `E-IMPROV` values
differ by a factor of `sqrt(5)`.

Let `d = (0.01, 0.03, 0.01, 0.03)` in both pairs.

| | Pair 1 | Pair 2 |
| --- | --- | --- |
| Benchmark `b` | `(0.02, -0.02, 0.02, -0.02)` | `(0.02, 0.02, -0.02, -0.02)` |
| Candidate `c = b + d` | `(0.03, 0.01, 0.03, 0.01)` | `(0.03, 0.05, -0.01, 0.01)` |

Benchmarks are permutations of one another; both have mean `0`, hence
`Ŝ(b) = 0` in both pairs.

Pair 1: `mean(c) = 0.02`; deviations `(±0.01)`; `s^2 = 0.0004/3`;
`S(c) = sqrt(3)`; `E-IMPROV_1 = sqrt(365)*sqrt(3) = sqrt(1095) ≈ 33.0907842682`.

Pair 2: `mean(c) = 0.02`; deviations `(0.01, 0.03, -0.03, -0.01)`;
`sum = 0.002`; `s^2 = 0.002/3`; `S(c)^2 = 0.0004*3/0.002 = 0.6`, so
`S(c) = sqrt(0.6)`; `E-IMPROV_2 = sqrt(365)*sqrt(0.6) = sqrt(219) ≈ 14.7986486`.

The shared difference series has `mean(d) = 0.02`, deviations `(±0.01)`,
`s^2 = 0.0004/3`, `S(d) = sqrt(3)`, hence in **both** pairs
`E-DIFF = sqrt(1095) ≈ 33.0907842682`.

`E-IMPROV_1 / E-IMPROV_2 = sqrt(1095)/sqrt(219) = sqrt(5) ≈ 2.2360679775`.

**Consequence.** Any frozen clause whose stored input is a difference series —
`validation.pbo.series_matrix`, `validation.dsr.series`,
`lockbox_policy.prediction_interval.construction` — cannot produce `E-IMPROV`.
This is an identifiability failure, not a precision issue: no estimator, and no
amount of data, recovers `E-IMPROV` from `d` alone.

### 2.1 Example A2 — the converse also fails

`E-DIFF` is likewise not a function of the two leg Sharpes. Keep
`b = (0.02, -0.02, 0.02, -0.02)` and take `c = (0.01, 0.03, 0.01, 0.03)`. Then
`mean(c) = 0.02`, deviations `(±0.01)`, so `S(c) = sqrt(3)` and `Ŝ(b) = 0` —
identical leg Sharpes to Pair 1 above. But
`d = c - b = (-0.01, 0.05, -0.01, 0.05)`, with `mean(d) = 0.02`, deviations
`(±0.03)`, `s^2 = 0.0036/3 = 0.0012`, giving `S(d) = 1/sqrt(3)` and
`E-DIFF = sqrt(365/3) ≈ 11.0302614` — against `sqrt(1095) ≈ 33.0907842682` for
Pair 1.

The two estimands are mutually non-identifiable. Neither can serve as a proxy for
the other, in either direction.

## 3. Example B — the two estimands disagree in sign

**Claim.** On admissible daily data, `E-IMPROV` can be strongly positive while
`E-DIFF` is negative. A gate phrased as `paired_delta_sharpe_point_estimate > 0`
therefore *passes* under one binding and *fails* under the other, on the same
returns.

```text
b = ( 0.20, -0.10,  0.20, -0.10)     benchmark
c = ( 0.04,  0.04,  0.05,  0.05)     candidate
d = (-0.16,  0.14, -0.15,  0.15)     difference
```

- `mean(b) = 0.05`; deviations `(±0.15)`; `s^2 = 0.09/3 = 0.03`;
  `S(b) = 0.05/(0.1*sqrt(3)) = sqrt(3)/6 ≈ 0.2886751346`.
- `mean(c) = 0.045`; deviations `(±0.005)`; `s^2 = 0.0001/3`;
  `S(c) = 4.5*sqrt(3) ≈ 7.7942286341`.
- `E-IMPROV = sqrt(365)*sqrt(3)*(4.5 - 1/6) = (13/3)*sqrt(1095) ≈ +143.3933985`.
- `mean(d) = -0.005`; deviations `(-0.155, 0.145, -0.145, 0.155)`;
  `sum = 0.0901`; `s^2 = 0.0901/3`;
  `S(d)^2 = 0.000025*3/0.0901 = 3/3604`, so `S(d) = -sqrt(3/3604)`.
- `E-DIFF = -sqrt(1095/3604) ≈ -0.5512070`.

The mechanism is general: `mean(d) = mean(c) - mean(b)` can be negative while
`mean(c)/sd(c) > mean(b)/sd(b)`, because a candidate that gives up a little mean
return for a large reduction in volatility improves its Sharpe ratio while
under-performing the benchmark on average. That is exactly the "de-risker" profile
the protocol's own `lockbox_policy.net_return_tolerance_rule` justification
(`protocols/protocol_v1.yaml:93–95`) anticipates, so the case is not pathological
for this project.

**Affected clauses.** `asset_evaluation.eth_gate` (line 43),
`promotion.eth_sanity_rule` (279), `promotion.survive_2x_cost_rule` (283),
`lockbox_policy.pass_rule` (91) via `BTC delta-Sharpe > 0`,
`lockbox_policy.attestation_coarse_fields.paired_delta_sharpe_sign` (78), and
`promotion.btc_min_sharpe_delta_ci_lower_bound` (275), whose lower endpoint must be
strictly positive, and `validation.plateau.pass_rule` (263–265). The binding
choice materially changes the test for all of them, and the outcome for the
sign-tested clauses. For `validation.plateau.pass_rule` the demonstrated effect
is a material change of test and of the direction of the requirement imposed; no
outcome reversal is demonstrated for it here, because the example supplies no
neighbour values against which the rule could be evaluated.

`validation.plateau.pass_rule` is included on the same evidence, and is listed
here explicitly so that the claim in `STATISTICAL_BINDING_CANDIDATE.md` §7 (route
R-B changes the outcome of rows 3, 4 and 6) is supported rather than asserted.
Its test is `median available-neighbour value >= 0.5 * selected-point value`,
which is not sign-invariant: applied to the returns above, the selected point's
value is `+143.39` under `E-IMPROV` and `-0.55` under `E-DIFF`. For a positive
selected value the rule demands that neighbours retain at least half of a
positive quantity; for a negative one, `0.5 * v > v`, so the rule instead demands
that neighbours be *better* than the selected point by at least half its
magnitude. The estimand choice therefore changes both the threshold's sign and
the direction of the requirement it imposes, on the same grid.

## 4. Example C — PBO trial ranking reverses completely

**Claim.** With a shared benchmark and two trials, ranking by `E-IMPROV` and
ranking by `E-DIFF` give opposite orders.

Common benchmark `b = (0.20, -0.10, 0.20, -0.10)`, `S(b) = sqrt(3)/6`.

| | Trial 1 | Trial 2 |
| --- | --- | --- |
| Candidate `c_j` | `(0.04, 0.04, 0.05, 0.05)` | `(0.22, -0.09, 0.22, -0.09)` |
| Difference `d_j` | `(-0.16, 0.14, -0.15, 0.15)` | `(0.02, 0.01, 0.02, 0.01)` |
| `S(c_j)` | `4.5*sqrt(3) ≈ 7.7942286` | `(13/62)*sqrt(3) ≈ 0.3631720` |
| **`E-IMPROV_j`** | `(13/3)*sqrt(1095) ≈ +143.3933985` | `(4/93)*sqrt(1095) ≈ +1.4232595` |
| **`E-DIFF_j`** | `-sqrt(1095/3604) ≈ -0.5512070` | `1.5*sqrt(1095) ≈ +49.6361764` |

Ranking by improvement: Trial 1 > Trial 2. Ranking by difference-series Sharpe:
Trial 2 > Trial 1. The reversal is total, with only two trials, on a shared
benchmark and complete aligned data.

**Consequence for `validation.pbo`.** `series_matrix` (237–239) stores the
difference matrix `{d_j}` and `ranking_metric` (240) says `paired_delta_sharpe`.
By Example A the stored matrix cannot yield `E-IMPROV`; by this example, reading
the ranking metric as `E-DIFF` instead is not a harmless default, because it
selects a different IS-best trial and therefore a different `phi`. The mismatch
must be resolved explicitly, and resolving it in favour of `E-IMPROV` requires
storing both legs — a change to a frozen input, hence a Constitution §4 question.

## 5. Example D — maximum difference-Sharpe is not maximum DSR

**Claim.** Under the *proposed* conventional DSR candidate
`aqt.dsr.iid_raw_count.proposal.v1` (`DSR_METHOD_PREREGISTRATION_DRAFT.md`), the
trial with the largest difference-series Sharpe need not have the largest DSR
score. The two error events in DEC-02 are therefore not interchangeable, even in a
complete two-trial family.

This example is conditional on that unaccepted candidate equation; it
demonstrates a property of the candidate, not a calibrated result.

Candidate score, for a column with sample Sharpe `S`, population skewness `g`,
Pearson kurtosis `k`, and `T` observations:

```text
D     = 1 - g*S + ((k-1)/4)*S^2
score = Phi( (S - S0) * sqrt(T-1) / sqrt(D) ),   S0 = sqrt(V) * A(N)
```

Two difference columns, `T = 4`, `N_cycle = N_lifetime = K = 2`:

| | Column X | Column Y |
| --- | --- | --- |
| Daily difference returns | `(-0.02, 0.00, 0.02, 0.04)` | `(-0.0111, -0.0111, 0.0289, 0.0289)` |
| Mean | `0.01` | `0.0089` |
| Centred values | `(-0.03, -0.01, 0.01, 0.03)` | `(-0.02, -0.02, 0.02, 0.02)` |
| Sample variance (`T-1`) | `1/1500` | `0.0016/3` |
| **Sharpe `S`** | `sqrt(3/20) ≈ 0.3872983346` | `(89/400)*sqrt(3) ≈ 0.3853813047` |
| Population `mu_2` | `0.0005` | `0.0004` |
| Skewness `g` | `0` | `0` |
| Pearson kurtosis `k` | `41/25 = 1.64` | `1` |
| **`D`** | `1 + 0.16*0.15 = 1.024` | `1` |

Selection by the candidate's own rule — greatest difference-series Sharpe —
picks **X**, since `0.3872983 > 0.3853813`.

Because `T` and `S0` are shared, `score_Y > score_X` is equivalent to

```text
sqrt(1.024) * (S_Y - S0)  >  (S_X - S0)
```

With `sqrt(1.024) = 1.0119288512`:

```text
sqrt(1.024)*S_Y - S_X = 0.3899784 - 0.3872983 = 0.0026801
S0 * (sqrt(1.024) - 1) = S0 * 0.0119288512
```

so the inequality holds for **every** `S0 < 0.0026801/0.0119288512 ≈ 0.2246724`.
The actual `S0` is far smaller: with `K = 2` the two Sharpe deviations from their
mean are `±(S_X - S_Y)/2`, so
`V = sum((S_j - mean(S))^2)/(K-1) = (S_X - S_Y)^2/2 ≈ 1.8375e-6` and
`sqrt(V) ≈ 0.0013555`. Since
`A(N)` is the two-term expected-maximum expression
`(1 - gamma) * Phi^-1(1 - 1/N) + gamma * Phi^-1(1 - 1/(N*e))`, whose **first term
vanishes at `N = 2`** because `Phi^-1(1 - 1/2) = Phi^-1(0.5) = 0`, leaving
`A(2) = gamma * Phi^-1(1 - 1/(2e)) ≈ 0.5772157 * 0.9004 ≈ 0.5198 < 1`, we have
`S0 ≈ 0.0007046`, four
orders of magnitude below the threshold. The conclusion is insensitive to any
reasonable error in `A(2)`.

Descriptive scores: `score_X ≈ 0.7459`, `score_Y ≈ 0.7474`. Y scores higher
although X was selected.

**Consequence.** "The selected trial clears 0.95" and "some null trial clears
0.95" are different events with different probabilities, so a calibration designed
around one does not bound the other (DEC-02). Neither score here approaches 0.95,
so the example demonstrates event non-equivalence only; it makes no claim about
error rates, and it is not evidence that any DSR method is or is not calibrated.
B1–B3 remain open and the owner's DEFER decision is untouched.

## 6. Previously published example, cited not recomputed

`review/estimand-disambiguation/PAIRED_SHARPE_USAGE_RECORD.md` records, for
`c = (0.01, 0.02, 0.04)` and `b = (0, 0.015, 0.025)`:

```text
E-IMPROV ≈ 8.939204453714432
E-DIFF   ≈ 38.209946349085600
```

`review/estimand-disambiguation/REVIEW_ADJUDICATION.md` records that `gpt-6-astra`
independently re-derived both values from rational moments and that a second
independent model review passed. That example shows non-equivalence; Examples A
through D above add non-identifiability in both directions, sign disagreement,
rank reversal, and selection-event non-equivalence.

## 7. Lockbox: the frozen construction cannot produce the proposed statistic

No new arithmetic is required; Example A settles it.

`lockbox_policy.prediction_interval.construction`
(`protocols/protocol_v1.yaml:83–86`) specifies: stationary-bootstrap **the
confirmation BTC paired-difference series**, generate synthetic paths, and
**compute delta-Sharpe per path**. Each bootstrap path is therefore a sequence of
difference returns. By Example A, such a path admits `E-DIFF` and does not
determine `E-IMPROV`. If "delta-Sharpe" in that clause means a difference of two
Sharpe ratios, the clause is unsatisfiable as written; if it means `E-DIFF`, then
`LOCKBOX_PREDICTION_PROPOSAL.md`'s `T_m = sqrt(365)*(S(candidate) - S(benchmark))`
is a different statistic and cannot be adopted without amending the clause. This
is Astra finding B4, restated with a proof rather than an assertion.

Three further mismatches in the same clause are independent of the estimand
question and are listed once here:

1. **Path length.** The frozen text sets path length by "decision-count equal to
   the lockbox BTC decision-count", while every Sharpe convention in the project
   is defined over complete UTC days. `LOCKBOX_PREDICTION_PROPOSAL.md` instead
   binds a calendar target length `m = (L1 - L0)/24h` before any target read.
   Decision count, hourly-bar count, trade count, and complete-day count are four
   different numbers.
2. **Source versus target length.** The inactive Task 12 index generator fixes
   output length equal to source length, so it cannot draw `m` indices from `n`
   source positions when `m != n`; its stream purpose is also fixed to
   `paired_sharpe_ci`. Any implementation therefore requires the reviewed
   migration of Astra finding B5, including refreshed deterministic reference
   vectors, because a changed stream binding changes every bootstrap sample.
3. **Joint resampling.** Computing `T_m` requires applying one index sequence to
   both legs. The frozen text resamples a single difference series, from which
   two legs cannot be recovered.

## 8. What these examples do not show

They do not establish that either estimand is the scientifically preferable target
for any gate; that is the judgement this packet requests. They supply no coverage,
calibration, power, or finite-sample evidence. They do not resolve the DSR
effective trial count, the 0.95 gate, PBO's ranking contract, or the lockbox
specification. They involve no market, confirmation, or lockbox data, and no
random sampling. A matching arithmetic example is not calibration evidence.
