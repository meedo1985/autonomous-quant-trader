# Review prompt: D-19 engine item 2b, the rule libraries (`calibration/rules.py`)

You are an independent, adversarial reviewer, not an authority. Your command
runner does not work in this environment, so everything is attached:

- the diff;
- the HEAD text of `calibration/rules.py`, `tests/unit/test_calibration_rules.py`
  and `calibration/semi.py`;
- the accepted proposal, revision 3, with the owner's decision record;
- `reaches_rebalance_band` and the canonical conventions it reuses.

Review from the attachments only, and say so.

Check the code against the accepted proposal, revision 3. The proposal is
binding and is not under review, but name any place where it is itself
inconsistent.

1. Does every rule, R-2 and R-3, implement the stated equations exactly? Cover
   SMA, refresh days, hold, EWMA, `GARCH_1_1` and its H-day forecast, `HAR_RV`
   and its iteration, the cold start (`r_s² = v̄` for s < 0), sizing, the
   v = 0 case, and τ.
2. Causality: does row t use only r_0 .. r_{t−1}? Is the prefix-invariance
   test strong enough to catch a one-day look-ahead in each rule?
3. The band: starting from 0, gating every day, moving fully to the target,
   via `reaches_rebalance_band`.
4. R-4: the index map, the trial identities table, and that the first K rules
   are used.
5. R-6 / QJ: one path and one sign sequence, trend columns first.
6. `reference_variance`, with ddof 0 and its guards, and the price guard.
7. Whether the tests prove what they claim.

State what is **not yet built**:

- wiring the Q5/QJ cells into the run definition and the driver, including the
  §8 stream use and source loading from `raw_root` on the server;
- the per-family test counting and the coverage categories.

Do not count these as defects of this diff.

Output a complete review record in markdown, ready to commit verbatim:

- a title;
- the reviewer model metadata, as you observe it;
- the commit reviewed, as given;
- the scope;
- the commands run (none possible);
- a verdict: ACCEPT, FIX or UNSOUND, for pilot use;
- findings with stable IDs I2BL-1, I2BL-2, ..., each with its severity,
  file:line, a concrete failure scenario and a proposed repair.

## Checks reported by the drafter (2026-10-11, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest` the eight calibration files (`rundef`, `chunks`, `reduce`, `binomial`, `choices`, `generator`, `semi`, `rules`) `-q -p no:cacheprovider` | 0 | 164 passed in 985.34 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those eight files | 0 | 1801 passed, 9 skipped in 838.16 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 144 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py tests/unit/test_calibration_rules.py` | 0 | No issues in 70 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |

Mutation check, not committed: when the trend comparison is changed to use `price[t]` (a one-day look-ahead), `test_every_rule_is_causal[trend]` fails. When the EWMA update is changed to use `r[t]`, the causal and EWMA tests fail. With the code restored, all 15 tests pass.
