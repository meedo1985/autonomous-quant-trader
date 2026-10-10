<!-- Recorded verbatim from codex exec (OpenAI Codex v0.160.0) on 2026-10-10. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12643-a76d-79d1-8540-22ffb8323598. Tokens used: 30,773. A first run of the same packet was killed by Claude Code for low system memory with no output. Made from a packet (Codex's command runner fails here): review/d19-engine/ITEM1R5_REREVIEW_PROMPT.md, the previous Sol review, ADJUDICATION_ITEM1R5_6FB810B.md, git diff 6fb810b..412cd54 -- calibration scripts tests, and the HEAD text of calibration/choices.py, dsr.py, classifier.py, scripts/d19_run.py. -->

# Focused re-review of I1R5 repairs at `412cd5422d96ab149e40da191b9703e2e4f577d8`

## Reviewer, basis, and scope

- **Reviewer:** Independent Codex reviewer, not an authority. This interface identifies me as GPT-6 based; it does not expose an exact model ID or reasoning effort.
- **Commit reviewed:** `412cd5422d96ab149e40da191b9703e2e4f577d8`, as given and not independently verified.
- **Basis:** Supplied attachments only: the previous review, adjudication, diff, and HEAD text of `calibration/choices.py`, `calibration/dsr.py`, `calibration/classifier.py`, and `scripts/d19_run.py`.
- **Scope:** The checks claimed in `choices.consistent`: structure, Annex B order, cross-rule and per-column agreement, and values recomputable from stored lengths. I did not assess the numerical correctness of z_f*, S0, nominee identity, or the U_G gate outcome.

## Commands run

None. The command runner was unavailable. The adjudication’s reported checks were not independently verified.

## Verdict: **FIX for pilot use of the choices report**

**I1R5-1, I1R5-2, and I1R5-3 are closed** against their reported scenarios. Equal derived blocks now require equal entries; fractional or nonpositive `T` is rejected before division; and arithmetic errors are reported as malformed records.

The stated limited scope is acceptable for a pilot consistency check. A chain hash binds the stored bytes, while replay from the §8 seeds is needed to check the excluded computations. The check should not be read as having verified those computations.

Within the stated scope, I found one record that `consistent` accepts but `dev_replication` cannot write. I found no driver-written record that the new checks refuse.

## Findings

### I1R6-1 — Medium — A zero-variance column can coexist with a recorded U_G nominee

**Location:** `calibration/choices.py:119–145, 184–190`; `scripts/d19_run.py:82–92`

**Concrete failure scenario:** Use a K = 1, T = 9 record for a constant finite column: `column_checks` is `[[true, false]]`, `columns` is null, and both rule entries have reason `ZERO_VARIANCE_COLUMN` with their other fields null. Give the diagnostics the driver’s required fields, including the nonfinite tails produced by that constant column. Set the top-level `nominee` to `0` and `u_g` to null. `consistent` accepts the record: rule 2 agrees with the column check, and its shape check permits that nominee and U_G pair. The driver cannot write it. Its `nominee()` computes an observed Sharpe, encounters division by zero, and returns null; it then writes `u_g = "NO_NOMINEE"`.

This checks whether nomination is possible from an already recorded rule 2 failure; it does not require recomputing *which* trial would win.

**Proposed repair:** For `ZERO_VARIANCE_COLUMN`, require a null top-level nominee and `u_g = "NO_NOMINEE"`. Add the altered constant-column record as a regression test.

### I1R6-2 — Low — The new T tests do not detect the T repairs

**Location:** `tests/unit/test_calibration_choices.py:329–332`

**Concrete failure scenario:** Revert only the positive-integer `T` check. Each new T test still starts from an available result. Changing T makes `classifier.within` refuse, so `_entry_problem` reports a classifier mismatch before the derived ratio is evaluated. Even the T = 0 case passes its assertion without testing the former division-by-zero path. Reverting only the new `ArithmeticError` catch likewise leaves these tests passing. The equal-block test does detect removal of the I1R5-1 repair.

**Proposed repair:** Test fractional T with otherwise coherent `UNSUPPORTED_LAW` entries and a ratio calculated from the fractional T. Test T = 0 with otherwise coherent refusal entries so the old code reaches `_derived_problem`, and assert that `consistent` returns a problem without raising.
