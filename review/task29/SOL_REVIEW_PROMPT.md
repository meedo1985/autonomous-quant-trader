# Review prompt: Task 29 forward paper mode (section 16 different-model review)

You are the independent different-model reviewer that Constitution §16
requires. You are not an authority: you may not merge, approve for the owner,
or decide owner questions. Do not edit, commit or push. Do not use the
network. Do not read confirmation or lockbox data. You may run the tests and
in-memory Python with `.venv/Scripts/python.exe`.

## Scope

Diff `main..task29-forward-paper` at the commit named in the request:
- `src/aqt/app/forward.py` (new);
- `scripts/run_forward_paper.py` (new);
- `configs/forward_paper.example.toml` (new);
- small hooks in protected code:
  - `SimulatedExchange(orders=...)`;
  - `reconcile.expected_balances`;
  - `Observation.scheduled` in `paper_loop.py`;
- `tests/integration/test_forward_paper.py`.

Authority for the task: `review/roadmap/OWNER_ANSWER_QC_2026-10-04.md`.
Scope and acceptance criteria: `review/roadmap/ROADMAP_2_PROPOSAL.md`,
Task 29.

## Questions

1. **Correctness.** Do forward steps give the same decisions as a replay of
   the same bars? Check the window rule: `start` is the hour after the last
   save, and `end` follows the last closed bar. Look for an off-by-one, a
   double-run or a skipped hour, especially around journal save times
   (`busy_until`, owner commands, FREEZE, HALT) and the startup check.
2. **Safety.**
   - Is rebuilding the simulated venue from the journal sound? It uses the
     reconciled balances plus every order since. An unknown outcome refuses
     the step.
   - Could the rebuild hide a real discrepancy that reconciliation is meant
     to catch?
   - Is every refusal logged?
   - Do order ids stay unique across steps?
3. **Health semantics.** In forward mode the loop-lag check is measured from
   when the newest fill bar closed, and missed hours are reported once as a
   CRITICAL `LOOP_LAG` and then run as a replay would run them. Does this meet
   "a missed hour is a health breach, never a silent skip"? Does it weaken any
   existing check on the replay path?
4. **L-02.** Is the effective-decision count correct, and does it state its
   method as `LOSS_BOUND_DEFAULTS.md` §3 requires? It values equity at each
   00:00 UTC from journal balances and that hour's close, then applies the
   Task 12 Newey-West estimator with H = 24. Check the hand-computed test.
5. **Boundaries.** Confirm the following:
   - no credential is read;
   - only public market data is fetched, and only by the script;
   - the simulator only;
   - the import contracts hold;
   - nothing on the research or lockbox side is reached.

Verdict: ACCEPT, FIX (with findings), or REJECT.

## Output

Start with your model name and family as you know them, the commit you
checked, and the verdict. Then give a findings table with IDs `S29-1, ...`.
Each row gives the severity (BLOCKER / MAJOR / MINOR), the location, the
scenario, the evidence and a proposed fix. List the exact commands you ran and
their results. End with five plain-language lines for the owner.
