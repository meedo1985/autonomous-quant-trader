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
