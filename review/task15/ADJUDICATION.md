# Task 15 review adjudication

Review: `review/task15/REVIEW.md`, saved unedited from the reviewer's reply.
Reviewer: GPT-6 Astra (`gpt-6-astra`, reasoning effort high), Codex CLI 0.154.0,
session `01a0ddaa-9b40-7ad3-9f8d-1ab435d34541`, read-only sandbox, no tools,
2026-09-26. Input: the full `main...HEAD` diff (including `LOCAL_REPORT.md` and
the generated report), implementer-run check output at `f7b0e0d`, a real-data
regeneration that reported `unchanged`, and the unchanged `ExplorationBuild`
source. The reviewer did not rerun the checks. Verdict: **FIX**.
Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the implementing model.

| ID | Severity | Adjudication | Evidence |
|---|---|---|---|
| R-1 | BLOCKER | **Accepted, reproduced.** | `_percent` divides and quantizes in the caller's ambient `decimal` context. Rendering the same synthetic build under `decimal.localcontext()` with `ROUND_DOWN` printed `1.209 %` where the default printed `1.210 %`. |
| R-2 | BLOCKER | **Accepted, reproduced.** | `render_report` verifies the manifest against its bars but trusts `outage_rows`, `missing_archives` and `bars_outside_window`. `dataclasses.replace(build, outage_rows=(), missing_archives=(), bars_outside_window=0)` rendered without error and printed `Outage rows excluded \| 0`. The committed real report is unaffected, because the CLI rebuilt every build from the raw archives, but the function's contract does not hold. |
| R-3 | NON-BLOCKING | **Accepted.** | `ZipFile.writestr` with a member name stamps the current local time into the archive, so two fixture builds that straddle a two-second boundary have different archive bytes and manifest hashes. |
| R-4 | NON-BLOCKING | **Accepted; a false statement in the implementer's record.** | `LOCAL_REPORT.md` says every decimal in the real report is a coverage figure. The outage-row table holds millisecond timestamps such as `12:29:13.419`, whose `13.419` matches the test's decimal pattern; the check passed only because it tests width, not meaning. A labelled statistic such as `Skewness: 1.234` would also pass it. |

All four are repaired below.

## Repairs (Claude Opus 5.5, 2026-09-26)

| ID | Change | Regression test |
|---|---|---|
| R-1 | `_percent` divides and quantizes in a fixed module context (`prec=28`, `ROUND_HALF_EVEN`), never the ambient one. | `test_coverage_ignores_the_ambient_decimal_context` renders under `ROUND_DOWN` with precision 2 and requires identical output. With the old `_percent` restored in the new module, it is the only test that fails. |
| R-2 | `render_report(raw_root, recorded_manifests)` now takes only the raw archive root and the recorded manifest bytes. It builds every symbol itself, refuses unless the rebuilt manifest equals the recorded bytes, and takes outage rows and missing archives from that same build. A caller can no longer pass, or omit, outage evidence. The CLI now only reads the recorded manifests and calls it. | `test_refuses_unless_the_recorded_manifest_matches`, `test_report_takes_no_caller_supplied_evidence`, and `test_every_gap_and_outage_row_appears` (the outage row derived from the archive is in the report). |
| R-3 | Fixture archives use a fixed `ZipInfo` timestamp. | Every test uses the fixed-timestamp fixture; `test_report_is_deterministic` builds twice in separate directories. |
| R-4 | The content check now reads the report's structure: after removing timestamps, a decimal may appear only as a three-place percentage in a `Coverage` column or the `Coverage` row of a field table; any decimal in prose fails. The false sentence in `LOCAL_REPORT.md` is marked as corrected in place. | `test_report_states_no_statistic_and_no_prices`, and `test_content_check_catches_a_planted_statistic`, which plants `\| Skewness \| 1.234 % \|`, a fractional bar count, and `Skewness: 1.234` in prose; each is flagged. The real report passes the new check. |

Real report: regenerated with the repaired code; the CLI reported `unchanged`,
so the committed report is byte-identical.

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1258 passed, 4
skipped; `ruff check .` pass; `ruff format --check .` 72 files formatted;
`mypy src` and the three scripts: no issues in 36 files; `lint-imports` 5
kept, 0 broken; `git diff --check main...HEAD` clean (after commit); no change
under the frozen paths.

These repairs have not been re-reviewed by a different model.
