# D-19: the C2 gap `g` and `T_C2` (proposal for review)

**Status:** PROPOSAL. The value is computed, not adopted. `g` is fixed only when the owner adopts it, before the threshold run (preregistration §3.1). Nothing here activates the §4 draft.
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-12.

**Rule.** §4 draft `gap_embargo.rule` ("ceiling, in whole days, of the maximum over declared horizons of max(label_horizon, target_autocorr_cutoff)"). The cutoff comes from the frozen `protocols/protocol_v1.yaml` `validation.embargo`: daily decision frequency, `ACF_with_Bartlett_bands`, alpha 0.05, max lag 4 × horizon in daily steps, "first lag after which no remaining lag is significant". The horizons are {24, 72, 168} h (`OWNER_DECISION_GAP_HORIZONS.md`).

**Readings G-1..G-5** are the AI's proposed readings of words the frozen text leaves open. They are listed in the `calibration/gap.py` docstring: data, target, decision time, ACF with missing days and Bartlett bands, and cutoff.

**Result** (`python scripts/d19_gap.py --raw-root data/raw`, BTCUSDT exploration manifest `5f92ec5041c9560d5f31bdb99b9686d7522697e65a8e61d514a0b0dda6d0b65b`, the same manifest the server recorded in FE-7):

| Horizon | Targets | Max lag | Cutoff | Gap (days) |
|---|---|---|---|---|
| 24 h | 1,592 | 4 | 4 | 4 |
| 72 h | 1,588 | 12 | 5 | 5 |
| 168 h | 1,584 | 28 | 7 | 7 |

**`g = 7`, so `T_C2 = 1,240` days.**

**For the reviewer:**
- At 24 h the cutoff equals the maximum lag. The protocol's lag cap binds there, and a longer cap could give a larger cutoff. The 24 h gap (4) is still below the 168 h one (7), so it does not set `g` here.
- At 168 h the cutoff (7) equals the label length. Overlapping weekly labels sampled daily are autocorrelated up to lag 6 by construction, so this is expected.
- The early targets use the cost model's start-up rule: a sample standard deviation over the first 168 returns.

Tests: `tests/unit/test_calibration_gap.py` (synthetic data only), 6 passed. ruff, `mypy calibration`, `mypy src` and import-linter (6 kept) are clean.
