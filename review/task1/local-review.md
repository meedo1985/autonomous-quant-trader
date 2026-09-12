# Task 1 local review

LOCAL GATE: PASS. Claude status: NOT SENT at packet creation.
Task 1 only; no Task 2, bar semantics, data download, strategies, exchange, ML,
LLM runtime, backtester, governor or executor implementation.

The four existing repository skills and AGENTS.md were already configured.
They were read, applied and preserved; all four skills pass quick_validate.py.
No extra third-party skill installation was necessary. The global ai-negotiation
skill describes Claude as coordinator; here real Claude Code is the independent
reviewer and Codex remains Codex. No different-model review is fabricated.

Ranked criteria:
1. Preserve the 28 frozen files against the independent pre-task snapshot.
2. Fulfil the original Task 1 acceptance criteria without scientific logic.
3. Fail on direct and indirect forbidden imports.
4. Pass all required checks without weakening configuration.
5. Provide a reproducible, secret-free review snapshot and honest limits.

Local disposition: no remaining Task 1 blocker. Code and package scope were read;
the assertions in the one-off audit were inspected. The first probe runner
incorrectly called an integer-returning import-linter helper without forwarding
its exit status; now it calls the actual CLI entry point and all 20 violations
exit 1 with their expected broken contract. Empty controls exit 0.
Initial failed validation records are retained.

Independent checks: 28 protected files match original SHA-256, 14 sidecars match,
canonical Constitution hash and manifest/protocol dependency bindings match,
five JSON schemas are valid and the protocol validates. Schema rejection controls
reject empty protocol and non-FROZEN status. Git text attributes disable newline
conversion for all protected paths; filtered Git object hashes equal raw hashes.

Scientific/quant review: N/A for returns, costs, leakage, seeds, trial budgets,
data partition computation and performance: no such runtime exists in Task 1.
No scientific values or frozen schema defects were repaired. NO_EDGE_FOUND remains valid.

Environment and limits:
- Windows, portable CPython 3.12.10 copied to ignored .venv; this is not a standard
  venv and lacks Activate.ps1 and the venv standard-library module.
- Initial isolated pip install failed because the embedded runtime could not
  resolve isolated hatchling. Installing hatchling and editables locally followed
  by pip install --no-build-isolation -e ".[dev]" "jsonschema>=4.23,<5" succeeded.
  README explains normal full-Python setup and how to use this current runtime.
- environment-freeze.txt records installed versions, not a portable dependency
  lock; no numerical/experiment byte-reproducibility claim is made.
- Required local checks pass. GitHub-hosted Linux CI has been configured but has
  not run: no push/commit is authorized or performed.
- pre-commit configuration and exclusion behavior were checked; hooks were not
  installed into .git and remote hook environments were not executed.
- Review audit additionally needs jsonschema; PyYAML is also used and present
  (a pre-commit dependency). It is one-off evidence tooling, not runtime enforcement.
- Existing governance and review instructions were untracked before this task;
  historical byte preservation is measured against the recorded pre-task copy,
  not against HEAD (which tracked only README.md).
- Codex CLI created the scaffold but exhausted its account usage. Automatic
  approval review rejected creating run_checks.ps1 because usage was exhausted.
  The coordinator obtained direct approval for that same action, completed the
  checks, corrected audit-only defects, and added Git byte preservation.

No protected runtime component in Constitution section 16 was implemented.
Claude feedback must be adjudicated before claiming external review complete.
No merge/publish/promotion approval is implied. Stop after Task 1.
