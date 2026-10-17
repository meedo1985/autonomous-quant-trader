# Adjudication of the Sol review of screen S8 at 042c8da

Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Review record: `SOL6_SCREEN_S8_REVIEW_042C8DA.md`.

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S8-R1 | High | **Accept.** Under `set -e`, `stop` exited at the absent calibration container. | `stop` stops each D-19 container that is up, independently, and says if none was. |
| S8-R2 | Medium | **Accept.** Both runs share `aqt-d19.slice`. | New `alone` guard: `run` and `screen-pilot` refuse while either D-19 container is up, so the runs never compete under the cap. The calibration `status` labels the slice peak as shared by all D-19 runs since the slice started; `screen-status` reports the screen container's own `memory.peak`. |
| S8-R3 | Medium | **Accept.** | The summary starts with `MEASUREMENT ONLY (prereg §10 pilot): gate results are availability, not passes; ...` and prints `G-n:available` for an available gate. Test updated. |
| S8-R4 | Medium | **Accept.** | Step 0 checks that `app-<old>` does not exist and that `<old>` is `e39b23d` before moving, and lists `/opt/aqt-d19` afterwards. |

Reviewer's cost note accepted: the sheet now states that the 15-hour estimate holds for this mix only (20 LightGBM trials ≈ 100 hours) and that the result is reported per kind of trial, not per set size.

The sheet names engine commit `e4e7339` (the repaired launcher and summary); the sheet itself is a later commit and is not part of the installed code's behaviour.

Not repaired: none.

Validation: full screen suite 188 passed (`-W error::FutureWarning`); `sh -n d19.sh` clean; ruff, mypy clean.

## Re-review at 85022c3 (`SOL6_SCREEN_S8_REREVIEW_85022C3.md`)

| ID | Decision | Repair |
|---|---|---|
| S8R-R1 | **Accept.** | `up` lists running D-19 engine containers and turns a failed docker query into `FAIL: cannot query docker`; every caller checks its status explicitly (a failure inside `$(...)` or an `if` condition would not stop the script by itself); `stop` reports a failed stop. Checked with a failing `docker` stub: `stop` and `screen-pilot` exit 1 with the FAIL line. |
| S8R-R2 | **Accept.** | `engine` labels every container `aqt-d19-run=1`; `alone` refuses while any labelled container is up and guards `run`, `clean-check` and `screen-pilot`; `stop` stops every labelled container. |
| S8R-R3 | **Accept.** | Step 0's destination check prints an explicit `ok: app-e39b23d is free` or `STOP: ...` line (no failing command); the sheet says which line carries the old commit. The sheet names the repaired engine commit `336e322`. |

## Re-review 2 at 4705c39 (`SOL6_SCREEN_S8_REREVIEW2_4705C39.md`)

| ID | Decision | Repair |
|---|---|---|
| S8R2-R1 | **Accept.** | New `lock`: `flock -n` on `$WORK/engine.lock`, taken once per script and held until it exits, then `alone`. `engine` and `probe` call it first, so every engine run (foreground or detached, including `timing`, `record`, `choose`, `nonfinite`, `manifests`, `screen-summary`) checks and starts under one lock; `run`, `screen-pilot` and `clean-check` take it before their own steps (`clean-check` holds it across both its runs). A detached run outlives the lock, and the next `alone` sees it. Unit test checks that `engine` and `probe` lock first. |
| S8R2-R2 | **Accept.** | `alone` also counts processes in `aqt-d19.slice` (`busy`: every `cgroup.procs` under the slice's control group; an inactive slice holds nothing; a read failure is FAIL), so a container without the label is seen too. A CI step starts an unlabelled container in the slice and checks that `timing` is refused. Step 0 of the sheet runs the same count with the old launcher still installed and must print `ok: no D-19 process is running` before the move. |
| S8R2-R3 | **Accept.** | `stop` attempts every labelled container, reports each failure, and exits 1 at the end if any failed. Checked with a docker stub where the first stop fails: `FAIL: could not stop aaa`, `stopped bbb`, exit 1. |

The sheet names engine commit `ebdf208` (`ebdf20806a0e59bde9305bc052a18c98fd3a7b33`).

Not repaired: none.

Validation: `tests/unit/test_d19_deploy.py` 6 passed; `sh -n d19.sh` clean; ruff check and format clean. `flock` and the slice count need Linux and are exercised by the CI `calibration-launcher` job.
