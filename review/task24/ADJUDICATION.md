# Task 24 review adjudication

## Claude Fable 5.1 review of `646d514`

Record: `FABLE_REVIEW_646D514.md` (committed `da2c532` before these repairs).
Owner answers: `OWNER_ANSWERS_2026-09-28.md`. Repairs by Claude Opus 5.5.

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| F24-1 | AGREE — BLOCKER, repaired on owner answer | The owner chose "My HALT wins". `safety.py` maps `(HALT, LOSS_STOP)` to HALT; the loop fires LOSS_STOP only in RUNNING. A breach first seen in HALT or FLATTEN leaves the latch armed, so if the owner later resumes RUNNING while still below the line, the stop fires then — that is "trading normally". | `test_the_loss_stop_never_overrides_an_owner_halt` (the reviewer's scenario: owner FLATTEN then HALT in the fall; no HALT -> FLATTEN) and the updated unit test; both fail on `646d514`. |
| F24-2 | AGREE — repaired | `FROZEN_MANIFEST_SHA256` pins `FROZEN_HASHES.json` in code; the per-file checks read that manifest, so rewriting a frozen file with its sidecar and manifest entry is refused. The Constitution's content hash is read from the pinned manifest. | `test_rewriting_a_frozen_file_and_its_hashes_is_still_refused` (the reviewer's scenario); fails on `646d514`. |
| F24-3 | AGREE — disclosed as a paper-only limit | Each paper run is a fresh simulated account, so its incident log, refuse marker, `peak` and `controller.sent` are per run. Before any stage that continues an account (shadow or later), they must be scoped per account and persisted. Recorded as T24-08 in `LOCAL_REPORT.md`. | Documentation. |
| F24-4 | OWNER DECIDED — no change | The owner chose "Pause only": a breach hour places nothing and skips the L-03 check and FLATTEN step; the next good hour checks again. | Existing `test_a_health_breach_blocks_orders_for_that_hour`. |

The repairs have not been re-reviewed.
