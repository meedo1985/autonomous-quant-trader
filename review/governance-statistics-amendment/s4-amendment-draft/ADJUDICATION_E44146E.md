# Adjudication of the reviews of §4 draft rev1 (`e44146e`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`). Reviews:
`FABLE_REVIEW_E44146E.md` (FA1, SOUND WITH FIXES) and
`SOL_REVIEW_E44146E.md` (SA1, UNSOUND), committed `2ecf18f`. Revision 2 of
the draft has **not** been written yet.

## Dispositions for revision 2 (all accepted, none rejected)

| Theme | Findings | Disposition |
|---|---|---|
| Decided rules incompletely encoded | SA1-1, SA1-2, SA1-3, FA1-8, FA1-9 | Make the D-18 rev 7 §2 text (P18-0..P18-7), with B-7's `T >= T_min` added to P18-0, a verbatim normative annex bound by hash |
| Method named, not frozen | FA1-2, SA1-4 | Make DESIGN rev 3 §2.1–§2.6 a normative method-spec annex bound by hash (with `u_j`, `psi_j`, cap, `B−1`, fsum, reason-code order, seed JSON) |
| Open rows not marked in text | FA1-3, SA1-7, FA1-14 | Put `<<OPEN D-nn>>` at every affected protocol line; add D-20; matrix line 80 is stale |
| B-5 only in the C2 protocol; `<` vs `≤` | FA1-1, SA1-8 | Put the schedule in Constitution §9; `m = 1` is the first eligible cycle; the partial sums are `< 0.10` and the infinite sum is `= 0.10`; each protocol binds only its own `z_crit_m` |
| Post-v1 data entry | SA1-5, FA1-5, FA1-6 | Remove it from the C2 text and defer it to a C3 amendment; C2 uses only the v1 window |
| Embargo | FA1-7, SA1-11 | Keep `validation.embargo`; add a separate gap key (max over declared horizons, data outside the window); record the computed UTC timestamp |
| Termination and processing | FA1-10, SA1-6, FA1-18 | Write out the post-nomination state machine; the precedences are owner items below |
| Outcome labels | FA1-11 | Widen `NO_RESULT` to P18-2's "no result in every declared family" |
| Schema | FA1-12 | Keep the v1.0 key paths (`trial_accounting`, `calendar_days_elapsed`) |
| Bootstrap purposes | FA1-13 | Mark the purposes as additions; the lockbox purpose is unchanged (D-11 open) |
| Rationale overclaims | FA1-4 | Make it conditional and list the weaknesses the owner accepted |
| Checklist and activation | FA1-15, FA1-16, SA1-10 | Add the version bump, the rationale, the §4 l.56 incident check, full §16 scope, re-review if the owner edits the text, `.gitattributes` `-text` before hashing, and the `FROZEN_HASHES.json` process |
| Mislabelled defaults; citations | FA1-17, SA1-9, FA1-19 | Relabel: per-cycle budget is derived from decided rules; 75-day window, safety classification and new-data allocation become owner items; fix the two citations |

## Owner items (to be asked together, when the text is near signable)

O-1 B-5 counting (recommend: `m` increments at every cycle declared on an
eligible window, whatever its outcome). O-2 calendar cap versus an unprocessed
nominee, and the window length (recommend: the cap wins, no promotion,
recorded as `U_ops`; 75 days). O-3 precedence if a revision or invalidation
comes after the pick. O-4 whether `RESEARCH_ONLY`/`NO_RESULT` opens the
NO_EDGE baseline path. O-5 safety classification and the 72-hour wait.

## Question FA1-14 (D-02..D-04, D-07)

A search of `review/` found no owner decision record for these rows, only
matrix/candidate/review mentions. Treated as **open** and to be listed with
the blocking rows.
