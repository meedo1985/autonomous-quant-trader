# Review prompt: D-19 screen slice S5b (G-11 runs) at the head carrying this prompt

You are an independent adversarial reviewer working read-only, not an authority. This is a §16 review of `calibration/screen.py` and of a small change to the accepted S2 runner `src/aqt/backtest/event_contract.py`. Everything is attached; if your shell works you may read the repository and run `python -m pytest -q tests/unit/test_calibration_screen.py tests/unit/test_event_contract.py`, but do not modify files.

1. **S2 change (EC-4):** `run_event_contract` accepts an optional precomputed `sigma_bps` (the series' own cost-model volatility), refusing one of the wrong length, so the screen does not recompute it for G-11's 500 runs per path. Check that results are identical and that nothing else in the accepted contract changed.
2. **S5b (from "S5b: G-11 runs", `g11_targets`, `g11_check` and the G-11 block of `screen_gates`, the new `g_days` parameter, `GATES`):** check against Annex C rev 4 C-10 (2)-(7) and the accepted S5 shifts. Assess readings GR-1..GR-3. In particular: the rotation `s'_h = s_((h + 24 k_i) mod 24T)` over the window's hours; re-sizing with `sigma_hat` at the real hour; the overlay re-run afresh per draw on the market at the real hour; every run starting flat from `w0`; the shared benchmark leg at 1x; the availability order (candidate first, then the shift range, then each draw); `constant_signal` as frozen N/A unless `CLASS_MISMATCH`; and whether anything in C-10 (6) is missed. Also check the features/volatility cache in `prepare` and the shared `inputs` / `contract` helpers that the other gates now use.
3. Whether the tests (500 draws in order on a 559-day window, the rotation formula, N/A and stream requirements, identical results with a precomputed sigma) would catch a broken implementation.

Out of scope: other accepted slices except where S5b changes them; the driver (S7) and the cost pilot (S8).

Verdict ACCEPT or FIX. Findings get stable IDs S5B-Rn with severity, file:line and a concrete failure scenario.
