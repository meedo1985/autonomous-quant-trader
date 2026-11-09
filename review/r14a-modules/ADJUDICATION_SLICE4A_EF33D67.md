# Adjudication: Sol review of confirmation slice 4a at ef33d67

- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the author, 2026-11-09. Adjudication
  is not approval; the owner decides the open blocker.
- Review: `SOL_CONFIRMATION_SLICE4A_EF33D67.md` (committed in e954677), verdict FIX.

| ID | Sol | Decision | Action |
|---|---|---|---|
| R14S4-S-1 | BLOCKER | **Accepted, left open (owner decision).** Correct: an injected `line266` is unauthenticated, and the 64-hex check does not bind it to the frozen `preregistration.trial_seed` (R-8). It is LG4-6 restated with the impact made concrete. It cannot be closed inside this slice without either importing the frozen module (impossible in the pinned image, which lacks `jsonschema`) or re-implementing it (R-14a item 4 forbids that). | Kept open as a **blocker before C2 signing**, decided with LG4-1 (BLS) as one image question. Options for the owner: (a) add `jsonschema` (and its deps) to the image in the slice-4b rebuild, so that the real run passes the frozen function itself; (b) a reviewed route that loads the frozen function from the hash-checked frozen file without the module's top-level imports. Until one is chosen and bound, no confirmation evaluation may run. The lockbox's use of `request.seed_l266` (c2_lockbox.py:642) is closed by the same binding plus the slice-6 loader, which must hand the lockbox the seed this derivation recorded. |
| R14S4-S-2 | NON-BLOCKING | **Accepted, repaired.** | `_check_records` refuses a duplicate `trial_id` in a family (`trial_id must be distinct`), so a seed cannot be silently dropped. Test `test_duplicate_trial_id_is_refused_not_dropped` (distinct indices, same id). |
| R14S4-S-3 | NON-BLOCKING (integration) | **Accepted, left open (not this slice).** Correct: the accepted lockbox looks the nominee up by `trial_id` alone, while `check_declaration` allows the same id in two families. | Open item for the lockbox integration (slice 6 / lockbox change, own review): match on `(family, trial_id)`. Changing accepted lockbox code is outside slice 4a. |
| Test note (R-13 bytes) | — | **Accepted, repaired.** | The provenance test now checks each `trial_seed` against the literal bytes `{"family_seed":…,"trial_id":…}`, not `seeds_record`. |
| Test note (zero through derivation) | — | **Accepted, repaired.** | `test_estimator_seed_zero_is_kept` also runs `derive_seeds` with a line-266 seed mapping to 0 and checks the record keeps 0. |

## Validation after the repairs (Windows 11, repo `.venv`, Python 3.14)

| Command | Result |
|---|---|
| `pytest tests/unit/test_c2_confirmation_seeds.py tests/unit/test_d19_deploy.py` | 37 passed |
| `pytest tests/unit/test_c2_confirmation*.py tests/unit/test_c2_lockbox*.py` | 218 passed |
| `ruff format --check calibration tests`, `ruff check .` | clean |
| `mypy --strict calibration/c2_confirmation.py tests/unit/test_c2_confirmation_seeds.py` | 10 errors, all in the imported `test_calibration_screen.py`; the same 10 at the unrepaired base (pre-existing, not in the changed files) |
| `lint-imports` | 7 contracts kept, 0 broken |

No frozen path touched.

## Status

Slice 4a stays **FIX** until R14S4-S-1 is closed by the owner's image decision (with
LG4-1). The repairs for S-2 and the test notes go to Sol for re-check together with that
decision's implementation, to avoid a second review round of the same code.
