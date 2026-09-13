# autonomous-quant-trader

Scientifically defensible, reproducible, cost-aware crypto spot research.
Current status: **Milestone 0.1 / Task 6 — accepted oracle/canary suite frozen**.
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
costs, causal features, and canonical benchmark definitions.
`core.paths.REPOSITORY_ROOT` describes this source checkout,
not an installed wheel's data location. It performs no filesystem reads.
Import contracts cover direct and indirect dependencies, including descendants.
Research-agent code belongs under `aqt.research`; any future agent package
elsewhere must be added to the live-path forbidden contracts before use.

## Backtester trust suite (Task 6)

Task 6 adds exact-arithmetic, synthetic-only mathematical oracles and leakage
canaries under `tests/oracles/` and `tests/canaries/`. They are independent of
the future production backtester. The NumPy reference and production engine
remain deferred until these tests receive the human acceptance required by the
Constitution. Evidence is in `review/task6/`.

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
