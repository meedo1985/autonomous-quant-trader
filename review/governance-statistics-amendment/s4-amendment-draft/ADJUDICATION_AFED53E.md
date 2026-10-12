# Adjudication of the focused checks of §4 draft rev2 (`afed53e`)

Date: 2026-10-03. By Claude Opus 5.5 (`claude-opus-5-5`). Checks:
`FABLE_REVIEW_AFED53E.md` (FA2, NOT READY, `b38204b`) and
`SOL_REVIEW_AFED53E.md` (SA2, NOT READY, `9f67598`). Applied in revision 3
of `DRAFT_WORDING.md`. All findings are accepted; none is rejected.

| Finding(s) | Disposition in rev 3 |
|---|---|
| FA2-1, SA2-1, FA2-12 | Precedence set out in §0: Constitution, then override clauses R-1..R-8 (§2.0), then annex text, then other protocol text. R-6 puts P18-2(a) under the calendar limit; R-3 reconciles "first embargo dropped" with `gap_embargo` |
| SA2-2, FA2-7 | R-7: the seed is fixed at declaration, before first evaluation; the "before any data exists" sentence is informative. Disclosed in §5. Owner item O-6 |
| FA2-2 | New §3 gate list G-1..G-13 per O18-5, with frozen N/A cases and open-row markers |
| FA2-3 | "Keep blocked" removed; §4 explains why every open gate must be decided before signing |
| FA2-4, SA2-5 | Lockbox rows narrowed to 77–79 (D-12) and 83–92 (D-11); lines 75, 76, 80–82, 294–296, 300 stay in force |
| SA2-3, FA2-8 | `nomination_deadline_days: 180` separate; `calendar_days_elapsed` is the hard limit (owner marker, recommended 255); `plan_complete_rule` defines the timeout case |
| SA2-4 | v1.0 leaf shapes kept (`{value, justification}` objects; `trial_budget_hard_stop: true`) |
| FA2-5, SA2-7 | O-3 presents both readings with no recommendation |
| SA2-6 | O-2 recommendation now shows the schedule fits, and justifies `U_ops` |
| FA2-6 | R-1, R-2, R-4 reading clauses |
| FA2-9 | §0 definition names conditions (i)–(v) as the minimum |
| FA2-10 | Round up (ceiling); "data mounted or evaluated before declaration" |
| FA2-11 | A technically failed lockbox read is a `NO_RESULT` cause; added to O-4 |
| FA2-13 | D-13 row added; D-20 placed at R-8 and the seed and purpose keys |
| FA2-14 | §9 l.106 reworded conditionally |
| SA2-8 | The rationale no longer states the review count |
| FA1-2 residue (code references) | R-8 under `<<OPEN D-20>>` |

The annex files are unchanged, so their hashes are unchanged.
