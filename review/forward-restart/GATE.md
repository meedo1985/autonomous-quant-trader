# F-RESTART build gate

Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-18, applying `task-gate-review`. A local gate, not Sol's build review and not the owner's §16 PR review.

**Authorization:** `OWNER_ANSWER_QR1.md` ("Yes, build it"). **Spec:** `PROPOSAL.md`, Sol ACCEPT at re-review 2.

## Change

| File | What |
|---|---|
| `scripts/run_forward_paper.py` | `first_slot(now)`: the next occurrence of HH:01 UTC. Without `--once`, `main` prints `waiting until … UTC for the first step` and sleeps until then, after the deployment check and the Telegram set-up and before the first step. The loop is unchanged. The module description is updated. |
| `tests/integration/test_forward_paper.py` | Boundary tests: 14:00:30 → 14:01, 14:01:10 → 15:01, 14:01:00 → 15:01, 23:59 → 00:01 the next day. The service sleeps before its first step; `--once` steps at once. |
| `deploy/RUNBOOK.md` §5 | After a start: the wait, the `active (running)` status while waiting, and the log command to check afterwards. |

Unchanged: every start check, the lag limit, the `LOOP_LAG` report, the replay, `paper_loop`, `forward`, the service unit, the configuration and frozen files.

## Acceptance (proposal §2)

| Item | Evidence |
|---|---|
| The next occurrence of HH:01 UTC, not "next hour plus offset" (FRR-1) | `test_the_first_step_waits_for_the_next_slot` (4 cases) |
| The wait comes before the first step; `--once` is immediate | `test_the_service_waits_before_its_first_step_and_once_does_not` |
| The deployment check still comes before anything | `test_the_script_checks_the_deployment_before_anything_else` (existing, passes) |
| The retry and refusal exit codes are unchanged | `test_the_script_retries_a_failed_fetch_and_stops_on_a_refusal` (existing, passes) |

## Validation (Windows laptop, `.venv`)

| Command | Result |
|---|---|
| `ruff format --check .` | exit 0, 176 files already formatted |
| `ruff check .` | exit 0 |
| `mypy src`; `mypy scripts/run_forward_paper.py` | exit 0 |
| `lint-imports` | exit 0, 7 contracts kept |
| `pytest tests/integration/test_forward_paper.py` | exit 0, 26 passed |
| `pytest --ignore-glob="tests/unit/test_calibration_*"` | exit 0, 1844 passed, 9 skipped |

No frozen file changed.

**LOCAL GATE: PASS.** Outstanding: Sol build review, owner §16 PR review, server update (RUNBOOK §7).

## Correction (after CI, 2026-10-18)

The validation table was run **before** a last edit of the module description in `scripts/run_forward_paper.py`. That edit left a 95-character line. CI `checks` failed on it (`ruff check`: E501 at line 13; run on head `46674e3`), and the table's `ruff check` row did not hold for the committed code. Repair: the paragraph is rewrapped; the text and the code are unchanged. Re-run after the repair:

| Command | Result |
|---|---|
| `ruff check .` | exit 0 |
| `ruff format --check .` | exit 0, 176 files already formatted |
| `mypy scripts/run_forward_paper.py` | exit 0 |
| `pytest tests/integration/test_forward_paper.py` | exit 0, 26 passed |

The diff of the repair is whitespace within the docstring only (4 lines). It came after Sol's build review and the owner's review of `46674e3`.
