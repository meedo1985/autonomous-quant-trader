# Adjudication of the reviews of the D-14/D-15 proposal rev1 (`0f16e97`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`).

Reviews:
- `FABLE_REVIEW_0F16E97.md`: FN1, UNSOUND, commit `317a3fc`.
- `SOL_REVIEW_0F16E97.md`: SN1, UNSOUND, commit `d4162c2`.

Both reviews are accepted. Revision 1 is withdrawn. D-14 and D-15 stay blocked
until a redesigned revision 2 has had two further reviews. Nothing was put to
the owner from revision 1.

## Why revision 1 fails

**D-14 (random-exposure null).**
- Circularly shifting the candidate's own exposure path moves vol-scaled
  positions into the wrong volatility regimes. The benchmark keeps that
  alignment, so the null draws are penalised for misalignment, not only for
  losing timing.
- A zero-skill vol-targeting candidate can therefore beat its own shifts.
  Fable proved this exactly: Sharpe² 1 vs 25/43, with Sharpe maximised by
  constant risk exposure. The gate becomes inert (FN1-1).
- The hourly input object is undefined (FN1-2).
- Realised mean exposure and turnover are not matched as the frozen text
  requires. The minimum hold, the bands and the initial state all change them
  (SN1-1).
- The shift universe is under-specified (SN1-2).
- The estimand `E-IMPROV` was presented as already decided; it is not
  (FN1-11, SN1-3).
- The 475 count rule is not "stricter than type-7" (the two rules are not
  nested), and its level is 26/501 = 5.19% (FN1-3, FN1-4, SN1-4).
- C-3's example is wrong (FN1-9, SN1-7).
- The stream belongs to D-20 and is new code (FN1-10).
- The minimum shift ignores how persistent the exposure is (FN1-14).

**D-15 (delay gates).**
- It does not say whether the benchmark leg is also delayed. Constitution §10
  l.111 requires identical semantics. The same gap exists, inherited, in the
  already-decided G-5 (FN1-5).
- The feature-delay scope (FN1-6), the min-hold clock (FN1-7) and the
  pending-order and boundary semantics (SN1-5) are undefined.
- Mirroring the 2x-cost rule tests survival, not bounded degradation. That
  must be stated as a choice (SN1-6).
- The workload and simulability consequences were understated (FN1-8,
  SN1-8).
- The owner questions bundled several separate choices (FN1-13, SN1-9).

## Redesign brief for revision 2

1. **D-14 null object.** Shift the **pre-sizing signal**, not the sized
   exposure. Each null draw is then sized by the same frozen vol rule at its
   own dates, so vol alignment is kept and only signal timing is broken.
   Alternatives to present to the owner: shifting the ratio of candidate to
   benchmark exposure, or shifting the full exposure.
   - "Match mean exposure and turnover" (l.136) is then met on the signal, not
     on realised exposure. Owner options: amend the word "match", or require
     realised matching within a stated tolerance (SN1-1).
   - Define the hourly object: shift the whole hourly signal path by 24k h,
     then re-run the backtester (FN1-2).
   - Define the modular shift universe, identity exclusion, minimum shift
     from exposure autocorrelation and embargo, uniqueness, and the
     availability check from the declared `T` and `g` (SN1-2, FN1-14).
   - For a vol-family trial whose "signal" is the vol forecast itself, say
     whether better forecasting counts as timing skill (FN1-1). This is an
     owner choice.
2. **D-14 estimand and rule.** `E-IMPROV` versus `E-DIFF` is a fresh choice
   (SN1-3). The percentile rule is offered as three options: type-7, rank 475,
   or plus-one Monte Carlo (≥ 476, level ≤ 25/501). The tie rule must be
   explicit. Keep consistent with N-2, which is decided at ≥ 476 (FN1-4).
3. **D-15 temporal contract.** Specify every action type: daily increases,
   intraday band reductions, pending orders, and cancellation and
   replacement. Also cover feature and state availability, which items lag
   (training, inference, sizing σ, slippage σ), the min-hold clock, window
   boundaries, BTC and ETH, and **the benchmark leg** (FN1-5, FN1-6, FN1-7,
   SN1-5).
4. **One §10 decision for G-5, G-6 and G-7.** Is the benchmark stressed
   identically under the 2x cost and both delays? G-5 is already decided as an
   estimand (D-02), but its stress semantics are open. This is presented as
   one owner decision citing §10 (FN1-5).
5. **D-15 statistic.** Survival (mirror l.283) versus bounded degradation, as
   an owner choice, with the consequence of each disclosed (SN1-6).
6. **Workload.** A per-replication inventory for D-19 (SN1-8, FN1-8). This
   links to N-1/N-2 rev 2 §3: either compute every gate, or have the
   amendment authorise a certification route.
7. **Owner questions.** Split into separate questions (SN1-9, FN1-13): null
   object, estimand, percentile and ties, feature-delay semantics,
   execution-delay semantics, benchmark under stress (§10), and survival
   versus degradation. Each keeps revise and keep-blocked options.

All findings FN1-1..FN1-14 and SN1-1..SN1-9 are accepted. None is rejected or
deferred without a disposition above.
