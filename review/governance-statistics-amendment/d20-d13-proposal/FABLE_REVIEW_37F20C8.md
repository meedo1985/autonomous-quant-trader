# Fable review of the D-20 (rest) and D-13 proposal, revision 1, at 37f20c8

- Reviewer: Claude Fable 5.1 (`claude-fable-5-1`), run as a read-only subagent of this Claude Code session; the model line below is the reviewer's own statement
- Date: 2026-10-13
- Reviewed: the same self-contained packet as Sol, plus repository files it read itself (listed in its review)
- Findings: DF-R1, DF-R2, DF-R3, DF-R4, DF-R10 (blocking); DF-R5..DF-R9, DF-R11..DF-R14 (notes). Verdicts: Q1-Q4 READY WITH FIXES ((b) still recommended for Q3).
- The reviewer's final report follows verbatim.

---

Model: Claude Fable 5.1 (claude-fable-5-1)

# Adversarial review: D-20 (rest) and D-13 proposal, rev 1, at 37f20c8

This was a read-only review. I edited nothing and ran no git command that writes. Checked against: `src/aqt/metrics/statistics.py`, `src/aqt/core/preregistration.py`, `src/aqt/metrics/descriptive.py`, `src/aqt/benchmarks/canonical.py`, `calibration/rundef.py`, `calibration/mapping.py`, `calibration/dsr.py`, `protocols/protocol_v1.yaml`, the S4 draft's markers, and `SOL6_BUILD_ORDER_REVIEW_D321147.md` (BO-2).

**Verified as the proposal states:**
- Every routine named in the §1 table exists. `paired_sharpe_improvement_interval` is at statistics.py:591, `max_drawdown` at descriptive.py:260 and `reaches_rebalance_band` at canonical.py:402.
- `CODE_DIRS = ("calibration", "src/aqt", "scripts")`, so the inventory hash covers all three bound files.
- `check_engine` (mapping.py:102–118) checks loaded files against the engine commit, as claimed.
- The paired CI uses `paired_sharpe_improvement_influence`, which is the `E-IMPROV` influence.
- `_uniform_index` does rejection sampling exactly as quoted.

## Findings

**DF-R1 (blocking, §1 / scope / item 7): the G-9 code-binding marker is left silently open.**
- Evidence: DRAFT_WORDING.md:295 reads `G-9: … status: "<<D19 values>>; code binding <<OPEN D-20>>"`. The proposal's "Not in scope" list names only "the G-9 values (`<<D19>>`)". M1–M11 never mention the G-9 code binding.
- Scenario: after the owner's answers, the replacement revision closes M1–M11. G-9's `<<OPEN D-20>>` survives, and BO-2's condition that every marker is closed before the freeze is not met.
- Repair: add the G-9 marker as M12. Close it by citing OWNER_DECISION_D20_V (method V at the recorded code hash and runtime), or list it explicitly as staying open, with a reason.

**DF-R2 (blocking, §1 table): the l.266 trial-seed code is not bound.**
- Evidence: under §4 option (a), all three streams take `trial_seed_hex` from l.266. Even under (b), the nominee's own fit still takes it. That seed is produced by `src/aqt/core/preregistration.py` `seed_material` / `trial_seed` (domain `aqt.trial_seed.v1`, a JSON array). Neither R-8 nor the §1 table names it, so its byte encoding is not bound.
- Under (b), the new `trial_seed_j = SHA256(cj({"family_seed", "trial_id"}))` and the null-stream function (§3, "in the screen's code") are new code. The proposal does not say which file holds them or that they are covered by the same binding.
- Repair: add `preregistration.trial_seed` (and `seed_material`) to the table. State that the `trial_seed_j` and null-stream functions live under `src/aqt/` or `calibration/` at the engine commit and are named in R-8.

**DF-R3 (blocking, §1 framing): "the D-20 trigger does not fire" is inaccurate. What is true is narrower.**
- Evidence: the matrix note says D-20 "is triggered by the first acceptance among D-03 or D-11". D-03 has been accepted, so by the matrix's own text the row is triggered.
- What the proposal actually shows is that the *harm* the row guards against (row option (b) silently changing resamples) does not happen for G-1, because the bound estimand is the Task 12 `E-IMPROV` influence. In effect the proposal picks matrix option (b), "reuse the Task 12 stream", for G-1. The matrix recommends (a) "if anything is bound at all", and gives as its falsifier a demonstration about block-length invariance, which does not quite match this argument.
- The substance is sound: same estimand, same influence, same block length, so the vectors stay valid. But the owner should be told plainly that he is choosing row option (b) for G-1, and why it is safe here.
- Repair: reword §1 and question 1 to "D-20 is triggered by D-03; for G-1 we propose row option (b), because the bound clause's estimand equals the Task 12 influence process, so no resample or vector changes".

**DF-R4 (blocking, §3 B4): `window_length` is undefined, and one reading breaks the null.**
- Evidence: C-12 (3) shifts labels "within each training window's retained rows". B4 sets `hi = window_length − horizon_days` but never says whether `window_length` is the count of retained rows `n_w` (after purge and embargo) or the calendar length of the training window.
- Scenario: if it is the calendar length, it is larger than `n_w`. An offset near the top of the range, taken modulo `n_w`, can land within `horizon_days` of 0. The "null" labels are then nearly aligned with the real ones and leak signal. The `NO_SHIFT_RANGE` test is also wrong under that reading.
- Repair: define `window_length := n_w`, the number of retained rows in window `w`. State that the shift is `label'[r] = label[(r + offset) mod n_w]`, with the direction given.

**DF-R5 (note, §3 B4): "deterministic classes ignore the model seed" holds only for some solvers.**
- Evidence: in scikit-learn, `LogisticRegression` with the `liblinear`, `sag` or `saga` solvers, and `Lasso`/`ElasticNet` with `selection="random"`, consume `random_state`.
- Repair: either pass `model_seed` as `random_state` to every class, or require each declaration to fix a deterministic solver. Record which one applies.

**DF-R6 (note, §3 B4): `model_seed` alone does not make LightGBM reproducible, and its runtime is not pinned.**
- LightGBM's `seed` only generates the sub-seeds (`bagging_seed`, `feature_fraction_seed`, `data_random_seed`, …). Per LightGBM's documentation, sub-seeds set explicitly take priority over it. A declaration that fixes them would give every null draw the same sub-seeds.
- Reproducibility also needs `deterministic=true`, a fixed `num_threads`, and `force_row_wise` or `force_col_wise`.
- Separately, `calibration/dsr.py` `runtime_identity()` hashes the interpreter and the NumPy/BLAS binaries, but not LightGBM. LightGBM is not installed in the repository at all; the only mention is in a Task 1 text file. So "stability comes from the pinned runtime" does not cover G-14 refits.
- Repair:
  - forbid explicit sub-seeds in declarations, or derive them all from `model_seed`;
  - fix the determinism parameters;
  - state that the C2 evaluation runtime identity must include the LightGBM version and binary hash.

**DF-R7 (note, §3 reference vectors): the vectors are too weak to catch drift.**
- "The first 10 `k_i`" cannot detect a divergence after draw 10, such as a change in rejection behaviour at larger `len(P) − i`.
- Repair: freeze a SHA-256 over all 500 `k_i` (and over all `(offset, model_seed)` pairs for a full `d × w` grid), alongside the readable first-10 sample.

**DF-R8 (note, §3 text): two small inconsistencies.**
- "Each draw gets its own seed" contradicts G-11's single generator with `indices = [500]`.
- The null streams embed `CONVENTION_DOCUMENT_SHA256`, which hashes a conventions document that does not describe these streams.
- Neither causes a collision, because the purposes differ. Repair: reword the first. For the second, say the hash is reused only as a domain field.

**DF-R9 (note, §3 correctness, confirmed).** I checked the core stream rules and they are right:
- `P = [m … T−m]` has `T − 2m + 1` elements, so `T − 2m ≥ 499` is exactly `|P| ≥ 500`.
- The partial Fisher–Yates with `j = i + U[0, len(P) − i)` is unbiased and draws without replacement.
- The offset `lo + U[0, hi − lo + 1)` is unbiased and inclusive of both ends.
- `hi < lo` makes the range empty.
- `getrandbits(31)` fits LightGBM's int32 seed.
- The stability paragraph is honest: Python guarantees only that `random()` repeats under the compatible seeder.

**DF-R10 (blocking for an honest §4, recommendation unchanged): (b) closes the stream-seed search but not the parallel nominee-seed search.**
- The FA5-6 threat model assumes the declarer can compute results offline on the window data before the post.
- Under that same model, the nominee's own fit seed is chosen before the post, either fixed by the declaration ("the nominee's own fit keeps the model seed its declaration fixes") or taken from l.266. It can be ground in the same way, and it moves every gate and the DSR claim, not just G-11 and G-14.
- More broadly, a declarer with offline access can search the strategy itself. The seed channel is one narrow route among several.
- "This closes the search" overstates what (b) does.
- Repair: say that (b) closes the null-stream and G-1 bootstrap seed route only. Keep a C-13 bullet disclosing the remaining routes (nominee model seed and strategy search under offline access) instead of deleting the "Seeds" bullet outright.
- Other costs of (b) to list:
  - G-1, G-11 and G-14 now cannot run without the beacon, so they inherit R-7's beacon-failure handling;
  - `trial_id` must be the exact identifier Annex B §2.4 hashes.
- I found no new grinding route in (b) itself. `family_seed_f` is fixed by an unpredictable beacon round after the post, provided R-7 fixes the round by procedure and the declarer cannot pick it.

**DF-R11 (note, §2): the encoding is sound but under-specified at its inputs.**
- Canonical JSON with named keys has no ambiguity, so B2 is fine.
- Repair: state the input formats.
  - `annex_b_seed` is the 64-character lowercase hex of the Annex B §2.4 digest.
  - `beacon_randomness` is the drand `randomness` field, not `signature`, as 64-character lowercase hex.
  - `round` is the drand round number fixed by R-7.
  - Validate all three before hashing.
- Also, "one function" overstates the sharing. `calibration/seeds.py` `family_seed` builds a synthetic Annex B seed. C2 needs its own builder, and only the final `sha({...})` step is shared. Name the shared function.

**DF-R12 (note, §5): closing by procedure is acceptable only with three conditions added.**
- (i) The identity-mapping code is merged with §16 review, including the owner's PR review, before the declaration post, not merely "before the declaration".
- (ii) There is one hash per cycle, the same for every trial, so the enforcement cannot be tuned per declaration.
- (iii) The code carries its own falsifier test (a declaration that uses `ewma_vol_168h` is rejected).
- Without (ii), the declarer controls the enforcement code its own declaration is checked by.

**DF-R13 (note, §6 D-13): the 5th percentile over 7 paths needs a quantile rule.**
- With 8 groups and 2 test groups there are C(8,2) = 28 splits and 7 paths. The "5th percentile" of 7 values depends on the quantile convention, and the median of 7 does not.
- Repair: bind it to `statistics.type_seven_quantile` (already used for the CI). Also define what the report says when a path's Sharpe, or `E-DIFF` on a zero-variance difference, is unavailable: report it as unavailable, with no dropping.
- Option (a) is otherwise consistent with frozen l.215–222. `diagnostic_only` and "no independent promotion gate" both hold, and naming both estimands follows D-01.

**DF-R14 (note, §1 falsifier): the C2 check is a requirement, not existing code.**
- `check_engine` exists for the mapping and the held-out runner, but no C2 evaluation path exists yet.
- Repair: state that the C2 evaluation must reuse the same check (`check_engine` / `loaded_outside`) against the object's `engine_commit`, and that this check is a §16 item of that build.

## Verdicts on the owner questions

1. **Code bindings (§1, §2): READY WITH FIXES.** Binding to the recorded engine commit is the right referent, since the certified `U_G` was measured on that code and runtime. Fix DF-R1 (the G-9 marker), DF-R2 (bind the trial-seed code and name the new code) and DF-R3 (state honestly that this is row option (b) for G-1). DF-R11 and DF-R14 are wording fixes.
2. **Null-test streams (§3): READY WITH FIXES.** The sampling is exact, unbiased and without replacement (DF-R9). DF-R4 (`window_length`) must be fixed before adoption. DF-R5, DF-R6 and DF-R7 should go into the screen-build requirements.
3. **Seed source (§4): READY WITH FIXES, (b) still recommended.** The weakness is real and (b) closes it at no compute cost without opening a new route. It does not close the parallel nominee-seed and strategy-search routes. Keep a disclosure of those (DF-R10) and list the beacon dependency as a cost.
4. **D-13 (§6): READY WITH FIXES.** Option (a) fits the frozen text. Bind the quantile rule and the unavailability reporting (DF-R13).

On §5, closing by procedure is acceptable with DF-R12's conditions (merged and §16-reviewed before the post, one hash per cycle).

## What I could not check

- The D-03 decision record and the Task 12 reference vectors themselves. I took "D-03 = `E-IMPROV`" from Annex C C-1 and the code.
- Whether R-7 or the channel text fixes the drand round by procedure so the declarer cannot pick it, and whether a declared trial can be withdrawn after the beacon without counting. Either would reopen a route under (b).
- LightGBM's actual behaviour in the pinned environment, because it is not installed. DF-R6 relies on LightGBM's documented seed priority.
- The full Annex B text, for code references beyond R-8's list.
- The CPCV path construction details beyond l.215–222.
