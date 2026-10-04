# Task 29: repairs for Sol re-review S29R-1..S29R-3

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`)
**Review:** `SOL_REVIEW_6B8D74D.md` (`1c98cb5`), verdict FIX

Every finding is accepted, and none is left unrepaired.

| Finding | Repair |
|---|---|
| S29R-1 (BLOCKER) | The step-level `completed_through` cursor is replaced by a two-phase cursor. Each step appends `START` (its window) before the loop runs and `END` after, whether refused or not. A `START` with no `END` means the process stopped during that step; a journal with no cursor at all is treated the same way. The next step reports it as one CRITICAL `LOOP_LAG` before anything else, including an unknown-order refusal from a pre-send save. The report names the step, the last save, and the only hour that may not have finished: the hour of the last save, or none when the step saved nothing. Every save site is either an hour's end (startup, each hour, the final save) or falls within one hour (owner command, pre-send, FREEZE/HALT reconciliation), so every earlier hour had finished. This removes the false alarms for finished hours. A crash after the final save but before `END` is still reported. It says the hour *may* be cut short, because the journal cannot tell an hour-end save from a save within the hour, and the process really did stop. When a reconciliation still running at the step's end makes the loop save after `end`, the skipped hours `[end, resume)` are now reported as a `LOOP_LAG` WARNING (`skipped_while_busy_event`), as a replay would skip them. Tests: `test_an_interrupted_step_names_only_the_hour_of_its_last_save` (save at an hour's start, mid-hour, the step's final save, and before the step), `test_an_interrupted_pre_send_is_reported_before_its_refusal`, `test_a_refused_step_is_not_an_interruption`, `test_hours_a_running_reconciliation_skips_are_reported`. The busy-skip test covers the event function; the call in `run_step` is the two lines after the run. |
| S29R-2 (BLOCKER) | CI now edits `configs/forward_paper.example.toml` and checks `/var/lib/aqt/data/forward/deployment_refusals.jsonl`. The failed `runbook-dry-run` on PR #42 showed the old path missing, which confirms the finding. |
| S29R-3 (MINOR) | `test_the_script_retries_a_failed_fetch_and_stops_on_a_refusal` covers code 1 retried, code 2 stopping, and `--once` returning 1 or 0. `test_the_script_checks_the_deployment_before_anything_else` covers the deployment refusal: it is logged and exits 2 before an unparsable config, the store, the account or a step. Also, as found while repairing: a deployment or Telegram refusal that cannot be logged now still exits 2 (`refuse`), as the replay runner does (S30-9). A refusal inside `run_step` that cannot be logged still raises `ForwardError`, so it exits 2 rather than crashing into a retry. |

**Validation after the repairs:** `ruff check .`, `ruff format --check .`,
`mypy src`, `lint-imports` and the full `pytest` suite. Results:
- ruff: pass; 117 files formatted;
- mypy: no issues in 53 source files;
- lint-imports: 6 contracts kept, 0 broken;
- pytest: **1776 passed, 9 skipped** (5 min 56 s).
