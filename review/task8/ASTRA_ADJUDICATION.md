# Task 8 Astra adjudication

Date: 2026-09-14
Initial reviewer verdict: FAIL
Corrected-snapshot reviewer verdict: PASS

| ID | Severity | Decision | Disposition | Validation |
|---|---|---|---|---|
| T8-ASTRA-B1 | BLOCKER | AGREE | Added fail-loud guards for invalid computed returns and equity, plus overflow/cancellation regressions. No clamping, new tolerance, or reference change. | Astra reproduced all five failures as rejected; focused 25 and full 845 passed. |
| T8-ASTRA-NB1 | NON-BLOCKING | AGREE | Corrected the report's attribution: section 16 binds the backtester implementation order but does not enumerate the backtester in its protected-component human-PR list. | Frozen Constitution hash remains verified; report text rechecked. |
| T8-ASTRA-Q1 | QUESTION | AGREE | Kept nonzero delay rejected because pending-fill exposure and supersession remain unbound. | Existing delay regression and frozen audit passed. |

Final implementation hashes:

```text
0cac409d20a6dde7f8c99e1ca58f49697ec6acd4eb9d8084c8d9eaa11e4c3ad1  src/aqt/backtest/engine.py
12d5338e57c6aa5c1e21129fb03be1ae8b57b65b7ebf0f37053ad156e100eee3  tests/unit/test_backtest_engine.py
f3f0b9486e5e77e5d1ee79666e35a260d5888aabe126abeddb07d9828323b231  tests/integration/test_production_backtest_comparison.py
```

`LOCAL GATE: PASS`
