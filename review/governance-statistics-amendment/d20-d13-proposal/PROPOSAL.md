# D-20 (rest) and D-13: code bindings, null-test streams and the CPCV report (proposal, revision 1)

**Status:** `AI PROPOSAL — NOT AN OWNER DECISION — NOT ACTIVE`
**Date:** 2026-10-13
**Drafted by:** Claude Opus 5.5 (`claude-opus-5-5`)

**Why now.** The §7.2 declared-strategy screen is the last piece of code
before the D-19 freeze. It runs G-11 and G-14, so it needs their open
mechanics. The build-order review (BO-2, `SOL6_BUILD_ORDER_REVIEW_D321147.md`)
also requires every open marker in Annex C to be closed before the freeze.
These markers act only on a declared trial set. They cannot change which
calibration cells qualify, the thresholds or `z_crit` (prereg §1, §7).

**Scope.** Every `<<OPEN D-20>>` and `<<OPEN D-13>>` marker in the S4 draft
(`s4-amendment-draft/`):

| # | Where | What is open | Section |
|---|---|---|---|
| M1 | DRAFT §2.0 R-8; Annex C C-0 "Code bindings" | the hash that the named existing code binds to | §1 |
| M2 | Annex C C-0 "Sharpe" | the Sharpe code | §1 |
| M3 | Annex C C-1; gate list G-1 | the paired-CI routine | §1 |
| M4 | Annex C C-6 4.2 | the band routine `reaches_rebalance_band` | §1 |
| M5 | Annex C C-11 (via R-8) | the ESS code | §1 |
| M6 | seed_disclosure `derivation`; R-7 | the byte encoding of the beacon-extended family seed | §2 |
| M7 | Annex C C-10 (3); gate list G-11; §2.4 `added_purposes` | how the 500 G-11 shifts are sampled | §3 |
| M8 | Annex C C-12 (5); gate list G-14 | the G-14 offset and model-seed stream | §3 |
| M9 | the seed under C-1, C-10 (3), C-12 (5) | which seed feeds these streams (C-13 "Seeds", FA5-6) | §4 |
| M10 | Annex C C-10 (1); gate list G-11 | the `s_inputs` identity mapping and its enforcement | §5 |
| M11 | Annex C C-11 (5); DRAFT §5 table l.215–222 | what the CPCV diagnostic reports (D-13) | §6 |

**Not in scope.** These stay open:
- D-11 (the lockbox interval, which is bootstrap-backed) and D-12;
- D-20 for any lockbox clause;
- the G-9 values (`<<D19>>`);
- the signing values (`<<SIGNING>>`).

## 1. Existing code: what it binds to (M1–M5)

**Background.** D-20 was written to stop a quiet migration. If a
bootstrap-backed clause were bound to `E-DIFF`, its influence process, and so
its block length and every resample, would change. The fix needs a reviewed
migration with new reference vectors (Lesson 6; matrix row D-20; Astra B5).

**Finding.** That trigger does not fire for the existing code:
- **G-1 does not change estimand.** D-03 decided G-1 on `E-IMPROV` (Annex C
  C-1). The Task 12 paired-CI routine is built on exactly the `E-IMPROV`
  influence process (`paired_sharpe_improvement_influence`). Binding it
  as-is therefore changes nothing, and the existing reference vectors stay
  valid.
- **The other routines carry no estimand choice.** These are the Sharpe,
  ESS, `max_drawdown` and band routines.

**The calibration already uses this code.** The D-19 engine computes G-1
and G-12 availability through the production routines
(`calibration/gates.py` imports `aqt.metrics.statistics`). The held-out
`U_G` bound is certified for that code, on the pinned runtime. Binding any
other version would leave the certified rate without a referent.

**Proposal (B1).** Each R-8 reference binds to the file as it stands at the
**engine commit recorded in the D-19 qualification object**
(`definition.json` `engine_commit`). That commit is checked by its code
inventory hash (`generator_sha256`, covering `calibration/`, `src/aqt/` and
`scripts/d19_*.py`; canonical SHA-256, CRLF read as LF). It also binds to
the object's pinned runtime identity. This is the same mechanism R-8
already uses for method V (A-V1). Named routines and files:

| Reference | Code at the engine commit |
|---|---|
| `bootstrap_indices`, replicate-seed construction (`replicate_seed_material`, `replicate_seed`, `SEED_DOMAIN`), Politis-White (`block_length`), paired CI (`paired_sharpe_improvement_interval` and the functions it calls), Task 12 Sharpe (`sharpe`, `paired_sharpe_statistics`), ESS (`effective_sample_size`) | `src/aqt/metrics/statistics.py` |
| `max_drawdown` | `src/aqt/metrics/descriptive.py` |
| `reaches_rebalance_band` | `src/aqt/benchmarks/canonical.py` |

- **Reference vectors.** These are the existing Task 12 vectors
  (`review/task12/IMPLEMENTATION_CONVENTIONS.md`) and the D-19 reference
  vectors recorded in the object's `gating.reference_vectors`. No vectors
  are regenerated, because no estimand changes.
- **Falsifier.** Any C2 evaluation path that calls a different version of a
  named routine. The evaluation must verify that the loaded files equal the
  engine commit's, as the mapping and held-out runner already do (MP-4,
  HO-1).
- **Consequence.** The engine commit is fixed only when the full run
  starts. Until the object exists, the binding is a reference, not a value.
  This is the same as the V binding today.

**Alternatives.**
- (b) Bind to the Task 12 commit that first introduced the code. That
  version could differ from what the calibration measured.
- (c) Keep blocked. C2 cannot then be evaluated.

## 2. Byte encoding of the beacon-extended family seed (M6)

R-7 fixes `family_seed_f = SHA256(annexB_family_seed_f || round ||
beacon_randomness)` and leaves the bytes of `||` open.

The engine already implements one encoding (`calibration/seeds.py`
`family_seed`, provisional):

```
family_seed_f = SHA256(cj({"annex_b_seed": <hex>, "beacon_randomness": <hex>, "round": <int>}))
```

Here `cj` is canonical JSON: UTF-8, sorted keys, no whitespace, decimal
integers, lowercase hex (prereg §8).

**Proposal (B2).** Adopt exactly this encoding. The calibration's synthetic
family seeds and the C2 family seeds are then made by one function, so there
is one code path to bind (§1). The calibration's results do not depend on
the encoding. Its seeds only need to be fixed in advance, and they are.

**Alternative.** Raw byte concatenation: 32-byte digest, 8-byte big-endian
round, 32-byte randomness. It is equally sound, but it needs a second
implementation.

## 3. Null-test streams (M7, M8)

**One stream convention for both null tests.** Each draw gets its own seed
from canonical material in the same form as the production replicate stream:

```
seed = SHA256(json.dumps([SEED_DOMAIN, trial_seed_hex, CONVENTION_DOCUMENT_SHA256,
                          purpose, "BTCUSDT", "1.0", evaluation_window_id,
                          *indices], separators=(",", ":"), ensure_ascii=False))
```

- `SEED_DOMAIN` is `"aqt.statistics.stream.v1"`.
- `purpose` is `"random_exposure_null"` or `"shuffled_labels_null"` (§2.4
  `added_purposes`).
- `indices` are given below.
- The generator is CPython `random.Random`, seeded with
  `int.from_bytes(bytes.fromhex(seed), "big")`. This is the Mersenne
  Twister.
- An integer in `[0, n)` is `_uniform_index`: rejection sampling on
  `getrandbits(n.bit_length())`, exactly as `bootstrap_indices` draws.
- No `random.sample`, `shuffle` or `randrange` is used. Python documents
  their algorithms as subject to change.
- **Stability.** Python guarantees only that `random()` repeats for the
  same seed; integer seeding and `getrandbits` are not formally guaranteed.
  As for the bound `bootstrap_indices`, which relies on the same calls,
  stability comes from the pinned runtime: the Python version is part of
  the object's runtime identity, and the reference vectors below detect
  any change.

**G-11 shifts (B3).** There is one generator, with `indices = [500]` (the
output length).
- Let `P` be the list `[m, m+1, …, T − m]`, in ascending order.
- For `i = 0 … 499`: set `j = i + _uniform_index(gen, len(P) − i)`, swap
  `P[i]` with `P[j]`, and set `k_i = P[i]`.
- This is a partial Fisher–Yates shuffle, so the 500 shifts are distinct
  and drawn without replacement, as C-10 (3) requires.
- The draw order only labels the reported draws. The pass count does not
  depend on it.

**G-14 offsets and model seeds (B4).** Each draw `d = 0 … 499` and each
walk-forward training window `w = 0, 1, …` (in time order) gets its own
generator, with `indices = [d, w]`. From that generator:
1. `offset = lo + _uniform_index(gen, hi − lo + 1)`, where `lo =
   horizon_days` and `hi = window_length − horizon_days` (C-12 (3)). If
   `hi < lo`, the gate is `UNAVAILABLE`, with reason `NO_SHIFT_RANGE`.
2. Then `model_seed = gen.getrandbits(31)`, which every allowed model class
   accepts. LightGBM uses it as its `seed`. Deterministic classes (linear,
   ridge, lasso, elastic net, logistic) ignore it.

The nominee's own fit keeps the model seed its declaration fixes. Null
draws never reuse it.

**Reference vectors.** The screen build adds frozen vectors for both
streams: the first 10 `k_i` for a fixed seed, `T` and `m`; and `(offset,
model_seed)` for `d ∈ {0, 499}`, `w ∈ {0, 1}`. They are reviewed with that
code and recorded in the object. They are new vectors for new code, not a
migration.

**Code change this needs.** `ReplicateStream` accepts only `purpose =
"paired_sharpe_ci"` and replicate indices 0..1999. The null streams
therefore get their own small function, in the screen's code, that builds
the material above. The paired-CI stream is not touched.

**Alternative.** numpy `Philox` streams, as in prereg §8. Their sampling
routines (`Generator.choice`, `integers`) can change between numpy
releases. They are safe only under the pinned runtime, and Python's
`getrandbits` path does not depend on numpy at all.

## 4. Which seed feeds the streams (M9) — a choice

Annex C says that the G-1 bootstrap, the G-11 shifts and the G-14 offsets
come from **the trial seed of l.266**: `SHA256(protocol_hash,
hypothesis_hash, trial_index)`. C-13 discloses the weakness (FA5-6). That
seed is known before the declaration post, so a declarer can make cosmetic
edits to the hypothesis text, recompute G-11 and G-14 offline for each
version, and post the luckiest one. The 476-of-500 pass rules give no
protection against that search.

- **(a) Keep the l.266 trial seed.** This is the decided text, unchanged,
  and the disclosed weakness remains.
- **(b) Use a beacon-protected trial seed** (recommended). Use
  `trial_seed_j = SHA256(cj({"family_seed": family_seed_f, "trial_id":
  <id>}))` for these three streams. Here `family_seed_f` is §2's
  beacon-extended seed, fixed only after the post. This closes the search
  at no compute cost.

  **Cost:** it amends decided wording in C-1, C-10 (3) and C-12 (5)
  ("from the trial seed (l.266)" becomes "from the trial's beacon-protected
  seed"). It also deletes the C-13 "Seeds" bullet. The owner must choose it
  explicitly.

The calibration is unaffected either way: its seeds are synthetic (prereg §8).

## 5. `s_inputs` enforcement (M10)

This marker names code that does not exist yet: the identity mapping that
gives `s` only its declared inputs. It belongs to the C2 evaluation build,
not to the D-19 object.

**Proposal (B5).** This marker closes **by procedure, not by a value now**:
1. That code is built and given a §16 review before the declaration.
2. Its file hash is recorded in the declaration.
3. The evaluation verifies the hash, as in §1.

Until then the marker reads "bound at the C2 evaluation build". This
decision does not authorize that build.

## 6. D-13: what the CPCV diagnostic reports (M11)

**Frozen text** (`protocol_v1.yaml` l.215–222): CPCV runs only if effective
decisions are at least 250 (with the ESS definition of C-11). It uses 8
groups, 2 of them test groups. Its role is `diagnostic_only`, and it reports
the "median and 5th-percentile path paired-delta-Sharpe; no independent
promotion gate". D-01 made `E-IMPROV` and `E-DIFF` both registered
estimands, so "paired-delta-Sharpe" is now ambiguous.

Options (matrix row D-13):
- **(a) Both estimands, separately labelled** (recommended). Report the
  median and 5th percentile over the CPCV paths for `E-IMPROV` and for
  `E-DIFF`, each named.

  It gates nothing, and nothing reads it: not a gate, the screen, the
  mapping, the DSR test or promotion. If effective decisions are below 250,
  the report says "CPCV not enabled", and it is not computed.

  This binds the least. Choosing one estimand would quietly set a precedent
  for a row that does gate.
- **(b) One estimand only.** Simpler, but it picks a winner without a
  reason.
- **(c) Report nothing.** This contradicts frozen l.221 ("Report median and
  5th-percentile ...").

CPCV needs no random stream, because its splits are combinatorial. D-13
therefore adds nothing to D-20.

## 7. Owner questions (after review)

1. **Code bindings (§1, §2).** Bind the named code to the D-19 engine commit
   recorded in the qualification object, and the family-seed bytes to the
   engine's canonical-JSON encoding.
   - Options: Adopt (recommended), or keep blocked.
2. **Null-test streams (§3).** Adopt the G-11 and G-14 stream rules
   (Python Mersenne Twister, per-draw seeds, partial Fisher–Yates), with new
   reference vectors reviewed with the screen code.
   - Options: Adopt (recommended), or use numpy Philox streams.
3. **Seed source (§4).**
   - Options: (b) beacon-protected trial seed (recommended), or (a) keep the
     l.266 trial seed.
4. **D-13 (§6).**
   - Options: (a) both estimands (recommended), (b) one, or (c) nothing.

§5 is procedural and needs no answer beyond question 1.

## Not changed by this proposal

- No frozen file, and no `HUMAN_DECISION_MATRIX.md`, is edited.
- Nothing is activated.
- The S4 draft is not yet edited. After the owner's answers, the markers are
  replaced with these texts in a separate revision.
- No calibration run, cycle, trial, data access, deployment or trading is
  authorized.
- No statistician has reviewed this.
