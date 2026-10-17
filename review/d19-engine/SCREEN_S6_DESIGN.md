# D-19 screen slice S6: walk-forward models and G-14, design (draft, no code)

**Status:** design for review before any code. Drafted by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Readings WF-n are proposals; items marked **OWNER** are bindings only the owner can make.

**Sources:** frozen protocol `target` (l.103-110), `models` (l.153-175), `validation` (l.196-214), `trial_accounting.parameter_point_includes`; Annex C rev 4 C-7 (2) (G-6 on model inputs), C-10 (1) (`s_inputs`, the REG (A) ban), C-12 (G-14); DRAFT rev 9 §2.5; owner decision S3R-R3 (G-14 applies to logistic sign models); `calibration/gap.py` (target and ACF readings, already reviewed for the C2 gap).

## 1. What S6 must deliver

1. **Model trials can run** on a screen path: a walk-forward pipeline produces, for each 00:00 UTC decision, the model's prediction, which the signal reads as its `model:<id>` input. Without it, every model trial is `MODEL_PENDING` (S4b RN-6).
2. **G-14 availability:** 500 refits with circularly shifted labels per training window (C-12 (3)-(5)), the OOS Spearman IC of the nominee and of every draw (C-12 (6)), and the unavailability rules (C-12 (3), (7)).

## 2. Proposed readings

- **WF-1 Rows and label.** One BTC row per 00:00 UTC decision instant (C-12 (2)). Features: the model's declared feature names from the frozen factory, read from the row of bar `j - 1` like every other input (S4b RN-2). Label: the protocol's vol-scaled target at the trial's horizon, `log(P[t+H] / P[t]) / (sigma_t * sqrt(H))`, `P` the hourly close and `sigma_t` the trailing EWMA hourly volatility (168 h half-life), exactly as `calibration/gap.py` G-2 already reads it, but at the 00:00 instant instead of the 23:00 close. For logistic models the label is its sign (S3R-R3); a zero label is a refusal (`LABEL_ZERO`, unavailability), never a coin flip.
- **WF-2 Walk-forward schedule.** Training window 24 months (730 days), step and retrain cadence 30 days (l.198-200). The first refit is at the first window decision `w0`, using the 730 days before it; then every 30 days. Predictions between refits use the latest fit. So a model trial needs a warm-up of at least 730 days plus the feature history (4,800 h) and the label horizon; a shorter declared warm-up makes every run `INSUFFICIENT_WARMUP`.
- **WF-3 Purge and embargo (l.205-214).** A training row is retained only if its label's horizon ends before the refit decision (purge = label horizon), and rows within the embargo before the refit are also dropped. **Embargo length:** l.207's `max(label_horizon, target_autocorr_cutoff)`. Two readings:
  - (a) the cutoff computed by `gap.py`'s ACF rule on the window's own training labels, at every refit (data-dependent, varies by window);
  - (b) the cycle constant `gap_embargo.value_days` (`g`), which the §4 draft already defines by the same ACF rule on exploration data and binds for C2 (DRAFT R-3, R-9).

  **Recommended (b):** one fixed number, already computed and reviewed, and no per-window choice that depends on the null path. **OWNER** if a reviewer finds (b) not faithful to l.207.
- **WF-4 Model inputs and the REG (A) ban.** The annex bans `sigma_hat` and its identical feature from `s_inputs` (C-10 (1)) but says nothing about the **model's** features. A model fed `ewma_vol_168h` could pass the sizing estimator into `s` through its prediction. Two readings:
  - (a) apply the same ban to the model's declared features (stricter: the ban cannot be bypassed through a model);
  - (b) the ban covers `s_inputs` only, as written.

  **Recommended (a). OWNER**, like S3R-R3: this is a binding of the REG (A) clause.
- **WF-5 Model classes (one exact library class each, C-12 (5)):** `linear` `sklearn.linear_model.LinearRegression`; `ridge` `Ridge`; `lasso` `Lasso`; `elastic_net` `ElasticNet`; `logistic` `LogisticRegression`; `lightgbm` `lightgbm.LGBMRegressor` with `deterministic=True`, `num_threads=1`, `force_col_wise=True`, and the frozen limits `max_depth <= 3`, `num_leaves <= 8`, `learning_rate = 0.05`, `n_estimators <= 300` (l.163-175) checked at declaration. `model_seed` is passed as `random_state` where the constructor accepts it, as `seed` to LightGBM. Parameters a declaration may set: each class's documented hyperparameters except seeds, thread counts and anything that reads files. Each class gets a reproducibility test (same data and seed, identical predictions).
- **WF-6 Model outputs as inputs (C-7 (2)).** The prediction is emitted at each 00:00 decision and held until the next; the signal's `model:<id>` input at instant `j` is the last emission at or before `j`. Under G-6 the model's *features* are lagged one hour and the prediction is re-inferred from them at its own emission time; refits and labels are not lagged (C-7 (2)).
- **WF-7 G-14 (C-12).** Draw `d = 0 .. 499`: in every training window, the retained rows' labels are circularly shifted by the offset of C-12 (5) (stream already specified; inside the screen the trial seed is `screen_trial_seed`, S5 GS-1), the whole pipeline is refit at the same parameter point with `model_seed` from the same stream, and the OOS Spearman IC (midranks) is computed over all OOS rows whose target realisation lies inside the window (C-12 (6)). Availability: `NO_SHIFT_RANGE` when a window has `n_w < 2 * horizon_days + 1` (C-12 (3)); a constant prediction or constant target for the nominee or any draw (C-12 (7)); any fit that raises. The screen needs availability only (PASS needs 476 of 500 strictly below).
- **WF-8 Reference vectors (C-12 (5)):** `(offset, model_seed)` for `d in {0, 499}`, `w in {0, 1}` and the SHA-256 over the full `d x w` grid, for a fixed set of `n_w`, frozen in the unit test (exact on every CPython, like S5).

## 3. Cost, the reason to measure early

Per trial and path: 1 nominee pipeline plus 500 null pipelines, each refitting every 30 days over the window (about 41 refits for C2's 1,247 days). For a LightGBM trial that is about 20,500 fits per path, so about 615,000 per trial over 30 paths. The S8 pilot measures it; the expected answer is that a 20-trial set of LightGBM trials is not feasible on the server, and prereg §12 item 2 then forbids declaring a set of that size (smaller sets, or linear models, remain).

## 4. Build order

S6a: rows, labels, walk-forward schedule, purge/embargo, model class mapping with reproducibility tests (no G-14). S6b: model trials in `screen_gates` (G-3..G-8 for model trials). S6c: G-14 draws, IC, availability, reference vectors. Each with Sol review, as before.

## 5. What needs the owner

WF-3 only if the reviewer rejects reading (b); WF-4 in any case (recommendation (a)).
