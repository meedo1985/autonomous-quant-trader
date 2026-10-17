# Adjudication of the Sol re-review of screen S7 at 951a5c7

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Review record: `SOL6_SCREEN_S7_REREVIEW_951A5C7.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S7R-R1 | High | **Accept.** An earlier entry of the trial-code directory (for example from `PYTHONPATH`) stayed before site-packages. | `_extend_path` removes every existing occurrence of the engine and trial-code entries, then puts the engine first and the trial code last; the parent and every worker use it. Test `test_workers_search_trial_code_last` starts with the trial directory first. |
| S7R-R2 | High | **Accept.** `declare` took a caller-built `HourlySource`. | `declare` takes the raw root and rebuilds the bars itself with `load_hourly_source` (`build_exploration_manifest` checks every archive against its sidecar), then compares the manifests with the run definition's. Changed bars cannot come with unchanged identity. Tests adjusted. |
| S7R-R3 | Medium | **Accept.** | `run_screen` applies the same import paths in the parent before preloading trial code. Test `test_run_screen_finds_trial_code_from_code_dir_alone` (module present only in `code_dir`). |
| S7R-R4 | Medium | **Accept.** | The CLI reserves the record file with exclusive creation before any work and removes only that reserved file if the screen fails. The CLI test asserts no run starts when the file exists and no file remains after a failing screen. |

Not repaired: none.

Validation: full screen suite (screen, event contract, deploy, feature columns) passed with `-W error::FutureWarning`; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
