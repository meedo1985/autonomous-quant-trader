# D-19 §7.2 declared-strategy screen: build plan (draft, nothing built)

**Status:** plan only. Drafted by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-16. No code is written until the owner says go. This plan decides nothing; where it chooses between readings, it says so and the choice goes to review.

**Timing.** Owner decision `OWNER_DECISION_BUILD_ORDER.md` ("By the freeze", Sol BO review): the screen is built and §16-reviewed during the full run, and must be in the qualification object at the freeze. The full run has not started yet, so there is time.

## 1. What the screen does, in plain words

Before a set of up to 20 strategies ("trials") is declared for C2, each trial is run on 30 made-up BTC/ETH price histories that contain no real edge. On each one, seven promotion gates (G-3, G-5, G-6, G-7, G-8, G-11, G-14) are computed exactly as they would be on real data. The screen does not ask whether a gate passes, only whether it **can be computed**. If any gate is `UNAVAILABLE` on any path for any trial, the whole set is invalid and cannot be declared (prereg §7.2, P18-1). Nothing is spent.

Sources: prereg §7.2 and §10; §13 rev 7g item 1 (20 trials, not 80); Annex C rev 4 C-0, C-3, C-5..C-8, C-10, C-12; DRAFT_WORDING rev 9 R-8, R-13, §2.5.

## 2. What already exists and is reused

| Need | Existing code |
|---|---|
| Stationary bootstrap indices, block signs | `calibration/semi.py` `stationary_indices`, `block_signs` |
| Exploration data, manifests | `calibration/semi.py` `load_source`; `aqt.data.manifest` |
| Gap `g` (G-11's `m = max(g, 30)`) | `calibration/gap.py` |
| Sharpe, `E-IMPROV`, drawdown, band test | R-8 functions in `aqt.metrics`, `aqt.benchmarks.canonical` |
| Benchmark leg `VOL_TARGET_BUY_AND_HOLD` | `aqt.benchmarks.canonical` |
| Costs, slippage, stress multiplier | `aqt.backtest.costs` |
| Seed hashing (`cj`, `sha`) | `calibration/seeds.py` |
| Model libraries | scikit-learn 1.9.1, LightGBM 4.7.0 in the image (PR #58) |

## 3. What is missing (the real size of the job)

1. **The event-contract runner (C-6).** The current backtester (`src/aqt/backtest/engine.py`) refuses delayed fills and does not implement the C-6 band, clamp and clock rules. G-5, G-6, G-7 and G-11 all need C-6. This is protected code (§16). **Where it lives is constrained by the binding:** the qualification object binds `calibration/screen.py` by its bytes and everything else by the engine commit in the full run's definition (DRAFT R-8, `calibration/qobj.py` `LATER`). Code merged into `src/` after that commit is bound by nothing. So either C-6 is merged into `src/aqt/backtest/` **before** the full run's definition is recorded (then the engine commit binds it, and C2 can reuse the same code), or it lives inside `screen.py`. Recommended: the first, if S2 is ready before the full run starts; otherwise inside `screen.py`, with the production backtester later required to match it. Decided at S2, with review.
2. **The trial declaration format.** The hashed interface of C-10 (1)-(2): `s`, `τ` ∈ {0.40, 0.60, 0.80}, `σ̂` (EWMA_168h or a vol-family estimator), overlay, `s_inputs`, `g11_class`, model class and parameter point, declared grid (for G-8), horizon, warm-up. Plus the REG (A) `s_inputs` enforcement and its falsifier test (rejects `ewma_vol_168h` or `σ̂` in a `σ̂`-sized trial's `s_inputs`).
3. **The walk-forward model pipeline** (protocol l.198-214: windows, purge, embargo) for G-14's 500 refits. `src/aqt/models` and `src/aqt/validation` are empty today.
4. **The seven gate availability checks** and the null-path generator.

## 4. Build slices (each: tests, Sol review to ACCEPT, record committed)

| # | Slice | Main content | Frozen reference vectors |
|---|---|---|---|
| S1 | Null paths | §7.2 path builder: joint hourly bootstrap (mean block 168 h), shared signs (mean 24 h), the OHLC sign flip and chaining, length = C2 window + warm-up; streams from `screen_seed` | draws (rows, signs) exact in the unit test; float path bit-exact on the pinned image at S7 |
| S2 | C-6 runner | event contract in `src/aqt/backtest/`, 1x/2x cost, execution delay, the reduction-to-0 rule, the decision-time clock; tests from each C-6 clause | — |
| S3 | Trial interface | declaration schema + hash, `s_inputs` gate (falsifier test), `g11_class` constant-signal check | — |
| S4 | Simple gates | G-3, G-5, G-7 on C-6; G-6 feature lag (`t − 1h` inputs); G-8 neighbours from the declared grid | — |
| S5 | G-11 | 500 shifts, CPython `random.Random` stream, partial Fisher-Yates, screen-internal seeds (D-20 B6) | first 10 `k_i` + SHA-256 of 500 |
| S6 | Walk-forward + G-14 | windows, purge, embargo; circular label shift; refits with `model_seed` → `random_state` / LightGBM `seed`, `deterministic`, 1 thread, `force_col_wise`; one exact class per allowed model, each with a reproducibility test | `(offset, model_seed)` for d ∈ {0, 499}, w ∈ {0, 1}, SHA-256 of the grid |
| S7 | Screen driver | `calibration/screen.py`: runs a trial set over 30 paths, records every run, outcome VALID / INVALID with cause codes; `scripts/d19_screen.py`; runs in the calibration image | — |
| S8 | Cost pilot | prereg §10 "one screen of a 20-trial set", measured on the server; feeds §12 item 2 (an infeasible size cannot be declared) | — |

Then a §16 different-model review of the whole screen, and your PR review, before merge. S1, S3 and S5 are independent of S2 and can come first.

## 5. Risks to know now

- **Cost.** One screen runs, per trial and path, 500 G-11 re-runs, 500 G-14 refits over every walk-forward window, and the stressed runs. For 20 model-fitting trials × 30 paths that is about 300,000 refit pipelines. LightGBM refits may make a 20-trial set infeasible on the server. S8 measures it; the answer can be "only smaller sets, or no model trials", which prereg §12 item 2 already allows.
- **Draft text.** Annex C rev 4 and DRAFT rev 9 are not signed. The screen is built against them, as the mapping and held-out runner were. If signing changes a gate, the screen changes before the freeze.
- **Protected code.** S2 (C-6) and `screen.py` are §16 components: different-model review and your PR review are merge conditions.

## 6. What needs you

Only the go-ahead to start building (§12 item 2 is already given for build and pilot; this asks to begin the screen slices now). The drafting choices above (C-6 in `src/aqt/backtest/`, slice order) are recommendations for review, not your decisions.
