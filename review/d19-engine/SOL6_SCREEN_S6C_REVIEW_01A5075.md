# §16 different-model review of the screen slice S6c (G-14) at 01a5075

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a148a7-cbbe-7922-a6e7-fd1ce92d3d8c)
- Date: 2026-10-17
- Prompt: `SCREEN_S6C_REVIEW_PROMPT.md`
- Limitation (the reviewer's own): its shell failed; packet only.
- Findings: S6C-R1 (High), S6C-R2 (Medium). Stream, rejection draw, shift, embargo order, IC rows, logistic score and grid encoding match. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for head `01a5075`.

- **S6C-R1 — High — `calibration/screen.py:spearman_ic` and `walk_forward` prediction collection.** A model can return a `NaN` prediction without raising. `spearman_ic` then ranks that `NaN` and can return a finite correlation, so `screen_gates` can mark G-14 available even though the IC is invalid. For example, one `NaN` among otherwise varying predictions passes the constant-input check. Reject nonfinite predictions before ranking and test that G-14 becomes unavailable.

- **S6C-R2 — Medium — `tests/unit/test_calibration_screen.py:test_a_null_pipeline_shifts_labels_circularly_within_each_window` and `_fast_g14`.** The shift spy uses a 30-day window, so it observes only refit window 0. Most pipeline tests use three draws. A regression that reuses `w=0` in later windows, or evaluates only three null pipelines in production, would pass these tests. Add a multi-window integration assertion and a count assertion for the nominee plus all 500 draws.

The reviewed code otherwise matches the specified stream fields and rejection draw, permits `n_w = 2h`, shifts retained labels with `np.roll(..., -offset)` after embargo from original labels, pools BTC IC rows with `t + H < w1`, uses continuous targets and logistic probabilities, and does not compute PASS/FAIL. The reference-grid construction is `d`-major with the specified canonical hash structure.

I could not run pytest or obtain exact numeric line numbers: the local shell failed before starting any process. The reported 146 passing tests are supplied validation, not independently verified here. No files were modified.