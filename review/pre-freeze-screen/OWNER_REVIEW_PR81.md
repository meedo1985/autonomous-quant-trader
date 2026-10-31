# Owner §16 PR review of PR #81 (pre-freeze screen.py change, D-20 Q5 and Q2(ii))

- PR: #81, branch pre-freeze-screen-q2-q5, reviewed head e035696 (Codex Sol final ACCEPT WITH NOTES, `SOL_CODE_RECHECK2_2E2C81E.md`; gate record `TASK_GATE.md`).
- Date: 2026-10-31.
- Asked, with options:
  1. "PR #81 changes calibration/screen.py before the freeze, as you decided in D-20 (Q5 and Q2(ii)). (1) The chosen strategy's model fit uses the protocol seed instead of 0. (2) A helper prices the last hour at its own close, so no run reads data after its window. With default settings the screen gives bit-for-bit the same results as before; a test checks this against the old file. Codex Sol reviewed it over 5 rounds and its final verdict accepts it for the freeze. All tests and checks pass. Do you accept this change?"
  2. "Merge PR #81 into main? Merging changes nothing on the server and doesn't touch the running development run. Afterwards two server steps are still needed before the freeze: redo step G0 at the new commit, and run the one test that only works on the pinned image. I'll give you a Notepad file for those."
- Owner's answers, verbatim (the option labels chosen): 1. "Yes, accept"; 2. "Yes, merge".
- Note on question 1's "bit-for-bit the same results": T1 shows this for the four affected functions on the test fixtures, on the Windows host. The pinned-image paths-vector test (T1b) has not run yet; it is one of the two server steps named in question 2.
- GitHub does not let the owner approve a PR opened from his own account, so the review is recorded here.
- Recorded by the AI from the owner's answers. The AI did not write the review.
- Merge condition: CI green on the head that carries this record. G0 redo and T1b in the pinned image are separate owner steps before step G.
