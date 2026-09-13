# Task 7 — NumPy reference implementation

Authorization: owner requested Claude Opus 5 to continue the project after
human acceptance and freezing of Task 6, 2026-09-13.

## Scope

Implement only an independent NumPy `float64` reference for the frozen
backtester semantics and compare it against the accepted exact Task 6 oracle.
The reference is a research validation artifact, not the production
backtester. It must model clipped targets, actual fractional-weight drift,
next-open execution, absolute exposure turnover, cost-before-return, the
inclusive 10pp band, 00:00 UTC risk-increase scheduling, 24h minimum hold, and
intraday reductions only. Preserve the accepted flat start, compounded
production equation, additive diagnostic, and no forced terminal liquidation.

## Required evidence

- Independent NumPy implementation with no import from `src/aqt` and no edits
  to `tests/oracles`, `tests/canaries`, frozen governance, or their hash files.
- Synthetic fixtures only; no network, exchange, confirmation, lockbox,
  credentials, strategy, ML, LLM, execution, governor, or live code.
- Tests compare the NumPy reference with exact Task 6 identities, including
  binary paths, clipping, fractional drift, next turnover, cost monotonicity,
  scheduling/band behavior, and deterministic reruns.
- Numeric comparison tolerance must be derived and documented from float64
  roundoff and operation count; do not invent a trading or performance
  threshold. Exact identity cases should use exact equality where representable.
- Record environment, commands, exit codes, scope, assumptions, and reviewed
  file hashes in `review/task7/`.

## Exclusions and gate

Do not implement a production backtester, adapter, metrics engine, strategy,
validation engine, or Task 8. Do not change frozen v1.0 artifacts or accepted
Task 6 files. Do not commit or push. Run the repository's tests, lint, type,
and import-boundary checks, plus frozen/hash verification. Stop at Task 7 and
report any unbound policy rather than guessing.
