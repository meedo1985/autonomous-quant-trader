# Adjudication of the GPT-6 Sol re-review of item 2b step 1 at b6edc5c

**Review:** `review/d19-engine/SOL6_ITEM2B_Q5_WIRING_REREVIEW_B6EDC5C.md`
(FIX for pilot use; no new I2BWR IDs. It carries I2BW-1, I2BW-2 and I2BW-5 as
open, and finds I2BW-3 and I2BW-4 resolved.)

**Adjudicated and repaired by:** Claude Opus 5.5 (`claude-opus-5-5`) on
2026-10-11. Repairs are in WIP commit `44c9859`. They have not been
re-reviewed yet.

| ID | Decision | Repair and evidence |
|---|---|---|
| I2BW-1 | AGREE; owner binding obtained, repaired | The reviewer is right. The per-K pooling was an AI default from item 1, and the owner never accepted it. The earlier adjudication's claim that pooling across K "could never accept" was wrong. It described how the code handled exact fields, and §3.5 does not require that. The owner chose "Pool over all K" (`OWNER_DECISION_I2BW1_THRESHOLD_POOLING.md`). `reduce.pooled` now returns one pool per `T` level. Each tail in the pool is the extreme over every cell at that level, whatever its K, and the pool carries no `K`. `reduce.for_k(pool, k)` builds one cell's set from that pool. `K` and `T` stay exact, and the set holds exactly the tails named by `classifier.required(k)`. It raises `ValueError` if no K >= 2 cell supplied the correlation tails. The driver's `dev_bounds` gives each `cell_id` its own set. `d19_choose` uses `for_k`, and its report keys `final_thresholds` as `"T=t"`. Tests: `test_pooled_takes_each_tails_extreme_per_t_level_over_every_k` (a K = 1 cell sets a K = 5 cell's kurtosis tail; T levels never mix) and `test_for_k_makes_an_exact_k_threshold_set_from_the_pool` (complete, accepted by `classifier.within`; K = 2 is refused when only K = 1 cells exist). |
| I2BW-2 | AGREE, repaired | Checking four fields let a forged object through. `record` now rebuilds the BTC exploration manifest from `--raw-root` with `klines.build_exploration_manifest`, the same builder `scripts/build_manifests.py` uses. It requires the supplied file to equal that manifest's canonical JSON byte for byte. Otherwise nothing is written. The end-to-end test adds `forged.json`, which holds the four fields copied from the real manifest, beside `{}` and the manifest of other archives. All three are refused. |
| I2BW-3 | No action | Resolved per the reviewer. |
| I2BW-4 | No action | Disagreement accepted by the reviewer. |
| I2BW-5 | AGREE IN PART, repaired | New test `test_a_q5_development_record_equals_an_independent_section_2_computation`. For each Q5 family and three replications, it rebuilds the stored record from its parts. The parts are: the dev-namespace `rules.draw`, `classifier.within`, `dsr.evaluate` under both block rules with the family seed labelled by the family, the P18-4 nominee as argmax of the per-candidate Sharpe ratio (computed in the test), and `gates.u_g`. It never calls `choices.consistent`. It also asserts that Annex B reached `z_f*` (reason `None`) on at least one Q5 draw. **Limit, stated plainly:** the test checks how the driver composes these steps for Q5. It reuses the production `dsr.evaluate` and `gates.u_g`, so it does not check them independently. Those components are checked elsewhere, and Q5 does not change them. `test_accelerated_path_is_bit_identical_to_the_reference` and `test_method_v_is_deterministic_and_close_to_the_task12_numerics` in `test_calibration_engine.py` check `dsr.evaluate` against the reference and Task 12 numerics. The `u_g` numerics are covered by the reference vectors (`test_reference_vectors_see_the_u_g_numerics`). Annex B numbers computed by hand for one Q5 draw would therefore add no check of the Q5 code that this test lacks. |

No calibration was run.

## Checks on `44c9859` (2026-10-11, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest` the nine `tests/unit/test_calibration_*.py` files `-q -p no:cacheprovider` | 0 | 194 passed in 650.98 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those nine files | 0 | 1786 passed, 9 skipped in 424.24 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 144 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_run_definition.py scripts/d19_choose.py` | 0 | No issues in 70 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |

The suite ran in one sequential run, without interruption. The total is 1980 tests, against 1978 at `b6edc5c`. The two added tests are `test_for_k_makes_an_exact_k_threshold_set_from_the_pool` (the pooled test was rewritten, not added) and `test_a_q5_development_record_equals_an_independent_section_2_computation`.
