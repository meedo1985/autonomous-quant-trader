# Review prompt: D-19 engine item 2b (semi-empirical infrastructure and rule-library proposal)

You are an independent, adversarial reviewer (not an authority). Your command
runner does not work in this environment, so everything is attached below:
the diff of item 2b, the HEAD text of `calibration/semi.py`,
`calibration/generator.py` and `tests/unit/test_calibration_semi.py`, the
proposal `ITEM2B_RULE_LIBRARY_PROPOSAL.md`, the accepted preregistration
§3.1-§3.4, §8 and §13, and the frozen protocol's exposure-mapping, partition
and trial-accounting sections. Review from the attachments only and say so.

Part A, code (`calibration/semi.py`, the `benchmark_exposure` refactor):
1. Partition safety: can any non-exploration bar be read, or a manifest be
   accepted outside the exploration window? Is the check before the load?
2. The stationary bootstrap, the block sign process (iid fair, independent
   of the path, first block at day 0, shared across columns) and whether
   E[X] = 0 holds exactly as §3.4 claims; draw order and determinism.
3. The column construction X = s(e − e^b) r, C = b + X, the benchmark on the
   resampled path, warm-up handling, and the refactor (behaviour unchanged).
4. The daily-return rule (also proposal item R-1) and the left-out count.
5. Whether the tests prove what they claim.

Part B, the proposal (a design for the owner; judge soundness, not taste):
6. Is a definition needed at all, and do R-1..R-6 fit the accepted text and
   the frozen protocol (budgets, vol targets, allowed estimators, trial
   unit)? Name any conflict.
7. Causality of every rule; the HAR/GARCH frozen-parameter simplification;
   the exact-duplicate EWMA horizons; the random K-subset (R-4) versus a
   fixed subset, including its effect on what a cell certifies and on the
   §3.6 mapping.
8. Anything that would make the Q5/QJ null not exact, or the cells
   unrepresentative of declarable C2 designs.

Output a complete review record in markdown, ready to commit verbatim:
title, reviewer model metadata (as you observe it), commit reviewed (as
given), scope, commands run (none possible), a verdict for part A (ACCEPT /
FIX / UNSOUND, for pilot use) and a recommendation for part B (SOUND /
SOUND WITH FIXES / UNSOUND, as advice to the owner), and findings with
stable IDs I2B-1, I2B-2, ... (severity, file:line or proposal item,
concrete failure scenario, proposed repair; mark anything that would change
the accepted preregistration as a proposal for the owner).
