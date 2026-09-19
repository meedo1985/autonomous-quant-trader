# Claude implementation review

**Date:** 2026-09-19
**Reviewed base:** `d0246a14aa34c98e29d95cf9e4ff7fb066e8d6ad`
**Observed primary model:** `claude-opus-5`
**Mode:** read-only, medium effort
**Initial verdict:** `BLOCKED` on B1 alone

Claude reviewed the proposed implementation, tests, import contract, owner
authorization, governance packet, frozen Constitution and protocol, and the
called production primitives. It made no edits and ran no commands.

## Findings

- **B1 — BLOCKER:** rounding the result stress multiplier to one decimal could
  bind an off-protocol `1.04` result to a `1.0` replicate stream. Require an
  exact numeric comparison and a regression test.
- **N1:** construct the expected canonical window with the same compact JSON
  convention rather than a hand-written string.
- **N2:** directly test both per-leg ESS fields, horizon propagation, and the
  Newey-West and explicit fallback paths; state that neither field is the
  protocol's governed `effective_decisions` value.
- **N3:** test stream asset, multiplier, window, and type mismatches.
- **N4:** add an independent hand-calculated fixture for the two Sharpe
  estimands rather than relying only on passthrough comparisons.
- **N5:** exercise the stream path under selected external-access tripwires and
  verify global RNG and stream preservation.
- **N6:** extend the import boundary to validation, allocation, and monitoring;
  record that `aqt.data.bars` is deliberately not forbidden indirectly because
  the required production backtester imports it.
- **N7:** document the deliberate segment-alignment call and error precedence.
- **N8:** normalize synthetic window boundaries to UTC before formatting.
- **N9:** avoid duplicating the primitive interval reason in the container.
- **Q1:** clarify that the component provides no serialization method; ordinary
  external dataclass utilities cannot be made unavailable by this type.
- **Q2:** paired-difference ESS would be a new scientific choice; do not add it
  without qualified human/statistician approval.
- **Q3:** leaving the inactive module out of `aqt.metrics.__init__` reduces
  accidental discoverability and should be deliberate.

Claude found no frozen-file change, threshold comparison, verdict, trial,
budget, I/O, clock, environment, or global-RNG access in the production module.
It confirmed that both Sharpe estimands remain separately named and delegated.
