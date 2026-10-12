# Review prompt: D-19 item 2b step 2 (test count M, coverage rule, QJ cells)

You are an independent adversarial reviewer working read-only. You are not an authority, and every finding will be adjudicated with evidence. Base the review on the attachments, and say so wherever you could not verify something.

Attachments:
- the step 2 plan: `ITEM2B_STEP2_PLAN.md`;
- the owner's readings: `OWNER_DECISION_ITEM2B_STEP2_READINGS.md`;
- the accepted preregistration excerpts: §1 claims, §3.2 groups and coverage, §5, §6, §8 and §13 rev 7g;
- the diff of the step 2 commits;
- the text of the changed files at the reviewed commit.

The step contains three slices:
1. **M.** `choices.enumerated_tests` counts 3 tests per agnostic or Q5 cell and 8 per QJ cell (3 trend, 3 vol, 2 joint). `d19_choose` accepts Q5 and QJ cells.
2. **Coverage.** `choices.categories` and `choices.coverage` implement the O18-4 table with the owner's readings, minus "unequal T" per O18-4-T. `qualifies` = qualifies before coverage AND every category has a qualifying cell.
3. **QJ.** The generator accepts `semi-joint` at K in {2, 20}. `rules.draw` builds one shared path with one sign stream for both libraries, and `rules.families` splits it into a trend half and a vol half. The driver stores one record per family:
   - **Threshold records:** diagnostics per family on the family's own K columns; the per-family sets enter the T pool.
   - **Development records:** each family uses its own family seed, and `U_G` uses the shared outer seed.

   In `choices`:
   - the two families qualify or are demoted together, at the larger N;
   - the joint `U_proc^R` 90% UCB is checked against τ(0.01) with the 20k/40k escape, and the cell is demoted if it fails;
   - `z_crit` must also satisfy the joint `P_0(E)` limit, τ(0.05), where E means either family passes.
   - **Disclosed:** at M ≈ 322 and 12,000 development replications, neither joint limit can bind once each family passes.

Questions:
1. Does each slice implement the cited preregistration clauses and the owner's readings exactly? Name anything that is under-counted or over-counted. Is anything anti-conservative?
2. **QJ:** are the halves truly the same path, signs and benchmark? Are the per-family seeds and the shared `U_G` seed as decided? Is the pairing of the two families' replications by index correct? Is the joint event definition correct: E as either family passing, and `U_proc^R` as either family's DSR or classifier or `U_G` event? Is the escape and demotion logic for the joint check right?
3. **Coverage:** are any categories missing or wrong? Does a demoted family of a QJ cell correctly remove `joint_generator`?
4. **Records:** can the QJ record shape be forged or mis-decoded by `d19_choose`? Does `choices.consistent` run per family?
5. **Tests:** are the tests sufficient? Are any vacuous? Note that the joint checks are shown only with tight τ.

Output:
- Put your model metadata at the top.
- Give a verdict for pilot use: ACCEPT or FIX.
- Number findings I2BS2-n. Give each one a severity, a file:line, a failure scenario and the minimal fix.
- Mark any finding that needs an owner decision.
