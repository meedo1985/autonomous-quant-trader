# Task 12 statistical conventions — Astra proposal

Status: **OWNER-APPROVED FOR INACTIVE TASK 12 IMPLEMENTATION — NOT GOVERNANCE-ACTIVE**

Date: 2026-09-14
Proposed by: GPT-6 Astra, high reasoning effort

The owner approved this proposal in the project conversation on 2026-09-14 as
the basis for inactive Task 12 implementation. It does not amend or activate
frozen governance or authorize confirmation/lockbox access.

## Recommended task boundary

Task 12 should implement pure statistical primitives only:

- construction of complete UTC-day net returns from accepted backtest results;
- daily and scaled Sharpe statistics;
- separately named difference-series Sharpe and paired Sharpe improvement;
- Newey-West effective sample size with full diagnostics;
- corrected Patton-Politis-White block-length selection;
- deterministic stationary-bootstrap indices and paired percentile intervals;
- immutable results carrying convention and seed identifiers;
- synthetic fixtures and independent numerical reference tests.

Task 12 must exclude DSR/PBO implementation, eligibility or PASS/FAIL gates,
trial execution/accounting enforcement, confirmation or lockbox access,
prediction, ingestion, models, delayed execution, schema changes, trading,
deployment, and governance activation.

## Return construction and Sharpe

For each complete UTC day, compound each accepted hourly equity path separately:

```text
c_t = candidate_close / candidate_open - 1
b_t = benchmark_close / benchmark_open - 1
d_t = c_t - b_t
```

Do not compound hourly differences as an investable equity path. Require exactly
24 contiguous, nonoverlapping hourly segments per day and identical candidate and
benchmark timestamps, asset, cost multiplier, and evaluation boundaries. Reject
missing, duplicate, irregular, partial, nonfinite, or misaligned inputs without
trimming, filling, interpolation, or intersection joins.

For a finite, nonconstant vector `x` with `n >= 2`:

```text
mean = fsum(x) / n
variance = fsum((x_i - mean)^2) / (n - 1)
daily_sharpe = mean / sqrt(variance)
scaled_daily_sharpe = sqrt(365) * daily_sharpe
paired_sharpe_improvement = scaled_sharpe(candidate) - scaled_sharpe(benchmark)
difference_series_sharpe = scaled_sharpe(candidate - benchmark)
```

Use zero risk-free return, `ddof=1`, binary64 arithmetic, deterministic ordering,
and `math.fsum`. The two Sharpe estimands are distinct and must never share a
name. Return explicit unavailable results for fewer than two observations, zero
variance, invalid timestamps, or nonfinite arithmetic; do not use epsilon floors.

## Newey-West effective sample size

Use daily BTC strategy returns, not paired differences, trade counts, or bars.
For horizon hours `H`, define `h = ceil(H / 24)`, centered returns `e_t`, and:

```text
gamma_k = fsum(e_t * e_(t-k)) / n
L = min(n - 1, max(h - 1, floor(4 * (n / 100)^(2 / 9))))
w_k = 1 - k / (L + 1)
Omega = gamma_0 + 2 * fsum(w_k * gamma_k, k=1..L)
ESS = clamp(n * gamma_0 / Omega, 1, n)
```

If otherwise-valid data has zero variance or nonpositive long-run variance, use
the frozen fallback `n / h`, record `HORIZON_FALLBACK`, and record its reason.
Do not use fallback for missing/nonfinite data, unknown horizon, invalid time, or
`n < 2`. Report `n`, `h`, `L`, `gamma_0`, `Omega`, method, and fallback status.

## Stationary bootstrap

Use the corrected Patton-Politis-White 2009 stationary-bootstrap block-length
constant. Select block length from the estimated influence series for the paired
Sharpe-improvement statistic. Require `n >= 16`; retain a fractional block length
and use restart probability `p = 1 / block_length`. Record all pilot parameters
and clipping/degeneracy status. Degenerate influence gives block length one;
nonconstant input with invalid long-run quantities is unavailable.

Each replicate selects an initial uniform index. At every later position it draws
one restart decision; on restart it draws a fresh uniform index, otherwise it
advances the prior index modulo `n`. Apply the same indices to candidate and
benchmark and subtract their recomputed Sharpes. Never resample the two legs
independently.

## RNG, repetitions, and quantiles

Retain Task 10's full 64-hex trial seed. Derive one seed per replicate as SHA-256
of compact UTF-8 canonical JSON containing:

```text
[
  "aqt.statistics.stream.v1",
  trial_seed_hex,
  statistical_convention_hash,
  purpose,
  asset,
  cost_multiplier_string,
  evaluation_window_id,
  output_length,
  replicate_index
]
```

Use a private stdlib `random.Random`/MT19937 instance with the exact Python
runtime recorded. Convert the complete digest to an unsigned big-endian integer.
Use rejection sampling with `getrandbits` for uniform indices. Do not use global,
time, or OS randomness. Execute and reduce replicates in index order.

Use exactly the frozen 2,000 attempted replicates. Any invalid replicate makes
the interval unavailable; never discard, replace, or extend attempts.

For sorted results `y` and probability `q`, use the linear/type-7 quantile:

```text
j = floor((B - 1) * q)
g = (B - 1) * q - j
Q(q) = (1 - g) * y[j] + g * y[j + 1]
```

The two-sided 90% percentile interval is `[Q(0.05), Q(0.95)]`. Preserve the
original mean; do not null-recenter.

## Deferred policy proposals

DSR remains based on unannualized daily candidate-minus-benchmark returns, which
is a different hurdle from paired Sharpe improvement. Exact DSR dependence
adjustment, effective family-trial construction, PBO partitions/ties, missing
attempt handling, CI equality, ETH stress interpretation, and all promotion
decisions remain outside Task 12.

Future PBO should use 16 chronological blocks and all 12,870 oriented 8/8
combinations, preserve remainder observations, use midranks and explicit tie
handling, and fail closed on incomplete matrices. This is only a downstream
proposal and is not authorized here.

Reuse Task 11 drawdown exactly: initial equity plus each hourly closing equity,
reported as a nonnegative fractional peak-to-trough magnitude.

## Frozen values confirmed by the review

- bootstrap attempts: 2,000;
- paired confidence level: 90%;
- DSR threshold: 0.95;
- PBO maximum: 0.30;
- PBO activation: 20 family trials;
- PBO partitions: 16;
- minimum effective decisions: 120;
- CPCV activation: 250 effective decisions;
- fold-win fraction: 0.60;
- null percentile: 0.95;
- trial budget: 81 per family.

These values do not by themselves define the estimators above.

## Acceptance gate

Inactive pure-primitives implementation may start under the recorded owner
approval. Use in a governed research cycle remains blocked until the applicable
formal governance binding is complete. Acceptance must include hand-calculated
Sharpe and daily-compounding examples, a fixture proving the two Sharpe estimands
differ, invalid/partial/misaligned data rejection, analytic Newey-West fixtures,
independent block-length fixtures, fixed RNG/index vectors, paired-index checks,
type-7 quantiles, exact 2,000-attempt handling, deterministic reruns, full tests,
static/import checks, frozen-byte verification, full base-to-final whitespace
checking, and independent scientific review of the final implementation.

Current decision: **GO for inactive Task 12 implementation; NO-GO for governed
use or activation.**
