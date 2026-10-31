# Task gate: pre-freeze `screen.py` change (D-20 Q2(ii), Q5)

**Gate run by:** Claude Opus 5.5 (`claude-opus-5-5`), the implementer, on 2026-10-31. This is a self-gate, not an approval.

**Branch:** `pre-freeze-screen-q2-q5`. **Base:** `main` at `ed8aa76`. **Head:** the commit that adds this file, whose parent is `471568c`.

**LOCAL GATE: PASS.**

## Scope

**Authorised by:**
- the owner's D-20 decision items 6 and 9 (freeze-sheet `OWNER_DECISION_D20_LOCKBOX.md`, f04aa6c);
- the owner's "go 1" (2026-10-31);
- the owner's R-14a decision (freeze-sheet `r14-exception/OWNER_DECISION_R14A.md`, 0d5b2b4), which limited `screen.py`'s part to the seed and the final-hour rule.

**Changed:**
- `calibration/screen.py`: new `estimator_seed` and `confirmation_path`; a `model_seed` parameter, default 0, through `screen_gates` → `model_column` / `walk_forward` and G-14's un-shifted pipeline;
- `tests/unit/test_calibration_screen.py`: T1, T1b, T2-T5, a bit-comparison check, and one existing wrapper made keyword-tolerant;
- `tests/unit/baselines/screen_ed8aa76.py.txt`: the reviewed pre-change `screen.py`, as T1's in-process baseline;
- `review/d19-engine/FREEZE_REVIEWS.json`: `screen.py` → `e6ba5ac5…82b6`, with its record;
- `review/pre-freeze-screen/`: the design and the review records.

**Not changed:**
- the data reader, the confirmation module and the lockbox module, which are later tasks under R-14a;
- `scripts/d19_heldout.py`, `calibration/mapping.py`, and every engine file.

No out-of-scope edit. No secrets. No confirmation or lockbox data is read; every fixture is synthetic.

## Acceptance (design rev 3, `DESIGN.md`)

| Criterion | Evidence |
|---|---|
| C1: seed map and routing | T2 (`test_estimator_seed_maps_the_l266_seed_mod_2_31`); T3 (`test_model_seed_reaches_the_nominee_fits_but_not_the_null_draws`, seeds recorded by route; `test_a_fixed_model_seed_gives_bit_identical_emissions`, all six classes) |
| C2: final-hour row and validation | T4 (`test_the_derived_terminal_row_changes_only_the_last_hours_return`, both symbols and both legs, final return asserted); `test_confirmation_path_appends_a_terminal_row_at_the_last_close`; T5 (`test_confirmation_path_validates_rows`) |
| The guard: defaults bit-identical | T1 (`test_defaults_match_the_pre_change_screen_exactly`, IEEE-754 bytes against the ed8aa76 module loaded in-process; baseline identity in `test_the_baseline_is_the_reviewed_pre_change_screen`; byte-check self-test `test_bits_tell_signed_zeros_and_nan_payloads_apart`) |
| Frozen reference vectors | G-11 and G-14: the existing exact tests pass. Paths: **T1b, skipped on this host** (pinned image only). **It must run in the image before step G.** |
| §4 freeze consequences | `FREEZE_REVIEWS.json` updated; `test_calibration_qobj.py` passes (38 with `test_d19_deploy.py`). G0 redo and the FREEZE_HELDOUT update come after merge (below). |

## Validation (Windows 11 host, project `.venv`, Python 3.14; head 471568c, test-only and docs commits after that)

| Command | Result |
|---|---|
| `ruff format --check .` | exit 0, 177 files formatted |
| `ruff check .` | exit 0, all checks passed |
| `mypy src` | exit 0, no issues in 56 files |
| `lint-imports` | exit 0, 7 contracts kept, 0 broken |
| `python -B -m pytest --ignore-glob=tests/unit/test_calibration_*` | 1856 passed, 9 skipped |
| `python -B -m pytest tests/unit/test_calibration_*.py tests/unit/test_d19_deploy.py` | 481 passed, 1 skipped (T1b) |

CI on the PR runs the same commands on Linux.

## Frozen artefacts

The `docs/`, `protocols/`, `schemas/` and `specs/` folders, `FROZEN_HASHES.json` and every `*.sha256` file are byte-unchanged against `ed8aa76` (`git diff --quiet ed8aa76 HEAD -- …` succeeded). All 13 sidecars under those folders were recomputed from the committed bytes and match. No frozen hash was regenerated.

## Reviews (independent, different model: Codex gpt-6-sol)

| Record | Verdict |
|---|---|
| `SOL_DESIGN_REVIEW_CEB12C3.md` | FIX (PFS-S-1..5); S-1 was routed to the owner, who chose R-14a |
| `SOL_DESIGN_RECHECK_73E22E6.md` | FIX (PFS2-S-1..2, tests) |
| `SOL_CODE_REVIEW_B8AB915.md` | FIX (PFSC-S-1..3, tests) |
| `SOL_CODE_RECHECK_61D44D5.md` | FIX (PFSC2-S-1, tests) |
| `SOL_CODE_RECHECK2_2E2C81E.md` | **ACCEPT WITH NOTES**, no findings; accepts `screen.py` for the freeze |

Every finding was repaired, and none is left unrepaired.

The `scientific-reproducibility-review` and `quant-code-review` skills were applied through the Sol prompts, which named both. The `claude-adversarial-review` packet does not apply as written, because the implementer is Claude. The independent different-model adversary was Codex Sol, recorded above.

## Outstanding before merge and before the freeze

1. **Owner §16 PR review** (Constitution §16; `screen.py` is evaluation code in the frozen object).
2. **T1b in the pinned image** before step G (`d19.sh` sets `AQT_IMAGE_DIGEST`).
3. **After merge:**
   - redo step G0, so `/opt/aqt-d19/build` is at the merged commit;
   - update `FREEZE_HELDOUT.md` FP2 (d), `G0_EVIDENCE.md` and step G's build commit (DESIGN §4 item 4).
4. The development run is unaffected (`screen.py` is a LATER file).
