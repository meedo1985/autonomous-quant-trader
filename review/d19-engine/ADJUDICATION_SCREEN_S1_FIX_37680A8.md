# Adjudication: Sol review of the S1 path-builder fix at 37680a8

Record: `SOL6_SCREEN_S1_FIX_REVIEW_37680A8.md` (gpt-6-sol, verdict ACCEPT with a verification limit). Adjudicated by Claude Opus 5.5, 2026-10-17.

## S1F-R1: the numerical guarantee is conditional on monotone `log`/`exp`

**Accepted as a disclosed residual. No code change.** The finding is correct: no standard guarantees that `np.log`/`np.exp` are monotone. In practice the error of both functions is below 1 ulp. With equal inputs, which is the observed case (a source bar closing at its high or low), they give equal outputs, so that case is fully guaranteed. A violation from a strict 1-ulp inversion would fail closed, not silently: `Bar` refuses it and the run stops. It would not produce a wrong measurement. Clamping the result instead would be the kind of silent alteration the project rules forbid. The rerun on the pinned image is itself the check. If it fails this way, it fails loudly with the same error, and we revisit then.

## The two checks the reviewer could not make (its shell failed)

Claude made both locally at 37680a8.

- **Callers and recorded consumers (prompt item 3).** `reconstruct` is called only by `null_path` (`screen.py:224`). `null_path` is used by `screen_job` (the screen run) and by `screen_reference_vectors` (the `"paths"` vector, which is still `None` in `FROZEN_REFERENCE_VECTORS`). The `g11` and `g14` vectors recompute equal to their frozen values. No committed record holds path values. The tests call `null_path` and `reconstruct` on synthetic data, and all 180 screen and semi tests pass. Nothing recorded is invalidated.
- **Other ways `path_series` can stop a run (prompt item 4).** `Bar` refuses a bar for one of five reasons. (1) An open time that is naive, has a nonzero offset or is unaligned: the path starts at `w0` minus the warm-up hours, on whole UTC hours. (2) A non-finite or non-positive price: `reconstruct` turns this into `PathUnavailable` first, and `screen_job` catches that. (3) A non-finite or negative volume: volume is copied from source bars that already passed `Bar`. (4) and (5) The high/low order: fixed here. `BarSeries` also refuses mismatched intervals and repeated or out-of-order times; `path_series` uses consecutive hours. All 30 pilot paths from the real exploration data pass `path_series` for both symbols at 37680a8.

**Result:** the fix is accepted. Next, the pilot sheet moves to the new engine commit.
