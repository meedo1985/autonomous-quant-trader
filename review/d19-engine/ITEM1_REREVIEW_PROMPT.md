# Re-review prompt: repairs of D-19 engine item 1 findings I1-1..I1-6

You are an independent reviewer (not an authority) of repository
`D:\PMP-programs-for-sharawi\autonomous-quant-trader`, branch
`d19-calibration-engine`, at its HEAD (check with `git rev-parse HEAD`). The
implementer was Claude Opus 5.5; the first review was by Claude Fable 5.1.

READ-ONLY: do not edit, create or delete files, commit, or change git state;
no network; no server; no calibration runs. If you can run tests, run only
fast ones: `tests/unit/test_calibration_choices.py`,
`test_calibration_reduce.py`, `test_calibration_chunks.py`,
`test_calibration_binomial.py`; otherwise judge tests by inspection.

Read `review/d19-engine/FABLE_ITEM1_REVIEW_3A84B86.md` (findings),
`review/d19-engine/ADJUDICATION_ITEM1_3A84B86.md` (decisions and checks),
`review/d19-engine/ITEM1_DEVELOPMENT_AND_CHOICES.md` (what item 1 is), then
`git diff 2b44fed HEAD -- calibration scripts tests`. The accepted
preregistration is at
`git show docs/d19-recommendation:review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md`
(§2, §3.2, §3.5, §5, §8, §9, §13 items 3, 4, 6).

Check:
1. Each of I1-1..I1-6 is closed as adjudicated; I1-7 and I1-8 dispositions.
2. `dsr.evaluate`'s new `columns` field: set correctly on every return after
   the block lengths exist, the same under both rules, no behaviour change
   to availability, z or the nominee.
3. The development record (`scripts/d19_run.py` `dev_replication`): every
   field, the `prereg` versus `anchor` split, bit-exactness.
4. `choices.consistent` and its use in `d19_choose`: can a record that does
   not follow from the thresholds or nominee rule pass, or a correct one be
   refused (rules 1-4 reasons, K = 1 shared records, NaN diagnostics)?
5. The margin check: are all decisive comparisons covered (cap, DSR, U_G
   20k/40k, the error limit around z_crit), is exit 3 fail-closed, can the
   report be mistaken for a pass?
6. The `AGNOSTIC_LAWS` guard and the recorded chain heads and
   `dev_thresholds_sha256`.
7. Whether the rewritten tests prove what they claim, and anything else the
   repairs introduce.

Output a complete review record in markdown, ready to commit verbatim:
title, reviewer model metadata (as you observe it), commit reviewed, scope,
commands run with results, verdict (ACCEPT / FIX / UNSOUND for pilot use),
findings with stable IDs I1R-1, I1R-2, ... (severity, file:line, concrete
failure scenario, proposed repair), or "no findings".
