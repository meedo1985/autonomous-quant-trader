# Task 15 local implementation and gate report

Date: 2026-09-26
Base commit: `69e71e1` (`main`)
Branch: `task15-data-quality-report`
Author and reviewer: Claude Opus 5.5 (`claude-opus-5-5`), coding AI. This is a
**self-review**, not an independent one.

## Authority

Task 15 is authorized by the owner's roadmap approval
(`review/roadmap/OWNER_APPROVAL.md`). The roadmap lists no blocking decision
for it. It reads only the exploration partition and binds nothing.

## Scope

- `src/aqt/data/quality.py` (new): `render_report`, a pure function of Task
  14's `ExplorationBuild`s (manifest, parsed bars, outage rows).
- `scripts/data_quality_report.py` (new): rebuilds each manifest from the raw
  archives, refuses unless it is byte-identical to the one Task 14 recorded,
  and writes the report write-once (line-ending-insensitive comparison, so a
  CRLF checkout of the committed report reruns as unchanged).
- `tests/unit/test_data_quality.py` (new): 7 synthetic tests.
- `review/task15/DATA_QUALITY_REPORT.md` (new): the generated evidence, 381
  lines, from the real exploration data.

Size: 805 added lines, of which 381 are the generated report; code and tests
are about 424, near the roadmap's ~400 target.

## What the report shows (real exploration data)

| Symbol | Hourly bars | Declared gaps | Gap hours | Coverage |
|---|---|---|---|---|
| BTCUSDT | 38166 | 31 | 186 | 99.515 % |
| ETHUSDT | 38166 | 31 | 186 | 99.515 % |

Declared gaps are identical across the symbols. Per symbol it lists the three
hashes (manifest `5f92ec50…` / `a587081e…`, parsed bars, parser code), all 31
outage windows, all 56 outage rows with reasons, coverage for each of the 53
months, and fees, exchange filters and symbol status as `UNAVAILABLE` with
reasons (T13-01). It contains no prices.

## Acceptance criteria (roadmap Task 15)

| # | Criterion | Evidence |
|---|---|---|
| 1 | Pure function of manifest plus bars; two runs byte-identical | `test_report_is_deterministic` (two independent builds); real-data rerun reported `unchanged` |
| 2 | Every `Gap` appears in the outage table | `test_every_gap_appears_in_the_outage_table`; each month's bars + gap hours must equal its hours or rendering raises (`test_monthly_coverage_accounts_for_every_hour`) |
| 3 | Refuses to emit if the manifest hash does not verify | `test_refuses_when_the_manifest_does_not_verify` (flipped manifest hash; bars that do not match the manifest) |
| 4 | No sample-size claim; no statistic beyond counts, coverage fractions, timestamps | `test_report_states_no_statistic_and_no_prices`: whole-word check for statistical terms, no prices, every decimal is a 3-place coverage figure. Same check run on the real report: no forbidden term, no other decimal. **Corrected:** this claim was false; the report's millisecond timestamps also contain decimals. See `ADJUDICATION.md` R-4. |

Also: symbol ordering and the gap-agreement statement, and the CLI's
recorded-manifest check and write-once behavior
(`test_cli_checks_recorded_manifests_and_is_write_once`).

## Validation

Environment: Windows 11, `.venv` Python 3.14.7.

| Command | Exit | Result |
|---|---|---|
| `python -m pytest -q` | 0 | 1253 passed, 4 pre-existing skips |
| `ruff check .` | 0 | all checks passed |
| `ruff format --check .` | 0 | 72 files already formatted |
| `mypy src scripts/download_market_data.py scripts/build_manifests.py scripts/data_quality_report.py` | 0 | no issues in 36 source files |
| `lint-imports` | 0 | 5 kept, 0 broken |
| `git diff --check main...HEAD` | 0 | clean (run after commit) |

Frozen verification: `git diff main` over `docs/`, `protocols/`, `schemas/`,
`specs/`, `FROZEN_HASHES.json` and its sidecar is empty.

## Findings (self-review)

- **T15-01 NON-BLOCKING, implementer error caught in-session.** While fixing
  the content check to match whole words, an edit script turned the regex's
  `\b` into literal backspace characters, which made the check unable to match
  anything; the test then passed vacuously. It was noticed on inspection and
  repaired before commit. The committed check was confirmed to catch
  `sample size`, `Sharpe`, `mean`, `ESS`, `returns` and `std` and to ignore
  `postdates`, `Missing archives`, `process`, `address` and `untradeable`.
- **T15-02 NON-BLOCKING.** Section 23's requirements for decision
  reports (raw decisions, overlap factor, ESS, trial counts, benchmark, costs)
  do not apply: this is a data report with no decisions. It states only what
  the roadmap asks for.
- **T15-03 NON-BLOCKING.** The report is committed evidence derived from real
  exploration data. It holds counts and timestamps only, no prices or raw rows.

## Gate

LOCAL GATE: PASS. Independent review status: `NOT SENT`.
