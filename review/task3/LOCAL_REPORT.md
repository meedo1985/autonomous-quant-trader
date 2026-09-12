# Task 3 — deterministic cost model: local implementation report

Executed by Claude Opus 5 (`claude-opus-5`) on 2026-09-12 under explicit user
authorization to implement **Task 3 only**. The authorization text is preserved
verbatim at `review/task3/authorized-spec.txt`.

**EXTERNAL REVIEW: DEFERRED UNTIL USAGE RESET.**
No independent-model review, adversarial review, or adjudication was run for
Task 3. Task 3 is **not** externally reviewed. Nothing in this report is an
independent sign-off; it is the implementing model's own account of its own
work. `AGENTS.md` requires `task-gate-review`,
`scientific-reproducibility-review`, `quant-code-review` and a
`claude-adversarial-review` packet before a task is declared complete; those
gates remain **OPEN** for Task 3 by the user's instruction.

## History of this file

An earlier revision of this file recorded Task 3 as **BLOCKED — no documented
scope**, because no Task 3 specification existed in the repository at that
time. That blocker is now resolved: the user supplied a written Task 3
specification, preserved at `review/task3/authorized-spec.txt`. This revision
supersedes the blocked revision. Neither revision was ever committed.

## Scope

Implemented: a pure, deterministic cost-model module encoding
`specs/COST_MODEL_v1.md` on top of the Task 2 bar semantics
(`src/aqt/data/bars.py`), plus synthetic unit tests.

Explicitly **not** implemented, per the authorization's exclusions: exchange or
network access, Binance credentials or SDK, live trading, order placement,
strategies or features, portfolio/allocation logic, ML or LLM code, backtester
orchestration, and all Task 4+ work. Also deliberately excluded inside the cost
domain because they belong to later tasks: exposure mapping, the rebalance
band, the minimum-hold rule, turnover accounting, and portfolio aggregation.

## Frozen sources honoured

| Frozen requirement | Source | Where encoded |
|---|---|---|
| Decision at 1h bar close; baseline fill at next 1h bar open | `specs/COST_MODEL_v1.md` "Baseline execution" | `resolve_execution` via `BarSeries.baseline_execution` |
| Taker-like only | `specs/COST_MODEL_v1.md` "Order style" | no passive/limit path exists in the module |
| Point-in-time taker fee where available | `specs/COST_MODEL_v1.md` "Fee" | `FeeSchedule.quote`, `resolve_taker_fee_bps` |
| Fallback taker fee 10 bps per side | `specs/COST_MODEL_v1.md` "Fee" | `FALLBACK_TAKER_FEE_BPS = 10.0` |
| Fixed spread allowance 2 bps per side | `specs/COST_MODEL_v1.md` "Spread allowance" | `SPREAD_ALLOWANCE_BPS = 2.0` |
| `min(15, max(1, 0.05 * sigma_hourly_bps))` | `specs/COST_MODEL_v1.md` "Slippage" | `slippage_bps` |
| EWMA half-life 168h; first 168 returns use simple sample stdev; from return 169 recursive EWMA initialised from the sample variance of the first 168 | `specs/COST_MODEL_v1.md` "Slippage" | `ewma_hourly_volatility_bps_series`, `_EWMA_DECAY = 0.5 ** (1/168)` |
| Total per side = `fee + spread + slippage` | `specs/COST_MODEL_v1.md` "Total modeled per-side cost" | `CostBreakdown.base_total_bps` |
| Stress 1.0x / 1.5x / 2.0x / 3.0x | `specs/COST_MODEL_v1.md` "Stress"; `protocols/protocol_v1.yaml` `cost_model.stress_multipliers` | `STRESS_MULTIPLIERS` |
| Delay stress = one additional 1h bar | `specs/COST_MODEL_v1.md` "Delay stress"; `protocols/protocol_v1.yaml` `validation.execution_delay_stress_bars` | `EXECUTION_DELAY_STRESS_BARS`, `resolve_execution(delay_bars=...)` |
| No passive-limit assumptions in Cycle 1 | `specs/COST_MODEL_v1.md` closing line | no maker/limit code path |

`protocols/protocol_v1.yaml` was read to confirm `cost_model.stress_multipliers`
= `[1.0, 1.5, 2.0, 3.0]` (line 150) and `validation.execution_delay_stress_bars`
= `1` (line 268).

## Properties enforced

- **Purity/determinism.** No clock, no randomness, no I/O, no global state. All
  public results are frozen slotted dataclasses. Inputs are never mutated;
  `trade_cost` reads `BarSeries` and returns new objects.
- **Point-in-time volatility.** A decision at `close(t)` uses closes up to and
  including bar `t` only. Appending later bars cannot change a past decision's
  cost (tested).
- **No silent correction.** Invalid input raises `CostModelError`; nothing is
  clamped, defaulted, or dropped behind the caller. The two prescribed
  behaviours that do adjust a value — the 10 bps fee fallback and the 1/15 bps
  slippage floor and cap — are always reported: `FeeQuote.source` says
  `"fallback"` or `"schedule"`, and `CostBreakdown` carries the
  `sigma_hourly_bps` that produced the slippage.
- **No bridging holes.** Hourly returns are never computed across a missing 1h
  bar, and a delayed fill is never shifted onto a different bar to make it
  resolvable.

## Corrections made to the pre-existing working-tree files in this session

The working tree already contained draft `src/aqt/backtest/costs.py` and
`tests/unit/test_cost_model.py`. They were reviewed line by line against the
frozen spec and the Task 2 module. Three defects were found and corrected:

1. `tests/unit/test_cost_model.py`,
   `test_trade_cost_matches_an_independently_computed_expectation`: the
   independently computed expectation prefixed the close series with an extra
   `100.0`, which equals the first bar's open. That injected a spurious zero
   return, so the test asserted four returns and the wrong sample standard
   deviation where the implementation correctly produces three. **This test
   would have failed.** Fixed to `_expected_returns_bps(closes[:4])`.
2. `tests/unit/test_cost_model.py`,
   `test_delay_stress_changes_only_the_fill_not_the_volatility`: asserted the
   delayed fill price was `series.bars[7].open`. A decision at `close(5)` fills
   at `open(5)` = `bars[5]` baseline and `open(6)` = `bars[6]` under one-bar
   delay stress; the same test's preceding assertion
   (`baseline.execution_time + BAR_INTERVAL`) already implies `bars[6]`. **This
   test would have failed.** Fixed to `series.bars[6].open`.
3. `src/aqt/backtest/costs.py` module docstring claimed "Invalid input raises
   `CostModelError`" without qualification, while a bare timestamp violation in
   `FeeTier` / `resolve_taker_fee_bps` propagates `BarSemanticsError` from
   `aqt.data.bars` unchanged (only `resolve_execution` and `trade_cost` re-raise
   it as `CostModelError`). Documentation corrected; behaviour unchanged,
   because the existing behaviour is deliberate and is covered by tests.

4. `tests/unit/test_cost_model.py`,
   `test_trade_cost_uses_only_information_available_at_the_decision`: the
   assertion was written as a single chained comparison across two
   `trade_cost(...).breakdown` calls, which `ruff format` rejects (it wraps the
   comparison in parentheses instead, because the right-hand side ends in an
   attribute access rather than a bracket). **This failed
   `ruff format --check .` in CI run 34701567324.** Rewritten as two local
   bindings plus a short assertion, which is format-stable. Test semantics are
   unchanged.

Defects 1 and 2 were identified by manual trace, not by execution — see the
blocker section. Defect 4 was identified by CI. No other behavioural change was
made to the draft module.

## Changed files

| File | Change |
|---|---|
| `src/aqt/backtest/costs.py` | new — deterministic cost model (stdlib only, imports `aqt.data.bars`) |
| `tests/unit/test_cost_model.py` | new — 52 synthetic test functions (55 collected cases, one parametrized over the four stress multipliers) |
| `review/task3/authorized-spec.txt` | new — preserved Task 3 authorization |
| `review/task3/LOCAL_REPORT.md` | new — this report |

No frozen governance file, sidecar, schema, protocol, specification,
`FROZEN_HASHES.json` entry, `pyproject.toml` contract, CI workflow, or
pre-commit configuration was modified. `README.md` was deliberately left
untouched to keep this commit to the authorized paths. No dependency was added;
the module uses only `math`, `statistics`, `collections.abc`, `dataclasses`,
`datetime`, `enum` and `typing`.

`aqt.backtest` importing `aqt.data` crosses none of the four `import-linter`
contracts in `pyproject.toml`, which constrain only `aqt.research`,
`aqt.governor`, `aqt.execution`, `aqt.allocation` and `aqt.monitoring`.

## Assumptions (documented, not silently taken)

1. **Return definition.** `sigma_hourly_bps` is the standard deviation of
   close-to-close hourly **log** returns in basis points. The frozen spec fixes
   the half-life and the initialisation but not the return definition.
2. **EWMA recursion form.** From return 169 onward,
   `var_t = d * var_{t-1} + (1 - d) * r_t^2` with `d = 0.5 ** (1/168)`, i.e. an
   uncentered (zero-mean) variance recursion seeded with the sample variance of
   the first 168 returns. The spec fixes the seed and the half-life but not the
   recursion form.
3. **Minimum history.** A sample standard deviation needs two returns, so a
   decision needs at least three contiguous bars of history; fewer raises
   rather than falling back to a default volatility.
4. **Schedule coverage.** A fill timestamp earlier than the first fee tier is
   *not covered* by the schedule, so the frozen 10 bps fallback applies and the
   quote reports `source="fallback"`.
5. **Stress multipliers are closed.** Only the four frozen multipliers are
   accepted; any other value raises rather than being silently honoured.
6. **Cost sign convention.** `TradeCost.effective_price` moves the fill against
   the trader on both sides; the raw open is left untouched in `ExecutionPoint`.

## Commands executed in this session

| Exact command | Exit | Result |
|---|---:|---|
| `sha256sum -c review/task1/protected-before.sha256sums` | 0 | **PASS** — 28/28 frozen governance files and sidecars byte-identical, including `specs/COST_MODEL_v1.md` and `protocols/protocol_v1.yaml` |
| `sha256sum -c --quiet review/task1/reviewed-files-final.sha256sums` | 1 | **Expected** — only `README.md` FAILED; that is the authorized Task 2 documentation update recorded in `review/task2/LOCAL_REPORT.md`. All other 66 reviewed files byte-identical |
| `git diff --check` | 0 | **PASS** — no whitespace errors (CRLF advisory warnings only) |
| `git diff --numstat` / `git diff \| grep -c "No newline at end of file"` | 0 | every new file ends with a newline |
| `git status --porcelain --untracked-files=all` | 0 | only the four intended paths above |

Line lengths in both new files were checked mechanically against the 88-column
`ruff` limit (`^.{89,}$` — no matches). That is a mechanical check, not a run
of `ruff`.

## Mandatory checks that could NOT be executed locally — BLOCKER

`python -m pytest`, `ruff format --check .`, `ruff check .`, `mypy src`,
`lint-imports`, `python review/task1/verify_task1.py` and
`pre-commit validate-config` were **not** run in this session.

Cause, unchanged from the Task 1 push session and the Task 2 session: this
Claude Code session is non-interactive and runs under a permission policy that
refuses every attempt to execute the project interpreter or its console
scripts, with no approval prompt that can be answered. Attempts made here, each
returning `This command requires approval`:

- `./.venv/Scripts/python.exe -V` (bash)
- `.venv/Scripts/python.exe -V` (bash, and again with the sandbox override)
- `.venv/Scripts/pytest.exe --version` (bash)
- `PATH="$PWD/.venv/Scripts:$PATH" pytest -q tests/unit/test_cost_model.py`
- `& ".\.venv\Scripts\python.exe" -V`, `.\.venv\Scripts\python.exe -V`,
  `python --version` (PowerShell)

`which -a python python3 py pytest` confirms the only interpreters on `PATH`
are the Microsoft Store alias stubs at
`AppData/Local/Microsoft/WindowsApps/python[3]`; `ruff` resolves to nothing
(`command not found`). The same blocker is recorded in
`review/task2/LOCAL_REPORT.md` and `review/task1/CLAUDE_PUSH_REPORT.md`
limitation 1.

**No check was weakened, skipped by choice, or reported as passing without
evidence.** In particular, the two test defects corrected above were found by
reading, not by a failing run, and the corrected tests have not been executed
locally.

Mitigation actually applied: GitHub Actions (`.github/workflows/ci.yml`) re-runs
five of the seven mandatory checks — `ruff format --check .`, `ruff check .`,
`mypy src`, `python -m pytest`, `lint-imports` — on a clean Linux Python 3.12
runner. Those CI runs are the **only** execution evidence for those five checks
for Task 3. Formatting, typing and test conformance therefore rest on CI, not on
a local run.

### CI history for Task 3

| Run | Commit | Result |
|---|---|---|
| [34701567324](https://github.com/meedo1985/autonomous-quant-trader/actions/runs/34701567324) | `ab8da50` | **FAILED** at step `ruff format --check .`: `Would reformat: tests/unit/test_cost_model.py` (1 file, 21 already formatted). The later steps did not run. Cause and fix are defect 4 above. |
| [34701759775](https://github.com/meedo1985/autonomous-quant-trader/actions/runs/34701759775) | `66b176e` | **SUCCESS**, 21s, ubuntu-latest, CPython 3.12.14 |

Per-step output of the successful run `34701759775`:

| CI step | Exact output |
|---|---|
| `ruff format --check .` | `22 files already formatted` |
| `ruff check .` | `All checks passed!` |
| `mypy src` | `Success: no issues found in 18 source files` |
| `python -m pytest` | `106 passed in 0.51s` (whole suite: Task 1 + Task 2 + the 55 Task 3 cases) |
| `lint-imports` | `Analyzed 18 files, 1 dependencies.` / `Contracts: 4 kept, 0 broken.` |

The single dependency edge `lint-imports` analysed is `aqt.backtest -> aqt.data`,
introduced by this task; all four frozen contracts remain kept.

Nothing here should be read as a claim that a check passed before its run
reported success. Local execution of these five commands remains **blocked**;
CI is the evidence.

Still **not** verified anywhere for Task 3:
`python review/task1/verify_task1.py` and `pre-commit validate-config`. Both are
Task 1 evidence tooling. Their frozen-hash assertions were independently
re-verified above with `sha256sum` (28/28 OK), and this change adds no
cross-package import edge beyond `aqt.backtest -> aqt.data`, but the two
commands themselves were not executed and are recorded as **unverified, not
passing**.

## Status

Implementation complete for the authorized Task 3 scope. Mandatory local
validation is blocked by the session permission policy described above; remote
CI is the substitute execution evidence for five of the seven commands, and it
reported **success** for commit `66b176e`. Task 4
was not started. No frozen artifact, protocol, schema, spec, sidecar, or
`FROZEN_HASHES.json` entry was touched. No network, exchange, trading, ML, or
LLM code was written. No commit was amended, force-pushed, or merged.

**EXTERNAL REVIEW: DEFERRED UNTIL USAGE RESET.**
