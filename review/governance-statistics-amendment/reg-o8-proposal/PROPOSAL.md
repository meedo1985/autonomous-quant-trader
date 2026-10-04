# REG-1, REG-2, O-8 proposal (revision 5): sizing that can be registered, and baseline runs under the event contract

**Status:** `NON-BINDING AI PROPOSAL — NOTHING DECIDED — NOT ACTIVE`
**Date:** 2026-10-04
**Author:** Claude Opus 5.5 (`claude-opus-5-5`), as drafting work. Owner items
are decided only by the owner, after two different-model reviews (R19-2).
**History:** rev 1 `370c50c` was reviewed by Fable FR1 (`36e24ab`), SOUND WITH
FIXES, and Sol SR1 (`8a68d02`), UNSOUND. Rev 2 applies
`ADJUDICATION_370C50C.md`. In particular, rev 1's claim that "the Sharpe-based
conclusions carry over" across sizing was **wrong** and is withdrawn (FR1-1,
SR1-2, SR1-3). Rev 3 applies Fable's focused check FR2 (`4f230cb`, NOT READY)
and the verified Sigstore facts. Sol's focused check SR2 was stopped by the
system for low memory before it returned any output, so revision 2 has only
one family's check. Rev 4 applies Sol's check SR3 (`26f3615`, NOT READY), and
takes O-6a out of this batch (§4). Rev 5 applies Fable's narrow check FR4
(`6b7a5f2`).
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
- **One frozen feature is not a proxy but `σ̂` itself.** `ewma_vol_168h` is
  identical by construction to the default sizing estimator `EWMA_168h`
  (`canonical.py` l.54–55, l.450–453; `factory.py` l.63, l.355; FR2-3). For a
  trial with default sizing it gives exact cancellation; for a trial sized by
  another vol-family estimator it is a close proxy.
- The other frozen volatility features (`rv_24`, `rv_168`, `rv_720`,
  `atr_24`) are proxies.
- A signal could also recompute `σ̂` if a declared model has access to return
  history (FR2-6).
- A proxy `v = σ̂(1+ε)` keeps almost all of the misalignment as `ε → 0`
  (SR1-1). In FR1's toy, `rv_720` kept about 82% of it and `rv_168` about 68%.
  Real BTC volatility, with longer memory, would likely keep more.
- This residual is **closely related to** what the owner accepted under
  D-14 Q3 (a), consequence (2), and wider than it. That consequence says "a
  signal that only reacts to volatility can pass the random-timing check with
  no price-direction skill". Sizing misalignment can also make a candidate
  **fail** for reasons unrelated to its timing, and a deliberate construction
  can pass through misalignment rather than through variance timing (FR2-5).
  **REG-2 cannot remove this residual.**

**Options:**

| Option | Rule | What it does, honestly |
|---|---|---|
| **(a) Declared-input ban** [recommended] | Each trial declares `s_inputs` (feature names and model ids), and the engine gives `s` only those inputs. `σ̂`, the sizing estimator's output and **any frozen feature identical to it** (currently `ewma_vol_168h` for a trial sized by `EWMA_168h`) are never among them. The identity mapping and its enforcement are §16 code, `<<OPEN D-20>>`. | It stops **accidental or honest** exact cancellation, including writing a fixed size as `0.10·σ̂/τ`. **It does not stop a deliberate declarer**, who can use a close proxy or recompute `σ̂` from prices. The disclosure stays. Honest variance-timing signals with default sizing lose `ewma_vol_168h` as an input; the other volatility features remain available. |
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

**At 10%, C2's DSR may mostly measure the benchmark.** The DSR asks whether
candidate-minus-benchmark has a positive Sharpe. When the position is much
smaller than the benchmark's, that difference is often dominated by "short
the benchmark", so the DSR verdict may say little about the 10% rule itself.

**No pass probability is claimed** (SR3-3). Size alone does not make
C − B ≈ −B: strong timing can still give a positive E-DIFF. In SR3's exact
synthetic example, a perfectly predictive 10% signal gave E-DIFF +1.71 while
the benchmark's Sharpe was +0.03. A poor benchmark window and a genuine
timing edge are separate routes to a pass. The pass probability is unknown
until the signal, the family, the window and the D-19 critical value are
fixed.

All of this follows from the decided selection rule (D-18, E-DIFF). None of
it is a verdict on the owner's idea.

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
| (b) Add a `fixed_size` class | Target `overlay(clip(c·e_h, 0, 1))`, with a declared constant `c` and an entry signal `e_h ≥ 0` that may not read `σ̂`. G-11 shifts `e` and keeps `c`. `c` becomes a counted structural dimension. | It tests the 10% rule on the improvement checks (G-1, G-4, G-8, G-11). But at small `c` the main promotion test (the DSR, on E-DIFF ≈ −Sharpe of the benchmark) mostly measures **how the benchmark did over the window, not the rule**. The DSR verdict may then be poorly informative about the rule. Its pass probability is unknown until D-19 (FR2-4, SR3-3). The drawdown checks become lenient. It also needs new clauses (protocol §2, Annex C C-10), a new review round and D-19 modelling. |

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

## 4. O-6a: deferred, not asked in this batch

The channel only has to be fixed **before signing**. It does not affect REG,
O-8 or O-9. It needs its own specification and review, so it is taken out of
this batch and stays `<<OWNER O-6a>>` in the draft.

**Established so far:**
- **Sigstore Rekor is rejected** (verified 2026-10-04).
  - Rekor is append-only (docs.sigstore.dev/logging/overview).
  - Rekor v2 removed the search index, and v1 will eventually be frozen
    (blog.sigstore.dev/rekor-v2-ga). So there is no supported way to list
    every entry by one identity.
  - Keyless signing makes the signer's identity public.
- **Bitcoin OP_RETURN candidate**, per an older developer guide that is
  no longer maintained (developer.bitcoin.org/devguide/transactions.html,
  read 2026-10-04). Current Bitcoin Core relay defaults are to be checked
  when O-6a is specified (FR4-2).
  - Null-data outputs are standard, "relayed and mined by default", and
    "provably unspendable".
  - That guide gives a default relay limit of **83 bytes**, and the DRAFT
    §2.0 message text is about 90 bytes. A reviewer recalls that later
    Bitcoin Core versions raised the default; this is unverified. Either
    way, a short prefix plus the raw 32-byte hash is the safe design.

**Before O-6a is asked, the specification must define** (SR3-2):
- the fixed key or script, and which spend counts as a post. Bitcoin has
  spends of outputs, not posts "from an address", and an inbound payment
  authenticates nothing;
- how all posts are listed;
- a confirmation depth that guards against reorganizations;
- the canonical timestamp. Block time is only bounded, so a
  confirmation-based time may be needed;
- evidence of an independent archive. Pruned nodes do not keep a permanent
  copy;
- the fee and funding lifecycle;
- a privacy disclosure: funding the address can link it to the owner.

The trusted-third-party alternative remains. Otherwise O-6a stays blocked,
and the amendment cannot be signed until it is resolved.

## 5. Consequences (all options)

- No error rate is claimed. These are definitions, not tests.
- REG-2 (a) is enforced at declaration and by input restriction at run time
  (`<<OPEN D-20>>`). A violation invalidates the declaration; it does not make
  a gate `UNAVAILABLE`. [AI default]
- No statistician reviewed this.

## 6. Proposed owner questions (neutral; each also allows "revise" or "keep blocked")

1. **REG-1 and REG-2 together, because they interact (FR2-2).** This
   question decides what sizing a C2 strategy may use, and whether its signal
   may use its own volatility-sizing number. If the signal uses that number,
   the random-timing check partly measures a sizing mismatch rather than
   timing skill. That can wrongly pass a deliberately built strategy, or
   wrongly fail an honest one.
   - **(A) Vol-target sizing only, and the sizing number is barred from the
     signal** [recommended].
     - This bars **direct** use of the number and stops accidental misuse.
       It does not stop a deliberate builder: a model allowed to read price
       history could rebuild the exact number, and other volatility features
       can approximate it (SR3-1).
     - So your 10% rule cannot be registered directly. A deliberately built
       exact or near-10% version stays possible, and the random-timing check
       judges such a version unreliably.
     - Honest variance-timing signals with default sizing lose one input,
       `ewma_vol_168h`, which equals the sizing number. The ban also needs
       new protected code (decided later, under D-20).
     - An entry/exit idea can later be tested at vol-target size. That is a
       different strategy, and its result does not tell you how 10% would do.
     - 10% stays your deployment choice under the loss bounds.
   - **(B) Vol-target sizing only, and the sizing number is allowed.** Your
     10% can be written exactly ("signal = 0.10 × volatility / target") and
     registered. The random-timing check then judges it unreliably: a plain
     version tends to **fail** that check, for reasons unrelated to its
     timing.
   - **(C) Add a separate fixed-size class, and keep (A)'s ban for the
     normal vol-target strategies.** This is the cleanest way to register
     10% itself (FR4-1).
     - It is checked on the improvement tests.
     - At 10% the main promotion test may mostly measure how the benchmark
       did over the window, so its verdict may say little about your idea.
       Its chance of passing is unknown until the statistical calibration
       (D-19) is done.
     - At 10%, the drawdown checks also become easy to pass.
     - It needs another drafting and review round.

   Under any choice, your rule needs a real entry signal from research before
   it becomes a testable strategy. If none of (A), (B) and (C) is acceptable,
   choose "keep blocked".
2. **O-8.** Do the order and fill rules apply to normal backtests too?
   Checked against the code, this changes nothing beyond the exits-to-zero
   rule you already chose. The benchmark definitions get new fingerprints,
   and their values are expected not to change; that is confirmed only once
   the new code exists.
   - (a) Yes [recommended].
   - (b) Only to the test runs.
3. **O-9.** If a cycle is invalidated after its fingerprint post (a second
   post, a mismatch, or no beacon value within 7 days), is the window used
   up?
   - (a) No [recommended]. The window can be reused, and each such
     invalidation costs one halving of the false-promotion allowance. A
     declarer who sees the seed and aborts pays only that halving.
   - (b) Yes. C2's window is the only eligible one, so promotion ends for
     **both** families until a later amendment creates a new eligible window.
