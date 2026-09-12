# Claude adversarial review packet — Task 1


Created 2026-09-12T11:19:00.112456+00:00
Base/HEAD: b596a8e73a563cb376361b3ca3cada8c0ea326f6


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



| Acceptance area | Implementation / evidence | Result |
|---|---|---|
| Python >=3.12, src layout, minimal runtime/dev deps | pyproject.toml; installed CPython 3.12.10 | PASS |
| Required packages including allocation; empty future dirs | full file listing, 16 import smoke tests | PASS |
| Frozen artifacts present and unchanged | protected-before.json and verify_task1.py | PASS |
| docs governance notice | docs/README.md | PASS |
| Required direct and indirect import boundaries | 4 contracts; 20 negative probes and positive controls | PASS |
| Ruff, mypy, pytest, import-linter | validation-results.json | PASS |
| Required CI triggers and failing steps | .github/workflows/ci.yml, parsed configuration check | PASS (local inspection) |
| Required pre-commit hooks; frozen exclusions | .pre-commit-config.yaml, validation and exclusion checks | PASS |
| Ignore rules, placeholder env, security policy | .gitignore, .env.example, SECURITY.md | PASS |
| README status/setup and version/path metadata only | README.md, src/aqt/core/{version,paths}.py | PASS |
| Frozen Git byte preservation | .gitattributes; 28 filtered/raw object comparisons | PASS |
| Requested skills/workflow | existing AGENTS.md + 4 validated skills | PASS |
| No Task 2, business or scientific implementation | source inspection, complete content below | PASS |


## Exact original authorized specification

TASK 1 — REPOSITORY FOUNDATION
Project: autonomous-quant-trader
Milestone: 0.1
Architecture status: v1.0 FROZEN

You are implementing repository infrastructure only.

DO NOT implement:
- trading strategies
- Binance API access
- market-data downloaders
- feature calculations
- machine learning
- backtesting logic
- portfolio logic
- governor logic
- execution logic
- LLM/agent logic
- secrets or API-key handling

Do not reinterpret or redesign the frozen architecture.

==================================================
1. FIRST: INSPECT THE EXISTING REPOSITORY
==================================================

Before changing anything:

1. Print the current repository tree.
2. Identify existing Python/project configuration files.
3. Identify any existing docs/protocol/spec/schema files.
4. Do not overwrite useful existing files blindly.
5. Report briefly what will be created or changed.

Then implement the foundation below.

==================================================
2. PYTHON PROJECT
==================================================

Target:
- Python >= 3.12

Create a modern pyproject.toml.

Use:
- pytest
- ruff
- mypy
- import-linter
- pydantic
- pydantic-settings

Runtime/data packages allowed at this stage:
- numpy
- polars
- duckdb
- pyarrow
- httpx
- websockets

Do NOT add:
- pandas unless a dependency later requires it
- scikit-learn yet
- lightgbm yet
- statsmodels yet
- arch yet
- Binance SDKs
- vectorbt
- backtrader
- MLflow
- Prefect
- Redis
- PostgreSQL
- Docker orchestration
- Kubernetes

Use a src-layout.

==================================================
3. PACKAGE STRUCTURE
==================================================

Create:

src/
  aqt/
    __init__.py

    core/
      __init__.py

    data/
      __init__.py

    research/
      __init__.py

    features/
      __init__.py

    models/
      __init__.py

    benchmarks/
      __init__.py

    validation/
      __init__.py

    backtest/
      __init__.py

    allocation/
      __init__.py

    governor/
      __init__.py

    execution/
      __init__.py

    monitoring/
      __init__.py

    lockbox_eval/
      __init__.py

tests/
  unit/
  integration/
  canaries/

configs/
scripts/
experiments/

Do not add implementation/business logic to these packages yet.

Use allocation/, NOT portfolio/.

==================================================
4. FROZEN GOVERNANCE FILES
==================================================

The repository must have these top-level governance areas:

docs/
protocols/
schemas/
specs/

If the frozen v1.0 files already exist, DO NOT alter their content.

Expected governance artifacts include:

docs/
  RESEARCH_CONSTITUTION.md
  THREAT_MODEL_v1.md

protocols/
  protocol_v1.yaml

specs/
  CANONICAL_BENCHMARKS_v1.md
  COST_MODEL_v1.md
  FEATURE_FACTORY_v1.md
  BACKTESTER_SPEC_v1.md

schemas/
  HASH_CANONICALIZATION_v1.md
  protocol.schema.json
  hypothesis.schema.json
  experiment.schema.json
  metrics.schema.json
  attestation.schema.json

If any frozen file is absent, report it.
Do NOT invent or reconstruct its contents.

Add a small docs/README.md explaining that the v1.0 governance artifacts are frozen and may not be edited during Cycle C1 except through the formal Constitution process.

Do NOT modify the frozen files themselves.

==================================================
5. IMPORT BOUNDARIES
==================================================

Configure import-linter so CI enforces at minimum:

- aqt.research MUST NOT import aqt.governor
- aqt.research MUST NOT import aqt.execution
- aqt.research MUST NOT import aqt.lockbox_eval

- aqt.governor MUST NOT import aqt.execution
- aqt.governor MUST NOT import aqt.research
- aqt.governor MUST NOT import model-training/research modules

- aqt.execution MUST NOT import aqt.research
- aqt.execution MUST NOT import model-training/research modules

- live-path packages must not import research-agent code

Because the packages are currently mostly empty, create the import-linter configuration in a way that can be enforced now and extended later.

Do not fake passing boundaries by disabling checks.

==================================================
6. CODE QUALITY
==================================================

Configure Ruff for:
- Python 3.12
- formatting
- import sorting
- common correctness rules
- reasonable line length

Configure mypy with strict-enough defaults for new code without making empty scaffold unusable.

Configure pytest.

Add:
tests/unit/test_package_imports.py

It should simply prove the main package and foundational subpackages import successfully.

Do not write fake trading tests.

==================================================
7. CI
==================================================

Create GitHub Actions workflow:

.github/workflows/ci.yml

Run on:
- pull_request
- push to main

CI steps:

1. checkout
2. setup Python 3.12
3. install project + dev dependencies
4. ruff format --check
5. ruff check
6. mypy
7. pytest
8. import-linter

All steps must fail the workflow if they fail.

Do not use continue-on-error.

==================================================
8. PRE-COMMIT
==================================================

Add .pre-commit-config.yaml with:
- ruff check --fix
- ruff format
- basic whitespace/end-of-file checks

Do not add large or unrelated hook collections.

==================================================
9. REPOSITORY HYGIENE
==================================================

Create/update:

.gitignore

Ignore at minimum:
- .venv/
- __pycache__/
- *.pyc
- .pytest_cache/
- .mypy_cache/
- .ruff_cache/
- .env
- .env.*
- data/raw/
- data/processed/
- data/lockbox/
- userdata/
- *.db
- build/
- dist/

Do NOT ignore governance documents.

Add:

.env.example

It must contain comments/placeholders only.
NO real secrets.

Add a SECURITY.md stating:
- never commit exchange credentials
- never place secrets in logs/artifacts/LLM context
- production exchange credentials belong only to the executor identity
- withdrawals must remain disabled
- Cycle 1 contains no live exchange integration

==================================================
10. README
==================================================

Update/create README.md.

Keep it concise.

Include:
- project purpose
- current status: Milestone 0.1 / Task 1
- NO EDGE FOUND is a valid result
- V1 is Binance Spot BTC/ETH research
- no leverage / margin / futures / withdrawals
- current task does not trade
- architecture governance files are frozen
- local developer setup
- commands:

python -m pytest
ruff check .
ruff format --check .
mypy src
lint-imports

Do not advertise guaranteed profitability.

==================================================
11. FOUNDATION METADATA
==================================================

Create:

src/aqt/core/version.py

Only include project version metadata.

Create:

src/aqt/core/paths.py

It may define repository-relative paths only.

It must NOT:
- read market data
- access secrets
- access lockbox files
- implement trading logic

==================================================
12. ACCEPTANCE TESTS
==================================================

Before finishing, run:

python -m pytest
ruff check .
ruff format --check .
mypy src
lint-imports

Also run:

git diff --check

If any fails:
FIX IT.

Do not weaken tests/configuration merely to make them green.

==================================================
13. FINAL RESPONSE
==================================================

Return:

1. concise summary of files created/changed
2. repository tree for the new foundation
3. exact commands run
4. result of every validation command
5. any frozen governance artifact that was missing
6. any assumption you had to make

Do NOT proceed to Task 2.

Do NOT implement bar semantics.

Stop after Task 1 passes.


## New files

- .env.example
- .gitattributes
- .github/workflows/ci.yml
- .gitignore
- .pre-commit-config.yaml
- SECURITY.md
- configs/.gitkeep
- docs/README.md
- experiments/.gitkeep
- pyproject.toml
- scripts/.gitkeep
- src/aqt/__init__.py
- src/aqt/allocation/__init__.py
- src/aqt/backtest/__init__.py
- src/aqt/benchmarks/__init__.py
- src/aqt/core/__init__.py
- src/aqt/core/paths.py
- src/aqt/core/version.py
- src/aqt/data/__init__.py
- src/aqt/execution/__init__.py
- src/aqt/features/__init__.py
- src/aqt/governor/__init__.py
- src/aqt/lockbox_eval/__init__.py
- src/aqt/models/__init__.py
- src/aqt/monitoring/__init__.py
- src/aqt/research/__init__.py
- src/aqt/validation/__init__.py
- tests/canaries/.gitkeep
- tests/integration/.gitkeep
- tests/unit/test_package_imports.py
- review/task1/verify_task1.py
- review/task1/run_checks.ps1

## Existing files changed

- README.md

## Worktree status

```text
 M README.md
?? .agents/skills/claude-adversarial-review/SKILL.md
?? .agents/skills/quant-code-review/SKILL.md
?? .agents/skills/scientific-reproducibility-review/SKILL.md
?? .agents/skills/task-gate-review/SKILL.md
?? .env.example
?? .gitattributes
?? .github/workflows/ci.yml
?? .gitignore
?? .pre-commit-config.yaml
?? AGENTS.md
?? FROZEN_HASHES.json
?? FROZEN_HASHES.json.sha256
?? SECURITY.md
?? configs/.gitkeep
?? docs/README.md
?? docs/RESEARCH_CONSTITUTION.md
?? docs/RESEARCH_CONSTITUTION.md.sha256
?? docs/THREAT_MODEL_v1.md
?? docs/THREAT_MODEL_v1.md.sha256
?? experiments/.gitkeep
?? protocols/protocol_v1.yaml
?? protocols/protocol_v1.yaml.sha256
?? pyproject.toml
?? review/task1/authorized-spec.txt
?? review/task1/boundary-probes.json
?? review/task1/environment-freeze.txt
?? review/task1/pre-task-files.json
?? review/task1/pre-task-status.txt
?? review/task1/protected-before.json
?? review/task1/reviewed-files.json
?? review/task1/run_checks.ps1
?? review/task1/supplemental-results.json
?? review/task1/validation-initial.json
?? review/task1/validation-results.json
?? review/task1/validation-second.json
?? review/task1/verify_task1.py
?? schemas/HASH_CANONICALIZATION_v1.md
?? schemas/HASH_CANONICALIZATION_v1.md.sha256
?? schemas/attestation.schema.json
?? schemas/attestation.schema.json.sha256
?? schemas/experiment.schema.json
?? schemas/experiment.schema.json.sha256
?? schemas/hypothesis.schema.json
?? schemas/hypothesis.schema.json.sha256
?? schemas/metrics.schema.json
?? schemas/metrics.schema.json.sha256
?? schemas/protocol.schema.json
?? schemas/protocol.schema.json.sha256
?? scripts/.gitkeep
?? specs/BACKTESTER_SPEC_v1.md
?? specs/BACKTESTER_SPEC_v1.md.sha256
?? specs/CANONICAL_BENCHMARKS_v1.md
?? specs/CANONICAL_BENCHMARKS_v1.md.sha256
?? specs/COST_MODEL_v1.md
?? specs/COST_MODEL_v1.md.sha256
?? specs/FEATURE_FACTORY_v1.md
?? specs/FEATURE_FACTORY_v1.md.sha256
?? src/aqt/__init__.py
?? src/aqt/allocation/__init__.py
?? src/aqt/backtest/__init__.py
?? src/aqt/benchmarks/__init__.py
?? src/aqt/core/__init__.py
?? src/aqt/core/paths.py
?? src/aqt/core/version.py
?? src/aqt/data/__init__.py
?? src/aqt/execution/__init__.py
?? src/aqt/features/__init__.py
?? src/aqt/governor/__init__.py
?? src/aqt/lockbox_eval/__init__.py
?? src/aqt/models/__init__.py
?? src/aqt/monitoring/__init__.py
?? src/aqt/research/__init__.py
?? src/aqt/validation/__init__.py
?? tests/canaries/.gitkeep
?? tests/integration/.gitkeep
?? tests/unit/test_package_imports.py
```


## Tracked diff (untracked full files also included below)

```diff
diff --git a/README.md b/README.md
index 7ffda99..4566f03 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,54 @@
-# autonomous-quant-trader
\ No newline at end of file
+# autonomous-quant-trader
+
+Scientifically defensible, reproducible, cost-aware crypto spot research.
+Current status: **Milestone 0.1 / Task 1 — repository foundation**.
+**NO EDGE FOUND (`NO_EDGE_FOUND`) is a valid result.**
+
+V1 is Binance Spot BTC/ETH research: no leverage, margin, futures, or
+withdrawals. This task does not trade or connect to an exchange.
+The v1.0 architecture and governance artifacts are frozen; see
+[docs/README.md](docs/README.md) and [SECURITY.md](SECURITY.md).
+
+## Local development
+
+Install Python 3.12 or newer. From the repository root on Windows PowerShell:
+
+```powershell
+python -m venv .venv
+.\.venv\Scripts\Activate.ps1
+python -m pip install -e ".[dev]"
+pre-commit install
+```
+
+On POSIX systems, activate with `source .venv/bin/activate` instead.
+Run the same checks as CI:
+
+```text
+python -m pytest
+ruff check .
+ruff format --check .
+mypy src
+lint-imports
+git diff --check
+```
+
+Source lives in `src/aqt`; packages are empty except for version and path
+metadata in `core`. `core.paths.REPOSITORY_ROOT` describes this source checkout,
+not an installed wheel's data location. It performs no filesystem reads.
+Import contracts cover direct and indirect dependencies, including descendants.
+Research-agent code belongs under `aqt.research`; any future agent package
+elsewhere must be added to the live-path forbidden contracts before use.
+
+Repository review instructions are in `AGENTS.md` and `.agents/skills/`.
+The Task 1 evidence and Claude handoff are in `review/task1/`.
+
+The existing local Task 1 environment uses portable Python 3.12.10. To use it
+from PowerShell without changing system Python settings:
+
+```powershell
+$env:PATH = "$PWD\.venv;$PWD\.venv\Scripts;$env:PATH"
+python -m pytest
+```
+
+This portable environment has no activation script or standard-library venv
+module. The fresh-install steps above assume a full Python installation.
```


## Reviewed snapshot SHA-256

```json
{
  ".agents/skills/claude-adversarial-review/SKILL.md": "a458262c26d044a57188571703d3e2ed46b6ca5ace271a81a49a8b27b5e8d77e",
  ".agents/skills/quant-code-review/SKILL.md": "d4bd95b8cb7cbb8bf6b2fd9a209f8cbaab5b31ccf84e2f1327fb65c3aa8ef90b",
  ".agents/skills/scientific-reproducibility-review/SKILL.md": "c86b8d0ac012d0bcd0ce6fc29756f1184439a444e483d398f6bd73c9eb4e142c",
  ".agents/skills/task-gate-review/SKILL.md": "624e21367f5f4fd7d489f9c6337eb4966ccc444b87a5467932fba3c561c82f10",
  ".env.example": "eeb0d966e75cb9dc165cf8a92f431dc6f1ab517a8799793de312e9128cae59d0",
  ".gitattributes": "c9fbda04e586ba51ee07412d87d06606128c78208f1d786a97e05897c72c2738",
  ".github/workflows/ci.yml": "0e5c1581ae721b253be27098d49239acc0ae1ee497623e1daf2816c4f2bca495",
  ".gitignore": "606d1c6164ede26c05606b5f32d787de3eaeb6a1481d221ee8bd68bf9d75af96",
  ".pre-commit-config.yaml": "5a64d8d9e329c78a4008dcdf95b297d8bfdd4f0648eee90931f0666f76b3058d",
  "AGENTS.md": "13f65d60429c393261552ad03127c9925ab89e29c76a7fee545a95ad708d2f77",
  "FROZEN_HASHES.json": "962bdb5096ae191556933cdde940d34f1548261f2ee9a7be65b523208b26912d",
  "FROZEN_HASHES.json.sha256": "c3c6fad72b72190f9641f00c5b0a8613e07881d98dfe12266f9a148468325d31",
  "README.md": "7c61f4243ea783148962487007a2e8c5954f0a030bd389a1e9e1eda49f19dc29",
  "SECURITY.md": "808bad0b71140b20cf743759c062a2f55fc4f6bae3fa0f17955c9125043c64fe",
  "configs/.gitkeep": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "docs/README.md": "f97a75eafe4b8a35dcb0e08121e35f3f2bcc3b9c0b47559fab61a753829a2262",
  "docs/RESEARCH_CONSTITUTION.md": "776396a25012276f22c4d7478166614e2f4f58e1a866e274ff8437e60cc09516",
  "docs/RESEARCH_CONSTITUTION.md.sha256": "8ee688159d5a2798eeeb3d826aa08a5d4cb88327966cd40cc786c7710efc49e5",
  "docs/THREAT_MODEL_v1.md": "8817a315b03564e833d6c556da5de07a0740c7d87c9f7820dd8280082e745d4e",
  "docs/THREAT_MODEL_v1.md.sha256": "a5ff879da90c3a5f0eea458f8186d8c4a55372b29a15bca985d979a56954e2a6",
  "experiments/.gitkeep": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "protocols/protocol_v1.yaml": "d22efb8989cb31a1d673000bba1e69baf5e0965bb400a8798aa966a3035d8b26",
  "protocols/protocol_v1.yaml.sha256": "cc6d2fb0498b98fc644eb51fb4f38d06314f794dc4bf2be8bb70cd56a777729f",
  "pyproject.toml": "5ae2ef39cac82e7ec06d5953c86975509f1c74ed09618e32de351111183c0840",
  "schemas/HASH_CANONICALIZATION_v1.md": "189e3525c5c63f9605f739386aa3edc16b7bf44b5f4f7196dd7f698c9fbdc3cf",
  "schemas/HASH_CANONICALIZATION_v1.md.sha256": "075cb0edb017fda165a32617aa38ed220937d396f53f8cc3b9c86780a8978984",
  "schemas/attestation.schema.json": "43e975bfe3a621371afd475ae6c8a53566e096b07cac45b3312a0ffe0ab9c2fa",
  "schemas/attestation.schema.json.sha256": "7ee6580c9c1f65bc664f375aba78a6581ed27e6a908fbb46082beaf9fd37e488",
  "schemas/experiment.schema.json": "46b85f29b029598d18f8c0691044c4a49589049e42c0c605f4c9dbb3c04be91a",
  "schemas/experiment.schema.json.sha256": "a071ed727c053f34300d524f18915ad980ffc708cb3c272e09f2c52508f005bf",
  "schemas/hypothesis.schema.json": "e1175e8b934b106d368c67e2b1851d2ccdde7ae69d27b8407fa573715bd4275f",
  "schemas/hypothesis.schema.json.sha256": "9a54c6625eaa420c81dd198da3611eea2df54198eee9e0bb0d17969aaae485ca",
  "schemas/metrics.schema.json": "e74d9c84ed717f1be3d099fa75ace52ee939a77486c0bbf775ca16b58ff6da68",
  "schemas/metrics.schema.json.sha256": "55f9f50678702d2168130c8d5c8cf703e02c0443356722ecbadc45bcf0ec96f0",
  "schemas/protocol.schema.json": "45eff36c324d18c1efda48f32e440d1a1b2a9bc5d4a2cf4e7db370973350134e",
  "schemas/protocol.schema.json.sha256": "ff3983d0ebb87f8342039bc89ff05b12a33235de40d26f09e7cd199c165a835a",
  "scripts/.gitkeep": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "specs/BACKTESTER_SPEC_v1.md": "a1bee89f6e0d1fe309b5b12317ff277e55a91b96c81174789f4bc4c09503d961",
  "specs/BACKTESTER_SPEC_v1.md.sha256": "aab08d35f73dc9fe028710020b482c05602bf20f1565cbfe68dff479fdf3aa79",
  "specs/CANONICAL_BENCHMARKS_v1.md": "b1baffd321c9adf2482350b35c73b3f436e9dda483d86b2c751e7ddddc606222",
  "specs/CANONICAL_BENCHMARKS_v1.md.sha256": "58e4e23498acf628a768329a413ab1101d695d86133dbf382e3edaebce6aaad9",
  "specs/COST_MODEL_v1.md": "3f5e62ab2df26f360f3ca13d2db379e95a1e52b25dc3d2c8f2683878b49327ae",
  "specs/COST_MODEL_v1.md.sha256": "a9b47f2c6364adb6e2fee3d04195c49d17e3934964bcc3a4d47d78680cf24066",
  "specs/FEATURE_FACTORY_v1.md": "c8a0ea027de04889ff90ca6a89ad1096a335ee9c368fea8cb138b85dbbe30348",
  "specs/FEATURE_FACTORY_v1.md.sha256": "49ce5adf439c142165ecd44e6cda0a208aff7fcde6de0b4c66ca802368eb29e6",
  "src/aqt/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/allocation/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/backtest/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/benchmarks/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/core/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/core/paths.py": "8cded3ef8a9093d1015892a9a04911574fcb5373f971c7652798c65933dc15e3",
  "src/aqt/core/version.py": "26b355c93e8469062bca6f1a88932d97f9fd0556abfec89f5bd8761c5f51d420",
  "src/aqt/data/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/execution/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/features/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/governor/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/lockbox_eval/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/models/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/monitoring/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/research/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "src/aqt/validation/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "tests/canaries/.gitkeep": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "tests/integration/.gitkeep": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "tests/unit/test_package_imports.py": "5d54a42b204547d0d16374f33d09a664766dd8eaf6db4126aec72c2c074aa62e",
  "review/task1/verify_task1.py": "7b8ef71cd6dc48a91ef1b059f1f7c53488ff27fed82fe5807ccb8d3f104ce7f4",
  "review/task1/run_checks.ps1": "3bff43968fadfe08b7008559cef5771b51b2042a2c1419cd062465df2d096c57"
}
```


## Final checks

```json
[
  {
    "command": "python -m pytest",
    "exit_code": 0,
    "output": "============================= test session starts =============================\r\nplatform win32 -- Python 3.12.10, pytest-8.4.2, pluggy-1.6.0\r\nrootdir: D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\r\nconfigfile: pyproject.toml\r\ntestpaths: tests\r\ncollected 16 items\r\n\r\ntests\\unit\\test_package_imports.py ................                      [100%]\r\n\r\n============================= 16 passed in 0.05s ==============================\r\n"
  },
  {
    "command": "ruff check .",
    "exit_code": 0,
    "output": "All checks passed!\r\n"
  },
  {
    "command": "ruff format --check .",
    "exit_code": 0,
    "output": "18 files already formatted\r\n"
  },
  {
    "command": "mypy src",
    "exit_code": 0,
    "output": "Success: no issues found in 16 source files\r\n"
  },
  {
    "command": "lint-imports",
    "exit_code": 0,
    "output": "\r\n╔══╗─────────▶╔╗ ╔╗      ╔╗◀───┐\r\n╚╣╠╝◀─────┐  ╔╝╚╗║║────▶╔╝╚╗   │\r\n ║║   ╔══╦══╦╩╗╔╝║║  ╔╦═╩╗╔╝╔═╦══╗\r\n ║║╔══╣╔╗║╔╗║╔╣║ ║║ ╔╬╣╔╗║║ ║│║╔═╝\r\n╔╣╠╣║║║╚╝║╚╝║║║╚╗║╚═╝║║║║║╚╗║═╣║\r\n╚══╩╩╩╣╔═╩══╩╝╚═╝╚═══╩╩╝╚╩═╩╩═╩╝\r\n  └──▶║║                    ▲ \r\n      ╚╝────────────────────┘\r\n\r\n\r\n---------\r\nContracts\r\n---------\r\n\r\nAnalyzed 16 files, 0 dependencies.\r\n----------------------------------\r\n\r\nResearch cannot reach protected runtime or lockbox packages KEPT\r\nGovernor cannot reach execution or model training KEPT\r\nExecution cannot reach model training KEPT\r\nLive packages cannot reach research agent code KEPT\r\n\r\nContracts: 4 kept, 0 broken.\r\n"
  },
  {
    "command": "git diff --check",
    "exit_code": 0,
    "output": "warning: in the working copy of 'README.md', LF will be replaced by CRLF the next time Git touches it\r\n"
  },
  {
    "command": "python review/task1/verify_task1.py",
    "exit_code": 0,
    "output": "PASS: 28 protected bytes/inventory; all existing untracked work; 14 sidecars\r\nPASS: Constitution canonical hash 4cb6c7d35e238bdd778e8dd74b25d1b978e57fedffdbfae83b2867b5ec4fb8d7; manifest/protocol bindings\r\nPASS: five Draft 2020-12 schemas; protocol instance; two rejection controls\r\nPASS: frozen hook exclusions, README inclusion, env ignore exception, CI\r\nPASS: 20 direct/indirect probes rejected; controls passed\r\n"
  },
  {
    "command": "python -m pip check",
    "exit_code": 0,
    "output": "No broken requirements found.\r\n"
  },
  {
    "command": "pre-commit validate-config",
    "exit_code": 0,
    "output": ""
  }
]

```


## Supplemental checks

```json
[
  {
    "command": "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe \"C:\\Users\\PMP Cordination\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py\" D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.agents\\skills\\claude-adversarial-review",
    "exit_code": 0,
    "output": "Skill is valid!\n"
  },
  {
    "command": "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe \"C:\\Users\\PMP Cordination\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py\" D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.agents\\skills\\quant-code-review",
    "exit_code": 0,
    "output": "Skill is valid!\n"
  },
  {
    "command": "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe \"C:\\Users\\PMP Cordination\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py\" D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.agents\\skills\\scientific-reproducibility-review",
    "exit_code": 0,
    "output": "Skill is valid!\n"
  },
  {
    "command": "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe \"C:\\Users\\PMP Cordination\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py\" D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.agents\\skills\\task-gate-review",
    "exit_code": 0,
    "output": "Skill is valid!\n"
  },
  {
    "command": "git check-attr text -- docs/RESEARCH_CONSTITUTION.md docs/RESEARCH_CONSTITUTION.md.sha256 docs/THREAT_MODEL_v1.md docs/THREAT_MODEL_v1.md.sha256 FROZEN_HASHES.json FROZEN_HASHES.json.sha256 protocols/protocol_v1.yaml protocols/protocol_v1.yaml.sha256 schemas/attestation.schema.json schemas/attestation.schema.json.sha256 schemas/experiment.schema.json schemas/experiment.schema.json.sha256 schemas/HASH_CANONICALIZATION_v1.md schemas/HASH_CANONICALIZATION_v1.md.sha256 schemas/hypothesis.schema.json schemas/hypothesis.schema.json.sha256 schemas/metrics.schema.json schemas/metrics.schema.json.sha256 schemas/protocol.schema.json schemas/protocol.schema.json.sha256 specs/BACKTESTER_SPEC_v1.md specs/BACKTESTER_SPEC_v1.md.sha256 specs/CANONICAL_BENCHMARKS_v1.md specs/CANONICAL_BENCHMARKS_v1.md.sha256 specs/COST_MODEL_v1.md specs/COST_MODEL_v1.md.sha256 specs/FEATURE_FACTORY_v1.md specs/FEATURE_FACTORY_v1.md.sha256",
    "exit_code": 0,
    "output": "docs/RESEARCH_CONSTITUTION.md: text: unset\ndocs/RESEARCH_CONSTITUTION.md.sha256: text: unset\ndocs/THREAT_MODEL_v1.md: text: unset\ndocs/THREAT_MODEL_v1.md.sha256: text: unset\nFROZEN_HASHES.json: text: unset\nFROZEN_HASHES.json.sha256: text: unset\nprotocols/protocol_v1.yaml: text: unset\nprotocols/protocol_v1.yaml.sha256: text: unset\nschemas/attestation.schema.json: text: unset\nschemas/attestation.schema.json.sha256: text: unset\nschemas/experiment.schema.json: text: unset\nschemas/experiment.schema.json.sha256: text: unset\nschemas/HASH_CANONICALIZATION_v1.md: text: unset\nschemas/HASH_CANONICALIZATION_v1.md.sha256: text: unset\nschemas/hypothesis.schema.json: text: unset\nschemas/hypothesis.schema.json.sha256: text: unset\nschemas/metrics.schema.json: text: unset\nschemas/metrics.schema.json.sha256: text: unset\nschemas/protocol.schema.json: text: unset\nschemas/protocol.schema.json.sha256: text: unset\nspecs/BACKTESTER_SPEC_v1.md: text: unset\nspecs/BACKTESTER_SPEC_v1.md.sha256: text: unset\nspecs/CANONICAL_BENCHMARKS_v1.md: text: unset\nspecs/CANONICAL_BENCHMARKS_v1.md.sha256: text: unset\nspecs/COST_MODEL_v1.md: text: unset\nspecs/COST_MODEL_v1.md.sha256: text: unset\nspecs/FEATURE_FACTORY_v1.md: text: unset\nspecs/FEATURE_FACTORY_v1.md.sha256: text: unset\n"
  },
  {
    "command": "28 protected files: compare Git filtered object hashes with raw object hashes and trusted SHA-256",
    "exit_code": 0,
    "output": "All 28 paths preserve original bytes through Git filters; all match the pre-task baseline."
  }
]

```


## Exact environment

```text
annotated-types==0.8.0
attrs==26.1.0
-e git+https://github.com/meedo1985/autonomous-quant-trader.git@b596a8e73a563cb376361b3ca3cada8c0ea326f6#egg=autonomous_quant_trader
cfgv==3.5.0
click==8.5.0
colorama==0.4.6
distlib==0.4.3
editables==0.6
filelock==3.32.6
grimp==3.17
hatchling==1.32.0
identify==2.6.19
import-linter==2.15
iniconfig==2.3.0
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
librt==0.15.0
markdown-it-py==4.2.0
mdurl==0.1.2
mypy==1.20.2
mypy_extensions==1.1.0
nodeenv==1.10.0
packaging==26.3
pathspec==1.1.1
pip==26.2.1
platformdirs==4.11.8
pluggy==1.6.0
pre_commit==4.6.2
pydantic==2.13.5
pydantic-settings==2.15.0
pydantic_core==2.46.5
Pygments==2.21.0
pytest==8.4.2
python-discovery==1.6.0
python-dotenv==1.2.3
PyYAML==6.0.2
referencing==0.37.0
rich==15.0.0
rpds-py==2026.6.3
ruff==0.11.13
tomlkit==0.15.1
trove-classifiers==2026.6.1.19
typing-inspection==0.4.4
typing_extensions==4.16.0
virtualenv==21.7.9

```


## Forbidden-import probe results

```json
[
  {
    "source": "aqt.allocation",
    "target": "aqt.research",
    "indirect": false,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-bt5vfu00",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 18 files, 1 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code BROKEN\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nLive packages cannot reach research agent code\n----------------------------------------------\n\naqt.allocation is not allowed to import aqt.research:\n\n-   aqt.allocation.probe -> aqt.research.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.allocation",
    "target": "aqt.research",
    "indirect": true,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-lymabe_0",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 19 files, 2 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code BROKEN\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nLive packages cannot reach research agent code\n----------------------------------------------\n\naqt.allocation is not allowed to import aqt.research:\n\n-   aqt.allocation.probe -> aqt.core.bridge (l.1)\n    aqt.core.bridge -> aqt.research.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.execution",
    "target": "aqt.models",
    "indirect": false,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-qw6i_t7l",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 18 files, 1 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training BROKEN\nLive packages cannot reach research agent code KEPT\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nExecution cannot reach model training\n-------------------------------------\n\naqt.execution is not allowed to import aqt.models:\n\n-   aqt.execution.probe -> aqt.models.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.execution",
    "target": "aqt.models",
    "indirect": true,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-klusxa3y",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 19 files, 2 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training BROKEN\nLive packages cannot reach research agent code KEPT\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nExecution cannot reach model training\n-------------------------------------\n\naqt.execution is not allowed to import aqt.models:\n\n-   aqt.execution.probe -> aqt.core.bridge (l.1)\n    aqt.core.bridge -> aqt.models.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.execution",
    "target": "aqt.research",
    "indirect": false,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-ithn7y2y",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 18 files, 1 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code BROKEN\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nLive packages cannot reach research agent code\n----------------------------------------------\n\naqt.execution is not allowed to import aqt.research:\n\n-   aqt.execution.probe -> aqt.research.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.execution",
    "target": "aqt.research",
    "indirect": true,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-x5ky3otg",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 19 files, 2 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code BROKEN\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nLive packages cannot reach research agent code\n----------------------------------------------\n\naqt.execution is not allowed to import aqt.research:\n\n-   aqt.execution.probe -> aqt.core.bridge (l.1)\n    aqt.core.bridge -> aqt.research.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.governor",
    "target": "aqt.execution",
    "indirect": false,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-1u_6ahqt",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 18 files, 1 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training BROKEN\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code KEPT\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nGovernor cannot reach execution or model training\n-------------------------------------------------\n\naqt.governor is not allowed to import aqt.execution:\n\n-   aqt.governor.probe -> aqt.execution.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.governor",
    "target": "aqt.execution",
    "indirect": true,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-lqgr6g9r",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 19 files, 2 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training BROKEN\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code KEPT\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nGovernor cannot reach execution or model training\n-------------------------------------------------\n\naqt.governor is not allowed to import aqt.execution:\n\n-   aqt.governor.probe -> aqt.core.bridge (l.1)\n    aqt.core.bridge -> aqt.execution.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.governor",
    "target": "aqt.models",
    "indirect": false,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-_bz21n0p",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 18 files, 1 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training BROKEN\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code KEPT\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nGovernor cannot reach execution or model training\n-------------------------------------------------\n\naqt.governor is not allowed to import aqt.models:\n\n-   aqt.governor.probe -> aqt.models.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.governor",
    "target": "aqt.models",
    "indirect": true,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-d2ibkgvf",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 19 files, 2 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training BROKEN\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code KEPT\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nGovernor cannot reach execution or model training\n-------------------------------------------------\n\naqt.governor is not allowed to import aqt.models:\n\n-   aqt.governor.probe -> aqt.core.bridge (l.1)\n    aqt.core.bridge -> aqt.models.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.governor",
    "target": "aqt.research",
    "indirect": false,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-toi4bel3",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 18 files, 1 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code BROKEN\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nLive packages cannot reach research agent code\n----------------------------------------------\n\naqt.governor is not allowed to import aqt.research:\n\n-   aqt.governor.probe -> aqt.research.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.governor",
    "target": "aqt.research",
    "indirect": true,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-qricrhmn",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 19 files, 2 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code BROKEN\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nLive packages cannot reach research agent code\n----------------------------------------------\n\naqt.governor is not allowed to import aqt.research:\n\n-   aqt.governor.probe -> aqt.core.bridge (l.1)\n    aqt.core.bridge -> aqt.research.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.monitoring",
    "target": "aqt.research",
    "indirect": false,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-l51nn6wm",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 18 files, 1 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code BROKEN\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nLive packages cannot reach research agent code\n----------------------------------------------\n\naqt.monitoring is not allowed to import aqt.research:\n\n-   aqt.monitoring.probe -> aqt.research.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.monitoring",
    "target": "aqt.research",
    "indirect": true,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-74iukg6o",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 19 files, 2 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages KEPT\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code BROKEN\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nLive packages cannot reach research agent code\n----------------------------------------------\n\naqt.monitoring is not allowed to import aqt.research:\n\n-   aqt.monitoring.probe -> aqt.core.bridge (l.1)\n    aqt.core.bridge -> aqt.research.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.research",
    "target": "aqt.execution",
    "indirect": false,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-031aujio",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 18 files, 1 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages BROKEN\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code KEPT\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nResearch cannot reach protected runtime or lockbox packages\n-----------------------------------------------------------\n\naqt.research is not allowed to import aqt.execution:\n\n-   aqt.research.probe -> aqt.execution.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.research",
    "target": "aqt.execution",
    "indirect": true,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-qv5falbj",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 19 files, 2 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages BROKEN\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code KEPT\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nResearch cannot reach protected runtime or lockbox packages\n-----------------------------------------------------------\n\naqt.research is not allowed to import aqt.execution:\n\n-   aqt.research.probe -> aqt.core.bridge (l.1)\n    aqt.core.bridge -> aqt.execution.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.research",
    "target": "aqt.governor",
    "indirect": false,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-ih5jkobe",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 18 files, 1 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages BROKEN\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code KEPT\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nResearch cannot reach protected runtime or lockbox packages\n-----------------------------------------------------------\n\naqt.research is not allowed to import aqt.governor:\n\n-   aqt.research.probe -> aqt.governor.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.research",
    "target": "aqt.governor",
    "indirect": true,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-ev4tgyfi",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 19 files, 2 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages BROKEN\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code KEPT\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nResearch cannot reach protected runtime or lockbox packages\n-----------------------------------------------------------\n\naqt.research is not allowed to import aqt.governor:\n\n-   aqt.research.probe -> aqt.core.bridge (l.1)\n    aqt.core.bridge -> aqt.governor.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.research",
    "target": "aqt.lockbox_eval",
    "indirect": false,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-tpr046ks",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 18 files, 1 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages BROKEN\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code KEPT\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nResearch cannot reach protected runtime or lockbox packages\n-----------------------------------------------------------\n\naqt.research is not allowed to import aqt.lockbox_eval:\n\n-   aqt.research.probe -> aqt.lockbox_eval.probe (l.1)\n\n\n"
  },
  {
    "source": "aqt.research",
    "target": "aqt.lockbox_eval",
    "indirect": true,
    "command": [
      "D:\\PMP-programs-for-sharawi\\autonomous-quant-trader\\.venv\\python.exe",
      "-c",
      "import sys; sys.path.insert(0, 'src'); from importlinter.cli import lint_imports_command as run; run()",
      "--no-cache"
    ],
    "cwd": "C:\\Users\\PMPCOR~1\\AppData\\Local\\Temp\\aqt-task1-import-7xe3pf2h",
    "control_exit": 0,
    "violation_exit": 1,
    "output": "\n\u2554\u2550\u2550\u2557\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u25b6\u2554\u2557 \u2554\u2557      \u2554\u2557\u25c0\u2500\u2500\u2500\u2510\n\u255a\u2563\u2560\u255d\u25c0\u2500\u2500\u2500\u2500\u2500\u2510  \u2554\u255d\u255a\u2557\u2551\u2551\u2500\u2500\u2500\u2500\u25b6\u2554\u255d\u255a\u2557   \u2502\n \u2551\u2551   \u2554\u2550\u2550\u2566\u2550\u2550\u2566\u2569\u2557\u2554\u255d\u2551\u2551  \u2554\u2566\u2550\u2569\u2557\u2554\u255d\u2554\u2550\u2566\u2550\u2550\u2557\n \u2551\u2551\u2554\u2550\u2550\u2563\u2554\u2557\u2551\u2554\u2557\u2551\u2554\u2563\u2551 \u2551\u2551 \u2554\u256c\u2563\u2554\u2557\u2551\u2551 \u2551\u2502\u2551\u2554\u2550\u255d\n\u2554\u2563\u2560\u2563\u2551\u2551\u2551\u255a\u255d\u2551\u255a\u255d\u2551\u2551\u2551\u255a\u2557\u2551\u255a\u2550\u255d\u2551\u2551\u2551\u2551\u2551\u255a\u2557\u2551\u2550\u2563\u2551\n\u255a\u2550\u2550\u2569\u2569\u2569\u2563\u2554\u2550\u2569\u2550\u2550\u2569\u255d\u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2569\u2569\u255d\u255a\u2569\u2550\u2569\u2569\u2550\u2569\u255d\n  \u2514\u2500\u2500\u25b6\u2551\u2551                    \u25b2 \n      \u255a\u255d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n\n---------\nContracts\n---------\n\nAnalyzed 19 files, 2 dependencies.\n----------------------------------\n\nResearch cannot reach protected runtime or lockbox packages BROKEN\nGovernor cannot reach execution or model training KEPT\nExecution cannot reach model training KEPT\nLive packages cannot reach research agent code KEPT\n\nContracts: 3 kept, 1 broken.\n\n\n----------------\nBroken contracts\n----------------\n\nResearch cannot reach protected runtime or lockbox packages\n-----------------------------------------------------------\n\naqt.research is not allowed to import aqt.lockbox_eval:\n\n-   aqt.research.probe -> aqt.core.bridge (l.1)\n    aqt.core.bridge -> aqt.lockbox_eval.probe (l.1)\n\n\n"
  }
]

```


## Complete file: .agents/skills/claude-adversarial-review/SKILL.md

~~~~text
---
name: claude-adversarial-review
description: Prepare a concise Claude adversarial review packet after major autonomous-quant-trader tasks or adjudicate returned Claude findings. Supports human relay without a Claude connector.
---

# Claude adversarial review

Read root `AGENTS.md` and the task's acceptance criteria. Claude is an independent adversarial reviewer, not an authority or an approval substitute. This skill prepares review material or adjudicates feedback; it does not authorize external transmission, implementation, merging, or governance amendments.

## Prepare a packet

Inspect the actual staged, unstaged, and relevant untracked files; record the base commit and reviewed state. Plain `git diff` omits untracked files. Separate pre-existing changes from this task. Never claim Claude saw a file or ran a check without evidence.

After local review passes, give the human a copyable packet in the response or a task-authorized review location outside frozen directories. For a blocked task, label any diagnostic packet BLOCKED, not ready for approval. Include:

- Task scope, exclusions, and exact acceptance criteria.
- Base/HEAD commit IDs, dirty-worktree status, changed file list, and diff summary. Include the actual relevant unified diff or complete new files as attachments/excerpts so the review is independently possible; a summary alone is not sufficient.
- Exact validation commands, exit codes, outcomes, and checks not run with reasons.
- Frozen-artifact verification method/results; relevant manifest, code, configuration, or artifact hashes. Hash the exact reviewed files when an uncommitted snapshot needs identification.
- Unresolved assumptions, limitations, and known blockers.
- Exact questions targeting plausible correctness, scope, reproducibility, security, or governance defects in this change.

Ask Claude to return stable finding IDs under `BLOCKER`, `NON-BLOCKING`, or `QUESTION`. Each finding should identify file/line, triggering scenario, evidence, impact, and a minimal proposed correction or clarifying question. Request explicit missing-evidence statements instead of guesses, and no new strategy logic.

Do not include secrets, raw confirmation/lockbox data, or restricted diagnostics. If Claude is not directly connected, label the packet READY FOR HUMAN RELAY and ask the human to paste Claude's full response back with its finding IDs. Direct transmission requires an available connection and explicit authorization to send the identified material; do not install a connector or claim a review occurred as part of packet preparation.

## Adjudicate feedback

For each finding, preserve its ID and Claude severity, then record:

`ID | Claude severity | AGREE / PARTIAL / DISAGREE | technical reasoning and evidence | disposition | validation`

Reproduce the alleged defect using authorized evidence. AGREE means evidence supports it; PARTIAL identifies exactly what holds and what does not; DISAGREE cites a counterexample, test, governing requirement, or faulty premise. With incomplete evidence, record the uncertainty and required check rather than inventing support. Separately state whether a local blocker remains.

Never automatically apply architecture, protocol, statistical, safety, or frozen-governance changes. Present those as proposals for the applicable human/owner decision. Frozen amendments must follow Constitution sections 3-4 and 27; AI cannot author, merge, activate, or self-approve amendments. Routine authorized corrections still require local validation and an updated packet if the reviewed snapshot changes. A Claude opinion does not satisfy missing human review or remove Constitution section 16 merge requirements.

~~~~


## Complete file: .agents/skills/quant-code-review/SKILL.md

~~~~text
---
name: quant-code-review
description: Review autonomous-quant-trader tasks involving data, backtesting, validation, benchmarks, features, models, or promotion gates for scientific and temporal correctness. Do not invent strategy logic.
---

# Quant code review

Read root `AGENTS.md`, the Constitution, protocol, and applicable frozen specs. Review the actual code paths and task acceptance criteria; do not design strategies, tune parameters, change statistical thresholds, or broaden the task. Use synthetic or exploration evidence only and respect restricted-data identities.

Follow a representative observation from availability time through features, labels, fitting, decisions, fills, returns, costs, metrics, and eligibility. Check relevant callers and tests, not only the changed lines.

- Look-ahead and label leakage: future inputs, centered windows, negative shifts, globally fit preprocessing, feature selection using OOS results, and labels entering their own predictors.
- Time semantics: UTC and timestamp meaning, availability versus event time, inclusive boundaries, joins/resampling, decision at close(t), and baseline fill at open(t+1). Features must exist by the decision timestamp; PnL must use actual simulated exposure.
- Sampling assumptions: survivorship, delistings/venue status, point-in-time universe/fees/filters, outages, missing/duplicate bars, silent dropping or correction, and untradeable intervals.
- Partition integrity: exploration/confirmation/lockbox boundaries, training/OOS separation, rolling fit windows, purge/embargo, overlapping labels, dependence-aware ESS, and fold aggregates. Bar count is not sample size; BTC/ETH agreement is not independent replication.
- Selection bias: hidden retries, excluded failures, per-fold reselection, implicit parameter tuning, unregistered grids, multiple comparisons, family/lifetime trial accounting, and post-result benchmark or acceptance-criterion changes.
- Transaction costs: traded-notional units, per-side charging, turnover, spread/slippage/fees, cost stress and delay stress, and agreement with the frozen cost model. Verify applicable analytic/oracle identities.
- Benchmark consistency: fixed identities and parameters, same bar/execution/cost semantics and applicable scheduling/band/min-hold rules, paired series alignment, and the predeclared comparison benchmark.
- Exposure constraints: accidental shorting or leverage, clipping and bounds, initial holdings, cash/accounting, scheduled risk increases, intraday reductions, and minimum holding periods.
- Determinism: seeds, data ordering, unstable joins, parallel reductions, serialization, reproducible outputs, and explicit handling of numerical edge cases without undocumented fallbacks.

For each applicable area, report evidence or a precise gap. Classify findings as `BLOCKER`, `NON-BLOCKING`, or `QUESTION`, with file/line, triggering example, governing rule, impact, and proposed minimal correction. Do not invent missing financial conventions to close a finding. Missing mandatory tests or violated scientific/safety invariants are blockers. Preserve `NO_EDGE_FOUND` as a valid result. Return findings to `task-gate-review`; never apply frozen-governance or scientific changes automatically.

~~~~


## Complete file: .agents/skills/scientific-reproducibility-review/SKILL.md

~~~~text
---
name: scientific-reproducibility-review
description: Review autonomous-quant-trader scientific tasks for determinism, provenance, canonical hashes, preregistration, schema enforcement, and reproducible artifacts. Use for scientific implementation and result review.
---

# Scientific reproducibility review

Read root `AGENTS.md`, the Constitution, protocol, `schemas/HASH_CANONICALIZATION_v1.md`, and applicable specifications. Review existing work against those artifacts; do not invent defaults, scientific criteria, or strategy logic. `NO_EDGE_FOUND` is valid, and must not trigger post-result tuning of success criteria.

Trace inputs through configuration, code, environment, execution, and outputs. Use synthetic or authorized exploration fixtures; never access restricted confirmation/lockbox material to reproduce a review finding.

- Check deterministic ordering, random-number generators and fixed/derived seeds, concurrency, reductions, and library nondeterminism. Seeds alone are not proof of reproducibility.
- Verify raw file SHA-256 sidecars separately from canonical content hashes. Apply the frozen self-reference rules without rewriting files. Check embedded dependency hashes, schema versions, and lineage against the actual inputs.
- Check schema enforcement at read/write boundaries, including missing/unknown/invalid values and rejection paths; parsing alone is not enforcement. Do not strengthen a frozen schema by editing it.
- Trace each scientific/configuration value to its frozen or preregistered source and binding time. Flag values existing only as code defaults, undocumented environment overrides, post-result changes, and unbound data/engine hashes before a trial. Distinguish ordinary implementation constants from scientific choices.
- Check exact dependency/runtime version pinning and recorded environment assumptions: OS, architecture, timezone/locale, numeric precision, BLAS/thread settings, serialization, newline/encoding rules, and relevant hardware.
- Require artifact traceability to code revision/hash, protocol, hypothesis, seeds, data manifest, schema, dependency versions, and execution identity where applicable. Check immutable inputs and append-only accounting; failed/aborted evaluated trials must not disappear.
- Detect silent fallback behavior: swallowed exceptions, missing dependencies/fees/data replaced by defaults, dropped rows, skipped checks, changed estimators, or nondeterministic seed selection. A fallback is acceptable only where governance authorizes it and its use is explicit and traceable.
- Run the task-required independent reruns and compare canonical artifact bytes/hashes byte-for-byte. State exactly what was reproduced and under which environment. If an applicable frozen contract prescribes numerical tolerance, report that test separately; a tolerance match is not byte-for-byte equality. Do not normalize away unexplained differences or invent tolerances.

Report `BLOCKER`, `NON-BLOCKING`, and `QUESTION` findings with file/line, governing requirement, reproducible evidence, impact, and next check. Mark checks N/A with a reason and distinguish missing evidence from passed validation. Propose changes only; required validation failures or missing mandatory reproducibility evidence block task completion. Return findings to `task-gate-review` without invoking it recursively.

~~~~


## Complete file: .agents/skills/task-gate-review/SKILL.md

~~~~text
---
name: task-gate-review
description: Run the end-of-task acceptance gate for every autonomous-quant-trader project task, especially before declaring a major task complete, and prepare the Claude review handoff after local checks pass.
---

# Task gate review

Read root `AGENTS.md`, the authorized task and its acceptance criteria, and relevant governance. This is a review gate, not authorization to implement the next task, commit, merge, publish, or modify governance.

1. Inspect `git status --untracked-files=all`, `git diff`, and `git diff --cached`, plus the relevant base-commit diff if the task includes commits. Read relevant untracked files separately; an empty Git diff does not prove an empty change. Separate pre-existing changes from this task and flag out-of-scope edits.
2. Identify required validation from the task, repository configuration/CI, and governing specs. Run every mandatory command, including tests, lint, type, and import-boundary checks where applicable. Record command, environment, exit code, result, and evidence. N/A needs a concrete reason; unavailable tools or skipped mandatory checks are blockers, never passes. Do not add new implementation/tooling just to fabricate a green gate.
3. Verify the frozen v1.0 files in `docs/`, `protocols/`, `schemas/`, and `specs/`, `FROZEN_HASHES.json`, and all sidecars. Compare file inventory and bytes against the trusted pre-task snapshot/accepted baseline, including untracked artifacts and sidecars themselves; detect deletion or changed manifests as well as changed content. Independently verify all sidecar SHA-256 values, manifest entries, Constitution canonical self-hash, and relevant embedded hash bindings using `schemas/HASH_CANONICALIZATION_v1.md`. Matching freshly changed sidecars is not proof of preservation. Never repair/regenerate frozen hashes. If no trusted baseline exists, state that limitation and do not claim historical preservation.
4. Map each acceptance criterion to changed files and validation evidence. Review simplicity, determinism, scope, secrets, and applicable safety/import/data-access boundaries. For scientific/quant tasks, read and invoke sibling `scientific-reproducibility-review/SKILL.md` and `quant-code-review/SKILL.md`; incorporate their findings without recursive gate invocation.
5. List `BLOCKER`, `NON-BLOCKING`, and `QUESTION` items. A question that prevents establishing a mandatory criterion remains a blocker. Any mandatory validation failure, missing mandatory check, unauthorized frozen change, or unmet acceptance criterion means `LOCAL GATE: BLOCKED`; do not declare the task complete.
6. When local checks pass, report `LOCAL GATE: PASS` and read/invoke sibling `claude-adversarial-review/SKILL.md` to prepare the actual review packet. If blocked, provide the blocking evidence and optionally a clearly labeled diagnostic packet. Record Claude status as `NOT SENT`, `AWAITING FEEDBACK`, or `ADJUDICATED` truthfully. Local pass and packet preparation are not external approval; enumerate outstanding human/different-model reviews required by the task or Constitution section 16 before merge.

Finish with scope, acceptance results, exact validation outcomes, frozen verification results, unresolved blockers/assumptions, and packet location or copyable packet. Stop at the current task boundary. Skills are instructions, not enforced CI or access controls; do not claim mechanical enforcement unless it exists and was tested.

~~~~


## Complete file: .env.example

~~~~text
# Task 1 has no environment variables or exchange integration.
# Comments and placeholders only; never put credentials in this file.

~~~~


## Complete file: .gitattributes

~~~~text
# Frozen bytes must survive Git add/checkout even when core.autocrlf is enabled.
/FROZEN_HASHES.json -text
/docs/RESEARCH_CONSTITUTION.md -text
/docs/THREAT_MODEL_v1.md -text
/protocols/protocol_v1.yaml -text
/schemas/HASH_CANONICALIZATION_v1.md -text
/schemas/*.schema.json -text
/specs/*_v1.md -text
*.sha256 -text

~~~~


## Complete file: .github/workflows/ci.yml

~~~~text
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - name: Install project and dev tools
        run: python -m pip install -e ".[dev]"
      - run: ruff format --check .
      - run: ruff check .
      - run: mypy src
      - run: python -m pytest
      - run: lint-imports

~~~~


## Complete file: .gitignore

~~~~text
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.import_linter_cache/
.env
.env.*
!.env.example
data/raw/
data/processed/
data/lockbox/
userdata/
*.db
build/
dist/
*.egg-info/

~~~~


## Complete file: .pre-commit-config.yaml

~~~~text
# Preserve every frozen governance file and SHA-256 sidecar byte-for-byte.
# docs/README.md is the expressly authorized, non-frozen documentation addition.
exclude: '^(?:docs/(?!README\.md$)|protocols/|schemas/|specs/|FROZEN_HASHES\.json$)|\.sha256$'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.13
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer

~~~~


## Complete file: AGENTS.md

~~~~text
# Codex collaboration

- Preserve frozen v1.0 artifacts in `docs/`, `protocols/`, `schemas/`, and `specs/`, plus `FROZEN_HASHES.json` and every SHA-256 sidecar. Never casually edit, normalize, regenerate, or update hashes to hide changes. Amendments require the Constitution's formal process; AI cannot author, merge, activate, or self-approve them.
- Before scientific implementation, read `docs/RESEARCH_CONSTITUTION.md`, `protocols/protocol_v1.yaml`, and the applicable frozen specifications. These instructions and skills do not amend governance.
- No secrets in the repository, logs, prompts, artifacts, or tests. No Binance credentials during Milestone 0.1.
- No trading, ML, or LLM implementation before its scheduled task. Do not skip tasks or silently expand scope. Implement only the currently authorized task.
- Prefer simple deterministic implementations. No silent data deletion or correction. `NO_EDGE_FOUND` is a valid scientific result.
- Tests and fixtures use synthetic or exploration data only. Respect confirmation and lockbox access restrictions.
- Every task finishes with applicable tests, lint, type, and import-boundary checks. Record exact commands and results; justify N/A checks. Failed or unavailable mandatory validation blocks completion.
- Invoke `task-gate-review` at every task end, before declaring a major task complete. For scientific/quant tasks also invoke `scientific-reproducibility-review` and `quant-code-review`.
- After local review passes, prepare a `claude-adversarial-review` packet. Claude is an independent adversarial reviewer, not an authority; adjudicate feedback with evidence instead of applying it blindly. Use human relay when no authorized connection exists.
- Architecture, protocol, statistical, safety, or frozen-governance changes from review are proposals, never automatic edits. Follow the applicable owner/human approval process. Constitution section 16 requires different-model and human PR review before merging its enumerated protected components.
- Repository skills live in `.agents/skills/<name>/SKILL.md`. Read the relevant skill before using it; if discovery has not refreshed, open that file directly.
- Consider new external skills only when needed: inspect source, provenance, permissions, dependencies, and relevance first. Prefer OpenAI-maintained skills. Do not install arbitrary third-party skills automatically; stop and report any proposed third-party skill before installation.

~~~~


## Complete file: FROZEN_HASHES.json

~~~~text
{
  "release": "v1.0",
  "status": "FROZEN",
  "constitution_content_hash": "4cb6c7d35e238bdd778e8dd74b25d1b978e57fedffdbfae83b2867b5ec4fb8d7",
  "protocol_file_sha256": "d22efb8989cb31a1d673000bba1e69baf5e0965bb400a8798aa966a3035d8b26",
  "cost_model_sha256": "3f5e62ab2df26f360f3ca13d2db379e95a1e52b25dc3d2c8f2683878b49327ae",
  "feature_factory_sha256": "c8a0ea027de04889ff90ca6a89ad1096a335ee9c368fea8cb138b85dbbe30348",
  "benchmark_set_sha256": "b1baffd321c9adf2482350b35c73b3f436e9dda483d86b2c751e7ddddc606222",
  "backtester_spec_sha256": "a1bee89f6e0d1fe309b5b12317ff277e55a91b96c81174789f4bc4c09503d961",
  "threat_model_sha256": "8817a315b03564e833d6c556da5de07a0740c7d87c9f7820dd8280082e745d4e",
  "hash_canonicalization_spec_sha256": "189e3525c5c63f9605f739386aa3edc16b7bf44b5f4f7196dd7f698c9fbdc3cf"
}

~~~~


## Complete file: FROZEN_HASHES.json.sha256

~~~~text
962bdb5096ae191556933cdde940d34f1548261f2ee9a7be65b523208b26912d  FROZEN_HASHES.json

~~~~


## Complete file: README.md

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
Run the same checks as CI:

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

The existing local Task 1 environment uses portable Python 3.12.10. To use it
from PowerShell without changing system Python settings:

```powershell
$env:PATH = "$PWD\.venv;$PWD\.venv\Scripts;$env:PATH"
python -m pytest
```

This portable environment has no activation script or standard-library venv
module. The fresh-install steps above assume a full Python installation.

~~~~


## Complete file: SECURITY.md

~~~~text
# Security

- Never commit exchange credentials.
- Never place secrets in logs, artifacts, or LLM context.
- Production exchange credentials belong only to the executor identity.
- Withdrawals must remain disabled.
- Cycle 1 contains no live exchange integration; Task 1 does not trade.

~~~~


## Complete file: configs/.gitkeep

~~~~text

~~~~


## Complete file: docs/README.md

~~~~text
# Frozen governance

The v1.0 governance artifacts in docs/, protocols/, schemas/, and specs/,
FROZEN_HASHES.json, and their SHA-256 sidecars are frozen for Cycle C1.
They may not be edited except through the formal process in the
[Research Constitution](RESEARCH_CONSTITUTION.md), sections 3, 4, and 27.
AI cannot author, merge, activate, or self-approve amendments.
This README is explanatory documentation, not a governance amendment.

~~~~


## Complete file: docs/RESEARCH_CONSTITUTION.md

~~~~text
# RESEARCH_CONSTITUTION.md
## autonomous-quant-trader — Research Constitution v1.0

**Status:** FROZEN  
**Effective date:** 2026-09-11  
**Hash canonicalization spec:** `schemas/HASH_CANONICALIZATION_v1.md`  
**Hash canonicalization spec SHA-256:** `189e3525c5c63f9605f739386aa3edc16b7bf44b5f4f7196dd7f698c9fbdc3cf`  
**Content hash:** `4cb6c7d35e238bdd778e8dd74b25d1b978e57fedffdbfae83b2867b5ec4fb8d7`

## §0 Definitions
Cycle = bounded period governed by one immutable protocol hash.  
Family = named hypothesis class with current-cycle and lifetime trial accounting.  
Trial = registered evaluation counted when evaluation begins.  
Hypothesis = immutable preregistered claim with hash/lineage.  
Candidate = hypothesis/model passing non-lockbox eligibility.  
Benchmark = fixed comparison strategy.  
Deployable baseline = exactly one protocol-designated benchmark eligible for the NO_EDGE_FOUND path.  
Exploration partition = data available for free-form biased exploration.  
Confirmation partition = data available only through the registered experiment engine.  
Lockbox = future data readable only by lockbox_eval.  
Promotion = eligibility → lockbox → signed attestation.  
Incident = HALT, reconciliation mismatch, unexplained exposure, ambiguous order, credential anomaly, or comparable safety event.

## §1 Purpose
Build a scientifically defensible, reproducible, cost-aware, risk-controlled crypto spot exposure platform.

**NO EDGE FOUND is acceptable.**

Passing validation means only failure to falsify under the tests actually run.

Success criteria may not be redefined after results; §§5 and 13 enforce this.

## §2 Scope
Binance Spot; BTC/USDT and ETH/USDT initially; exposure per asset in [0,1]; no shorting, margin, futures, leverage, withdrawals, RL, deep learning without a later Constitution-compliant amendment, autonomous production promotion, or LLM in the live decision path.

BTC+ETH agreement is a sanity check, not independent replication.

Known incompletely modelable risks include custody/insolvency, stablecoin depeg, venue/regulatory action, account-access loss, rule changes, and extreme discontinuities.

## §3 Governance
Constitution → Schemas/Threat Model → Cycle Protocol → Hypothesis → Experiment → Artifacts.

This binds owner, humans, AIs, and software.

Scientific/safety-relevant schema or threat-model changes during a cycle follow the protocol-change rule and end that cycle.

## §4 Amendment rule
Amendment requires version bump, written rationale, owner-of-record signed/dated commit, cycle termination, pre-new-cycle activation, preserved history, and no retroactive effect on open promotions.

Research/coding AI may propose but not author/merge/activate/self-approve amendments.

No protocol may set capital-increase cooling-off, risk-loosening cooling-off, or safety-amendment activation delay below **72 hours**.

`owner_change_control` is governed by this Constitution, not ordinary protocol editing.

Safety-clause amendments cannot be proposed/activated during an open incident or post-HALT cooling-off.

## §5 Cycle rule
One frozen protocol hash per cycle.

Every cycle protocol must define family-budget exhaustion, calendar/time limit, and candidate-promotion termination. Otherwise invalid.

Outcomes: `CANDIDATE_PROMOTED`, `NO_EDGE_FOUND`, `PROTOCOL_REVISION`, `INVALIDATED`.

Invalidation voids scientific results but not lockbox exposure or lifetime trial counts.

Prior-cycle results are not pooled into later DSR/PBO matrices; lifetime trial counts persist.

## §6 Data invariants
Raw immutable; no silent deletion/correction; outages untradeable; full hash lineage; causal time semantics; no future leakage; features versioned; point-in-time fees/filters/status where available; UTC only; one tested bar-semantics module.

## §7 Lockbox
Only lockbox_eval reads it.

Research/coding environments receive no raw lockbox data or full diagnostics.

Access requires ELIGIBLE; every read consumes budget, logs, creates evaluation ID, and marks segment EXPOSED.

Research receives PASS/FAIL only.

Exposed segments never re-lock and roll forward only into **confirmation**. Lockbox boundary only moves forward.

Exploration/confirmation boundary changes only between cycles and only forward.

After LOCKBOX_FAIL, descendants cannot request another lockbox read in that cycle.

## §7a Exploration/confirmation
Sandbox mounts exploration only.

Confirmation is accessible only through the registered experiment engine.

Sandbox receives only metrics.json, 3-month fold aggregates, and report.md from confirmation.

Per-bar confirmation returns/equity/trades remain under experiment-engine identity.

## §8 Hypotheses
Immutable after preregistration. Required fields include ID/hash/family/creator/target/horizon/bar+decision frequency/feature hash/exposure mapping/rebalance rule including band+min hold/cost hash/training rule/retrain hash/grid/protocol hash/parent lineage.

Hashes follow §27 canonicalization.

## §9 Trials
Count when evaluation begins; aborted evaluated runs count.

All failures count. Lifetime family accounting persists.

If no frozen effective-count method exists, raw count is used.

Exploration is not a registered trial because it is confined to exploration data.

## §10 Benchmarks
Fixed, hashed, untuned, and evaluated under identical bar semantics, comparison benchmark, cost model, execution baseline, and applicable band/min-hold rules.

## §11 NO_EDGE baseline
Exactly one deployable baseline named before cycle. Changing it ends cycle.

Exempt only from beating itself; all live-safety, paper, reconciliation, canary, owner, and cooling-off gates still apply.

## §12 Vol-managed constraint
Spot max exposure 100% means vol management is **de-risking, not alpha**. It may lag B&H in bull markets and this alone is not grounds for override.

## §13 Promotion
`eligibility_gate → lockbox_request → promotion_attestation`.

Attestation binds constitution/protocol/hypothesis/benchmark/cost/feature/data-manifest/backtester hashes, eligibility ID, lockbox ID, and cooling-off start.

Human decision: `APPROVE_AS_IS` or `REJECT` only.

## §14 Owner clauses
Risk increases require formal review/cooling-off.

Risk reductions are immediate: reduce capital, tighten limits, kill, HALT, FREEZE.

HALT override requires: written incident record, identified or bounded cause, successful reconciliation, explicit owner action, and timestamp.

Trading resumes only after incident closure plus successful reconciliation.

## §15 Research AI
Exploration only; aggregate confirmation artifacts only; no direct confirmation/lockbox; no protected-code writes; no credentials/live access; Cycle-1 network denied.

## §16 Coding AI
Untrusted.

Backtester order: human spec review → oracle tests → leakage canaries → NumPy reference → production implementation.

Accepted oracle/canary tests are frozen; changes require human rationale/review.

The following **enumerated components** require different-model + human PR review before merge:
- validation engine
- promotion gate
- governor
- executor state machine
- lockbox ACL tooling
- protocol-enforcement logic

Tests/fixtures use only synthetic or exploration data.

## §17 Import boundaries
CI enforces: research !→ governor/execution/lockbox_eval; governor !→ execution/model-training; execution !→ research/model-training; live !→ AI-agent code.

## §18 Backtester trust
Must pass analytic identities, zero exposure, known turnover, cost monotonicity, future-feature canary, lagged-feature canary, shuffled-label null, NumPy reference, deterministic rerun.

Any backtester change creates a new hash and reruns the suite.

## §19 Live path
predictor → governor → executor → exchange.

Alerting before shadow. Startup reconciliation required. Config/hash mismatch → REFUSE_START.

Separate deployment protocol required before shadow.

## §20 Governor
Authorization binds bounded state transition: proposal hash, current-state reference, symbol, target/qty bounds, max slippage, expiry, nonce. Re-evaluate from actual fills.

## §21 Ambiguous orders
Timeout → query clientOrderId. NOT_FOUND → wait protocol delay → query again. Confirmed absence may resend only with same clientOrderId and unexpired authorization; otherwise get new authorization. UNKNOWN → reconcile/FREEZE.

## §22 HALT/FLATTEN/FREEZE
HALT adds no risk. FLATTEN is bounded de-risking. FREEZE makes no autonomous risk change. State transitions logged; exit FREEZE only after reconciliation.

## §23 Reporting honesty
Every report states raw decisions, overlap factor, ESS+method, trial counts, comparison benchmark, costs, protocol hash, and confirmation-period limitations. Bar count is never sample size.

## §24 Required before Task 1
Constitution, research protocol, protocol/hypothesis/experiment/metrics/attestation schemas, threat model, backtester spec, cost-model spec.

## §25 Owner acknowledgment
Owner signs/date before first equity curve: NO_EDGE acceptable; BTC/ETH not independent replication; de-risking may lag B&H; no risk-increase bypass; no HALT override without incident process; AI advisory only; total deployed allocation can be lost via risks no backtest captures; only fully-loss-acceptable capital may be deployed; owner read §§12/14.

## §26 Audit logs
Registry, trials, lockbox logs, attestations, incidents, cycle outcomes are append-only/tamper-evident.

## §27 Reproducibility/hash canonicalization
Promotion-relevant artifacts must reproduce from recorded hashes/seeds or are void.

Self-referential hashes are computed with that hash value blanked/removed according to `HASH_CANONICALIZATION_v1.md`, whose sidecar hash is itself recorded.

## §28 Secrets
No secrets in repo/artifacts/logs/reports/screenshots/LLM context/CI. Production keys only under executor identity. Rotation/revocation rehearsal and permission/IP checks required before canary; withdrawals disabled.

~~~~


## Complete file: docs/RESEARCH_CONSTITUTION.md.sha256

~~~~text
776396a25012276f22c4d7478166614e2f4f58e1a866e274ff8437e60cc09516  RESEARCH_CONSTITUTION.md

~~~~


## Complete file: docs/THREAT_MODEL_v1.md

~~~~text
# THREAT_MODEL_v1.md

Actors: owner, research AI, coding AI, research user, experiment-engine identity,
lockbox_eval identity, predictor, governor, executor, watchdog/alerter, exchange.

Core permissions:
- Research AI/coding AI: exploration only; no direct confirmation/lockbox.
- Experiment engine: may evaluate confirmation after registered hypothesis verification.
- lockbox_eval: lockbox read + attestation signing only; no exchange credentials.
- Predictor: approved live inputs/model, no exchange key.
- Governor: proposal/account/market state + signing key, no exchange key.
- Executor: only holder of exchange trading key; no research/lockbox access.
- Owner: approvals/change-control, but no default raw lockbox access.

Core threats:
- preregistration bypass by exploration on confirmation,
- repeated lockbox probing,
- coding agent weakening tests/referee,
- owner risk escalation during drawdown,
- duplicate order after ambiguous timeout,
- credential leakage,
- stale/mismatched deployed config,
- exchange/custody/stablecoin failure.

Controls are defined by the Constitution and protocols; this document does not weaken them.

~~~~


## Complete file: docs/THREAT_MODEL_v1.md.sha256

~~~~text
8817a315b03564e833d6c556da5de07a0740c7d87c9f7820dd8280082e745d4e  THREAT_MODEL_v1.md

~~~~


## Complete file: experiments/.gitkeep

~~~~text

~~~~


## Complete file: protocols/protocol_v1.yaml

~~~~text
protocol_version: "1.0"
cycle_id: "C1"
status: "FROZEN"
constitution_version: "1.0"
constitution_hash: "4cb6c7d35e238bdd778e8dd74b25d1b978e57fedffdbfae83b2867b5ec4fb8d7"
hash_canonicalization_spec_hash: "189e3525c5c63f9605f739386aa3edc16b7bf44b5f4f7196dd7f698c9fbdc3cf"
feature_factory_hash: "c8a0ea027de04889ff90ca6a89ad1096a335ee9c368fea8cb138b85dbbe30348"
benchmark_set_hash: "b1baffd321c9adf2482350b35c73b3f436e9dda483d86b2c751e7ddddc606222"
cost_model_hash: "3f5e62ab2df26f360f3ca13d2db379e95a1e52b25dc3d2c8f2683878b49327ae"
backtester_spec_hash: "a1bee89f6e0d1fe309b5b12317ff277e55a91b96c81174789f4bc4c09503d961"
threat_model_hash: "8817a315b03564e833d6c556da5de07a0740c7d87c9f7820dd8280082e745d4e"

cycle_start_bindings:
  data_manifest_hash:
    value: "BOUND_IN_CYCLE_RECORD_BEFORE_FIRST_TRIAL"
    justification: "Data cannot be hashed before ingestion, so the cycle record binds it before any trial begins."
  backtester_code_hash:
    value: "BOUND_IN_CYCLE_RECORD_BEFORE_FIRST_TRIAL"
    justification: "Implementation does not exist at protocol freeze; no trial may run until an accepted backtester hash is bound."
  no_trial_before_bindings_complete:
    value: true
    justification: "Prevents protocol-frozen research from running on unbound data or engine code."

comparison:
  promotion_benchmark:
    value: "VOL_TARGET_BUY_AND_HOLD"
    justification: "One predeclared comparator is used for every eligibility, robustness, DSR/PBO, null, and lockbox comparison."
  other_benchmarks_eligibility_role:
    value: "report_only"
    justification: "Prevents choosing the most flattering comparator after results."

asset_evaluation:
  primary_asset:
    value: "BTCUSDT"
    justification: "All formal eligibility statistics use one predeclared primary series."
  sanity_asset:
    value: "ETHUSDT"
    justification: "ETH is a correlated sanity check, not independent replication."
  btc_gate:
    value: "full_eligibility_and_lockbox_rules"
    justification: "Defines the single formal gate series."
  eth_gate:
    value: "paired_delta_sharpe_point_estimate_gt_0_AND_drawdown_constraint_holds_at_1x_cost"
    justification: "Requires directional consistency without pretending ETH is an independent second test."
  combined_portfolio_gate:
    value: false
    justification: "Avoids introducing an undeclared allocation problem."

scope:
  exchange: {value: "Binance", justification: "Single venue limits semantic/operational variance."}
  market: {value: "spot", justification: "Avoids leverage/funding/liquidation complexity."}
  symbols: {value: ["BTCUSDT","ETHUSDT"], justification: "Initial liquid pair; formal roles defined above."}
  bar_interval: {value: "1h", justification: "Causal feature resolution without 15m noise/trial inflation."}
  scheduled_decision_anchor_utc: {value: "00:00", justification: "Fixes intraday timing before results."}
  hourly_signal_evaluation: {value: true, justification: "Allows intraday risk-reduction monitoring."}
  risk_increase_rule:
    value: "only_at_00_00_UTC_and_only_if_24h_since_last_risk_increase"
    justification: "Makes risk increases scheduled and bounded."
  intraday_action_rule:
    value: "only_reduce_exposure_if_target_is_at_least_0.10_below_current"
    justification: "Band-triggered intraday actions are safety-direction only."
  max_exposure_per_asset: {value: 1.0, justification: "Long-only unlevered spot."}

partitions:
  exploration: {start: "2017-08-17T00:00:00Z", end: "2021-12-31T23:59:59Z"}
  confirmation: {start: "2022-01-01T00:00:00Z", end: "2025-05-31T23:59:59Z"}
  lockbox: {start: "2025-06-01T00:00:00Z", end: "2026-08-31T23:59:59Z"}
  exploration_may_enter_training_folds: true
  sandbox_exploration_policy:
    value: "all jobs logged; human review triggered after 250 jobs"
    justification: "Partition boundary is the control; high exploratory volume triggers governance review."

lockbox_policy:
  max_evaluations_per_family_per_cycle: {value: 2, justification: "One primary and one replacement candidate."}
  cooldown_days: {value: 30, justification: "Prevents rapid re-probing."}
  result_to_research: {value: "PASS_FAIL_ONLY", justification: "Prevents tuning feedback."}
  attestation_coarse_fields:
    value: ["paired_delta_sharpe_sign","drawdown_constraint_held","prediction_decay_test_passed"]
    justification: "Enumerated fields prevent diagnostic drift."
  cost_multiplier:
    value: 1.0
    justification: "Lockbox tests consistency of the validated baseline-cost prediction; cost fragility was already gated at 2x pre-lockbox."
  prediction_interval:
    construction:
      value: "stationary bootstrap the confirmation BTC paired-difference series using Politis-White blocks; generate synthetic paths with decision-count equal to the lockbox BTC decision-count; compute delta-Sharpe per path"
      justification: "Produces a prediction distribution for a lockbox-length realization rather than a CI on the confirmation mean."
    tail:
      value: "one_sided_lower_5_percentile"
      justification: "Unexpected underperformance fails; upside exceedance is logged but does not fail."
  pass_rule:
    value: "BTC passes iff lockbox delta-Sharpe >= 5th percentile of confirmation-derived lockbox-length prediction distribution AND BTC delta-Sharpe > 0 AND BTC drawdown constraint holds; ETH sanity gate must also pass"
    justification: "Tests consistency and direction without pretending 15 months is a fresh high-power significance sample."
  net_return_tolerance_rule:
    value: "REMOVED"
    justification: "A de-risker may legitimately trail on absolute return while improving risk-adjusted behavior."
  exposed_segments_release_to: {value: "confirmation", justification: "Exposed data never returns to free exploration."}

feature_factory:
  hash: "c8a0ea027de04889ff90ca6a89ad1096a335ee9c368fea8cb138b85dbbe30348"
  frozen: true

target:
  formula:
    value: "log(P[t+H]/P[t]) / (sigma_hourly_t * sqrt(H_hours))"
    justification: "Comparable scale across declared horizons."
  normalization_vol:
    value: "EWMA hourly vol, 168h half-life"
    justification: "Fixed label normalization across all families."
  horizons_hours: [24,72,168]

exposure_mapping:
  rebalance_band_absolute: 0.10
  minimum_holding_hours_for_risk_increase: 24
  default_sizing_vol_estimator:
    value: "EWMA_168h"
    justification: "Used by trend family and canonical baseline."
  volatility_family_sizing_estimator_rule:
    value: "may declare a preregistered alternative estimator as part of hypothesis content and parameter_point"
    justification: "Allows HAR/GARCH/alternate EWMA to be tested without changing target normalization."
  allowed_volatility_family_estimators:
    value: ["EWMA_72h","EWMA_168h","EWMA_336h","HAR_RV","GARCH_1_1"]
    justification: "Predeclared bounded categorical estimator set."
  sizing_estimator_dimension_type:
    value: "categorical_structural"
    justification: "Estimator classes have no meaningful +/-1 ordering; they count as trials but are excluded from numeric boundary rules."
  vol_target_trial_dimension:
    value: [0.40,0.60,0.80]
    justification: "Small explicit annualized sizing grid."
  canonical_baseline_vol_target: 0.60

benchmarks:
  deployable_baseline: "VOL_TARGET_BUY_AND_HOLD"
  benchmark_set_hash: "b1baffd321c9adf2482350b35c73b3f436e9dda483d86b2c751e7ddddc606222"
  null_models:
    random_exposure:
      construction:
        value: "match candidate mean exposure and turnover on BTC; evaluate paired delta-Sharpe versus VOL_TARGET_BUY_AND_HOLD"
        justification: "Removes beta/time-in-market advantage from the trading null."
      samples: 500
      gate_metric: "paired_delta_sharpe_vs_VOL_TARGET_BUY_AND_HOLD"
    shuffled_labels:
      samples: 500
      gate_metric:
        value: "OOS Spearman IC between model prediction and vol-scaled target"
        justification: "Explicit predictive null metric."

cost_model:
  hash: "3f5e62ab2df26f360f3ca13d2db379e95a1e52b25dc3d2c8f2683878b49327ae"
  baseline_execution: "next_1h_bar_open_plus_frozen_cost_model"
  stress_multipliers: [1.0,1.5,2.0,3.0]


models:
  allowed_classes_cycle_1:
    value: ["linear","ridge","lasso","elastic_net","logistic","lightgbm"]
    justification: "Enforces the agreed low-complexity model progression and excludes undeclared model classes."
  deep_learning_allowed:
    value: false
    justification: "Deep learning requires a future Constitution-compliant amendment."
  logistic_use:
    value: "only_if_sign_objective_is_preregistered"
    justification: "Prevents casual conversion of a magnitude target into classification."
  lightgbm_constraints:
    max_depth:
      value: 3
      justification: "Keeps tree complexity shallow in the small-sample Cycle-1 setting."
    num_leaves_max:
      value: 8
      justification: "Consistent with max_depth<=3 and reduces overfitting capacity."
    learning_rate:
      value: 0.05
      justification: "Conservative fixed learning rate; not a free post-hoc knob."
    n_estimators_max:
      value: 300
      justification: "Bounds boosting capacity; any exact estimator count is preregistered inside the hypothesis grid."

trial_accounting:
  trial_unit:
    value: "(hypothesis_id, parameter_point, horizon); BTC and ETH evaluated jointly inside the same trial"
    justification: "ETH sanity does not double trial count."
  parameter_point_includes:
    value: ["vol_target","model_or_estimator_parameters"]
    justification: "Makes trial arithmetic explicit."
  trend_budget:
    value: 81
    justification: "Supports up to three 27-trial fully gridded hypotheses (3 model points × 3 vol targets × 3 horizons)."
  volatility_budget:
    value: 81
    justification: "Same bounded capacity for up to three fully gridded volatility hypotheses."
  lifetime_accounting: true

cycle_termination:
  calendar_days_elapsed: 180
  ends_when_any: ["all_family_trial_budgets_exhausted","calendar_days_elapsed","candidate_promoted","protocol_revision","cycle_invalidated"]
  outcomes: ["CANDIDATE_PROMOTED","NO_EDGE_FOUND","PROTOCOL_REVISION","INVALIDATED"]

validation:
  training_window_months: 24
  walk_forward_step_days: 30
  retrain_cadence_days: 30
  reporting_fold_months: 3
  final_partial_reporting_block:
    value: "excluded_from_paired_fold_win_rate_but_reported_separately"
    justification: "Avoids changing the denominator with a shorter fold."
  purge_rule: "label_horizon"
  embargo:
    rule: "max(label_horizon,target_autocorr_cutoff)"
    target_acf_sampling_frequency:
      value: "daily_decision_frequency"
      justification: "Avoids overstating dependence using overlapping hourly labels."
    estimator: "ACF_with_Bartlett_bands"
    alpha: 0.05
    max_lag: "4 * horizon_in_daily_steps"
    cutoff: "first lag after which no remaining lag is significant"
  cpcv:
    enabled_if_effective_decisions_gte: 250
    groups: 8
    test_groups: 2
    role:
      value: "diagnostic_only"
      justification: "Report median and 5th-percentile path paired-delta-Sharpe; no independent promotion gate."
    training_rule: "all non-test groups with purge and embargo; 24-month rolling window applies to walk-forward only"
  bootstrap:
    type: "stationary_block"
    block_method: "politis_white"
    iterations: 2000
  dsr:
    series:
      value: "BTC candidate_minus_VOL_TARGET_BUY_AND_HOLD paired OOS return series"
      justification: "Measures incremental evidence rather than BTC beta."
    minimum: 0.95
    effective_trial_count_method: "eigenvalue_effective_number_from_trial_return_correlation_matrix"
    fallback: "raw_trial_count"
  pbo:
    enabled_if_family_trials_gte: 20
    partitions: 16
    series_matrix:
      value: "family trial paired-difference return matrix versus VOL_TARGET_BUY_AND_HOLD"
      justification: "Keeps PBO on the same incremental objective as DSR."
    ranking_metric: "paired_delta_sharpe"
    maximum: 0.30
  effective_decisions:
    method: "newey_west_autocorrelation_adjusted_ESS_on_BTC_OOS_strategy_returns"
    fallback: "raw_decisions / ceil(horizon_hours/24)"
  oos_is_ratio:
    in_sample_definition:
      value: "training-window Sharpe of the same fixed configuration on the paired-difference series"
      justification: "Avoids mixing absolute beta Sharpe with incremental OOS evidence."
    note_for_rule_based_no_fit_models: "gate_is_reported_as_not_applicable"
  configuration_selection:
    value: "each grid point is one fixed trial; no per-fold reselection; submitted candidate is one grid point; family DSR/PBO/plateau account for selection"
    justification: "Removes hidden nested/post-hoc ambiguity."
  plateau:
    tunable_dimensions:
      value: "model_or_estimator_parameters_only"
      justification: "Structural dimensions horizon and vol_target remain counted trials but do not trigger boundary-optimum rejection."
    structural_dimensions:
      value: ["horizon","vol_target","sizing_estimator"]
      justification: "Horizon/vol-target are bounded by design and estimator class is categorical; all count as trials but do not trigger numeric boundary rejection."
    neighbor_inclusion:
      value: "available +/-1-step neighbors are used only for ordered numeric dimensions; categorical sizing_estimator is excluded from neighbor arithmetic; the three EWMA half-lives may be treated as ordered numeric neighbors only within the EWMA subclass"
      justification: "Avoids inventing distance between HAR, GARCH, and EWMA while preserving local checks where an ordering exists."
    pass_rule:
      value: "if no ordered numeric tunable dimensions: N/A; otherwise median available-neighbor BTC OOS paired-delta-Sharpe >= 0.5 * selected-point value AND selected point is not on a boundary of any ordered numeric tunable dimension"
      justification: "Rejects isolated numeric peaks without arbitrarily penalizing categorical estimator choices."
  random_seed_policy: "SHA256(protocol_hash,hypothesis_hash,trial_index) -> deterministic seed"
  feature_delay_stress_bars: 1
  execution_delay_stress_bars: 1

promotion:
  comparison_benchmark: "VOL_TARGET_BUY_AND_HOLD"
  primary_asset: "BTCUSDT"
  sanity_asset: "ETHUSDT"
  paired_confidence_interval: "two_sided_90_percent"
  btc_min_sharpe_delta_ci_lower_bound: 0.0
  btc_drawdown_constraint:
    value: "confirmation OOS max drawdown point estimate no worse than benchmark by >0.05"
    justification: "MDD is a robustness constraint, not primary bootstrap inference."
  eth_sanity_rule: "paired_delta_sharpe_point_estimate > 0 AND drawdown_constraint_holds_at_1x_cost"
  paired_fold_win_rate:
    minimum: 0.60
    unit: "complete_3_month_reporting_blocks"
  survive_2x_cost_rule: "BTC paired_delta_sharpe_point_estimate > 0 AND BTC candidate_net_return > 0 AND BTC drawdown_constraint_holds; ETH sanity rule also holds"
  feature_delay_hard_gate: true
  execution_delay_hard_gate: true
  parameter_plateau_required: true
  dsr_minimum: 0.95
  pbo_maximum_if_enabled: 0.30
  null_minimum_percentile: 0.95
  minimum_effective_decisions: 120
  benchmark_hash_must_match: true
  trial_budget_hard_stop: true

lockbox_request:
  allowed_only_after_eligibility: true
  descendant_retry_same_cycle_after_fail: false

promotion_attestation:
  human_decisions: ["APPROVE_AS_IS","REJECT"]
  cooling_off_hours: 72

owner_change_control:
  capital_increase_cooling_off_hours: 72
  risk_loosening_cooling_off_hours: 72
  safety_amendment_activation_delay_hours: 72
  risk_decrease_immediate: true

freeze_sequence:
  value:
    - "freeze Constitution v1.0 and compute canonical content hash"
    - "update protocol constitution_hash"
    - "verify all referenced dependency hashes"
    - "set protocol status to FROZEN"
    - "recompute protocol sidecar hash"
    - "create cycle record"
    - "bind data_manifest_hash and accepted backtester_code_hash before first trial"
  justification: "Makes expected hash changes during freezing explicit."

~~~~


## Complete file: protocols/protocol_v1.yaml.sha256

~~~~text
d22efb8989cb31a1d673000bba1e69baf5e0965bb400a8798aa966a3035d8b26  protocol_v1.yaml

~~~~


## Complete file: pyproject.toml

~~~~text
[build-system]
requires = ["hatchling>=1.27,<2"]
build-backend = "hatchling.build"

[project]
name = "autonomous-quant-trader"
version = "0.1.0"
description = "Governed crypto spot research infrastructure"
readme = "README.md"
requires-python = ">=3.12"
dependencies = ["pydantic>=2.10,<3", "pydantic-settings>=2.7,<3"]

[project.optional-dependencies]
dev = [
    "pytest>=8.3,<9",
    "ruff==0.11.13",
    "mypy>=1.15,<2",
    "import-linter>=2.3,<3",
    "pre-commit>=4.2,<5",
]

[tool.hatch.build.targets.wheel]
packages = ["src/aqt"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--strict-config --strict-markers"

[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]

[tool.mypy]
python_version = "3.12"
strict = true

[tool.importlinter]
root_package = "aqt"

[[tool.importlinter.contracts]]
name = "Research cannot reach protected runtime or lockbox packages"
type = "forbidden"
source_modules = ["aqt.research"]
forbidden_modules = ["aqt.governor", "aqt.execution", "aqt.lockbox_eval"]
allow_indirect_imports = false

[[tool.importlinter.contracts]]
name = "Governor cannot reach execution or model training"
type = "forbidden"
source_modules = ["aqt.governor"]
forbidden_modules = ["aqt.execution", "aqt.models"]
allow_indirect_imports = false

[[tool.importlinter.contracts]]
name = "Execution cannot reach model training"
type = "forbidden"
source_modules = ["aqt.execution"]
forbidden_modules = ["aqt.models"]
allow_indirect_imports = false

[[tool.importlinter.contracts]]
name = "Live packages cannot reach research agent code"
type = "forbidden"
source_modules = ["aqt.allocation", "aqt.governor", "aqt.execution", "aqt.monitoring"]
forbidden_modules = ["aqt.research"]
allow_indirect_imports = false

~~~~


## Complete file: schemas/HASH_CANONICALIZATION_v1.md

~~~~text
# HASH_CANONICALIZATION_v1.md

Canonicalization rules:
1. UTF-8, LF line endings.
2. For YAML/JSON, parse then recursively sort mapping keys; preserve list order.
3. Remove the self-referential hash field (or set it to the empty string) before hashing.
4. Serialize structured objects as compact JSON with ensure_ascii=false and separators ',' ':'.
5. For Markdown self-hash fields, replace only the hash value with the empty string before hashing.
6. SHA-256 the resulting bytes.
7. This file is sidecar-hashed; its own hash is not embedded in itself.

~~~~


## Complete file: schemas/HASH_CANONICALIZATION_v1.md.sha256

~~~~text
189e3525c5c63f9605f739386aa3edc16b7bf44b5f4f7196dd7f698c9fbdc3cf  HASH_CANONICALIZATION_v1.md

~~~~


## Complete file: schemas/attestation.schema.json

~~~~text
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "constitution_hash",
    "protocol_hash",
    "hypothesis_hash",
    "benchmark_set_hash",
    "cost_model_hash",
    "feature_set_hash",
    "data_manifest_hash",
    "backtester_hash",
    "eligibility_result_id",
    "lockbox_evaluation_id",
    "cooling_off_start",
    "signature"
  ]
}

~~~~


## Complete file: schemas/attestation.schema.json.sha256

~~~~text
43e975bfe3a621371afd475ae6c8a53566e096b07cac45b3312a0ffe0ab9c2fa  attestation.schema.json

~~~~


## Complete file: schemas/experiment.schema.json

~~~~text
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "experiment_id",
    "hypothesis_hash",
    "protocol_hash",
    "protocol_status",
    "trial_index",
    "seed",
    "backtester_hash",
    "data_manifest_hash"
  ],
  "properties": {
    "experiment_id": {
      "type": "string"
    },
    "hypothesis_hash": {
      "type": "string"
    },
    "protocol_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "protocol_status": {
      "const": "FROZEN"
    },
    "trial_index": {
      "type": "integer",
      "minimum": 0
    },
    "seed": {},
    "backtester_hash": {
      "type": "string"
    },
    "data_manifest_hash": {
      "type": "string"
    }
  },
  "additionalProperties": true
}

~~~~


## Complete file: schemas/experiment.schema.json.sha256

~~~~text
46b85f29b029598d18f8c0691044c4a49589049e42c0c605f4c9dbb3c04be91a  experiment.schema.json

~~~~


## Complete file: schemas/hypothesis.schema.json

~~~~text
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "hypothesis_id",
    "content_hash",
    "family",
    "created_by",
    "target_definition",
    "horizon",
    "bar_frequency",
    "decision_frequency",
    "feature_set_hash",
    "exposure_mapping",
    "rebalance_rule",
    "cost_model_hash",
    "training_window",
    "retrain_policy_hash",
    "parameter_grid",
    "protocol_hash"
  ],
  "properties": {
    "hypothesis_id": {
      "type": "string"
    },
    "content_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "family": {
      "type": "string"
    },
    "created_by": {
      "enum": [
        "human",
        "ai"
      ]
    },
    "target_definition": {},
    "horizon": {},
    "bar_frequency": {},
    "decision_frequency": {},
    "feature_set_hash": {
      "type": "string"
    },
    "exposure_mapping": {},
    "rebalance_rule": {},
    "cost_model_hash": {
      "type": "string"
    },
    "training_window": {},
    "retrain_policy_hash": {
      "type": "string"
    },
    "parameter_grid": {},
    "protocol_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "parent_id": {
      "type": [
        "string",
        "null"
      ]
    }
  },
  "allOf": [
    {
      "if": {
        "properties": {
          "hypothesis_id": {
            "pattern": ".+"
          }
        }
      },
      "then": {}
    }
  ],
  "additionalProperties": true
}

~~~~


## Complete file: schemas/hypothesis.schema.json.sha256

~~~~text
e1175e8b934b106d368c67e2b1851d2ccdde7ae69d27b8407fa573715bd4275f  hypothesis.schema.json

~~~~


## Complete file: schemas/metrics.schema.json

~~~~text
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "protocol_hash",
    "benchmark_set_hash",
    "comparison_benchmark",
    "btc",
    "eth",
    "trial_accounting",
    "reproducibility"
  ]
}

~~~~


## Complete file: schemas/metrics.schema.json.sha256

~~~~text
e74d9c84ed717f1be3d099fa75ace52ee939a77486c0bbf775ca16b58ff6da68  metrics.schema.json

~~~~


## Complete file: schemas/protocol.schema.json

~~~~text
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "protocol_version",
    "cycle_id",
    "status",
    "constitution_version",
    "constitution_hash",
    "hash_canonicalization_spec_hash",
    "feature_factory_hash",
    "benchmark_set_hash",
    "cost_model_hash",
    "backtester_spec_hash",
    "threat_model_hash",
    "cycle_start_bindings",
    "comparison",
    "asset_evaluation",
    "scope",
    "partitions",
    "lockbox_policy",
    "feature_factory",
    "target",
    "exposure_mapping",
    "benchmarks",
    "cost_model",
    "models",
    "trial_accounting",
    "cycle_termination",
    "validation",
    "promotion",
    "lockbox_request",
    "promotion_attestation",
    "owner_change_control",
    "freeze_sequence"
  ],
  "properties": {
    "protocol_version": {
      "type": "string"
    },
    "cycle_id": {
      "type": "string"
    },
    "status": {
      "const": "FROZEN"
    },
    "constitution_version": {
      "type": "string"
    },
    "constitution_hash": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "cycle_start_bindings": {
      "type": "object"
    },
    "comparison": {
      "type": "object"
    },
    "asset_evaluation": {
      "type": "object"
    },
    "benchmarks": {
      "type": "object",
      "required": [
        "deployable_baseline",
        "benchmark_set_hash",
        "null_models"
      ]
    },
    "cost_model": {
      "type": "object",
      "required": [
        "hash",
        "baseline_execution",
        "stress_multipliers"
      ]
    },
    "feature_factory": {
      "type": "object",
      "required": [
        "hash",
        "frozen"
      ]
    },
    "models": {
      "type": "object",
      "required": [
        "allowed_classes_cycle_1"
      ]
    },
    "cycle_termination": {
      "type": "object",
      "required": [
        "calendar_days_elapsed",
        "ends_when_any",
        "outcomes"
      ]
    }
  },
  "additionalProperties": true
}

~~~~


## Complete file: schemas/protocol.schema.json.sha256

~~~~text
45eff36c324d18c1efda48f32e440d1a1b2a9bc5d4a2cf4e7db370973350134e  protocol.schema.json

~~~~


## Complete file: scripts/.gitkeep

~~~~text

~~~~


## Complete file: specs/BACKTESTER_SPEC_v1.md

~~~~text
# BACKTESTER_SPEC_v1.md

Status: pre-implementation specification.

1. Input is a timestamped target-exposure path plus prices and frozen cost-model inputs.
2. Bar semantics: decision at close(t); baseline execution at open(t+1).
3. Exposure changes are clipped to [0,1].
4. Costs are charged on absolute change in exposure using COST_MODEL_v1.
5. Risk increases occur only at the scheduled 00:00 UTC decision and are subject to the 24h minimum-hold rule.
6. Intraday hourly actions are allowed only for exposure reductions when the 10pp band is crossed.
7. No partial fills or passive limits in backtester v0.
8. PnL is computed from actual simulated exposure after execution, never intended exposure.

Pre-existing acceptance tests:
- zero exposure => zero trading PnL,
- buy-and-hold analytic identity,
- known alternating exposure => exact turnover/cost,
- higher cost never improves identical-path net PnL,
- future-return leakage canary produces absurd performance,
- causally lagged version does not,
- shuffled-label OOS null centered near zero,
- NumPy reference implementation matches within tolerance,
- deterministic rerun produces identical canonical metrics.

Oracle/canary tests are frozen after human acceptance.

~~~~


## Complete file: specs/BACKTESTER_SPEC_v1.md.sha256

~~~~text
a1bee89f6e0d1fe309b5b12317ff277e55a91b96c81174789f4bc4c09503d961  BACKTESTER_SPEC_v1.md

~~~~


## Complete file: specs/CANONICAL_BENCHMARKS_v1.md

~~~~text
# CANONICAL_BENCHMARKS_v1.md

Status: Cycle-1 canonical benchmark specification.

Shared rules for candidate-comparable benchmarks:
- 1h bars.
- Same bar-semantics module as candidates.
- Same cost model and baseline execution assumption as candidates.
- Same scheduled 00:00 UTC evaluation.
- Same 10 percentage-point rebalance band where relevant.
- Risk increases respect the 24h minimum-holding rule.
- Intraday band-triggered actions are allowed only to reduce exposure.

## CASH
Exposure = 0.

## BUY_AND_HOLD
Enter 100% exposure at the first eligible execution and hold.

## VOL_TARGET_BUY_AND_HOLD
- Volatility estimator: EWMA of hourly log returns.
- EWMA half-life: 168 hours.
- Annualization factor: sqrt(8760).
- Annualized volatility target: 0.60.
- Target exposure = clip(0.60 / annualized_forecast_vol, 0, 1).
- Rebalance under the shared scheduling/band/min-hold rules.

## CANONICAL_TREND
- Trend signal: close > 200-day simple moving average.
- Exposure target: 1 if true, else 0.
- Rebalance under the shared scheduling/band/min-hold rules.

## CANONICAL_TSMOM
- Momentum signal: trailing 180-day log return > 0.
- Exposure target: 1 if true, else 0.
- Rebalance under the shared scheduling/band/min-hold rules.

These parameters are fixed and not tunable in Cycle 1.

~~~~


## Complete file: specs/CANONICAL_BENCHMARKS_v1.md.sha256

~~~~text
b1baffd321c9adf2482350b35c73b3f436e9dda483d86b2c751e7ddddc606222  CANONICAL_BENCHMARKS_v1.md

~~~~


## Complete file: specs/COST_MODEL_v1.md

~~~~text
# COST_MODEL_v1.md

Status: Cycle-1 frozen cost-model specification.

## Baseline execution
Decision timestamp = eligible 1h bar close.
Baseline fill price = next 1h bar open, then costs are applied.

## Order style
Taker-like only.

## Fee
- Use point-in-time Binance spot taker fee where a reliable historical schedule is available.
- Fallback taker fee when unavailable: 10 basis points per traded notional, per side.

## Spread allowance
- Fixed allowance: 2 basis points per traded notional, per side.

## Slippage
Let `sigma_hourly_bps` be trailing EWMA hourly volatility expressed in basis points.
- EWMA half-life: 168 hours.
- Initialization: for the first 168 available hourly returns, use the simple sample standard deviation of available returns; from bar 169 onward use the recursive EWMA initialized from the simple sample standard deviation of the first 168 returns.
Per-side slippage in basis points:

`slippage_bps = min(15.0, max(1.0, 0.05 * sigma_hourly_bps))`

Properties:
- non-negative,
- monotone in volatility,
- floor 1 bp,
- cap 15 bps.

## Total modeled per-side cost
`fee_bps + spread_bps + slippage_bps`

## Stress
1.0x, 1.5x, 2.0x, 3.0x multiply total modeled trading cost.

## Delay stress
Shift the baseline fill by one additional 1h bar, then apply the same cost model.

No passive-limit assumptions in Cycle 1.

~~~~


## Complete file: specs/COST_MODEL_v1.md.sha256

~~~~text
3f5e62ab2df26f360f3ca13d2db379e95a1e52b25dc3d2c8f2683878b49327ae  COST_MODEL_v1.md

~~~~


## Complete file: specs/FEATURE_FACTORY_v1.md

~~~~text
# FEATURE_FACTORY_v1.md

Status: Cycle-1 frozen feature definitions.

All features are causal and computed only from data available at the decision timestamp.

## Returns
- `ret_1h = log(close_t / close_t-1)`
- `ret_24h = log(close_t / close_t-24)`
- `ret_72h = log(close_t / close_t-72)`
- `ret_168h = log(close_t / close_t-168)`

## Trend
- `ema_24 = EMA(close, span=24)`
- `ema_72 = EMA(close, span=72)`
- `ema_168 = EMA(close, span=168)`
- `ema_dist_24 = close / ema_24 - 1`
- `ema_dist_72 = close / ema_72 - 1`
- `ema_dist_168 = close / ema_168 - 1`
- `sma_4800 = SMA(close, window=4800)`  # 200 days of 1h bars
- `trend_200d = close / sma_4800 - 1`
- `breakout_720 = close / rolling_max(close, 720) - 1`  # 30 days

## Volatility
Hourly log returns are used throughout.
- `rv_24 = std(ret_1h, trailing=24) * sqrt(8760)`
- `rv_168 = std(ret_1h, trailing=168) * sqrt(8760)`
- `rv_720 = std(ret_1h, trailing=720) * sqrt(8760)`
- `ewma_vol_168h = EWMA_std(ret_1h, halflife=168) * sqrt(8760)`
- `atr_24 = ATR(high, low, close, window=24) / close`

No volume-derived alpha, spread, order-book, trade-imbalance, or seasonality features are allowed in Cycle 1.

Any change to a formula or window creates a new feature-factory hash and ends the active cycle.

~~~~


## Complete file: specs/FEATURE_FACTORY_v1.md.sha256

~~~~text
c8a0ea027de04889ff90ca6a89ad1096a335ee9c368fea8cb138b85dbbe30348  FEATURE_FACTORY_v1.md

~~~~


## Complete file: src/aqt/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/allocation/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/backtest/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/benchmarks/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/core/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/core/paths.py

~~~~text
"""Paths for the source checkout; no directory creation or data access."""

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).absolute().parents[3]

~~~~


## Complete file: src/aqt/core/version.py

~~~~text
"""Project version metadata."""

__version__ = "0.1.0"

~~~~


## Complete file: src/aqt/data/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/execution/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/features/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/governor/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/lockbox_eval/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/models/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/monitoring/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/research/__init__.py

~~~~text

~~~~


## Complete file: src/aqt/validation/__init__.py

~~~~text

~~~~


## Complete file: tests/canaries/.gitkeep

~~~~text

~~~~


## Complete file: tests/integration/.gitkeep

~~~~text

~~~~


## Complete file: tests/unit/test_package_imports.py

~~~~text
"""Smoke checks for the foundation; no trading or data fixtures."""

from importlib import import_module

import pytest


@pytest.mark.parametrize(
    "module",
    [
        "aqt",
        "aqt.core",
        "aqt.core.version",
        "aqt.core.paths",
        "aqt.data",
        "aqt.research",
        "aqt.features",
        "aqt.models",
        "aqt.benchmarks",
        "aqt.validation",
        "aqt.backtest",
        "aqt.allocation",
        "aqt.governor",
        "aqt.execution",
        "aqt.monitoring",
        "aqt.lockbox_eval",
    ],
)
def test_package_imports(module: str) -> None:
    assert import_module(module).__name__ == module

~~~~


## Complete file: review/task1/verify_task1.py

~~~~text
"""One-off Task 1 evidence checks; never imported by the runtime package."""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "review/task1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def governance() -> None:
    baseline = json.loads((REVIEW / "protected-before.json").read_text())
    expected = {entry["path"]: entry["sha256"] for entry in baseline}
    inventory = {
        p.relative_to(ROOT).as_posix()
        for area in ("docs", "protocols", "schemas", "specs")
        for p in (ROOT / area).rglob("*")
        if p.is_file() and p != ROOT / "docs/README.md"
    } | {"FROZEN_HASHES.json", "FROZEN_HASHES.json.sha256"}
    assert len(expected) == 28 and inventory == set(expected)
    for path, sha256 in expected.items():
        assert digest(ROOT / path) == sha256, path
    before = json.loads((REVIEW / "pre-task-files.json").read_text())
    for path, sha256 in before.items():
        if path != "README.md":
            assert digest(ROOT / path) == sha256, path
    for path in sorted(inventory):
        if path.endswith(".sha256"):
            sidecar = ROOT / path
            sha256, filename = sidecar.read_text().strip().split(maxsplit=1)
            assert filename == sidecar.stem
            assert digest(sidecar.with_suffix("")) == sha256, path

    constitution = (ROOT / "docs/RESEARCH_CONSTITUTION.md").read_text(encoding="utf-8")
    pattern = r"(\*\*Content hash:\*\* `)([0-9a-f]{64})(`)"
    matches = re.findall(pattern, constitution)
    assert len(matches) == 1
    canonical = re.sub(pattern, r"\1\3", constitution)
    content_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert content_hash == matches[0][1]
    manifest = json.loads((ROOT / "FROZEN_HASHES.json").read_text())
    assert manifest["release"] == "v1.0" and manifest["status"] == "FROZEN"
    assert manifest["constitution_content_hash"] == content_hash
    bindings = {
        "protocol_file_sha256": "protocols/protocol_v1.yaml",
        "cost_model_sha256": "specs/COST_MODEL_v1.md",
        "feature_factory_sha256": "specs/FEATURE_FACTORY_v1.md",
        "benchmark_set_sha256": "specs/CANONICAL_BENCHMARKS_v1.md",
        "backtester_spec_sha256": "specs/BACKTESTER_SPEC_v1.md",
        "threat_model_sha256": "docs/THREAT_MODEL_v1.md",
        "hash_canonicalization_spec_sha256": "schemas/HASH_CANONICALIZATION_v1.md",
    }
    for field, path in bindings.items():
        assert manifest[field] == digest(ROOT / path), field
    protocol = yaml.safe_load((ROOT / "protocols/protocol_v1.yaml").read_text())
    assert protocol["constitution_hash"] == content_hash
    for key in (
        "cost_model",
        "feature_factory",
        "benchmark_set",
        "backtester_spec",
        "threat_model",
        "hash_canonicalization_spec",
    ):
        assert protocol[key + "_hash"] == manifest[key + "_sha256"], key
    assert protocol["feature_factory"]["hash"] == protocol["feature_factory_hash"]
    assert protocol["cost_model"]["hash"] == protocol["cost_model_hash"]
    assert (
        protocol["benchmarks"]["benchmark_set_hash"] == protocol["benchmark_set_hash"]
    )
    assert manifest["hash_canonicalization_spec_sha256"] in constitution

    schemas = sorted((ROOT / "schemas").glob("*.schema.json"))
    assert len(schemas) == 5
    for path in schemas:
        schema = json.loads(path.read_text())
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        Draft202012Validator.check_schema(schema)
    schema = json.loads((ROOT / "schemas/protocol.schema.json").read_text())
    validator = Draft202012Validator(schema)
    validator.validate(protocol)
    assert list(validator.iter_errors({}))
    assert list(validator.iter_errors({**protocol, "status": "UNFROZEN"}))
    print(
        "PASS: 28 protected bytes/inventory; all existing untracked work; 14 sidecars"
    )
    print(
        f"PASS: Constitution canonical hash {content_hash}; manifest/protocol bindings"
    )
    print("PASS: five Draft 2020-12 schemas; protocol instance; two rejection controls")


def configuration() -> None:
    hooks = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
    excluded = re.compile(hooks["exclude"])
    baseline = json.loads((REVIEW / "protected-before.json").read_text())
    assert all(excluded.search(entry["path"]) for entry in baseline)
    for path in ("docs/README.md", "src/aqt/core/paths.py", "README.md"):
        assert not excluded.search(path), path
    assert excluded.search("any/future.sha256")
    ignored = subprocess.run(
        ["git", "check-ignore", "--no-index", ".env", ".env.local", ".env.example"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert ignored.returncode == 0
    assert set(ignored.stdout.splitlines()) == {".env", ".env.local"}
    # BaseLoader preserves GitHub's YAML key 'on' as text, unlike YAML 1.1 booleans.
    ci = yaml.load(
        (ROOT / ".github/workflows/ci.yml").read_text(), Loader=yaml.BaseLoader
    )
    assert set(ci["on"]) == {"pull_request", "push"}
    assert ci["on"]["push"]["branches"] == ["main"]
    assert "continue-on-error" not in (ROOT / ".github/workflows/ci.yml").read_text()
    runs = [step["run"] for step in ci["jobs"]["checks"]["steps"] if "run" in step]
    assert runs == [
        'python -m pip install -e ".[dev]"',
        "ruff format --check .",
        "ruff check .",
        "mypy src",
        "python -m pytest",
        "lint-imports",
    ]
    print("PASS: frozen hook exclusions, README inclusion, env ignore exception, CI")


def boundaries() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text())
    edges = set()
    for contract in config["tool"]["importlinter"]["contracts"]:
        assert contract["type"] == "forbidden"
        assert contract["allow_indirect_imports"] is False
        assert not contract.get("ignore_imports")
        for source in contract["source_modules"]:
            for target in contract["forbidden_modules"]:
                edges.add((source, target))
    required = {
        ("aqt.research", "aqt.governor"),
        ("aqt.research", "aqt.execution"),
        ("aqt.research", "aqt.lockbox_eval"),
        ("aqt.governor", "aqt.execution"),
        ("aqt.governor", "aqt.models"),
        ("aqt.execution", "aqt.models"),
        *(
            (f"aqt.{p}", "aqt.research")
            for p in ("allocation", "governor", "execution", "monitoring")
        ),
    }
    assert required <= edges
    results = []
    # Disposable copies only. No import probes ever enter the user's source tree.
    for source, target in sorted(required):
        for indirect in (False, True):
            with tempfile.TemporaryDirectory(prefix="aqt-task1-import-") as temporary:
                probe = Path(temporary)
                shutil.copytree(
                    ROOT / "src",
                    probe / "src",
                    ignore=shutil.ignore_patterns("__pycache__"),
                )
                shutil.copyfile(ROOT / "pyproject.toml", probe / "pyproject.toml")
                command = [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, 'src'); "
                    "from importlinter.cli import lint_imports_command as run; run()",
                    "--no-cache",
                ]
                control = subprocess.run(
                    command, cwd=probe, capture_output=True, text=True, check=False
                )
                assert control.returncode == 0, control.stdout + control.stderr
                source_path = probe / "src" / source.replace(".", "/") / "probe.py"
                target_path = probe / "src" / target.replace(".", "/") / "probe.py"
                target_path.write_text("", encoding="utf-8")
                if indirect:
                    (probe / "src/aqt/core/bridge.py").write_text(
                        f"import {target}.probe\n", encoding="utf-8"
                    )
                    source_path.write_text("import aqt.core.bridge\n", encoding="utf-8")
                else:
                    source_path.write_text(f"import {target}.probe\n", encoding="utf-8")
                violation = subprocess.run(
                    command, cwd=probe, capture_output=True, text=True, check=False
                )
                assert violation.returncode == 1, violation.stdout + violation.stderr
                assert "BROKEN" in violation.stdout and target in violation.stdout
                results.append(
                    {
                        "source": source,
                        "target": target,
                        "indirect": indirect,
                        "command": command,
                        "cwd": str(probe),
                        "control_exit": control.returncode,
                        "violation_exit": violation.returncode,
                        "output": violation.stdout + violation.stderr,
                    }
                )
    (REVIEW / "boundary-probes.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    print(f"PASS: {len(results)} direct/indirect probes rejected; controls passed")


if __name__ == "__main__":
    governance()
    configuration()
    boundaries()

~~~~


## Complete file: review/task1/run_checks.ps1

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
