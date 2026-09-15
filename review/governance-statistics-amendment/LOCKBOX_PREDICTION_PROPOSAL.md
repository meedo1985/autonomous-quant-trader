# Proposed joint-leg lockbox prediction estimand

**Status:** AI proposal only; not accepted, implemented, frozen, or active
**Illustrative identifier:** `joint_daily_delta_sharpe_prediction.v1`

## Source and target

The authorized experiment identity receives aligned BTCUSDT confirmation OOS
pairs `(candidate_return, benchmark_return)` at the frozen 1.0x modeled
fee/spread/slippage cost multiplier. It computes and seals the prediction
artifact before any lockbox access. Raw confirmation pairs, replicate values,
and diagnostics never cross into `lockbox_eval`. Each leg is compounded
separately into a complete UTC day containing exactly 24 accepted contiguous
hourly holding segments. Missing, duplicated, irregular, nonfinite, or
misaligned source days make the calculation unavailable.

The candidate configuration, comparison benchmark, causal training schedule,
source window, target window, and all hashes are prebound. Resampling realized
OOS pairs does not rerun or reselect a model.

## Prediction length

Let `m` be the number of scheduled complete UTC days in a prebound half-open
target window `[L0, L1)`, with both endpoints at midnight UTC:

```text
m = (L1 - L0) / 24 hours
```

Bind `m` before any target-data read. It is not hourly-bar count, trade count,
risk-increase count, ESS, or a count reduced after observing gaps. If the target
window cannot supply its complete prebound paired path, the result is
unavailable; do not shorten `m` or reveal gap diagnostics to research.

## Prediction statistic

For a valid paired path of length `m`, compute each leg's zero-risk-free sample
Sharpe with denominator `m-1`, then:

```text
T_m = sqrt(365) * (Sharpe_daily(candidate) - Sharpe_daily(benchmark))
```

Both leg variances must be positive and all arithmetic finite. A Sharpe of the
return-difference series is a different estimand and cannot substitute.

## Joint stationary-bootstrap distribution

1. Let `n` be the number of aligned valid source daily pairs. Require `n>=16` as
   the proposed PPW method-admissibility minimum and `m>=2` as the target Sharpe
   arithmetic minimum. Neither proves adequate prediction coverage.
2. Select one fractional PPW block length from the confirmation paired-Sharpe
   improvement influence process using the inactive Task 12 convention.
3. For each replicate, draw `m` indices from source positions `0..n-1`: draw an
   initial uniform index; then, at each subsequent position, restart with
   probability `1/b`. On restart draw a fresh uniform index from `0..n-1`;
   otherwise advance the prior index modulo source length `n`.
4. Apply the same index to the complete candidate/benchmark pair.
5. Compute `T_m` from the two sampled legs.
6. Execute exactly 2,000 attempts in order `0..1999`. Any invalid replicate makes
   the prediction quantile unavailable; never omit, replace, or extend attempts.
7. Preserve source means and use no null recentering.
8. Use the lower type-7 quantile at 0.05. For 2,000 sorted values with zero-based
   indexing, this is `0.05*y[99] + 0.95*y[100]`.

This is a plug-in distribution for an `m`-day realization under the fitted joint
resampling process. It is not a confidence interval for the confirmation mean or
a distribution-free guarantee about future lockbox behavior.

## Future comparison and information boundary

The experiment engine computes and seals the confirmation-derived prediction
quantile before target access. `lockbox_eval` verifies the bound sealed artifact,
computes the actual paired target statistic, and compares it to the frozen lower
prediction quantile with `>=`. Target BTC candidate and benchmark returns use the
same frozen 1.0x modeled-cost and execution semantics as the confirmation source.
The existing strictly positive BTC improvement, hourly-path drawdown constraint,
and ETH 1.0x modeled-cost sanity rule remain separately mandatory. A daily
bootstrap path does not supply the hourly drawdown test. Missing or invalid input
cannot pass.

Source data, replicate values, target paths, and diagnostics remain under their
authorized identities. The experiment engine seals the prediction artifact;
`lockbox_eval` receives no raw confirmation data. Research receives PASS/FAIL
only. A failed lockbox result never authorizes adaptive reseeding, resizing,
recalibration, or retry using exposed information.

## Deterministic implementation migration

Current Task 12 code cannot implement this proposal: its stream purpose is only
`paired_sharpe_ci`, and its index generator fixes output length equal to source
length. A future reviewed contract must separately bind:

- full Task 10 seed and final statistical-specification hash;
- distinct prediction purpose and method identifier;
- asset, canonical cost string, candidate and benchmark identity;
- source artifact/window identity and source length `n`;
- target window identity and output length `m`;
- replicate index, serialization bytes, digest interpretation, runtime, integer
  rejection sampling, random draw order, floating reductions, and quantile rule.

Independent references must cover `m<n`, `m=n`, and `m>n`; modulo-`n`
wraparound; fractional and unit block lengths; shared-leg indices; exact seed
material and digests; invalid replicas; intermediate moments; threshold equality;
and same-runtime byte reproducibility separately from independent numerical
agreement.

## Acceptance boundary

Coverage under finite `n,m`, serial dependence, selection conditioning, and
changing distributions requires independent assessment. B4-B5 remain open. No
code, lockbox access, governed trial, promotion, or activation is authorized.
