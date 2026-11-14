# Adjudication: final Fable review of slice 6b design rev 9 (R14D6B9-F-1..6)

- Record adjudicated: `FABLE_FINAL_DESIGN_SLICE6B_9CA4DE5.md` (commit `9cc082d`), verdict FIX.
  Reviewer Claude Fable 5.2 (`claude-fable-5-2`), run as a subagent of the author's session
  on the owner's machine at the owner's request, after the owner's own run left no record.
  R14D6B-FINAL-F-1..9 all APPLIED; C-1..C-3 implemented as recorded.
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the design's author. Not an authority.
- Date: 2026-11-14.

## Evidence checked

- `c2_confirmation.py` `start` l.2714-2716 passes `rows["qualification_object_sha256"]` to
  `verify_code`; `Started.screen_object_sha256` (l.2668) is a different signed row, and
  `Started` has no qualification-object field (F-1, confirmed).
- `c2_lockbox.py` `Store` docstring l.1221-1240: `begin_read` requires sealing records to
  exist and status (a); nothing about a closing entry (F-2, confirmed).
- Rev 9 §3 runner rule names no lock for start/outcome writes (F-3, confirmed).

## Decisions

| ID | Decision | Rev 10 |
|---|---|---|
| F-1 | Accept, route via `protocol_row` (no reviewed-code change). | §2 classifier row compares with `protocol_row(started.protocol, "qualification_object_sha256")`. |
| F-2 | Accept as proposed. | §12 Store obligation: records released only with a matching closing entry and no termination entry; store-build test. No `c2_lockbox.py` change. |
| F-3 | Accept, stronger form. | §3 runner takes the look lock around every start and outcome write. |
| F-4 | Accept the minimum. | Residual stated; B-3 row names "records stored, no closing entry"; counting of `LOOK_WITHOUT_RECORD` marked [OWNER] P18-7. **Not applied:** the optional pre-`persist` hash entry; with F-2 the stored records are never released, and the evaluation is deterministic from ledger, look `now` and served bars, so a verifier can recompute it; an extra entry type is not needed now. |
| F-5 | Accept. | `sources` listed; acceptance record bytes passed and hash-checked; `evaluate_trial` takes `attempt_id`, bound and `running` before any read; `start`/`started` wording; §13 adds `completed_entry`, `family_attempts`, `nominate`, `trial_result`; first breach in ledger order; superseded-attempt test scoped to breached families. |
| F-6 | Accept. | Residuals stated (unbreached recode route, extra start); capture time floor `headers[5]` time − 2 h added. |

One proposal left unapplied (F-4 optional entry), reason above. No new owner item beyond
the [OWNER] marking of how `LOOK_WITHOUT_RECORD` is counted.
