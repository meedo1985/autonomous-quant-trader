# Task 12 independent Sol High review

Date: 2026-09-15
Model: `gpt-5.6-sol`, high reasoning effort
Mode: independent read-only adversarial review

## Decision

**PASS.** No blockers or unresolved questions were found.

## Evidence

- Daily aggregation preserves accepted equity effects and rejects partial,
  irregular, non-UTC, discontinuous, and misaligned paths.
- Sharpe uses sample variance, zero risk-free return, and `sqrt(365)`. Paired
  improvement and difference-series Sharpe remain separately named estimands.
- Newey-West uses denominator `n`, the approved bandwidth and Bartlett weights,
  bounded ordinary ESS, complete diagnostics, and only authorized fallbacks.
- An independent exact-rational PPW comparison covered 15,000 generated cases,
  including the final admissible cutoff at `n=16, k=5`; no window/indexing error
  was found. Exact `G=0` and degenerate/invalid-spectrum paths also behaved as
  specified.
- Seed JSON is compact and canonical, uses the full digest, binds the raw
  convention-document hash, creates private MT19937 streams, uses unbiased
  rejection sampling, and preserves draw order.
- Bootstrap intervals execute replicate indices 0 through 1999 exactly once,
  share indices between legs, retain invalid attempts without replacement, fail
  closed, and use unrecentered type-7 5th/95th percentiles.
- No protected policy, filesystem/environment/network/exchange access, global
  RNG, DSR/PBO, verdict, or governance activation exists.
- Focused independent validation: 37 passed with bytecode/cache writes disabled.
- Reviewed source/test hashes matched `LOCAL_REPORT.md`; frozen paths were
  unchanged from the authorized base.

## Non-blocking finding

`T12-NB-01`: the primitives remain inactive for governed research, exactly as
recorded in `OWNER_DECISION.md`. Formal governance binding is a later task and is
not a Task 12 defect.
