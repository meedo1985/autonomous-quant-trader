# N-1, N-2 proposal (revision 1): the effective-decisions gate and the shuffled-labels null

**Status:** `NON-BINDING AI PROPOSAL — NO ROW DECIDED — NOT ACTIVE`
**Date:** 2026-10-03
**Author:** Claude Opus 5.5 (`claude-opus-5-5`). This is design and drafting
work, under the owner's instruction "let agent do the answers all the time".
N-1 and N-2 are proposed **new** decision rows (§4 draft rev 4, §4; FA3-1,
FA3-2). Adding them to the matrix is the owner's act. Like D-rows, they are
decided only by the owner, after two different-model reviews (R19-2).
**Why now:** gates G-12 (minimum effective decisions) and G-14
(shuffled-labels null) are blocked by N-1 and N-2. Both are mandatory
pre-lockbox gates, so their availability counts toward `U_proc` (P18-7). They
must be defined before D-19 (FA3-12).

## 1. N-1: the effective-decisions gate (G-12)

**Frozen text:** l.242–244
(`effective_decisions: method: "newey_west_autocorrelation_adjusted_ESS_on_BTC_OOS_strategy_returns", fallback: "raw_decisions / ceil(horizon_hours/24)"`)
and l.290 (`minimum_effective_decisions: 120`). The same ESS switches CPCV on
at ≥ 250 (l.216). The frozen text gives no kernel, no bandwidth and no
fallback trigger (FA3-1).

**Existing, inactive binding:** `review/task12/IMPLEMENTATION_CONVENTIONS.md`
§"Newey-West ESS", owner-approved for inactive use only. Decision packet R3
(`review/inactive-paired-evaluation-proposal/SCIENTIFIC_DECISION_PACKET.md`)
says never to compare it with 120 until a statistician approves. Under R19-2
the owner replaced that statistician step with two different-model reviews
plus the owner's decision. This proposal is that step.

**Proposal N1:**
- **Series:** the nominee's BTC OOS daily net returns (candidate leg only,
  not paired), at 1x cost, over the eligible window. One observation per
  complete UTC day, which is one 00:00 UTC decision per day, so "decisions"
  equals days.
- **Formula:** exactly the Task 12 convention.
  - `h = ceil(H/24)`, with `H` the trial's declared horizon in hours (l.109:
    24, 72 or 168).
  - Bartlett weights, with `L = min(n−1, max(h−1, floor(4·(n/100)^(2/9))))`.
  - `ESS = clamp(n·γ0/Ω, 1, n)`.
- **Fallback:** `n/h` (l.244), used only for otherwise-valid zero variance or
  non-positive `Ω`, as in Task 12. Missing or non-finite data, invalid time,
  an unknown horizon or `n < 2` give `UNAVAILABLE`, with no fallback.
- **Gate:** `PASS` iff `ESS >= 120`; otherwise `FAIL`.
- **Report:** the method actually used (Newey-West or fallback) and its reason.

**Consequences:**
- For C2 (`n` ≈ 1,219 days), `L` = max(h−1, 6), and daily strategy returns
  usually have weak autocorrelation. So ESS will be far above 120 unless
  returns are strongly autocorrelated. The gate then matters mainly for short
  windows, where `T_min` already applies. (Heuristic, `UNVERIFIED`.)
- A nominee that is entirely in cash has zero variance and takes the fallback
  `n/h` ≥ 120. Its other gates are unavailable anyway.
- The clamp and fallback are Task 12 choices that are now made governing.

## 2. N-2: the shuffled-labels null (G-14)

**Frozen text:** l.141–145 (`shuffled_labels: samples: 500, gate_metric: "OOS
Spearman IC between model prediction and vol-scaled target"`) and l.289
(`null_minimum_percentile: 0.95`, unqualified). The backtester spec uses a
shuffled-label null as an acceptance canary ("shuffled-label OOS null
centered near zero"). D-14 covers only the random-exposure null.

**The question:** does l.289 make the shuffled-labels null a promotion gate?

| Option | Rule | Consequence |
|---|---|---|
| (a) gate for fitted predictors, N/A otherwise [recommended] | For a nominee whose trial fits a model predicting the vol-scaled target (l.103–105) with an allowed class (l.153), `PASS` iff its OOS Spearman IC is strictly above at least 475 of 500 ICs from refits on shuffled training labels (the same count rule as D-14). `N/A` for trials with no fitted target predictor, by analogy with l.249's precedent for rule-based models. | It reads `gate_metric` and the unqualified l.289 as written. The new `N/A` case needs §4 wording. It costs 500 full walk-forward refits per nominee. |
| (b) canary only | Not a promotion gate; reported, and used as the backtester acceptance test. | Cheap. But it reads l.289 as applying only to the random-exposure null, which the text does not say. |
| (c) gate for every nominee | As (a), with no `N/A`. | Undefined for trials without a target predictor (for example, a vol-family trial whose model forecasts volatility, not the target), so the gate would be `UNAVAILABLE` there, which counts toward `U_proc`. |

**Proposal N2, details for option (a):**
- **Shuffle:** a permutation of the training labels within each walk-forward
  training window, drawn from a stream seeded from the trial seed (l.266),
  purpose `"shuffled_labels_null"` (a D-20 stream). Features, folds,
  retraining cadence (l.198–200), purge and embargo are unchanged.
- **IC:** Spearman rank correlation, over all OOS predictions on the eligible
  window, between prediction and realised vol-scaled target, with midranks for
  ties.
- **Availability:** a non-finite IC (constant predictions or constant target)
  for the nominee or any of the 500 draws makes the gate `UNAVAILABLE`, with
  no replacement.

## 3. A problem for D-19 that these rows expose

P18-7 requires every pre-lockbox gate to be computed for every simulated
nominee in the calibration. Several gates cannot be computed from the
simulated return matrix that Annex B uses:
- G-11 needs exposure paths and the backtester (D-14);
- G-6 and G-7 need delayed re-runs (D-15);
- G-14 needs model refits on labels (this proposal);
- G-3 needs ETH.

So D-19 must either simulate at the level of prices, positions and models, or
argue, deterministically and per gate, why a gate cannot be `UNAVAILABLE`
when the return-level statistics are available. This is recorded here as a
D-19 requirement. The compute cost of option (a) under full simulation is
large (500 refits × nominees × replications).

## 4. Proposed owner questions (after the reviews)

1. "N-1, minimum 120 effective decisions: use the existing, tested
   effective-sample-size formula (adjusting for day-to-day dependence in the
   strategy's returns) as a real pass/fail check. In cycle 2 it will almost
   always pass. Accept / keep blocked?"
2. "N-2, shuffled-labels test: (a) a required check for strategies with a
   prediction model (beat at least 475 of 500 versions trained on shuffled
   data), skipped for strategies without one [recommended]; (b) only a
   software sanity check, not a promotion check; (c) required for all,
   which would make it unavailable for strategies without a model."

Both are filters with no error guarantee of their own. No statistician
reviewed this. Nothing is activated.

## 5. Next

[AI default] Two different-model reviews, adjudication, then the owner's
questions.
