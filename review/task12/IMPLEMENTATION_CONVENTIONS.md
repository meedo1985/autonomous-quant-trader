# Task 12 implementation conventions

Status: owner-approved for inactive Task 12 implementation; not governance-active.

This document fixes the numerical details implemented by
`aqt.metrics.statistics`. It does not authorize governed research, promotion,
confirmation/lockbox access, or a frozen-artifact amendment.

## Daily observations and Sharpe

Each observation is one complete UTC day containing exactly 24 contiguous,
nonoverlapping accepted one-hour segments. Candidate and benchmark paths must
share symbol, cost multiplier, timestamps, and boundaries. Missing, duplicated,
irregular, partial, or nonfinite data is rejected without repair.

Daily net return is `day_close_equity / day_open_equity - 1`, calculated for
each leg before subtraction. For `n >= 2`, use zero risk-free return, sample
variance with denominator `n - 1`, and `math.fsum`. Daily Sharpe is mean divided
by sample standard deviation; scaled daily Sharpe multiplies it by `sqrt(365)`.
Paired improvement is scaled candidate Sharpe minus scaled benchmark Sharpe.
Difference-series Sharpe is separately named and calculated from daily
candidate-minus-benchmark returns. Zero variance and nonfinite arithmetic are
unavailable; no epsilon floor or rounding is permitted.

## Newey-West ESS

For daily BTC strategy returns and horizon hours `H`, set `h = ceil(H / 24)`.
With centered observations `e`:

```text
gamma_k = fsum(e[t] * e[t-k], t=k..n-1) / n
L = min(n-1, max(h-1, floor(4 * (n/100)^(2/9))))
w_k = 1 - k/(L+1)
Omega = gamma_0 + 2 * fsum(w_k * gamma_k, k=1..L)
ESS = clamp(n * gamma_0 / Omega, 1, n)
```

For otherwise-valid zero variance or nonpositive `Omega`, return the protocol
fallback `n / h`, with method and reason. Missing/nonfinite data, invalid time,
unknown horizon, and `n < 2` do not use fallback.

## Paired-Sharpe influence and PPW block length

For each leg, use population-centered scale
`v = fsum((x-mean)^2)/n`, standardized `u = (x-mean)/sqrt(v)`, and the sample
daily Sharpe `S`:

```text
psi = u - (S/2) * (u^2 - 1)
z = psi_candidate - psi_benchmark
```

Require `n >= 16`. Center `z` and calculate autocovariances with denominator
`n`. Then:

```text
K = max(5, floor(log10(n)))
M_max = min(n-1, ceil(sqrt(n)) + K)
a = 2 * sqrt(log10(n)/n)
```

Find the smallest `k >= 1` for which all `K` autocorrelations beginning at `k`
have absolute value below `a`, with the full run inside `M_max`. If found, set
`M = min(2*k, M_max)`; otherwise set `M = M_max`. For `1 <= j <= M`, use
flat-top weight one when `j/M <= 1/2`, else `2*(1-j/M)`. Calculate:

```text
G = 2 * fsum(weight_j * j * gamma_j)
V = gamma_0 + 2 * fsum(weight_j * gamma_j)
b_raw = ((G^2 * n) / V^2)^(1/3)
b_max = min(n, ceil(min(3*sqrt(n), n/3)))
b = min(b_max, max(1, b_raw))
```

Retain fractional `b`; restart probability is `1/b`. Constant influence or
`G == 0` with positive `V` gives one. Nonconstant input with `V <= 0`, nonfinite
intermediates, or insufficient observations is unavailable.

## RNG, resampling, and interval

For replicate indices 0 through 1999, derive SHA-256 from compact UTF-8 JSON:

```text
[
  "aqt.statistics.stream.v1",
  trial_seed_hex,
  statistical_convention_hash,
  "paired_sharpe_ci",
  asset,
  cost_multiplier_string,
  evaluation_window_id,
  output_length,
  replicate_index
]
```

The statistical convention hash must equal the raw SHA-256 of this file. Convert
the complete digest to an unsigned big-endian integer and seed a private stdlib
`random.Random` instance. Draw uniform indices with `getrandbits(n.bit_length())`
and rejection. Draw the initial index first; at each later position draw one
restart decision, then a fresh index only on restart, otherwise advance modulo
`n`. Apply identical indices to candidate and benchmark.

Execute exactly 2,000 attempts in index order. Any invalid replicate makes the
interval unavailable; never drop, replace, or extend attempts. For sorted valid
values, use linear/type-7 quantiles with position `(B-1)*q`. The two-sided 90%
percentile interval is `[Q(0.05), Q(0.95)]` without null recentering.
