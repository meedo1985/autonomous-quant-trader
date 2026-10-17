# Review prompt: D-19 screen slice S4b (trial runs; G-3, G-5, G-6, G-7) at the head carrying this prompt

You are an independent adversarial reviewer working read-only, not an authority. This is a §16 review of `calibration/screen.py`, which the qualification object binds by its bytes. Everything is attached; if your shell works you may read the repository and run `python -m pytest -q tests/unit/test_calibration_screen.py`, but do not modify files.

Check the S4b part of `calibration/screen.py` (from "S4b: trial runs") and the changed TI-2 sentence against prereg §7.2 ("Runs", "Outcome"), Annex C rev 4 C-0, C-3, C-5, C-7 and C-10 (1), using the accepted S2 runner (`aqt.backtest.event_contract`), the S4a feature columns, `aqt.benchmarks.canonical.vol_target_exposure` and the R-8 metric code. Assess readings RN-1..RN-7. In particular:
- RN-3 changes the signal's call form from whole arrays to one call per hour with the trial's own state, so that look-ahead is impossible by construction. Is that faithful to C-10 (1), and does it lose anything a later gate needs?
- RN-2 refuses sizing estimators other than EWMA_168h (`SIGMA_UNBOUND`) because no hourly definition of EWMA_72h/EWMA_336h/HAR_RV/GARCH_1_1 is bound. Is refusing correct, rather than inventing a definition?
- Instant and row indexing: decision at instant j reads bar j - 1; G-6 reads bar j - 2 for s, the sizing estimator and the overlay, and never lags the benchmark; window decisions start at w0; one extra hour for the last segment.
- Daily returns from 00:00 equity marks, E-IMPROV via `paired_sharpe_statistics`, drawdown on the hourly equity path, net return.
- Availability semantics: what makes each gate UNAVAILABLE here, whether an unavailable G-3 is correctly carried into G-5..G-7, and whether anything that the annex makes unavailable is missed, or anything that is only a FAIL is wrongly treated as unavailability.
- Whether the tests would catch a broken implementation.

Out of scope: S1, S2, S3, S5 (accepted), S4a (in its own review), G-8, G-11 runs, G-14 and the driver.

Verdict ACCEPT or FIX. Findings get stable IDs S4B-Rn with severity, file:line and a concrete failure scenario.
