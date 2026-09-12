# autonomous-quant-trader

Scientifically defensible, reproducible, cost-aware crypto spot research.
Current status: **Milestone 0.1 / Task 1 — repository foundation**.
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

Source lives in `src/aqt`; packages are empty except for version and path
metadata in `core`. `core.paths.REPOSITORY_ROOT` describes this source checkout,
not an installed wheel's data location. It performs no filesystem reads.
Import contracts cover direct and indirect dependencies, including descendants.
Research-agent code belongs under `aqt.research`; any future agent package
elsewhere must be added to the live-path forbidden contracts before use.

Repository review instructions are in `AGENTS.md` and `.agents/skills/`.
The Task 1 evidence and Claude handoff are in `review/task1/`.
