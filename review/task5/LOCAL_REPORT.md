# Task 5 — canonical benchmarks: local implementation report

Executed by Claude Opus 5 (`claude-opus-5`) on 2026-09-12 under explicit user
authorization to implement **Task 5 only**. The authorization text is preserved
verbatim at `review/task5/authorized-spec.txt`.

**EXTERNAL REVIEW: DEFERRED UNTIL USAGE RESET.**
No independent-model review, adversarial review, or adjudication was run for
Task 5. Task 5 is **not** externally reviewed. Nothing in this report is an
independent sign-off; it is the implementing model's own account of its own
work. `AGENTS.md` requires `task-gate-review`,
`scientific-reproducibility-review`, `quant-code-review` and a
`claude-adversarial-review` packet before a task is declared complete; those
gates remain **OPEN** for Task 5 by the user's instruction.

## Scope

Implemented: pure, deterministic, causal signal and exposure definitions for
the five canonical benchmarks in `specs/CANONICAL_BENCHMARKS_v1.md` — `CASH`,
`BUY_AND_HOLD`, `VOL_TARGET_BUY_AND_HOLD`, `CANONICAL_TREND`,
`CANONICAL_TSMOM` — plus the shared scheduling / rebalance-band /
minimum-hold decision rule, built on the Task 2 bar semantics
(`src/aqt/data/bars.py`), the approved Task 3 volatility convention
(`src/aqt/backtest/costs.py`, `review/task3/SCIENTIFIC_DECISION.md`) and the
Task 4 feature factory (`src/aqt/features/factory.py`), plus synthetic unit
tests.

Explicitly **not** implemented, per the authorization's exclusions: a full
backtester; any performance, metric, eligibility or promotion engine; null
models; live, exchange or network access; Binance credentials; trading or
execution; ML or LLM code; the research engine; the lockbox; the governor;
allocation orchestration; and all Task 6+ work. No PnL, turnover, cost
application, fill resolution, or capital accounting appears anywhere in the
new module: `rebalance` decides a target-exposure path and nothing else.

## Frozen sources honoured

| Frozen requirement | Source | Where encoded |
|---|---|---|
| `CASH`: exposure = 0 | `CANONICAL_BENCHMARKS_v1.md` "CASH" | `cash_exposure`, `MIN_EXPOSURE` |
| `BUY_AND_HOLD`: 100% at the first eligible execution, then hold | "BUY_AND_HOLD" | `buy_and_hold_exposure` (constant target) + `rebalance` (when it may first act) |
| `VOL_TARGET_BUY_AND_HOLD`: EWMA of hourly log returns, half-life 168h, `sqrt(8760)` annualisation, target 0.60, `clip(0.60 / vol, 0, 1)` | "VOL_TARGET_BUY_AND_HOLD" | `VOL_TARGET_HALF_LIFE_HOURS`, `ANNUALIZATION_HOURS`, `VOL_TARGET_ANNUALIZED`, `annualized_forecast_volatility`, `vol_target_exposure` |
| `CANONICAL_TREND`: `close > 200-day SMA` → 1 else 0 | "CANONICAL_TREND" | `TREND_SMA_DAYS = 200`, `TREND_SMA_WINDOW = 4800`, `trend_reference`, `canonical_trend_exposure` |
| `CANONICAL_TSMOM`: trailing 180-day log return `> 0` → 1 else 0 | "CANONICAL_TSMOM" | `TSMOM_LOOKBACK_DAYS = 180`, `TSMOM_LOOKBACK_HOURS = 4320`, `tsmom_lookback_return`, `canonical_tsmom_exposure` |
| Parameters are fixed and not tunable in Cycle 1 | spec final line | every parameter is a module `Final`; no function takes a window, half-life, or target as an argument |
| 1h bars | shared rules; `protocol_v1.yaml` `scope.bar_interval` | `BAR_INTERVAL` from `aqt.data.bars`; non-1h series rejected |
| Same bar-semantics module as candidates | shared rules | `aqt.data.bars` is the only timestamp authority used |
| Same scheduled 00:00 UTC evaluation | shared rules; `scope.scheduled_decision_anchor_utc` | `SCHEDULED_DECISION_ANCHOR_HOUR_UTC`, `is_scheduled_decision`, `BenchmarkSignal.scheduled` |
| Same 10pp rebalance band | shared rules; `exposure_mapping.rebalance_band_absolute` | `REBALANCE_BAND_ABSOLUTE = 0.10` |
| Risk increases respect the 24h minimum hold | shared rules; `exposure_mapping.minimum_holding_hours_for_risk_increase`; `scope.risk_increase_rule` | `MINIMUM_HOLD_FOR_RISK_INCREASE`, `rebalance` |
| Intraday band-triggered actions only reduce exposure | shared rules; `scope.intraday_action_rule` | `rebalance` (`RebalanceAction.INTRADAY_REDUCTION` only) |
| Exposure clipped to `[0, 1]`; long-only unlevered spot | `BACKTESTER_SPEC_v1.md` item 3; `scope.market`, `scope.max_exposure_per_asset` | `MIN_EXPOSURE`, `MAX_EXPOSURE`, `_require_exposure`, `_clip_exposure` |
| Decision at close(t) | `BACKTESTER_SPEC_v1.md` item 2 | `_history_through`, `BenchmarkSignal.decision_time` |
| `VOL_TARGET_BUY_AND_HOLD` is the predeclared comparator | `comparison.promotion_benchmark`, `benchmarks.deployable_baseline` | `PROMOTION_BENCHMARK` (recorded only; no comparison logic implemented) |
| Benchmark set is closed and hash-bound | `benchmarks.benchmark_set_hash`, `promotion.benchmark_hash_must_match` | `BenchmarkId`, `BENCHMARK_SET`, `require_canonical_benchmark`; asserted element-by-element in tests |
| Same cost model as candidates | shared rules | the Task 3 estimator is reused unchanged; **no cost is applied here** — cost application is the backtester's job |
| Causal time semantics, no future leakage, UTC only, no silent deletion/correction, one bar-semantics module | `RESEARCH_CONSTITUTION.md` section 6 | see "Properties enforced" |

`specs/CANONICAL_BENCHMARKS_v1.md`, `specs/BACKTESTER_SPEC_v1.md`,
`protocols/protocol_v1.yaml` and `docs/RESEARCH_CONSTITUTION.md` were read
directly; no frozen file was modified.

## Shared semantics reused rather than re-derived

- `CANONICAL_TREND` calls `aqt.features.factory.simple_moving_average` with
  `SMA_WINDOW`, so the frozen "200-day simple moving average" is the same
  number as the Task 4 `sma_4800` feature by construction. A test asserts
  `TREND_SMA_WINDOW == SMA_WINDOW`.
- `CANONICAL_TSMOM` calls `aqt.features.factory.log_return`.
- `VOL_TARGET_BUY_AND_HOLD` calls `aqt.features.factory.ewma_volatility`,
  which delegates to the Task 3 estimator
  `aqt.backtest.costs.ewma_hourly_volatility_bps`. The benchmark's volatility
  forecast is therefore identical to the `ewma_vol_168h` feature and to the
  protocol's `EWMA_168h` sizing estimator by identity, not by claim, as
  `review/task3/SCIENTIFIC_DECISION.md` item 5 requires. A test asserts exact
  floating-point equality with the shared function, and a second test checks
  the value against a hand-written transcription of the frozen recursion.

## Properties enforced

- **Causality.** A signal is computed at a decision timestamp that is a bar
  close in the Task 2 sense (`decision_time == open_time(t) + 1h`). Only bars
  whose close is at or before the decision are read, so bar `t` is the last
  observation used. No fill is resolved here; baseline execution at open(t+1)
  stays in Tasks 2 and 3.
- **No future leakage.** Appending 48 extreme future bars cannot change an
  already-computed signal (tested for all five). A signal computed on a series
  truncated at the decision bar equals the signal on the full series (tested
  for all five). A hole strictly *after* the decision bar is irrelevant
  (tested for all five).
- **Warm-up.** Each benchmark declares its own requirement in
  `REQUIRED_HISTORY_BARS_BY_BENCHMARK` — `CASH` 1, `BUY_AND_HOLD` 1,
  `VOL_TARGET_BUY_AND_HOLD` 169, `CANONICAL_TREND` 4800, `CANONICAL_TSMOM`
  4321 — and `REQUIRED_HISTORY_BARS` is the binding maximum, 4800. Exactly the
  requirement is accepted and one bar short is rejected, per benchmark.
- **Gap rejection.** Any hole in the supplied history up to and including the
  decision bar raises. Nothing is forward-filled, interpolated, dropped,
  reset, or silently sliced to a post-gap segment, per
  `review/task3/SCIENTIFIC_DECISION.md` item 4.
- **Exposure bounds / no shorting.** Every target lies in `[0, 1]`; a caller
  supplying exposure outside `[0, 1]` is rejected rather than clipped; the
  only clip performed is the frozen `clip(0.60 / vol, 0, 1)`. `rebalance`
  never produces an exposure outside `[0, 1]` and never returns anything other
  than the prior or the target exposure.
- **Scheduled timing.** `rebalance` raises exposure only at a 00:00 UTC
  decision and only when at least 24h have elapsed since the last risk
  increase; intraday actions are reductions only; changes inside the 10pp band
  are not acted on. A 48-decision walk over each benchmark asserts these
  invariants hold step by step, without a backtester.
- **Purity/determinism.** No clock, no randomness, no I/O, no global mutable
  state. Results are frozen slotted dataclasses; inputs are never mutated.
  Repeated computation, an independently rebuilt identical series, and
  reversed decision order all produce equal results (tested).
- **Forbidden inputs.** Only `close` (and, through `aqt.data.bars`, the
  timestamp) is read. `Bar.volume` enters no benchmark: volumes of `0.0` and
  `1e9` give bit-identical signals (tested for all five). No timestamp is
  decomposed into a calendar term: shifting the whole series by 4321 hours
  leaves every signal value bit-identical (tested for all five).
- **No silent correction.** Invalid input raises `CanonicalBenchmarkError`.
  Functions that resolve a decision re-raise the underlying
  `BarSemanticsError` as `CanonicalBenchmarkError`, matching the Task 3/4
  convention; `ExposureState.last_risk_increase_time` is a bare timestamp, so
  its `BarSemanticsError` surfaces unchanged.

## Conventions the frozen spec leaves open

Documented, not silently taken. None changes a frozen formula, window,
half-life, target, band, or annualisation constant. They are also recorded in
the module docstring of `src/aqt/benchmarks/canonical.py`.

1. **The 10pp band applies to every rebalance**, scheduled and intraday, not
   only to intraday reductions. `CANONICAL_BENCHMARKS_v1.md` lists the band
   among the shared rules ("the same 10 percentage-point rebalance band where
   relevant") while `protocol_v1.yaml` `scope.intraday_action_rule` fixes it
   explicitly only for intraday reductions. The uniform reading is the
   lower-turnover one and never manufactures a trade the narrower reading
   would forbid. It binds only for `VOL_TARGET_BUY_AND_HOLD`; every other
   benchmark targets exactly 0 or 1, so any change it requests is 1.0.
2. **A permitted rebalance moves to the target in full**, not to the near edge
   of the band. The frozen documents name a band, not a partial-adjustment
   rule.
3. **A zero annualised forecast volatility yields full exposure**, the limit
   of `clip(0.60 / vol, 0, 1)` as `vol -> 0+`. The division is not performed,
   so there is no `ZeroDivisionError` and no silently defaulted value; the
   zero forecast is reported through `BenchmarkSignal.signal`. A negative
   forecast is impossible from a standard deviation and is rejected.
4. **Trend and momentum use the strict comparison directly.**
   `CANONICAL_TREND` maps `close > sma_4800` and `CANONICAL_TSMOM` maps
   `log(close_t / close_{t-4320}) > 0`, both strict as written.
   `BenchmarkSignal.signal` carries a comparable scalar for audit
   (`close / sma_4800 - 1` and the 180-day log return), but exposure never
   depends on that derived scalar's floating-point sign.
5. **The 24h minimum hold gates risk increases only.** Reductions are never
   blocked by it, consistent with
   `owner_change_control.risk_decrease_immediate = true`, and a reduction does
   not restart the clock.
6. **"200-day" and "180-day" are 4800 and 4320 1h bars**, using the same
   `days x 24` arithmetic `specs/FEATURE_FACTORY_v1.md` already uses for
   `sma_4800`.
7. **Contiguity is checked over the whole supplied history** through the
   decision bar, not only over the trailing window a benchmark reads. A hole
   therefore also refuses `CASH` and `BUY_AND_HOLD`, whose exposure needs no
   history. This is deliberate: silently accepting a series known to be
   broken, or quietly reading only the post-gap tail, is what
   `review/task3/SCIENTIFIC_DECISION.md` item 4 forbids.

### Flagged for owner/reviewer attention

- **`rebalance` is a rule, not an engine.** It is a single-step pure function
  of `(state, target, decision_time)`. No loop, path builder, PnL, cost, or
  turnover accounting is provided, so it is not a backtester and cannot be
  mistaken for one. Whether the shared scheduling rules belong in
  `aqt.benchmarks` at all, or should later move to the backtester module and
  be imported by both candidates and benchmarks, is an architecture question
  for the owner. They are here because `CANONICAL_BENCHMARKS_v1.md` states
  them as part of the benchmark definitions, and because the authorization
  asked for causal decision timing and exposure bounds to be preserved.
- **Convention 1 (band on scheduled decisions) is the one substantive reading
  a reviewer might dispute.** If the owner reads the band as intraday-only,
  `VOL_TARGET_BUY_AND_HOLD` would rebalance to target at every 00:00 UTC
  decision regardless of size. That is a one-line change in `rebalance`; it is
  flagged rather than buried.
- **New import edges.** `aqt.benchmarks -> aqt.data` and
  `aqt.benchmarks -> aqt.features`. `aqt.features -> aqt.backtest` already
  exists from Task 4 and was flagged there; this task inherits it rather than
  adding to it. Neither new edge crosses any of the four `import-linter`
  contracts in `pyproject.toml`.

## Changed files

| File | Change |
|---|---|
| `src/aqt/benchmarks/canonical.py` | new — canonical benchmark signal/exposure definitions and the shared scheduling rule (stdlib only; imports `aqt.data.bars` and `aqt.features.factory`) |
| `tests/unit/test_canonical_benchmarks.py` | new — 105 synthetic test functions |
| `review/task5/authorized-spec.txt` | new — preserved Task 5 authorization |
| `review/task5/LOCAL_REPORT.md` | new — this report |

No frozen governance file, sidecar, schema, protocol, specification,
`FROZEN_HASHES.json` entry, `pyproject.toml` contract, CI workflow, or
pre-commit configuration was modified. No dependency was added; the module
uses only `math`, `collections.abc`, `dataclasses`, `datetime`, `enum` and
`typing`.

## Test coverage of the required categories

| Required by the authorization | Tests |
|---|---|
| Fixed identities and parameters | all five identities checked against expectations computed inside the test file — a hand-written EWMA transcription, an independent `fsum` mean, an independent log return — plus analytic checks on rising, falling, flat and high-volatility synthetic paths; every frozen constant (0.60, 168, 8760, 200/4800, 180/4320, 0.10, 24, 00:00, 0/1 bounds) asserted; `vol_target_exposure` checked on a table of forecasts including the clip at both ends |
| Causal decision timing | `decision_time` equals the decision bar's `close_time` and `open_time + 1h`; the decision bar is included; `scheduled` is true only at 00:00 UTC; `is_scheduled_decision` checked across the day and on unaligned/naive input |
| Exposure bounds / no shorting | every target in `[0, 1]` across benchmarks, hours and paths; `BenchmarkSignal` and `ExposureState` reject exposure outside `[0, 1]` and non-finite exposure; `rebalance` rejects out-of-bounds targets and never leaves `[0, 1]` over a 5x5x2 sweep |
| Deterministic outputs | repeated evaluation equal; independently rebuilt series equal; `benchmark_signals` order-independent; input series not mutated; volume-invariance; 4321-hour time-shift invariance |
| Benchmark set completeness | `BENCHMARK_SET` asserted element-by-element and equal to the full enum, with the frozen spellings; every member has a signal label and a warm-up entry; `require_canonical_benchmark` rejects six near-miss names |
| Insufficient / gapped history rejection | exactly the requirement accepted and one bar short rejected, per benchmark; early decision inside a long series rejected; the reported shortfall names the actual count; hole mid-history, hole immediately before the decision, and a post-gap segment all rejected; duplicate open times, unaligned, naive, non-UTC and unknown decision timestamps, and a non-1h series all rejected; helper-level warm-up rejection for SMA, TSMOM and the volatility forecast |
| No future leakage | truncation at the decision bar changes nothing; 48 appended extreme bars change nothing; a hole after the decision bar is irrelevant — each for all five benchmarks |
| Shared scheduling / band / min-hold | cold-start scheduled increase; `BUY_AND_HOLD` first eligible entry only at 00:00 UTC; intraday increase refused; intraday and scheduled reductions across the band allowed; changes inside the band refused; exact-boundary change acted on; min-hold blocks at 1/12/23h and permits at 24/25/48/1000h; min-hold never blocks a reduction and a reduction does not restart the clock; a future `last_risk_increase_time` rejected; a 48-decision walk per benchmark |

## Commands executed in this session

| Exact command | Exit | Result |
|---|---:|---|
| `sha256sum -c review/task1/protected-before.sha256sums` | 0 | **PASS** — 28/28 frozen governance files and sidecars byte-identical, including `specs/CANONICAL_BENCHMARKS_v1.md`, `specs/CANONICAL_BENCHMARKS_v1.md.sha256`, `specs/BACKTESTER_SPEC_v1.md`, `protocols/protocol_v1.yaml` and `FROZEN_HASHES.json` |
| `sha256sum -c --quiet review/task1/reviewed-files-final.sha256sums` | 1 | **Expected** — only `README.md` FAILED; that is the authorized Task 2 documentation update recorded in `review/task2/LOCAL_REPORT.md`. All other reviewed files byte-identical |
| `git diff --check` | 0 | **PASS** — no whitespace errors |
| `git status --porcelain --untracked-files=all` | 0 | only the intended new paths; no tracked file modified |
| `od -c src/aqt/benchmarks/canonical.py \| tail -2` | 0 | file ends with exactly one `\n`, LF endings |
| `od -c tests/unit/test_canonical_benchmarks.py \| tail -2` | 0 | file ends with exactly one `\n`, LF endings |

Line lengths in both new files were checked mechanically against the 88-column
`ruff` limit (`^.{89,}$` — no matches), and both were checked for trailing
whitespace (`[ \t]+$` — no matches). Those are mechanical checks, not runs of
`ruff` or `pre-commit`.

## Mandatory checks that could NOT be executed locally — BLOCKER

`python -m pytest`, `ruff format --check .`, `ruff check .`, `mypy src`,
`lint-imports`, `python review/task1/verify_task1.py` and
`pre-commit validate-config` were **not** run in this session.

Cause, unchanged from the Task 1 push session and the Task 2, 3 and 4
sessions: this Claude Code session is non-interactive and runs under a
permission policy that refuses every attempt to execute the project
interpreter or its console scripts, with no approval prompt that can be
answered. Attempts made here, each rejected with
`This command contains multiple operations ... requires approval`:

- `./.venv/Scripts/python.exe -V` (bash)
- `& ".\.venv\Scripts\python.exe" -V` (PowerShell)
- `.venv\Scripts\python.exe -V` (PowerShell)
- `.venv\Scripts\pytest.exe --version` (PowerShell)

`which -a python python3 py pytest ruff mypy` confirms the only interpreters on
`PATH` are the Microsoft Store alias stubs at
`AppData/Local/Microsoft/WindowsApps/python[3]`; `pytest`, `ruff`, `mypy` and
`py` resolve to nothing. The project virtualenv at `.venv/Scripts` exists and
contains `pytest.exe`, `ruff.exe`, `mypy.exe`, `lint-imports.exe` and
`pre-commit.exe`, but none of them may be invoked. `sha256sum` is available,
which is why the frozen verification above could run. The same blocker is
recorded in `review/task4/LOCAL_REPORT.md`, `review/task3/LOCAL_REPORT.md`,
`review/task2/LOCAL_REPORT.md` and `review/task1/CLAUDE_PUSH_REPORT.md`
limitation 1.

**No check was weakened, skipped by choice, or reported as passing without
evidence.** In particular, no assertion in
`tests/unit/test_canonical_benchmarks.py` has been executed locally; the
module's behaviour rests on reading and on CI.

Mitigation actually applied: GitHub Actions (`.github/workflows/ci.yml`)
re-runs five of the seven mandatory checks — `ruff format --check .`,
`ruff check .`, `mypy src`, `python -m pytest`, `lint-imports` — on a clean
Linux Python 3.12 runner. Those CI runs are the **only** execution evidence for
those five checks for Task 5. Formatting, typing and test conformance
therefore rest on CI, not on a local run.

### CI history for Task 5

Recorded in a follow-up commit once the run for this commit has completed; see
the section appended below.

Still **not** verified anywhere for Task 5:
`python review/task1/verify_task1.py` and `pre-commit validate-config`. Both
are Task 1 evidence tooling. Their frozen-hash assertions were independently
re-verified above with `sha256sum` (28/28 OK), and this change adds no
cross-package import edge beyond `aqt.benchmarks -> aqt.data` and
`aqt.benchmarks -> aqt.features`, but the two commands themselves were not
executed and are recorded as **unverified, not passing**.

## Status

Implementation complete for the authorized Task 5 scope. Mandatory local
validation is blocked by the session permission policy described above; remote
CI is the substitute execution evidence for five of the seven commands. Task 6
was not started. No frozen artifact, protocol, schema, spec, sidecar, or
`FROZEN_HASHES.json` entry was touched. No network, exchange, credential,
trading, strategy, ML, or LLM code was written. No backtester, performance
engine, or promotion logic was written. No commit was amended, force-pushed,
or merged.

**EXTERNAL REVIEW: DEFERRED UNTIL USAGE RESET.**
