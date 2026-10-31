# Pre-freeze `screen.py` change for D-20 Q2(ii) and Q5: design (rev 2)

**Author:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-31. This is AI drafting and not an authority. **Status: DESIGN rev 2, UNREVIEWED. No code is written yet.** Rev 1 is at `ceb12c3`, and its review is `SOL_DESIGN_REVIEW_CEB12C3.md` (gpt-6-sol: FIX, PFS-S-1..5).

**Authority:** the owner's D-20 decision (`OWNER_DECISION_D20_LOCKBOX.md`, freeze-sheet `f04aa6c`), items 6 and 9, which are time-sensitive. The binding text is `PROPOSAL_REV3.md` A1b and A6 "The final hour", as amended by `PROPOSAL_REV4.md` A1b (D20L-44, D20L-47, D20L-48) and `PROPOSAL_REV5.md` (D20L-55). None of this binds until C2 is signed.

## 0. Dispositions of rev 1's review

| ID | Disposition |
|---|---|
| **PFS-S-1** (BLOCKER; R-14 needs the whole C2 confirmation coordinator frozen) | **Routed to the owner, who decided (2026-10-31): "Exception like Q4 (Recommended)".** The coordinator becomes a separately reviewed **confirmation module** under a proposed C2 row R-14a, which also covers the Q4 lockbox module. The proposal is freeze-sheet `review/governance-statistics-amendment/r14-exception/PROPOSAL.md`. It is inactive until reviewed, decided and signed. **Consequence here:** rev 1's C3 entry point is deleted, because that coordination belongs to the confirmation module. `screen.py` keeps only what R-14a item 4 forbids defining elsewhere: the seed reaching the model fit (C1), and the final-hour rule both modules must share (C2). **If R-14a is not adopted**, this change is still needed but no longer enough. The coordinator would then have to be frozen too, before step G. |
| **PFS-S-2** (BLOCKER; guard overclaims) | **Accepted.** The guard is narrowed in §1. |
| **PFS-S-3** (BLOCKER; validation rejects zero volume) | **Accepted.** See C2 validation and T5. |
| **PFS-S-4** (NON-BLOCKING; freeze consequences incomplete) | **Accepted.** See §4 items 1, 3 and 5. |
| **PFS-S-5** (QUESTION; caller-supplied seeds unbound) | **Accepted, moved.** C3 is deleted, so `screen.py` takes no seed derivation from a caller beyond `model_seed`. R-14a item 5 makes the confirmation module verify and record every such value from the trial record and the signed C2. |

Sol's answers to rev 1's questions are adopted. Q-a: G-14's un-shifted pipeline uses `model_seed`. Q-b: terminal values are computed but not used inside the window; zero volume is safe; T4 now separates computed from used values. Q-c: answered by PFS-S-1's routing.

## 1. What changes, and what must not

**The guard (narrowed, PFS-S-2).** For identical inputs and the pinned runtime and image, every **scientific value** that `screen_job`, `screen_gates`, `walk_forward` and `model_column` return with default arguments is bit-identical to `main`. Scientific values are gate results and every number those results are built from. Every frozen reference vector is also bit-identical: S8's paths vector, which needs the pinned image for its float path, and the G-14 `(offset, model_seed)` vectors.

**Expected to differ:**
- elapsed `seconds`, which is not repeatable even on `main`;
- every identity hash over `screen.py`'s bytes, such as `run_screen`'s `screen_sha256`;
- the qualification-object manifest and hash, which changes the held-out seed anchor for any new attempt (§4).

**C1. Estimator seed (Q5, A1b `L266_MOD_2_31`).**
- New `estimator_seed(seed_l266: str) -> int` returns `int(seed_l266, 16) % 2**31`. It refuses anything that is not 64 lowercase hex digits. A result of 0 is legitimate (D20L-44).
- `walk_forward(..., model_seed: int = 0)`: the nominee's fit uses `model_seed` where it now hard-codes `seed = 0` (l.1547). A G-14 null draw still replaces it with its own `g14_draw` seed. Equality with that seed by chance is allowed (C-12 (5)).
- `model_column(..., model_seed=0)` and `screen_gates(..., model_seed=0)` pass it through. In `screen_gates` it reaches both the emission fits (`inputs` → `model_column`) and G-14's un-shifted pipeline (`draw is None`, l.1176).
- `ZERO`, the owner's rejected alternative, needs no code because the default stays 0.

**C2. Final-hour end price (Q2(ii), A6).**
- New `confirmation_path(rows: np.ndarray) -> np.ndarray`. The input is real joint rows of shape `(n, len(SYMBOLS), 5)`, OHLCV as `joint_bars` gives them. The output appends one derived terminal row per symbol: open = high = low = close = that symbol's last close, and volume = 0.
- With rows over exactly `[w0 − warmup, w1)`, this gives the `warmup + window_hours + 1` rows `screen_gates` requires. The runner prices the last hour's exit at `bars[j + 1].open`, which is the terminal open, equal to the last close (C-6 (1)'s close(t) = open(t + 1), used as a definition). No run reads the bar at `w1`.
- **Validation (PFS-S-3).** It refuses with `TrialError` unless all of these hold:
  - the shape is exactly `(n ≥ 1, len(SYMBOLS), 5)`;
  - every price is finite and > 0;
  - every volume is finite and ≥ 0;
  - every row satisfies `low ≤ min(open, close)` and `max(open, close) ≤ high`.
- The hour span and contiguity are checked by the confirmation module (R-14a item 5), which holds the timestamps. `screen_gates` already checks the length.
- The lockbox module uses this same function (R-14a item 6), because A7 compares hashes of `d`.

## 2. Tests (synthetic data only)

- **T1 guard.** For the existing fixtures with defaults, the scientific values of `screen_job`, `screen_gates`, `walk_forward` and `model_column` equal `main`'s, which are captured as fixtures before the edit. `seconds` and `screen_sha256` are excluded and named in the test. All reference-vector tests pass unchanged.
- **T2 seed map.** Known vectors: an all-zero hex gives 0 (accepted), `"f"*64` gives `2**31 − 1`, plus one fixed mid value. Malformed input is refused: wrong length, uppercase, non-hex.
- **T3 seed reaches the fit.** A spy `build_model` records the seed. The nominee's emission fits and G-14's un-shifted pipeline get `model_seed`, and each G-14 null draw gets its `g14_draw` seed. With a fixed `model_seed`, two runs are bit-identical for each allowed class (A1b test).
- **T4 terminal row, at consumer boundaries.** On a synthetic path whose true bar at `w1` has an open different from the last close, compare runs on `confirmation_path(path[:-1])` and on the true path:
  - **used values are identical** except the last hour: every target, decision, fill, fill cost, emission and fit input inside the window, and every equity value before the last hour;
  - the last hour's exit is priced at the last close;
  - **computed terminal values may differ** (the terminal feature row, the terminal close-to-close return and its EWMA value), and the test shows that none of them is used inside the window.
- **T5 validation.** Accepted: zero volume. Refused: a zero price, a negative or non-finite value, OHLC out of order, a wrong shape or symbol count, and empty input.

Each test fixture is synthetic. No confirmation or lockbox bytes are read.

## 3. Out of scope (later tasks, each authorised separately)

- the confirmation module and the lockbox module (R-14a, Q4);
- the R-14a decision itself;
- the S4 C-0/C-6 wording of the end-price rule (D20L-34);
- the Annex C l.412 wording.

## 4. Freeze consequences (to state in the PR)

1. **`screen.py`'s SHA-256 changes.** It needs a new independent review record, and `review/d19-engine/FREEZE_REVIEWS.json` must name the new hash and record. Without them, `qobj.build` refuses (QO-5).
2. **Owner §16 PR review before merge**, because `screen.py` is evaluation code in the frozen object.
3. **The qualification object changes (PFS-S-4).** The new `screen.py` bytes change the object's manifest and its `qualification_object_sha256`. That is the hash posted as `AQTQ1` and the anchor of every held-out attempt. No artifact of an object built from the old `screen.py` is claimed to equal one from the new object. None has been built or posted yet.
4. **G0 must be redone.** `FREEZE_HELDOUT.md` FP2 (d) pins `/opt/aqt-d19/build` at `ed0bfbf`. These must be updated together: the build checkout reinstalled at the merged commit; FP2 (d) and `G0_EVIDENCE.md` re-recorded; step G's pinned `d19.sh freeze <build commit>`. D20L-47 requires the freeze to name a build commit whose `screen.py` is this version.
5. **The development run is unaffected.** `screen.py` is a LATER file (`qobj.py` `LATER`), not an engine file pinned to `/opt/aqt-d19/app` at `eeaa728`.
