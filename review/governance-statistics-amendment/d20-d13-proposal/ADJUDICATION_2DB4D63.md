# Adjudication of the Sol and Fable re-checks of the D-20/D-13 proposal rev 2 (2db4d63)

Records: `SOL_RECHECK_2DB4D63.md` (gpt-6-sol), `FABLE_RECHECK_2DB4D63.md`
(claude-fable-5-1). Adjudicated by Claude Opus 5.5, the drafter. Revision 3
applies every disposition below.

| ID | Severity | Decision | Reasoning and evidence | Disposition in rev 3 |
|---|---|---|---|---|
| DC2-R1 | blocking | AGREE | `mapping.check_engine` allows only `mapping.py` as an object file. `loaded_outside` checks location, not bytes. "Verify against `engine_commit`" cannot bind `screen.py`. | §1 "Two binding times": existing code binds to the engine commit; `mapping.py`, `screen.py` and `heldout.py` bind to their object bytes. The C2 build must check loaded bytes against both, generalising `check_engine` (a §16 item). |
| DC2-R2 / DF2-R3 | blocking / note | AGREE | `LinearRegression` has no `random_state`. | §3: `random_state` only where the constructor accepts it; `screen.py` maps each protocol class to one library class, each with a reproducibility test. |
| DC2-R3 / DF2-R2 | blocking | AGREE | Confirmed in the accepted prereg (l.536): "C2's real evaluation must run in the same image". `requirements.lock` pins only numpy. A library added later changes the image digest, which is in the run definition and the gating identity. | New §3a and owner question 2b: (a) add scikit-learn and LightGBM to the image before the run definition is recorded, through their own §16-reviewed PR (recommended); or (b) no model-fitting trials in C2 under this object. Either way, no later addition. |
| DC2-R4 | blocking | PARTIAL | Holds: data independence alone does not prove equal finite-bootstrap rates, and "unaffected" overstated the conclusion. Holds: (a) is not a safe fallback. Contested: that the objection is specific to (b). The `U_G` rate is a probability over replications with hashed seeds. Transfer to any C2 seed, under (a) or (b), rests on the same modelling assumption, a SHA-256 seed acting as an unpredictable draw independent of the data. (b) meets that assumption; (a) does not, because of the free pre-post search. | §4 "Calibration": scoped to G-1; states what is certified and the modelling assumption (which the owner accepts as such); (b) meets it except for priced retries; (a) does not; if the assumption is rejected, neither transfers. "Safe fallback" removed. |
| DC2-R5 / DF2-R6 | note | AGREE | Invalidate-and-retry after the beacon is possible at will (a second post), priced at one `m`, not statistically corrected. | §4: "Within one cycle, no new route opens"; a separate disclosed paragraph for retries across attempts; the C-13 bullet says so. |
| DC2-R6 / DF2-R5 | note | AGREE | B6 extends accepted prereg §7.2; its window id and path streams were undefined; the screen seed can be searched through the trial-set hash. | §3 B6: recorded as a clarification of prereg §7.2; window id = the C2 C-0 window id from the declaration; the path streams are bound by the reviewed `screen.py` and its vectors; the search surface is disclosed (power only). |
| DC2-R7 / DF2-R8 | note | AGREE | Path assembly and the per-path routine were unspecified. | §6: groups, split order, the path assignment rule, chronological concatenation and the per-path routines are fixed. |
| DF2-R1 | blocking | AGREE | The G-9 seed is `dsr._replicate_seed` (inline, DSR purpose, fixed `WINDOW`), not `statistics.replicate_seed*`. Annex B §2.4's "extend the stream / regenerate I-10" was open with no marker. | §1: the statistics row no longer claims the Annex B seeds; the G-9 row binds `_replicate_seed` and `indices` with `WINDOW` as a fixed domain label; new M13 supersedes the §2.4 sentence, and the D-19 reference-vector suite serves as I-10; M7 covers all three `added_purposes`. |
| DF2-R4 | note | AGREE | The formula also appears in `seed_disclosure.derivation`; validation must not apply to the engine's 0-based synthetic rounds. | §2: both places replaced; validation is the C2 builder's, not the shared hashing step's. |
| DF2-R7 | note | AGREE | The D-19 vectors exercise G-1's availability path, not the interval routine itself. | §1: the acceptance condition for the interval, Sharpe and quantile rests on the Task 12 tests. |

**Partial adjudications DC-R5 and DC-R6 (rev 2).** Fable judged both correct.
Sol judged them sound only to the narrower extent stated. Rev 3 adopts that
narrower wording (DC2-R4, DC2-R5).

Nothing was left unrepaired.
