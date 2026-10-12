# Adjudication of the focused checks of §4 draft rev3 (`fcc0cf2`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`). Checks:
`FABLE_REVIEW_FCC0CF2.md` (FA3, NOT READY, `5ba2c05`) and
`SOL_REVIEW_FCC0CF2.md` (SA3, NOT READY, `5f09df9`). Applied in revision 4
of `DRAFT_WORDING.md`. All findings are accepted; none is rejected.

| Finding(s) | Disposition in rev 4 |
|---|---|
| FA3-1 | G-12 now depends on proposed new row N-1 (ESS series, kernel, bandwidth, fallback trigger); G-2 depends on new owner item O-7 |
| FA3-2 | New gate G-14 (shuffled-labels null) under proposed new row N-2 |
| FA3-3 | The gate list is now protocol YAML (`promotion.gates`), so it is frozen with the protocol |
| FA3-4 | The two `dsr_minimum` leaf-shape exceptions are named |
| FA3-5, SA3-1 | R-3 path corrected to `partitions.confirmation.start` |
| FA3-6 | G-9 depends on D-20; §4 wording on clauses both bound and marked is corrected |
| FA3-7 | Revision 2's "termination follows the post-nomination procedure" restored in §5 l.61 |
| FA3-8, SA3-5 | O-6 rewritten: logging is not protection; correct magnitudes; recommends a seed from public randomness published after declaration |
| FA3-9, SA3-3 | Lockbox components L-1..L-4 listed (stage `lockbox`, outside `U_proc`, under D-11) |
| FA3-10 | "A violation invalidates the cycle" labelled `[AI default]` |
| FA3-11 | `excluded_days_status` for the gap days [AI default] |
| FA3-12 | §6 step 1 now orders the work: gate-availability rows and O-1..O-7 first, then D-19, then the remaining rows |
| SA3-2 | New override clause R-9 replaces Annex A's "data outside the window" with mounted-or-evaluated data |
| SA3-4 | R-1 makes R-8 an explicit exception |

## Review cadence from here [AI default]

Revisions 2–4 converged: each round found fewer and smaller blockers. The
draft cannot be signed until about fifteen decision rows and owner items are
settled, and §6 step 2 already requires two-model review of the final
wording. Further focused checks are therefore deferred to that point, or to
any substantive change before it. Revision 4 has not been checked, and this
is recorded as weaker.

## What blocks the amendment now

Content decisions, not drafting: D-02..D-15, D-20, proposed new rows N-1 and
N-2, owner items O-1..O-7, then D-19. Under FA3-12 the rows that govern gate
availability come before D-19.
