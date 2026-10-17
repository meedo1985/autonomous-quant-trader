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

## Re-review 2 at 8f40348 (`SOL6_SCREEN_S7_REREVIEW2_8F40348.md`)

| ID | Decision | Repair |
|---|---|---|
| S7R-R1 (still open) | **Accept.** Exact-string comparison missed aliases. | `_extend_path` compares `os.path.realpath` of every entry; any spelling of the engine or trial-code directories is removed before placing them. Test `test_an_alias_of_the_trial_code_directory_is_moved_last` (a `..` detour). |
| S7R2-R1 | **Accept.** Cleanup unlinked by name. | The CLI records the reserved file's `(st_dev, st_ino)` and removes the path only if it still names that file. Test case (POSIX only: Windows cannot replace an open file, so the race cannot arise there). |

## Re-review 3 at da1eaad (`SOL6_SCREEN_S7_REREVIEW3_DA1EAAD.md`): S7R2-R1

Accepted, by removing destination cleanup altogether. The CLI refuses an existing destination before any work, writes the record to a private `mkstemp` file beside it, and publishes with `os.link` (atomic create-if-absent); the `finally` removes only the private file, never the published path. A file created at the destination during the screen makes publishing fail and is left untouched. Test cases: refusal before work, a file created meanwhile (kept, no `.partial` left), a successful publish.

## Re-review 4 at 1304d7b (`SOL6_SCREEN_S7_REREVIEW4_1304D7B.md`)

| ID | Decision | Repair |
|---|---|---|
| S7R4-R1 | **Accept, by removing the temporary file.** The threat assumes another writer in the run directory, which on the server is root; still, a simpler design closes it. | `reserve` claims the destination with `open("xb")` (O_CREAT \| O_EXCL) before any work and the record is written through that handle; no temporary file, no link, no rename. |
| S7R4-R2 | **Accept.** | The exclusive claim before work is a reservation: a second run is refused at once. Test case. |
| S7R4-R3 | **Accept.** | O_EXCL fails on any existing entry, a dangling symlink included, so the refusal is before work. |

Nothing is ever deleted: a run that fails after its claim leaves the empty claimed file, which the owner removes by hand before a rerun (the CLI's message says so). Test cases: existing file refused before work, a second claim refused, a failed run leaves an empty file, a successful run writes through its claim.
