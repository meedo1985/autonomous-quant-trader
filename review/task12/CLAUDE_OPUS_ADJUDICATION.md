# Task 12 Claude review adjudication and follow-up gate

Date: 2026-09-18  
Base reviewed by Claude: `c59447a5d9b4db0c4aaa3c0188a698e88b031300`  
Claude model: `claude-opus-5`, medium effort, read-only  
Follow-up scope: tests and review evidence only; production source and frozen
v1.0 artifacts unchanged

## Adjudication

| ID | Claude severity | Decision | Evidence and disposition |
|---|---|---|---|
| T12C-01 | NON-BLOCKING | PARTIAL | `LOCAL_REPORT.md` is an accurate historical record of its named uncommitted snapshot and should not be rewritten as if produced at HEAD. `git diff b48293e..c59447a -- src tests review/task12` showed no post-Task-12 drift before this follow-up. Current validation is recorded below. |
| T12C-02 | NON-BLOCKING | AGREE | Added `test_real_non_degenerate_interval_regression`, which uses the real block selector, private RNG, 2,000 attempts, and hardcoded block/point/lower/upper anchors for distinct paired series. |
| T12C-03 | NON-BLOCKING | AGREE | The test now compares the recorded value to the exact running `sys.implementation.name` and `sys.version`, preserving the runtime-provenance check across the declared Python range. |
| T12C-04 | NON-BLOCKING | PARTIAL | The weakness is real for a future governed caller, but Task 12 explicitly permits plain finite sequences and no production caller exists. A future authorized integration must bind or validate stream identity; no Task 12 API expansion is authorized here. |
| T12C-05 | NON-BLOCKING | DISAGREE | The code exactly implements the owner-approved `K = max(5, floor(log10(n)))`. An external reference variant cannot silently replace that fixed convention, and no practical Task 12 case is shown to fail. |
| T12C-06 | NON-BLOCKING | AGREE | Added direct rejection cases for a non-midnight boundary and JSON with noncanonical spacing. Both return `INVALID_IDENTITY`. |
| T12C-07 | NON-BLOCKING | AGREE | The repeated equality arm is redundant, but it is behaviorally harmless. Removing it would add production-code churn without improving an acceptance criterion, so it remains unchanged. |
| T12C-08 | QUESTION | AGREE | The below-one fallback is explicitly owner-approved in `IMPLEMENTATION_CONVENTIONS.md`. Whether governed use should retain or clamp it belongs to a future formal binding; Task 12 remains inactive. |
| T12C-09 | QUESTION | AGREE | The percentile construction is exactly the approved inactive primitive. Coverage-method selection for a promotion gate remains a blocked governance decision. |
| T12C-10 | QUESTION | AGREE | The mapping is deliberately deferred in `ASTRA_PROPOSED_STATISTICAL_CONVENTIONS.md`. DSR calibration, Task 13, and promotion remain blocked. |
| T12C-11 | NON-BLOCKING | DISAGREE | `NONFINITE_RESULT` is the approved umbrella for unrepresentable arithmetic, and the exception message already says `unrepresentable daily return`. Adding a new stable code would change an unapproved scientific interface. |
| T12C-12 | QUESTION | PARTIAL | The diagnostic ordering is as described, but no approved precedence rule requires a different code and both cases fail closed. A future reason-code contract may fix precedence; Task 12 source remains unchanged. |

## Follow-up changes

Only `tests/unit/test_statistical_metrics.py` changed:

- added two evaluation-window identity rejection cases;
- made runtime provenance assert the exact current runtime string;
- added a real-RNG, non-degenerate interval regression covering block length,
  point estimate, and both percentile bounds.

Reviewed follow-up test hash:

```text
4bcc1a98ead080c35cebf1da520dff30324c4dba1d0850bf5e5a8315e7a7be3b  tests/unit/test_statistical_metrics.py
```

## Validation

- Focused Task 12 tests: **91 passed**.
- Full suite with an explicit writable `--basetemp`: **1092 passed, 4 skipped**.
- The first full-suite attempt produced 40 setup errors solely because pytest's
  default user-temp directory was inaccessible; 1052 tests passed in that
  attempt. The same suite then passed completely with the explicit base temp.
- Ruff format check: **57 files already formatted**.
- Ruff check: **all checks passed**.
- mypy: **28 source files clean**.
- import-linter: **4 contracts kept, 0 broken**.
- Frozen verification: **28/28 trusted bytes and exact inventory; 14/14
  sidecars; Constitution self-hash; 7/7 manifest and protocol bindings; all
  nested cost, feature, and benchmark bindings passed**.
- Task 6 accepted oracle/canary hashes: **6/6 passed**.
- `git diff --check`: **passed**.

## Gate

No local or Claude blocker remains. The added regressions close T12C-02,
T12C-03, and T12C-06 without changing production behavior.

**LOCAL GATE: PASS. Claude status: ADJUDICATED.**

Task 12 remains inactive. This follow-up does not authorize Task 13, DSR/PBO,
governed trials, confirmation/lockbox access, promotion, exchange connectivity,
or trading.
