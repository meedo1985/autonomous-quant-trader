# REG-1, REG-2, O-8 proposal (revision 2): sizing that can be registered, and baseline runs under the event contract

**Status:** `NON-BINDING AI PROPOSAL — NOTHING DECIDED — NOT ACTIVE`
**Date:** 2026-10-04
**Author:** Claude Opus 5.5 (`claude-opus-5-5`), as drafting work. Owner items
are decided only by the owner, after two different-model reviews (R19-2).
**History:** rev 1 `370c50c` was reviewed by Fable FR1 (`36e24ab`), SOUND WITH
FIXES, and Sol SR1 (`8a68d02`), UNSOUND. Rev 2 applies
`ADJUDICATION_370C50C.md`. In particular, rev 1's claim that "the Sharpe-based
conclusions carry over" across sizing was **wrong** and is withdrawn (FR1-1,
SR1-2, SR1-3).
**Context:**
- §4 draft rev 6 (`5c89f82`) §7;
- Annex C rev 2, C-6 and C-10 (1);
- `d14-d15-proposal/OWNER_DECISION_D14_D15_ADDENDUM.md` (Q2b re-ask, FC7-3).

## 1. REG-2: may the signal `s` depend on `σ̂`?

**Mechanism (confirmed by FR1 and SR1).** Under C-10, a trial's target is
`overlay(clip(s_h·τ/σ̂_h, 0, 1))`. The G-11 null shifts `s` and re-sizes each
draw with the real-hour `σ̂_h`.

If `s_h = a_h·σ̂_h/τ`:
- the candidate's target is `a_h`;
- draw `k` gets `a_(h+k)·σ̂_(h+k)/σ̂_h`, which carries a mismatched volatility
  ratio that the candidate does not have.

G-11 then measures **sizing misalignment as well as timing**. This can pass
or fail a candidate for reasons unrelated to timing skill (FR1-3):
- a deliberately built signal can pass;
- a plain fixed-size rule tends to fail (FR1 toy: 53 of 500 draws below the
  candidate, where 476 are needed).

**The artifact cannot be closed by a rule on inputs.**
- The frozen features include `rv_24`, `rv_168`, `rv_720`, `ewma_vol_168h` and
  `atr_24` (`factory.py`).
- A signal can also recompute `σ̂` from raw returns.
- A proxy `v = σ̂(1+ε)` keeps almost all of the misalignment as `ε → 0`
  (SR1-1). In FR1's toy, `rv_720` kept about 82% of it and `rv_168` about 68%.
  Real BTC volatility, with longer memory, would likely keep more.
- This is the residual the owner already accepted under D-14 Q3 (a),
  consequence (2): "a signal that only reacts to volatility can pass the
  random-timing check with no price-direction skill". **REG-2 cannot remove
  it.**

**Options:**

| Option | Rule | What it does, honestly |
|---|---|---|
| **(a) Declared-input ban** [recommended] | Each trial declares `s_inputs` (feature names and model ids), and the engine gives `s` only those inputs. `σ̂` and the sizing estimator's output are never among them. Enforcement is §16 code, `<<OPEN D-20>>`. | It stops **accidental or honest** exact cancellation, including writing a fixed size as `0.10·σ̂/τ`. **It does not stop a deliberate declarer**, who can use a close proxy or recompute `σ̂` from prices. The disclosure stays. |
| (b) Allow | No restriction. | Exact cancellation becomes an ordinary, legal registration. Same disclosure. |
| (c) Functional ban | No volatility-level feature may scale `s` multiplicatively. | This partly reverses the owner's D-14 Q3 (a), which credits variance timing inside `s`. It is still not mechanically checkable for model internals. Not recommended. |

## 2. REG-1: can a fixed-size rule (for example the owner's 10%) be registered for C2?

**Frozen position.** Sizing in v1.0 is vol-targeted only:
- `default_sizing_vol_estimator`, l.114–116;
- the vol-family estimators, l.117–122;
- `vol_target_trial_dimension` ∈ {0.40, 0.60, 0.80}, l.126–128.

A fixed-size mapping needs a **new amendment clause**. Under REG-2 (b), or
through a proxy under (a), an approximately fixed size can still be written
as `s = 0.10·v/τ`. It then inherits §1's misalignment problem.

**What size does to each statistic** (corrected; FR1-1, SR1-2, SR1-3).
- **`E-IMPROV`** = Sharpe(C) − Sharpe(B), used by G-1, G-4, G-8 and G-11.
  Multiplying a *given* candidate return series by a constant leaves it
  unchanged. Clipping, the 0.10 band, costs (charged before the exposure
  return) and drift all break exact invariance (SR1-3).
- **`E-DIFF`** = Sharpe(C − B), used by **DSR (the only error-controlled
  test) and PBO**, depends strongly on size.
  - If C is small, C − B ≈ −B, so `E-DIFF` ≈ −Sharpe(B).
  - FR1 toy, same entry signal at size 0.1 / 0.5 / 1.0: `E-DIFF` −1.94 /
    −1.61 / −0.74, while `E-IMPROV` stays −0.30.
  - SR1 toy: scaling a candidate by 0.1 moved `E-DIFF` from +0.48 to −0.57.
- **Drawdown** (G-2 and the drawdown parts of G-3, G-5, G-6, G-7): a smaller
  exposure makes these checks **materially easier, and potentially weak**.
  There is no fixed ratio, because the benchmark itself varies in size, and
  costs, repeated stops and compounding all matter (SR1-4, FR1-6). This holds
  for any candidate with less exposure than the benchmark, not only fixed
  size.
- **Vol-target sizing is a different strategy, not a rescaled 10%.** It is
  vol-timed, it resizes at 00:00 whenever `τ/σ̂` moves by 0.10 or more, and
  its costs and turnover differ. FR1 toy, same entry: `E-IMPROV` −0.30 at
  fixed size, +0.02 vol-targeted.

**So a test under vol-target sizing does not tell the owner whether his 10%
rule works.** It tests a different strategy that shares only the entry/exit
logic.

**A fixed 10% is very unlikely to pass C2's DSR.** The DSR asks whether
candidate-minus-benchmark has a positive Sharpe. When the position is much
smaller than the benchmark's, that difference is dominated by "short the
benchmark". So a small fixed size is very unlikely to be promoted against
`VOL_TARGET_BUY_AND_HOLD`, unless the benchmark did poorly over the window.
This is a qualitative argument backed by toys, not a computed probability.
It is a property of the decided selection rule (D-18, E-DIFF), not of the
owner's idea.

**What the owner's rule is missing in any case** (FR1-5, SR1-3). The
recorded rule has no entry trigger. With "always enter when flat", it is
`constant_signal`, and G-11 is `N/A`. A real entry signal would have to come
from research. Other differences, under any option:
- the stop is checked at hourly instants and filled at the next open;
- at 10% a stopped trade risks about 0.05% of equity, while at vol-target
  size it risks up to about 0.5% plus costs.

**Options:**

| Option | Rule | Consequence |
|---|---|---|
| **(a) Not in C2** [recommended] | C2 registers only the C-10 vol-targeted form. | The owner's fixed-10% rule is **not tested** in C2. A *different* hypothesis can be registered once research supplies an entry signal: that signal with the −0.5% / +10% overlay, at vol-target size. Its result says nothing directly about 10% sizing. The 10% stays a deployment choice, governed by L-01..L-04. No new clause and no new trial dimension. |
| (b) Add a `fixed_size` class | Target `overlay(clip(c·e_h, 0, 1))`, with a declared constant `c` and an entry signal `e_h ≥ 0` that may not read `σ̂`. G-11 shifts `e` and keeps `c`. `c` becomes a counted structural dimension. | This is the only route that tests the 10% rule as such. It needs new clauses (protocol §2, Annex C C-10), a new review round and D-19 modelling. **At small `c` it is very unlikely to pass the DSR (above)**, while the drawdown checks become lenient. |

## 3. O-8: does the full event contract govern baseline and benchmark runs?

**Checked against the code by the drafter, FR1 and SR1** (SR1 also ran the
targeted synthetic tests: 542 passed, 4 skipped):
- **Fills.** `engine.py` resolves the fill at the decision instant: l.210,
  through `costs.py` l.400–420 (`baseline_execution`). l.225–235 compute the
  segment return and the clip (FR1-7).
- **Drift.** Held exposure drifts between segments (`_drifted_exposure`,
  l.138, used at l.296–298).
- **Rebalance rule.** `canonical.py` `rebalance` (l.690–785):
  - tests the band against drifted exposure;
  - allows an increase only at 00:00 and after 24 h, where an unset clock
    (`None`) permits it (l.767);
  - sets the clock to the decision time of an increase (l.783);
  - allows reductions across the band at any hour.
- **Clamp and direction rule.** With no delay, both are inert.
- **One difference in float handling.** The band test is
  `reaches_rebalance_band`, which uses `≥ 0.10 − 4·ulp(1.0)` (`canonical.py`
  l.232, l.402–412), while C-6 says `≥ 0.10`. Rev 2 proposes that C-6 read the
  band through that routine, with its binding under `<<OPEN D-20>>` (FR1-7).

**So at baseline the contract equals current behaviour plus N-4.** N-4 is
already decided. N-4 cannot change any canonical benchmark's values:
- vol-target never targets 0;
- trend and TSMOM targets move between 0 and 1;
- CASH and BUY_AND_HOLD are constant.

The benchmark **text**, and so its hash, changes. Unchanged **values** are
expected but **unverified** until the v1.1 code exists.

| Option | Consequence |
|---|---|
| **(a) Confirm: the full contract governs every run** [recommended] | One engine semantics. Nothing changes measurably beyond N-4. |
| (b) Only gate, stressed and null runs | A second specification for baseline runs, with no practical difference. |

## 4. O-6a channel candidates (for the question; to be verified)

The channel must meet four requirements (DRAFT §2.0): authentication, append-only, third-party timestamp, independent archive.
- **Sigstore Rekor** (public transparency log) with a dedicated signing
  identity. It is append-only, it gives each entry an integrated timestamp
  and an inclusion proof, and entries are searchable by identity.
  **Unverified, from memory.** Check against official Sigstore documentation
  before the question is asked.
- **A trusted third party.** If the owner wants no public post, O-6 is
  re-asked instead.
- **Ordinary social or code-hosting accounts** (posts can be deleted, history
  rewritten): they fail requirement (2) and are not candidates.

The post is a bare hash. It reveals nothing about the strategies.

## 5. Consequences (all options)

- No error rate is claimed. These are definitions, not tests.
- REG-2 (a) is enforced at declaration and by input restriction at run time
  (`<<OPEN D-20>>`). A violation invalidates the declaration; it does not make
  a gate `UNAVAILABLE`. [AI default]
- No statistician reviewed this.

## 6. Proposed owner questions (neutral; each also allows "revise" or "keep blocked")

1. **REG-2.** Should a strategy's signal be barred from using its own
   volatility-sizing number? If a signal uses it, the random-timing check
   partly measures sizing mismatch instead of timing skill.
   - (a) Bar it through declared inputs [recommended]. Accidental misuse is
     stopped, but a deliberate near-copy of the number (other volatility
     features) stays possible. That residual is the one you already accepted
     in D-14.
   - (b) Allow it.
2. **REG-1.** Can a fixed-size rule like your 10% be registered for C2?
   - (a) Not in C2 [recommended]. Your 10% rule itself is **not** tested.
     Later, an entry/exit idea can be tested at volatility-targeted size,
     which is a different strategy, and its result does not tell you how 10%
     would do. 10% stays your deployment choice under the loss bounds.
   - (b) Add a fixed-size class. This is the only way to test 10% itself. It
     needs another drafting and review round, and at 10% the strategy is very
     unlikely to pass the main statistical test against the benchmark.

   Either way, your rule needs a real entry signal from research before it
   can be a testable strategy.
3. **O-8.** Do the order and fill rules apply to normal backtests too? Checked
   against the code, this changes nothing beyond the exits-to-zero rule you
   already chose. It is confirmed only once the new code exists.
   - (a) Yes [recommended]
   - (b) Only to the test runs
4. **O-6a.** The single hash post needs one dedicated identity that verifies
   who posted, can never edit or delete, carries an outside timestamp and is
   archived. The post is a bare fingerprint and reveals nothing about your
   strategies. The candidate is a public transparency log (Sigstore Rekor,
   to be verified). Alternative: no public post, with a trusted third party
   holding the fingerprint, in which case the seed question O-6 is re-asked.
5. **O-9.** If a cycle is invalidated after its hash post (for example a
   second post, a mismatch, or no beacon value within 7 days), is the window
   used up?
   - (a) No [recommended]. The window can be reused, and each such
     invalidation costs one halving of the false-promotion allowance. A
     declarer who sees the seed and aborts pays only that halving.
   - (b) Yes. C2's window is the only eligible one, so any such invalidation
     ends promotion for **both** families.
