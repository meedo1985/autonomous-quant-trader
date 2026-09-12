# Post-Fable review addendum

Only documentation and an empty EOF line changed. Original transmitted packet is retained unchanged.

## README.md

Final SHA-256: 624eedf92b1b6ef6c8903f9bced198b560ae54fb149de2714ee1254707e13291

~~~~text
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

~~~~

## review/task1/README.md

Final SHA-256: 38d7b14b7fdf0987ffbb855a38ba05cef3d383bdb48f4c0c23e4f7f5387cc34d

~~~~text
# Re-running the Task 1 evidence checks

From the repository root, using Python 3.12+ with the project and dev tools installed:

```powershell
python -m pip install "PyYAML>=6,<7" "jsonschema>=4.23,<5"
.\review\task1\run_checks.ps1
```

The two packages above are explicit extra requirements of the one-off review audit.
They are not application runtime dependencies.

This workstation's ignored .venv contains portable CPython 3.12.10.
It has no Activate.ps1 or standard-library venv module. Use its existing interpreter
by setting the shell PATH (run_checks.ps1 does this automatically):

```powershell
$env:PATH = "$PWD\.venv;$PWD\.venv\Scripts;$env:PATH"
$env:PYTHONUTF8 = "1"
python -m pytest
```

The repository README's fresh-install instructions assume full CPython.
The portable environment needed hatchling and editables installed first, followed
by pip install --no-build-isolation -e ".[dev]"; this workaround is not required
by the project configuration on a standard Python installation.

The historical verify_task1.py audit deliberately compares against Task 1's original
frozen inventory and pre-task files. It is evidence for this task, not a generic
future-task gate. Use the current task's own authorized baseline for future reviews.

Remote GitHub CI and remote pre-commit hook environments have not run. All claimed
results are local; see FINAL_REPORT.md and the saved command outputs.

~~~~

## review/task1/run_checks.ps1

Final SHA-256: 0ba98123fd87cc39abb839d85b0be98888ef5617b4fe7b8073d60bcc840a1161

~~~~text
$ErrorActionPreference = 'Stop'
$aqtRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location -LiteralPath $aqtRoot
$env:PATH = "$aqtRoot\.venv;$aqtRoot\.venv\Scripts;$env:PATH"
$env:PYTHONUTF8 = '1'
$aqtChecks = @(
    @{ command = 'python -m pytest'; executable = 'python'; arguments = @('-m', 'pytest') },
    @{ command = 'ruff check .'; executable = 'ruff'; arguments = @('check', '.') },
    @{ command = 'ruff format --check .'; executable = 'ruff'; arguments = @('format', '--check', '.') },
    @{ command = 'mypy src'; executable = 'mypy'; arguments = @('src') },
    @{ command = 'lint-imports'; executable = 'lint-imports'; arguments = @() },
    @{ command = 'git diff --check'; executable = 'git'; arguments = @('diff', '--check') },
    @{ command = 'python review/task1/verify_task1.py'; executable = 'python'; arguments = @('review/task1/verify_task1.py') },
    @{ command = 'python -m pip check'; executable = 'python'; arguments = @('-m', 'pip', 'check') },
    @{ command = 'pre-commit validate-config'; executable = 'pre-commit'; arguments = @('validate-config') }
)
$aqtResults = @()
foreach ($aqtCheck in $aqtChecks) {
    $aqtArgs = $aqtCheck.arguments
    $aqtOutput = & $aqtCheck.executable @aqtArgs 2>&1
    $aqtExit = $LASTEXITCODE
    $aqtResults += [PSCustomObject]@{command=$aqtCheck.command; exit_code=$aqtExit; output=($aqtOutput | Out-String)}
    Write-Output "$($aqtCheck.command): exit $aqtExit"
    Write-Output $aqtOutput
}
$aqtResults | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath 'review/task1/validation-results.json' -Encoding utf8
if (@($aqtResults | Where-Object exit_code -ne 0).Count) { exit 1 }

~~~~
