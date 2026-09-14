# Task 10 Claude adversarial review packet

Status: ready for direct local Claude Code review
Date: 2026-09-14
Base commit: `a50ed80d0a258afdb9e37917a5b9c8807b170250`

## Review scope

Review only Task 10 against `review/task10/AUTHORIZED_SPEC.md`, root
`AGENTS.md`, the frozen Constitution/protocol/hash-canonicalization rules,
and the repository review skills. The implementation records identities and
facts only. It must not make eligibility, budget, protected binding, lockbox,
metrics, result, promotion, governor, execution, strategy, or network decisions.

Inspect the actual unified diff plus every untracked file. The relevant complete
working-tree files are:

- `src/aqt/core/ledger.py`
- `src/aqt/core/preregistration.py`
- `tests/unit/test_registry_ledger.py`
- `tests/unit/test_preregistration.py`
- `tests/integration/test_preregistration_schema_binding.py`
- `README.md`
- `pyproject.toml`
- `review/task10/AUTHORIZED_SPEC.md`
- `review/task10/FABLE_DECISION_REVIEW.md`
- `review/task10/LOCAL_REPORT.md`

Snapshot SHA-256 values before this packet/report were written:

- `4746b158ae70d3e6fb6c51f3b0292e65626a3869aff3731e8b48df91cf5652ac  src/aqt/core/ledger.py`
- `e35844e28adcab413cf1c73b80ce157fdabd0dfa2a34b0fe4a232fbd56b53fc2  src/aqt/core/preregistration.py`
- `c5f0919d917d58bca33a838b4ec484235bd22d9771c8438869fb69651e876cc2  tests/unit/test_registry_ledger.py`
- `d7ffcce5c270d56f80e897fc8e876cb58b93bd06b0d8eed73f06b57c50006427  tests/unit/test_preregistration.py`
- `982f22a2437c1ce04dbb88083a3d4adfed1b6dd10a2af6be9eba18c7c734f96d  tests/integration/test_preregistration_schema_binding.py`
- `4656377a081bd22c941d1a1a78e73d0d7d8262e29f1a273e61ccc6b8004d9ddf  pyproject.toml`

## Validation evidence

Local gate: PASS. See `review/task10/LOCAL_REPORT.md` for exact commands.
The full result was 961 passed and 4 pre-existing skips. Ruff, formatting,
mypy, all four import contracts, Git whitespace, 28/28 frozen baseline files,
14/14 sidecars, all embedded bindings, and 6/6 Task 6 accepted hashes passed.

## Questions for adversarial review

1. Can any malformed, noncanonical, or schema-invalid hypothesis/experiment be
   recorded through the Task 10 public preregistration APIs?
2. Can concurrent Windows writers lose, duplicate, or fork a sequence, or can a
   crash/torn write be silently repaired or overwritten?
3. Is the full SHA-256 seed material/output unambiguous and fully fixed by the
   recorded test vector?
4. Can read-side family accounting be misattributed in a way that Task 10 itself
   should prevent without crossing into protected protocol enforcement?
5. Does any API quietly implement permission, budget, hash acceptance, cycle
   binding, confirmation/lockbox access, or another excluded behavior?
6. Are the tests meaningful, and is any acceptance criterion missing evidence?

Return stable finding IDs grouped under BLOCKER, NON-BLOCKING, and QUESTION.
For each, name file/line, triggering scenario, evidence, impact, and minimal
correction. State missing evidence instead of guessing. End with PASS or BLOCK.
Do not modify files and do not propose strategy logic.
