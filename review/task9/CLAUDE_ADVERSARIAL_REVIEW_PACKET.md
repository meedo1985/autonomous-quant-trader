# Task 9 Claude Adversarial Review Packet

## Requested verdict

Return `PASS` or `REVISE`. Report only concrete blockers or material
non-blocking risks with file/function and a reproducible trigger. Do not edit.

## Scope and authority

Review the staged Task 9 change against `review/task9/AUTHORIZED_SPEC.md`, the
frozen constitution, protocol, hash canonicalization rules, experiment schema,
and existing bar semantics. Frozen artifacts must remain untouched. This task
records identities only and must not bind a trial or start Task 10.

## Files to inspect

- `src/aqt/data/manifest.py`
- `src/aqt/core/code_identity.py`
- `tests/unit/test_data_manifest.py`
- `tests/unit/test_code_identity.py`
- `tests/integration/test_manifest_experiment_binding.py`
- `pyproject.toml`
- Task 9 decision and review records under `review/task9/`

## Prior adversarial findings

Read `SOL_HIGH_REVIEW.md` and `SOL_FINDING_DISPOSITION.md`. Verify that all five
fixes close the demonstrated bypasses rather than only satisfying their tests.

## Executed evidence

- Focused: 55 passed.
- Full: 900 passed, 4 pre-existing skips.
- Ruff, mypy strict, and all four import contracts passed.
- Frozen verification passed 28/28 files, 14/14 sidecars, and all bindings.
- Task 6 accepted hashes passed 6/6.
- Git whitespace check passed.

## Specific attack surface

- Direct dataclass construction plus a recomputed self-hash.
- Non-hourly series and mislabeled intervals.
- Sealed references outside lockbox, invalid composite headers, and incomplete
  per-symbol partition coverage.
- Raw identity asserted without bytes.
- Git ignored source, index masking flags, checkout line endings, and dirty or
  untracked covered paths.
- Leakage of raw lockbox identity through any general API or composite mapping.
- Canonical JSON floats and self-hash handling.
