# Review and test plan

**Status:** `PROPOSAL — APPLIES ONLY IF IMPLEMENTATION IS LATER AUTHORIZED`

## Containment checks

- The output type is frozen and slotted, with no mutable fields.
- It has mandatory `INACTIVE_DIAGNOSTIC_ONLY` status and convention fields.
- No field name expresses pass, fail, eligibility, promotion, gate, verdict,
  decision, approval, or rejection.
- The output exposes no serialization, mapping, persistence, or hashing method.
- Source contains no protocol threshold literals or threshold comparisons.
- A fifth import-linter contract machine-enforces the forbidden imports listed
  in the proposal.

## Determinism and purity

- Equal accepted inputs produce field-by-field equal outputs.
- Candidate, benchmark, and caller-supplied stream remain unchanged.
- Global random state remains unchanged and no module-level RNG exists.
- The full path succeeds while guarded filesystem, environment, process, socket,
  and URL entry points raise on access.
- Identity values are syntax-checked opaque strings and are never resolved.

## Independent numerical evidence

- Hand-computed complete-day fixtures cover per-leg mean, sample variance,
  daily/scaled Sharpe, drawdown, and paired improvement.
- One fixture proves difference-series Sharpe and difference of Sharpes are
  distinct estimands and remain separately named.
- For at least 16 observations, the assembled interval equals a direct call to
  the existing interval primitive with the same caller-supplied stream.
- Both Newey-West and horizon-fallback ESS paths surface method, diagnostics,
  fallback reason, horizon, and source-series identity unchanged.

## Fail-closed matrix

Reject or faithfully surface existing stable errors for mismatched symbols,
multipliers, counts, timestamps, incomplete days, discontinuities, broken equity
chains, nonfinite/nonpositive values, insufficient observations, zero variance,
malformed opaque identity, and a stream whose identity conflicts with the input.
Do not repair data. No stream produces an explicit unavailable interval rather
than an error. An off-protocol multiplier remains usable for descriptive
statistics but cannot accept a conflicting governed stream.

## Metamorphic evidence

- Swapping candidate and benchmark negates the appropriate paired quantities,
  permutes per-leg diagnostics, and preserves day boundaries.
- Mutating one candidate price changes the candidate and paired outputs while
  benchmark diagnostics remain bit-identical.
- Appending a strictly future suffix cannot change a prefix-only result.

## Required gates

Before implementation: owner-signed authorization with a closing stop gate.

Before merge: focused and full tests; Ruff format/check; strict mypy;
import-linter; whitespace check; complete frozen verification; Task 6 accepted
oracle/canary hash verification; byte equality for all frozen artifacts and
sidecars; independent quantitative review; independent governance review;
written adjudication of every finding; and the Constitution section 16
different-model plus human pull-request review.

Suggested future test locations are
`tests/unit/test_paired_evaluation_assembly.py` and a separate guarded-access
integration test. Existing passing Task 12 audit evidence must not be edited to
make the new component appear covered.
