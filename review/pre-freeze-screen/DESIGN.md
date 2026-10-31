# Pre-freeze `screen.py` change for D-20 Q2(ii) and Q5: design

**Author:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-31. This is AI drafting and not an authority. **Status: DESIGN, UNREVIEWED. No code is written yet.**

**Authority:** the owner's D-20 decision (`OWNER_DECISION_D20_LOCKBOX.md`, freeze-sheet `f04aa6c`), items 6 and 9, which are time-sensitive. The binding text is `PROPOSAL_REV3.md` A1b and A6 "The final hour", as amended by `PROPOSAL_REV4.md` A1b (D20L-44, D20L-47, D20L-48) and `PROPOSAL_REV5.md` (D20L-55). None of this binds until C2 is signed. The only purpose of the change is to keep the recommended options available: under R-14 (S4 `DRAFT_WORDING.md` l.152), C2 evaluation code must lie in the engine commit or in a later object file, so these pieces must be in the frozen `screen.py`.

## 1. What changes, and what must not

**Must not change (the guard):** with default arguments, every existing function returns bit-identical output. This covers the D-19 screen (`screen_job`), the held-out run (`scripts/d19_heldout.py`), and every frozen reference vector, including S8's paths vector and the G-14 `(offset, model_seed)` vectors. The new parameters default to today's behaviour.

**C1. Estimator seed (Q5, A1b `L266_MOD_2_31`).**
- New `estimator_seed(seed_l266: str) -> int` returns `int(seed_l266, 16) % 2**31`. It refuses anything that is not 64 lowercase hex digits. A result of 0 is legitimate (D20L-44).
- `walk_forward(..., model_seed: int = 0)`: the nominee's fit uses `model_seed` where it now hard-codes `seed = 0` (l.1547). A G-14 null draw still replaces it with its own `g14_draw` seed, unchanged (C-12 (5): "null draws never reuse it").
- `model_column(..., model_seed=0)` and `screen_gates(..., model_seed=0)` pass it through. In `screen_gates`, it reaches both the emission fits (`inputs` → `model_column`) and G-14's un-shifted pipeline (`draw is None`, l.1176), which is also the nominee's own fit.
- `ZERO` is the owner's rejected alternative. It needs no code, because the default stays 0.

**C2. Final-hour end price (Q2(ii), A6).**
- New `confirmation_path(rows: np.ndarray) -> np.ndarray`. The input is real joint rows (`rows × SYMBOLS × OHLCV`, as `joint_bars` gives) over exactly `[w0 − warmup, w1)`. The output appends one derived terminal row per symbol: open = high = low = close = that symbol's last close, and volume = 0.
- That gives the `warmup + window_hours + 1` rows `screen_gates` already requires. The runner reads the last hour's exit price as `bars[j + 1].open`, the terminal open, which is the last bar's close (C-6 (1)'s close(t) = open(t + 1), used as a definition). So no confirmation run reads the bar at `w1`, and the lockbox checker never reads past L1.
- It refuses with `TrialError` unless the rows are finite and positive and have a symbol axis of `len(SYMBOLS)`. Contiguity of the hours is the caller's input check (C3).
- Note: the lockbox run's own adapter lives in the separate lockbox module (Q4). It must use the same rule, because A7 compares hashes of `d`.

**C3. One confirmation entry point (R-14).**
- New `confirmation_gates(trial, rows, hours, w0, window_hours, seed_l266, trial_seed, window_id, g_days)`. It checks that `hours` are contiguous and equal to `[w0 − warmup, w1)` hour by hour. It then calls `screen_gates(trial, confirmation_path(rows), w0, window_hours, trial_seed, window_id, g_days, model_seed=estimator_seed(seed_l266))`.
- `trial_seed` is R-13's beacon-protected seed, supplied by the caller. Reading confirmation data, the paired statistics and the C2 record are **not** part of this change (§3).

## 2. Tests (synthetic data only)

- **T1 guard.** `screen_job`, `screen_gates`, `walk_forward` and `model_column` with defaults give bit-identical results to `main` on the existing fixtures. All reference-vector tests pass unchanged.
- **T2 seed map.** Known vectors: an all-zero hex gives 0 (accepted), `"f"*64` gives `2**31 − 1`, plus one fixed mid value. Malformed input is refused.
- **T3 seed reaches the fit.** A spy `build_model` records the seed. The nominee fit gets `model_seed`, and G-14 draws still get their `g14_draw` seeds. With a fixed `model_seed`, two runs are bit-identical for each allowed class (A1b test).
- **T4 terminal row.** On a synthetic path whose true bar at `w1` has an open different from the last close, `confirmation_path` differs from the true path only in that last hour's leg return: every earlier equity value, target, feature, emission and cost-volatility value used inside the window is identical. The last hour's exit is priced at the last close.
- **T5 refusals.** Non-contiguous hours, wrong span, non-finite or zero rows.

Each test fixture is synthetic. No confirmation or lockbox bytes are read.

## 3. Out of scope (later tasks, each authorised separately)

The C2 runner itself is out of scope: loading the confirmation partition, the paired statistics and the C2 record. So are the lockbox module (Q4), the S4 C-0/C-6 wording of the end-price rule (D20L-34), and the Annex C l.412 wording.

## 4. Freeze consequences (to state in the PR)

1. `screen.py`'s SHA-256 changes. It needs a new independent review record (Sol), and `review/d19-engine/FREEZE_REVIEWS.json` must name the new hash and record. Without them, `qobj.build` refuses (QO-5).
2. Owner §16 PR review before merge (`screen.py` is evaluation code in the frozen object).
3. **G0 must be redone.** `FREEZE_HELDOUT.md` FP2 (d) pins `/opt/aqt-d19/build` at `ed0bfbf`. The build checkout must be reinstalled at the merged commit, and the sheet updated (D20L-47: the freeze names a build commit whose `screen.py` is this version).
4. The development run is unaffected. `screen.py` is a LATER file (`qobj.py` `LATER`), not an engine file pinned to `/opt/aqt-d19/app` at `eeaa728`.

## 5. Questions for the reviewer

- Q-a: Should G-14's un-shifted pipeline use `model_seed` (as proposed), or stay at 0? C-12 (5) says the nominee's own fit keeps its declared seed.
- Q-b: Does anything in a run read the terminal row beyond `bars[j + 1].open` and the last close-to-close cost return? Is volume 0 safe?
- Q-c: Is C3 enough for R-14 at freeze time, given that the runner (data loading and statistics) comes later? Or must more of the C2 evaluation be in a later object file before the freeze?
