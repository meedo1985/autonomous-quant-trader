<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12733-8eea-7fc3-9b43-e2a523e8087e. Tokens used: 31,067. Made from a packet (Codex's command runner fails here): review/d19-engine/ITEM2B_LIBRARIES_REVIEW_PROMPT.md, git diff 0e8de45..161751b -- calibration tests, the HEAD text of calibration/rules.py, tests/unit/test_calibration_rules.py and calibration/semi.py, ITEM2B_RULE_LIBRARY_PROPOSAL.md revision 3, OWNER_DECISION_ITEM2B_RULE_LIBRARIES.md, src/aqt/benchmarks/canonical.py conventions and reaches_rebalance_band, and generator.benchmark_exposure. -->

# Independent review: D-19 engine item 2b rule libraries

**Reviewer model metadata:** Codex, GPT-6 family as identified by the session instructions. The exact served model identifier and reasoning effort are not exposed here.

**Commit reviewed:** `161751b` on `d19-calibration-engine`, parent `0e8de45`.

**Scope:** The attached diff and HEAD text for `calibration/rules.py`, `tests/unit/test_calibration_rules.py`, and `calibration/semi.py`, checked against accepted proposal revision 3, the owner decision, and the attached canonical band and benchmark functions. This review uses **attachments only**.

**Commands run:** None. The command runner is unavailable. The drafter’s reported test, lint, type, import, and frozen-byte results, including the two mutation checks, were not independently reproduced.

**Verdict for pilot use: FIX.** The implementation matches the stated rule equations on the contracted inputs. The causal test does not establish prefix invariance for every rule, and several binding constants and identities lack independent assertions.

## Findings

### I2BL-1 — High — Causal test misses some one-day look-ahead errors

**Location:** `tests/unit/test_calibration_rules.py:39`

**Failure scenario:** The test changes the path at cuts 0, 1, 22, 120, 230, and 319. None is a post-start refresh day for an H = 7 trend rule with enough SMA history. Replacing `price[t - 1]` with `price[t]` only in those rules can therefore pass this test. For vol rules, the 0.10 band can hide a changed target in the held exposure being compared. The reported trend mutation failure shows that *a* trend rule was caught, not every rule.

**Proposed repair:** For each of the 27 rules in each family, compare the direct target at deliberately chosen cuts after changing `r_t`; include an H = 7 trend refresh after its SMA warm-up. Also compare held exposures, but do not rely on band-gated output alone to prove target causality.

### I2BL-2 — Medium — Tests do not pin the accepted index table and constants

**Location:** `tests/unit/test_calibration_rules.py:18`, `tests/unit/test_calibration_rules.py:29`, `tests/unit/test_calibration_rules.py:59`

**Failure scenario:** A different balanced index permutation can pass the balance test while violating R-4. Swapping the 100- and 50-day SMA entries can preserve the asserted rule-0 identity and uniqueness. Changing HAR coefficients while preserving their sum, or changing GARCH coefficients while updating the implementation’s constants, can pass tests whose expected values read those same constants.

**Proposed repair:** Assert the accepted index formula and trial identities against an independent expected table. Pin the SMA, horizon, τ, EWMA, HAR, and GARCH constants explicitly in tests; retain the direct-recursion tests for the calculations.

### I2BL-3 — Low — Required guards are only partly tested

**Location:** `tests/unit/test_calibration_rules.py:50`, `tests/unit/test_calibration_rules.py:114`

**Failure scenario:** Removing the non-finite price-index check at `calibration/rules.py:125` would leave the supplied tests green. The source test covers BTC `-1` and `NaN`, but not an infinite value or a non-finite ETH row. Thus the tests do not prove the guards they describe.

**Proposed repair:** Add a synthetic path whose cumulative price becomes non-finite and assert rejection. Add source cases for infinity and a non-finite second column.

## Equation and integration assessment

R-2 uses `P_{t-1}` and exactly the L prices `P_{t-L}…P_{t-1}`, applies the strict SMA comparison on `t ≡ 0 mod H`, retains the target between refreshes, and sizes with the 7-day EWMA and selected τ. R-3’s EWMA recursion, GARCH recursion and averaged H-day forecast, and HAR 1/5/22 lag windows and forward iteration match revision 3. HAR’s negative-index squared returns are seeded with `v̄`. Sizing returns 1 at `v = 0`; the τ ordering is correct.

For valid paths, each row’s indexed inputs stop at `r_{t-1}`. `held` starts at zero, calls `reaches_rebalance_band` on every daily target, and moves fully when the band is reached. R-4’s implemented index formula, trial identities, and first-K selection match the proposal. `joint` places trend columns before vol columns and passes one path to both; `semi_empirical` applies one sign sequence across all columns. The QJ test supports that composition, while reusing the implementation’s helpers for its expected result.

`reference_variance` computes the specified mean square of the demeaned BTC source, checks source finiteness and `1 + r > 0`, and the trend function rejects a non-finite price index.

**Proposal consistency:** Revision 3 calls `v̄` both a `ddof = 0` population variance and the mean of squares. These are mathematically equal for an exactly zero-mean column, but need not be bitwise equal after floating-point demeaning; the code follows the proposal’s explicit mean-square formula. The proposal header’s “DRAFT” and pending-acceptance wording is stale in light of the attached owner decision. Neither point changes the accepted equations.

**Work not yet built, excluded from this verdict’s findings:** Q5/QJ cell wiring into the run definition and driver, including §8 stream use and server loading from `raw_root`; and per-family test counting and coverage categories.
