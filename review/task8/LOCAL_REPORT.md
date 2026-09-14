# Task 8 local report

Date: 2026-09-14
Base/HEAD commit: `5e03693457a50b830c65da1c5d8f5e3ccaf6ce23`
(`Finalize Task 7 review evidence`)

## Scope and implementation

Task 8 adds the smallest pure production backtester for a timestamped hourly
target-exposure path. It starts flat, resolves the frozen next-open execution,
clips targets to `[0, 1]`, applies the accepted band/scheduling/minimum-hold
rules to actual drifted exposure, charges absolute-turnover cost before the
following open-to-open return, compounds equity, retains audit-rich segment
records, and does not force terminal liquidation.

Claude Code supplied the initial design and reviewed the finished accounting
path using the observed canonical model metadata `claude-opus-5` at medium
effort. Exact `claude-opus-5-1` was requested first but the installed Claude
Code reported it as an unrecognised model; no silent substitution is claimed.
The Opus review found no accounting bug and raised two coverage/API findings:
the causal volatility offset needed a direct regression, and a malformed
`series` escaped the public `BacktestError`. Both were fixed. The independent
oracle comparison then exposed a binary64 operation-order discrepancy in the
gross return; production now uses the accepted `(next_open - open) / open`
order rather than widening the proven tolerance.

An independent GPT-6 Astra High review then demonstrated a numeric-result
blocker outside the normal fixture magnitudes: finite positive prices could
overflow the computed return, cancellation could round a strictly greater
than `-1` loss to `-1`, and a long valid path could overflow compounded
equity. Production now rejects nonfinite or `<= -1` computed returns and
nonfinite or nonpositive equity states before publishing a segment. Astra
reproduced all five original failure cases after the correction; every case
now raises `BacktestError`.

No Task 9 logic, data ingestion, strategy/model logic, portfolio aggregation,
metrics engine, validation/promotion, governor, execution, exchange/network,
credential, paper-trading, or live-trading code was added. No frozen file,
accepted Task 6 file, or Task 7 reference file changed.
`README.md` only advances the repository status from accepted Task 7 to
accepted Task 8 and links the new evidence directory.

## Acceptance evidence

- The integration matrix runs all 20 accepted fixtures under floor/cap costs
  and all four frozen stress multipliers: 160 paths and 11,816 hourly
  segments. Every discrete action must match the independent NumPy reference;
  every production numeric quantity must lie in the exact-oracle-centred,
  operation-derived binary64 bound. The same bounds separately contain the
  NumPy values.
- Direct tests cover next-open timestamps/prices, clipping, fractional and
  adverse drift, inclusive/inside band behavior, scheduled and intraday
  decisions, the 24-hour minimum hold, cost-before-return, fee provenance,
  stress, zero exposure, no forced liquidation, invalid inputs, missing/gapped
  history, deterministic reruns, and input immutability.
- Numeric-domain regressions cover return overflow, a rounded total loss, and
  cumulative equity overflow without clamping or widening Task 7 bounds.
- A causality regression calculates the decision-time volatility from the two
  observable prefix returns and proves that changing execution/future closes
  cannot change the first segment's cost inputs.
- The floor/cap adapter is pinned to 13/27 bps per side.

Delay stress remains intentionally rejected. The frozen artifacts require one
bar of delay but do not bind how hourly decisions that occur while an earlier
fill is delayed observe exposure: pre-fill state, a pending target, or
post-fill state. Task 8 does not guess. The baseline engine is complete and
returns an explicit `BacktestError` for nonzero `delay_bars`.

## Environment

- Microsoft Windows NT 10.0.26200.0, AMD64
- PowerShell 7.6.5; timezone `West Bank Standard Time`
- CPython 3.12.10, 64-bit AMD64, MSC v.1943
- NumPy 2.5.3; pytest 8.4.2
- Ruff 0.11.13; mypy 1.20.2; import-linter 2.15

The engine reads no clock, environment variable, random source, file, network,
exchange, credential, or market-data service. Tests use only fixed synthetic
fixtures. The production reduction and record order are deterministic.

## Final validation evidence

```text
.\.venv\Scripts\pytest.exe -q -p no:cacheprovider
  tests/unit/test_backtest_engine.py
  tests/integration/test_production_backtest_comparison.py
exit 0 — 25 passed in 5.72s

.\.venv\Scripts\pytest.exe -q -rs -p no:cacheprovider
exit 0 — 845 passed, 4 skipped in 36.93s

.\.venv\Scripts\ruff.exe check --no-cache .
exit 0 — All checks passed

.\.venv\Scripts\ruff.exe format --check --no-cache .
exit 0 — 42 files already formatted

.\.venv\Scripts\mypy.exe src --no-incremental
  --cache-dir "$env:TEMP\aqt-task8-mypy-final"
exit 0 — Success, 21 source files

.\.venv\Scripts\lint-imports.exe --no-cache
exit 0 — 4 contracts kept, 0 broken

git diff --check
exit 0

& .\review\task6\verify_frozen.ps1
exit 0 — 28/28 trusted bytes and exact inventory; 14/14 sidecars;
Constitution self-hash, 7/7 manifest/protocol bindings, and all nested
cost/feature/benchmark bindings passed

review/task6/ACCEPTED_ORACLE_HASHES.sha256 independent SHA-256 loop
exit 0 — 6/6 accepted Task 6 oracle/canary hashes
```

The four skips are the pre-existing constant-benchmark branches at
`tests/unit/test_canonical_benchmarks.py:767` and `:777` (two cases each). They
are intentional and unrelated to Task 8.

## Reviewed implementation hashes

```text
c2ad8002bea19feabd223685e00e0b3a230eb4c5e0849f6c1a805d27fb042bde  README.md
61ad9f0abc6ae1641b47a39fe4f04693a745c75ccc9c723f196492c5e63b181b  review/task8/AUTHORIZED_SPEC.md
c890d2a2d7605de15fced390491a4e058c0403be4c524247c67ff5d64a37432b  review/task8/OPUS_PROMPT.md
0cac409d20a6dde7f8c99e1ca58f49697ec6acd4eb9d8084c8d9eaa11e4c3ad1  src/aqt/backtest/engine.py
12d5338e57c6aa5c1e21129fb03be1ae8b57b65b7ebf0f37053ad156e100eee3  tests/unit/test_backtest_engine.py
449160eeaf2ca8bdc6d146170b5d7463389891d9485d0a75115bea19128c1b9f  tests/integration/__init__.py
f3f0b9486e5e77e5d1ee79666e35a260d5888aabe126abeddb07d9828323b231  tests/integration/test_production_backtest_comparison.py
```

This report, adversarial packet, Fable review/adjudication, and Astra
review/adjudication are excluded from their own hash list. The worktree
contains only the six new Task 8 files above, those six review documents, and
the Task 8 status update in `README.md`. No commit or push has been performed.

Scientific reproducibility review: PASS. Quant review: PASS for the baseline;
delay stress is the explicit non-blocking policy question above. Local task
gate: PASS. The independent Claude Fable 5.1 review returned PASS with no
blockers. Its findings were adjudicated in `REVIEW_ADJUDICATION.md`; its
accepted Boolean-stress correction passed. Astra's later numeric blocker was
corrected and independently reproduced, and the complete final validation
above passed. External AI review status: ADJUDICATED.

Constitution section 16's required backtester implementation order—exact
oracle, NumPy reference, then production—has been followed. Its enumerated
human-PR list does not include the production backtester, so the earlier
blanket attribution was removed. The requested Astra review is an independent
AI review in a human-style PR format; it is not represented as a real human
approval. Commit and push remain withheld because `AUTHORIZED_SPEC.md`
explicitly requires stopping after the Task 8 implementation and local report.

`LOCAL GATE: PASS`
