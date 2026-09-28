# Task 24 review adjudication

## Claude Fable 5.1 review of `646d514`

Record: `FABLE_REVIEW_646D514.md` (committed `da2c532` before these repairs).
Owner answers: `OWNER_ANSWERS_2026-09-28.md`. Repairs by Claude Opus 5.5.

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| F24-1 | AGREE — BLOCKER, repaired on owner answer | The owner chose "My HALT wins". `safety.py` maps `(HALT, LOSS_STOP)` to HALT; the loop fires LOSS_STOP only in RUNNING. (Corrected after F24R-3: a run has no HALT exit, so resuming RUNNING below the line cannot happen inside `run_paper`; see T24-08.) | `test_the_loss_stop_never_overrides_an_owner_halt` (the reviewer's scenario: owner FLATTEN then HALT in the fall; no HALT -> FLATTEN) and the updated unit test; both fail on `646d514`. |
| F24-2 | AGREE — repaired | `FROZEN_MANIFEST_SHA256` pins `FROZEN_HASHES.json` in code; the per-file checks read that manifest, so rewriting a frozen file with its sidecar and manifest entry is refused. The Constitution's content hash is read from the pinned manifest. | `test_rewriting_a_frozen_file_and_its_hashes_is_still_refused` (the reviewer's scenario); fails on `646d514`. |
| F24-3 | AGREE — disclosed as a paper-only limit | Each paper run is a fresh simulated account, so its incident log, refuse marker, `peak` and `controller.sent` are per run. Before any stage that continues an account (shadow or later), they must be scoped per account and persisted. Recorded as T24-08 in `LOCAL_REPORT.md`. | Documentation. |
| F24-4 | OWNER DECIDED — no change | The owner chose "Pause only": a breach hour places nothing and skips the L-03 check and FLATTEN step; the next good hour checks again. | Existing `test_a_health_breach_blocks_orders_for_that_hour`. |

These repairs were re-reviewed; see below.

## Claude Fable 5.1 re-review of `2dc79ae`

Record: `FABLE_REREVIEW_2DC79AE.md` (committed `e206675` before these
repairs). F24-1 and F24-2 repairs judged correct; F24-3 correct as a
disclosure; F24-4 consistent with the owner's answer. Verdict FIX.

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| F24R-1 | AGREE — BLOCKER, repaired | The F24-1 repair also silenced the breach after an owner HALT, contradicting deployment draft section 5 ("Must alert CRITICAL: … any `L-03` breach") and the Effect record. The loop now fires LOSS_STOP in any mode except FREEZE (latch still once per fall): from RUNNING it sells (S-4); in HALT it stays HALT with an incident and a CRITICAL alert; during an owner FLATTEN it alerts and the FLATTEN goes on. This follows the owner's answers: HALT wins, and he decides with the breach in front of him. | `test_a_loss_stop_breach_after_an_owner_halt_alerts_but_sells_nothing` (reviewer's scenario); fails on `2dc79ae`. |
| F24R-2 | AGREE — repaired | `ZERO_FILL_ALERT_AFTER` docstring now says owner-set, alert only. | Inspection. |
| F24R-3 | AGREE — corrected | The unreachable sentence in the F24-1 row is corrected. The override and latch rules for a continuing account are added to T24-08 as an open decision. | Documentation. |

The F24R repairs have not been re-reviewed.
