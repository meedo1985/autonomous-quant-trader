<!-- Recorded verbatim from codex exec (OpenAI Codex v0.160.0) on 2026-10-10. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a125de-82f3-7b20-b548-efdc49dc94f6. Tokens used: 59,089. Codex's command runner failed in this environment ("Failed to create unified exec process: helper_unknown_error: setup refresh had errors"); an earlier attempt (session 01a125db-e9cf-76f0-be25-920bf3e3d8ea) gave no review for that reason. This review was made from a self-contained packet: review/d19-engine/ITEM1_REREVIEW_PROMPT.md plus the Fable review, the adjudication, the item-1 notes, git diff 2b44fed..580acfe -- calibration scripts tests, the full HEAD text of calibration/choices.py, dsr.py, reduce.py, classifier.py, scripts/d19_choose.py, scripts/d19_run.py, and the accepted preregistration text (docs/d19-recommendation). -->

# D-19 engine item 1 repair re-review at `580acfe8`

## Reviewer and scope

- **Reviewer:** Codex independent review. The interface identifies this assistant as GPT-6 based; it does not expose an exact model ID or effort setting. This review is not an authority.
- **Implementer:** Claude Opus 5.5, as stated in the attached adjudication.
- **Commit reviewed:** `580acfe8cb88cf64589e589b77341018dfecaa8f`, **as supplied in the prompt; not independently verified**.
- **Scope:** The attached first review, adjudication, development record, accepted preregistration, diff, and files at HEAD. This review used **attachments only**.

## Commands and results

| Command | Result |
|---|---|
| `git rev-parse HEAD` | Not run; command runner unavailable. |
| `git diff 2b44fed HEAD -- calibration scripts tests` | Not run; reviewed the supplied diff. |
| Fast unit tests, lint, type and import checks | Not run. The adjudication reports passing checks, but I could not verify them. |

No files or git state were changed. No network access or calibration run was made.

## Verdict: **FIX for pilot use of the choices report**

The replication and recording repairs appear suitable for a **measurement-only re-pilot** by inspection. The choices report still accepts some internally impossible development records, and its margin-failure report can display qualification fields as though a choice succeeded. Repair these before treating a pilot choices report as a validated selection result. This verdict does not authorize a full development run.

## Disposition of the original findings

| Finding | Re-review disposition |
|---|---|
| I1-1 | The rewritten test reaches an available `z` for each parametrized cell and checks accepted and refused classifier paths. It compares both rule records with `dsr.evaluate`. The column values themselves are checked only for presence and count. |
| I1-2 | `block`, `s0`, nominees and column lengths/cap flags are recorded. Per-column **failure** attribution remains incomplete for failures before lengths are computed; see I1R-3. |
| I1-3 | Verified threshold chains are pooled again; heads and a deterministic hash of the pooled bounds enter the report. `consistent` does not enforce all outcomes implied by those bounds or by K = 1 reuse; see I1R-1 and I1R-2. |
| I1-4 | The literal law guard fails closed for laws outside its five-name list. The attachments do not include the full manifest or `Cell` encoding, so I cannot verify coverage of every eventual Q1–Q4 law from inspection. |
| I1-5 | `anchor` and `prereg` are separate arguments; the family seed receives `prereg`. |
| I1-6 | The decisive cap, DSR and attempted `U_G` comparisons record margins. For qualifying cells, both counts bordering the error limit are checked. Exit 3 is fail closed **if the caller checks the exit code**; the written report needs clearer failure status (I1R-4). |
| I1-7 | The measurement-only pilot interpretation is recorded in the adjudication, but the choices report does not state it; see I1R-5. |
| I1-8 | Timing the second rule and any preregistration change remain owner matters. No code change was required by the adjudication. |

`dsr.evaluate` sets `columns` on every return after `pairs` exists, including unavailable lengths, capping, classifier refusal, bootstrap failures and success. The same input computes `pairs` before either block rule is applied, so the field is rule independent. The added conversion and field do not appear to change the existing reason, nominee or `z` decisions.

`dev_replication` stores its floating results as binary64 hex, uses the preregistration hash for the family seed, and reuses the K = 1 rule result. These conclusions are by inspection; bit identity was not executed here.

## Findings

### I1R-1 — Medium — `consistent` accepts impossible availability and post-classifier records

**Location:** `calibration/choices.py:65–82`; consumed at `scripts/d19_choose.py:70–75`.

**Failure scenario:** A record with diagnostics outside the pooled bounds and `reason="INVALID_REPLICATE"` passes `consistent`, although the classifier must return `UNSUPPORTED_LAW` before rule 5 can run. Separately, a record with diagnostics inside the bounds, `reason=None`, `z=None`, and matching null nominees passes. `development` then counts it as DSR available, while `_passes` counts no error event. Either record can be present in an otherwise valid hash chain; chain verification establishes integrity, not that the stored outcome follows the algorithm. NaN diagnostics have the same classifier refusal implication when rules 1–4 did not stop first.

**Proposed repair:** Validate reason-specific invariants in sequence. Permit rules 1–4 reasons before the classifier; require `UNSUPPORTED_LAW` when the classifier refuses after those rules; permit post-classifier reasons only when it accepts. For `reason=None`, require a finite stored `z`, a valid nominee and the fields produced by an available evaluation. Add synthetic records for each pre- and post-classifier reason, including a non-finite diagnostic.

### I1R-2 — Medium — K = 1 shared-rule invariant is not checked by the chooser

**Location:** `calibration/choices.py:71–82`; `scripts/d19_choose.py:67–75`.

**Failure scenario:** At K = 1, a development record can give `largest` and `median` different reasons or `z` values while each entry separately passes `consistent`. `choose` can then select a rule from data that `dev_replication` cannot produce, because it reuses the same result object for both rules at `scripts/d19_run.py:111–114`.

**Proposed repair:** In `development`, require the two stored rule entries to be identical for K = 1 before constructing `Rep` objects. Add a chooser test with a differing K = 1 rule record.

### I1R-3 — Medium — per-column failure rates cannot be reconstructed for early failures

**Location:** `calibration/dsr.py:132–146`; `scripts/d19_run.py:110,124–125`.

**Failure scenario:** If one column has zero variance, `evaluate` returns `ZERO_VARIANCE_COLUMN` before computing `pairs`; the development record has `columns=None`. The record does not identify which column failed. The same limitation applies to an invalid series. Thus the new field supports per-column block-length and cap analysis after lengths are attempted, but does not by itself support §9’s unqualified “failure rates per column.”

**Proposed repair:** Define which per-column failures §9 requires. Record the failing column indicators for the included early checks, or obtain those rates from a separately specified source. Keep whole-family reason precedence unchanged.

### I1R-4 — Medium — margin failure writes a report that can read as a passing choice

**Location:** `scripts/d19_choose.py:117–131`; `calibration/choices.py:199–208`.

**Failure scenario:** With a comparison inside `MARGIN_MIN`, the script writes `z_crit`, `qualifies_before_coverage: true` and `final_thresholds`, then prints the normal `z_crit` line before returning exit 3. A person or consumer reading the JSON without retaining the process exit code can take those fields as an accepted choice despite `margin_ok: false`.

**Proposed repair:** Put an explicit failed or pending status and reason in the JSON, and suppress the success-style console line on exit 3. Test the script-level exit code and written report for a forced close-margin case. The existing test changes `MARGIN_MIN` inside `choices.choose`; it does not test this script behavior.

### I1R-5 — Low — pilot-only interpretation is absent from the report

**Location:** `scripts/d19_choose.py:111–127`.

**Failure scenario:** With a small pilot and zero capped events, the cap UCB still demotes every cell. The JSON says `demoted_cap` and has no `z_crit`, without saying that the pilot size cannot exercise the qualification choices. The adjudication promises that the pilot report will state this limitation; the supplied change does not implement it.

**Proposed repair:** Mark pilot-sized reports as measurement-only and state that their demotion statuses are not qualification decisions. Retain the event counts for rate inspection.

## Test assessment and limits

The rewritten independent-development test usefully checks stored rule fields against direct `dsr.evaluate` calls on both cells, with classifier acceptance and refusal forced. It checks that `columns` exists and has the expected length, but not its values or cap flags. The new `consistent` test mocks `classifier.within` and exercises three reasons; it does not cover I1R-1 or K = 1 disagreement. The margin test proves that changing the threshold can flip `margin_ok`, but not that each comparison or exit 3 is covered.

The attachments do not expose the complete manifest, chain implementation, binomial implementation or test output from this reviewer’s runtime. Conclusions about their integration and the adjudication’s reported test results remain limited to inspection.
