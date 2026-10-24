# Whole-repo audit, 2026-10-24 (ponytail-audit)

**Auditor:** Claude Opus 5.5 (`claude-opus-5-5`), Claude Code, ponytail 5.3.2 `ponytail-audit`, 2026-10-24.
**Load assumed:** one server; one forward-paper process stepping hourly (systemd `aqt-paper`); one D-19 calibration container with 2 workers; one owner.
**Read:** `scripts/run_forward_paper.py`, `src/aqt/app/forward.py`, `src/aqt/data/live_bars.py`, `src/aqt/monitoring/alerts.py`, `src/aqt/monitoring/telegram.py` (error paths), `src/aqt/core/ledger.py` (lock and append), `src/aqt/core/deployment.py`, `deploy/aqt-paper.service`, `deploy/calibration/d19.sh`, the write paths of `calibration/` and `scripts/d19_*.py`, `configs/forward_paper.example.toml`, `paper_loop.load_config`.
**Not read:** calibration maths (`screen.py`, `choices.py`, `dsr.py`, `qobj.py`) beyond writes; backtest, benchmarks, features, metrics; dashboard.
**Checks run at audit:** ruff clean; mypy clean (56 files); 207 live-path tests passed.

## Findings

| ID | Group | Finding | Status |
|---|---|---|---|
| PA-1 | Should fix | `run_forward_paper.main` caught only fetch failures and `ForwardError`. Any other error (e.g. `OSError` on a full disk writing `forward_reports.jsonl`, `LedgerError` on the cursor) ended the process with no alert; systemd restarts it at the next slot, so a crash loop could be silent. Forward paper did restart on 2026-10-23 06:34:53Z, cause unknown at audit time. | **Repaired**: `crashed()` alerts a CRITICAL `SHUTDOWN` naming the error, then the error is re-raised (exit 1, restart unchanged). Test `test_a_crash_is_alerted_then_raised`. |
| PA-2 | Should fix | `deployment.approved_code` checked only `git status`'s exit code; a failing `git ls-files -v` or ignored-files listing gave empty output, so those checks passed (fail-open at a trust boundary). | **Repaired**: any failed git call refuses ("git could not check the checkout"). Test `test_a_failed_git_listing_refuses[-v,--others]`. |
| PA-3 | Nice to have | `scripts/d19_choose.py:174` and `scripts/d19_heldout.py:458` write their results with plain `write_text`, not temp + fsync + rename as `calibration/rundef.py:379-384` does; a crash mid-write leaves a torn file. | **Not repaired.** The running D-19 run uses the engine pinned at `eeaa728`; a change on `main` would not be used by it, and both files are regenerated from the stored chunks. Revisit with the next engine change. |
| PA-4 | Nice to have | `paper_loop.run_paper` is about 790 lines (start checks, decision loop, reconciliation, flatten, report). No bug. | **Not repaired.** Refactor alone of §16-protected, heavily tested code costs a full review cycle for no behaviour change. Revisit when the function is next changed. |

Not a finding (noted): every ledger append rescans the whole file (O(n) per append); server log sizes were not measured.

## Repair validation (crash-alert branch)

- The 3 new tests fail with the repairs stashed (3 failed) and pass with them.
- `pytest` without the calibration tests (`--ignore-glob='tests/unit/test_calibration_*' --ignore=tests/unit/test_d19_deploy.py`): 1841 passed, 9 skipped. The calibration tests were not run: the change does not touch `calibration/` or `scripts/d19_*`, and they have exhausted the laptop's memory before; CI runs them.
- `ruff check .` clean; `ruff format` applied; `mypy src` clean; `lint-imports` 7 kept, 0 broken; `git diff --check` clean.

Both repairs touch the forward-paper live path and the deployment check, so they need a different-model review and the owner's §16 PR review before merge.
