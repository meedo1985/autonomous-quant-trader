# Task 12 independent review packet

Status: ready for different-model review
Base commit: `b963120dbd45add2c36e0fab91d6388ca8cefe27`
Worktree: uncommitted Task 12 snapshot

## Review scope

Read the complete current contents of:

- `review/task12/AUTHORIZED_SPEC.md`
- `review/task12/ASTRA_PROPOSED_STATISTICAL_CONVENTIONS.md`
- `review/task12/IMPLEMENTATION_CONVENTIONS.md`
- `review/task12/OWNER_DECISION.md`
- `src/aqt/metrics/statistics.py`
- `tests/unit/test_statistical_metrics.py`
- the one-line package import change in `tests/unit/test_package_imports.py`

Use the exact validation and hashes in `LOCAL_REPORT.md`. Independently inspect
all relevant existing backtest and descriptive-metric types. Do not edit files.

## Required adversarial questions

1. Does daily aggregation preserve all costs and accepted equity effects while
   rejecting partial, irregular, non-UTC, or misaligned data?
2. Are paired Sharpe improvement and difference-series Sharpe mathematically and
   semantically distinct everywhere, with sample variance, zero risk-free return,
   and `sqrt(365)` scaling implemented exactly?
3. Does Newey-West ESS use the approved denominator, Bartlett weights, bandwidth,
   bounds, diagnostics, and only the authorized fallback conditions?
4. Does PPW cutoff/window indexing have an off-by-one error? Are the influence
   transform, flat-top weights, corrected constant, degeneracy, clipping, and
   invalid-spectrum behavior exact?
5. Is seed material compact/canonical and bound to the actual convention document?
   Are integer draws unbiased, streams private, indices paired, and draw order
   stable?
6. Does the interval execute exactly 2,000 attempts, record every invalid
   replicate without replacement, use type-7 5th/95th percentiles, avoid
   recentering, and fail closed?
7. Can any input mutation, global RNG, filesystem/environment/network access,
   policy decision, DSR/PBO behavior, protected-data access, or governance
   activation occur?
8. Are tests independently meaningful rather than restating implementation, and
   is any acceptance criterion missing a regression test?

Return stable finding IDs under BLOCKER, NON-BLOCKING, and QUESTION. Include
file/line, reproducible evidence, impact, and minimal correction. End with PASS
or BLOCK. Do not modify files or propose strategy logic.
