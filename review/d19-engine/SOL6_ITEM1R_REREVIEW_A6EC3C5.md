<!-- Recorded verbatim from codex exec (OpenAI Codex v0.160.0) on 2026-10-10. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a125f2-85e6-72d2-8678-7846aeae26dc. Tokens used: 30,942. Codex's command runner fails in this environment, so the review was made from a packet: review/d19-engine/ITEM1R_REREVIEW_PROMPT.md, the previous Sol review and ADJUDICATION_ITEM1R_580ACFE.md, git diff 580acfe..a6ec3c5 -- calibration scripts tests, and the HEAD text of calibration/choices.py, scripts/d19_choose.py, scripts/d19_run.py, calibration/dsr.py. -->

# D-19 engine item 1 repair re-review at `a6ec3c5`

## Reviewer and scope

- **Reviewer:** Codex independent review; not an authority. The interface identifies this assistant as GPT-6 based. It does not expose an exact model ID or reasoning effort.
- **Commit reviewed:** `a6ec3c5ed4f307c127ef25999ff8191f5c1a6d96`, as given in the prompt; not independently verified.
- **Scope:** The attached prior review, adjudication, diff, tests, and full text of `calibration/choices.py`, `scripts/d19_choose.py`, `scripts/d19_run.py`, and `calibration/dsr.py`. This review used **attachments only**.

## Commands run

None. The command runner was unavailable. I did not run tests, inspect other repository files, or verify the adjudication’s reported results.

## Verdict: **FIX for pilot use of the choices report**

The cause-code lists match every return path shown in `dsr.evaluate`, and the K = 1, margin-failure, and pilot-label repairs are present. Two remaining problems prevent the chooser’s consistency check and per-column checks from supporting their stated claims.

## Disposition of I1R-1 through I1R-5

| Prior finding | Disposition |
|---|---|
| I1R-1 | **Partially closed.** `BEFORE_CLASSIFIER` contains all four returns before the classifier; `AFTER_CLASSIFIER` contains both returns after it. `UNSUPPORTED_LAW` and available results are placed correctly. Finite `z`, `s0`, and `block` are required for availability. Other impossible records still pass; see I1R2-1. |
| I1R-2 | **Closed by inspection.** `dev_replication` reuses the result at K = 1, and `consistent` requires equal rule entries. |
| I1R-3 | **Partially closed.** `column_checks` records per-column predicates, and on finite input its variance expression uses the same `std(ddof=1) != 0` test as `dsr.evaluate`. Its result for a non-finite column misstates rule 2; see I1R2-2. |
| I1R-4 | **Closed by inspection.** A close margin sets `status` to `margin_failed` and `qualifies_before_coverage` to false. The script writes that report, prints a failure message instead of the `z_crit` success line, and returns 3. The report still contains provisional cell statuses and thresholds, so consumers must honor its top-level status. |
| I1R-5 | **Closed by inspection.** Pilot reports carry `measurement_only` text saying that statuses, `z_crit`, and final thresholds are not qualification decisions and directing readers to event counts. The approximate 7,700 count was not independently checked from the attachments. |

## Findings

### I1R2-1 — Medium — Impossible DSR outcomes pass `consistent`

**Location:** `calibration/choices.py:94–108`

**Failure scenario:** For an accepted K = 2 record, set both rule entries to `reason=None`, finite encoded `z`, `s0`, and `block`, and `nominee=None`; set the record’s `nominee=None` too. `consistent` returns `None`. An available `dsr.evaluate` result always chooses an integer nominee in `range(k)` at line 183, so `dev_replication` cannot produce that outcome. Likewise, a pre-classifier cause code with a non-null `z` passes because line 95 skips all other entry checks, although those `dsr.evaluate` returns have `z=None`. A chain hash cannot establish these outcome invariants.

**Proposed repair:** Check the fields implied by each `dsr.evaluate` return, including a valid integer nominee for availability and the null or populated fields appropriate to each refusal. Keep the current cause-code ordering and K = 1 equality check. Add corruption tests based on otherwise valid records.

### I1R2-2 — Medium — `column_checks` reports rule 2 as passed for a non-finite column

**Location:** `scripts/d19_run.py:114–118`; compare `calibration/dsr.py:131–135`

**Failure scenario:** For a column containing NaN, `np.isfinite(c).all()` is false, while `c.std(ddof=1)` is NaN and `NaN != 0` is true. The stored check is therefore `[False, True]`. `dsr.evaluate` returns `INVALID_SERIES` at rule 1 and never evaluates rule 2. Treating the second boolean as a rule 2 outcome overstates what ran and can distort per-column failure rates.

**Proposed repair:** Define the second field as an independent raw variance predicate or as the Annex B rule 2 outcome. For the latter, record “not evaluated” when rule 1 stops the family; for the former, do not record a non-finite column as passing variance. Test a non-finite column and compare the recorded semantics with the `dsr.evaluate` return order.

## Test assessment and limits

The new K = 1 test demonstrates the equality check, and the script-level margin test demonstrates exit 3, the written failure status, and suppression of the success line. The `consistent` test exercises every listed cause code, but its classifier is mocked and its NaN case is a **NaN `z`**, not a NaN diagnostic; it does not prove the adjudication’s diagnostic-refusal claim. The end-to-end test checks that `column_checks` exists, not its values or rule-order meaning. These observations are from test text only; the reported passing test and lint results were not independently run.
