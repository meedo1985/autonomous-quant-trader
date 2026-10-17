# Review prompt: D-19 screen slice S4c (G-8) at the head carrying this prompt

You are an independent adversarial reviewer working read-only, not an authority. This is a §16 review of `calibration/screen.py`. Everything is attached; if your shell works you may read the repository and run `python -m pytest -q tests/unit/test_calibration_screen.py`, but do not modify files.

Check the S4c part (from "S4c: G-8") and its use in `screen_gates` against Annex C rev 4 C-8, the frozen protocol plateau lines (l.254-265: tunable and structural dimensions, neighbour inclusion, pass rule) and the owner's decision `OWNER_DECISION_G8_RULE_SETTINGS.md` (rule settings count). Assess readings PL-1..PL-4. Look for:
- a dimension wrongly included or excluded (tau, sigma, categorical strings, booleans, `model.<name>`, single-value dimensions), and whether the protocol's "the three EWMA half-lives may be treated as ordered numeric neighbors only within the EWMA subclass" needs handling now (the screen refuses every sizing estimator but EWMA_168h, RN-2);
- the ordering and the +/-1-step neighbours (by exact decimal value; edges; equal numbers);
- neighbour trials: one dimension at a time, the same `signal_params` / `model_params` path, still valid declarations;
- availability: `NA` without a dimension; `UNAVAILABLE` if the point's or any neighbour's baseline BTC E-IMPROV cannot be computed; whether anything else in C-8 step 2 is missed;
- whether the tests would catch a broken implementation.

Out of scope: accepted slices (S1, S2, S3, S4a, S4b, S5) except where S4c changes them, G-11 runs, G-14 and the driver.

Verdict ACCEPT or FIX. Findings get stable IDs S4C-Rn with severity, file:line and a concrete failure scenario.
