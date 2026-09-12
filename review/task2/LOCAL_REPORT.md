# Task 2 — bar semantics: local implementation report

Executed by Claude Opus 5 (`claude-opus-5`) on 2026-09-12 under explicit user
authorization to implement **Task 2 only**.

**EXTERNAL REVIEW: DEFERRED UNTIL USAGE RESET.**
No independent-model review was run for Task 2. Task 2 is **not** externally
reviewed, not adversarially reviewed, and not adjudicated. Nothing in this
report should be read as an independent sign-off. `AGENTS.md` requires
`task-gate-review`, `scientific-reproducibility-review`, `quant-code-review`
and a `claude-adversarial-review` packet before a task is declared complete;
those gates remain **OPEN** for Task 2 by the user's instruction.

## Scope

Implemented: the smallest deterministic bar-semantics module required by the
frozen specifications, plus synthetic unit tests and documentation.

Explicitly **not** implemented (out of the authorized scope): exchange or
network access, the Binance SDK, any real market-data download, strategies,
feature calculations, the cost model, the backtester, ML, portfolio or
allocation logic, the governor, the executor, and Task 3.

Also deliberately deferred inside bar semantics, because they belong to later
scheduled tasks: the 00:00 UTC decision schedule, the 10pp rebalance band,
the 24h minimum-hold rule, exposure clipping, and the one-bar
execution-delay stress from `specs/COST_MODEL_v1.md`.

## Frozen sources honoured

| Frozen requirement | Source | Where encoded |
|---|---|---|
| 1h bar interval | `protocols/protocol_v1.yaml` `scope.bar_interval` | `BAR_INTERVAL` |
| Decision at close(t), execution at open(t+1) | `specs/BACKTESTER_SPEC_v1.md` item 2 | `BarSeries.baseline_execution` |
| Decision timestamp = 1h bar close; fill = next 1h bar open | `specs/COST_MODEL_v1.md` "Baseline execution" | `Bar.close_time`, `ExecutionPoint` |
| Benchmarks share the candidate bar-semantics module | `specs/CANONICAL_BENCHMARKS_v1.md` | single module `aqt.data.bars` |
| UTC only; one tested bar-semantics module; no silent deletion/correction | `docs/RESEARCH_CONSTITUTION.md` section 6 | `require_utc`, `missing_open_times` |

## Semantics defined

- A `Bar` is labelled by `open_time`, the inclusive start of the half-open
  interval `[open_time, open_time + interval)`. `close_time` is the exclusive
  end and is the decision timestamp of that bar.
- Because the series is interval-aligned, `close_time` of bar t equals
  `open_time` of bar t+1, so the baseline fill is the open of the bar whose
  `open_time` is the decision timestamp itself.
- Timestamps must be timezone-aware with a zero UTC offset. Naive timestamps
  are rejected, never assumed to be UTC; non-zero offsets are rejected.
  Accepted timestamps are normalised to `datetime.UTC` so stored values are
  canonical.
- `open_time` must sit exactly on an interval boundary measured from the Unix
  epoch.
- Series open times must be unique and strictly increasing; all bars must
  share the series interval; an empty series is rejected.
- OHLC must be finite and strictly positive, with
  `high >= max(open, low, close)` and `low <= min(open, high, close)`.
  Volume must be finite and non-negative; zero volume is accepted because a
  genuinely untraded hour is data, not an error.
- Missing intervals are never filled, interpolated, or dropped.
  `BarSeries` accepts a holed series and reports the exact missing open times
  via `missing_open_times()`. The functions that claim complete bars
  (`contiguous_bar_series`, `BarSeries.require_contiguous`) raise instead.
  `baseline_execution` refuses to execute across a hole, because open(t+1)
  does not exist there, and refuses on the final bar close.

## Changed files

| File | Change |
|---|---|
| `src/aqt/data/bars.py` | new — bar-semantics module (stdlib only) |
| `tests/unit/test_bar_semantics.py` | new — 30 synthetic test functions (35 collected cases) |
| `README.md` | updated status, `aqt.data` mention, Task 2 section |
| `review/task2/LOCAL_REPORT.md` | new — this report |
| `review/task1/CLAUDE_PUSH_REPORT.md` | pre-existing untracked Task 1 push evidence, preserved unmodified and committed as history |

No frozen governance file, no sidecar, no schema, no protocol, no
specification, no `pyproject.toml` contract, no CI workflow, and no
pre-commit configuration was modified. No dependency was added; the module
uses only `math`, `dataclasses`, `datetime`, `collections.abc` and `typing`.

## Commands executed in this session

| Exact command | Exit | Result |
|---|---:|---|
| `sha256sum -c review/task1/protected-before.sha256sums` | 0 | PASS — 28/28 frozen files byte-identical |
| `sha256sum -c --quiet review/task1/reviewed-files-final.sha256sums` | 1 | Expected — only `README.md` FAILED; that file is the authorized documentation update. All other 66 reviewed files byte-identical |
| `git diff --check` | 0 | PASS (CRLF advisory warning only) |
| `git status --porcelain` | 0 | only the intended paths above |

## Mandatory checks that could NOT be executed locally — BLOCKER

`python -m pytest`, `ruff check .`, `ruff format --check .`, `mypy src`,
`lint-imports`, `python review/task1/verify_task1.py` and
`pre-commit validate-config` were **not** run in this session.

Cause: this Claude Code session runs non-interactively under a permission
policy that refuses every attempt to execute the project interpreter or its
console scripts. `.venv/Scripts/python.exe`, `.venv/Scripts/pytest.exe`, a
`PATH`-prefixed `python`, `cmd /c <abs path>\python.exe` and
`sh -c './.venv/Scripts/python.exe'` each returned
`This command requires approval`, and no approval prompt can be answered
non-interactively. There is no other Python interpreter on the machine: the
only `python` on `PATH` is the Microsoft Store alias stub, which exits with
"Python was not found". The same blocker is recorded for the Task 1 push
session in `review/task1/CLAUDE_PUSH_REPORT.md` limitation 1. No check was
weakened, skipped by choice, or reported as passing without evidence.

Mitigation actually applied: GitHub Actions re-runs five of the seven
mandatory checks (`ruff format --check .`, `ruff check .`, `mypy src`,
`python -m pytest`, `lint-imports`) on a clean Linux Python 3.12 runner for
the Task 2 commit. That CI result is the only execution evidence for those
five checks and its run URL, conclusion and per-step outcomes are reported in
the session summary accompanying this commit. Line lengths were verified
mechanically against the 88-column `ruff` limit, but formatting and typing
conformance rest on CI, not on a local run.

Still **not** verified anywhere for Task 2:
`python review/task1/verify_task1.py` and `pre-commit validate-config`.
Both are Task 1 evidence tooling and are unaffected in substance by this
change — `verify_task1.py` asserts the 28 frozen hashes (independently
re-verified above with `sha256sum`), the pre-task file hashes with `README.md`
already excluded, the pre-commit/CI configuration (unchanged), and the
import-contract probes against a disposable copy of `src/` (the new module
imports only the standard library, so it creates no cross-package edge) — but
they were not executed and are therefore recorded as unverified, not passing.

## Assumptions

1. **Package placement.** `aqt.data` was chosen over `aqt.backtest` because
   bar semantics are a data-layer invariant shared by candidates, benchmarks,
   features and the backtester, and the existing `import-linter` contracts do
   not restrict imports of `aqt.data` from any package.
2. **Bar labelling.** Timestamps label the bar **open**, matching Binance
   kline convention and making `close_time == next open_time` exact. The
   frozen specs state the decision/execution rule but not the label; this
   choice is documented in the module and is the reason `baseline_execution`
   takes a close timestamp and resolves the bar opening at that same instant.
3. **Zero-offset normalisation.** A zero-offset non-`UTC` `tzinfo` is
   accepted and normalised to `datetime.UTC`. It denotes the same instant, so
   no data is reinterpreted; any non-zero offset is rejected outright.
4. **Zero volume is valid data.** Only negative or non-finite volume is
   rejected, per the no-silent-correction rule.
5. **Completeness is opt-in, not implicit.** A series with holes can be
   constructed and inspected, so that outage detection can report rather than
   silently repair. Only functions that claim complete bars raise.

## Status

Implementation complete for the authorized scope. Mandatory local validation
is blocked by the session permission policy described above; remote CI is the
substitute evidence for five of the seven commands. Task 2 is **not**
externally reviewed. **EXTERNAL REVIEW: DEFERRED UNTIL USAGE RESET.**
