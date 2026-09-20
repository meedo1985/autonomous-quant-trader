# Paired Sharpe estimands: existing definitions, consumer requirements, and unresolved governance bindings

**Decision ID:** `OD-EST-001`
**Status:** `UNSIGNED PROPOSAL — NO SCIENTIFIC OR GOVERNANCE APPROVAL`
**Date:** 2026-09-19

## Authority and boundary

This record is blocked-proposal preparation authorized by
`review/governance-statistics-amendment/OWNER_DECISION.md`. It does not amend or
reinterpret the frozen v1.0 protocol. The later owner decision in
`OWNER_DSR_DEFER_DECISION.md` remains controlling: DSR is diagnostic-only, its
mandatory 0.95 promotion gate is unsatisfied, and no calibration engine,
simulation, Task 13, governed trial, confirmation or lockbox access, promotion,
deployment, or trading is authorized.

The definitions below already exist in inactive Task 12 evidence and code. The
open issue is the governed binding for each consumer, not the mathematics of the
two definitions.

## Existing estimands

For aligned complete UTC-day candidate returns `c` and benchmark returns `b`,
using zero risk-free return, sample standard deviation, and `A = sqrt(365)`:

```text
E-IMPROV = A * Sharpe_daily(c) - A * Sharpe_daily(b)
E-DIFF   = A * Sharpe_daily(c - b)
```

`E-IMPROV` is named `paired_sharpe_improvement`; `E-DIFF` is the `.scaled`
value of `difference_series_sharpe` in `src/aqt/metrics/statistics.py`. The accepted
inactive conventions are recorded in `review/task12/IMPLEMENTATION_CONVENTIONS.md`.
Neither quantity can generally be reconstructed from the other, and a
difference-return series alone cannot reconstruct `E-IMPROV`.

Illustration only: for three daily observations
`c=(0.01, 0.02, 0.04)` and `b=(0, 0.015, 0.025)`, the existing convention gives
`E-IMPROV ~= 8.9392044537` and `E-DIFF ~= 38.2099463491`. This deterministic
example demonstrates non-equivalence; it is not an accepted numerical reference,
calibration result, or evidence for either estimand's governed use.

## Consumer and input audit

Status labels mean:

- **Settled:** explicit frozen wording or accepted inactive implementation fact.
- **Proposed:** present in review material but not accepted or active governance.
- **Unresolved:** requires a qualified human/statistician decision or a formal
  amendment path; this record assigns no default.

| Consumer | Frozen v1.0 wording or requirement | Existing inactive implementation or proposal | Required input / current status |
| --- | --- | --- | --- |
| Paired 90% interval and BTC CI lower-bound gate | `promotion.paired_confidence_interval` and `btc_min_sharpe_delta_ci_lower_bound` name a paired interval/delta without an estimator definition. | Task 12 jointly resamples both legs and computes an interval for `E-IMPROV`. | **Proposed/unresolved:** governed binding of the interval to `E-IMPROV`; interval interpretation remains R2. |
| Three-month fold wins | `promotion.paired_fold_win_rate` fixes complete three-month reporting blocks and a 0.60 minimum. | `DRAFT_AMENDMENT_PROPOSAL.md` proposes strict positive paired improvement. No fold implementation exists. | **Unresolved:** estimand, anchoring, UTC completeness, and minimum days; R4 blocks fold work. |
| ETH sanity gate | `asset_evaluation.eth_gate` and `promotion.eth_sanity_rule` require `paired_delta_sharpe_point_estimate > 0` at 1x cost. | The amendment proposal uses positive paired improvement and preserves 1x. | **Proposed/unresolved:** `E-IMPROV` binding; ETH 1x itself is settled. |
| BTC 2x cost stress | `promotion.survive_2x_cost_rule` requires positive BTC `paired_delta_sharpe_point_estimate`. | The amendment proposal interprets this as positive paired improvement. | **Proposed/unresolved:** `E-IMPROV` binding. |
| Feature and execution delay stress | `promotion.feature_delay_hard_gate` and `execution_delay_hard_gate` are mandatory, but the frozen lines do not bind a Sharpe estimand. | No governed consumer binding exists. | **Unresolved:** exact pass statistic and relation to either estimand; no default is inferred. |
| Parameter plateau | `validation.plateau.pass_rule` compares neighbor and selected `paired-delta-Sharpe`. | The amendment proposal states paired improvement for gates generally but supplies no accepted binding. | **Unresolved:** likely consumer of a point statistic, but neither estimand is selected here. |
| Random-exposure null | `benchmarks.null_models.random_exposure` evaluates paired delta-Sharpe versus the comparison benchmark. | No accepted implementation exists. | **Unresolved:** null construction, nominated statistic, percentile event, and estimand. |
| CPCV diagnostic paths | `validation.cpcv.role` requires median and 5th-percentile path `paired-delta-Sharpe`. | No accepted implementation or binding exists. | **Unresolved:** path statistic and estimand. CPCV remains diagnostic-only under frozen v1.0. |
| DSR | `validation.dsr.series` explicitly requires the BTC candidate-minus-comparison paired OOS return series. | The amendment and calibration drafts preserve unannualized daily difference returns as DSR input. | **Settled input:** difference series. A complete DSR equation, selection correction, calibration, and governed score remain unresolved; this is not permission to substitute `E-IMPROV`. |
| PBO | `validation.pbo.series_matrix` requires a family trial paired-difference return matrix, while `ranking_metric` says `paired_delta_sharpe`. | The amendment proposal suggests ranking by paired Sharpe improvement. | **Input settled, ranking unresolved:** the matrix alone cannot reconstruct `E-IMPROV`; an accepted consumer contract must resolve the mismatch without silently replacing either frozen clause. |
| OOS/IS ratio | `validation.oos_is_ratio.in_sample_definition` explicitly uses training-window Sharpe of the paired-difference series. | No active implementation exists. | **Settled input:** `E-DIFF`-style series Sharpe for the in-sample definition; the full governed ratio remains unimplemented. |
| Lockbox prediction and pass rule | Frozen construction says bootstrap the confirmation paired-difference series and compute delta-Sharpe per path; the pass rule compares lockbox delta-Sharpe with the prediction distribution and zero. | `LOCKBOX_PREDICTION_PROPOSAL.md` instead preserves both legs and defines `T_m = E-IMPROV`. | **Unresolved conflict:** source representation, statistic, joint resampling, target length, coverage, identity boundary, and acceptance all remain open; B4 is not closed. |
| Lockbox coarse attestation | `lockbox_policy.attestation_coarse_fields` includes `paired_delta_sharpe_sign`. | No accepted binding exists. | **Unresolved:** must follow the accepted lockbox estimand and may not be inferred from a different statistic. |

## Consequences and dependencies

There is no scientifically valid universal substitution:

- DSR and the OOS/IS definition deliberately name a difference-return series.
- `E-IMPROV` requires both legs and is the implemented Task 12 interval statistic.
- PBO currently names both a difference-series input matrix and an ambiguous
  ranking metric.
- The lockbox proposal's `E-IMPROV` cannot be recovered from the frozen phrase
  "paired-difference series."

This audit does **not** resolve `DSR_CALIBRATION_RECONCILIATION.md` DEC-02. The
selected-trial event versus any-null-trial event, global versus composite null,
and maximum Sharpe versus maximum DSR remain separate selection and error-event
questions.

It closes none of Astra findings B1-B5. In particular, B4 also requires accepted
joint resampling, prediction length, coverage, identity boundaries, and lockbox
semantics. B5 still requires a human-authored final specification and reviewed
code/hash migration.

## Next permitted decision

A qualified human/statistician may later review this audit and choose one of:

1. accept clause-specific bindings while preserving the explicit DSR and OOS/IS
   difference-series inputs;
2. request a revised, source-linked binding proposal; or
3. retain the current pause.

Any proposed change to frozen wording, thresholds, or required inputs is a
separate amendment question. Owner trust in an AI review and ordinary owner PR
acceptance do not establish statistician qualifications. Constitution section
16 does not itself require a paid reviewer or a public repository, but its human
and different-model review requirements still apply to later protected code.

```text
Decision: ACCEPT BINDING PROPOSAL / REVISE / RETAIN PAUSE
DSR difference-series input preserved: YES (required; NO is out of scope and requires a formal amendment)
PBO input and ranking contract accepted: YES / NO
Interval and gate estimands accepted: YES / NO
Lockbox estimand and remaining B4 work acknowledged: YES / NO
Qualified reviewer name and basis:
Owner-of-record name/signature:
Date/time UTC:
Commit:
```

All fields remain intentionally blank. This record authorizes no implementation,
simulation, data access, activation, or trading.
