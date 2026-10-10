# Proposal: the trend and vol rule libraries of the D-19 semi-empirical cells (Q5, QJ)

**Status:** DRAFT, revision 2: reviewed once (GPT-6 Sol, I2B-1..I2B-8), the
owner's choices on I2B-3, I2B-4 and I2B-7 written in, the equations and
timing added (I2B-5, I2B-6). It needs a re-review and then the owner's
recorded acceptance. Nothing here is binding before that. No calibration
has been run.

**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-10. The owner
delegates drafting choices; every item below is an `[AI default]` with its
alternatives, and the owner decides.

## 1. Why this is needed

The accepted preregistration (§3.2 Q5 and QJ, §3.4) builds the semi-empirical
cells from "trend-rule and vol-rule exposures ... computed causally on the
BTC path" and "the trend library and the vol library". Neither library is
defined anywhere:

- the frozen protocol (`protocols/protocol_v1.yaml`) fixes only the families'
  budgets (81 trials each: "3 model points × 3 vol targets × 3 horizons"),
  the vol targets {0.40, 0.60, 0.80}, the default sizing estimator
  `EWMA_168h` and the vol family's allowed estimators {`EWMA_72h`,
  `EWMA_168h`, `EWMA_336h`, `HAR_RV`, `GARCH_1_1`};
- the frozen specs define one rule only, the canonical baseline's trend
  signal "close > 200-day simple moving average" (`CANONICAL_BENCHMARKS_v1`);
- `PILOT_FINDINGS_2.md` records that "the strategy-rule libraries ... are not
  built yet".

Without a definition, the Q5/QJ generator would encode an unreviewed choice
of what those cells certify. The library-independent parts are built
(`calibration/semi.py`, engine item 2b); the rule libraries plug in as the
`exposures` function.

## 2. What the libraries are for

Q5 and QJ certify the method on realistic **null** columns: real BTC/ETH
market dynamics from the exploration partition, real-looking exposure
patterns, and an exact zero mean by block sign flips (§3.4). The libraries
only need to produce exposure paths of the kind the C2 families will
declare. They are not the declared families, and they carry no claim of
edge.

## 3. Decision items

### R-1 Daily returns from the hourly exploration bars

**Recommendation (built, pending):** a UTC day is used only when all 24 hourly
bars are present; its close is the 23:00 bar's close. Day d's return is
`close_d / close_{d−1} − 1`, kept only when both days are complete for **both**
BTC and ETH. Every other day is left out, never filled (Constitution §6), and
the count is reported with the source. The two columns are then demeaned
(§3.4).

Every return day of the window is accounted for: the left-out days are
listed, leading and trailing ones included (I2B-2). Kept rows are adjacent in
the source array even across a left-out day, so the bootstrap can join the
two sides of a gap as it joins the array's end to its start; this is
disclosed (alternative: restart a block at every gap).

*Alternatives:* (a) use each day's last available bar; (b) chain across a
missing day. Both fill or bridge gaps, which the rules forbid.

### Common definitions (I2B-5, I2B-6)

These hold for every rule. Path day 0 is the first warm-up day, and evaluation
starts at path day W = 250 (R-5).

- **Returns and price.** `r_t` is the path's BTC daily simple return on day t.
  The price index is `P_t = Π_{s ≤ t} (1 + r_s)`.
- **Timing.** The exposure held on day t, which earns `r_t`, is decided at the
  close of day t − 1 (00:00 UTC of day t). It uses only `r_0 … r_{t−1}`.
  Changing any path row from t onward cannot change it, and the built
  libraries will be tested for that prefix invariance.
- **Reference variance.** `v̄` is the variance of the source's BTC column (the
  demeaned exploration returns). It is computed once per source and frozen,
  never refitted on a replication.
- **Annualising and clipping.** A daily variance forecast v becomes the target
  `min(1, τ / √(365 v))`, with target 1 when v = 0 (canonical convention 3).
  The target always lies in [0, 1].
- **Frozen controls (owner decision, I2B-4).** The held exposure starts at 0 on
  path day 0. Each day the new target replaces the held exposure only when
  `aqt.benchmarks.canonical.reaches_rebalance_band(target − held)` is true:
  the frozen 0.10 band, on every rebalance, moving fully to the target
  (canonical conventions 1, 2 and 8). Decisions are daily at 00:00 UTC, so a
  risk increase is at least 24 h after the previous one, and the 24-hour
  minimum hold is met by construction (convention 5). Intraday reductions
  across the band are not simulated, since the path has no intraday data;
  this is disclosed.
- **EWMA variance**, half-life h days: `v_t = λ v_{t−1} + (1 − λ) r_{t−1}²` with
  `λ = 0.5^{1/h}` and `v_0 = v̄`. The forecast is flat in the horizon. The
  daily half-lives 3, 7 and 14 days stand in for `EWMA_72h`, `EWMA_168h` and
  `EWMA_336h`, the same daily stand-in convention as §3.1.

### R-2 Trend library (27 rules)

Long-only, in the protocol's 3 × 3 × 3 shape:

- **Model point:** SMA length L ∈ (200, 100, 50) days, in that index order.
  200 is the canonical baseline's.
- **Horizon:** H ∈ (1, 3, 7) days, the frozen 24/72/168 h.
- **Vol target:** τ ∈ (0.60, 0.40, 0.80). 0.60 is the canonical baseline's.

On refresh days, t ≡ 0 (mod H) counted from path day 0, the target is
`1[P_{t−1} > mean(P_{t−L} … P_{t−1})] × min(1, τ / √(365 v_t))`, using the
7-day EWMA v_t (the default `EWMA_168h`). Between refreshes the target is
held. The comparison is strict, as in the canonical rule. Before L prices
exist the target is 0; this happens only in the warm-up.

### R-3 Vol library (27 rules)

Always long, with the duplicates removed (owner decision, I2B-7):

- **Model point:** estimator class ∈ (EWMA, `HAR_RV`, `GARCH_1_1`).
- **Second index:** for EWMA it selects the half-life (7, 3, 14) days, i.e.
  `EWMA_168h`, `EWMA_72h`, `EWMA_336h`, with a 1-day horizon. For HAR and
  GARCH it selects the forecast horizon H ∈ (1, 3, 7) days.
- **Vol target:** τ ∈ (0.60, 0.40, 0.80).

The target is recomputed every day from the forecast below. The frozen
parameters are illustrative constants of the usual magnitude. They are
**not fitted** to any data, and they are disclosed.

- **`GARCH_1_1`:** `g_{t} = ω + α r_{t−1}² + β g_{t−1}`, with α = 0.10,
  β = 0.85 (the §3.1 values), `ω = (1 − α − β) v̄` and `g_0 = v̄`. The H-day
  forecast is `v_{t,H} = v̄ + (g_t − v̄) · (1/H) Σ_{h=0}^{H−1} (α + β)^h`.
- **`HAR_RV`:** with `RV_s = r_s²`, the one-day forecast is
  `f_t = c + β_d RV_{t−1} + β_w mean(RV_{t−5…t−1}) + β_m mean(RV_{t−22…t−1})`,
  with (β_d, β_w, β_m) = (0.35, 0.35, 0.20) and `c = 0.10 v̄`. The H-day
  forecast iterates the same equation forward, with forecasts in place of
  unobserved RV, and averages the H one-day forecasts.

### R-4 Which K rules a cell uses (owner decision, I2B-3)

**Fixed set per K.** Rule index i = 0 … 26 has digits a = i mod 3,
b = ⌊i/3⌋ mod 3 and c = ⌊i/9⌋. It maps to (model point a, second index
(a + b) mod 3, τ index (a + 2b + c) mod 3). The map is one-to-one, and:

- the first 3 rules use every value of every dimension once;
- the first 9 rules contain every pair of values from any two dimensions once;
- rule 0 is the canonical-like rule (SMA 200 or `EWMA_168h`, H = 1, τ = 0.60).

A cell with K rules uses rules 0 … K − 1 of its family, in that order. Under
rev 7g's grid that is K ∈ {1, 2, 5, 20}. The cell then certifies exactly
these designs. §3.6 maps a declared design to a cell by its diagnostics,
unchanged.

### R-5 Warm-up and simplifications

There are W = 250 warm-up days before day 0 of the evaluation, which covers the
200-day SMA, the 22-day HAR window and the EWMA/GARCH starts. The following
simplifications are disclosed:

- decisions and returns are daily, and intraday band reductions are not
  simulated;
- there are no trading costs, since the legs are null E-DIFF columns;
- estimator parameters are frozen, not fitted;
- the daily EWMA stands in for the hourly one (§3.1).

The §3.4 sensitivity rerun uses mean blocks of 60, with the same libraries.

### R-6 QJ

Each family uses its own fixed first-K rules (R-4) from its own library.
Both use the **same** resampled path and the **same** block signs (§3.4), so
their columns share the BTC benchmark days.

## 4. What the owner decides

The owner chose on 2026-10-11, in the session: a fixed set per K (I2B-3), the
frozen controls applied (I2B-4), and `EWMA_72h`/`EWMA_336h` in place of the
duplicate horizons (I2B-7). These choices are written above. Once this
revision is re-reviewed, the owner accepts, amends or rejects R-1 to R-6 as a
recorded clarification of the accepted preregistration's §3.4. That does not
change §13's budget, §3.6 or the certified claim's form. The rules then
become part of the generator code that the qualification object binds (§4).

## 5. Checks of the built part (2026-10-10, Windows local venv, Python 3.14.7)

`calibration/semi.py`, the `generator.benchmark_exposure` refactor and
`tests/unit/test_calibration_semi.py`, before review:

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python -m pytest` the seven calibration files (`rundef`, `chunks`, `reduce`, `binomial`, `choices`, `generator`, `semi`) `-q -p no:cacheprovider` | 0 | 143 passed in 1007.76 s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` with `--ignore=` each of those seven files | 0 | 1801 passed, 9 skipped in 964.67 s |
| `.venv/Scripts/python -m ruff check .` | 0 | All checks passed |
| `.venv/Scripts/python -m ruff format --check .` | 0 | 142 files already formatted |
| `.venv/Scripts/python -m mypy calibration src scripts/d19_run.py scripts/d19_choose.py` | 0 | No issues in 68 source files |
| `.venv/Scripts/lint-imports.exe` | 0 | 6 contracts kept, 0 broken |
| bundled `pwsh.exe -NoProfile -File review/task6/verify_frozen.ps1` | 0 | 28/28 trusted bytes and inventory, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings pass |
