# Adjudication: Sol review of slice 4a route M, at 540215d

- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the author, 2026-11-09. Not approval.
- Review: `SOL_CONFIRMATION_SLICE4A_M_540215D.md` (committed 10f649a), verdict
  **ACCEPT WITH NOTES**: no forgery, wrong-round acceptance or valid-signature refusal found;
  all 53 isogeny constants compared with RFC 9380 E.2 independently; message and DST agree
  with drand-client.

| ID | Decision | Repair |
|---|---|---|
| R14SM-S-1 (stale `_TRIAL_SEED` after a failed reload) | Accepted, repaired. | `load_line266` sets `_TRIAL_SEED = None` first. Test `test_a_failed_reload_clears_line266`: after a success, a failing import leaves `None` and `derive_seeds` refuses. |
| R14SM-S-2 (no G2 wrong-subgroup key test) | Accepted, repaired. | Test `test_a_g2_key_outside_the_subgroup_is_refused` with x = (0, 1) (on the twist, outside G2); it fails if the G2 subgroup check is removed. |

Reviewer notes not taken as findings: direct `bls_verify` accepts uppercase or spaced hex
through `bytes.fromhex`, but the only gate path (`check_beacon`) refuses non-canonical hex
first; if `aqt.core.preregistration` is already loaded, `load_line266` reuses it, which the
slice-6 pre-read byte scan covers (LGM-3).

Sol's sandbox could not run `mypy src` or `lint-imports`; both ran here (below).

## Validation after the repairs (Windows 11, repo `.venv`, Python 3.14)

| Command | Result |
|---|---|
| `pytest tests/unit/test_c2_confirmation_bls.py tests/unit/test_c2_confirmation_seeds.py tests/unit/test_d19_deploy.py` | 70 passed |
| `pytest tests/unit/test_c2_confirmation*.py tests/unit/test_c2_lockbox*.py tests/unit/test_d19_deploy.py` | 262 passed |
| `mypy --strict` module + both test files | 10 errors, all in the imported `test_calibration_screen.py`, pre-existing |
| `mypy src` | no issues (56 files) |
| `ruff format --check .`, `ruff check .` | clean |
| `lint-imports` | 7 kept, 0 broken |

## Status

Slice 4a route M: **ACCEPT WITH NOTES, notes repaired.** R14S4-S-1, LG4-1 and LG4-6 are
closed in code. Open, as recorded: LGM-1 (OD-2, placeholder) and LGM-2 (OD-4, genesis and
period in the signed C2) for the owner; LGM-3/LGM-4 for slice 6 and the lockbox
(R14S4-S-3, SV1-S-6 handoff). A re-check of these two small repairs is optional.
