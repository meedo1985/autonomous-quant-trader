# Adjudication of Sol's lockbox re-check 3 (`SOL_LOCKBOX_RECHECK_87FF5E0.md`)

- Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-02, the module's author,
  against the code at `87ff5e0`. The repair is in the commit that adds this file.
- Format: `ID | Sol severity | AGREE / PARTIAL / DISAGREE | reasoning and evidence |
  disposition | validation`.

| ID | Sol | Verdict | Reasoning and evidence | Disposition | Validation |
|---|---|---|---|---|---|
| R14L3-S-1 | BLOCKER | AGREE | `Started` is a frozen dataclass, but its `declaration` field was the parsed `dict`, which can be edited after `start()`; Sol's probe (index 3 → 4 in the dict, request and artifact made coherent) returned `PASS`. | Repaired: `Started` carries the verified declaration as `bytes` and `declaration_sha256` (the hash the chain checked against the post), both immutable; `chain_log` is a read-only `MappingProxyType`. `pre_read_check` re-hashes the bytes against that hash and parses them itself; any difference is `IDENTITY_MISMATCH`. **Residual, unchanged:** a Python caller can still build a `Started` by hand with a self-consistent false declaration and hash; only the launch route can rule that out (LG-8, R14D3-S-2). | `test_declaration_changed_after_start_refused` (Sol's probe; shown to return `PASS` with the hash comparison removed and `IDENTITY_MISMATCH` with it); `test_declared_entry_binds_the_nominee` (7 cases, re-encoded); `test_started_carries_immutable_verified_values`. |

Sol's other observations are accepted as stated: R14L2-S-2's field checks hold and its
provenance gap is correctly an owner decision; R14L2-S-3's refusal precedes any append;
the open items (launch route, acceptance provenance, qualified-image vectors, S4 format
bindings) are described as open; no other regression.

Validation (Windows, repo `.venv`, Python 3.14.7): lockbox tests and the five fast
calibration-tree test files 271 passed; `test_calibration_rundef` in the commit message;
ruff, ruff format, mypy strict per file and lint-imports (7 kept) clean.
