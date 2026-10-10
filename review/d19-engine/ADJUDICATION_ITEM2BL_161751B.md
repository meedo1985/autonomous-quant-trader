# Adjudication of the GPT-6 Sol review of the item 2b rule libraries at 161751b

**Review:** `review/d19-engine/SOL6_ITEM2B_LIBRARIES_REVIEW_161751B.md`. The verdict was FIX for pilot use, with findings I2BL-1..I2BL-3. The review was made from a packet.

The reviewer found that the equations, the timing, the band, the index map, the trial identities and the QJ composition match the accepted proposal revision 3. All three findings concern the tests.

Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-11.

| ID | Decision | Repair and evidence |
|---|---|---|
| I2BL-1 High | AGREE, repaired | New test `test_every_target_ignores_its_own_day[trend/vol]` covers all 54 rules. It checks the **direct target**, not the band-gated exposure. At each cut it sets r_t to +60%, −60% and 0, and requires targets 0..t to be identical across the three. The cuts are days 0, 1, 22, 23, 200 and 250, plus each trend rule's first two refresh days after its L prices exist (days 203 and 210 for L = 200, H = 7). The earlier held-exposure test is kept. **Mutation check (not committed):** a look-ahead `price[t]` planted only in the L = 200, H = 7 rules fails this test; with the code restored, all tests pass. |
| I2BL-2 Medium | AGREE, repaired | New test `test_the_accepted_table_and_constants_are_pinned[trend/vol]`. It pins the 27-entry index order and every trial identity against a table written out independently from the proposal. It also pins the SMA lengths, the horizons, τ, the EWMA half-lives, the GARCH α and β, and the HAR β, c and lags. |
| I2BL-3 Low | AGREE, repaired | The source-guard test now covers BTC −1, NaN and +inf, and ETH NaN and −inf. New test `test_a_non_finite_price_index_is_refused` uses a path whose price index overflows. Numpy's overflow warning inside that guarded product is silenced, because the very next line checks the result. |

**Proposal-consistency notes from the review:**

- *`v̄`:* revision 3 says "population variance (ddof 0)" and "the mean of its squares". The code implements the mean of squares, which is the formula the proposal states explicitly. The two differ only by floating-point rounding of the demeaned mean.
- *The DRAFT header* in the proposal is stale. The accepted text is revision 3 as of `52316cf`, per `OWNER_DECISION_ITEM2B_RULE_LIBRARIES.md`. The accepted file is left unedited.

No calibration was run.

## Checks after repair (2026-10-11, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_rules.py tests/unit/test_calibration_semi.py -q -p no:cacheprovider` | 0 | 36 passed |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 144 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py tests/unit/test_calibration_rules.py` | 0 | No issues in 70 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |

The rest of the suite and the frozen-file check were not rerun. The only code change is an `np.errstate` guard in `calibration/rules.py`, and no module other than its test imports `calibration.rules`. The full gate last passed at `161751b`.
