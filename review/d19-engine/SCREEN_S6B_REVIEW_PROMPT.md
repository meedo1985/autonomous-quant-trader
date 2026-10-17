# Review prompt: D-19 screen slice S6b (model trials in the screen runs) at the head carrying this prompt

You are an independent adversarial reviewer working read-only, not an authority. This is a §16 review of `calibration/screen.py`. Everything is attached; if your shell works you may read the repository and run `python -m pytest -q tests/unit/test_calibration_screen.py`, but do not modify files.

Check the S6b part (from "S6b: model trials in the screen runs": `model_warmup_hours`, `model_column`) and its use in `screen_gates` against the READY design `SCREEN_S6_DESIGN.md` revision 4 (WF-1..WF-6) and Annex C rev 4 C-7 (2). Assess readings MR-1..MR-4. In particular:
- MR-1: a model trial's ETH run (G-3) fits its own walk-forward on ETH rows. Is that faithful to "BTC and ETH evaluated jointly inside the same trial", or should the BTC-fitted model predict ETH? Say whether this is a reading or the owner's to decide.
- MR-2: the nominee's model seed is 0, on the argument that every allowed configuration is deterministic. Check that argument against WF-5's fixed settings.
- MR-3: emission indexing (one prediction per 00:00 window decision, held until the next; the `model:<id>` column indexed like a feature column read at the run's lag), G-6 re-inference on features of the bar closing at `t - 1h` with refits and labels unlagged, and the cache that lets G-5 and G-7 reuse the baseline emissions.
- The rows: every 00:00 instant with a feature row and a realised label; training rows by `training_rows`; non-finite features and fit failures as unavailability.
- Whether the tests would catch a broken implementation.

Out of scope: accepted slices, the S6a repairs (their own re-review), G-14 draws (S6c), the driver.

Verdict ACCEPT or FIX. Findings get stable IDs S6B-Rn with severity, file:line and a concrete failure scenario.
