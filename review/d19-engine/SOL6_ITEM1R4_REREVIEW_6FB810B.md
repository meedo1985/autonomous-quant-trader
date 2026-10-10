<!-- Recorded verbatim from codex exec (OpenAI Codex v0.160.0) on 2026-10-10. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12626-1407-7a02-9c22-16c1cafe68ae. Tokens used: 34,700. Made from a packet (Codex's command runner fails here): review/d19-engine/ITEM1R4_REREVIEW_PROMPT.md, the previous Sol review, ADJUDICATION_ITEM1R4_C90AA7E.md, git diff c90aa7e..6fb810b -- calibration scripts tests, and the HEAD text of calibration/choices.py, dsr.py, classifier.py, scripts/d19_run.py. -->

# Focused re-review of I1R4 repairs at `6fb810b182e97c5ca7dd57e73aed19cda562dc7e`

## Reviewer, basis, and scope

- **Reviewer:** Independent Codex reviewer, not an authority. This interface identifies me as GPT-6 based; it does not expose an exact model ID or reasoning effort.
- **Commit reviewed:** `6fb810b182e97c5ca7dd57e73aed19cda562dc7e`, as given and not independently verified.
- **Basis:** Supplied attachments only: the prior review, adjudication, diff, and HEAD text of `choices.py`, `dsr.py`, `classifier.py`, and `d19_run.py`.
- **Scope:** The stated checks in `choices.consistent`: record structure, Annex B order, cross-rule and per-column agreement, and values recomputable from stored lengths. I did not assess the numerical correctness of z_f*, S0, the selected trial, or the U_G outcome.

## Commands run

None. The command runner was unavailable. The adjudication’s reported checks were not independently verified.

## Verdict: **FIX for pilot use of the choices report**

**I1R4-1 is closed:** the reported ratio and family-block contradictions are now checked. **I1R4-2 is only partly closed:** the cited key and pair-shape defects are repaired, but the new promise that every malformed record returns a problem is false.

The stated limited scope is acceptable for a pilot consistency check. Chain hashes protect the stored record’s integrity, while replay from the stated seeds is needed to establish the excluded computed outcomes; the consistency check itself does not establish those outcomes.

## Findings

### I1R5-1 — Medium — Equal blocks can yield contradictory rule outcomes

**Location:** `calibration/choices.py:253–264`

**Concrete failure scenario:** Start with an accepted K = 2 record with `T = 9`, column lengths `[3, 3]`, and block `3` under both rules. Keep `largest` available, but set `median.reason` to `INVALID_REPLICATE` and its `z`, `s0`, and nominee to null. The ratio remains `3/9` in both entries. `consistent` accepts this record: neither reason is in `RULE_FREE`, and both derived blocks are correct. The driver cannot write it. With the same input, family seed, classifier result, and block, the two `dsr.evaluate` calls use identical draws and computations, so their outcomes must agree.

**Proposed repair:** When the recomputed family blocks are equal, require the two rule entries to agree. Add this K = 2 case to the tests.

### I1R5-2 — Medium — A fractional `T` is accepted as a driver diagnostic

**Location:** `calibration/choices.py:240–248, 194–213`

**Concrete failure scenario:** Take a K = 2 record with column lengths `[3, 3]`, set diagnostic `T` to `9.5`, both entries to `UNSUPPORTED_LAW`, both ratios to `3/9.5`, and their block, `z`, `s0`, and DSR nominee to null. Keep valid column checks, a top-level nominee of `0`, and `u_g` null. With thresholds for `T = 9`, the classifier refuses and `consistent` accepts the record. `classifier.diagnostics` obtains `T` from the integer row count of `x`, so the driver cannot write `9.5`.

**Proposed repair:** Validate that decoded `T` is a finite positive integer before checking classifier outcomes or derived values. Add a fractional-`T` corruption test.

### I1R5-3 — Medium — A malformed record can raise instead of returning a problem

**Location:** `calibration/choices.py:194–208, 234–237`

**Concrete failure scenario:** Use K = 2, diagnostic `T = 0`, two finite stored lengths of `3`, a capped column, and identical `BLOCK_LENGTH_CAPPED` entries with a present finite ratio and null block, `z`, `s0`, and DSR nominee. Keep valid column checks, top-level nominee `0`, and `u_g` null. The shape, early-rule, and column checks pass. `_derived_problem` then evaluates `3 / 0` and raises `ZeroDivisionError`, which `consistent` does not catch.

**Proposed repair:** Validate `T` before division and make arithmetic failures return a problem through the documented interface. Add a test asserting that this record returns a problem without raising.

## Repair and test assessment

- The new wrong-ratio and wrong-median-block assertions would fail without the I1R4-1 repair.
- The new finite-column `[True, None]`, missing-`u_g`, and extra-entry-key assertions would fail without the I1R4-2 shape repair. The malformed-record loop also contains inputs that raised before the repair.
- The tests do not cover equal-block outcome agreement, fractional `T`, or zero `T`.
- I identified no record the supplied driver can write that the new checks would refuse, based on the attachments.
