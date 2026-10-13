# D-20 (rest) and D-13: code bindings, null-test streams and the CPCV report (proposal, revision 2)

**Status:** `AI PROPOSAL — NOT AN OWNER DECISION — NOT ACTIVE`
**Date:** 2026-10-13
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`)

**History.**
- Rev 1 `37f20c8` was reviewed by Sol (`SOL_REVIEW_37F20C8.md`: Q1 NOT
  READY, Q2 READY WITH FIXES, Q3 NOT READY, Q4 READY WITH FIXES) and Fable
  (`FABLE_REVIEW_37F20C8.md`: Q1–Q4 READY WITH FIXES).
- Rev 2 applies `ADJUDICATION_37F20C8.md`, which accepts every finding, two of them
  (DC-R5, DC-R6) in part.

**Why now.** The §7.2 declared-strategy screen is the last piece of code
before the D-19 freeze. It runs G-11 and G-14, so it needs their open
mechanics and the `s_inputs` mapping. The build-order review (BO-2,
`SOL6_BUILD_ORDER_REVIEW_D321147.md`) requires every open marker in Annex C
to be closed before the freeze. These markers act only on a declared trial
set. They cannot change which calibration cells qualify, the thresholds or
`z_crit` (prereg §1, §7).

**Scope.** Every `<<OPEN D-20>>` and `<<OPEN D-13>>` marker in the S4 draft
(`s4-amendment-draft/`):

| # | Where | What is open | Section |
|---|---|---|---|
| M1 | DRAFT §2.0 R-8; Annex C C-0 "Code bindings" | the hash that the named existing code binds to | §1 |
| M2 | Annex C C-0 "Sharpe" | the Sharpe code | §1 |
| M3 | Annex C C-1; gate list G-1 | the paired-CI routine | §1 |
| M4 | Annex C C-6 4.2 | the band routine `reaches_rebalance_band` | §1 |
| M5 | Annex C C-11 (via R-8) | the ESS code | §1 |
| M12 | gate list G-9 ("code binding `<<OPEN D-20>>`") | the DSR test code (DF-R1) | §1 |
| M6 | seed_disclosure `derivation`; R-7 | the byte encoding of the beacon-extended family seed | §2 |
| M7 | Annex C C-10 (3); gate list G-11; §2.4 `added_purposes` | how the 500 G-11 shifts are sampled | §3 |
| M8 | Annex C C-12 (5); gate list G-14 | the G-14 offset and model-seed stream | §3 |
| M9 | the seed under C-1, C-10 (3), C-12 (5) | which seed feeds these streams (C-13 "Seeds", FA5-6) | §4 |
| M10 | Annex C C-10 (1); gate list G-11 | the `s_inputs` identity mapping and its enforcement | §5 |
| M11 | Annex C C-11 (5); DRAFT §5 table l.215–222 | what the CPCV diagnostic reports (D-13) | §6 |

**Not in scope.** These stay open:
- D-11 (the lockbox interval, which is bootstrap-backed) and D-12;
- every D-20 binding of a lockbox clause (L-1..L-4, l.83–92), which is
  expressly reserved (DC-R8);
- the G-9 values (`<<D19>>`);
- the signing values (`<<SIGNING>>`).

## 1. Existing code: what it binds to (M1–M5, M12)

**D-20 is triggered.** The matrix says D-20 "is triggered by the first
acceptance among D-03 or D-11", and D-03 is accepted (DC-R1, DF-R3). So this
section answers the row.

**For G-1, this proposal picks row option (b), "reuse the Task 12
stream".** The row's recommended option is (a), a migration with refreshed
reference vectors. That option exists for a clause whose estimand differs
from the Task 12 influence process, because then the block length and every
resample would change.

G-1 has no such difference:
- D-03 decided G-1 on `E-IMPROV` (Annex C C-1).
- The Task 12 paired-CI routine is built on the `E-IMPROV` influence
  process (`paired_sharpe_improvement_influence`).
- The estimand, the influence process, the block length and the resamples
  are therefore those of the existing code. Nothing migrates, and no vector
  is regenerated.

This argument does not, on its own, show the existing vectors are valid.
**Acceptance condition:** the existing Task 12 tests and the D-19 reference
vectors must pass at the bound commit on the pinned runtime. The D-19 start
gate already runs the reference-vector suite, including the G-1 trace, at
every start (`rundef.start_gate`). The Task 12 tests run in CI.

**The calibration already uses this code.** The D-19 engine computes G-1
and G-12 availability through the production routines
(`calibration/gates.py` imports `aqt.metrics.statistics`). G-9, the DSR
test, runs in `calibration/dsr.py`. The held-out `U_G` and DSR-availability
bounds are certified for that code, on the pinned runtime.

**Proposal (B1).** The R-8 references listed below bind to the files as
they stand at the **engine commit recorded in the D-19 qualification
object** (`definition.json` `engine_commit`), and to the object's pinned
runtime identity.
- That commit is checked by its code inventory hash (`generator_sha256`).
  The hash covers `calibration/`, `src/aqt/` and `scripts/d19_*.py`, as
  canonical SHA-256 with CRLF read as LF.
- This is the same mechanism R-8 already uses for method V (A-V1).
- R-8 is re-worded to name these clauses only (DC-R8).

| Clause | Reference | Code at the engine commit |
|---|---|---|
| C-0 Sharpe; C-1 (G-1); C-11 (G-12); Annex B replicate seeds | `sharpe`, `paired_sharpe_statistics`, `paired_sharpe_improvement_influence`, `block_length` (Politis-White), `bootstrap_indices`, `replicate_seed_material`, `replicate_seed`, `SEED_DOMAIN`, `paired_sharpe_improvement_interval` and every function it calls, `type_seven_quantile`, `effective_sample_size` | `src/aqt/metrics/statistics.py` |
| C-0 `DD`, G-2 | `max_drawdown` | `src/aqt/metrics/descriptive.py` |
| C-6 4.2 (band tests) | `reaches_rebalance_band` | `src/aqt/benchmarks/canonical.py` |
| l.266 trial seed (DF-R2) | `seed_material`, `trial_seed` (domain `aqt.trial_seed.v1`) | `src/aqt/core/preregistration.py` |
| G-9 (Annex A P18-6; Annex B) (DF-R1) | `evaluate` and the functions it calls; replicate Sharpes by method V as already decided | `calibration/dsr.py` |

**C2 must check its code (DF-R14).** No C2 evaluation path exists yet. Its
build must load only the code above, verified against the object's
`engine_commit` by the same check the mapping and the held-out runner use
(`mapping.check_engine` and `rundef.loaded_outside`). That check is a §16
item of the C2 evaluation build.

**Falsifier.** Any C2 evaluation that calls a different version of a bound
routine.

**Consequence.** The engine commit is fixed only when the full run starts.
Until the object exists, the binding is a reference, not a value. This is
the same as the V binding today.

**Alternatives.**
- (b′) Bind to the Task 12 commit that first introduced the code. That
  version could differ from what the calibration measured.
- (c) Keep blocked. C2 cannot then be evaluated.

## 2. Byte encoding of the beacon-extended family seed (M6)

R-7 writes `family_seed_f = SHA256(annexB_family_seed_f || round ||
beacon_randomness)` and leaves the bytes of `||` open.

The engine already uses one encoding (`calibration/seeds.py`, final step of
`family_seed`):

```
family_seed_f = SHA256(cj({"annex_b_seed": <hex>, "beacon_randomness": <hex>, "round": <int>}))
```

Here `cj` is canonical JSON: UTF-8, sorted keys, no whitespace, decimal
integers, lowercase hex (prereg §8).

The sorted keys serialise in a different order from R-7's written order.
**This is therefore an amendment of R-7's wording, not just a choice of
bytes** (DC-R2).

**Proposal (B2).** Amend R-7's formula to the named-object form above.
Inputs are validated before hashing (DF-R11):
- `annex_b_seed`: the Annex B §2.4 family-seed digest, as 64-character
  lowercase hex;
- `beacon_randomness`: the drand `randomness` field (not `signature`), as
  64-character lowercase hex;
- `round`: the drand round number fixed by the R-7 procedure, as a
  positive integer.

**Why this, not R-7's literal order.**
- The D-19 engine is reviewed and merged with this form. Its synthetic
  seeds use it (prereg §8 R-7; `seeds.py` marks it provisional).
- Changing the engine now would change its synthetic draws and force a
  re-review. The calibration's validity does not depend on the encoding,
  only on seeds fixed in advance.
- The C2 builder shares the final hashing step, `calibration.seeds.sha`,
  over this object. The C2 Annex B seed itself is built from the real
  declaration, not the synthetic fields (DF-R11).

**Alternative.** An ordered array in R-7's order: `cj([annex_b_seed,
round, beacon_randomness])`. It is equally sound, and R-7's wording stands.
But it needs a second encoding and changes the calibration's synthetic
draws, so the engine would need re-review.

## 3. Null-test streams (M7, M8)

**Stream material.** Each generator is seeded from canonical material in
the same form as the production replicate stream:

```
seed = SHA256(json.dumps([SEED_DOMAIN, trial_seed_hex, CONVENTION_DOCUMENT_SHA256,
                          purpose, "BTCUSDT", "1.0", evaluation_window_id,
                          *indices], separators=(",", ":"), ensure_ascii=False))
```

- `SEED_DOMAIN` is `"aqt.statistics.stream.v1"`.
- `CONVENTION_DOCUMENT_SHA256` is reused only as a fixed domain field.
  That document does not describe these streams (DF-R8).
- `purpose` is `"random_exposure_null"` or `"shuffled_labels_null"` (§2.4
  `added_purposes`).
- `evaluation_window_id` is the canonical string the production stream
  already validates: the JSON array
  `["<w0>","<w1>"]`, each element formatted as `YYYY-MM-DDT00:00:00Z`, with
  no spaces (C-0 window; DC-R4).
- `trial_seed_hex` is set by §4 in C2, and in the screen by B6 below.
- G-11 uses one generator for all 500 shifts. G-14 uses one generator per
  (draw, window) (DF-R8).

**Generator.**
- The generator is CPython `random.Random`, seeded with
  `int.from_bytes(bytes.fromhex(seed), "big")`.
- An integer in `[0, n)` is `_uniform_index`: rejection sampling on
  `getrandbits(n.bit_length())`, exactly as `bootstrap_indices` draws.
- No `random.sample`, `shuffle` or `randrange` is used. Python documents
  their algorithms as subject to change.

**Stability.** Python guarantees only that `random()` repeats for the same
seed. Integer seeding and `getrandbits` are not formally guaranteed. The
bound `bootstrap_indices` relies on the same calls, and for both, stability
comes from the pinned runtime. The interpreter binary's hash is part of the
runtime identity (`dsr.runtime_identity`), and the reference vectors below
detect any drift.

**G-11 shifts (B3).** There is one generator, with `indices = [500]`.
- If `T − 2m < 499`, the gate is `UNAVAILABLE`, with reason
  `INSUFFICIENT_SHIFT_RANGE`. `P` below has `T − 2m + 1` elements (DC-R9).
- Let `P` be `[m, m+1, …, T − m]`, in ascending order.
- For `i = 0 … 499`: set `j = i + _uniform_index(gen, len(P) − i)`, swap
  `P[i]` and `P[j]`, and set `k_i = P[i]`.
- This is a partial Fisher–Yates shuffle, so the shifts are distinct and
  drawn without replacement, and the sample is unbiased. Sol and Fable both
  confirmed this (DC-R9, DF-R9).
- The draw order only labels the reported draws.

**G-14 offsets (B4).** Let window `w = 0, 1, …` be the trial's walk-forward
training windows in time order, starting from the first.
- `n_w` is the number of rows **retained** in window `w` after purge and
  embargo, in time order (DF-R4, DC-R4).
- Each draw `d = 0 … 499` and window `w` gets its own generator, with
  `indices = [d, w]`.
- From it: `offset = lo + _uniform_index(gen, hi − lo + 1)`, with `lo =
  horizon_days` and `hi = n_w − horizon_days`.
- The null label of retained row `r` is `label[(r + offset) mod n_w]`.
- If `hi < lo` in any window, the gate is `UNAVAILABLE`, with reason
  `NO_SHIFT_RANGE`. Windows are never dropped.

**G-14 model seeds (B4, continued; DC-R3, DF-R5, DF-R6).**
- **Seed.** After the offset, the same generator gives `model_seed =
  gen.getrandbits(31)`. The refit passes `model_seed`:
  - as `random_state` to every scikit-learn class (linear, ridge, lasso,
    elastic net, logistic), whatever its solver;
  - as `seed` to LightGBM.
- **No other source.** No other source of randomness may enter the refit
  pipeline. A declaration may not set LightGBM sub-seeds (`bagging_seed`,
  `feature_fraction_seed`, `data_random_seed`, `extra_seed`,
  `objective_seed`, `drop_seed`); LightGBM derives them all from `seed`.
- **Fixed LightGBM settings.** `deterministic = true`, `num_threads = 1`
  and `force_col_wise = true`.
- **The nominee's own fit** keeps the model seed its declaration fixes.
  Null draws never reuse it.
- **Runtime.** The model libraries are part of the evaluation runtime
  identity: the scikit-learn and LightGBM versions and binary hashes. A
  declaration whose model class needs a library missing from the recorded
  runtime is refused.

  LightGBM is not installed today. So until a runtime with it is recorded
  and reviewed, `lightgbm`-class trials cannot be declared (DF-R6).

**B6 — Seeds inside the screen.** The screen runs before the declaration
post, so it cannot use the beacon. Its null streams use the trial seed
`SHA256(cj({"path": p, "screen_seed": <hex>, "trial_id": <id>}))`, where:
- `screen_seed` is the §7.2 seed `SHA256(cj({"stream": "screen",
  "trial_set_sha256": <hex>}))`;
- `p = 0 … 29` is the screen path.

This is new. Rev 1 left it implicit.

**Reference vectors (DF-R7).** The screen build freezes, with its review:
- the first 10 `k_i` for a fixed seed, `T` and `m`, together with the
  SHA-256 of all 500 `k_i`;
- `(offset, model_seed)` for `d ∈ {0, 499}` and `w ∈ {0, 1}`, together with
  the SHA-256 over the full `d × w` grid for a fixed set of `n_w`.

They go into the object with `screen.py`. They are new vectors for new
code, not a migration.

**Where the code lives.** These functions, the B6 seed and the `s_inputs`
mapping (§5) live in `calibration/screen.py`. That file is frozen in the
qualification object, which already lists it (`qobj.LATER`, `REVIEWED`). It
is reviewed under §16, with the owner's PR review, before the freeze. The
C2 evaluation imports them from the object's copy. `ReplicateStream` is not
touched.

**Alternative.** numpy `Philox` streams, as in prereg §8. Their sampling
routines can change between numpy releases.

## 4. Which seed feeds the streams in C2 (M9) — a choice

Annex C says that the G-1 bootstrap, the G-11 shifts and the G-14 offsets
come from **the trial seed of l.266**: `SHA256(protocol_hash,
hypothesis_hash, trial_index)`. C-13 discloses the weakness (FA5-6). That
seed is known before the declaration post, so a declarer can edit a
hypothesis cosmetically, recompute G-1, G-11 and G-14 offline for each
version, and post the luckiest one.

- **(a) Keep the l.266 trial seed.** The decided text is unchanged, and the
  disclosed route remains.
- **(b) Beacon-protected trial seed** (recommended). For these three
  streams only, use
  `trial_seed_j = SHA256(cj({"family_seed": family_seed_f, "trial_id":
  <id>}))`.
  - `family_seed_f` is §2's beacon-extended seed.
  - `trial_id` is exactly the `trial_id` that Annex B §2.4 hashes.
  - The nominee's own fit, and anything else that uses l.266, are
    unchanged.

**What (b) closes, and what it does not (DF-R10).** It closes the seed
search for the G-1 bootstrap and both null streams. It does **not** close:
- a search over the nominee's own model seed, which is still fixed before
  the post;
- a search over the strategy itself by a declarer with offline access.

The C-13 "Seeds" bullet is therefore **rewritten, not deleted**. It names
the closed route and keeps these two open routes.

**Why no new route opens (DC-R5).** The conditions Sol asked for are
already decided text:
- the complete trial set `J_f` is frozen by hash before any evaluation
  (Annex A P18-1);
- the first post on the channel governs, and any later post invalidates the
  cycle (seed_disclosure `first_post_rule`);
- the round is fixed by procedure from the archive-capture time, so the
  declarer cannot pick it (`round`);
- there is one nomination look, after every declared trial has been
  evaluated (P18-2);
- an abort after the beacon costs one halving of the allowance (FA5-3,
  `invalidation_after_post`).

**Costs of (b) (DC-R6, DF-R10).**
- **Precedence.** For C-1, C-10 (3) and C-12 (5) only, (b) overrides
  l.266's seed policy. The wording "from the trial seed (l.266)" becomes
  "from the trial's beacon-protected seed (R-7)".
- **Beacon dependency.** G-1, G-11 and G-14 cannot run without the beacon,
  so they inherit R-7's beacon-failure handling (the cycle is invalidated,
  with no fallback).
- **Calibration.** The D-19 certification is unaffected.
  - The calibration models each replication's stream seed as a fixed hash
    that is independent of the data (the synthetic outer seed, prereg §8).
  - The certified rates are rates over the data law, at seeds that do not
    depend on the data.
  - Under (b), the C2 seed is a hash of public randomness that the declarer
    cannot choose. That matches this model at least as well as (a), whose
    seed the declarer can pick.
  - The reviewers are asked to confirm this argument. If it fails, (b)
    would need requalification, and (a) would be the safe choice.
- **Audit.** The C2 evaluation must record `trial_seed_j` for every trial
  and every stream (Constitution §27).

## 5. `s_inputs` enforcement (M10)

Rev 1 left this to the later C2 build. That collides with BO-2, the rule
that every marker closes before the freeze. Both reviewers flagged it
(DC-R7, DF-R12).

The screen needs this mapping anyway, because G-11 shifts `s`, and `s` may
read only its declared inputs.

**Proposal (B5).** The identity mapping and its enforcement are built in
`calibration/screen.py`. That means:
- they are frozen in the qualification object, so one hash serves the
  whole cycle and is the same for every trial;
- they are reviewed under §16, with the owner's PR review, **before the
  freeze**;
- they carry their own falsifier test: a declaration that puts
  `ewma_vol_168h` (or `σ̂`) in a `σ̂`-sized trial's `s_inputs` is rejected.

The C2 evaluation uses the object's copy. The marker then reads: "the
mapping and its enforcement in the qualification object's `screen.py`".

## 6. D-13: what the CPCV diagnostic reports (M11)

**Frozen text** (`protocol_v1.yaml` l.215–222): CPCV runs only if effective
decisions are at least 250 (with C-11's ESS definition). It uses 8 groups,
2 of them test groups: 28 splits, which make 7 paths. Its role is
`diagnostic_only`, and it reports the "median and 5th-percentile path
paired-delta-Sharpe; no independent promotion gate". D-01 made `E-IMPROV`
and `E-DIFF` both registered estimands, so "paired-delta-Sharpe" is now
ambiguous.

**Options** (matrix row D-13):
- **(a) Both estimands, separately labelled** (recommended). Report the
  median and the 5th percentile over the 7 path values, for `E-IMPROV` and
  for `E-DIFF`, each named.
  - **Quantiles.** Both are `type_seven_quantile`, at 0.5 and 0.05 (§1
    binding; DF-R13).
  - **Unavailability.** A path whose Sharpe, or whose `E-DIFF` on a
    zero-variance difference, is unavailable is reported as unavailable.
    The summaries for that estimand are then reported as unavailable. Paths
    are never dropped.
  - **Below 250.** If effective decisions are below 250, the report says
    "CPCV not enabled", and nothing is computed.
  - **Nothing reads it.** Neither output is consumed by any gate, the
    screen, the mapping, the DSR test, the nomination or promotion.
  - **What it binds.** These two labelled reporting outputs and their
    conventions (DC-R10). Choosing only one estimand would quietly set a
    precedent for a row that does gate.
- **(b) One estimand only.** It picks a winner without a reason.
- **(c) Report nothing.** This contradicts frozen l.221.

CPCV needs no random stream, because its splits are combinatorial. D-13
therefore adds nothing to D-20.

**Statistical acceptance.** The matrix gives this row a `STAT` authority.
No statistician has reviewed it. The owner's decision records that, as for
the earlier rows.

## 7. Owner questions (after the re-check)

1. **Code bindings (§1, §2).**
   - D-20 is triggered. For G-1 this picks row option (b): reuse the Task
     12 stream, which is safe because the estimand is unchanged.
   - The named code (including the trial-seed and DSR code) binds to the
     D-19 engine commit recorded in the qualification object. Lockbox
     clauses are reserved.
   - R-7's family-seed formula is amended to the engine's named-object
     encoding.
   - Options: Adopt (recommended), or keep blocked.
2. **Null-test streams and `s_inputs` (§3, §5).** The G-11 and G-14 stream
   rules, the model-seed and runtime requirements, the screen's seeds, and
   the `s_inputs` mapping, all built and frozen in `screen.py`.
   - Options: Adopt (recommended), or use numpy Philox streams.
3. **Seed source in C2 (§4).**
   - Options: (b) beacon-protected seed (recommended), or (a) keep the
     l.266 trial seed.
4. **D-13 (§6).**
   - Options: (a) both estimands (recommended), (b) one, or (c) nothing.

## Not changed by this proposal

- No frozen file, and no `HUMAN_DECISION_MATRIX.md`, is edited.
- Nothing is activated.
- The S4 draft is not yet edited. After the owner's answers, the markers are
  replaced with these texts in a separate revision.
- The engine is not changed.
- No calibration run, cycle, trial, data access, deployment or trading is
  authorized.
- No statistician has reviewed this.
