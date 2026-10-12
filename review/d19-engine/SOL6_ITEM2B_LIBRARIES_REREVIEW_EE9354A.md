<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12736-bb02-7c90-8398-80de6398b3da. Tokens used: 21,831. Made from a packet (Codex's command runner fails here): the focused re-review prompt, SOL6_ITEM2B_LIBRARIES_REVIEW_161751B.md, ADJUDICATION_ITEM2BL_161751B.md, git diff 161751b..ee9354a -- calibration tests, and the HEAD text of tests/unit/test_calibration_rules.py and calibration/rules.py. -->

# Focused independent re-review: D-19 item 2b rule-library repairs

**Reviewer model metadata:** Codex, based on GPT-6 as identified by the session instructions. The exact served model identifier and reasoning effort are not exposed.

**Commit reviewed:** `ee9354a` (`161751b..ee9354a`).

**Scope:** The attached earlier review, adjudication, diff, and HEAD text of `tests/unit/test_calibration_rules.py` and `calibration/rules.py`. This review uses **attachments only**. The accepted proposal itself was not attached.

**Commands run:** None. The command runner is unavailable; the adjudication’s reported checks and mutation result were not independently reproduced.

**Verdict for pilot use: FIX.** The guards and independent expected values address I2BL-2 and I2BL-3. The causal test improves I2BL-1 but does not establish its claimed coverage of a one-day look-ahead in any single rule at any target day. No defect in the changed production code is apparent from the attachments.

## Status of earlier findings

| ID | Status | Assessment |
|---|---|---|
| I2BL-1 | **Partially resolved** | The new test compares direct targets for all 27 indices in each family and includes the previously missing post-warm-up H = 7 refreshes. Its selected cuts still leave target days untested; see I2BLR-1. |
| I2BL-2 | **Resolved within the attached scope** | `ORDER`, `TAU`, `HOURS`, and the expected trial names are literal test values, rather than values read from `calibration.rules`. The test also pins the listed constants. The unattached proposal prevents independent verification of the table’s provenance. |
| I2BL-3 | **Resolved** | The added cases cover non-finite values in both source columns and an overflowing price index. The `np.errstate(over="ignore")` change is followed immediately by a finiteness check; no introduced production defect is evident. |

## New finding

### I2BLR-1 — High — The causal test leaves target days untested

**Location:** `tests/unit/test_calibration_rules.py:104–130`

**Failure scenario:** Trend rule `i = 6` has `(m, s, k) = (0, 2, 1)`, so its 200-day SMA refreshes every seven days. The new test checks its targets at days 203 and 210, but does not change `r_217` when checking target 217. A one-day look-ahead confined to that rule’s target at its day-217 refresh can pass the new test. The older held-exposure test also does not perturb `r_217` while comparing row 217: its cuts before 217 compare only earlier prefixes, and its later cuts leave `r_217` intact.

The three values used at a *tested* cut do not turn a finite set of cuts into a guarantee for every target day. Target equality can also mask a look-ahead when the trend signal is zero or sizing produces the same value.

**Required repair:** Check direct target causality at every decision day for each rule on the synthetic path, or narrow the test’s claim and supply other evidence that covers the omitted days. Keep the direct-target comparison, since the rebalance band can mask a target change.

**Implementation assessment:** This is a remaining verification gap, not evidence that `calibration/rules.py` currently reads a future return.
