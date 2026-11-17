# Slice 6b build, B2 (ledger rules): build notes for review

- Builder: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15, branch `confirmation-module`.
- Design: `DESIGN_SLICE6B.md` rev 16 §3, §5, §13. B1 notes: `BUILD_NOTES_SLICE6B_B1.md`
  (B1 reviewed by Astra, record `ASTRA_REVIEW_B1_637A7B0.md`, adjudication
  `ADJUDICATION_B1_637A7B0.md`).
- §16 applies as for B1: not merged; different-model review and the owner's PR review first.

## What B2 changes

| Piece | Design | Commit |
|---|---|---|
| B2a: `TRIAL_RESULT_SCHEMA` v2 with `IDENTITY_KEYS`; `result_identity`; `trial_result(identity=...)`; `completed_entry(result, window)` returns `(hash, days, d, reason)`, `window_id` against the governing window, days form-only, identity fields checked for form | §3, §13 | `1782fc3` |
| B2b: `family_attempts` returns `attempt_id` and every outcome position, matches outcomes to this cycle's starts, refuses an outcome with no start anywhere, reports a second outcome; new `RESULT_ENTRY`, `FamilyLedger`, `family_ledger` (decode, bind, compare identity; completion and crash rewrite; order breaches; FINAL-F-2 states for breached families; `trial_states` for the others) | §3 rules 1-3, §13 | `aec0987` |
| B2c: `nominate(..., breach=, results=)` (required keywords), §5 precedence, `failing`, `u_proc_results`, `u_proc_present` on `Nomination` | §5, §13 | `70c379b` |

Tests: `tests/unit/test_c2_confirmation_ledger.py` (new; real ledgers written with
`attempts.start_attempt`, `finish_attempt` and `ledger.append_entry`), plus updated
`test_c2_confirmation_run.py` and `test_c2_confirmation_cycle.py`.

## Readings taken (for the reviewer to confirm or correct)

- **B2-R-1** `family_ledger` takes the ledger *up to* any look entry; rule 3 (a result after
  the look is ignored) is the caller's slice, done in B3/B5 when the look entry exists.
- **B2-R-2** A result entry of this cycle naming a family outside `FAMILIES` is a
  `CycleError` (otherwise no family's analysis would see it).
- **B2-R-3** A breach's position is the position of the breaching entry (the second result,
  the second outcome, or the first result after the outcome); `breach_reason` names the
  attempt of the earliest such entry.
- **B2-R-4** In a breached family an attempt with two results or a result after its outcome
  gets no derived outcome (marked `breach`); FINAL-F-2 then gives its trial `final` unless a
  later attempt of that trial is derived-completed or running.
- **B2-R-5** `nominate`'s configuration-hash defence is grouped with rule 2 (U_ops), as in
  rev 6; it cannot be reached when `family_ledger` ran first (rule 2 identity check).
- **B2-R-6** For a breached family the record's `reason` is `LEDGER_ORDER:<attempt>`; the
  per-trial list is in `failing`. For an unbreached failing family `reason` is the message
  `"<id>: <reason or state>; ..."`.
- **B2-R-7** `u_proc_results` is also recorded for an available family (normally empty).

## Not in B2

The anchor rules, each start's `protocol_hash` against the signed hash, the look and
termination entry checks (B3); `look_allowed` changes (B3); `evaluate_trial` and
`evaluate_look` (B4, B5).
