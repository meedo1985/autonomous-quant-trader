# Task 12 — deterministic statistical primitives

Approved: 2026-09-14
Base commit: `b963120dbd45add2c36e0fab91d6388ca8cefe27`

## Scope

Implement the smallest pure standard-library statistical layer consistent with
`ASTRA_PROPOSED_STATISTICAL_CONVENTIONS.md`:

1. Construct complete UTC-day candidate and benchmark net returns from accepted,
   strictly aligned hourly `BacktestResult` values.
2. Calculate sample-variance daily Sharpe, 365-day scaled Sharpe, separately
   named difference-series Sharpe, and paired Sharpe improvement defined as
   `scaled_sharpe(candidate) - scaled_sharpe(benchmark)`.
3. Calculate Newey-West ESS and expose all method diagnostics and explicit
   horizon fallback status.
4. Calculate the approved corrected PPW block length from the paired-Sharpe
   influence series.
5. Deterministically derive private replicate RNG seeds and generate stationary-
   bootstrap index sequences shared by candidate and benchmark.
6. Produce a paired 90% percentile interval from exactly 2,000 attempted
   replicates using the approved type-7 quantile; any invalid replicate makes the
   interval unavailable.
7. Use immutable result types, explicit stable error codes, finite validation,
   deterministic ordering, binary64 arithmetic, and `math.fsum` reductions.

## Exclusions

Do not implement DSR, PBO, prediction or lockbox workflows, gates or PASS/FAIL,
trial execution/accounting enforcement, confirmation/lockbox access, ingestion,
models, delay semantics, schema changes, governance amendment or activation,
trading, deployment, or Task 13.

The module must perform no filesystem, network, environment, exchange, or hidden
data access. It consumes supplied accepted objects or plain finite sequences.
These primitives remain inactive for governed research until formal governance
binding is completed.

## Acceptance criteria

- Hand-calculated daily compounding, sample variance, Sharpe, paired improvement,
  and difference-series examples, including a case proving the estimands differ.
- Complete rejection coverage for partial, misaligned, invalid, zero-variance,
  insufficient, and nonfinite inputs without silent repair.
- Analytic Newey-West fixtures for lag-zero, positive/negative dependence,
  bandwidth bounds, and explicit fallback.
- Independent PPW fixtures for cutoff discovery, no cutoff, clipping,
  degeneracy, and invalid long-run quantities.
- Fixed seed and index vectors, restart/wraparound checks, shared paired indices,
  and deterministic replicate ordering.
- Hand-calculated type-7 quantiles, exactly 2,000 attempts, and fail-closed invalid
  replicate behavior.
- No input mutation, prohibited I/O, policy verdict, or frozen-file change.
- Focused and full tests, Ruff, mypy, import-linter, complete base-to-final
  whitespace check, frozen verification, Task 6 accepted hashes, and independent
  scientific/adversarial review of the final implementation.

## Gate

Completion requires all acceptance evidence and adjudication of independent
review findings. Stop after Task 12; do not start Task 13.
