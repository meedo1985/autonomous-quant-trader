# D-19 engine item 1: development namespace, targets and choices

Implemented by Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-10 on branch
`d19-calibration-engine`, under the owner's build go-ahead
(`OWNER_DECISION_D19_ACCEPT.md`) and the accepted §13 rev 7g. Not yet
reviewed. No calibration was run; tests use tiny synthetic pilot cells.

## What was built

| Piece | Files | Prereg |
|---|---|---|
| Exact binomial targets: Clopper-Pearson upper bound, critical count, tau | `calibration/binomial.py` | §5, §6, §13 item 3 (every tabled value reproduced in `tests/unit/test_calibration_binomial.py`) |
| Reduction: bit-exact decode, per-cell thresholds, pooled development thresholds | `calibration/reduce.py` | §3.5 items 1-2, §13 item 4 |
| Development namespace `d19-dev-v1` in the run driver, 12,000 prescribed | `scripts/d19_run.py`, `calibration/rundef.py` | §2, §8, §13 item 3 |
| Development choices: block rule, availability with the 40k escape and demotion, cap rule, `z_crit` | `calibration/choices.py`, `scripts/d19_choose.py` | §5 steps 1-3, §3.2 cap rule, §13 item 3 |
| A missing chain is now a clean `ChainError` ("chain missing"), not a traceback | `calibration/chunks.py` | §13 item 6 integrity |

## Interpretations made here (AI defaults; for review and the owner)

1. **Development thresholds are pooled per `K`.** §3.5 item 2 pools "per `T` level, the extreme over all candidate cells". `K` is an exact check of the classifier (§13 item 4: "`K` and `T` are exact checks"), and the tail set differs at `K = 1`, so cells are pooled within each `K` at the single `T = T_C2`.
2. **The `U_G` nominee does not depend on DSR availability.** P18-7: "every pre-lockbox mandatory gate is computed for every nominee regardless of the DSR or other gate outcomes, and a gate not computed counts as `UNAVAILABLE`". The development replication nominates by P18-4 (highest observed `S`, ties to the lowest id) whenever every `S` is finite. If some `S` is not finite, no gate can be computed, and the replication is a `U_G` event `NO_NOMINEE` (conservative).
3. **Both block rules run in every development replication** (§5 step 1 needs `P̂_0(E_f)` under each). At `K = 1` both rules give the same block, so the result is reused. **Cost, disclosed:** at `K ≥ 2` the Annex B bootstrap runs twice per development replication. If the §13 estimate assumed one evaluation, development costs more than estimated; the re-pilot measures it.
4. **`M` for tau** is the candidate manifest's test count (§5 `M_max`, conservative): 3 tests per family-agnostic cell (error, DSR availability, `U_G`). Q5 and QJ add their tests when their generators are built (item 2).
5. **`z_crit` search range** is the 0.001 grid on [0, 20]. If no grid value qualifies, the report says so (`z_crit: null`), which is §5 step 6 "no qualifying choice".
6. **Cap rule** compares the 90% UCB of the `BLOCK_LENGTH_CAPPED` rate with τ_DSR(20k)/4. At 12,000 development replications one capped replication already demotes a cell (UCB 3.24·10⁻⁴ > 3.0·10⁻⁴). This follows the accepted text; it is worth the owner's attention because the re-pilot will show how often capping occurs.
7. **The selection script runs the start gate** (pinned runtime) before deciding, because the targets use `lgamma`/`exp`, and recomputes nothing else.

## Not built in item 1

- Held-out namespaces (`d19-heldout-v1/v2`): they need the qualification object and the drand anchor (§4, §8).
- Q5 and QJ (per-family and joint tests), the coverage rule (needs the frozen manifest's O18-4 categories), and §5 step 5's joint plug-in diagnostic.
- The FA-1 governance item (canonical qualification cell ids) remains with the owner.

## Checks (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rundef.py tests/unit/test_calibration_chunks.py tests/unit/test_calibration_reduce.py tests/unit/test_calibration_binomial.py tests/unit/test_calibration_choices.py -q -p no:cacheprovider` (final code) | 0 | 100 passed in 321.72 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider --ignore=` the four calibration files above except choices (run during development; includes `test_calibration_choices.py` and `test_calibration_engine.py`) | 0 | 1813 passed, 9 skipped in 385.80 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 139 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py` | 0 | No issues in 67 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| `pwsh -NoProfile -File review/task6/verify_frozen.ps1` (bundled pwsh path as in earlier records) | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |

During development the first run of the new end-to-end test failed: running
development before the threshold run raised `FileNotFoundError` from
`chunks.verify`; repaired (clean `ChainError`, test
`test_verify_refuses_a_missing_chain`).
