# D-20 lockbox bindings: proposal, revision 2 (replaces revision 1 for the owner)

**Author:** the `senior-statistical-governance` agent, Claude Opus 5.5, model ID `claude-opus-5-5` (observed in this session's own metadata). I am an AI reviewer, not an authority. I propose and check bindings. I cannot decide, accept, activate or amend anything.

**Status: INACTIVE PROPOSAL.** Nothing frozen changed. No row binds until the owner decides and signs the C2 §4 amendment. `PROPOSAL.md` (d87ab70) stays as history only.

**VERDICT: `AMENDMENT_REQUIRED`.**

**Answers:**
- `SOL_REVIEW_D87AB70.md` (gpt-6-sol, FIX, D20LR-S-1..9);
- `ASTRA_REVIEW_D87AB70.md` (gpt-6-astra, FIX, D20LR-A-1..9, recorded from `D20LR-Codex-n`).

I read both in full.

**Review status:** revision 2 is unreviewed. R19-2 requires a focused re-check by two model families before any owner decision. No human statistician has reviewed it.

**Checkout and mode:**
- Checkout: `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`.
- Files: I wrote this one file only, and **ran no git command**. Revision 1's git deviation (its §0) is not repeated.
- Access: no confirmation or lockbox data, network, credentials, keys or simulation.

**Row labels used in §1** (Astra A-5):
- **[DECIDED]**: already decided by the owner; the source is cited.
- **[DETAIL]**: a necessary implementation detail of a decided rule. Any correct implementation needs some value, and this is the simplest one.
- **[NEW DEFAULT]**: a recommended new choice. The owner adopts it through Q1 unless it has its own question.

## 0. Verification

**Basis files, all re-read this session:**
- the revision-1 basis set (`PROPOSAL.md` header);
- `deploy/calibration/runs/qualification-definition.json`, `review/d19-engine/FULL_RUN_START_EVIDENCE.md`, `deploy/calibration/FREEZE_HELDOUT.md`, `calibration/qobj.py`;
- `calibration/screen.py` l.1008-1029 and l.1499-1556;
- `src/aqt/backtest/event_contract.py` l.93-111;
- `src/aqt/metrics/descriptive.py` l.126-135 and l.223-262;
- `src/aqt/core/ledger.py` l.282 and l.369-414;
- `src/aqt/core/preregistration.py` l.257-285, l.350-394 and l.457-490;
- the S4 draft's `DRAFT_WORDING.md` l.162, l.183-197, l.228-245, and `ANNEX_C_GATE_DEFINITIONS.md` l.44-48, l.66-71, l.405-413.

**Repository facts established for R-14** (files only, no git):
1. The D-19 engine commit is fixed.
   - `qualification-definition.json` l.1 records `"engine_commit":"eeaa7282e3b7c87790c162d679016c290d5f4ea5"`.
   - The file's SHA-256 is `0f47b9e5…a7a9`, equal to the record hash committed before the run (`FULL_RUN_START_EVIDENCE.md` l.6-8; run started 2026-10-20).
2. The qualification-object freeze has not happened. `FREEZE_HELDOUT.md` l.3: "DRAFT … Not usable yet"; FP1 "open (run going)".
3. The later object files are fixed by engine code: `qobj.py` l.56-63 lists `preregistration.md`, `mapping.py`, `screen.py` and `heldout.py`. No new object file can be added under this run.

**Other code facts:**
- `walk_forward` gives the nominee's own fit seed 0 (`screen.py` l.1547).
- `max_drawdown` refuses anything that is not a `BacktestResult` (`descriptive.py` l.126-135).
- `screen.daily_returns` takes every 24th equity mark with `zip(strict=False)` (l.1010-1013). A run whose length is not a whole number of days silently loses the partial day.

**Corrections to revision 1:**
- **Source length.** The source has n = 1,247 − `gap_embargo.value_days` days, because w0 is 2022-01-01 plus the gap (Annex C l.44-48; DRAFT l.187). The figure 1,247 is the whole v1 partition (Astra A-9).

**Local evidence for the signing rows:**
- RFC 8032 is not available locally. "Ed25519 signing is deterministic and has no time input" therefore rests on the reviewers' citation (Astra report l.73, RFC 8032 §§6, 8.1-8.2), not on my reading.
- A local library README (`deploy/calibration/drand-verify/node_modules/@noble/curves/README.md` l.158-159) shows that Ed25519 verifiers differ: ZIP215 against strict RFC 8032 (D20L-17).

**Arithmetic reused from revision 1 (fractions):**
- 457 days and 10,968 hours;
- the type-7 position 1999/20, whose float64 fraction is 0.9500000000000028;
- the four distinct block lengths.

Astra reproduced the same kind of block-length separation on its own series (report l.35).

## 1a. Disposition of the review findings

**Overlaps:** A-2 = S-1; A-3 ~ S-4; A-5 ~ S-3; A-7 = S-8; A-9 (cryptography) ~ Sol's Q4 note. No finding is left unrepaired without a reason.

| ID | Disposition | Where |
|---|---|---|
| S-1 / A-2 (model seed) | **Accepted.** R-13 keeps protocol l.266 for the nominee's own fit. That seed and an explicit estimator-seed mapping are bound and stored in the nominee identity. Revision 1's "whatever `walk_forward` passes" is withdrawn. | A1b; D20L-15 |
| S-2 (artifact provenance) | **Accepted.** A canonical artifact schema, bound at sealing. Before sealing, the experiment engine recomputes the artifact from the registered source and checks the source series against the hash recorded before the look. `lockbox_eval` re-derives every derivable field. | A7; D20L-20 |
| S-3 / A-5 (w0 start, "technical" label) | **Accepted.** Rows carry the three labels. The w0 start is its own question, Q2. | labels; A2; Q2 |
| S-4 / A-3 (key custody) | **Accepted.** The key is generated and the raw public key bound before C2 is signed. The publisher reads the key bytes from the signed C2. Permissions are stated, and the loss/compromise rule is Q5. | B1; Q5 |
| S-5 (day-255 boundary) | **Accepted.** One cap instant, its anchor, strict and non-strict comparisons, and equality tests. D-12 is not reopened. | B3a; D20L-18, D20L-21 |
| S-6 (vector bytes) | **Accepted.** Exact byte serialisation is defined. | A5; B4 |
| S-7 (L-4 drawdown) | **Accepted.** L-3 and L-4 name the same kernel and the same L0 path. | A6 |
| S-8 / A-7 (R-14 overstated) | **Accepted.** The engine commit is already fixed (§0). The object-file route is real but closes at the freeze. Lockbox orchestration stays out of `screen.py`. D20L-3 is downgraded. | Q4; D20L-19 |
| S-9 (nonce under R-a) | **Accepted.** A sealed `verify_commitment` operation returns only MATCH or MISMATCH. | B4 |
| A-1 (runner/metric interface) | **Accepted.** A validated `EventResult` conversion, the drawdown kernel reused, agreement tests, and separate availability for BTC E-DIFF and ETH E-IMPROV. | A6; D20L-16 |
| A-4 (exact schemas) | **Accepted.** All bundle kinds, the null encoding, reason enums, numeric decoding and ordering, upside `k` and ties, and an atomic step 2 with a definitive-uncommitted retry rule. | B4 |
| A-6 (JSON vs source bytes) | **Accepted.** Validation branches by artifact kind. D20L-13 is corrected: the current loader does hash and compile the same bytes. | A1a |
| A-8 (seed wording) | **Accepted.** The protection is narrowed to what it actually does, "small" is removed, and the old-seed variable is specified. | §1.3; Q3 |
| A-9 (three supporting claims) | **Accepted.** n is corrected (§0). V's checker is called unnecessary, not unusable. Hand-written cryptography is removed as an option. | §0; A6; B1 |

**Revision 1's own findings:**
- D20L-1, 2, 4, 5, 6, 8, 9, 11 and 14 stand as stated.
- Corrected:
  - D20L-3 becomes NON-BLOCKING (it is superseded by D20L-19);
  - D20L-7 becomes BLOCKER, repaired by A1b;
  - D20L-10 becomes BLOCKER for signing, repaired by B3a;
  - D20L-12 is narrowed to a definitively uncommitted step 2;
  - D20L-13 is narrowed per A-6;
  - D20L-14's reason is corrected: the lockbox does not use V, so V's checker is unnecessary.

## 1. Bindings

**Shared encodings [DETAIL]:**
- `cj` is `calibration/seeds.py` l.11-19, matching `HASH_CANONICALIZATION_v1.md` l.4-9.
- Times are `YYYY-MM-DDTHH:MM:SSZ` strings in whole UTC seconds. Every comparison is on integer seconds.
- `hexf(x)` is `struct.pack(">d", x).hex()`: 16 lowercase hex digits. `unhexf` reverses it.
- Unavailable values are JSON `null`, with a reason. NaN is never written, because `cj` refuses it.
- Order between floats is always numeric, on decoded values. Lexicographic order of the hex strings is never used, because it is wrong for negative numbers.

### 1.1 D-11 items (`OWNER_DECISION_D11.md` l.26)

**A1a. Nominee artifacts: identity and verified retrieval (D11R3-S-1).**

What crosses identities, the lookup and the verification order are **[DECIDED]**: D-11 REV3 §4 items 1-3 (l.35-55), adopted at `OWNER_DECISION_D11.md` l.16. The rest is **[DETAIL]**:
- **Trial object.** The `TRIAL_FIELDS` object (`screen.py` l.302-306). The declaration's `configuration_hash` is `trial_sha256(trial)` = SHA-256(cj(trial)) (`screen.py` l.490-492).
- **Code.** The signal and overlay source files, each identified by the raw SHA-256 of its exact bytes (`signal_sha256`, `overlay_sha256`, as `load` checks at l.587-590).
- **Storage.**
  - Store: an immutable directory of hash-named files, `<sha256>.json` for trial objects and `<sha256>.py` for code, under the cycle's §26 store (Constitution l.191).
  - Fixing the set: one ledger entry, `aqt.c2.artifacts.v1` = `{items: [{kind, sha256, size}]}`, appended before the declaration post.
  - Not built: a general artifact framework (Astra note, report l.89).
- **Retrieval, branching by kind (A-6).**
  - *Trial object:* read the bytes, check SHA-256, check `cj(json.loads(b)) == b`, then `check_trial`.
  - *Source file:* read the raw bytes, check SHA-256, `check_code`, then compile those same bytes.
  - This is `screen.load`'s own hash-before-execute order (l.579-600). The only change is that the bytes come from the store instead of the import path. That is what retrieval from immutable storage needs, not a safety repair (D20L-13 corrected).
- **On any mismatch:** a pre-read rejection with no read and no retry (REV3 l.53-55).
- **Tests:**
  - a flipped byte is refused for each kind;
  - a valid Python source file is never parsed as JSON.

**A1b. The nominee's model seed (S-1, A-2).**
- **The seed is [DECIDED].** R-13 (DRAFT l.151; `OWNER_DECISION_D20_D13.md` l.91-94) keeps protocol l.266 for "the nominee's own fit": `seed_l266 = preregistration.trial_seed(protocol_hash, hypothesis_hash, trial_index)` (l.257-285). Here:
  - `protocol_hash` is the C2 protocol hash;
  - `trial_index` is the one in the nominee's C2 trial record. `record_trial` already re-derives that seed and refuses a mismatch (l.457-490).
- **The mapping to an estimator seed is [DETAIL]:** `estimator_seed = int(seed_l266, 16) % 2**31`. That is the same range as B4's `getrandbits(31)`.
- **How it is passed** reuses B4's rule (Annex C l.405-411): as `random_state` where a constructor accepts it, as `seed` to LightGBM, and to no other estimator.
- **Stored** in the nominee identity (A7): `seed_l266` and `estimator_seed`.
- **Used** identically by the confirmation fit and the lockbox refit.
- **Conflict with existing code (D20L-15).** `walk_forward` passes 0 for the nominee (`screen.py` l.1547, MR-2 l.1473-1477). The C2 code must pass `estimator_seed` instead.
- **Tests:**
  - for every allowed class, a refit with `estimator_seed` and a refit with 0 give bit-identical predictions. This is MR-2's own claim that the allowed fits are deterministic. If it holds, the screen's earlier seed-0 results stay valid;
  - the stored seed re-derives from the trial record.

**A2. Start state of the confirmation baseline run (D11-16).**
- **[DECIDED] for the lockbox:** both legs flat at L0 (`OWNER_DECISION_D11.md` l.11).
- **[NEW DEFAULT] for the confirmation source, asked plainly in Q2:**
  - both legs flat at w0: exposure 0, no pending order, an unset clock, a fresh overlay, equity 1.0;
  - each leg pays its entry cost at its first permitted entry;
  - MDD is measured from w0.
- **What it reuses.** It is EC-3 (`event_contract.py` l.44-45), which is a proposed code reading, not a decision (Sol S-3).
- **Why it matters.** D-11 Q2's justification ("matching how the confirmation runs started") holds only under this default. A different start changes d and q.

**A3. The lockbox stream identity [DETAIL].**
- `purpose = "lockbox_prediction"`, `asset = "BTCUSDT"`, `cost = "1.0"` (protocol l.80-82).
- `evaluation_window_id` is the canonical `["<w0>","<w1>"]` (D20_D13 `PROPOSAL.md` l.240-243).
- m = 457, and r = 0..1999.
- The seed is decided by Q3 (§1.3).
- C2 must add `lockbox_prediction` to `added_purposes` (DRAFT l.254; D20L-8).

**A4. The index generator for m ≠ n [DETAIL]** (unchanged from revision 1; both reviewers confirmed it).
- **Seed material.** The production layout of IMPLEMENTATION_CONVENTIONS l.84-94, with purpose `lockbox_prediction` and `output_length` 457.
- **Draws.** The `bootstrap_indices` draw order (l.535-551), run m times over the index range [0, n). n is fixed by the window id, because the source days are exactly w0 + k days (REV2 l.60).
- **Replicates.** `T*_r = sharpe(d[idx_r]).scaled`, with the Task 12 numerics.
- **Quantile.** `q = type_seven_quantile(T*, 0.05)`.
- **Code.** `ReplicateStream` is not touched.

**A5. ψ, the block length and the reference vectors [DETAIL].**
- **ψ and b.** `ψ = statistics._influence(d, sharpe(d))` and `b = block_length(ψ).value`. This is D-11 REV2 l.73 **[DECIDED]**. It is not `dsr._column_lengths` (D20L-2).
- **Matrix row.** This is option (a): migrate with refreshed vectors (matrix l.72; D20L-1).
- **Vector bytes (S-6).** Each hash is a SHA-256 over these bytes:
  - a float sequence: the concatenation of `struct.pack(">d", x)` in sequence order;
  - all index sequences: the concatenation of `struct.pack(">I", i)` for every index, sequence r = 0..1999 in order, each exactly m entries. The fixed lengths make the bytes unambiguous.
- **Frozen with the code review.** For one published synthetic d, they record:
  - ψ's hash and every `BlockLength` field (floats as hexf);
  - the first 10 indices of r = 0 and of r = 1999, and the hash of all sequences;
  - the hash of the replicates in index order;
  - q, as hexf.
- **Checked every run.** Each real computation reproduces the vectors bit for bit in-process before use (the V pattern, `V_BINDING.md` l.92-93).

**A6. Runner-to-metric interface, and the R-8 extension (A-1, S-7).**
- **Conversion [DETAIL].** The C2 runner, `run_event_contract`, returns an `EventResult`: hourly `equity` starting from 1.0 (`event_contract.py` l.93-111). Before any metric:
  - `start` must be the instant of L0 (or w0) at 00:00 UTC;
  - `len(equity) == 24·m_days` exactly (10,968 for the lockbox);
  - every value must be finite and greater than 0.

  If any check fails, the reason is `DAYS_INCOMPLETE` or `NONFINITE_EQUITY`.
- **Daily returns:** `screen.daily_returns` (l.1010-1013), for the source and the target alike (D20L-16).
- **MDD:** `descriptive._max_drawdown((1.0, *equity))`, the kernel that `max_drawdown` itself uses (l.232-241, l.260-262).
- **Not reused:** `screen.leg_stats`. It raises whenever E-IMPROV is unavailable (l.1021-1023; citation corrected by the caller).
- **Availability is separate per asset [DECIDED, REV2 l.61, l.66]:**
  - BTC L-1 and L-2 test `paired_sharpe_statistics(c, b).difference_series_sharpe.reason is None`;
  - ETH L-4 tests `paired_sharpe_improvement is not None` and the aggregate `reason is None`.
- **Drawdown uses (S-7):**
  - L-3: `MDD_BTC(cand) − MDD_BTC(bench) ≤ 0.05`;
  - L-4's DD(ETH): the same comparison on ETH (Annex C l.66-71).

  Both use the kernel above on the path from 1.0 at L0, in float64.
- **R-8 wording [DETAIL].** Replace "No lockbox clause is bound here" (DRAFT l.147). Bind, for L-1..L-4:
  - in `statistics.py`: `sharpe`, `paired_sharpe_statistics`, `_influence`, `block_length`, `_uniform_index`, `SEED_DOMAIN`, the constant `CONVENTION_DOCUMENT_SHA256` (D20L-6) and `type_seven_quantile`;
  - `_max_drawdown` in `descriptive.py`;
  - `daily_returns` in the object copy of `screen.py`;
  - the lockbox module per Q4.
- **Runtime [DETAIL].** The run uses the qualified image `sha256:54bfcf53…790c` (`qualification-definition.json` l.1, `gating.image_digest`) plus the A5 vectors. V's runtime checker is unnecessary here, because the lockbox calculation does not use method V or BLAS (A-9).
- **Agreement tests:**
  - the kernel and `max_drawdown` on the same synthetic path give equal values, bit for bit;
  - the BTC E-DIFF result stays available when ETH E-IMPROV is unavailable, and the reverse.

**A7. Prediction artifact: schema, binding time, provenance (S-2).**
- **Schema [DETAIL],** `aqt.lockbox.prediction.v1`:
  - `cycle_id`, `family`;
  - `nominee`: `{trial_id, configuration_hash, hypothesis_hash, protocol_hash, trial_index, seed_l266, estimator_seed}`;
  - `source`: `{window_id, n, d_sha256, evaluation_record_sha256}`;
  - `block`: `{psi_sha256, value, raw, clipping}`;
  - `stream`: `{seed_hex, seed_source, purpose, asset, cost, m: 457, attempts: 2000}`;
  - `replicates_sorted`: 2,000 hexf values;
  - `q`;
  - `code`: `{lockbox_module_sha256, engine_commit, screen_object_sha256}`.

  `replicates_sorted` is Python `sorted()` of the index-ordered replicates. Its SHA-256 is `artifact_sha256 = SHA256(cj(artifact))`.
- **Bound at sealing [DECIDED timing, REV3 l.89-98].** One ledger entry, `aqt.lockbox.sealing.v1`, holds each family's status (a)-(d) and, for status (a), the `artifact_sha256`. It is written before any lockbox read.
- **Provenance, part 1 [NEW DEFAULT].** The C2 evaluation record of every trial stores `d_sha256` (the A5 float bytes of the trial's BTC E-DIFF series) when the trial is evaluated, which is before the look (D20L-20). Then, before sealing, a separate engine-identity job:
  - re-runs the nominee's BTC baseline from the confirmation bars;
  - recomputes d and requires its hash to equal the pre-look `d_sha256`;
  - recomputes b, every replicate and q, and requires the whole artifact to be byte-identical.

  Any failure gives status (d), "prediction artifact UNAVAILABLE". A self-consistent artifact built from a different d, seed or code therefore cannot pass.
- **Provenance, part 2 [DETAIL].** `lockbox_eval`'s pre-read checks:
  - the artifact hash matches the sealing entry;
  - `seed_l266` and `estimator_seed` re-derive from the nominee record;
  - `seed_hex` re-derives from `family_seed_f` and `trial_id` (both public after the post);
  - `purpose`, `m` and the module hash match the signed values;
  - P-4: all 2,000 values are finite and numerically non-decreasing, and `type_seven_quantile(values, 0.05)` equals `q` bit for bit.

### 1.2 D-12 groups (P-1..P-8 [DECIDED], `OWNER_DECISION_D12.md` l.22-26; D-20 items l.29)

**B1. Signing and key custody (S-4, A-3, A-9).**
- **[DECIDED]** The signer is the `lockbox_eval` identity (THREAT_MODEL l.9). The publisher is a separate job that never reads lockbox data (Q6(i), `OWNER_DECISION_D12.md` l.17).
- **Scheme [NEW DEFAULT]:**
  - Ed25519 (PureEdDSA, RFC 8032), through the maintained `cryptography` library;
  - hash-pinned in one small signer-and-publisher environment, not in the calibration image;
  - hand-written Ed25519 is dropped (A-9; RFC 8032 calls its Python code illustrative).
- **Message [DETAIL].**
  - Fields: the 12 fields `attestation.schema.json` l.4-17 requires, plus `family`, `nominee_trial_id`, `prediction_artifact_sha256` and the three coarse fields.
  - `lockbox_evaluation_id` is the evaluation ID.
  - Signed bytes: cj of the object without `signature` (`HASH_CANONICALIZATION_v1.md` l.6).
  - Signature: 128 hex characters.
- **Key lifecycle [NEW DEFAULT]:**
  1. Before the owner signs C2, the signer host generates the key pair with the library, from the OS random source.
  2. The **raw 32-byte public key, as 64 hex characters**, is written into the signed C2's signing values (DRAFT l.340), so it is bound by the protocol hash.
  3. The private key file is readable only by the signer's service account. It is never copied, backed up, logged or put in the repository (Constitution l.198-199).
- **Verification [DETAIL].** The publisher reads the public-key bytes from the signed C2 protocol file, never from the signer. It verifies every attestation with the same pinned library and version as the signer, then applies P-8 (D20L-17).
- **Permissions [DETAIL]:**
  - **Signer:** reads its evaluation's sealed bundle and the store clock; returns a signature to the publisher; writes nothing to the index.
  - **Publisher:** appends pre-read and release entries; reads state, the index and commitments; has no access to the sealed store or any lockbox bytes.
  - **Store:** append-only, with its own clock.
- **Guard and effectiveness:** P-7 l.90 and l.93, with the boundary in B3a.
- **Loss or compromise:** Q5.
- **Tests:**
  - RFC 8032 §7.1 vectors, cited from the RFC at build time;
  - signing twice gives identical bytes;
  - each guard refusal;
  - an attestation signed by a different key is refused.

**B2. Contracts. [DECIDED: P-1..P-4]; encodings [DETAIL].**
- **Sign field.** It is computed from `T_L` (the BTC `difference_series_sharpe.scaled`) in float64: `positive` if `T_L > 0.0`, `zero` if `T_L == 0.0` (including −0.0), `negative` otherwise. A null `T_L` is a technical FAIL.
- **P-3 lineage.** Fixed at sealing, through the transitive `parent_id` chain of the hypothesis records.
- **Upside [DETAIL; the 0.95 point is D-12's AI default]:**
  - computed only for a finite `T_L`;
  - `k` = the number of replicates strictly below `T_L`, so ties are not counted;
  - `exceeds_p95` = `T_L > type_seven_quantile(values, 0.95)`;
  - otherwise `{status: NOT_COMPUTED, k: null, exceeds_p95: null, reason: "T_L_UNAVAILABLE"}`.

**B3. Order [DECIDED: steps 1-5, P-7, P-8]; values [DETAIL].**
- `t_s` is the store-clock second at which the step-2 entry commits.
- `R_0 = t_s + 7 d` and `R_j = R_0 + j d`.
- `D_w = R_0 − 12 h`. A worker's "finished" mark is accepted only if the store clock is earlier than `D_w`.
- The publisher's window is `[R_j − 6 h, R_j)`.
- The R-b items do not apply.

**B3a. The day-255 boundary (S-5).**
- **Anchor A [NEW DEFAULT; D20L-18].** A is the archive timestamp T of the C2 declaration capture, which already fixes the drand round (DRAFT l.162). It is public, fixed by procedure, and cannot be chosen by the declarer.
- **Cap C [DETAIL].** `C = A + 255 × 86,400 s`. D-12's choice ("decided by day 255") is kept. Until the S4 draft resolves D11-15, C is the earlier of that and `look + 75 d`, the safe reading that satisfies both texts (D11R3-A-2). D11-15 itself stays with S4.

**Comparisons [DETAIL].** "Processing ends at C" means an action is valid only if its time is earlier than C (`t < C`).

| Event | Valid iff |
|---|---|
| Signing for `R_j` | `R_j < C` |
| Insert | store clock `< R_j` |
| Row visible | `t ≥ visible_from` |
| Cooling-off ends | at the first second `E` with 72 available hours in `[R_j, E)` (P-5) |
| Owner decision accepted | `E ≤ t_dec < C` |

- **Consequence (D20L-21):** a PASS released with `R_j > C − 72 h` can never be promoted. It expires `U_ops` under P-6. D-12 allows that; it is disclosed, not reopened.
- **Equality tests,** one pair for each comparison: at the boundary second and at one second before it (`R_j = C` and `C − 1`; insert at `R_j` and `R_j − 1`; read at `visible_from` and one second before; decision at `E − 1`, `E`, `C − 1` and `C`).

**B4. Records (A-4, S-9). [DETAIL] unless marked.**
- **Step 2 is atomic.** It happens in this order:
  1. the store creates a 32-byte nonce (`secrets.token_bytes`) and the default bundle, and keeps both in the sealed store under `(evaluation_id, attempt)`;
  2. the publisher appends **one** ledger entry, `aqt.lockbox.pre_read.v1` = `{evaluation_id, family, nominee_trial_id, prediction_artifact_sha256, eligibility_result_id, lockbox_evaluation_id, budget_before: 1, budget_after: 0, segment_status: "EXPOSED", t_s, r0, d_w, default_commitment}`.

  The ledger writes and fsyncs one line under a lock (`ledger.py` l.412-414). The budget, the EXPOSED status and the commitment therefore become true together in that one line. An orphan bundle from an attempt that never committed binds nothing.
- **Retry [NEW DEFAULT, narrowed].** Retry is allowed only if the step-2 attempt is definitively uncommitted. That means `verify_ledger` (l.282) reports an intact chain with no entry for this `evaluation_id`. An ambiguous acknowledgement is first reconciled against that ID. A damaged chain stops the process, as a §26 incident, until a human reconciles it.
- `evaluation_id` = `"<cycle_id>/<family>/1"`.
- **Sealed bundle,** `aqt.lockbox.sealed_bundle.v1`:
  - `evaluation_id`, `kind` (`RESULT` or `DEFAULT`), `result` (`PASS` or `FAIL`), `cause_class` (`PERFORMANCE`, `TECHNICAL` or `DEADLINE`);
  - `values` (hexf or null): `t_l`, `q`, `mdd_btc_cand`, `mdd_btc_bench`, `eth_e_improv`, `mdd_eth_cand`, `mdd_eth_bench`;
  - `conditions` (each true, false or null): `L1`..`L4`;
  - `reasons`: a sorted, unique list;
  - `upside`, as B2;
  - `times`: `{read_start, finished | null}`;
  - `capture`: `{input_manifest_sha256, lockbox_module_sha256, engine_commit, image_digest, prediction_artifact_sha256, seed_l266, estimator_seed, block, m}`.
- **Result rules:**
  - PASS iff all four conditions are true;
  - PERFORMANCE iff all four are non-null and one is false;
  - TECHNICAL iff any is null.
- **Default bundle:** `kind DEFAULT`, `FAIL`, `DEADLINE`, every value null except `q`, conditions null, `reasons ["DEADLINE:NOT_FINISHED_BY_D_W"]`, upside `NOT_COMPUTED`, and `finished` null.
- **Reason enum:** `<scope>:<code>`, where:
  - scope ∈ {`BTC_EDIFF`, `BTC_MDD`, `ETH_EIMPROV`, `ETH_MDD`, `RUN`, `DEADLINE`};
  - code ∈ {`INSUFFICIENT_OBSERVATIONS`, `ZERO_VARIANCE`, `NONFINITE_RESULT`, `NONPOSITIVE_LONG_RUN_VARIANCE`, `DAYS_INCOMPLETE`, `NONFINITE_EQUITY`, `RUN_FAILED`, `NOT_FINISHED_BY_D_W`}.
- **Pre-read reason codes (Q2b):** `ARTIFACT_NOT_FOUND`, `ARTIFACT_HASH_MISMATCH`, `IDENTITY_MISMATCH`, `PREDICTION_ARTIFACT_INVALID`, `REFERENCE_VECTOR_MISMATCH`, `IMAGE_MISMATCH`, `BUDGET_EXHAUSTED`, `COOLDOWN_NOT_ELAPSED`.
- **Release entry,** `aqt.lockbox.release.v1`: `{evaluation_id, result, visible_from, commitment, attestation | null, attestation_ref | null}`. `attestation_ref` is SHA-256(cj(attestation)).
- **Commitment:** `SHA256(nonce ‖ cj(bundle))`.
- **Later verification under R-a (S-9).** The store offers one operation, `verify_commitment(evaluation_id, bundle_bytes)`, which returns only `MATCH` or `MISMATCH`. The R-a re-run job calls it after the segment has become confirmation data. The nonce never leaves the store.

**B5. Tests.**
- **[DECIDED]** T-1..T-8 (REV7 l.140-147), run against a synthetic store with an injectable clock.
- **[DETAIL]**
  - the B3a equality tests and the A1-A7 tests;
  - byte-exact bundles for each kind;
  - the retry reconciliation cases (committed, uncommitted, damaged).

**B6. Review [DECIDED].** Constitution l.147-153 requires a different-model plus human PR review before merge for:
- the lockbox ACL tooling (store, publisher, signer, `lockbox_eval`);
- the promotion gate.

D-20's authority is `§16` + `STAT` (matrix l.72).

### 1.3 The lockbox seed (Q3)

**Recommended:** `seed_hex = trial_seed_j = SHA256(cj({"family_seed": family_seed_f, "trial_id": <nominee trial_id>}))`, the R-13 seed, with purpose `lockbox_prediction`.

**What it does, narrowed (A-8).** It prevents choosing the realised lockbox bootstrap seed through cosmetic edits made before the declaration post. That holds under the existing commitment and beacon assumptions: the O-6a channel, drand and the archive capture, plus the owner's SHA-256 modelling assumption (`OWNER_DECISION_D20_D13.md` l.92-93).

**What it does not do:**
- It does not stop a search over the strategy or the nominee's model seed.
- It does not stop outcome-dependent invalidation and re-declaration. Each retry costs one m, and no probability bound across such retries is asserted (D20_D13 `PROPOSAL.md` l.455-474).
- It does not hide q after the post, because prices are public (D20L-5).
- No bound shows that bootstrap noise near the pass boundary is negligible.

**Alternative:** `seed_hex = seed_l266` of the nominee (A1b). Then streams separate only by purpose, and the seed can be computed before the post.

**Anti-probing:** neither option reads lockbox bytes, uses budget or bypasses eligibility. So there is no conflict with Constitution l.77, l.85, protocol l.74-76, l.296 or THREAT_MODEL l.17. A second beacon is unnecessary.

**Cost:** one C2 row adding the lockbox prediction stream to R-13 (D20L-4).

## 2. Findings

**Revision 1's findings D20L-1..14.** Their text stands except as §1a corrects:
- D20L-3 is NON-BLOCKING;
- D20L-7 is a BLOCKER, repaired;
- D20L-10 is a BLOCKER, repaired;
- D20L-12, 13 and 14 are narrowed.

**New findings:**
- **D20L-15 BLOCKER (for building; repaired in the binding).** `walk_forward` hard-codes the nominee's seed as 0 (`screen.py` l.1547). R-13 keeps l.266.
  - So the C2 confirmation fit and the lockbox refit need a seed parameter. That means either a `screen.py` change before the freeze, or a fit path in the lockbox and C2 code.
  - A1b's determinism test decides whether the screen's earlier seed-0 results are affected.
- **D20L-16 NON-BLOCKING.** D-11 REV2 l.49 names `daily_net_returns` and `paired_daily_returns`, which need a `BacktestResult`. The C2 runner yields an `EventResult`.
  - The binding uses `screen.daily_returns` for source and target alike, with length validation. The decided meaning (daily net returns over complete UTC days) is kept.
- **D20L-17 NON-BLOCKING.** Ed25519 verifiers differ: ZIP215 against strict RFC 8032 (local evidence, noble-curves README l.158-159).
  - The signer and the publisher must use one pinned library and version, with tests. Otherwise one verifier can accept a signature that another refuses.
- **D20L-18 QUESTION (S4).** No text binds day 0. Only REV3 l.103 assumes it.
  - B3a recommends A = T. The S4 draft should use the same anchor for day 180, or the calendar becomes inconsistent.
- **D20L-19 NON-BLOCKING (supersedes D20L-3).** Facts from §0:
  - the engine commit is fixed at `eeaa728`;
  - the freeze is still open;
  - the object-file list is fixed by engine code.

  So placing code in the engine commit is no longer possible. `screen.py` is possible only before the freeze. The lockbox service needs a narrow R-14 exception under every route.
- **D20L-20 NON-BLOCKING.** Provenance needs `d_sha256` in every C2 evaluation record, written before the look. That is a field for the C2 evaluation-record build.
- **D20L-21 NON-BLOCKING (disclosure).** A PASS released after `C − 72 h` cannot lead to promotion (B3a). This is D-12's chosen consequence, now made explicit and tested.

## 3. Owner questions (each has "Keep blocked")

**Q1. Adopt the detail rows and the new defaults?** Row by row:
- **[DETAIL]:** A1a, A1b's mapping, A3, A4, A5, A6, A7's schema and checks, B2, B3, B3a's comparisons, B4, B5.
- **[NEW DEFAULT]:** A7's pre-sealing recomputation; Ed25519 through the maintained library; key generation before C2; B3a's anchor A = T; B4's narrowed retry.

This does not make every row ready to build; D20L-15 and D20L-18 must still be settled.
- **"Adopt (Recommended)."** Cost: several builds, each needing its own §16 review.
- **"Keep blocked."** The lockbox cannot run, so C2 cannot promote anything.

**Q2. How should the confirmation runs that the lockbox forecast is built from begin?**
- **"Both strategy and benchmark start with no position on the first day, each paying its entry cost (Recommended)."** This matches the lockbox's own start, as decided. Cost: the first day carries an entry cost for both.
- **"Carry positions over from the warm-up period."** Cost: the forecast and the lockbox no longer start the same way, and D-11's stated reason for the lockbox start no longer holds.
- **"Keep blocked."**

**Q3. Which seed drives the lockbox forecast's random draws?**
- **"The post-protected seed, as for G-1 (Recommended)."** Cosmetic edits made before the public post cannot pick it. Cost: one more C2 row.
- **"The old protocol seed (l.266)."** No wording change. Cost: the seed is known before the post, so cosmetic edits can be tried offline for free. This must be disclosed.
- **"Keep blocked."**

**Q4. Where does the lockbox code live?** The engine commit is already fixed, so the lockbox service needs an exception to rule R-14 either way.
- **"One separate reviewed lockbox module, its hash written into the signed C2, with a narrow R-14 exception (Recommended)."** The freeze is not delayed. Cost: one amendment row, and the module must be built and reviewed before you sign C2.
- **"The forecast code inside `screen.py` before the freeze; only the lockbox service under the exception."** Cost: the freeze waits for that build and review, and the exception is still needed.
- **"Keep blocked."**

**Q5. What happens if the signing key is lost or stolen during C2?**
- **"No replacement during the cycle (Recommended)."**
  - *Lost key:* certificates already in force stay valid. Any PASS not yet certified cannot be certified and expires `U_ops`.
  - *Stolen key, or suspected theft:* it is a §26 incident. Every certificate without your recorded approval becomes void. Approvals recorded before the incident stand, after an incident review.
  - Cost: one lost key can cost a good PASS this cycle.
- **"Allow a replacement key, through your signed incident record."** Cost: new machinery mid-cycle, a new review, and a path by which a key could be swapped.
- **"Keep blocked."**

## 4. What changed in revision 2, and what remains

**Changed:**
- the three row labels;
- the model seed bound to l.266, with a mapping;
- artifact provenance;
- the separate w0 question;
- key custody and the loss question;
- the exact cap instant and comparisons;
- the runner-to-metric bridge;
- exact schemas and an atomic step 2;
- the R-14 facts;
- the narrowed seed claims;
- n corrected;
- the hand-written cryptography option removed.

Nothing in D-11, D-12 or D20_D13 was reopened.

**Remaining:**
- the R19-2 re-check of this revision;
- owner Q1-Q5;
- C2 rows for R-8, R-13 (Q3), R-14 (Q4), `added_purposes`, the public key and the anchor (S4, D20L-18);
- D11-15 in S4;
- builds, each a later authorised task with §16 review: the artifact store, the C2 runner and evaluation records, the lockbox module and its vectors, the signer, the publisher and the store, and the tests.

**Unauthorised:**
- frozen edits, activation and acceptance;
- any code;
- key generation;
- simulation;
- confirmation or lockbox access;
- promotion, deployment and trading.

`KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.
