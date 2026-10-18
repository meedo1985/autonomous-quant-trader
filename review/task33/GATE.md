# Task 33 gate: read-only dashboard

Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-18, applying `task-gate-review`. This is a local gate. It is not the Sol build review and not the owner's §16 PR review (owner answer Q-D3).

**Base:** `b0c668b` (dashboard-proposal, with owner answers). **Authorization:** `review/roadmap/DASHBOARD_OWNER_ANSWERS.md` (Q-D1 yes, Q-D2 later, Q-D3 yes). **Spec:** `review/roadmap/DASHBOARD_PROPOSAL.md` (Sol ACCEPT at re-review 7).

## Changed files

| File | What |
|---|---|
| `src/aqt/dashboard.py` | Reads the inputs (four states), renders the escaped static page, builds it atomically (staging, then rename), and the sandbox check. Standard library plus `aqt.core.ledger` and `aqt.core.deployment.APPROVED`. |
| `scripts/dashboard.py` | Entry point: `build` or `check`; no logic. |
| `deploy/dashboard/aqt-dashboard@.service`, `.timer` | The sandboxed unit (section 2 settings) and the 15-minute timer. |
| `deploy/dashboard/install.sh` | Account, own checkout at `/opt/aqt-dashboard/app`, units, first page, timer. Does not touch the paper app. |
| `deploy/dashboard/copy-dashboard.bat` | The laptop copy-and-open file (owner fills in the address). |
| `deploy/RUNBOOK.md` §9 | Install, port check, sandbox check, copy, removal. |
| `pyproject.toml` | New forbidden contract for `aqt.dashboard`. |
| `.github/workflows/ci.yml` | `runbook-dry-run` gains the real install, port diff, sandbox check and page checks on Ubuntu 24.04. |
| `tests/unit/test_dashboard.py` | 11 tests. |

Out of scope and untouched: the paper app, governor, execution, protocol, frozen files, the Telegram summary (Q-D2 later).

## Acceptance (proposal section 4)

| Criterion | Evidence |
|---|---|
| Every panel renders on synthetic files | `test_every_panel_renders_with_its_labels` |
| Four states, never a crash, nothing invented; concurrent append and corrupt record | `test_the_four_states`, `test_missing_inputs_show_no_data_never_numbers` |
| Red for a stale report, a stale bar, a refusal | `test_health_is_red` (3 cases) |
| Malicious strings escaped and inert | `test_file_text_is_escaped`; CSP `default-src 'none'` |
| Staged and renamed; no partial page | `test_build_renames_a_finished_page_into_place` |
| "As of" shown; a stopped generator keeps its time | same test, and the page header |
| `L-02` raw, effective, method, reason; fallback labelled; no date | `test_every_panel_renders_with_its_labels`, `test_fallback_count_is_labelled` |
| Tampered ledgers show unknown or invalid | `test_tampered_ledgers_show_unknown_or_invalid` |
| Labels; no equity line | `test_every_panel_renders_with_its_labels` |
| Import contract | `lint-imports`: 7 kept, 0 broken |
| Sandbox boundaries on a server | `sandbox_check` reports each one (`test_sandbox_check_reports_each_boundary` shows they are reported as not holding outside the sandbox); proven on Linux in CI `runbook-dry-run`, and on the owner's server by RUNBOOK §9 |
| No listening port added | CI port diff; RUNBOOK §9 |
| End-to-end copy by the owner | after merge, RUNBOOK §9; recorded then |

## Validation (Windows laptop, repository `.venv`)

| Command | Result |
|---|---|
| `ruff format --check .` | exit 0, 163 files already formatted |
| `ruff check .` | exit 0 |
| `mypy src` | exit 0, no issues in 54 files; `mypy src/aqt/dashboard.py scripts/dashboard.py` exit 0 |
| `lint-imports` | exit 0, 7 contracts kept |
| `pytest tests/unit/test_dashboard.py` | exit 0, 11 passed |
| `pytest --ignore-glob="tests/unit/test_calibration_*"` | exit 0, 1804 passed, 9 skipped |
| CI YAML parses | `yaml.safe_load` ok |

**Not run locally:** the systemd unit, the install script and the sandbox check need Linux with systemd. The CI `runbook-dry-run` job runs them on the PR. Until it passes, the sandbox claims are unproven.

## Frozen artifacts

No file under `docs/`, `protocols/`, `schemas/`, `specs/` and no `FROZEN_HASHES.json` or sidecar changed (`git status` lists none).

## Findings

| ID | Class | Finding |
|---|---|---|
| G33-1 | NON-BLOCKING | `_io_uring_refused` uses the x86-64 syscall number 425; the server is x86-64 (Haswell probe). On another architecture the check would test the wrong call. |
| G33-2 | NON-BLOCKING | The incidents panel shows raw payload JSON (escaped); readable, not pretty. |
| G33-3 | BLOCKER, repaired | **Found by the CI dry run, not by any review.** At `97a4160` the check printed `FAIL cannot read /etc/aqt/telegram` (run 39118454935; the other 10 checks PASS). `InaccessiblePaths=` mounts a mode-000 node, and `CAP_DAC_READ_SEARCH`, the unit's one capability, bypasses file modes. So the proposal's setting (section 2) did not hide the token. Repair: `TemporaryFileSystem=/etc/aqt:ro` plus `BindReadOnlyPaths=/etc/aqt/deployments.jsonl`: inside the unit the token file does not exist. This deviates from the setting the proposal names; its stated boundary ("cannot read the credential") is unchanged, and the CI check now tests it. |
| G33-4 | BLOCKER, repaired | Found by the CI dry run at `c1e4b3e`: `SystemCallFilter=` kills a process that makes a filtered call (the check's `io_uring_setup` probe dumped core). Repair: `SystemCallErrorNumber=EPERM`, so the call fails cleanly. |
| G33-5 | NON-BLOCKING, disclosed | The capability reads every file visible in the unit, for example `/etc/shadow`. The proposal claims no more ("not: it can read only the input files"); nothing can leave, because the unit has no socket but the journal's, and the code writes only the page. |

## Sandbox on Linux (CI `runbook-dry-run`, run 39118571234, commit `6eb05e6`, Ubuntu 24.04)

The real install, with synthetic inputs private to `aqt` (mode 600):

```
PASS can read /var/lib/aqt/data/forward/account-1/forward_reports.jsonl
PASS can read /var/lib/aqt/data/live/BTCUSDT-1h.jsonl
PASS can read /var/lib/aqt/data/forward/account-1/incidents.jsonl
PASS can read /etc/aqt/deployments.jsonl
PASS cannot write in /var/lib/aqt
PASS cannot write in /etc/aqt
PASS cannot write in /opt
PASS cannot read /etc/aqt/telegram
PASS cannot open a socket (inet)
PASS cannot open a socket (Unix)
PASS io_uring_setup is refused
```

The job also checked that:
- no listening port was added (port diff);
- the page is mode 644 and alone in `page/`;
- the page shows the approved commit;
- `aqt-dash` cannot read the token outside its unit;
- the timer is `enabled`.

**LOCAL GATE: PASS**, including the sandbox on Linux. Outstanding: Sol's build review, the owner's §16 PR review, and the end-to-end copy on the owner's server after merge.
