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
