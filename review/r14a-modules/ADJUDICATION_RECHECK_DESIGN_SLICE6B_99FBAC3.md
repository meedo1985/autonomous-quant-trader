# Adjudication: Astra re-check of slice 6b design rev 10 (R14D6B10-A-1)

- Record adjudicated: `ASTRA_RECHECK_DESIGN_SLICE6B_99FBAC3.md` (commit `bc1fc66`), verdict FIX.
  R14D6B9-F-1/2/3/5/6 APPLIED; F-4 PARTIAL (minimum applied, optional entry omitted, judged
  sound).
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the design's author. Not an authority.
- Date: 2026-11-14.

## Evidence checked

- Bitcoin's future-time rule compares a header with the validating node's own clock
  (cited Bitcoin Core v30.0 `validation.cpp`), so "a block cannot be accepted more than two
  hours before its header time" holds only relative to some node's clock, not true UTC.
  O-6a SPEC §5 fixes the earliest qualifying capture, so a refusal would be permanent (A-1).

## Decisions

| ID | Decision | Rev 11 |
|---|---|---|
| A-1 | Accept. | Hard capture floor removed; diagnostic `capture_before_tip_window` logged in the evaluation record; a hard floor marked [OWNER] (needs an accepted clock-bound rule, S4/SPEC wording). |
| N-1 | Accept. | "before any read" → "before any protected-data read" (5 places). |
| N-2 | Accept. | Runner makes its eligibility checks inside the same locked write. |
| N-3 | Accept (qualifier). | The F-4 justification in `ADJUDICATION_FINAL_DESIGN_SLICE6B_9CA4DE5.md` is qualified here: recomputation recovers the expected result from retained inputs; it cannot prove the original run finished or committed those hashes. The omission rests on F-2 (unclosed records are never released) and the owner-controlled counting of `LOOK_WITHOUT_RECORD`. |

Nothing left unrepaired; new [OWNER] marking only for an optional hard capture floor.
