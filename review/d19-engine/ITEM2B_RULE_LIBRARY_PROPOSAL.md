# Proposal: the trend and vol rule libraries of the D-19 semi-empirical cells (Q5, QJ)

**Status:** DRAFT for review, then the owner's decision. Nothing here is
binding until the owner accepts it in a recorded decision. No calibration
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

*Alternatives:* (a) use each day's last available bar; (b) chain across a
missing day. Both fill or bridge gaps, which the rules forbid.

### R-2 Trend library (27 rules)

**Recommendation:** long-only, the protocol's 3 × 3 × 3 shape:

- **3 model points:** price above its L-day simple moving average, with
  L ∈ {50, 100, 200} (200 is the canonical baseline's signal);
- **3 horizons:** the signal is held for H ∈ {1, 3, 7} days. It is re-read
  every H days, on days 0, H, 2H, … of the replication path; the
  frozen 24/72/168-hour horizons expressed in days;
- **3 vol targets:** τ ∈ {0.40, 0.60, 0.80}.

The exposure on day t is `signal_t × min(1, τ / (σ̂_t √365))`, where σ̂ is
the daily EWMA with a 7-day half-life (the §3.1 stand-in for `EWMA_168h`).
Everything is computed from returns up to day t − 1 only.

*Alternatives:* (a) time-series momentum, `sign(P_{t−1}/P_{t−1−L} − 1)`, in
place of or alongside the SMA rule; (b) fewer rules (K ≤ 20 needs at least
20).

### R-3 Vol library (27 rules)

**Recommendation:** always long, the same 3 × 3 × 3 shape:

- **3 model points (estimators):** `EWMA_168h` (7-day half-life), `HAR_RV`,
  `GARCH_1_1`;
- **3 horizons:** the estimator's variance forecast for the next H ∈ {1, 3, 7}
  days;
- **3 vol targets:** τ ∈ {0.40, 0.60, 0.80}.

The exposure is `min(1, τ / (σ̂_{t,H} √365))`. The estimators work on daily
returns, with **frozen** parameters and no refits per replication, as
disclosed simplifications:

- `HAR_RV` uses squared daily returns over 1, 5 and 22 days with frozen
  weights;
- `GARCH_1_1` uses α = 0.10 and β = 0.85, the §3.1 values.

An EWMA forecast is flat across horizons, so its three horizon variants are
identical. That gives exact-duplicate columns, which real families can have
too. They are kept, and the disclosure says so.

*Alternatives:* (a) use all five allowed estimators × 3 targets (15 rules), and
add the horizon only where it changes the forecast; (b) drop the duplicate
EWMA horizons and add `EWMA_72h`/`EWMA_336h`.

### R-4 Which K rules a cell uses

**Recommendation:** in every replication, draw a uniform random K-subset of
the family's 27 rules from the `"columns"` stream. The subset is kept in
library order, and at K = 1 it is one rule. The certified law then averages
over designs of size K. A declared design is mapped to cells by its
diagnostics anyway (§3.6), so no single fixed design is privileged.

*Alternative:* a fixed, frozen subset per K, such as the first K in an
interleaved order. That is simpler, but it certifies one design per K.

### R-5 Warm-up and simplifications

**Recommendation:** 250 warm-up days before day 0. That covers the 200-day SMA,
the 22-day HAR window and EWMA convergence. The following simplifications are
disclosed:

- exposures are daily, with no rebalance band and no minimum holding, since
  the hourly execution contract is not simulated;
- there are no trading costs (the legs are null E-DIFF columns);
- estimator parameters are frozen.

The §3.4 sensitivity rerun uses mean blocks of 60, with the same libraries.

### R-6 QJ

**Recommendation:** each family draws its own K-subset (R-4) from its own
library. Both families use the **same** resampled path and the **same** block
signs (§3.4), so their columns share the BTC benchmark days.

## 4. What the owner decides

Accept, amend or reject R-1 to R-6 as a recorded clarification of the
accepted preregistration's §3.4. It does not change §13's budget or the
certified claim's form. The rules become part of the generator code that the
qualification object binds (§4).

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
