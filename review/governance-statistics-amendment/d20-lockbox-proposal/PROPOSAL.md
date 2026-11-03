# D-20 lockbox bindings: proposal, revision 1

**Author:** the `senior-statistical-governance` agent, Claude Opus 5.5, model ID `claude-opus-5-5` (observed in this session's own metadata). I am an AI reviewer, not an authority. I propose and check bindings. I cannot decide, accept, activate or amend anything.
**Status: INACTIVE PROPOSAL.** Nothing frozen was changed. No row binds until the owner decides and signs the C2 §4 amendment.
**VERDICT: `AMENDMENT_REQUIRED`.** Most rows are technical binding candidates. The seed row (Q2), the code-location row (Q3) and the C2 rows in §4 need owner choices and amendment wording.
**Review status:** unreviewed. R19-2 requires two AI reviews from different model families before any owner decision. No human statistician has reviewed it.
**Checkout and mode:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch freeze-sheet. I wrote one file, this one. No confirmation or lockbox data, network, credentials or simulation were used.

**Basis files (all in this checkout).** I give file names only, without commits, because the caller did not allow git.
- `review/governance-statistics-amendment/`:
  - `d11-proposal/`: `OWNER_DECISION_D11.md`, `PROPOSAL_REV2.md`, `PROPOSAL_REV3.md`, `SOL_REREVIEW2_6CE228C.md`;
  - `d12-proposal/`: `OWNER_DECISION_D12.md`, `PROPOSAL_REV7.md`;
  - `d20-d13-proposal/`: `OWNER_DECISION_D20_D13.md`, `PROPOSAL.md` (rev 6);
  - `d20-proposal/`: `OWNER_DECISION_D20_V.md`, `V_BINDING.md`;
  - `v1.1-method-candidate/HUMAN_DECISION_MATRIX.md`;
  - `s4-amendment-draft/`: `DRAFT_WORDING.md`, `ANNEX_B_DSR_METHOD.md`, `ANNEX_C_GATE_DEFINITIONS.md`.
- Frozen texts: `docs/RESEARCH_CONSTITUTION.md`, `docs/THREAT_MODEL_v1.md`, `protocols/protocol_v1.yaml`, `schemas/attestation.schema.json`, `schemas/HASH_CANONICALIZATION_v1.md`.
- Conventions: `review/task12/IMPLEMENTATION_CONVENTIONS.md`.
- Code:
  - `src/aqt/metrics/statistics.py`, `src/aqt/metrics/descriptive.py`, `src/aqt/backtest/event_contract.py`;
  - `src/aqt/core/preregistration.py`, `src/aqt/core/ledger.py`;
  - `calibration/dsr.py`, `calibration/seeds.py`, `calibration/screen.py`, `calibration/qobj.py`;
  - `deploy/calibration/requirements.lock`, `.gitattributes`.

## 0. Verification

**Citations.** I re-read every file:line cited below in this session.

**Topic search, in both directions:**
- A search for seed rules found the nominee model-seed conflict (D20L-7): R-13 against screen.py MR-2.
- A search for code-loading rules found R-14 (D20L-3). D-11 and D-12 did not cite it, and it decides where the lockbox code may live.

**Exact arithmetic (`fractions`, `datetime`), run this session:**

| Check | Result |
|---|---|
| Lockbox length, `[2025-06-01, 2026-09-01)` | 457 days, 10,968 hours |
| Confirmation source `[2022-01-01, 2025-06-01)` | n = 1,247 days |
| `S_pre` | 2022-11-13 |
| Last refit `r_15` | 2026-08-25; `r_16` would fall on or after L1 |
| Type-7 position, p = 1/20, B = 2,000 | exactly 1999/20, so j = 99 with fraction 19/20 |
| Same, in float64 | fraction 0.9500000000000028, not 19/20 (D20L-11) |
| Type-7 at p = 19/20 | exact fraction 1/20; float64 0.049999999999954525 |

**Discriminating checks, using repository code on synthetic series only:**
- **Generator.** The proposed lockbox generator (§1, A4), given purpose `paired_sharpe_ci` and m = n, reproduces `bootstrap_indices` exactly. The alternative material layout `[…, n, m, r]` does not. With purpose `lockbox_prediction` and m = 457 it returns 457 indices, all below n. Its stream also depends on m: the m = 457 draws are not a prefix of the m = n draws.
- **Block length.** On one synthetic series, four conventions give four different values of b:

| Convention | b |
|---|---|
| ψ(d), population scale (the D-11 binding) | 7.702771461455618 |
| `dsr._column_lengths(d)` (sample scale) | 7.702712614045081 |
| Task 12 E-IMPROV influence | 6.311079424990612 |
| Raw d | 7.648723008544073 |

- **File bytes.** `IMPLEMENTATION_CONVENTIONS.md` here has 107 CRLF line endings out of 107 lines. Its raw SHA-256 is `d6d9de50…139a`. Its LF form hashes to the code constant `f3ba9362…515c` (D20L-6).

**Not checked:**
- the index blobs, because git was not allowed;
- whether the D-19 full run has started (this matters for Q3);
- Ed25519 behaviour. "RFC 8032 Ed25519 is deterministic and carries no time" is an `UNVERIFIED_EXTERNAL_ASSUMPTION` here, checked from memory only.

**Tooling notes:**
- Git Bash `grep -c $'\r'` reported 0 CRs on that CRLF file. Python byte counts are the evidence used.
- **Process deviation, disclosed:** at the start I ran `git log -1` and `git status --short`, both read-only, before applying the caller's "no git commands" rule. I ran no other git command.

## 1. Bindings, one row per item

Every row is proposed C2 wording. **TECHNICAL** means the owner has no real choice and only adopts the row. **CHOICE** means an owner question in §3 decides it.

**Shared definitions:**
- `cj` is canonical JSON as in `calibration/seeds.py` l.11-19, matching `HASH_CANONICALIZATION_v1.md` l.4-9.
- Times are UTC strings `YYYY-MM-DDTHH:MM:SSZ` in whole seconds.
- Every float that must be stored exactly is the 16-hex-digit big-endian IEEE-754 binary64 encoding.
- Ledger entries hold no floats (`ledger.py` l.11-13).

### 1.1 D-11 items (`OWNER_DECISION_D11.md` l.26)

**A1. (i) Nominee artifact identity and verified retrieval (D11R3-S-1). TECHNICAL.**

What has to be stored, and where:

| Object | Identity | Source of the rule |
|---|---|---|
| The nominee's trial object, which has the `TRIAL_FIELDS` of `screen.py` l.302-306 | `configuration_hash := screen.trial_sha256(trial)` = SHA-256(cj(trial)) | `screen.py` l.490-492 |
| Its signal and overlay source code | `signal_sha256` and `overlay_sha256`, the raw SHA-256 of the exact bytes | `screen.py` l.587-590 |
| The hypothesis | `hypothesis_hash`, as `record_hypothesis` stores it | `preregistration.py` l.437-454 |
| The model seed | the value the bound `walk_forward` passes: 0 under MR-2 | `screen.py` l.1473-1477, l.1547; see D20L-7 |

The Annex B declaration lists each trial as `{trial_id, hypothesis_hash, configuration_hash}` (Annex B l.97-102).

- **Storage.** Before the declaration post, every trial object (as its cj bytes) and every code file (its exact declared bytes) is written into a content-addressed store. Each item is filed under its own SHA-256 and listed in one §26 ledger entry, `aqt.c2.artifact.v1` = `{kind, sha256, size}` (Constitution l.191).
- **Retrieval.** `lockbox_eval` fetches each item by its hash and recomputes SHA-256 over the bytes it actually read. It then checks that `cj(json.loads(bytes)) == bytes`, and runs `check_trial` and `check_code`. It loads the code from those bytes, never from a checkout. Any mismatch is a pre-read rejection (`ARTIFACT_HASH_MISMATCH`, see B4), with no read and no retry (D-11 REV3 l.53-55).
- **Reuses:** the `ledger.append_entry` chain; `check_trial`, `check_code` and `trial_sha256` from screen.py.
- **To build:**
  - the artifact store and its writer;
  - a byte-based variant of `screen.load`, because `load` reads the file from its import path (l.587-588), see D20L-13.
- **Tests:**
  - a byte flip in any artifact is refused before any read;
  - a CRLF copy of LF source is refused.

**A2. (ii) Start state of the confirmation baseline run (D11-16). TECHNICAL.**
- **Binding.** Both confirmation legs start flat at w0: exposure 0, no pending order, an unset clock, a fresh overlay and equity 1.0. MDD is measured from w0. This is EC-3 (`event_contract.py` l.44-45).
- **Why it is technical.** D-11 Q2 adopted "both legs flat at L0" (`OWNER_DECISION_D11.md` l.11). Its justification holds only if the source run starts the same way (D11R3-A-5, `SOL_REREVIEW2_6CE228C.md` l.21; REV3 l.140).
- **Reuses:** `run_event_contract`.
- **To build:** the C2 baseline runner, which is a later task.
- **Test:** the initial state is asserted for both legs.

**A3. (iii) Lockbox seed source and stream identity.** The seed is a CHOICE (Q2). The identity is TECHNICAL.
- **Stream identity:**
  - `purpose = "lockbox_prediction"`, `asset = "BTCUSDT"`, `cost = "1.0"` (protocol l.80-82);
  - `evaluation_window_id` is the source window id, formatted as in D20_D13 `PROPOSAL.md` l.240-243;
  - output length m = 457, replicates r = 0..1999.
- **Seed (recommended):** `trial_seed_j = SHA256(cj({"family_seed": family_seed_f, "trial_id": <nominee trial_id>}))`. This is exactly R-13's beacon-protected seed (DRAFT l.151). See §1.3.
- **C2 wording:** add `lockbox_prediction` to `added_purposes` (DRAFT l.254; D20L-8).

**A4. (iv) The index generator for m ≠ n. TECHNICAL.**
- **Seed material.** The exact production layout (IMPLEMENTATION_CONVENTIONS l.84-94; `statistics.py` l.500-515), with only the purpose and length changed:
  - material = `json.dumps([SEED_DOMAIN, trial_seed_j, CONVENTION_DOCUMENT_SHA256, "lockbox_prediction", "BTCUSDT", "1.0", evaluation_window_id, 457, r], ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")`;
  - n is fixed by the window id, because the source days are exactly w0 + k days (D-11 REV2 l.60).
- **Draws.** The generator is `random.Random(int.from_bytes(sha256(material).digest(), "big"))`. Draw the first index with `_uniform_index(gen, n)`. Then for each of the other 456 positions: if `gen.random() < 1/b`, draw a new `_uniform_index(gen, n)`; otherwise take `(previous + 1) % n`. This is the `bootstrap_indices` algorithm (l.535-551) with the loop length set to m.
- **Replicates.** `T*_r = sharpe([d[i] for i in idx_r]).scaled`, with the Task 12 numerics (l.173-205). Method V (DSR only) is not used.
- **Quantile.** `q = type_seven_quantile(T*, 0.05)` (l.554-566).
- **Precedent.** The new code is built inline, as `dsr._replicate_seed` was (dsr.py l.57-65). `ReplicateStream` stays unchanged: it refuses any other purpose (l.465). This keeps the engine-bound file unchanged.
- **Tests:**
  - with purpose `paired_sharpe_ci` and m = n, the generator equals `bootstrap_indices` (shown in §0);
  - it returns exactly m indices, all in [0, n).

**A5. (v) ψ and the reference vectors. TECHNICAL.**
- **ψ.** `ψ = statistics._influence(d, sharpe(d))` (l.311-322): population scale and the sample daily Sharpe (D-11 REV2 l.73; IMPLEMENTATION_CONVENTIONS l.44-51).
- **Block length.** `b = block_length(ψ).value` (l.368-438). Availability follows D-11 REV2 l.59-66.
- **Not the DSR helper.** The code must not reuse `dsr._column_lengths`, which uses the sample scale and max(L(u), L(ψ)) (D20L-2).
- **Matrix row.** This is option (a), "migrate with refreshed vectors" (matrix l.72), not (b) (D20L-1).
- **Vectors.** Frozen with the code review, following the B3/B4 precedent (D20_D13 `PROPOSAL.md` l.331-338). For one fixed synthetic d of length ≥ 16 and one fixed seed, they record:
  - the SHA-256 of ψ, as hex floats;
  - every `BlockLength` field;
  - the first 10 indices of r = 0 and of r = 1999, and the SHA-256 of all 2,000 sequences;
  - the SHA-256 of the sorted T*;
  - q, as hex.
- **Discriminating tests:** b(ψ) differs from both the DSR helper and the E-IMPROV influence.
- **Every real lockbox computation** first reproduces the vectors bit for bit in the same process (the V pattern, `V_BINDING.md` l.92-93). Failure is a pre-read rejection, `REFERENCE_VECTOR_MISMATCH`.

**A6. (vi) R-8 extension, including `max_drawdown`.** The wording is TECHNICAL. The code location is a CHOICE (Q3).
- **The new R-8 text** replaces "No lockbox clause is bound here; those stay with D-11" (DRAFT l.147). It binds, for L-1..L-4:
  - in `statistics.py`: `sharpe`, `paired_sharpe_statistics`, `_influence`, `block_length`, `_uniform_index`, `SEED_DOMAIN`, `CONVENTION_DOCUMENT_SHA256` (a literal domain field only, D20L-6) and `type_seven_quantile`;
  - `max_drawdown` in `descriptive.py` (l.260-262) for L-3;
  - and the lockbox module per Q3.
- **L-3 is computed as** `max_drawdown(cand) − max_drawdown(bench) ≤ 0.05` in float64, on the hourly equity path from 1.0 at L0 (`descriptive.py` l.223-241).
- **Runtime.** Lockbox computation runs in the qualified image, checked by digest. Its streams depend on interpreter stability (D20_D13 `PROPOSAL.md` l.256-261), and the A5 vectors check that.
- **Not reused:** `dsr.v_runtime_check`. Its canaries are bound to one machine (dsr.py l.297-299; D20L-14).

### 1.2 D-12 groups (`OWNER_DECISION_D12.md` l.29; `PROPOSAL_REV7.md` §5 l.132-149)

**B1. Signing.** The scheme is a CHOICE (Q4). The rest is TECHNICAL.
- **Writer.** The signer process runs under the `lockbox_eval` identity, which THREAT_MODEL l.9 already allows to sign. It runs in its own small environment, not the calibration image.
- **Key:**
  - one Ed25519 key pair, generated on the signer host before the declaration post;
  - SHA-256 of the 32-byte raw public key is recorded in the cycle record and in the signed C2 signing values (DRAFT l.340);
  - the private key never leaves the host or enters the repository, logs or prompts (Constitution §28).
- **Message.** The attestation object, which holds:
  - the 12 fields `attestation.schema.json` l.4-17 requires;
  - `family`, `nominee_trial_id`, `prediction_artifact_sha256`;
  - `paired_delta_sharpe_sign`, `prediction_decay_test_passed`, `drawdown_constraint_held`.

  `lockbox_evaluation_id` is the evaluation ID; it is the "lockbox ID" of P-8. The signed bytes are cj of the object without `signature` (`HASH_CANONICALIZATION_v1.md` l.6). `signature` is 128 lowercase hex characters (PureEdDSA, RFC 8032).
- **Release-time guard (P-7, l.90).** The signer refuses unless all of these hold:
  - the read is finished as PASS;
  - P-2 holds against the sealed bundle;
  - the store clock is before `R_j`;
  - `R_j` is at or before the day-255 instant (D20L-10);
  - no release entry exists for the evaluation.
- **Effectiveness (l.93).** A certificate is effective only if a committed release entry with `visible_from == cooling_off_start` references SHA-256(cj(attestation)).
- **Tests:**
  - the RFC 8032 §7.1 vectors;
  - signing the same object twice gives identical bytes;
  - each refusal condition has its own test.

**B2. Contracts. TECHNICAL.**
- **P-1 and P-2** as written (l.69, l.71).
- **Sign function.** It reads `T_L = paired_sharpe_statistics(c, b).difference_series_sharpe.scaled` in float64. The result is `positive` if `T_L > 0.0`, `zero` if `T_L == 0.0` (including −0.0), and `negative` if `T_L < 0.0`. A non-finite or missing `T_L` is a technical FAIL and never a field value (l.65).
- **P-3 lineage.** Fixed at sealing. Nominee B descends from A if A's `hypothesis_id` is in B's transitive `parent_id` chain in the ledger (hypothesis schema `parent_id`; Constitution l.97).
- **P-4.** The sealed artifact holds exactly 2,000 finite, ascending hex floats, and `type_seven_quantile(v, 0.05)` must equal the sealed q bit for bit, using the same float literal (D20L-11). The upside value uses p = 0.95 on the same vector.

**B3. Order. TECHNICAL.**
- The order is steps 1-5 and P-7 and P-8 as written (l.79-102), with these values:
  - `t_s` is the store-clock time of the committed step-2 entry;
  - `R_0 = t_s + 7 days`, `R_j = R_0 + j days`;
  - `D_w = R_0 − 12 h`;
  - the publisher's window is `[R_j − 6 h, R_j)`.
- **Step 2 is one atomic store write.** If it does not commit, no evaluation exists and no budget is spent. It may then be retried, with an incident logged (D20L-12).
- Under Q4 route R-a, the R-b items are dropped (`OWNER_DECISION_D12.md` l.15).

**B4. Records. TECHNICAL.**
- **Pre-read entry,** `aqt.lockbox.pre_read.v1`:
  - `evaluation_id = "<cycle_id>/<family>/1"` (one read per family, DRAFT l.221-223);
  - `family`, `nominee_trial_id`, `prediction_artifact_sha256`, `eligibility_result_id`, `lockbox_evaluation_id`;
  - `r0`, `d_w`, `status: "EXPOSED"`, `default_commitment`.
- **Release entry,** `aqt.lockbox.release.v1`: `evaluation_id`, `result` (PASS or FAIL), `visible_from`, `commitment`, and `attestation_ref` (a hex string on PASS, `null` on every FAIL).
- **Sealed bundle** (`lockbox_eval` only), as cj with hex floats. It holds:
  - `T_L`, q, both BTC MDDs, ETH E-IMPROV and the ETH drawdown flag;
  - L-1..L-4, each `true`, `false` or `"UNAVAILABLE"`;
  - the reasons, and `cause_class` (PERFORMANCE, TECHNICAL or DEADLINE);
  - the times and the upside record;
  - the captures: input hashes, code hashes, image digest, `trial_seed_j`, b and m.
- **Commitment:** `SHA256(nonce ‖ cj(bundle))`, where `nonce` is 32 bytes from `secrets.token_bytes` that the store holds and never releases. The fixed-length prefix makes the concatenation unambiguous.
- **Pre-read reason codes (Q2b):** `ARTIFACT_NOT_FOUND`, `ARTIFACT_HASH_MISMATCH`, `IDENTITY_MISMATCH`, `PREDICTION_ARTIFACT_INVALID`, `REFERENCE_VECTOR_MISMATCH`, `IMAGE_MISMATCH`, `BUDGET_EXHAUSTED`, `COOLDOWN_NOT_ELAPSED`.
- **Separate record:** `BARRED_DESCENDANT` (P-3).
- **Reuses:** `ledger.append_entry` for the chain.
- **To build:**
  - the time-checking store: it refuses inserts at or after `R_j` and filters on `visible_from`;
  - the publisher.

**B5. Timing tests. TECHNICAL.** T-1..T-8 as written (l.140-147). They run against a synthetic store with an injectable store clock, and each states its fault model. In addition:
- the A4 and A5 vectors;
- the sign function at ±0.0;
- the B1 vectors.

**B6. Review. TECHNICAL.** Constitution l.147-153 requires a different-model plus human PR review before merge for:
- the lockbox ACL tooling (store, publisher, signer, `lockbox_eval`);
- the promotion gate.

D-20's own authority is `§16` + `STAT` (matrix l.72). The reviews of A4 and A5 come under it.

### 1.3 The lockbox seed

**Recommended:** derive it from the C2 beacon-protected trial seed, `trial_seed_j`. Its stream label is `"lockbox_prediction"` (A3, A4).

**Why this is enough.**
- The seed exists only after the declaration post (DRAFT l.146, l.151). After the post, everything that feeds q is fixed:
  - the trial set is frozen by hash;
  - the nominee is chosen by rule;
  - the round is fixed by procedure (D20_D13 `PROPOSAL.md` l.442-453).
- So nobody can search the lockbox draws offline before the post. After it, nothing they could learn can be fed back in. The only exception is invalidating the cycle and declaring again, which costs one m and is already disclosed (l.455-463).
- A second beacon at sealing would add machinery and gain nothing.

**Anti-probing rules: no conflict.**
- Seeding reads no lockbox byte. So §7 l.77, l.85, protocol l.74-76, l.296 and THREAT_MODEL l.17 are untouched.
- What it does not hide is in D20L-5.

**Cost.** R-13 says "only" for C-1, C-10 (3) and C-12 (5), and D11R-S-7 (REV2 l.175) said the beacon decision does not extend to the lockbox. So C2 needs one row adding "the lockbox prediction stream (L-1)" to R-13 (D20L-4).

## 2. Findings

1. **D20L-1 NON-BLOCKING.** The lockbox stream needs matrix option (a): new vectors (l.72).
   - ψ(d) is not the Task 12 E-IMPROV influence: b is 7.70277 against 6.31108 (§0).
   - D20_D13's argument for reusing the stream for G-1 rested on an unchanged estimand (l.72-84). It does not carry over here.
2. **D20L-2 NON-BLOCKING.** The code has two ψ conventions for E-DIFF:
   - Task 12 `_influence`, with the population scale, which is what D-11 bound;
   - `dsr._column_lengths` (dsr.py l.84-97), with the sample scale and the maximum of two lengths.

   Their b values differ (§0). The lockbox must call the first, and a test must pin it. This is not a conflict: they serve different clauses.
3. **D20L-3 BLOCKER (for building; owner Q3).** Decided R-14 (DRAFT l.152) lets C2 evaluation code load only from the engine commit or the later object files (`mapping.py`, `screen.py`, `heldout.py`; qobj.py l.56-63). The lockbox prediction artifact is computed by the experiment engine (D-11 REV3 l.35-41), and the lockbox run uses engine code. So the lockbox code cannot load anywhere today. This is the same build-order consequence that D20_D13 noted (l.155-160).
4. **D20L-4 QUESTION (owner Q2).** Using the beacon seed for the lockbox means extending R-13, and through it overriding protocol l.266 for one more stream.
5. **D20L-5 NON-BLOCKING (disclosure).** Even with the beacon seed:
   - after the post, anyone with the public confirmation prices can compute q;
   - lockbox prices are public (D-11 Q3, `OWNER_DECISION_D11.md` l.12).

   The seed closes only the free search, before the post, over q's Monte Carlo noise. C-13 (Annex C l.477-486) should say so.
6. **D20L-6 NON-BLOCKING (inherited from Task 12; not repaired).**
   - `CONVENTION_DOCUMENT_SHA256` is the SHA-256 of the LF bytes of `IMPLEMENTATION_CONVENTIONS.md`. The working-tree file here is CRLF, raw hash `d6d9de50…`.
   - Root `.gitattributes` does not protect `review/task12/**`. So the file's sentence "must equal the raw SHA-256 of this file" (l.97) holds only for the LF form.
   - Streams are unaffected, because the constant is a literal.
   - The index blob was not checked.
7. **D20L-7 QUESTION (wording, not an owner choice).** The rules on the nominee's model seed disagree:
   - R-13 (DRAFT l.151) keeps l.266 for "the nominee's own fit";
   - Annex C l.412 says "the model seed its declaration fixes";
   - `screen.py` MR-2 (l.1473-1477, l.1547) uses seed 0. It is a proposed reading, pending review.

   A1 binds whatever the reviewed `walk_forward` passes. The screen.py §16 review and the C2 wording should reconcile the three.
8. **D20L-8 NON-BLOCKING (inherited D11-8).** DRAFT l.254 says the existing purposes include "the lockbox interval (line 85)". No such purpose exists in the code: `ReplicateStream` accepts only `paired_sharpe_ci` (l.465). C2 must add `lockbox_prediction` and correct the comment.
9. **D20L-9 NON-BLOCKING.** There is no signing code or signing library in the repository, the venv or the image (`requirements.lock`). HMAC is unsuitable, because the P-8 publisher verifies signatures and would then hold a key that can forge them. Hence Q4.
10. **D20L-10 NON-BLOCKING (dependency).** The signer's guard needs the exact day-255 instant. That waits on D11-15 in the S4 draft (`OWNER_DECISION_D11.md` l.28). It blocks the signer's build, not this proposal.
11. **D20L-11 NON-BLOCKING.** float64 type-7 uses fraction 0.9500000000000028, not 19/20. Under D-11's float rule, the vectors and the P-4 check must record and compare float outputs computed with the same `0.05` literal.
12. **D20L-12 NON-BLOCKING (AI default, adopted only through Q1).** A step-2 write that fails before it commits may be retried.
    - D-11 REV3 l.55 ("no retry") covers verification mismatches only.
    - An uncommitted step 2 reads no lockbox byte and spends no budget.
13. **D20L-13 NON-BLOCKING.** `screen.load` re-reads source from its import path (l.587-588). For verified retrieval the lockbox needs a variant that loads from bytes. Otherwise a CRLF checkout fails the hash, or a substituted path is loaded.
14. **D20L-14 NON-BLOCKING.** `dsr.v_runtime_check` uses canaries measured on the run's own machine (l.297-299), so the lockbox must not reuse it. A6 uses the image digest plus the A5 vectors instead.

## 3. Owner questions

**Q1. Adopt all the technical rows?** These are A1, A2, the A3 identity, A4, A5, the A6 wording and B1-B6, including the AI default in D20L-12.
- **"Adopt (Recommended)."** The lockbox rules become exact enough to build and test. Cost: several builds, each with its own §16 review.
- **"Keep blocked."** No lockbox read can run, so C2 cannot promote anything.

**Q2. Which seed drives the lockbox's random draws?**
- **"The beacon-protected seed, as for G-1 (Recommended)."** Nobody can tune the forecast's random noise before the public post. Cost: one more C2 row extending R-13.
- **"The old protocol seed (l.266)."** No wording change. Cost: the seed is known before the post, so cosmetic edits can be tried offline in search of a luckier forecast. The effect is small, but it is free, and it must be disclosed.
- **"Keep blocked."**

**Q3. Where does the lockbox code live, given rule R-14?**
- **"Its own reviewed file, with its hash written into the signed C2 (Recommended)."** The freeze is not delayed. Cost: one row amending R-14, and the code must be built and reviewed before you sign C2.
- **"Inside `screen.py`, before the freeze."** No wording change. Cost: the freeze waits until the lockbox code is built and reviewed.
- **"Keep blocked."**

**Q4. How are lockbox certificates signed?**
- **"Ed25519 with the standard `cryptography` library, hash-pinned, in the signer's own small environment (Recommended)."** Cost: one new dependency and one key-setup step. The calibration image does not change.
- **"Ed25519 written in plain Python from the RFC."** No new library. Cost: hand-written cryptographic code that does not run in constant time, and a heavier review.
- **"Keep blocked."** No PASS can be certified.

## 4. What remains, and what stays unauthorised

**C2 rows needed:**
- R-8 (A6);
- R-13 (Q2);
- R-14 (Q3);
- the `added_purposes` correction (D20L-8);
- the signing values (B1), alongside the D-12 rows `OWNER_DECISION_D12.md` l.28 already lists.

**Before building:**
- D11-15 (D20L-10);
- the D20L-7 seed wording;
- the R19-2 reviews of this proposal.

**Builds, each a later authorised task with §16 different-model and owner PR review:**
- the artifact store and the byte-based loader;
- the C2 baseline runner;
- the lockbox stream, ψ and q code, with its vectors;
- the `lockbox_eval` runner;
- the signer, the publisher and the time-checking store;
- tests T-1..T-8.

**Unauthorised:**
- frozen edits, hash or sidecar changes;
- activating or accepting this proposal;
- any code;
- calibration or simulation runs;
- confirmation or lockbox data access;
- key generation;
- promotion, deployment and trading.

`KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.
