# Review prompt: D-19 screen slice S6c (G-14) at the head carrying this prompt

You are an independent adversarial reviewer working read-only, not an authority. This is a §16 review of `calibration/screen.py`. Everything is attached; if your shell works you may read the repository and run `python -m pytest -q tests/unit/test_calibration_screen.py`, but do not modify files.

Check the S6c part (from "S6c: G-14": `g14_draw`, `g14_grid_sha256`, `midranks`, `spearman_ic`), the null-pipeline branch of `walk_forward` and the G-14 block of `screen_gates` (`g14_check`, the new `trial_seed` / `window_id` parameters, `GATES`) against Annex C rev 4 C-12, the READY design `SCREEN_S6_DESIGN.md` revision 4 (WF-7, WF-8) and the owner decisions (S3R-R3: G-14 for logistic models; S6D-R6: zero target is class 0). Assess readings G14-1..G14-5. In particular:
- the stream bytes (purpose, asset, cost string, window id, trailing `d, w`), the offset formula and the `NO_SHIFT_RANGE` boundary;
- the circular shift (`np.roll(fit_y, -offset)` must equal `label[(r + offset) mod n_w]`), applied within each window after purge and embargo, with the embargo computed from original labels;
- the IC: one pooled Spearman IC per pipeline over the BTC baseline's 00:00 window decisions with `t + H < w1`, midranks against the continuous target, `predict_proba[:, 1]` for logistic; constant inputs and failures as unavailability;
- that the nominee and all 500 draws must give an IC for G-14 to be available, and that PASS/FAIL is not computed;
- the reference vectors' encoding (`sha({"grid": [[d, w, offset, model_seed], ...]})`, `d`-major);
- that the tests (stream formula, boundary, frozen vectors, midranks, the circular-shift spy, N/A without a model) would catch a broken implementation. The tests patch `G14_DRAWS` to 3 for speed; production uses 500.

Out of scope: accepted slices; the S6a/S6b repairs (their own re-review); the driver (S7) and the cost pilot (S8).

Verdict ACCEPT or FIX. Findings get stable IDs S6C-Rn with severity, file:line and a concrete failure scenario.
