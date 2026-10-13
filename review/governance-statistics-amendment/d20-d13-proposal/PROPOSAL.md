# D-20 (rest) and D-13: code bindings, null-test streams and the CPCV report (proposal, revision 5)

**Status:** `AI PROPOSAL — NOT AN OWNER DECISION — NOT ACTIVE`
**Date:** 2026-10-13
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`)

**History.**
- Rev 1 `37f20c8` was reviewed by Sol (`SOL_REVIEW_37F20C8.md`: Q1 NOT
  READY, Q2 READY WITH FIXES, Q3 NOT READY, Q4 READY WITH FIXES) and Fable
  (`FABLE_REVIEW_37F20C8.md`: Q1–Q4 READY WITH FIXES).
- Rev 2 applies `ADJUDICATION_37F20C8.md`, which accepts every finding, two of them
  (DC-R5, DC-R6) in part.
- Rev 2 `2db4d63` was re-checked by Sol (`SOL_RECHECK_2DB4D63.md`: Q1–Q3
  NOT READY, Q4 READY WITH FIXES) and Fable (`FABLE_RECHECK_2DB4D63.md`:
  Q1–Q4 READY WITH FIXES). Rev 3 applies `ADJUDICATION_2DB4D63.md` and adds
  owner question 2b (model libraries, §3a).
- Rev 3 `dba31fb` was narrowly re-checked by Fable
  (`FABLE_RECHECK2_DBA31FB.md`: Q1 and Q4 READY WITH FIXES, Q2, Q2b and Q3
  READY) and Sol (`SOL_RECHECK2_DBA31FB.md`: Q1, Q2b (a), Q3 and Q4 NOT
  READY; Q2 READY WITH FIXES). Rev 4 applies `ADJUDICATION_DBA31FB.md`.
- Rev 4 `4645e0a` was narrowly re-checked by Fable
  (`FABLE_RECHECK3_4645E0A.md`: Q1, Q2 and Q4 READY; Q2b and Q3 READY WITH
  FIXES, notes only) and Sol (`SOL_RECHECK3_4645E0A.md`: Q1, Q2, Q2b and Q4
  READY; Q3 NOT READY). Rev 5 applies `ADJUDICATION_4645E0A.md`, which
  narrows the §4 claims and adds three short notes.

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
| M7 | Annex C C-10 (3); gate list G-11; §2.4 `added_purposes` (all three purposes) | how the 500 G-11 shifts are sampled | §3 |
| M8 | Annex C C-12 (5); gate list G-14 | the G-14 offset and model-seed stream | §3 |
| M9 | the seed under C-1, C-10 (3), C-12 (5) | which seed feeds these streams (C-13 "Seeds", FA5-6) | §4 |
| M10 | Annex C C-10 (1); gate list G-11 | the `s_inputs` identity mapping and its enforcement | §5 |
| M11 | Annex C C-11 (5); DRAFT §5 table l.215–222 | what the CPCV diagnostic reports (D-13) | §6 |
| M13 | Annex B §2.4 l.110–113 (no marker) | the promised extension of the stream and I-10 vectors for `dsr_family_max_null` (DF2-R1) | §1 |

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
vectors must pass at the bound commit on the pinned runtime.
- The D-19 start gate already runs the reference-vector suite at every start
  (`rundef.start_gate`). Its G-1 trace covers the availability path: the
  production `bootstrap_indices`, `block_length` and influence routine, with
  the replicate Sharpes recomputed by `calibration.fast`.
- It does not exercise `paired_sharpe_improvement_interval` itself, the
  Task 12 Sharpe or `type_seven_quantile` (DF2-R7). For those, the condition
  rests on the Task 12 tests, which run in CI.

**What the calibration measured.** The D-19 engine computes G-1 and G-12
availability through the production routines (`calibration/gates.py`
imports `aqt.metrics.statistics`). G-1's availability rule matches the
interval routine's: any invalid replicate is `INVALID_REPLICATE`. G-9, the
DSR test, runs in `calibration/dsr.py`. The held-out `U_G` and
DSR-availability bounds are certified for that code, on the pinned
runtime.

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
| C-0 Sharpe; C-1 (G-1); C-11 (G-12) | `sharpe`, `paired_sharpe_statistics`, `paired_sharpe_improvement_influence`, `block_length` (Politis-White), `bootstrap_indices`, `replicate_seed_material`, `replicate_seed`, `SEED_DOMAIN`, `paired_sharpe_improvement_interval` and every function it calls, `type_seven_quantile`, `effective_sample_size` | `src/aqt/metrics/statistics.py` |
| C-0 `DD`, G-2 | `max_drawdown` | `src/aqt/metrics/descriptive.py` |
| C-6 4.2 (band tests) | `reaches_rebalance_band` | `src/aqt/benchmarks/canonical.py` |
| l.266 trial seed (DF-R2) | `seed_material`, `trial_seed` (domain `aqt.trial_seed.v1`) | `src/aqt/core/preregistration.py` |
| G-9 (Annex A P18-6; Annex B) (DF-R1, DF2-R1) | `evaluate` and the functions it calls, including the replicate seeds and indices `_replicate_seed` and `indices` (purpose `dsr_family_max_null`, with the `WINDOW` constant as a fixed domain label, not the C-0 window); replicate Sharpes by method V as already decided | `calibration/dsr.py` |

**Annex B §2.4's stream extension is superseded (M13; DF2-R1).** Annex B
§2.4 says the build "would extend the conventions ..., the stream, and
regenerate and review reference vectors (I-10)". The D-19 engine instead
built the DSR stream inline (`dsr._replicate_seed`), in the production
layout with the DSR purpose. It was reviewed under §16 with the engine.
- This proposal binds that construction as frozen (table above).
- It replaces the §2.4 sentence with: "The DSR replicate seeds and indices
  are `calibration/dsr.py` `_replicate_seed` and `indices` at the engine
  commit (R-8). The I-10 reference vectors are the D-19 reference-vector
  suite, which runs `dsr.evaluate`."
- `ReplicateStream` and IMPLEMENTATION_CONVENTIONS.md stay unchanged.

**Two bindings, and C2 must check both (DF-R14, DC2-R1, DC3-R1, DF3-R1).**
- **Engine files** bind to the engine commit (the table above).
- **Object files** bind to their reviewed bytes in the qualification
  object. These are the `qobj.LATER` files, reviewed separately and frozen
  at the freeze:
  - `calibration/mapping.py` (object `mapping.py`);
  - `calibration/screen.py` (object `screen.py`);
  - `scripts/d19_heldout.py` (object `heldout.py`).
- No C2 evaluation path exists yet. Its build must run two disjoint checks
  on the **loaded bytes**:
  1. each loaded `calibration` or `aqt` module that is not an object file
     must equal the engine commit's file;
  2. each object file, whether loaded as a module or run as the entry
     point, must equal the object's copy, verified against the posted
     object manifest. That copy **replaces** any engine-commit entry for the
     same path, as `mapping.check_engine` already does for `mapping.py`.
- Nothing may be loaded from outside these (`rundef.loaded_outside`).
- `mapping.check_engine` and the held-out runner's gate each cover one
  object file today. The C2 build generalises them. It is a §16 item of
  that build.
- **Build-order consequence (DF4-R1).** Under these checks the C2
  evaluation's own code (the B2 input validation, §4's `trial_seed_j`, the
  §6 path assembly and its entry point) can load only from the engine
  commit or from an object file such as `screen.py`. No third location can
  load. So that code must either be in the engine commit before the full
  run starts, or be built into an object file before the freeze.

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

This validation belongs to the C2 builder. The shared hashing step
`calibration.seeds.sha` does not validate; the engine's synthetic calls use
`round = rep`, which starts at 0 (prereg §8) (DF2-R4).

**Both places change.** The same `||` formula appears in R-7 and in
`seed_disclosure.derivation` (DRAFT l.157). Both are replaced (DF2-R4).

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
  - as `random_state` to every estimator whose constructor accepts
    `random_state`; deterministic estimators without it (such as
    `LinearRegression`) get no seed (DC2-R2, DF2-R3);
  - as `seed` to LightGBM.
- **Class map.** `screen.py` maps each protocol class name (linear, ridge,
  lasso, elastic_net, logistic, lightgbm) to one exact library class. Each
  class has a test showing that its refit is reproducible from
  `model_seed`.
- **No other source.** No other source of randomness may enter the refit
  pipeline. A declaration may not set LightGBM sub-seeds (`bagging_seed`,
  `feature_fraction_seed`, `data_random_seed`, `extra_seed`,
  `objective_seed`, `drop_seed`); LightGBM derives them all from `seed`.
- **Fixed LightGBM settings.** `deterministic = true`, `num_threads = 1`
  and `force_col_wise = true`.
- **The nominee's own fit** keeps the model seed its declaration fixes.
  Null draws never reuse it.
- **Runtime.** The model libraries must be in the D-19 image. §3a explains
  why, and gives the owner's choice.

**B6 — Seeds inside the screen.** The screen runs before the declaration
post, so it cannot use the beacon. Its null streams use the trial seed
`SHA256(cj({"path": p, "screen_seed": <hex>, "trial_id": <id>}))`, where:
- `screen_seed` is the §7.2 seed `SHA256(cj({"stream": "screen",
  "trial_set_sha256": <hex>}))`;
- `p = 0 … 29` is the screen path.

This is new. Rev 1 left it implicit. It adds sub-derivations to the
accepted prereg §7.2, which fixes only the screen seed. It is therefore
recorded as a **clarification of prereg §7.2**, with the owner's decision on
this proposal, not only as D-20 (DF2-R5). Inside the screen:
- `evaluation_window_id` is the C2 cycle's C-0 window id, which the
  declaration fixes;
- the bootstrap and sign streams of the screen's paths derive from
  `screen_seed` as `screen.py` implements them. **The reviewed code is the
  binding**, with its reference vectors.

**Disclosed (DC2-R6, DF2-R5).** The screen seed is a function of the trial
set, which the declarer controls, and has no nonce. A declarer can therefore
search trial sets offline for one that passes the screen. Recording every
submitted screen run cannot rule this out. The screen has no certified error
rate, so this weakens only its power claim, not the D-19 bound.

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
C2 evaluation imports them from the object's copy, checked by its bytes (§1).
`ReplicateStream` is not touched.

**Alternative.** numpy `Philox` streams, as in prereg §8. Their sampling
routines can change between numpy releases.

## 3a. Model libraries and the image (DC2-R3, DF2-R2) — a choice

The accepted preregistration says: "C2's real evaluation must run in the
same image" as the calibration (prereg §13 rev 7g item 6, A-V1). The screen
also runs from the frozen object.

**Today that image holds no model library.** `requirements.lock` pins only
numpy, and neither scikit-learn nor LightGBM is installed. Without them no
model-fitting trial can be screened or evaluated.

Adding a library later would change the image. Its digest is part of the
run definition and the gating identity, so a later change voids the run
(prereg §13 item 6). So the choice must be made **before the full run
starts**:

- **(a) Add scikit-learn and LightGBM to the image now** (recommended).
  - **How.** One §16-reviewed image PR, before the run definition is
    recorded and before any qualification on the image:
    - pin scikit-learn and LightGBM and every transitive dependency (SciPy,
      joblib, threadpoolctl and any other), with exact versions and hashes,
      in `requirements.lock`. The Dockerfile installs with
      `--require-hashes --only-binary :all:`;
    - the lock must resolve against `numpy==2.5.3` on CPython 3.14, so the
      NumPy pin, and with it method V's identity, does not move;
    - add any system library LightGBM's wheel needs (such as `libgomp1`)
      to the Dockerfile.
  - **How the libraries are bound (DC3-R2, DF3-R2).** Through the **image
    digest**, which is part of the gating identity and covers every byte of
    the image, these libraries included. No separate model-runtime identity
    is added, and no engine code changes. The C2 verification rule is the
    existing one: the evaluation runs in the image with the recorded digest
    (prereg l.536).
  - **What changes in the engine's record.** The image digest changes.
    The A-V1 gating identity also changes: `dsr.runtime_identity` hashes
    every `*openblas*` file under site-packages, so SciPy's bundled
    OpenBLAS enters it. This is harmless if it happens before the run
    definition is recorded.
  - **That the engine's numbers are unchanged is a claim to check, not an
    assumption (DC3-R2).** The image PR must show that both canaries and
    the full reference-vector suite give byte-identical outputs on the
    rebuilt image and on the current one. The run definition is then
    recorded on the rebuilt image. No earlier qualification on the old
    image is carried over.
  - **The re-pilot and the go-ahead (DF4-R2).** The re-pilot's measurements
    carry over on the strength of the proven-identical canary and
    reference-vector outputs: the rates, the cost and the speed come from
    engine code that imports none of the new libraries. The cheap checks are
    redone on the rebuilt image: the CPU probe and the interrupt-and-resume
    byte-identity test (prereg §13 item 6). FE-4's "image done" status
    reopens until the image PR is merged.
  - **What it keeps open.** Model-fitting trials stay possible in C2.
- **(b) No model-fitting trials in C2 under this object.** Every C2 trial
  must be a pure rule, so G-14 is always `N/A` (C-12 (1)). The image is
  unchanged.
  - **Cost.** The protocol's model classes are unusable in C2. Using them
    later needs a new image and a new qualification object.

Either way, **no library can be added after the run starts**. A model class
whose library is not in the recorded image cannot be declared under that
object.

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

**Within one cycle, no new route opens (DC-R5, DC2-R5).** The conditions Sol
asked for are already decided text:
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

**Across attempts, one route stays open, disclosed (DC2-R5, DF2-R6).** After
the beacon, a declarer with offline access to the window can compute G-1,
G-11 and G-14 under the beacon seeds. If they look bad, the declarer can
invalidate the cycle at will with a second post from A, then re-declare.
The window stays eligible (O-9 (a)).
- Each such retry costs one `m`, and `m` is the applicable multiplicity
  correction for false promotion: the `m`-th cycle's allowance is
  `0.05 / 2^(m−1)`. The total stays below 0.10 after any finite number of
  cycles, and is at most 0.10 overall (Constitution v1.1 §9; DC4-R3).
  - That arithmetic becomes a probability bound only if each cycle's test
    controls its error at its allowance **given the history that led to
    that cycle**. That holds when each re-declaration is fixed
    independently of the window's earlier outcomes.
  - A re-declaration adapted to what earlier attempts revealed on the same
    window breaks that premise. This is part of the disclosed open route
    (strategy search with offline access, DF-R10), and no allowance
    corrects it (DC4-R2, DF4-R3).
- For the seed-driven gates G-1, G-11 and G-14, a retry is only a price:
  they have no calibrated error rate. See the calibration point below.
- This is the FA5-3 residual, already disclosed. It is far narrower than
  (a)'s free search before the post.
- The rewritten C-13 bullet says so.

**Costs of (b) (DC-R6, DF-R10).**
- **Precedence.** For C-1, C-10 (3) and C-12 (5) only, (b) overrides
  l.266's seed policy. The wording "from the trial seed (l.266)" becomes
  "from the trial's beacon-protected seed (R-7)".
- **Beacon dependency.** G-1, G-11 and G-14 cannot run without the beacon,
  so they inherit R-7's beacon-failure handling (the cycle is invalidated,
  with no fallback).
- **Calibration (DC-R6, DC2-R4, DF2-R6).** Only G-1 matters here. G-11 and
  G-14 have no certified rate (they are screened gates), and G-9 already
  uses the beacon seed under R-7.
  - **What is certified.** The `U_G` bound is a probability over
    replications, each with its own G-1 stream seed: a SHA-256 hash that is
    fixed in advance and independent of the data (prereg §8). It is not a
    statement about any one fixed seed. Two fixed seeds can give different
    results, as Sol notes.
  - **The assumption it rests on.** The certified rate transfers to a C2
    attempt if that attempt's G-1 seed behaves like one more such draw: an
    unpredictable hash, independent of the data. This is a modelling
    assumption (SHA-256 as a random function), and no invariance bound
    proves it. It is the same assumption every hash-seeded rate in this
    project makes. **Adopting (b) records the owner's acceptance of this
    assumption.** If the owner does not accept it, neither option transfers
    the rate (DF3-R4).
  - **The claim covers a first attempt fixed in advance, not adaptive
    attempts or retained cycles (DC3-R3, DC4-R1).** If a cycle can be
    invalidated after the beacon and retried, a selected cycle is not one
    fresh draw. For example, keeping the better of two attempts turns a
    per-attempt probability `p` into `2p − p²` for the event the actor
    prefers. An attempt made only because an earlier one failed is
    conditioned on that failure, and its data may differ in law: if
    unavailability is driven by a feature of the data, the second attempt's
    unavailability can be near 1 even though the ex ante rate is `p`. So:
    - the D-19 `U_G` bound is asserted only for an attempt whose
      declaration is fixed before any outcome on the window is seen, in
      practice the first attempt on it. It is **not** asserted for an
      attempt reached adaptively, nor as a frequency over the cycles a
      declarer chooses to keep. No conditional, sequential argument is
      offered;
    - `U_G` bounds **unavailability**, a no-result outcome. Retrying to
      escape unavailability can only lower the unavailability of the
      retained cycles, so it cannot make the certified bound
      anti-conservative;
    - retrying to reach a G-1, G-11 or G-14 *pass* is not covered by any
      certified rate here. These gates are filters with no calibrated
      error rate of their own (C-13).
    - for false promotion, the allowance rule applies under the
      conditional premise stated above (each attempt's test valid at its
      allowance given its history). This stays disclosed in C-13.
  - **How each option meets it.**
    - (b) meets it for every attempt whose declaration is fixed in advance.
      Retries change only the uncertified pass frequencies over retained
      cycles (DF4-R3).
    - (a) does not meet it: the l.266 seed can be searched for free before
      the post.
    - So (a) is **not** a safe fallback. If the assumption is rejected,
      neither option transfers the rate, and G-1's rate would need its own
      qualification.
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
  - **Path assembly (DF2-R8, DC2-R7).**
    - The `T` OOS days form 8 chronological groups `g = 0 … 7`. The
      remainder days go to the earliest groups, as in G-10.
    - The 28 splits are the pairs `{a, b}` with `a < b`, in lexicographic
      order. Each split trains on the other 6 groups, with purge and
      embargo, and predicts its 2 test groups.
    - **Paths (DC3-R4).** Path `p = 1 … 7` is made of the 4 splits
      `{g, g XOR p}`, for `g = 0 … 7` (bitwise exclusive or). Each path
      covers all 8 groups exactly once, each split is used in exactly one
      path, and both test groups of a split go to the same path. Path 1,
      for example, is `{0,1}, {2,3}, {4,5}, {6,7}`. Rev 3's rank rule
      split a split's two groups across paths, and is withdrawn.
    - **State at each group (DF3-R5).** Each test group is simulated from
      its own first 00:00 UTC decision, starting flat: exposure 0, no
      pending order, an unset clock and a fresh overlay state (as C-10 (4)
      starts a draw). The benchmark is the window's single benchmark
      series, sliced by group.
    - A path's daily candidate and benchmark returns are its 8 groups'
      returns concatenated in chronological order.
    - Per path: `E-IMPROV` = Sharpe(candidate) − Sharpe(benchmark), and
      `E-DIFF` = Sharpe(candidate − benchmark), by `sharpe` and
      `paired_sharpe_statistics` (§1).
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
     D-19 engine commit recorded in the qualification object. The object
     files (`mapping.py`, `screen.py`, `heldout.py`) bind to their reviewed
     bytes in the object. Lockbox clauses are reserved.
   - R-7's family-seed formula is amended to the engine's named-object
     encoding.
   - Options: Adopt (recommended), or keep blocked.
2. **Null-test streams and `s_inputs` (§3, §5).** The G-11 and G-14 stream
   rules, the model-seed rules, the screen's seeds (a clarification of
   prereg §7.2), and the `s_inputs` mapping, all built and frozen in
   `screen.py`.
   - Options: Adopt (recommended), or use numpy Philox streams.

   2b. **Model libraries (§3a).**
   - Options: (a) add scikit-learn and LightGBM to the image before the full
     run, through one reviewed image PR that proves the engine's outputs
     unchanged (recommended), or (b) no model-fitting trials in C2 under
     this object.
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
- The engine code is not changed. Under §3a (a), the engine image changes,
  through its own reviewed PR.
- No calibration run, cycle, trial, data access, deployment or trading is
  authorized.
- No statistician has reviewed this.
