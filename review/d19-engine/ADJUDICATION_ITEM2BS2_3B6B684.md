# Adjudication of the GPT-6 Sol review of item 2b step 2 at 3b6b684

**Review:** `review/d19-engine/SOL6_ITEM2B_STEP2_REVIEW_3B6B684.md`. The
verdict is ACCEPT for pilot use (measurement only), with two Low findings,
I2BS2-1 and I2BS2-2. The reviewer found no under-counted test, no wrong
coverage category for a valid cell, and no anti-conservative QJ event
definition.

**Adjudicated and repaired by:** Claude Opus 5.5 (`claude-opus-5-5`) on
2026-10-11, in commit `212a949`. Both repairs are Low and add tests only
around existing behaviour, so no re-review was requested. The verdict was
already ACCEPT.

| ID | Decision | Repair and evidence |
|---|---|---|
| I2BS2-1 Low | AGREE, repaired | `reduce.cell_thresholds(chain, joint)` no longer infers the record shape from the first draw. The caller passes `joint = (law == "semi-joint")`, both in the driver's `dev_bounds` and in `d19_choose`. For a QJ cell, every draw must be a dict with exactly the keys `{"trend", "vol"}`. Otherwise the call raises `ValueError` ("not one record per family"), which both scripts already report as a controlled refusal. Test `test_a_qj_threshold_chain_needs_one_record_per_family_on_every_draw` covers three cases: a later draw with an extra key, a draw with a missing family, and a flat draw. All three are refused. A good chain gives two threshold sets in family order. |
| I2BS2-2 Low | AGREE, repaired | Test `test_a_successful_choice_covers_every_category_until_qj_is_demoted`. It builds one qualifying cell per O18-4 category plus a QJ cell, and runs `choices.choose` at M = 322. Every category has a qualifying cell, and `joint_generator` lists both QJ families. When the QJ trend family is given 10 DSR events, both families are demoted, and `joint_generator` and `two_trial` become empty. **Not done:** the test does not show that the joint limits bind at the real targets. At M ≈ 322 and 12,000 replications they cannot bind (disclosed at build time). The tight-τ tests remain the only evidence for the joint branches. |

**Boundary repeated from the review:** full preregistered grid validation
(I2A-4) is item 3. This step does not make an off-grid manifest safe for
certification.

No calibration was run.

## Checks

| On | Command | Exit | Result |
|---|---|---:|---|
| `3b6b684` (reviewed) | the nine calibration test files | 0 | 215 passed in 760.48 s |
| `3b6b684` | the rest of the suite (`--ignore=` those nine) | 0 | 1786 passed, 9 skipped in 370.12 s |
| `3b6b684` | ruff check / format --check; mypy (70 files); lint-imports; verify_frozen.ps1 | 0 | all pass (6 contracts kept; 28/28, 14/14, 7/7, nested) |
| `212a949` (repaired) | the nine calibration test files | 0 | 217 passed in 830.95 s |
| `212a949` | the rest of the suite (`--ignore=` those nine) | 0 | 1786 passed, 9 skipped in 383.49 s |
| `212a949` | ruff check / format --check; mypy (70 files); lint-imports; verify_frozen.ps1 | 0 | all pass (6 contracts kept; 28/28, 14/14, 7/7, nested) |

The `212a949` gate kept running after Claude Code stopped its separate
watcher for low system memory. The gate's own output is complete, and the
results above come from it.

**Outcome:** item 2b step 2 is accepted for pilot use. With step 1
(`SOL6_ITEM2B_Q5_WIRING_REREVIEW3_3E622D2.md`), item 2b (Q5 and QJ) is
complete for pilot use. Carried to item 3: I2A-4 (qualifying-grid
enforcement and out-of-grid rejection).
