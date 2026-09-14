# Task 11 Claude adversarial review packet

Status: ready for direct local Claude Code review
Date: 2026-09-14
Base commit: `0d48d884469382940d26d24d93a983d758382afb`

Review only Task 11 against `review/task11/AUTHORIZED_SPEC.md`,
`review/task11/SCIENTIFIC_DECISION.md`, root `AGENTS.md`, the frozen protocol,
backtester spec, and the repository review skills. Do not edit files, access
network/confirmation/lockbox data, or propose statistical policy.

Inspect the actual working-tree files and untracked files:

- `src/aqt/metrics/__init__.py`
- `src/aqt/metrics/descriptive.py`
- `tests/unit/test_descriptive_metrics.py`
- `tests/unit/test_package_imports.py`
- `review/task11/AUTHORIZED_SPEC.md`
- `review/task11/SCIENTIFIC_DECISION.md`
- `review/task11/LOCAL_REPORT.md`

Local evidence: 998 tests passed with 4 pre-existing skips; Ruff, format,
mypy, import contracts, Git whitespace, frozen 28/28 and 14/14 sidecars, and
Task 6 6/6 hashes passed. See `LOCAL_REPORT.md` for command details.

Questions:

1. Are every descriptive metric and net-return observation derived exactly
   from accepted backtester equity/cost semantics without look-ahead or hidden
   correction?
2. Are finite values, continuity, timestamps, stress identity, symbols, and
   pairing mismatches fail-closed?
3. Is maximum drawdown's initial-peak and magnitude convention explicit and
   correctly tested?
4. Does any code accidentally implement Sharpe, ESS, bootstrap, DSR, PBO,
   selection, eligibility, promotion, or a metrics-schema amendment?
5. Are the tests meaningful and is any acceptance criterion missing evidence?

Return stable finding IDs under BLOCKER, NON-BLOCKING, and QUESTION. For each
finding name file/line, triggering scenario, evidence, impact, and the minimal
correction or clarification. End with PASS or BLOCK. Do not modify files.
