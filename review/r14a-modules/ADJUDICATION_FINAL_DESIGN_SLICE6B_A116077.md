# Adjudication: final Fable review of slice 6b design rev 12 (R14D6B12-F-1..4)

- Record adjudicated: `FABLE_FINAL_DESIGN_SLICE6B_A116077.md` (commit `0142294`), verdict FIX.
  Reviewer Claude Fable 5.2 (`claude-fable-5-2`), run as a subagent of the author's session
  on the owner's machine at the owner's request. R14D6B9-F-1/2/3/5/6 APPLIED, F-4 PARTIAL
  (optional entry omission judged sound); removal of the capture floor judged right.
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the design's author. Not an authority.
- Date: 2026-11-14.

## Evidence checked

- `seal_family` (`c2_confirmation.py` l.1950-1968) returns `(sealing entry, artifact or
  None)`; rev 12 passed only the two records to `persist` (F-1).
- `c2_lockbox.py` l.584-586: a listed artifact missing from the store → `ARTIFACT_NOT_FOUND`;
  l.566 A1a needs the `aqt.c2.artifacts.v1` list (F-1).
- `check_screen_record` (l.714-727) takes the record bytes; lockbox `_check_declared`
  (l.718-723) lists hashes only, not trial objects (F-3).

## Decisions

| ID | Decision | Rev 13 |
|---|---|---|
| F-1 | Accept as proposed. | `persist` takes each status (a) artifact's bytes; release rule covers artifacts (hash = sealing record's `prediction_artifact_sha256`); store build writes `aqt.c2.artifacts.v1` (not in 6b); store-build test. |
| F-2 | Accept the minimum. | Runner obligation: one `evaluate_trial` per `attempt_id`; crash outcome before any new start; residual stated. **Not applied:** the optional "read begun" entry; a hidden relaunch gives no choice of `d` (deterministic result) and a new entry type would need P18-1 wording; revisit if the owner wants crashes visible to the look by itself. |
| F-3 | Accept. | `sources` adds `screen_record` and `trial_objects`, each hash-checked; `[DESIGN layout]` declaration field list; attempt binding names partition and family, applied by `evaluate_trial` before any protected-data read. |
| F-4 | Accept. | Release tests required of the one store build; a true `capture_before_tip_window` must be cleared by the verifier; hard floor added to the B-1 row as [OWNER] open; look-lock waiter blocks with no timeout. |

One proposal left unapplied (F-2 optional entry), reason above. No new owner decision
beyond the existing hard-floor item, now in the owner table.
