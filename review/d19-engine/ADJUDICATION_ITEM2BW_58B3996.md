# Adjudication of the GPT-6 Sol review of item 2b step 1 (Q5 wiring) at 58b3996

**Review:** `review/d19-engine/SOL6_ITEM2B_Q5_WIRING_REVIEW_58B3996.md` (FIX
for pilot use; I2BW-1..I2BW-5; from a packet). The reviewer found no
defect in seed routing, the identity check of the source, the refusal
without `--raw-root`, or the synthetic cells.

**Adjudicated and repaired by:** Claude Opus 5.5 (`claude-opus-5-5`) on
2026-10-11. Not yet re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| I2BW-1 High | AGREE IN PART, repaired | **Disagreed part:** pooling across different K. `K` and `T` are exact checks of the classifier (§13 item 4; `classifier.within` refuses another K), and `K = 1` has no correlation tails. A threshold set pooled across K could therefore never accept a replication. Pooling within K at each T level is the reading recorded in item 1 (`ITEM1_DEVELOPMENT_AND_CHOICES.md`, "Interpretations made here", item 1); it passed that item's seven review rounds. The reviewer was not given that note. **Agreed part:** `reduce.pooled` refused a manifest with two T levels at one K instead of pooling each T level. It now pools per (K, T): every candidate cell at that T level and K, agnostic and Q5 alike. The driver selects `bounds[(c.k, c.t)]`, and `d19_choose` uses the same key; its report keys `final_thresholds` as `"K=k,T=t"`. Test `test_pooled_takes_the_extreme_per_t_level_and_k_and_never_mixes_them` covers two T levels at one K and two K at one T. If the owner reads §3.5 item 2 differently, that is a proposal to the owner. |
| I2BW-2 Medium | AGREE, repaired | In a run with Q5 cells, `record` now requires `--exploration-manifest` to be the BTC exploration manifest of `--raw-root`: a partition manifest, exploration partition, BTCUSDT, with a `manifest_sha256` equal to the source's BTC manifest hash. Otherwise nothing is written. The end-to-end test refuses `{}` and the manifest of other archives. For runs without Q5 cells, that field keeps its earlier meaning: the hash of the given file. The assumption that it names the BTC hourly manifest is stated in the script's docstring. |
| I2BW-3 Medium | AGREE, repaired | `reference_variance` moved to `calibration.semi` (re-exported by `rules`). `semi.load_source` validates the source and fixes `v̄` once, in `Source.v_bar`. `record` therefore refuses an invalid source before writing anything, and every draw uses that fixed value. Test `test_a_source_r5_refuses_is_refused_when_loaded`. |
| I2BW-4 Low | AGREE that the claim was wrong; change kept | The job tuple is internal to the driver. Each job now always carries `bounds` and `raw_root`, and the worker's defaults keep the earlier behaviour. Nothing outside the driver uses the tuples. The prompt's claim that they were unchanged was wrong; it is corrected here, and the code is not reverted. |
| I2BW-5 Medium | AGREE, repaired | The end-to-end test now recomputes every stored Q5 development diagnostic with `rules.draw` under the `d19-dev-v1` namespace. It also requires each record to pass `choices.consistent` against the pooled thresholds: the full record check that `d19_choose` applies, covering keys, Annex B order, cause codes and recomputed lengths. |

No calibration was run.

## Checks after repair (2026-10-11, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest` the eight calibration files `-q -p no:cacheprovider` | 0 | 177 passed in 834.42 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those eight files | 0 | 1801 passed, 9 skipped in 905.90 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 144 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_run_definition.py scripts/d19_choose.py` | 0 | No issues in 70 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |

The calibration files finished in a first gate run. Claude Code then stopped
that run for low memory during the rest of the suite. With the owner's word
("contenue"), only the unfinished part was rerun, on the same unchanged files.
