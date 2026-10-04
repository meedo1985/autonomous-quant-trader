# Sol §16 fourth focused re-review of Task 29 repair at `881cb9c`: FIX

Date: 2026-10-04. Focused re-review of the S29R3-1 repair (`REPAIRS_0DDDDAE.md`), finding IDs `S29R4-n`. Prompt scope: `git diff 98e0910 881cb9c`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a10618-c376-73f1-b5f3-3b795d62295c`. The final message is reproduced below unchanged.

---

Model: OpenAI Codex Sol (`gpt-5.6-sol` reviewer role requested; exact serving variant not exposed), GPT-5 family  
Commit: `881cb9ca161563100b312ce729658bd6ebe7fca9`  
Verdict: **FIX**

### S29R3-1

**RESOLVED in code at all three saves.**

`unfinished_from` becomes `hour + 1h` for:

- Passed `FREEZE_EXIT`: `paper_loop.py:905`
- Failed HALT-override reconciliation: `paper_loop.py:935`
- Accepted HALT override: `paper_loop.py:967`

The other save sites retain correct in-progress or hour-end values. Refused overrides and refused `FREEZE_EXIT` attempts reach the subsequent hour-end/final save correctly. No remaining incorrect save site found.

### New findings

| ID | Severity | Location | Scenario and evidence | Fix |
|---|---|---|---|---|
| S29R4-1 | **BLOCKER** | `src/aqt/app/paper_loop.py:888-905` | Replay behavior is not unchanged. Previously, successful exit logged the `FREEZE_EXIT` transition before the same-hour `HALT_OVERRIDE` refusal; now the refusal comes first. When `exit_freeze()` raises `SafetyError`, the former order was `FREEZE_EXIT` refusal then `HALT_OVERRIDE` refusal; it is now reversed. Timestamps and normal-path incidents remain the same, and moving `fire()` into `end_halt()` is behavior-equivalent. However, event order changed, and an alert-write failure can now prevent the exit attempt entirely. | Attempt `exit_freeze()` first. On failure, log the `FREEZE_EXIT` refusal followed by the HALT refusal. On success, log the HALT refusal after the exit transition/replay but before `save(..., ended=hour)`. |
| S29R4-2 | **MINOR** | `tests/integration/test_paper_recovery.py:936-955`; `REPAIRS_0DDDDAE.md` | The claimed successful-`FREEZE_EXIT` crash test is not a crash test: it neither delays reconciliation nor kills after the save, and it does not call `unfinished_hours()`. It verifies the state field directly, but does not cover the multi-hour crash scenario requested by S29R3-1. | Add a delayed successful reconciliation, kill immediately after its journal save, and assert that only the intervening skipped hours are returned. |

For a refused HALT override (`override_halt()` raising `SafetyError`), the moved loss-stop call retains the old event order, timestamp, firing condition and incident behavior. For failed reconciliation it remains a no-op in `FREEZE`; for an accepted override it remains suppressed in `RUNNING`.

### Commands and results

```text
rtk git status --untracked-files=all
PASS — clean; branch task29-forward-paper; HEAD 881cb9c.

rtk git diff 98e0910 881cb9c
INSPECTED — scoped source and test changes plus repair record.

rtk git diff --check 98e0910 881cb9c
PASS.

rtk git diff --quiet 98e0910 881cb9c -- docs protocols schemas specs FROZEN_HASHES.json
PASS — no frozen-path change.

rtk .venv/Scripts/ruff.exe check --no-cache .
PASS.

rtk .venv/Scripts/ruff.exe format --check --no-cache .
PASS — 117 files formatted.

rtk .venv/Scripts/mypy.exe --no-incremental --no-sqlite-cache --cache-dir=NUL src
PASS — 53 source files.

rtk .venv/Scripts/lint-imports.exe --no-cache
PASS — 6 contracts kept.

rtk .venv/Scripts/python.exe -B -m pytest -q -s -p no:cacheprovider tests/unit/test_package_imports.py
PASS — 19 passed.

rtk .venv/Scripts/python.exe -m pytest --collect-only -q -s -p no:cacheprovider tests/integration/test_paper_recovery.py
PASS — 30 tests collected.
```

Test execution requiring `tmp_path` was unavailable in this read-only sandbox. The repair record reports `1784 passed, 9 skipped` locally. No network, credentials, confirmation/lockbox data, edits, commits, or pushes were used.

Do not merge `881cb9c` yet.  
The unfinished-hour repair itself is correct at all three terminal saves.  
Restore the original FREEZE-exit event ordering and add the promised delayed-crash test, then re-review.
