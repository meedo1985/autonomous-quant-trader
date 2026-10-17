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
