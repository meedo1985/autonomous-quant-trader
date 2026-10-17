# D-19 screen slice S6: walk-forward models and G-14, design revision 4 (no code)

**Status:** design for review before any code. Drafted by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-17. Revision 2 applied the Sol review of revision 1 (`SOL6_SCREEN_S6_DESIGN_REVIEW_5892A4A.md`, S6D-R1..R8). Revision 3 applied the re-review of revision 2 (`SOL6_SCREEN_S6_DESIGN_REREVIEW_5D722FD.md`): the owner's S6D-R6 decision (WF-1). Revision 4 applies the re-review of revision 3 (`SOL6_SCREEN_S6_DESIGN_REREVIEW2_51E2ACD.md`): S6D2-R1 is accepted, `t + H < w1`. Each change cites its finding. Readings WF-n are proposals for review.

**Sources:** frozen protocol `target` (l.103-110), `models` (l.153-175), `validation` (l.196-214), `trial_accounting`; Annex C rev 4 C-7 (2), C-10 (1), C-12; DRAFT rev 9 §2.5; owner decisions S3R-R3 (G-14 applies to logistic sign models) and WF-4 (the sizing-estimator ban covers model inputs); `calibration/gap.py` (target, ACF and cutoff rules, already reviewed).

**Decided by the owner, not open here:** G-14 applies to every model trial, logistic included (S3R-R3); a model's declared features obey the same ban as `s_inputs` (WF-4); a zero target is the logistic class "not up" (S6D-R6, `OWNER_DECISION_S6D_R6_ZERO_TARGET.md`).

## 1. What S6 delivers

1. **Model trials run** on a screen path: a walk-forward pipeline emits, at each 00:00 UTC decision, the model's prediction, which the signal reads as `model:<id>`. Until then every model trial is `MODEL_PENDING` (S4b RN-6).
2. **G-14 availability** (C-12): 500 null pipelines with circularly shifted labels; the nominee's and each draw's OOS Spearman IC; the unavailability rules.

## 2. Timestamps (S6D-R5, S6D-R6 notes; WF-1, WF-6)

A **decision instant** `t` is a bar boundary; at 00:00 UTC it is the close of the 23:00 bar and the open of the 00:00 bar. As in S4b, the decision at `t` reads the feature row of the bar that closes at `t` (bar index `j - 1` for instant `j`). The model emits once per 00:00 instant. The signal's `model:<id>` input at instant `j` is the last emission at or before `j`.

## 3. Readings

- **WF-1 Rows and label (S6D-R6).** One BTC row per 00:00 UTC decision instant `t` (C-12 (2)). Features: the model's declared feature names (a new `model.features` list in the trial interface, frozen factory names only, checked with the WF-4 ban), read from the row of the bar closing at `t`. Label: `y_t = log(P[t+H] / P[t]) / (sigma_t * sqrt(H))` (l.103), `P[t]` the close at `t`, `P[t+H]` the close at `t + H`, `sigma_t` the cost model's EWMA hourly volatility of the hourly log returns up to `t`, in log-return units (`ewma_hourly_volatility_bps_series / 1e4`, as `gap.py` G-2). **Logistic class (owner decision S6D-R6):** `1` if `y_t > 0`, else `0`. A zero target is class 0, never a refusal and never a dropped row.
- **WF-2 Walk-forward schedule (S6D-R2).** Refit instants `r_k = w0 + 30k` days, `k = 0, 1, ...`, while `r_k < w1` (l.199-200: step and cadence 30 days). Training window of `r_k`: calendar months, `[r_k - 24 months, r_k)` (l.198), where "minus 24 months" keeps the day and time and clamps to the month's last day when that day does not exist. Each refit predicts the 00:00 decisions in `[r_k, r_{k+1})` (the last up to `w1`). On a screen path the training data before `w0` is the path's own warm-up, so a model trial needs `warmup_hours >= hours(w0 - (w0 - 24 months)) + 4,800 + 1` (the feature history before the first training row); a shorter declared warm-up is refused at declaration, not reported as a run failure. For C2 the same schedule reads 24 months of data before `w0`; which partition supplies it is the C2 evaluation's own binding, not the screen's.
- **WF-3 Purge and embargo (S6D-R1, S6D-R7).** The frozen rule governs: purge = label horizon, embargo = `max(label_horizon, target_autocorr_cutoff)` (l.205-214). For each refit `r_k`:
  1. *Candidate rows*: 00:00 instants `t` in the training window whose label is realised by the refit, `t + H <= r_k`.
  2. *Cutoff*: `gap.py`'s ACF with Bartlett bands, alpha 0.05, lags up to `4 * H_days`, "first lag after which no remaining lag is significant", computed on the candidate rows' **original** labels (never on null-shifted labels), in time order, at the daily decision frequency (l.208).
  3. *Embargo* `E_k = max(H_days, cutoff_k)` days; a row is **retained** iff `t + E_k days <= r_k`. Since `E_k >= H_days`, this also enforces the purge.

  Boundary example: `H = 168 h` (7 days), `cutoff_k = 12`, so `E_k = 12` days; with `r_k` at 00:00 on day 100, the row at 00:00 on day 88 is retained (88 + 12 = 100, `<=`), the row on day 89 is not. Revision 1's use of the cycle constant `g` is withdrawn: it would change the frozen embargo (S6D-R1).
- **WF-4 Model inputs.** Owner decision: `model.features` is checked exactly like `s_inputs` (TI-3): never `sigma_hat`, never the feature identical to the trial's sizing estimator.
- **WF-5 Model classes and parameter allowlist (S6D-R3).** One exact class each (C-12 (5)); a declaration may set only the parameters listed, inside the ranges listed; everything else is fixed. Decimal values are declared as strings, as in TI-1.

  | `class` | Library class (fixed settings) | Declarable parameters |
  |---|---|---|
  | `linear` | `StandardScaler` then `sklearn.linear_model.LinearRegression` | `fit_intercept` (bool) |
  | `ridge` | `StandardScaler` then `Ridge` | `alpha` (decimal > 0), `fit_intercept` |
  | `lasso` | `StandardScaler` then `Lasso` (`max_iter=10000`, `selection="cyclic"`) | `alpha` (> 0), `fit_intercept` |
  | `elastic_net` | `StandardScaler` then `ElasticNet` (`max_iter=10000`, `selection="cyclic"`) | `alpha` (> 0), `l1_ratio` (0 to 1), `fit_intercept` |
  | `logistic` | `StandardScaler` then `LogisticRegression` (`penalty="l2"`, `solver="lbfgs"`, `max_iter=10000`) | `C` (> 0), `fit_intercept` |
  | `lightgbm` | `lightgbm.LGBMRegressor` (`objective="regression"`, `learning_rate=0.05`, `deterministic=True`, `num_threads=1`, `force_col_wise=True`, `verbose=-1`, no bagging, no feature subsampling) | `n_estimators` (int 1-300), `max_depth` (int 1-3), `num_leaves` (int 2-8), `min_child_samples` (int >= 1), `reg_alpha`, `reg_lambda` (decimal >= 0) |

  The scaler is part of the label-independent pipeline and is refit on each window's retained rows. `model_seed` is passed as `random_state` where accepted and as `seed` to LightGBM. Aliases (for example LightGBM's `min_data_in_leaf`) are refused, because only the listed names are accepted. Each class has a reproducibility test (same data and seed, identical predictions).
- **WF-6 Emission and G-6 (C-7 (2)).** At each 00:00 instant the latest fit predicts from that instant's feature row. Under G-6 the inference features are those of the bar closing at `t - 1h` (the last available by 23:00), and the prediction is recomputed from them; refits, training rows and labels are not lagged.
- **WF-7 G-14 (S6D-R4, S6D-R5).**
  - Draw `d = 0 .. 499`, window `k`: with `n_k` retained rows and `h = H_days`, the offset is `h + draw(n_k - 2h + 1)` and `model_seed = getrandbits(31)` from the C-12 (5) stream (inside the screen the trial seed is `screen_trial_seed`, S5 GS-1). `NO_SHIFT_RANGE` iff `n_k < 2h` (revision 1's `2h + 1` was off by one: `n_k = 2h` allows the single offset `h`).
  - The null labels of window `k` are the retained labels circularly shifted by the offset; the whole pipeline (scaler and model) is refit on them at the same parameter point.
  - **IC:** one pooled Spearman IC per pipeline (nominee or draw): midranks of the OOS predictions against midranks of the **continuous** target `y_t`, over every 00:00 decision `t` in `[w0, w1)` with `t + H < w1`, all refit intervals together. For logistic models the prediction is `predict_proba[:, 1]`.
  - **Why `t + H < w1` (S6D2-R1, accepted in revision 4).** The realisation `P[t+H]` carries the timestamp `t + H` (the close of the bar ending then), and `[w0, w1)` excludes `w1`. A label realised at `w1` is therefore not realised inside the window under C-12 (6)'s wording, even though its bar is the window's last. Revision 3 argued for `<=`; the stricter reading is adopted as a drafting choice because it never uses a price stamped at `w1` and costs one boundary label per horizon.
  - Unavailable: `NO_SHIFT_RANGE` (any window); a constant prediction or constant target over the IC rows, for the nominee or any draw; any fit or prediction that raises. PASS (476 of 500 strictly below) is not part of the screen's outcome.
- **WF-8 Reference vectors (S6D-R8 note).** Frozen in the unit test, for the fixed window sizes `n = (120, 365)` and `h = 7`: `(offset, model_seed)` for `d in {0, 499}`, `k in {0, 1}`, and `sha({"grid": [[d, k, offset, model_seed], ...]})` over the full `500 x 2` grid in `d`-major order (`seeds.sha`, canonical JSON). They are exact on the pinned runtime; C-12 (5)'s byte-identity across the rebuilt and current images is checked by the S7 image check, not claimed for every CPython.

## 4. Cost (S6D-R8)

Under WF-2, a C2-length window of 1,247 days has 42 refits. Per trial and path: 501 pipelines x 42 refits = about 21,000 fits; about 631,000 per trial over 30 paths. This is arithmetic, not a feasibility result: the S8 pilot measures it, and only a measured infeasible cost triggers prereg §12 item 2.

## 5. Build order

S6a: interface field `model.features`, the parameter allowlist, rows, labels, the schedule, purge/embargo with the per-window cutoff, the class mapping with reproducibility tests. S6b: model trials in `screen_gates`. S6c: G-14 draws, IC, availability, reference vectors. Each with Sol review.

## 6. What needs the owner

Nothing open. S6D-R6 was decided on 2026-10-17.
