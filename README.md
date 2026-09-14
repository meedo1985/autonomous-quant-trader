# autonomous-quant-trader

Scientifically defensible, reproducible, cost-aware crypto spot research.
Current status: **Milestone 0.1 / Task 8 — production backtester accepted**.
**NO EDGE FOUND (`NO_EDGE_FOUND`) is a valid result.**

V1 is Binance Spot BTC/ETH research: no leverage, margin, futures, or
withdrawals. This task does not trade or connect to an exchange.
The v1.0 architecture and governance artifacts are frozen; see
[docs/README.md](docs/README.md) and [SECURITY.md](SECURITY.md).

## Local development

Install Python 3.12 or newer. From the repository root on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pre-commit install
```

On POSIX systems, activate with `source .venv/bin/activate` instead.
Run the checks used by CI, plus the local Git whitespace check:

```text
python -m pytest
ruff check .
ruff format --check .
mypy src
lint-imports
git diff --check
```

Source lives in `src/aqt`. Implemented foundations cover bar semantics,
costs, causal features, canonical benchmark definitions, and the deterministic
production backtester.
`core.paths.REPOSITORY_ROOT` describes this source checkout,
not an installed wheel's data location. It performs no filesystem reads.
Import contracts cover direct and indirect dependencies, including descendants.
Research-agent code belongs under `aqt.research`; any future agent package
elsewhere must be added to the live-path forbidden contracts before use.

## Backtester trust suite and production engine (Tasks 6–8)

Task 6 adds the frozen exact-arithmetic oracle and leakage canaries under
`tests/oracles/` and `tests/canaries/`. Task 7 adds the independent NumPy
`float64` reference under `tests/reference/`, with derived numerical error
bounds and comparison tests. Task 8 adds the pure production engine under
`aqt.backtest.engine` and verifies it against both accepted reference layers.
Delay stress remains explicitly rejected until pending-fill exposure semantics
are bound. Evidence is in `review/task6/`, `review/task7/`, and `review/task8/`.

## Bar semantics (Task 2)

`aqt.data.bars` is the single tested bar-semantics module required by the
Constitution. It defines timestamped 1h OHLCV bars in UTC only, rejects naive
or non-UTC timestamps, requires strictly increasing unique interval-aligned
open times, reports missing intervals explicitly instead of filling or
dropping them, and encodes the frozen convention of a decision at close(t)
executing at open(t+1). It reads no market data and performs no network
access; its tests are synthetic.

Repository review instructions are in `AGENTS.md` and `.agents/skills/`.
Task evidence and external-review records are under `review/`.
