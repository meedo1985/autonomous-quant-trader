# Adjudication of the reviews of the D-14/D-15 proposal rev3 (`540e773`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`).

Reviews:
- `FABLE_REVIEW_540E773.md` (FN3, SOUND WITH FIXES, `0c141a5`)
- `SOL_REVIEW_540E773.md` (SN3, SOUND WITH FIXES, `40e1266`)

Both reviewers verified the core signal-shift construction with exact
examples. All findings are accepted; none is rejected. They are applied in
revision 4.

| Finding(s) | Disposition in rev 4 |
|---|---|
| FN3-1 | §2.1 states the 23 h block. The clock anchor is owner question Q10; the recommendation is the decision time of an increase that was later filled. "≥ 24 h" is stated. |
| FN3-2 | §2.1 treats timestamps as instants. A baseline order fills at the same instant, and a stressed order is due at the next instant. Fill-first ordering means no order is ever replaced. |
| FN3-3, SN3-1 | §1.2 makes the separable form a G-11 applicability contract, with a preregistered `N/A` outside it. The signal may be hourly, must depend only on market and model data, and is part of the hashed interface. Restricting C2 eligibility is offered as Q1b. The owner's recorded rule is named as outside the class. |
| FN3-4 | §1.2 limits the alignment claim to `σ̂`. §1.3 / Q3 asks whether to credit variance timing in `s` (recommended) or treat it as sizing. |
| FN3-5, SN3-3 | §1.6 states the tie consequence for each pass rule. Under type-7, a candidate that ties all draws passes. The clone and "always fail" sentences are corrected. |
| FN3-6, SN3-2 | §1.1 defines `T`, `g`, 0-based indexing, BTC and 1x cost. §1.5 lists all unavailable routes, says no draw is replaced, and keeps the denominator at 500. `i = 0…499` is stated. |
| FN3-7 | §2.1 applies the l.112 band to 00:00 increases [AI default]. |
| FN3-8 | §2.1: held exposure drifts with price [AI default]. |
| FN3-9 | §2.2 / Q11 offers recomputing with cutoff `t − 1h` (recommended) or last-emitted (up to 24 h; the "25 h" in rev 3 is corrected). |
| FN3-10 | §1.5 cites `excluded_days_status` for warm-up. Q5 asks whether warm-up may read the gap days. |
| FN3-11 | §1.2 states that the G-11 `na` field must change and the P18-7 exception applies. |
| FN3-12, SN3-6 | §2.3 opens a new row N-3 for G-5's stress semantics. Separate questions Q12–Q17 cover the BTC and ETH legs of G-5, G-6 and G-7, including the G-5 ETH point estimate. |
| FN3-13 | §3 adds the counts for each ETH option and 0 runs for a preregistered `N/A`. |
| FN3-14 | Accepted. The rev-4 history attributes the signal-shift design to SN2-1. The committed `ADJUDICATION_C872066.md` l.9–10 is left as is; this record corrects it. |
| FN3-15 | §2.3 cites l.42–43. |
| SN3-4 | §1.5: the source of `g` and the floor `f` are a separate question (Q6); the sampling mechanics are left to D-20. |
| SN3-5 | §2.1: an order stores an absolute target, and an unset clock permits the first increase. |
| SN3-7 | §2.4: `0 ≤ θ ≤ 1`; an unavailable unstressed statistic makes the gate `UNAVAILABLE`. |
| SN3-8 | The term "preregistered `N/A`" is used throughout, and it is amendment-required. |

**Review cadence [AI default].** Revision 4 changes only bounded text and adds
owner questions; the core construction is unchanged. A focused check of the
3 → 4 diff by both families follows before the owner is asked.
