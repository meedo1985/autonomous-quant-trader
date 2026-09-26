# Task 16 local implementation and gate report

Date: 2026-09-26
Base commit: `5fda787` (`main`)
Branch: `task16-research-harness`
Author and reviewer: Claude Opus 5.5 (`claude-opus-5-5`), coding AI. This is a
**self-review**, not an independent one.

## Authority

Roadmap Task 16, approved in `review/roadmap/OWNER_APPROVAL.md`. It was blocked
by Q1 until the owner signed the section 25 acknowledgment on 2026-09-26
(`review/pre-deployment/S25_SIGNATURE_RECORD.md`). The owner said "start task 16"
on 2026-09-26.

## Scope

- `src/aqt/research/harness.py` (new, 234 lines): `run_exploration`,
  `HarnessConfig`, `HarnessResult`, `RunResult`, `SkippedRun`, `HarnessError`.
- `src/aqt/research/__init__.py`: exports.
- `tests/integration/test_research_harness.py` (new, 7 tests, synthetic data).

No existing module, frozen artifact, or import contract changed. The existing
contract "Research cannot reach protected runtime or lockbox packages" covers
the new submodule, so `pyproject.toml` needed no change. No real data was run.

## Design

`run_exploration(manifest, load, config)`:

1. Refuses any partition other than `exploration` with `HarnessError`
   **before** `load` is called.
2. Calls `load(manifest)` and checks the bars with
   `verify_partition_manifest(manifest, series=...)`, so a run is bound to
   the manifest's parsed hash.
3. Splits the bars into contiguous runs. Each run long enough for the
   benchmark's warm-up is backtested separately, starting flat, with
   `benchmark_signals` -> `ExposureTarget` -> `run_backtest` -> `describe`.
   Shorter runs are listed in `skipped_runs` with a reason.
4. Returns `HarnessResult`, which is marked `NOT_A_REGISTERED_TRIAL`. It has an
   exact `as_mapping()` (floats as `float.hex`) and a SHA-256 `digest()`.

Configurations are the five canonical benchmarks plus a cost stress
multiplier. No model class is implemented.

### Deliberate differences and limitations

- **T16-01. `features.factory` is not composed.** The roadmap lists it, but no
  permitted configuration consumes features: the canonical benchmarks compute
  their own signals, and no model class exists before its scheduled task.
  Adding an unused feature pass would only add computation.
- **T16-02. Gaps split the run, and each part starts flat.** The backtester and
  the benchmarks require contiguous history (Constitution section 6: nothing is
  filled). So exposure never carries across a gap. On the real exploration
  data (31 gaps per symbol), `CANONICAL_TREND` needs 4800 contiguous bars, so
  every shorter run is skipped and reported.
- **T16-03. Vol-target runs are slow.** `annualized_forecast_volatility`
  (existing code, via `costs.ewma_hourly_volatility_bps_series` and
  `statistics.variance`) costs about 0.1 s per decision. So a full
  exploration-window run of `VOL_TARGET_BUY_AND_HOLD` would take on the order of
  an hour. It is not optimized here, because that code is outside this task.
- **T16-04. Task 17 (job log) is not folded in.** It stays a separate task.

## Acceptance criteria (roadmap Task 16)

| # | Criterion | Evidence |
| --- | --- | --- |
| 1 | Deterministic across two runs and two processes | `test_a_run_is_deterministic_across_runs_and_processes` (digest equal in-process and in a subprocess) |
| 2 | Confirmation or lockbox manifest raises before data is read | `test_other_partitions_are_refused_before_data_is_read` (loader call list stays empty) |
| 3 | No ledger attempt record, no trial registered | `test_no_attempt_or_ledger_entry_is_written` (`start_attempt` and `append_entry` patched to fail; no `aqt.core`, `aqt.validation` or `aqt.lockbox_eval` import) |
| 4 | `lint-imports` passes with the research contract intact | 5 contracts kept, 0 broken |
| 5 | Descriptive metrics only; promotion-statistic keys rejected | `test_the_result_exposes_descriptive_metrics_only` (key scan plus exact field set) |

Also: `test_bars_that_do_not_match_the_manifest_are_refused` and
`test_each_contiguous_run_is_backtested_and_short_runs_are_reported`.

Mutation checks: removing the partition check fails 2 tests; removing the
manifest verification fails 1 test.

## Validation

Environment: Windows 11, `.venv` Python 3.14.7.

| Command | Result |
| --- | --- |
| `pytest -q` | 1367 passed, 4 skipped in 193.17s |
| `ruff check .` | All checks passed (after wrapping two long lines) |
| `ruff format --check .` | 81 files already formatted (after formatting `harness.py`) |
| `mypy src scripts` | Success: no issues found in 41 source files |
| `lint-imports` | Contracts: 5 kept, 0 broken |
| `git diff --check main...HEAD` | clean |

Frozen verification: `git diff --name-only main` over `docs`, `protocols`,
`schemas`, `specs` and `FROZEN_HASHES.json` is empty.

## Reproducibility and quant review (self)

- Deterministic: no clock, randomness, file or network access in the harness;
  data enters only through `load`, and is checked against the manifest.
- Causal: signals come from `benchmark_signal`, which reads only bars closed
  at or before each decision; fills are at the next open (frozen engine).
- No data deleted or corrected; short runs are reported.
- No statistic beyond `DescriptiveMetrics` is computed.

## Outstanding

- An independent review by a different model has not been done.
- **QUESTION T16-Q1 (owner):** section 16 lists "protocol-enforcement logic"
  among the components that need a different-model and a human PR review. The
  harness's refusal of non-exploration partitions enforces section 7a, so it
  may fall under that heading. The roadmap does not say so, and the AI does not
  decide it. Treating it as protected (a different-model review plus the
  owner's own review before merge) is the cautious reading.
