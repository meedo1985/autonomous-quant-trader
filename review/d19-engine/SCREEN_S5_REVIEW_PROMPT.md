# Review prompt: D-19 screen slice S5 (G-11 shifts) at the head carrying this prompt

You are an independent adversarial reviewer working read-only, not an authority. Everything is attached; if your shell works you may read the repository and run `python -m pytest -q tests/unit/test_calibration_screen.py`, but do not modify files.

Check the S5 part of `calibration/screen.py` (from "S5: G-11 shifts") against Annex C rev 4 C-10 (3) (shifts, stream, draws, availability, reference vectors, and "Inside the D-19 screen") and the R-8-bound `aqt.metrics.statistics` constants and `bootstrap_indices` draw it must match. Assess readings GS-1..GS-5. Look for: any byte of the seed material that differs from the annex (types, order, separators, the "1.0" string, the window id), an off-by-one in `P = [m, ..., T - m]` or the availability rule `T - 2m >= 499`, a draw that differs from `bootstrap_indices`' rejection sampling, a seed collision with the S1 path seeds or other streams, and whether the tests (an independent formula check, an independent draw, boundary cases, frozen vectors) would catch a broken implementation. Out of scope: S1 and S3 (accepted) and the G-11 runs themselves (draw `i`, statistic, pass rule), which need the C-6 runner.

Verdict ACCEPT or FIX. Findings get stable IDs S5-Rn with severity, file:line and a concrete failure scenario.
