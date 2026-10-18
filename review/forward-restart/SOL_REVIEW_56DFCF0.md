<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-18. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a14fad-917e-7692-a4f7-c1bd3d17ac5a. Tokens used: 19,260. Packet built from restart-wait-proposal 56dfcf0 (git show only): prompt SOL_REVIEW_PROMPT.md, PROPOSAL.md, review/task33/SERVER_EVIDENCE.md (main), scripts/run_forward_paper.py, src/aqt/app/forward.py lines 100-185, deploy/aqt-paper.service. -->

# Sol review of the F-RESTART proposal at 56dfcf0

## Review (final message, verbatim)

**Verdict: FIX.** The diagnosis fits the two refused restarts: the first step used the newest bar’s close as its scheduled time, and the recorded lags exceeded the 300-second limit. The proposed wait does not change that limit or the replay code, but the timing claim and trade-offs need correction before approval.

- **FR-1 — Starts before :01 are still exposed.** The proposal runs a step immediately from :00 through :04. A restart at :00 can fetch before the newly closed bar is available, leaving the previous hour as the newest bar and causing another lag refusal when hours are pending. The existing `STEP_OFFSET` schedules :01 for a reason. Define what happens before :01; “a restart works at any minute” is not established.

- **FR-2 — :04 has an unproven safety margin.** :04 leaves **60 seconds** before the five-minute limit, or about 55 seconds allowing for the permitted five-second clock skew. `step()` captures `now` **before** fetching, and `observation()` later uses that captured time. A slow fetch can therefore make the check pass using an age measured before the fetch, even if the bar is over five minutes old when the check runs. The proposal needs a bound on fetch and scheduling delay, or a freshness check using the time at evaluation.

- **FR-3 — The delayed-check description is inaccurate.** Deployment approval and Telegram channel setup occur before the proposed wait; the alert-test and other checks reached through `run_step()` occur afterward. During a wait of nearly 57 minutes, systemd can show the service as running while no step or startup refusal has occurred. State precisely which checks are delayed and when the owner will see a refusal.

- **FR-4 — Reported values and the replay window can change.** The replay and `LOOP_LAG` rules remain the same, but waiting fetches a later bar. The eventual step may cover another hour, report a higher missed-hour count, and emit the report later. The proposal should distinguish unchanged rules from changed outcomes.

A revised proposal can keep the small scheduling change, but should specify the pre-:01 case, justify or revise the :04 cutoff using actual check timing, and state the visibility and reporting effects plainly.

## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-18)

| ID | Decision | Change to the proposal |
|---|---|---|
| FR-1 | Agree | No cut-off: the service always waits for the next :01 slot, so a start before :01 waits for it too. |
| FR-2 | Agree | With no cut-off, the first step has the same freshness margin as every hourly step. The pre-fetch `now` is recorded as a residual that predates the change; not proposed now. |
| FR-3 | Agree | The checks before the wait (deployment, Telegram set-up) and after it (everything through `run_step`, including the alert test) are named; the misleading "active (running)" during the wait is stated, with what the owner checks. |
| FR-4 | Agree | Unchanged rules and changed outcomes are listed separately. |

No finding is left unrepaired.
