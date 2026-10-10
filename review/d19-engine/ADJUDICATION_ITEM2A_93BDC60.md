# Adjudication of the GPT-6 Sol review of D-19 engine item 2a at 93bdc60

Review: `review/d19-engine/SOL6_ITEM2A_REVIEW_93BDC60.md` (FIX for pilot
use; I2A-1..I2A-5; from a packet). Adjudicated and repaired by Claude Opus
5.5 (`claude-opus-5-5`) on 2026-10-10. Not yet re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| I2A-1 High | AGREE, repaired (pre-existing code) | `generator.market` makes ε itself AR(1) for `ar0.2`/`ar0.5` (§3.1 lists AR(1) among the laws of ε), from a stationary N(0,1) start with the 500-day burn-in, on the market stream. Test `test_an_ar_market_is_ar1` (lag-1 autocorrelation 0.5, unit variance). |
| I2A-2 High | AGREE, repaired (pre-existing code) | GARCH(1,1) now draws one t5 shock sequence and uses it both for the return and the next variance: σ²ₜ₊₁ = ω + a(σₜεₜ)² + bσₜ²; `market` returns (σ, ε) together and the common σ still scales the columns. Test `test_garch_variance_is_driven_by_the_observed_return` (the recursion holds to 1e-12 on the emitted series). |
| I2A-3 Medium | AGREE, repaired | Every market law runs 500 days and discards them (§3.1 "every series"); iid laws discard 500 draws. Test `test_iid_markets_discard_the_burn_in` (five laws). |
| I2A-4 Medium | AGREE, carried to engine item 3 | The qualifying grid (law × dependence × K × T per group) belongs to the frozen cell manifest; it will be enforced there, at the qualification boundary, with a rejection test for an out-of-grid Q2 cell. Qualification runs stay refused in code (`rundef.run_plan`) until that manifest exists, so the generator's broader acceptance cannot reach a qualification run now. |
| I2A-5 Medium | AGREE, repaired | Tests added: draw order U0, U1, W reproduced from a controlled generator (`test_skew_t_draw_order_is_u0_u1_w`); α_s checked by independent quadrature of the skew-normal and χ² densities, agreeing with skewness 1 to 2e-4 (`test_alpha_s_by_independent_quadrature`); the Q2m and Q4 markets asserted Gaussian with constant σ; Q4 cross-column independence; reference case `refvec-k5-mixed-ar` added (`skewt+` shares every code path with `skewt-` but the sign of α). The note's "exchangeable" wording is corrected. Population, not sample, mean and variance are the exact ones; the tests treat samples with tolerances. |

These repairs change the deterministic market draws of every law (the
burn-in and the GARCH/AR repairs), so the reference vectors measured on the
server will differ from any measured before; none has been recorded for a
run yet (the run definition is recorded on the server before the threshold
run).

No calibration was run.

## Checks after repair (2026-10-10, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_generator.py -q -p no:cacheprovider` | 0 | 22 passed |
| `.venv/Scripts/python -m pytest` the six calibration files (`rundef`, `chunks`, `reduce`, `binomial`, `choices`, `generator`) `-q -p no:cacheprovider` | 0 | 133 passed in 1036.38 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those six files | 0 | 1801 passed, 9 skipped in 925.35 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 140 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py` | 0 | No issues in 67 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |
