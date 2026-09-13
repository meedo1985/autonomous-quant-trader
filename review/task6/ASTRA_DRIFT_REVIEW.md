# Task 6 — Astra High accounting gate

Date: 2026-09-13

**LOCAL GATE: PASS — no remaining accounting defect under the accepted convention.**

Astra High performed the final high-impact read-only review. It found that an
adverse return could make an unchanged fractional target look like an intraday
risk increase; the first sequential oracle raised instead of holding. The
minimal correction now matches Task 5: forbidden intraday or minimum-hold
increases leave actual exposure unchanged and charge no turnover.

Astra verified the exact no-trade drift equation, target-versus-actual tracking,
clipping, inclusive band, scheduled/minimum-hold increases, intraday reductions,
cost-before-return ordering, all 16 binary daily paths, invalid boundaries, and
an increase exactly 24 hours after entry. The exact adverse-drift regression
records exposure `(1/2, 1/3)`, turnover `(1/2, 0)`, and gross equity `3/4`.

Final evidence: 58 focused passes; 783 full-suite passes with four pre-existing
skips; Ruff, mypy, four import contracts, frozen bytes/sidecars/bindings,
whitespace, and Task 6 scope pass. Astra made no edits and found no NumPy,
production, or Task 7 implementation.
