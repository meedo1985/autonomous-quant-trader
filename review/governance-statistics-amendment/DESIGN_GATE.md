# Design-preparation gate

**Date:** 2026-09-15
**Scope:** DSR calibration plan and joint-leg lockbox prediction proposal
**Local gate:** **PASS** for blocked-proposal preparation only
**Activation gate:** **BLOCKED** by B1-B5

## Scope and evidence

- Added an AI-proposed DSR calibration plan without selecting a method or
  post-calibration acceptance values.
- Added an AI-proposed lockbox estimand with separate source length `n`, prebound
  calendar target length `m`, joint-leg resampling, and fail-closed gaps.
- Preserved the experiment-engine and `lockbox_eval` identity boundary: the
  former computes and seals the confirmation prediction artifact; the latter
  receives no raw confirmation data and returns PASS/FAIL only to research.
- Recorded Astra scientific design and synthesis verification.
- Recorded Binance/trading specialist review and its resolved identity-boundary
  correction.

## Validation

- Frozen verifier: 28/28 trusted bytes and exact inventory; 14/14 sidecars;
  Constitution self-hash; 7/7 manifest/protocol bindings; nested cost, feature,
  and benchmark bindings all passed.
- Git whitespace check: passed.
- Focused wording checks confirmed explicit `n`/`m`, fresh restart indices,
  current-cycle matrix restrictions, 1.0x paired execution semantics, no raw
  confirmation transfer, and PASS/FAIL-only research output.
- Tests, Ruff, mypy, and import-linter: N/A because this task changes review
  documents only and no executable or import-boundary behavior.

## Outstanding blockers

B1-B3 require selection and independent calibration of a complete DSR method.
B4 requires human acceptance and independent coverage assessment of the lockbox
estimand. B5 requires human-authored final specification, deterministic
implementation migration, independent reference vectors, version/hash binding,
and formal Constitution section 4 activation. No governed trial, lockbox access,
promotion, or Task 13 implementation is authorized by this gate.
