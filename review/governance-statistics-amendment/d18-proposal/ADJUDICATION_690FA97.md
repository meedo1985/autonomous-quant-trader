# Adjudication of the two D-18 reviews of `690fa97`

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`), author of the
proposal under review, so this adjudication is not independent; it decides
nothing. Records: `FABLE_REVIEW_690FA97.md` (FR-1..FR-14, UNSOUND as written),
`SOL_REVIEW_690FA97.md` (SR-1..SR-6, SOUND WITH FIXES).

## Agreement

Both reviewers accept the section 3 identity for a fixed, complete family of
finite scores, and the inclusion `false promotion ⊆ E` under the same
probability law. Both reject the proposal as written for the gaps below.

| Topic | Fable | Sol | Adjudication |
|---|---|---|---|
| Unavailable scores make `E` undefined; define `E` = all scores available AND max >= 0.95, unavailable kept in the denominator | FR-7 | SR-1 | Accept. |
| Global-null calibration does not bound mixed nulls | FR-6 | SR-2 | Accept; claim global null only, mixed nulls as separate challenge. |
| Scope across families / cycles; two opportunities give ~9.75% not 5% | FR-2 | SR-3 | Accept. |
| Selection time / look schedule undefined | FR-1 | SR-3 (nomination time) | Accept; one preregistered look. |
| Ties, Φ saturation, NaN; rank on a stated full-precision key | FR-8 | SR-4 | Accept. |
| Top-DSR differs from the max-Sharpe procedure the motivation was written for | FR-5, FR-12 | SR-6 | Accept; calibrate the max-DSR procedure itself, with non-Gaussian correlated cells. |

## Disagreement

- **Line 74 replacement candidate (FR-3 BLOCKER vs SR-5 NON-BLOCKING).** Sol is
  right that `max_evaluations_per_family_per_cycle: 2` is a ceiling and using
  one is permitted, so P18-2 does not contradict the frozen text. Fable is
  right that while the frozen text still allows a replacement, a single-
  submission bound does not cover the permitted behaviour. Adjudication: the
  amendment must state that the replacement allowance is not used (or the
  calibration must cover two submissions). Treat as a required amendment-scope
  item.
- **Strictness (FR-4).** Fable's exact example (E_S strictly inside E) is
  correct: "top Sharpe, no fallback" passes fewer no-edge strategies than "top
  DSR, no fallback". Sol's "simplest conservative bound" concerns the
  DSR event, not comparison with top-Sharpe. The owner's direction was chosen
  on my incorrect description ("strictest", "simplest to calibrate"), so the
  owner is to be re-asked with the corrected comparison.

## Fable-only items accepted for the revision

FR-9 (call it the "nominated trial"; selection is a function of the DSR score
vector and IDs), FR-10 (list gates from protocol), FR-11 (cite Astra line 208,
not AS-2), FR-13 (matrix authority label, owner's call), FR-14 (owner: decide
D-18 before D-16 closes?).

## Not repaired here

All findings remain open until the proposal is revised and the owner
decides. No frozen file is edited; promotion stays blocked.
