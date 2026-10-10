# Review prompt: D-19 engine item 2b step 1, Q5 cells wired into the run

You are an independent, adversarial reviewer, not an authority. Your command
runner does not work in this environment, so everything is attached below:

- the diff;
- the HEAD text of `scripts/d19_run.py`, `scripts/d19_run_definition.py`,
  `calibration/rules.py` (`family_label`, `draw`) and the changed parts of
  `calibration/semi.py`, `calibration/generator.py` and `calibration/rundef.py`;
- the new tests;
- the accepted preregistration §2, §3.2, §3.4, §3.5 and §8;
- the accepted rule-library proposal, revision 3.

Review from the attachments only, and say so.

**Scope.** Q5 cells (laws `semi-trend` and `semi-vol`, one family per cell)
run in the threshold and development namespaces. Two things are deliberately
**not** in scope:

- QJ (`semi-joint`) stays refused by `cells_from_manifest`, until its
  cycle-level tests (§1, §6: `P_0(E)` and `U_proc^R` over both families) are
  counted in step 2;
- `d19_choose` still refuses any law outside the agnostic set (I1-4).

Check:

1. **Seeds (§8).**
   - A Q5 replication uses the outer seed's `"market"` stream for the
     stationary bootstrap and its `"sign"` stream for the block signs. A
     synthetic cell still uses `"market"` and `"columns"`, unchanged.
   - The inner Annex B family seed's `family_id` is the family label
     (`trend` or `vol`), and `"agnostic"` for Q1-Q4.
2. **Data boundary and identity.**
   - The run definition records the source identity: both manifest hashes,
     the SHA-256 of the returns' bytes, the row count and the left-out count.
   - Every worker of a Q5 cell rebuilds the source from `--raw-root` and
     refuses, before any chunk, unless the identity is equal.
   - Q5 cells without `--raw-root` are refused at record time and at run
     time.
   - Can a Q5 chunk be computed from data other than the recorded data?
3. **Behaviour unchanged for Q1-Q4.** The synthetic draws, the reference
   vectors and the job tuples all stay as they were.
4. **The R-5 warm-up and `v̄`.** `v̄` is computed from the whole source on
   every draw. Is that correct per revision 3, and deterministic?
5. **What is still open.** Is anything here inconsistent with §3.5? In
   particular, the thresholds are pooled per K across agnostic and Q5 cells
   (the existing `reduce.pooled`).
6. **Whether the tests prove what they claim.**

Output a complete review record in markdown, ready to commit verbatim. It
should give:

- a title;
- the reviewer model metadata, as you observe it;
- the commit reviewed, as given;
- the scope;
- the commands run (none possible);
- a verdict: ACCEPT, FIX or UNSOUND, for pilot use;
- findings with stable IDs I2BW-1, I2BW-2, ..., each with its severity,
  file:line, a concrete failure scenario and a proposed repair.

Mark anything that would change the accepted preregistration as a proposal
for the owner.

## Checks reported by the drafter (2026-10-11, Windows local venv, Python 3.14.7)

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest` the eight calibration files `-q -p no:cacheprovider` | 0 | 177 passed in 1250.48 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those eight files | 0 | 1801 passed, 9 skipped in 588.89 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 144 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_run_definition.py scripts/d19_choose.py` | 0 | No issues in 70 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |

mypy on `tests/unit/test_calibration_rundef.py` reports 7 errors. All 7 were present before this change: the same count appears with the change stashed. That file is outside the gate's mypy scope.
