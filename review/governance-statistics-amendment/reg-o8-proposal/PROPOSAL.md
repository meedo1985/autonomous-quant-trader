# REG-1, REG-2, O-8 proposal (revision 1): sizing that can be registered, and baseline runs under the event contract

**Status:** `NON-BINDING AI PROPOSAL — NOTHING DECIDED — NOT ACTIVE`
**Date:** 2026-10-04
**Author:** Claude Opus 5.5 (`claude-opus-5-5`), as drafting work. Owner items
are decided only by the owner, after two different-model reviews (R19-2).
**Context:** §4 draft rev 6 (`5c89f82`) §7; Annex C rev 2 C-6 and C-10 (1);
`d14-d15-proposal/OWNER_DECISION_D14_D15_ADDENDUM.md` (Q2b re-ask, FC7-3);
`ADJUDICATION_AB9AD3F.md` (FA5-2, SA5-1, SA5-2).

## 1. REG-2: may the signal `s` depend on `σ̂`?

**The mechanism.** Under C-10, a trial's target is
`overlay(clip(s_h·τ/σ̂_h, 0, 1))`. The G-11 null shifts `s` and re-sizes each
draw with the **real-hour** `σ̂_h`.

**What goes wrong if `s` contains `σ̂`.** Suppose `s_h = a_h·σ̂_h/τ`. The
candidate's target is then `a_h`, with no vol scaling at all. Draw `k`, by
contrast, gets `a_(h+k)·σ̂_(h+k)/σ̂_h`: a shifted entry multiplied by a
mismatched vol ratio. The draws carry sizing noise that the candidate does
not have. A candidate can then beat most draws because the draws are mis-sized,
not because its timing is good. This is the situation FN3 called exact only
"for signals that do not depend on volatility". It is also why the corrected
Q2b question said the check "would test something unrelated" for a fixed
10% rule.

**Options:**

| Option | Rule | Consequence |
|---|---|---|
| **(a) No** [recommended] | `s` may not take the trial's declared sizing estimator `σ̂` (its output, or that estimator recomputed) as an input, directly or through a declared model. This is checked mechanically from the hashed interface (Constitution l.97). | It closes the exact cancellation route. **Residual, already accepted under D-14 Q3 (a):** other volatility features remain allowed and credited. A feature that closely tracks `σ̂` can still partly reproduce the effect. |
| (b) Yes | No restriction. | G-11 can be passed through vol-ratio misalignment, with no timing skill. Fixed sizes become expressible (see REG-1). |

## 2. REG-1: can a fixed-size rule (for example the owner's 10%) be registered for C2?

**Frozen position.** Sizing in v1.0 is vol-targeted only:
- `exposure_mapping.default_sizing_vol_estimator` (l.114–116);
- the vol-family estimator set (l.117–122);
- `vol_target_trial_dimension` ∈ {0.40, 0.60, 0.80} (l.126–128).

v1.0 has no fixed-size mapping. So under REG-2 (a), a fixed size cannot be
registered without a **new amendment clause**. Under REG-2 (b) it could be
written as `s = 0.10·σ̂/τ`, which has the G-11 problem in §1.

**Scale matters less than it looks.**
- Most gate statistics are Sharpe-based (`E-IMPROV`, `E-DIFF`, G-11, G-4,
  G-8, PBO). Multiplying a position by a constant leaves its Sharpe
  unchanged, and costs scale with it too.
- The exceptions are clipping at exposure 1 and the 0.10 band, which a small
  size makes harder to cross.
- So whether the owner's entry/stop/take-profit idea has an edge can be
  tested at vol-target size. The 10% is a **deployment** choice, made later
  together with the loss bounds (L-01..L-04). It is not a research choice.

**One gate is not scale-free: G-2 (drawdown).** G-2 compares absolute
drawdowns, with a tolerance of 5 points. A trial held at 10% exposure has
roughly a tenth of the benchmark's drawdown, so it passes G-2 and the
drawdown parts of G-3, G-5, G-6 and G-7 almost automatically. A
fixed-small-size class would make those checks close to inert for it.

**Options:**

| Option | Rule | Consequence |
|---|---|---|
| **(a) Not in C2** [recommended] | C2 registers only the C-10 vol-targeted form. The owner's rule can be registered as an entry signal `s ∈ {0, 1}` (or ≥ 0) with an overlay at −0.5% stop / +10% take-profit, sized by `τ/σ̂`. | No new amendment clause, no new trial dimension, and G-11 works as decided. The tested position is larger than 10%, but the Sharpe-based conclusions carry over. Deployment size stays the owner's later choice. Stop/take-profit timing stays untested by G-11 (Q2b (A), already accepted). |
| (b) Yes, a new `fixed_size` class | The target is `overlay(clip(c·e_h, 0, 1))`, with a declared constant `c` and an entry signal `e_h ≥ 0` that may not read `σ̂`. G-11 shifts `e` and keeps `c`. `c` becomes a declared structural dimension, counted in trials. | It needs new clauses in protocol §2 and Annex C C-10, and a fresh two-model review. G-2-type drawdown checks become nearly inert at small `c`. D-19 must model the class. |
| (c) Yes, via REG-2 (b) | `s = c·σ̂/τ`. | It inherits the G-11 misalignment pass in §1. Not recommended under any reading. |

## 3. O-8: does the full event contract govern baseline and benchmark runs?

**Concrete effect, checked against the code at this commit:**
- `src/aqt/backtest/engine.py` already does the following:
  - it fills at the decision instant over open-to-open segments (l.225–235);
  - it drifts held exposure with price between segments (`_drifted_exposure`,
    l.138, used at l.296–298);
  - it tests the band against that drifted exposure.
- `src/aqt/benchmarks/canonical.py` `rebalance` (l.690–785) matches the
  contract's decision rule:
  - it allows an increase only at 00:00 and only after 24 h, and an unset
    clock (`None`) permits the increase;
  - it sets the clock to the decision time of the increase (l.783), and a
    same-instant fill makes that equal to the fill time;
  - it tests reductions against the band at any hour.
- Without an execution delay, the clamp and the decision-time direction rule
  never come into play, because no price moves between decision and fill.

**So at baseline, the contract differs from current behaviour only by N-4:**
an exit to 0 is never blocked by the band. N-4 is already decided for all
runs. For the canonical benchmarks, even N-4 changes nothing:
- `VOL_TARGET_BUY_AND_HOLD` targets `clip(0.60/σ̂, 0, 1)`, which is never 0
  for a finite `σ̂`;
- the trend and TSMOM benchmarks move between 0 and 1, a change of 1.0 that
  always crosses the band.

The v1.1 benchmark **text** changes, so the benchmark hash changes (G-13). The
benchmark **values** are expected to stay the same. This expectation is
unverified until the v1.1 code exists.

| Option | Consequence |
|---|---|
| **(a) Confirm: the full contract governs every run** [recommended] | Every run shares one engine semantics, which is already the engine's baseline behaviour plus N-4. No measurable change is expected beyond N-4. |
| (b) Only gate, stressed and null runs | Baseline runs would follow a different text that the engine does not implement differently. That adds a second specification with no practical difference. |

## 4. Consequences (all options)

- No error rate is claimed for any of this. These are definitions, not
  statistical tests.
- REG-2 (a) is enforced at declaration from the declared interface. A
  violation makes the declaration invalid; it does not make a gate
  `UNAVAILABLE`. [AI default]
- REG-1 (a) leaves the owner's 10% for the deployment stage. If the owner
  wants the 10% tested as such, (b) is the route. It costs another
  proposal-and-review round.
- No statistician reviewed this.

## 5. Proposed owner questions (neutral; each also allows "revise" or "keep blocked")

1. **REG-2:** may a strategy's signal use its own volatility-sizing estimate?
   - (a) No [recommended]
   - (b) Yes
2. **REG-1:** can a fixed-size rule like your 10% be registered for C2?
   - (a) Not in C2: test the idea at vol-target size, and choose 10% later
     for deployment [recommended]
   - (b) Add a fixed-size class
3. **O-8:** do the order/fill rules apply to normal (baseline) backtests too?
   This has no practical effect beyond the exits-to-zero rule you already
   chose.
   - (a) Yes [recommended]
   - (b) Only to the test runs
4. **O-6a:** which public account carries the single hash post? It must be
   one dedicated account that cannot edit or delete, with a third-party
   timestamp and an archive copy.
5. **O-9:** if a cycle is cancelled after its hash post, is the window used
   up?
   - (a) No; it still costs one halving of the allowance [recommended]
   - (b) Yes
