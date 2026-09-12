## Adversarial Review — Task 1 Foundation

Reviewed snapshot: `b596a8e` plus full untracked working tree as provided. No tools invoked; all judgment from packet content only.

---

### Findings

| ID | Severity | File + Location | Trigger and Evidence | Impact | Minimal Correction | Falsifier |
|----|----------|-----------------|---------------------|--------|-------------------|-----------|
| C1 | NON-BLOCKING | `pyproject.toml` / `[project] dependencies` | Runtime data packages (numpy, polars, duckdb, pyarrow, httpx, websockets) are absent. The spec says "allowed at this stage," which the implementer read as optional rather than required. Confirmed by `environment-freeze.txt` — none appear in installed set. | Future tasks adding data/research code will need these added to pyproject.toml before they can import them; no Task 2+ scaffold works without it. Does not block Task 1: all packages are empty, no imports fail. | Add the six packages to `[project] dependencies` now while they are scope-authorized, before Task 2 needs them. | If any Task 2+ code imports numpy/polars without them in pyproject.toml, pip install of the bare package will fail — which confirms the gap. Absent that failure, the word "allowed" is sufficient cover for Task 1. |
| C2 | NON-BLOCKING | `.github/workflows/ci.yml` (entire file) | The CI workflow has never executed on any remote runner. Local inspection and `verify_task1.py` confirm step order, branch triggers, and absence of `continue-on-error`. No workflow run ID or artifact exists. The local environment is Windows + portable CPython 3.12.10; the CI target is `ubuntu-latest` + standard Python 3.12. | Line-ending, path-separator, or locale edge cases invisible on Windows could fail the first real CI run. For this all-empty scaffold the risk is minimal, but it is unverified. | First authorized push will produce the missing evidence. No code change needed now. | A green CI run at the HEAD commit of the reviewed files falsifies this. |
| C3 | QUESTION | `pyproject.toml` `[tool.importlinter.contracts]` / "Governor cannot reach execution or model training" | The spec says "aqt.governor MUST NOT import model-training/research modules." The contract forbids governor → {execution, models}. `aqt.research` is separately covered by the "Live packages" contract. But `aqt.features` and `aqt.data` are not forbidden for governor by any contract — if "model-training modules" is intended to include feature/data packages used in training pipelines, the boundary is incomplete. All packages are empty so no violation is possible in Task 1. | If a future task implements a governor that pulls live feature vectors directly (bypassing the predictor) the contract would not catch it. This is not a Task 1 gap but may become one in Task 2. | Decide now whether `aqt.features` and `aqt.data` are "model-training" per the spec; if yes, add them to the governor forbidden list before Task 2. | Falsified if the spec author confirms "model-training modules" means only fitting/inference packages (models, research) and excludes raw features/data. |
| C4 | QUESTION | `review/task1/protected-before.json` (baseline provenance) | The 28-file pre-task baseline is entirely implementer-recorded. Git history contains only one commit (README.md); all governance files are untracked. The `verify_task1.py` proves current files match `protected-before.json`, but cannot prove `protected-before.json` was written before any task modification began. The git status at conversation start (all files `??`) confirms they were present in the working directory before this conversation, but provides no content snapshot independent of the implementer's record. | If `protected-before.json` was written after any file was modified during the task, the "byte preservation" check is circular. For Task 1 this is a provenance question, not a confirmed defect. The closed-loop self-consistency of Constitution ↔ manifest ↔ protocol cross-hashes provides corroborating (though not independent) evidence. | Retain the Codex session transcript or any Codex-side file snapshot that predates the task as independent corroboration. | Falsified if an external timestamp (Codex session log, file-system mtime audit, or explicit pre-task snapshot committed elsewhere) shows the governance files were present with identical hashes before the task session began. |

---

### Consequential Shared Assumptions — What Both Reviewers May Have Missed

**1. Import-linter contract coverage passes trivially on empty packages.**
The final `lint-imports` reports "Analyzed 16 files, 0 dependencies" — no code to check, so all four contracts vacuously pass. Enforcement only activates when implementation code is added. The probes are the true test, and they are correct. But there is a residual risk: if a future task adds code and the developer does not re-run `lint-imports` locally, a boundary violation might only be caught by CI (which has never run). Pre-commit does not run import-linter; CI does. This is a process gap, not a code gap.

**2. `allow_indirect_imports = false` across import-linter 2.3–2.15 version range.**
The probes confirm behavior at 2.15. The pyproject.toml pin is `>=2.3,<3`. If a developer installs 2.3 and the indirect-import semantics changed between minor versions, the probes would not catch it (they were run at 2.15). Both reviewers appear to have assumed version stability; neither tested at the minimum pinned version.

**3. `.gitattributes` `-text` attribute is not retroactive on already-staged files.**
The `.gitattributes` correctly prevents future newline conversion on frozen files. But since no files have ever been staged/committed to this repository (all 28 are untracked), the attributes have never been exercised by an actual `git add`. The `git check-attr` output showing `text: unset` confirms the attribute is parsed correctly. A full `git add` + `git commit` cycle would be the first real test.

**4. Missing evidence: no `pre-commit run --all-files` result.**
`pre-commit validate-config` confirms the YAML is parseable. Neither the implementer nor local reviewer ran `pre-commit run --all-files` to confirm the exclusion regex actually prevents the hooks from touching frozen files in practice. The regex is verified analytically in `verify_task1.py`, but a live run would close this.

---

### TASK 1 PASS

All mandatory acceptance criteria are satisfied: project structure, frozen artifact byte-preservation with cross-hash closure, all four import boundary contracts active and probe-verified for both direct and indirect violations, CI step order and trigger configuration confirmed, all five required checks exit 0 locally (pytest 16/16, ruff, mypy, lint-imports, git diff --check), secrets absent, README and governance notice present. No task-blocking defects were found. The four findings above are non-blocking or questions that do not prevent Task 1 completion; C3 and C4 carry forward as pre-Task-2 concerns.
