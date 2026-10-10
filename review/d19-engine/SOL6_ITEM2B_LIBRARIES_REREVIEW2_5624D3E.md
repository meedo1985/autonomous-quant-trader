<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12739-ed3f-7903-b7f0-e5fadb2ebd76. Tokens used: 30,498. Made from a packet (Codex's command runner fails here): the focused re-review prompt, SOL6_ITEM2B_LIBRARIES_REREVIEW_EE9354A.md, ADJUDICATION_ITEM2BLR_EE9354A.md, git diff ee9354a..5624d3e -- calibration tests, and the HEAD text of tests/unit/test_calibration_rules.py and calibration/rules.py. -->

# Focused independent re-review: I2BLR-1 repair

**Reviewer model metadata:** Codex, based on GPT-6 as identified by the session instructions. The exact served model identifier and reasoning effort are not exposed.

**Commit reviewed:** `5624d3e` (`ee9354a..5624d3e`).

**Scope:** The attached earlier review, adjudication, diff, and HEAD text of `tests/unit/test_calibration_rules.py` and `calibration/rules.py`. This review is **from attachments only**.

**Commands run:** None. The command runner is unavailable. The adjudication’s test results and mutation check were not independently reproduced.

**Verdict for pilot use: FIX.** The repair checks every rule on every day of the 240-day path, closing the omitted-day coverage gap. It does not establish the stronger claim that *any* one-day look-ahead in a single rule’s target, on *any* day, must fail.

## Answers and finding status

| Question or ID | Assessment |
|---|---|
| **I2BLR-1 and I2BL-1** | **Partially resolved.** Every day now receives a direct-target comparison, including day 217 for rule 6. The attached mutation result supports detection of that particular defect. Universal detection is unproved because the test compares only three replacement values, and a future return read at day `t` can produce the same target for all three. |
| **Non-vacuity assertion** | **No, it does not support the universal claim.** It checks whether a changed return affects *some later target* on at least 95% of days per rule. It does not establish that the target **on the same day** is sensitive to a one-day look-ahead. It also permits days with no later change, including the final day. |

## New finding

### I2BLR2-1 — High — Later-target sensitivity does not establish same-day look-ahead detection

**Location:** `tests/unit/test_calibration_rules.py:110–132`

**Evidence:** The causal assertion compares outputs through day `t` after replacing `r_t` with `+0.6`, `−0.6`, and `0`. The non-vacuity counter instead compares `out[t + 1:]`, then applies a 95% aggregate threshold. A return can visibly affect later targets while a look-ahead read in target `t` is masked by the trend signal, sizing saturation, or equal outcomes for the three probes. The assertion provides no per-day witness for the claimed detection. The unmodified `UP[t]` is also absent from the comparison.

**Required repair:** Narrow the claim to what the test demonstrates, or add evidence for the intended defect class at each applicable decision day. A per-day detection claim needs same-day sensitivity or a targeted mutation check; later-target sensitivity alone cannot supply it.

**Implementation assessment:** This is a verification finding. The attached production code shows lagged return reads in the relevant calculations, and the repair changes only the test file.
