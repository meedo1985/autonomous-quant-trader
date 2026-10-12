# Adjudication of the two D-18 re-reviews of `ffbedad` (revision 2)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`), author of the
proposal, so not independent; decides nothing. Records:
`FABLE_REVIEW_FFBEDAD.md` (FR2-1..FR2-13, UNSOUND as written),
`SOL_REVIEW_FFBEDAD.md` (SR2-1..SR2-8, SOUND WITH FIXES).

## Agreement

Both accept `F ⊆ E` for a total, fixed procedure and the top-Sharpe
nomination as a defensible candidate. Both resolve FR-3, FR-4, FR-6, FR-8,
FR-9, SR-1, SR-2, SR-5, SR-6.

| Topic | Fable | Sol | Adjudication |
|---|---|---|---|
| Strictness comparison holds for the DSR stage only; full promotion events not nested | FR2-5 | SR2-6 | Accept; restate. |
| "Single-test meaning" overstated (selected-point CI after max-Sharpe: 1−0.95^81 ≈ 98.4%) | FR2-6 | SR2-5 | Accept; restate as: no fallback limits repetition and lockbox use. |
| Unavailability can make `P(E)=0` vacuously; availability needs an accepted ceiling | FR2-4 | SR2-3 | Accept; owner question. |
| Whole-cycle split 2.5%+2.5% is an extra choice; feasibility at 0.95 not shown | FR2-2, FR2-3 | SR2-7 | Accept. Fable adds known infeasible cells (N=1 ≈5%, ρ=0.9 ≈4.25%); owner re-asked with the consequence. |
| Calibration cells / joint generator underspecified | FR2-3, FR2-11 | SR2-4 | Accept; belongs to D-19/calibration preregistration, D-18 must make the procedure total. |
| Ties / technical invalidation / gate states | FR2-10 | SR2-2, SR2-8 | Accept; fix in text. |

## Found by one reviewer only, accepted

- **FR2-1 (BLOCKER) adaptive trial set:** one fixed look does not fix how many
  trials are run; stopping after a lucky one raises null pass from ~0.2% to up
  to ~8.7% in Fable's model. Owner question.
- **SR2-1 (BLOCKER) no-look families:** a cycle can end (promotion, revision,
  invalidation) before the other family's look; `E_vol` undefined. Owner question.
- **SR2-2 (BLOCKER) threshold comparator:** `NormalDist().cdf(z95)` is
  `0.94999999999999984`, so `z >= z95` and `DSR >= 0.95` disagree at the
  boundary. Fix in text: compare the pre-Φ statistic with a frozen `z95`.
- FR2-7 (D-08 dependency), FR2-8 (estimand names), FR2-9 (`EVALUATION_STARTED`),
  FR2-12 (one unavailable non-nominee blocks the family), FR2-13 (record the
  option descriptions shown to the owner).

## Not repaired here

All findings remain open until revision 3 and the owner's decisions.
No frozen file edited; promotion stays blocked.
