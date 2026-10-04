# Sol §16 review of Task 29 at `37a9d1b`: FIX

Date: 2026-10-04. This is the different-model review required by Constitution §16, run from prompt `review/task29/SOL_REVIEW_PROMPT.md`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a105b2-f705-7620-9b7a-a27ffc10b272`. The final message is reproduced below unchanged, except that local file links were shortened to repository-relative form.

---

OpenAI Codex, GPT‑5 family (exact serving variant is not exposed in-session).  
Checked commit `37a9d1b629ef52c11533cc8c3535b2938e8f8ca6` against `7f86530c6c164f48b4348a0ca03c16e2ce941b0c`.  
Verdict: **FIX**

## Findings

| ID | Severity | Location | Scenario, evidence, and proposed fix |
|---|---|---|---|
| S29-1 | BLOCKER | [forward.py](</src/aqt/app/forward.py:85>), [paper_loop.py](</src/aqt/app/paper_loop.py:994>) | `pending_window()` treats every journal save timestamp as proof that its hour completed. But the loop saves at startup, after owner commands, and before sending an order. A hard crash after `save(ready)` can therefore skip the entire pending hour. The in-memory reproduction returned `(h, h+1)` for a fresh journal but `None` after merely checkpointing at `h`. Add an explicit `completed_through` cursor written only after an hour completes; test hard crashes at every save site, including startup, owner commands, pre-send, FREEZE/HALT, and `busy_until`. |
| S29-2 | MAJOR | [forward.py](</src/aqt/app/forward.py:244>), [run_forward_paper.py](</scripts/run_forward_paper.py:124>) | The journal is read before the alert router and normal startup-refusal boundary. `StateError`, ledger damage, I/O errors, or invalid reconstructed balances can escape unlogged; the synthetic damaged-journal run raised `StateError` with `events 0`. Telegram setup refusal is also printed to stderr rather than written to the operational ledger. Establish logging before reading state and convert expected state/rebuild failures into logged CRITICAL `REFUSE_START` outcomes. |
| S29-3 | MAJOR | [run_forward_paper.py](</scripts/run_forward_paper.py:135>) | In continuous mode, return code `2` is ignored. A refused step is retried each hour against the unchanged journal, so the same pending hours can emit repeated `LOOP_LAG` alerts rather than being reported once and resolved. Stop the service loop on refusal and reserve a distinct retryable code for fetch failures. The later commit `d40e34d` appears to implement this, but it is not part of the requested commit. |
| S29-4 | MINOR | [forward.py](</src/aqt/app/forward.py:185>) | When the first snapshot is exactly 00:00 UTC, valuation starts at the following midnight. With snapshots at day-0 midnight and closes at day 0/day 1, `daily_equity_returns()` returned `[]` instead of one daily observation. This conservatively undercounts L‑02 by one decision. Include the initial midnight when the first snapshot is exactly aligned and add that boundary to the hand-computed test. |
| S29-5 | MAJOR | [run_forward_paper.py](</scripts/run_forward_paper.py:120>), [telegram.py](</src/aqt/monitoring/telegram.py:466>) | The unqualified boundary “no credential is read” is false when `--telegram` is used: `owner_channel()` calls `read_credential()` from Windows Credential Manager or `/etc/aqt/telegram`. No Binance credential is read, and public-market requests remain credential-free. Either remove Telegram from this entry point or have the owner clarify the boundary as “no exchange credential,” then correct the misleading module/script text. |
| S29-6 | BLOCKER | Validation environment | Mandatory full pytest validation could not complete because the supplied read-only environment has no writable temporary directory. Three of four Task-29 tests failed during `tmp_path` setup, not in tested code. Rerun the exact target in writable CI before merge. |

## Assessment by review question

- Normal uninterrupted hourly steps use the correct half-open window, and the supplied replay-equivalence test is well targeted. S29-1 breaks that guarantee after a hard crash.
- Reconstruction uses the same exact balance effects as reconciliation, refuses unknown outcomes, and preserves terminal orders for idempotency. It is necessarily not an independent reconciliation source after restart because the simulated venue is reconstructed from the journal; this limitation must never be carried into a real venue adapter.
- Order identifiers are deterministically distinct across normal steps because each step’s run ID contains its start hour.
- `Observation.scheduled` does not weaken replay: existing observations leave it `None`, preserving the old decision-time check. Successful catch-up emits one aggregate CRITICAL event, but S29-3 causes repeats after refusal.
- The Task‑12 Newey–West calculation with `H=24`, clamping, fallback, and method reporting is correct; the supplied hand computation passed. S29-4 is the remaining boundary error.
- Simulator-only enforcement, public Binance market endpoints, import contracts, and research/model/lockbox isolation passed. No Binance key is read; S29-5 concerns the separate Telegram credential.

## Commands and results

```text
rtk git diff --stat 7f86530 37a9d1b
PASS — nine changed files, 773 insertions, 2 deletions.

rtk git diff --check 7f86530 37a9d1b
PASS.

rtk git status --short --branch --untracked-files=all
PASS — clean worktree. The branch later advanced to d40e34d during review.

rtk git diff --quiet 37a9d1b d40e34d -- src tests
PASS — source package and tests used by the focused checks are unchanged after 37a9d1b.

rtk git show 37a9d1b:scripts/run_forward_paper.py | rtk .venv/Scripts/ruff.exe check --stdin-filename scripts/run_forward_paper.py -
PASS.

rtk git show 37a9d1b:scripts/run_forward_paper.py | rtk .venv/Scripts/ruff.exe format --check --stdin-filename scripts/run_forward_paper.py -
PASS.

rtk .venv/Scripts/python.exe -m ruff format --check .
PASS — 117 files already formatted.

rtk .venv/Scripts/python.exe -m ruff check .
PASS.

rtk .venv/Scripts/python.exe -m mypy --no-incremental --no-sqlite-cache --cache-dir=NUL src
PASS — no issues in 53 source files.

rtk .venv/Scripts/lint-imports.exe --no-cache
PASS — six contracts kept, zero broken.

rtk .venv/Scripts/python.exe -m pytest -s -p no:cacheprovider tests/unit/test_package_imports.py -q
PASS — 19 passed.

rtk .venv/Scripts/python.exe -m pytest -s -p no:cacheprovider tests/integration/test_forward_paper.py::test_l02_counts_a_hand_computed_example -q
PASS — 1 passed.

rtk .venv/Scripts/python.exe -m pytest -s tests/integration/test_forward_paper.py -q
INCOMPLETE — 1 passed, 3 setup errors: no writable temporary directory.

rtk .venv/Scripts/python.exe -m pytest -s -p no:cacheprovider tests/unit/test_monitoring.py -q
INCOMPLETE — 31 passed, 6 tmp_path setup errors for the same environment reason.

rtk .venv/Scripts/python.exe -c "<pending_window fresh/checkpoint reproduction>"
PASS — fresh=(h,h+1), checkpoint_at_start=None; reproduced S29-1.

rtk .venv/Scripts/python.exe -c "<damaged-journal run_step reproduction>"
EXPECTED FAILURE — StateError: damaged; events 0; reproduced S29-2.

rtk .venv/Scripts/python.exe -c "<midnight daily_equity_returns reproduction>"
PASS — returned []; reproduced S29-4.

rtk .venv/Scripts/python.exe -c "from pathlib import Path; from aqt.app.paper_loop import frozen_hash_problems; print(frozen_hash_problems(Path('.').resolve()))"
PASS — [].

rtk .venv/Scripts/python.exe -c "<verify every frozen .sha256 sidecar>"
PASS — 13 sidecars checked, none bad.

rtk git diff --quiet 7f86530 37a9d1b -- docs protocols schemas specs FROZEN_HASHES.json
PASS — frozen baseline bytes and inventory unchanged.
```

No network was used, and no confirmation or lockbox data was read. I made no edits, commits, or pushes. This review must be written into and committed in the repository before any repair/merge claims rely on it.

Do not merge `37a9d1b` yet.  
A crash at the wrong checkpoint can silently lose an hour.  
Some startup refusals can fail without reaching the operational log.  
The L‑02 method is sound, but its first-midnight count needs correction.  
Commit this review record, repair the findings, rerun writable CI, and return the result for human review.
