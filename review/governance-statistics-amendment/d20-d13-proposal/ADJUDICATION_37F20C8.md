# Adjudication of the Sol and Fable reviews of the D-20/D-13 proposal rev 1 (37f20c8)

Records: `SOL_REVIEW_37F20C8.md` (gpt-6-sol), `FABLE_REVIEW_37F20C8.md`
(claude-fable-5-1). Adjudicated by Claude Opus 5.5, the drafter. Revision 2
applies every disposition below. The re-check decides whether the repairs
hold.

| ID | Severity | Decision | Reasoning and evidence | Disposition in rev 2 |
|---|---|---|---|---|
| DC-R1 / DF-R3 | blocking | AGREE | By the matrix's own trigger note, D-03's acceptance triggers D-20. Rev 1's "does not fire" was wrong. What holds is narrower: G-1 needs no migration. | §1: "D-20 is triggered". G-1 is named as row option (b), with the reason. The acceptance condition is that the Task 12 tests and D-19 reference vectors pass at the bound commit on the pinned runtime. Q1 reworded. |
| DC-R2 | blocking | AGREE | Sorted-key JSON reorders R-7's written components, so rev 1's "only a byte encoding" was wrong. | §2: stated as an amendment of R-7's wording, with the reason. The ordered-array alternative is kept, with its cost (a second encoding; changes the engine's synthetic draws; engine re-review). |
| DC-R3 / DF-R5 / DF-R6 | blocking / note / note | AGREE | One `seed` does not control LightGBM sub-seeds set explicitly; some scikit-learn solvers consume `random_state`; LightGBM is not in any pinned runtime. | §3 B4: `model_seed` is passed as `random_state` to every scikit-learn class and as `seed` to LightGBM. Declared sub-seeds are forbidden; `deterministic`, `num_threads = 1` and `force_col_wise` are fixed; the model libraries are part of the runtime identity. `lightgbm` trials cannot be declared until such a runtime is recorded and reviewed. |
| DC-R4 / DF-R4 | blocking | AGREE | `window_length` and `evaluation_window_id` were undefined. The calendar-length reading lets a null shift land near alignment. | §3: the canonical window id is defined; `n_w` = rows retained after purge and embargo; the shift direction is `label[(r + offset) mod n_w]`; `hi < lo` in any window is `UNAVAILABLE`, and windows are never dropped. Vectors cover these. |
| DC-R5 | blocking | PARTIAL | Holds as a requirement: (b) is sound only if the trial set, trial ids, round and evaluation obligation are fixed before the beacon. Does not hold as a gap: each condition is already decided text (P18-1 frozen `J_f`; `first_post_rule`; round by procedure; P18-2 one look after every trial; FA5-3 abort cost). | §4 "Why no new route opens" cites each decided clause. No new rule is needed. |
| DC-R6 | blocking | PARTIAL | Holds: (b) also changes G-1's seed, overrides l.266 for these streams and adds a beacon dependency; "no compute cost" understated the governance cost. Contested: that (b) undermines the D-19 certification. The calibration's rates are over the data law at data-independent seeds, and (b)'s seed is data-independent and cannot be chosen. | §4 "Costs of (b)": scoped precedence over l.266, beacon dependency and R-7 failure handling, audit record, and the calibration argument stated for the re-check to confirm. If it fails, (a) is the safe choice. The C-13 bullet is rewritten, not deleted. |
| DC-R7 / DF-R12 | blocking / note | AGREE | Leaving `s_inputs` to a later build collides with BO-2. The screen needs the mapping anyway, because G-11 shifts `s`. | §5: the mapping and its enforcement are built in `calibration/screen.py`, frozen in the object (one hash per cycle, the same for every trial), §16- and owner-reviewed before the freeze, with a falsifier test. |
| DC-R8 | blocking | AGREE | R-8's broad wording could bind a lockbox bootstrap clause. | §1: R-8 is re-worded to the enumerated clauses; lockbox clauses (L-1..L-4, l.83–92) are expressly reserved. |
| DC-R9 / DF-R9 | note | AGREE | Both confirm that the G-11 algorithm is correct. A missing reason code was flagged. | §3 B3: `INSUFFICIENT_SHIFT_RANGE`, with the element count stated. |
| DC-R10 / DF-R13 | note | AGREE | The 5th percentile of 7 paths depends on the quantile rule, and invalid paths were unhandled. "Binds nothing" overstated it. | §6: `type_seven_quantile` at 0.5 and 0.05; an unavailable path makes that estimand's summaries unavailable, with no dropping; the text says it binds two reporting outputs and nothing reads them; STAT acceptance absent, recorded. |
| DF-R1 | blocking | AGREE | The G-9 "code binding `<<OPEN D-20>>`" marker was missing from scope. | M12 added; G-9 binds to `calibration/dsr.py` at the engine commit, with method V as already decided. |
| DF-R2 | blocking | AGREE | The l.266 trial-seed code was not bound, and the new seed and stream code had no stated home. | `preregistration.seed_material` and `trial_seed` added to the §1 table. The new functions live in `calibration/screen.py`, frozen in the object (§3 "Where the code lives"). |
| DF-R7 | note | AGREE | The first 10 `k_i` cannot detect a later divergence. | §3: a SHA-256 over all 500 `k_i`, and over the full `d × w` grid, is added. |
| DF-R8 | note | AGREE | "Each draw gets its own seed" contradicted G-11; the convention hash's role was unstated. | §3: one generator for G-11, one per (d, w) for G-14; the hash is a fixed domain field. |
| DF-R10 | blocking (honesty) | AGREE | (b) does not close the nominee-seed or strategy-search routes. | §4: (b)'s reach is stated; the C-13 bullet keeps both open routes; the beacon dependency and the exact `trial_id` are listed. |
| DF-R11 | note | AGREE | Input formats were unstated, and "one function" overstated the sharing. | §2: input validation and formats; only `calibration.seeds.sha` over the named object is shared. |
| DF-R14 | note | AGREE | The C2 check is a requirement, not existing code. | §1: the C2 evaluation must use `mapping.check_engine` and `rundef.loaded_outside` against the object's `engine_commit`, as a §16 item of that build. |

**Found while repairing (new in rev 2).** B6: the screen runs before the
post, so its null streams cannot use the beacon. They use the §7.2 screen
seed, the path index and the trial id. Rev 1 left this implicit.

Nothing was left unrepaired.
