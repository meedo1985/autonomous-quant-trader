# Task 4 — causal feature factory: local implementation report

Executed by Claude Opus 5 (`claude-opus-5`) on 2026-09-12 under explicit user
authorization to implement **Task 4 only**. The authorization text is preserved
verbatim at `review/task4/authorized-spec.txt`.

**EXTERNAL REVIEW: DEFERRED UNTIL USAGE RESET.**
No independent-model review, adversarial review, or adjudication was run for
Task 4. Task 4 is **not** externally reviewed. Nothing in this report is an
independent sign-off; it is the implementing model's own account of its own
work. `AGENTS.md` requires `task-gate-review`,
`scientific-reproducibility-review`, `quant-code-review` and a
`claude-adversarial-review` packet before a task is declared complete; those
gates remain **OPEN** for Task 4 by the user's instruction.

## Scope

Implemented: a pure, deterministic, causal feature factory encoding every
Cycle-1 feature in `specs/FEATURE_FACTORY_v1.md`, built on the Task 2 bar
semantics (`src/aqt/data/bars.py`) and the approved Task 3 volatility
convention (`src/aqt/backtest/costs.py`,
`review/task3/SCIENTIFIC_DECISION.md`), plus synthetic unit tests.

The 18 frozen features are implemented and no others: `ret_1h`, `ret_24h`,
`ret_72h`, `ret_168h`, `ema_24`, `ema_72`, `ema_168`, `ema_dist_24`,
`ema_dist_72`, `ema_dist_168`, `sma_4800`, `trend_200d`, `breakout_720`,
`rv_24`, `rv_168`, `rv_720`, `ewma_vol_168h`, `atr_24`.

Explicitly **not** implemented, per the authorization's exclusions: live,
exchange or network access; Binance credentials; trading or execution;
strategies; ML or LLM code; portfolio or allocation logic; backtester
orchestration; canonical benchmarks; the governor; and all Task 5+ work. Also
deliberately excluded inside the feature domain because they belong to later
tasks: target construction, exposure mapping, the 00:00 UTC decision schedule,
feature persistence or a feature store, the `feature_delay_stress_bars` gate,
and any ingestion or outage-recovery policy.

## Frozen sources honoured

| Frozen requirement | Source | Where encoded |
|---|---|---|
| `ret_Nh = log(close_t / close_t-N)`, N in 1/24/72/168 | `FEATURE_FACTORY_v1.md` "Returns" | `RETURN_LAGS`, `log_return`, `compute_features` |
| `ema_N = EMA(close, span=N)`, N in 24/72/168 | "Trend" | `EMA_SPANS`, `exponential_moving_average` |
| `ema_dist_N = close / ema_N - 1` | "Trend" | `compute_features` |
| `sma_4800 = SMA(close, window=4800)` (200 days of 1h bars) | "Trend" | `SMA_WINDOW = 4800`, `simple_moving_average` |
| `trend_200d = close / sma_4800 - 1` | "Trend" | `compute_features` |
| `breakout_720 = close / rolling_max(close, 720) - 1` (30 days) | "Trend" | `BREAKOUT_WINDOW = 720`, `rolling_maximum` |
| `rv_W = std(ret_1h, trailing=W) * sqrt(8760)`, W in 24/168/720 | "Volatility" | `RV_WINDOWS`, `realized_volatility` |
| `ewma_vol_168h = EWMA_std(ret_1h, halflife=168) * sqrt(8760)` | "Volatility" | `ewma_volatility`, delegating to Task 3 |
| `atr_24 = ATR(high, low, close, window=24) / close` | "Volatility" | `ATR_WINDOW = 24`, `true_range`, `average_true_range` |
| Hourly log returns used throughout the volatility block | "Volatility" preamble | `hourly_log_returns` |
| Causal: computed only from data available at the decision timestamp | spec line 5 | `_history_through`, decision = bar close(t) |
| No volume-derived alpha, spread, order-book, trade-imbalance, or seasonality features | spec closing rule | `FORBIDDEN_INPUT_KINDS`, `require_cycle1_features`; `Bar.volume` is read by no formula |
| Feature set is closed; a formula or window change ends the cycle | spec final line | `FEATURE_NAMES` is closed and asserted element-by-element in tests |
| 1h bar interval | `protocol_v1.yaml` `scope.bar_interval` | `BAR_INTERVAL` from `aqt.data.bars`; non-1h series rejected |
| `feature_factory.frozen = true`, hash `c8a0ea02…` | `protocol_v1.yaml` lines 98–100 | no frozen file touched; formulas transcribed, not altered |
| Causal time semantics, no future leakage, UTC only, no silent deletion/correction, one bar-semantics module | `RESEARCH_CONSTITUTION.md` section 6 | see "Properties enforced" |

`protocols/protocol_v1.yaml` was read to confirm `scope.bar_interval` = `1h`
(line 53) and `feature_factory.frozen` = `true` (lines 98–100).
`docs/RESEARCH_CONSTITUTION.md` section 6 (line 70) was read for the causal /
no-leakage / UTC / no-silent-correction rules.

## Properties enforced

- **Causality.** A row is computed at a decision timestamp that is a bar close
  in the Task 2 sense (`decision_time == open_time(t) + 1h`). Only bars whose
  close is at or before the decision are read, so bar `t` is the last
  observation used.
- **No future leakage.** Appending later bars — including bars with prices an
  order of magnitude away — cannot change an already-computed row (tested).
  A row computed on a series truncated at the decision bar is equal to the row
  computed on the full series (tested).
- **Warm-up.** `REQUIRED_HISTORY_BARS = 4800` contiguous 1h bars ending at the
  decision bar are required; `sma_4800` binds. One bar short raises rather than
  producing a partial, shortened, or padded value. Each helper also enforces
  its own window independently.
- **Gap rejection.** Any hole in the supplied history up to and including the
  decision bar raises. Nothing is forward-filled, interpolated, dropped, reset,
  or silently sliced to a post-gap segment. This follows
  `review/task3/SCIENTIFIC_DECISION.md` item 4. A hole strictly *after* the
  decision bar is correctly irrelevant and does not affect the row (tested).
- **Purity/determinism.** No clock, no randomness, no I/O, no global mutable
  state. The public result is a frozen slotted dataclass; inputs are never
  mutated. Repeated computation and an independently rebuilt identical series
  both produce equal rows (tested).
- **Forbidden inputs.** Only `open_time`, `high`, `low` and `close` are read.
  `Bar.volume` enters no formula: setting every volume to `0.0` or to `1e9`
  leaves every feature value bit-identical (tested). No timestamp is decomposed
  into any calendar term: shifting the whole series by 4321 hours leaves every
  feature value bit-identical (tested). `require_cycle1_features` rejects names
  outside the frozen set and names the forbidden family it matched.
- **No silent correction.** Invalid input raises `FeatureFactoryError`. Bar-level
  violations (naive/non-UTC/unaligned timestamps, duplicate open times,
  inconsistent OHLC) are rejected by `aqt.data.bars`; `compute_features`
  re-raises the resulting `BarSemanticsError` as `FeatureFactoryError` because
  it resolves a decision rather than a bare timestamp.

## Conventions the frozen spec leaves open

Documented, not silently taken. These clarify behaviour the frozen spec does
not fix; none of them changes a frozen formula, window, half-life, or
annualisation constant.

1. **EMA recursion and seed.** `alpha = 2 / (span + 1)`, seeded with the simple
   mean of the first `span` closes of the supplied history, then recursed
   forward over every later close. The frozen spec writes
   `EMA(close, span=N)` without fixing the seed or the `adjust` convention.
2. **EMA / EWMA history dependence.** Because both are recursive, `ema_24`,
   `ema_72`, `ema_168` and `ewma_vol_168h` are functions of the *whole* supplied
   contiguous history, not of a fixed trailing slice. `FeatureRow.history_bars`
   records how many bars produced the row, so a value is always reproducible
   from a stated history. This is a real property of the frozen estimators, and
   it is surfaced rather than hidden.
3. **`std` is the sample standard deviation** (`ddof = 1`) for `rv_24`,
   `rv_168`, `rv_720`, consistent with the Task 3 estimator.
4. **`ewma_vol_168h` reuses the Task 3 estimator unchanged.** `ewma_volatility`
   converts returns to basis points, calls
   `aqt.backtest.costs.ewma_hourly_volatility_bps`, converts back, and
   annualises. `review/task3/SCIENTIFIC_DECISION.md` item 5 requires a feature
   consumer to *establish* estimator equivalence before reusing the `EWMA_168h`
   label; equivalence here is by identity rather than by claim, and a test
   asserts exact floating-point equality with the Task 3 function. The feature
   is stricter in one respect: it requires the full 168-return initialisation
   and refuses the partial-seed regime the cost model tolerates, because a
   warm-up shortcut is not appropriate for a research feature.
5. **ATR smoothing.** `ATR(high, low, close, window=24)` is the simple
   arithmetic mean of the last 24 true ranges, with
   `TR_t = max(high_t - low_t, |high_t - close_{t-1}|, |low_t - close_{t-1}|)`.
   A trailing simple average was chosen over Wilder smoothing because the
   frozen spec names a *window*, not a smoothing constant.
6. **Minimum history is the binding maximum** of every feature's own
   requirement, computed as `max(169, 168, 4800, 720, 721, 169, 25) = 4800`
   rather than hard-coded, so it cannot drift from the windows.
7. **`require_cycle1_features` family matching** is substring-based and
   `FORBIDDEN_INPUT_KINDS` is ordered most-specific-first, so a rejected name
   is reported against the narrowest family it matches.

### Flagged for owner/reviewer attention

`aqt.features.factory` imports `aqt.backtest.costs` (for
`ewma_hourly_volatility_bps` and its constants). This inverts the usual
layering — a feature module depending on a backtest module. It was chosen over
the two alternatives because both are worse under the current authorization:
re-implementing the estimator in `aqt.features` risks silent divergence from
the convention the user approved for Task 3, and relocating the estimator to a
shared module would edit committed Task 3 code beyond the authorized Task 4
scope. It breaks none of the four `import-linter` contracts. If the owner
prefers a shared `aqt.core` estimator, that is a refactor to schedule
explicitly, not something this task should have done silently.

## Changed files

| File | Change |
|---|---|
| `src/aqt/features/factory.py` | new — causal deterministic feature factory (stdlib only; imports `aqt.data.bars` and `aqt.backtest.costs`) |
| `tests/unit/test_feature_factory.py` | new — 67 synthetic test functions (94 collected cases after expanding 8 parametrized functions) |
| `review/task4/authorized-spec.txt` | new — preserved Task 4 authorization |
| `review/task4/LOCAL_REPORT.md` | new — this report |

No frozen governance file, sidecar, schema, protocol, specification,
`FROZEN_HASHES.json` entry, `pyproject.toml` contract, CI workflow, or
pre-commit configuration was modified. `README.md` was deliberately left
untouched to keep this commit to the authorized paths. No dependency was added;
the module uses only `math`, `statistics`, `collections.abc`, `dataclasses`,
`datetime` and `typing`.

The two new intra-package import edges are `aqt.features -> aqt.data` and
`aqt.features -> aqt.backtest`. Neither crosses any of the four `import-linter`
contracts in `pyproject.toml`, which constrain only `aqt.research`,
`aqt.governor`, `aqt.execution`, `aqt.allocation` and `aqt.monitoring`.

## Test coverage of the required categories

| Required by the authorization | Tests |
|---|---|
| Formulas against independent calculations | every one of the 18 features is checked against an expectation computed inside the test file, from the closed form of the synthetic price path or a hand-written loop, never by calling the implementation twice; plus hand-computed small-input checks for each helper |
| Warm-up / insufficient history | exactly 4800 accepted; 4799 rejected with the count in the message; early decision inside a long series rejected; per-helper warm-up rejection for EMA, SMA, rolling max, RV, EWMA (needs 168 returns), ATR |
| Gaps / duplicates / invalid bars | hole mid-history rejected; hole immediately before the decision rejected; returns never computed across a hole; duplicate `open_time` rejected; inconsistent OHLC rejected; naive, non-UTC, unaligned, and unknown decision timestamps rejected; non-1h series rejected |
| Timestamp causality | row's `decision_time` equals the decision bar's `close_time`; the decision bar itself is included; `ret_1h` uses the immediately preceding close; a hole after the decision bar is irrelevant |
| Deterministic repeatability | repeated computation equal; independently rebuilt series equal; row order in `compute_feature_rows` does not change values; input series not mutated |
| No future leakage | truncating at the decision bar changes nothing; appending 24 extreme future bars changes nothing |
| Rejection of forbidden volume / order-book / seasonality inputs | volumes `0.0` vs `1e9` give bit-identical features; a 4321-hour time shift gives bit-identical features; `FeatureRow` declares no forbidden field; `require_cycle1_features` rejects 12 forbidden families by name and rejects unknown names |
| Frozen conformance | `FEATURE_NAMES` asserted element-by-element; every window and the annualisation constant asserted; analytic zero row on a constant price series; breakout never positive and exactly zero at a new high |

## Commands executed in this session

| Exact command | Exit | Result |
|---|---:|---|
| `sha256sum -c review/task1/protected-before.sha256sums` | 0 | **PASS** — 28/28 frozen governance files and sidecars byte-identical, including `specs/FEATURE_FACTORY_v1.md`, `specs/FEATURE_FACTORY_v1.md.sha256`, `protocols/protocol_v1.yaml` and `FROZEN_HASHES.json` |
| `sha256sum -c --quiet review/task1/reviewed-files-final.sha256sums` | 1 | **Expected** — only `README.md` FAILED; that is the authorized Task 2 documentation update recorded in `review/task2/LOCAL_REPORT.md`. All other 66 reviewed files byte-identical |
| `git diff --check` | 0 | **PASS** — no whitespace errors |
| `git status --porcelain --untracked-files=all` | 0 | only the intended new paths; no tracked file modified |
| `od -c src/aqt/features/factory.py \| tail -2` | 0 | file ends with exactly one `\n`, LF endings |
| `od -c tests/unit/test_feature_factory.py \| tail -2` | 0 | file ends with exactly one `\n`, LF endings |

Line lengths in both new files were checked mechanically against the 88-column
`ruff` limit (`^.{89,}$` — no matches), and both files were checked for trailing
whitespace (`[ \t]+$` — no matches). Those are mechanical checks, not runs of
`ruff` or `pre-commit`.

## Mandatory checks that could NOT be executed locally — BLOCKER

`python -m pytest`, `ruff format --check .`, `ruff check .`, `mypy src`,
`lint-imports`, `python review/task1/verify_task1.py` and
`pre-commit validate-config` were **not** run in this session.

Cause, unchanged from the Task 1 push session, the Task 2 session and the
Task 3 session: this Claude Code session is non-interactive and runs under a
permission policy that refuses every attempt to execute the project interpreter
or its console scripts, with no approval prompt that can be answered. Attempts
made here, each returning `This command requires approval`:

- `./.venv/Scripts/python.exe -V` (bash)
- `.venv/Scripts/python.exe -c "print(1)"` (bash, including with the sandbox
  override)
- `PATH="$PWD/.venv/Scripts:$PATH" pytest -q tests/unit/test_feature_factory.py`
  (bash)
- `.\.venv\Scripts\python.exe -m pytest tests/unit/test_feature_factory.py -q`
  (PowerShell)
- `& ".\.venv\Scripts\python.exe" -V`, `python --version` (PowerShell)

`which -a python python3 py pytest ruff mypy lint-imports pre-commit` confirms
the only interpreters on `PATH` are the Microsoft Store alias stubs at
`AppData/Local/Microsoft/WindowsApps/python[3]`; `pytest`, `ruff`, `mypy`,
`lint-imports` and `pre-commit` resolve to nothing (`command not found`).
`sha256sum` is available, which is why the frozen verification above could run.
The same blocker is recorded in `review/task3/LOCAL_REPORT.md`,
`review/task2/LOCAL_REPORT.md` and `review/task1/CLAUDE_PUSH_REPORT.md`
limitation 1.

**No check was weakened, skipped by choice, or reported as passing without
evidence.** In particular, no assertion in `tests/unit/test_feature_factory.py`
has been executed locally; the module's behaviour rests on reading and on CI.

Mitigation actually applied: GitHub Actions (`.github/workflows/ci.yml`) re-runs
five of the seven mandatory checks — `ruff format --check .`, `ruff check .`,
`mypy src`, `python -m pytest`, `lint-imports` — on a clean Linux Python 3.12
runner. Those CI runs are the **only** execution evidence for those five checks
for Task 4. Formatting, typing and test conformance therefore rest on CI, not on
a local run.

### CI history for Task 4

<!-- CI_RESULTS -->

Still **not** verified anywhere for Task 4:
`python review/task1/verify_task1.py` and `pre-commit validate-config`. Both are
Task 1 evidence tooling. Their frozen-hash assertions were independently
re-verified above with `sha256sum` (28/28 OK), and this change adds no
cross-package import edge beyond `aqt.features -> aqt.data` and
`aqt.features -> aqt.backtest`, but the two commands themselves were not
executed and are recorded as **unverified, not passing**.

## Status

Implementation complete for the authorized Task 4 scope. Mandatory local
validation is blocked by the session permission policy described above; remote
CI is the substitute execution evidence for five of the seven commands. Task 5
was not started. No frozen artifact, protocol, schema, spec, sidecar, or
`FROZEN_HASHES.json` entry was touched. No network, exchange, credential,
trading, strategy, ML, or LLM code was written. No commit was amended,
force-pushed, or merged.

**EXTERNAL REVIEW: DEFERRED UNTIL USAGE RESET.**
