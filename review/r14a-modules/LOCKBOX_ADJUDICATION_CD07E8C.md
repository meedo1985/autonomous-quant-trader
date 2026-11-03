# Adjudication of Sol re-check 6 of the lockbox module (cd07e8c)

- Review record: `SOL_LOCKBOX_RECHECK_CD07E8C.md` (Codex `gpt-6-sol`, high, read-only; verdict FIX).
- Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-03, owner's Windows laptop.

| ID | Sol | Verdict | Reasoning and evidence | Disposition | Validation |
|---|---|---|---|---|---|
| R14L6-S-1 | BLOCKER | AGREE | Annex D §D-3.7 `begin_read` step 4 (freeze-sheet 8a1ec72) ends: "With no check record or differing identities, refuse, write nothing and log an incident. A check result that is a reason code appends a rejection entry." The `Store` docstring listed the entitlement conditions but not these two outcomes. | Repaired (contract text only): the `Store` docstring now states both outcomes, and that a reason-code check grants no read. The store build's tests stay an open item. | ruff, ruff format, mypy strict on the file clean. |
| R14L6-S-2 | BLOCKER | AGREE | `test_malformed_request_seed_l266_refused` changed only `Request.seed_l266`; the nominee kept a different valid seed, so the `n["seed_l266"] == seed_l266` comparison refused on its own and the format refusal was untested. | Repaired: `test_coherent_malformed_seed_l266_refused` (uppercase 64 chars; 63 chars): nominee and request carry the same malformed seed with the estimator value `int(seed, 16) % 2**31`, and the check must answer `IDENTITY_MISMATCH`. | Both cases pass. Mutation: with the `_sha256_hex` format check removed from `screen.estimator_seed` in the working copy, both fail; `calibration/screen.py` was then restored with `git checkout`, and its committed bytes hash to the frozen `e6ba5ac5...`. |

Sol's other observations are accepted: `screen.estimator_seed` is called, not re-implemented (R-14a item 4); no `aqt.core.preregistration` import; no remaining caller of `c2_lockbox.trial_seed`; CI's engine job covers all five lockbox test files; the non-derivation and coherent wrong-index tests catch their mutations.

Validation (Windows, repo `.venv`, Python 3.14.7, Bitcoin node running): `python -m pytest -q -p no:cacheprovider tests/unit/test_c2_lockbox*.py` -> 130 passed; ruff check, ruff format --check, `mypy --strict` on both changed files clean; lint-imports 7 kept, 0 broken. `test_calibration_rundef` not run locally (low memory with the node up); CI on PR #83 runs it.

**Open before signing C2 (unchanged):** the sealing record's `seed_l266` and `family_seed_f`; the launch route; acceptance provenance (owner decision); the reference vectors on the qualified image; the S4 format bindings; the store build's §D-3.7 obligations.
