# Adjudication of the reviews of the D-14/D-15 proposal rev2 (`c872066`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`).

Reviews:
- `FABLE_REVIEW_C872066.md` (FN2, UNSOUND, `cb29034`)
- `SOL_REVIEW_C872066.md` (SN2, UNSOUND, `6ddd8c0`)

Both reviews are accepted, and revision 2 is withdrawn. Revision 3 was
redesigned along the line both reviewers suggested. Nothing was put to the
owner.

| Finding(s) | Disposition in rev 3 |
|---|---|
| FN2-1, SN2-1 | The ratio null is replaced by a shift of the declared pre-sizing signal, sized with the trial's own estimator at the real hour (§1.2). The pure-sizing case is now an owner question with options (a)/(b)/(c)/keep blocked, and §12 is cited. |
| SN2-2, FN2-4, FN2-5 | §1.2 states exactly what is held fixed and what is not. The l.137 rewording is offered alongside a tolerance-matching alternative. The constant-multiple claim is removed. |
| SN2-3 | §1.3 adds the numerical domain, reason codes, initial state, warm-up and wrap. |
| FN2-7, SN2-4, FN2-8 | §1.4 offers seeded random vs deterministic shifts as an owner choice. It discloses the power cost and that 30 days is an AI default. 25/501 is labelled hypothetical. The `T_min >= 559` dependency is placed on D-19. |
| FN2-6 | §1.5 discloses L-1 and states E-DIFF's fit. |
| FN2-11 | §1.6 notes that type-7 was the matrix's option (a). The §5 questions are split into ten. |
| FN2-2, SN2-5 | §2.1 gives the full event contract: fill before decision, held-exposure state, order creation and replacement, and a clock set on filled increases (frozen "last risk increase"). |
| SN2-6, FN2-12 | §2.2 gives the information cutoff (the value at `t − 1h`, last emitted), daily aggregates, unchanged items, warm-up and fail-closed behaviour. |
| FN2-3, SN2-7 | §2.3 asks separate questions for G-5, G-7, G-6 and ETH. §10 is presented as evidence. The l.279 ETH-at-1x clause is cited, and changing it is amendment-required. |
| FN2-9, SN2-9 | §2.4 cites l.264 as a partial precedent, makes θ a separate choice, and makes the drawdown part conditional on O-7. |
| FN2-10, SN2-8 | §3 gives a gross vs marginal inventory, including re-inference and option (ii) counts. |
| FN2-13 | Left unedited. The committed FN1 record's "§12 (l.115)" should read l.119; correcting a committed record is the owner's call. |
