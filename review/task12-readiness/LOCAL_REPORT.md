# Task 12 synthetic cross-layer readiness audit

Date: 2026-09-19

Authorized base: `f235843981ae964b02707904d25d356f453d8b54`

Status: local gate passed; GitHub CI pending push

## Scope and evidence

One synthetic integration test connects all five canonical benchmark signal
paths to the production backtester. It then carries selected synthetic paths
through descriptive metrics, complete UTC-day aggregation, paired statistics,
and the inactive Task 12 bootstrap interval.

The test also proves prefix causality under a real future mutation, fail-closed
handling at representative bar/backtest/statistical boundaries, deterministic
reruns, preservation of inputs and global RNG, and absence of calls through the
guarded post-import filesystem, environment, process, and network entry points.

`BTCUSDT`, 2020 timestamps, and the all-zero seed are API-mandated or explicit
synthetic labels. Prices are a deterministic sine fixture around 100 arbitrary
units. They are not Binance market data. No registry entry, experiment, trial,
account, credential, API, order, or network connection exists in this audit.
The resulting numbers provide no evidence of edge, profitability, Binance
parity, confirmation readiness, eligibility, or promotion.

New coverage is specifically:

```text
canonical causal benchmark target
→ production backtester timing/cost/exposure path
→ descriptive metrics
→ aligned complete-day Task 12 statistics
```

Existing unit assertions for 2,000 attempts, RNG isolation, and statistical
error behavior are corroborating evidence, not claimed as new coverage.

## Specialist review

- Senior quantitative/statistical agent defined the permitted arithmetic,
  causality, alignment, and non-promotion assertions.
- Senior software-test/Binance-safety agent inspected the exact APIs and
  designed the five-test cross-layer audit. It confirmed that no Binance
  adapter or executor currently exists, so exchange parity is N/A.
- Senior governance agent confirmed that Task 13 and DSR remain blocked and
  drafted the closed authorization boundary.
- Claude Opus independently reviewed the first complete audit and returned
  PASS with 15 non-blocking/questions. Every item is adjudicated in
  `ADJUDICATION.md`.

The quantitative and governance agents later attempted separate command reruns
but hit the Codex usage limit. Their earlier completed reviews remain evidence;
they did not claim those reruns succeeded. The primary agent ran every mandatory
command, and Claude reviewed the code read-only.

## Validation

- Focused audit: **5 passed in 54.86 seconds** after final corrections.
- Full suite: **1097 passed, 4 skipped in 189.43 seconds** using an explicit
  writable pytest base temp.
- Ruff format: **58 files already formatted**.
- Ruff check: **all checks passed**.
- mypy: **28 source files clean**.
- import-linter: **4 contracts kept, 0 broken**.
- Frozen verifier: **28/28 trusted bytes and exact inventory; 14/14 sidecars;
  Constitution self-hash; 7/7 manifest and protocol bindings; nested cost,
  feature, and benchmark bindings passed**.
- Task 6 accepted oracle/canary hashes: **6/6 passed**.
- `git diff --check`: **passed**.

Final pre-commit hashes:

```text
78779a787043bebd741c62b87eaf6af2cb698459899ff46a910373a53930facf  tests/integration/test_synthetic_readiness_audit.py
20e66898fef7747d9859440f7933c83f970e949c6baee6ed15fd23b3c81fe5a3  review/task12-readiness/OWNER_AUTHORIZATION.md
```

## Gate

**PASS WITH ADVISORIES** for Task 12 synthetic integration readiness. No local
or independent-review blocker remains.

This gate closes `OD-T12R-001` only. It does not authorize Task 13, DSR/PBO,
calibration, governed trials, confirmation/lockbox access, Binance integration,
eligibility, promotion, deployment, or trading.
