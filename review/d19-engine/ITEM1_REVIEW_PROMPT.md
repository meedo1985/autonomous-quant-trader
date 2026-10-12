# Review prompt: D-19 engine item 1 at 3a84b86

You are an independent, adversarial reviewer (not an authority) of the
repository `D:\PMP-programs-for-sharawi\autonomous-quant-trader`, branch
`d19-calibration-engine`, commit `3a84b86` (diff against `8103052^`, which
includes the binomial commit `8103052`). The implementer was Claude Opus 5.5.

READ-ONLY: no edits, commits, or git state changes (no `git stash`); no
network; no server; no calibration runs. The laptop has ~8 GB RAM: run only
focused tests, e.g. `tests/unit/test_calibration_binomial.py`,
`test_calibration_choices.py`, `test_calibration_reduce.py`,
`test_calibration_chunks.py` (fast), and if needed single tests of
`test_calibration_rundef.py` with `-k` (each driver test takes ~1 minute).

Read first: `review/d19-engine/ITEM1_DEVELOPMENT_AND_CHOICES.md` (what was
built, the seven interpretations, what is not built), then the accepted
preregistration: `git show docs/d19-recommendation:review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md`
(§2, §3.2 cap rule, §3.5, §5, §6, §8, §13 items 2-4 and 6), and Annex A
P18-3..P18-7: `git show docs/d19-recommendation:review/governance-statistics-amendment/s4-amendment-draft/ANNEX_A_SELECTION_RULE.md`.

Check, against the accepted text:
1. `calibration/binomial.py`: exact Clopper-Pearson, critical count, tau
   definitions and numerics (bisection, log-space sums, edge cases, large N).
2. `calibration/reduce.py` and development thresholds: pooling per K (§3.5
   item 2), bit-exact decode, completeness of the threshold chains.
3. `scripts/d19_run.py` dev replication vs §2 and §8: seeds and namespace,
   family seed fields, classifier position and thresholds, both block rules,
   z_f* storage, the U_G nominee rule (interpretation 2 vs P18-4/P18-7),
   K = 1 reuse, what is recorded.
4. `calibration/choices.py` and `scripts/d19_choose.py` vs §5 steps 1-3 and
   §13 item 3: block-rule choice and tie, which replications count as DSR
   unavailability, the cap rule, the escape and demotion, M and tau (each
   test at its N_i, including an escape cell's error tau at 40k), the z_crit
   grid/search and the P18-6 decimal-to-binary64 comparison, the final
   thresholds over qualifying cells.
5. Each of the seven interpretations: correct, defensible, or wrong?
6. Anything that could make a development result non-reproducible or not
   bound to the run definition, and whether the tests prove what they claim.

Output a complete review record in markdown, ready to commit verbatim:
title, reviewer model metadata (as you observe it), commit reviewed, scope,
commands run with results, verdict (ACCEPT / FIX / UNSOUND for pilot use of
the development namespace and choices), and findings with stable IDs
I1-1, I1-2, ... (severity BLOCKER / NON-BLOCKING / QUESTION, file:line,
concrete failure scenario, proposed repair; mark any finding that would
change the accepted preregistration as a proposal for the owner).
