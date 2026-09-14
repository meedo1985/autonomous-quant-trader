# Task 8 Fable 5.1 adjudication

Date: 2026-09-14
Reviewer verdict: PASS
Final local gate: PASS

| ID | Claude severity | Decision | Reason and disposition | Validation |
|---|---|---|---|---|
| T8-NB-1 | NON-BLOCKING | AGREE | Terminal equity alone cannot prove intra-segment ordering. The authorized evidence separately requires direct tests and matrix comparison; `test_cost_is_charged_before_return_with_fee_source_and_stress` pins both intra-segment states, while the matrix covers all accepted paths. No extra tolerance or duplicate test was added. | Focused 22 passed; full 842 passed, 4 documented skips. |
| T8-NB-2 | NON-BLOCKING | PARTIAL | Fail-loud behavior is correct, but no triggering input was demonstrated. A deterministic local probe checked `nextafter(1, 0)` across powers and 3,999 positive-return ratios and found no out-of-range result. The domain guard remains authoritative; no clamp or unbound numeric policy was added. | Probe printed `drift_outside None`; existing invalid-state guards and full suite passed. |
| T8-NB-3 | NON-BLOCKING | AGREE | Whole-series continuity is intentional under the approved no-silent-slicing rule. It rejects an invalid supplied dataset and does not feed future values into a segment. No change. | Direct causal sigma regression plus complete matrix passed. |
| T8-NB-4 | NON-BLOCKING | AGREE | Boolean stress is an avoidable public-API inconsistency. The engine now rejects it before cost calculation and a regression pins the error. | Focused 22 passed; Ruff/mypy/import contracts passed; full 842 passed. |
| T8-Q-1 | QUESTION | AGREE | Frozen sources do not bind exposure state while a fill is pending. Nonzero delay remains explicitly rejected, as authorized. The future owner decision must choose pre-fill, pending-target, or post-fill observation and supersession behavior. | Existing delay rejection test passed; frozen audit 28/28 and Task 6 hashes 6/6 passed. |

Post-review implementation hashes:

```text
2451154a15aa42783f5e2992bde6115d6dcaa7c02894e6e220f1fddaddf67fb8  src/aqt/backtest/engine.py
2445283bc561747636d59c9b7d6f8feff15683138b2b54506e8cad5939512874  tests/unit/test_backtest_engine.py
f3f0b9486e5e77e5d1ee79666e35a260d5888aabe126abeddb07d9828323b231  tests/integration/test_production_backtest_comparison.py
```

No blocker remains. No architecture, scientific threshold, frozen artifact,
oracle/reference, or Task 9 change was made.
