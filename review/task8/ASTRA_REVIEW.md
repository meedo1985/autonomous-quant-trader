# Task 8 independent Astra review

Reviewer: GPT-6 Astra High review agent
Date: 2026-09-14
Mode: independent read-only, human-style PR review
Final verdict: **PASS**

This is an AI review and is not represented as approval by a human person.
The reviewer inspected the whole repository, the complete untracked Task 8
snapshot, reused production modules, accepted Task 6 exact oracle, Task 7
NumPy reference and bounds, frozen governance, prior Fable review, and local
gate evidence. No files were edited, committed, or pushed by the reviewer.

## Initial blocker: T8-ASTRA-B1

The original engine did not validate computed return and equity values. Astra
demonstrated five failures using valid contiguous UTC bars and strictly
positive finite prices:

- `1e-300 -> 1e300` produced an infinite return and NaN equity at zero
  exposure.
- The same prices produced infinite equity at full exposure.
- `1 -> 1e-20` rounded a strictly greater than `-1` loss to `-1.0`.
- The rounded loss returned zero equity at full exposure and a successful
  result at half exposure.
- A 26,400-segment path using only prices 100 and 200 overflowed accumulated
  equity at segment 24,648 although every individual return was finite.

Impact: the engine could publish a successful audit record containing NaN,
infinity, or an artificial total loss. Normal-magnitude oracle fixtures could
not expose this domain failure.

## Correction and independent reproduction

The accepted return operation order remains unchanged. The engine now raises
`BacktestError` when a computed gross return is nonfinite or `<= -1`, and when
an equity state is nonfinite or nonpositive. It does not clamp a result, widen
a tolerance, or edit the frozen references.

Astra reran all five original probes against the correction; every probe now
raises `BacktestError`. It confirmed that the implementation delta consists
only of the three fail-loud guards and that the tests add the three targeted
regression cases.

## Non-blocking governance correction: T8-ASTRA-NB1

The earlier local report overstated Constitution section 16. The section
requires the exact-oracle/NumPy/production implementation order, but its
enumerated protected-component human-PR list does not include the production
backtester. The report now states the exact rule. This does not grant commit,
push, or Task 9 authorization.

## Open question: T8-ASTRA-Q1

Delayed-fill exposure observation remains unbound. The frozen one-bar shift
and Task 3 volatility cutoff do not decide how a target arriving while a fill
is pending observes exposure or supersedes the pending target. Explicitly
rejecting nonzero delay remains correct for the authorized baseline.

## Astra's corrected-snapshot validation

```text
Focused Task 8 suite: 25 passed, exit 0
Full suite: 845 passed, 4 pre-existing skips, exit 0
Ruff check: passed
Ruff format check: passed
Mypy: 21 source files passed
Import contracts: 4 kept, 0 broken
git diff checks: passed
Frozen audit: 28/28 bytes, 14/14 sidecars, all bindings passed
Accepted Task 6 hashes: 6/6 passed
```

Corrected implementation hashes:

```text
0cac409d20a6dde7f8c99e1ca58f49697ec6acd4eb9d8084c8d9eaa11e4c3ad1  src/aqt/backtest/engine.py
12d5338e57c6aa5c1e21129fb03be1ae8b57b65b7ebf0f37053ad156e100eee3  tests/unit/test_backtest_engine.py
f3f0b9486e5e77e5d1ee79666e35a260d5888aabe126abeddb07d9828323b231  tests/integration/test_production_backtest_comparison.py
```

No blocker remains. Astra's final verdict for the corrected Task 8 baseline is
**PASS**.
