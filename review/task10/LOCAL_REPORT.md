# Task 10 local implementation and gate report

Date: 2026-09-14
Base commit: `a50ed80d0a258afdb9e37917a5b9c8807b170250`
Worktree state: uncommitted Task 10 snapshot

## Scope completed

Implemented the bounded identity/storage layer authorized in
`AUTHORIZED_SPEC.md`:

- canonical immutable hypothesis content and full Draft 2020-12 frozen-schema
  validation;
- domain-separated deterministic full SHA-256 trial seeds;
- fixed parameter-grid and horizon enumeration;
- frozen-schema-validated experiment records;
- canonical append-only hash-chained JSON Lines storage;
- Windows/POSIX cross-process append locking, flush and fsync;
- torn-write/history corruption detection without repair;
- pure read-side family and hypothesis trial counts.

No budget gate, trial permission, protected hash acceptance, real cycle binding,
confirmation/lockbox access, metrics/results, strategy, model, network, Binance,
promotion, governor, or execution behavior was added.

## Implementation model and adjudication

Claude Code implemented the first snapshot. Observed model metadata was
`claude-opus-5`; exact Opus 5.1 was not available. Claude reached its tool-turn
limit before it could run tests because its local PowerShell tool calls were
denied.

Local review corrected three faulty test expectations, replaced required-field
inspection with real Draft 2020-12 validation, removed caller-selectable schema
paths, and replaced an undocumented 64-bit seed truncation with the complete
SHA-256 digest.

## Validation

All commands ran from the repository root with Python 3.12.10.

- `.venv/python.exe -m pytest tests/unit/test_registry_ledger.py tests/unit/test_preregistration.py tests/integration/test_preregistration_schema_binding.py -q`
  — exit 0; 61 passed.
- `.venv/python.exe -m pytest -q`
  — exit 0; 961 passed, 4 pre-existing skips.
- `.venv/Scripts/ruff.exe check .`
  — exit 0; all checks passed.
- `.venv/Scripts/ruff.exe format --check .`
  — exit 0; 52 files already formatted.
- `.venv/Scripts/mypy.exe src`
  — exit 0; 25 source files clean.
- `.venv/Scripts/lint-imports.exe`
  — exit 0; 4 contracts kept, 0 broken.
- `git diff --check`
  — exit 0.
- `review/task6/verify_frozen.ps1`
  — exit 0; 28/28 trusted files, 14/14 sidecars, Constitution self-hash,
  7/7 manifest/protocol bindings, and nested bindings passed.
- Independent SHA-256 verification of
  `review/task6/ACCEPTED_ORACLE_HASHES.sha256`
  — 6/6 passed.

## Local review findings

BLOCKER: none.

NON-BLOCKING: the generic ledger intentionally stores arbitrary canonical
record types. Semantic schema checks belong to the preregistration functions.
The lock sidecar persists as an empty file so crashed processes release locks
through the operating system without stale-lock recovery.

QUESTION: whether a later protected experiment engine should enforce unique
hypothesis IDs and registered-family linkage. Task 10 does not grant trial
permission or enforce protocol policy, so this remains outside this task.

LOCAL GATE: PASS.
Claude adversarial status: ADJUDICATED — Fable 5.1 PASS, no blockers.
