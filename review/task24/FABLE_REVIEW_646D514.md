# Task 24 adversarial review of `646d514` (Claude Fable 5.1)

Date: 2026-09-28

- Reviewer model: Claude Fable 5.1 (`claude-fable-5-1`), a read-only Claude
  Code subagent, requested by the owner ("yes run the Fable review") as a
  substitute for the exact GPT-6 Astra review while Codex is at its limit.
- Implementation: Claude Opus 5.5.
- Reviewed commit: `646d5148074363cb996a20a11504d57ab474d9e9`
  (`task24-paper-loop-v2`, draft PR #30), `git diff c84a5e2 646d514`.
- Reviewer's tests: `test_safety.py` and `test_paper_loop.py`, 79 passed in
  277.64s. Probe scripts in the session scratchpad, deleted afterwards.

## F24-1 — BLOCKER — the automatic L-03 stop overrides an owner HALT and resumes selling

`safety.py:121` maps `(HALT, LOSS_STOP) -> FLATTEN`; `paper_loop.py:567-576`
fires LOSS_STOP in RUNNING or HALT while the latch is armed; the latch is
disarmed only when the stop fires, so a breach first seen in FLATTEN leaves it
armed. Reproduced with `_config(12)`, `_crash_series(24*22, crash_at=24*12)`,
owner FLATTEN at 2020-01-13T21:00 and owner HALT at 22:00:

```
21:00 RUNNING -> FLATTEN OWNER_FLATTEN
22:00 FLATTEN -> HALT   OWNER_HALT
22:00 HALT -> FLATTEN   LOSS_STOP
2020-01-14T07:00 FLATTEN -> HALT FLATTEN_DONE
orders_sent 11 final HALT BTC 0.00106
```

A second probe (owner HALT on day 2, then the crash) also went HALT ->
FLATTEN and made 10 sells. The owner's Task 23 answers (Q1 "HALT … places no
new orders at all … waits for you"; Q2 "any alarm during FLATTEN … stops
selling and goes to HALT") conflict; the S-4 question asked only "When the
20% loss stop fires, what should the system do?" and never put the
owner-HALT case. "From RUNNING or HALT" appears only in the AI-written
Effect section — the same authority defect class as T23-C1. Repair pending
an owner decision: `(HALT, LOSS_STOP) -> HALT` (S-4 from RUNNING only) or
ask the owner explicitly; separately decide whether a breach seen during
FLATTEN disarms the latch.

## F24-2 — NON-BLOCKING — frozen-hash check trusts `FROZEN_HASHES.json` without checking its integrity

`paper_loop.py:283-308` compares each file to the manifest and its sidecar
but never checks `FROZEN_HASHES.json` against `FROZEN_HASHES.json.sha256`
(`verify_frozen.ps1` checks every sidecar against a fixed baseline).
Reproduced on a temp copy: edit `protocol_v1.yaml`, update its sidecar and
`protocol_file_sha256` → `frozen_hash_problems` returns `[]`, while the
manifest's own sidecar no longer matches. Repair: check the manifest and
Constitution sidecars; better, pin expected values outside the checked files
(relates to T24-03).

## F24-3 — NON-BLOCKING — incident log and refuse marker are per `run_id`

`scripts/run_paper_trading.py:39-50` puts `incidents.jsonl` (and so the
marker, `paper_loop.py:720-723`) under `out/<run_id>/`. A new `run_id`
starts RUNNING without seeing a previous run's open incident or marker. Not
executed; code reading. Not a blocker: each paper run is a fresh simulated
account. `peak` and `controller.sent` are likewise not persisted (T23-09),
moot on the simulator, required before any stage continuing an account.
Repair: scope per account/deployment, or record as a paper-only limit.

## F24-4 — QUESTION — health-breach hours also skip the L-03 check and FLATTEN

`paper_loop.py:546-555` `continue`s before the loss-stop check and the
FLATTEN tick. With a live feed, a breach during a fall means no L-03 and no
owner FLATTEN sell while it lasts; the controller stays RUNNING though it
places no orders. Defensible (prices untrusted; S-5 "blocking trading"), but
§14 says risk reductions are immediate and the owner was not asked. Not
reproducible on the bar clock. Suggest: ask the owner; at minimum enter a
protective mode (HALT) during a breach.

## Checked and sound

No order without authorization or outside RUNNING except FLATTEN steps;
`settle_flatten` pops only resolved ids of a passed report and the loop
queries every FLATTEN id; failed check keeps baseline plus orders; executor
orders enter the record before FREEZE; one step per bar survives the S-4
self-transition; equity from reconciled balances; latch fires once per
breach (apart from F24-1); marker catches BaseException; zero-fill streak
correct; credential check does not echo; import contract per local report.

## Acceptance criteria

1 deterministic run: holds. 2 each REFUSE_START tested: holds (gaps F24-2,
T24-03). 3 no order without authorization: holds for executor orders; see
F24-1 on when FLATTEN may run. 4 non-simulator adapter refused: holds. 5
mid-run fault ends in FREEZE: holds. 6 report hashes and count: holds.

## Verdict

FIX.
