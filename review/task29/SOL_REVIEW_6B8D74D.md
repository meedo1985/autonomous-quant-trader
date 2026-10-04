# Sol §16 focused re-review of Task 29 repairs at `6b8d74d`: FIX

Date: 2026-10-04. Focused re-review of the S29-1..S29-6 repairs (`REPAIRS_37A9D1B.md`), finding IDs `S29R-n`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a105c7-97a8-7e70-8b2f-f38145c34271`. The final message is reproduced below unchanged, except that local file links were shortened to repository-relative form.

---

Model: OpenAI Codex, GPT-5 family; exact serving variant is not exposed in-session. Same Codex Sol reviewer family requested.  
Commit: `6b8d74ddd91bd37919a3f4765cbd1a8c6e308241`  
Verdict: **FIX**

### Earlier findings

| Finding | Status | Evidence |
|---|---|---|
| S29-1 | **Not resolved** | The cursor is step-level, not hour-level. It generates false alarms at several save sites and silently suppresses hours skipped by `busy_until`; see S29R-1. |
| S29-2 | Resolved | Router exists before journal/cursor reads; expected reconstruction failures and Telegram setup refusal become logged `REFUSE_START`. |
| S29-3 | Behavior resolved | No-write execution confirmed fetch code `1` retries and refusal code `2` stops. Committed regression coverage remains incomplete; see S29R-3. |
| S29-4 | Resolved | Aligned first midnight is included; hand-computed test passed. |
| S29-5 | Resolved | Text now accurately says “no exchange credential” and discloses the optional Telegram credential. |
| S29-6 | Resolved by recorded writable validation | Repair record reports `1766 passed, 9 skipped`. This sandbox still has no writable temporary directory, so I could not independently repeat it; this is not a code finding. |

### Findings

| ID | Severity | Location | Evidence | Required fix |
|---|---|---|---|---|
| S29R-1 | **BLOCKER** | [forward.py](src/aqt/app/forward.py:279), [paper_loop.py](src/aqt/app/paper_loop.py:994), [repair test](tests/integration/test_forward_paper.py:103) | The cursor advances only after the entire step returns. With prior cursor hour 0 and an owner-command save at hour 2, restart reports hours `[0,1,2]` lost although 0 and 1 completed. FREEZE/HALT terminal saves likewise produce false alarms; a crash after the final state save but before the separate cursor append reports an entirely completed run as lost. Pre-send restart refuses on the unknown order before emitting the cursor lag. Conversely, with `end=3` and final `busy_until=4`, lines 315–321 set the cursor to 5, so decision hours 3 and 4 are skipped without a `LOOP_LAG`. The repair’s single seeded-startup test does not exercise these cases. | Store `completed_through` atomically with each state snapshot and advance it only at an actual hour-completion boundary. Explicitly record hours intentionally skipped while busy. Add crash injection at startup, owner command, pre-send, FREEZE exit, both HALT paths, ordinary final save, cursor-write boundary, and `busy_until > end`. |
| S29R-2 | **BLOCKER** | [ci.yml](.github/workflows/ci.yml:60), [run_forward_paper.py](scripts/run_forward_paper.py:58) | d40e34d moved deployment refusals to `data/forward/deployment_refusals.jsonl`, but CI still greps `/var/lib/aqt/data/processed/paper/deployment_refusals.jsonl`. The mandatory `runbook-dry-run` therefore fails after the service correctly exits 2. It also corrupts the obsolete paper config instead of the configured forward-paper file. | Change CI to modify `configs/forward_paper.example.toml` and inspect `/var/lib/aqt/data/forward/deployment_refusals.jsonl`; rerun the Ubuntu systemd job. |
| S29R-3 | MINOR | [run_forward_paper.py](scripts/run_forward_paper.py:80) | d40e34d changed deployment ordering and codes 1/2 without adding committed tests. My no-write mocked execution passed, but the repository does not preserve that regression evidence. | Add small tests proving continuous code 1 retries, code 2 stops, `--once` returns 1, and deployment refusal occurs before config/channel/network access. |

No additional Binance market-data, simulator, credential, import-boundary, research, or lockbox defect was found. Official Binance behavior was not freshly checked because network access was explicitly prohibited and the exchange module was unchanged.

### Commands and results

```text
rtk git status --short --branch --untracked-files=all
PASS — clean task29-forward-paper worktree; only global-ignore permission warnings.

rtk git diff --stat / --name-status 37a9d1b 6b8d74d
PASS — seven expected changed files; 291 insertions, 38 deletions.

rtk git diff --check 37a9d1b 6b8d74d
PASS.

rtk .venv/Scripts/python.exe -m ruff format --check .
PASS — 117 files already formatted.

rtk .venv/Scripts/python.exe -m ruff check .
PASS.

rtk .venv/Scripts/python.exe -m mypy --no-incremental --no-sqlite-cache --cache-dir=NUL src
PASS — no issues in 53 source files.

rtk .venv/Scripts/lint-imports.exe --no-cache
PASS — six contracts kept, zero broken.

rtk .venv/Scripts/python.exe -B -m pytest -s -p no:cacheprovider tests/unit/test_package_imports.py -q
PASS — 19 passed.

rtk .venv/Scripts/python.exe -B -m pytest -s -p no:cacheprovider tests/integration/test_forward_paper.py::test_l02_counts_a_hand_computed_example -q
PASS — 1 passed.

rtk .venv/Scripts/python.exe -B -m pytest -s -p no:cacheprovider tests/integration/test_forward_paper.py -q
ENVIRONMENT INCOMPLETE — 1 passed, 5 tmp_path setup errors: no usable writable temporary directory. Not counted as a code finding.

No-write Python cursor matrix
REPRODUCED — accurate startup alarm; owner/catch-up and terminal-state false alarms; pre-send refusal precedes LOOP_LAG; post-final-save/pre-cursor false alarm; busy_until hours silently unreported.

No-write mocked scripts/run_forward_paper.py main-loop check
PASS — continuous [1,2] retried once then stopped; --once returned 1; deployment refusal returned 2 before config read.

rtk git grep -n "deployment_refusals.jsonl|paper_trading.example.toml|forward_paper.example.toml" ...
FAIL CONFIRMED — runtime writes data/forward, CI checks data/processed/paper and modifies the obsolete config.

rtk .venv/Scripts/python.exe -B -c "...frozen_hash_problems..."
PASS — [].

Independent SHA-256 manifest/sidecar verifier
PASS — 31 entries checked, zero failures.

rtk git diff --quiet 37a9d1b 6b8d74d -- docs protocols schemas specs FROZEN_HASHES.json
PASS — frozen files unchanged.
```

No network, credentials, confirmation data, or lockbox data were accessed. No files, commits, or remote state were changed. This review record remains uncommitted because the requested scope was read-only.

Do not merge 6b8d74d yet.  
The cursor can still misreport completed hours and silently lose hours after a long busy interval.  
Repair the cursor and stale CI paths, add the missing lifecycle tests, then rerun writable CI and human review.
