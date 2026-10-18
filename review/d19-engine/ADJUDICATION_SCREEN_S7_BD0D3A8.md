# Adjudication of the Sol review of screen S7 at bd0d3a8

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Review record: `SOL6_SCREEN_S7_REVIEW_BD0D3A8.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S7-R1 | High | **Accept.** The trial-code directory came first on `sys.path`, so it could shadow `sklearn` or `lightgbm`. | DR-8: workers put the repository and `src` first and the trial-code directory **last**; the CLI appends it last. Test `test_workers_search_trial_code_last`. |
| S7-R2 | High | **Accept.** The caller supplied the window, window id, gap and source unchecked. | DR-6: `declare` takes no window inputs: `C2_G_DAYS = 1247 - grid.T_C2` (7), `C2_W0 = 2022-01-01 + g` (2022-01-08), `C2_WINDOW_DAYS = grid.T_C2` (1240), `C2_WINDOW_ID` built from them; and the exploration bars' manifests must equal the run definition's `exploration_source` manifests. Tests `test_c2_constants_follow_the_engine`, `test_a_declaration_record_needs_the_checks_and_names_the_object`. |
| S7-R3 | High | **Accept.** A direct `run_screen` call produced a declaration-shaped record without any object check. | `run_screen` now makes only a measurement record (no outcome); only `declare`, after `check_object`, produces an outcome, and its record carries `qualification_object_sha256`. |
| S7-R4 | Medium | **Accept, in two steps.** | `FROZEN_REFERENCE_VECTORS` freezes the G-11 and G-14 vectors (exact on every CPython); `declare` refuses if any differ. The float path's vector is `None` until the S8 pilot computes it on the pinned image, and `declare` refuses until it is frozen. Test `test_the_screen_reference_vectors_are_frozen_where_exact`. |
| S7-R5 | Medium | **Accept.** | DR-7: a measurement record has `availability` (ALL_AVAILABLE / SOME_UNAVAILABLE) and `measurement_only`, never `outcome`; the CLI's `pilot` command requires exactly 20 trials and prints `MEASUREMENT`. Tests `test_a_measurement_records_every_run_and_no_outcome`, `test_the_cli_pilot_needs_twenty_trials_and_never_overwrites`. |
| S7-R6 | Medium | **Accept.** | `run_screen` loads every trial's signal and overlay from its declared bytes before any job; a stale hash refuses the screen with no run started. Test case in `test_an_unbuildable_path_and_refusals_before_any_run`. |
| S7-R7 | Medium | **Accept.** | `check_object` verifies every file listed in the object's manifest (and requires `definition.json`, `mapping.py`, `screen.py`). Test `test_check_object_verifies_every_manifest_file`. |
| S7-R8 | Low | **Accept.** | The CLI writes the record with exclusive creation (`open("xb")`). Test case in the CLI test. |

The CLI now has two commands, `pilot` and `declare`; the free `--w0`, `--window-days`, `--window-id`, `--g-days` arguments are gone (the pilot measures at the C2 constants).

Not repaired: none.

Validation: full screen suite (screen, event contract, deploy, feature columns) 185 passed in 145 s with `-W error::FutureWarning`; ruff check and format clean; mypy clean; lint-imports 6 kept, 0 broken.
