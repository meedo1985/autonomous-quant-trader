# Sol §16 second focused re-review of Task 29 repairs at `da27588`: FIX

Date: 2026-10-04. Focused re-review of the S29R-1..S29R-3 repairs (`REPAIRS_6B8D74D.md`), finding IDs `S29R2-n`. Prompt: scope `git diff 1c98cb5 da27588`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a105dc-c060-73f3-9152-795d6e12875e`. The final message is reproduced below unchanged.

---

Model: OpenAI Codex Sol (`gpt-5.6-sol` requested; exact serving variant not exposed); GPT-5 family  
Commit: `da2758882e78f432cbe005f28f99c869ece25b66`  
Verdict: **FIX**

### Earlier findings

| Finding | Status | Evidence |
|---|---|---|
| S29R-1 | **Not resolved** | The two-phase cursor fixes normal refused-step handling and reports busy skips after a successful return, but it is not atomic with journal saves. Long reconciliations invalidate the “only the last-save hour can be unfinished” claim; see S29R2-1. A final-save/pre-`END` crash also still produces a conservative false alarm. |
| S29R-2 | **Resolved** | CI now modifies `configs/forward_paper.example.toml` and checks `/var/lib/aqt/data/forward/deployment_refusals.jsonl`, consistent with the service’s `/var/lib/aqt` working directory. |
| S29R-3 | **Resolved** | Committed tests cover retry/stop/`--once` behavior and deployment-first refusal. Independent no-write probes confirmed `[1,0,2]` returns `2` after three calls and an unloggable refusal still returns `2`. |

### New findings

| ID | Severity | Location | Scenario and evidence | Fix |
|---|---|---|---|---|
| S29R2-1 | **BLOCKER** | `src/aqt/app/forward.py:330-336,376-405`; `src/aqt/app/paper_loop.py:896,916,947,1003,1221`; `tests/integration/test_forward_paper.py:131-208` | A reconciliation can finish two hours after decision hour H—existing recovery tests explicitly exercise this. The loop can save at H+2 before H+1 has been processed or durably reported. If the process dies after that journal save but before `skipped_while_busy_event` and cursor `END`, restart begins at H+3 while `_interruption` names only H+2 and says every earlier hour finished. H+1 is silently omitted. Separately, a crash after the ordinary final save but before cursor `END` reports an interruption although all hours completed. The new tests seed timestamps or test the event helper; they do not crash at the real save sites. | Store completed-through and busy-skipped progress in the same durable journal record that advances restart time, rather than inferring it from a separate cursor. Add crash injection after every save site, including ≥2-hour FREEZE/HALT reconciliation and final-save/pre-`END`. |

No other repair-introduced defect was found.

### Commands and results

```text
rtk proxy git diff --check 1c98cb5 da27588 -- <four scoped files>
PASS

rtk .venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests/integration/test_forward_paper.py -q
ENVIRONMENT BLOCKED — exit 1 before collection; no writable temporary directory.

rtk .venv/Scripts/python.exe -B -m pytest -s -p no:cacheprovider tests/integration/test_forward_paper.py::test_hours_a_running_reconciliation_skips_are_reported -q
PASS — 1 passed.

rtk .venv/Scripts/python.exe -m ruff check --no-cache src/aqt/app/forward.py scripts/run_forward_paper.py tests/integration/test_forward_paper.py
PASS

rtk .venv/Scripts/python.exe -m ruff format --check --no-cache src/aqt/app/forward.py scripts/run_forward_paper.py tests/integration/test_forward_paper.py
PASS — 3 files formatted.

rtk .venv/Scripts/python.exe -m mypy --no-incremental --no-sqlite-cache --cache-dir=NUL src/aqt/app/forward.py
PASS

rtk .venv/Scripts/lint-imports.exe --no-cache
PASS — 6 contracts kept.

No-write script probes
PASS — unloggable refusal returned 2; continuous [1,0,2] returned 2 after 3 calls.

rtk proxy git diff --quiet 1c98cb5 da27588 -- docs protocols schemas specs FROZEN_HASHES.json
PASS — frozen scope unchanged.

rtk git status --porcelain=v1 --untracked-files=all
PASS — clean.
```

No network, credentials, confirmation data, lockbox data, or repository writes were used.

Do not merge `da27588` yet.  
A long reconciliation followed by a crash can still hide an earlier skipped hour, and the final cursor boundary can still false-alarm.  
The CI-path and runner-exit repairs are sound; make progress atomic with journal saves and test real crash boundaries.
