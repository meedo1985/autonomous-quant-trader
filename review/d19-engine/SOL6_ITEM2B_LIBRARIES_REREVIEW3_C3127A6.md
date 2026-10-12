<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a1273c-88ae-7cd3-b51b-bd9c01d36fe9. Tokens used: 17,974. Made from a packet (Codex's command runner fails here): the focused re-review prompt, SOL6_ITEM2B_LIBRARIES_REREVIEW2_5624D3E.md, ADJUDICATION_ITEM2BLR2_5624D3E.md, git diff 5624d3e..c3127a6 -- calibration tests, and the HEAD text of tests/unit/test_calibration_rules.py and calibration/rules.py. -->

# Focused independent re-review: I2BLR2-1 repair

**Reviewer model metadata:** Codex, based on GPT-6 as identified by the session instructions. The exact served model identifier and reasoning effort are not exposed.

**Commit reviewed:** `c3127a6` (`5624d3e..c3127a6`).

**Scope:** The attached I2BLR2-1 review, adjudication, diff, and HEAD text of `tests/unit/test_calibration_rules.py` and `calibration/rules.py`. This review is **from attachments only**.

**Commands run:** None. The command runner is unavailable. The adjudication’s reported test, lint, and type-check results were not independently reproduced.

**Verdict for pilot use: ACCEPT.**

## Assessment

| Question | Assessment |
|---|---|
| **I2BLR2-1 status** | **Resolved.** The revised test compares the path’s own return with three replacements for every day and all 54 rules, with `UP_V_BAR` held fixed. Its docstring limits the claim to those probes on that path. The new witness requires the same check to reject a shifted-path version of each rule at least once. It does not claim to detect every partial look-ahead or a look-ahead on every day. |
| **Are the repaired claims supported?** | **Yes.** `_first_violation` checks prefixes through day `t` for each probe; the witness invokes it separately for every rule. The assertion establishes at least one violation per shifted rule, which is exactly the witness test’s stated requirement. |
| **Is the witness a genuine one-day look-ahead?** | **Yes, for applicable days `t ≥ 1`.** At shifted input position `t−1`, the rule receives original `r_t`. Its day-`t` target can therefore use the return from day `t`. Day 0 has no earlier return slot, and the appended zero only fills the final unused input position for a causal day-239 target. |
| **Did the repair introduce a defect?** | **No defect identified** in the attached diff or its interaction with the attached production code. |

**New findings:** None. No `I2BLR3-*` ID assigned.
