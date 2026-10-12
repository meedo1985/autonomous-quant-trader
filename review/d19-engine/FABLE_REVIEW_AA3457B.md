# Fable 5.1 review of D-19 engine repairs and D19CR-4 build (2e77f45..aa3457b)

- Reviewer: Fable 5.1 as a Claude subagent, read-only (implementer: Claude Opus 5.5).
- Scope: `git diff 2e77f45 aa3457b -- calibration scripts tests pyproject.toml` against prereg §13 rev 7g items 4 and 6.
- Verdict: FIX (FE-1..FE-8). Hand-back reproduced verbatim below.

---

Reviewer model: claude-fable-5-1

Verdict: FIX

The D19CR-1, D19CR-2 and D19CR-3 repairs hold. The D19CR-4 build has three MAJOR gaps against §13 item 6: the start gate does not check code identity, the generator hash leaves out code that method V and U_G call, and the U_G reference vector cannot catch runtime differences.

Evidence I ran myself, all output in a temp dir:
- The rundef, chunks and engine tests: 32 passed.
- `mypy calibration scripts/d19_run_definition.py`: Success, no issues in 10 files.
- I traced the 4 reference cases directly. Every case gives `reason=None` and has a nominee. `u_g` returned `None` in all four.

**Q1. D19CR-1..3 repairs: confirmed**
- **D19CR-1 (classifier.py):**
  - `required(k)` gives 8 tails, or 6 at K=1. The tails match item 4.
  - `fit_thresholds` refuses empty input, a missing K/T, mixed fields, mixed K/T and non-finite draws.
  - `ranks` is unchanged: (n−q, q+1).
  - Ties are accepted (`<=` / `>=`).
  - Thresholds are refused when incomplete or non-finite.
- **D19CR-2 (chunks.py:102-111, 152):** `verify` and `reduce` now refuse `.tmp`, duplicated and out-of-range files without deleting them. Only `run` (a restart) deletes `.tmp`.
- **D19CR-3:** `mypy_path = "src"` works.
- **Revert check:** the new tests at test_calibration_engine.py:228-265 and test_calibration_chunks.py:139-155 would fail if their repair were reverted.

**FE-1 MAJOR — rundef.py:152-166; scripts/d19_run_definition.py:51-52**
- **Problem:** `start_gate` never recomputes `generator_sha256`, and `engine_commit` is a free CLI string that is never checked against the checkout.
- **Failure scenario:** the owner pulls or edits code between a stop and a resume. The gate still passes because identity, canaries and reference vectors are unchanged. New chunks are then computed by different code but carry the same run-definition binding hash. The reference vectors catch a change only if it affects their 4 cases.
- **Repair:**
  - In `start_gate`, recompute the code hash and compare it to `defn["generator_sha256"]`. Fail closed with a U_ops error.
  - At `record`, check that `engine_commit` equals HEAD and the tree is clean. If git is not available in the image, hash the tracked files instead.

**FE-2 MAJOR — rundef.py:102-106**
- **Problem:** `generator_sha256` hashes only `calibration/*.py`. Method V imports `aqt.metrics.statistics` (dsr.py:29), and so do G-1 and G-12 (gates.py:13). Those use its `block_length`, `bootstrap_indices`, `paired_sharpe_*` and `effective_sample_size`.
- **Failure scenario:** a change in `src/aqt/metrics` changes U_G or DSR outcomes, and the run definition does not record it.
- **Repair:** also hash `src/aqt/metrics/**/*.py`, or every `src/aqt` module file found in `sys.modules` after importing `dsr` and `gates`. Add a test that edits `statistics.py` and expects the hash to change.

**FE-3 MAJOR — rundef.py:56-66 (reference vectors and U_G)**
- **Problem:** `gates.u_g` returns only an availability reason or `None`. I measured `None` for all 4 cases, so the U_G part of the suite is one constant value per case.
- **What escapes:** none of these numerics are compared bit-exactly:
  - the G-1 bootstrap: block length, `bootstrap_indices`, `fast.mean_var` and the scaled replicate Sharpes;
  - the G-12 ESS values;
  - the G-10 split variances.
- **Also:**
  - `legs.benchmark` is never hashed, so its generator path goes unchecked.
  - No case reaches an UNAVAILABLE reason.
- **Failure scenario:** a runtime that changes these intermediates passes the gate unless one of 4 availability flags flips. The spec asks for a suite that exercises U_G.
- **Repair:**
  - Hash `legs.benchmark`.
  - Record the U_G intermediates per case: `st.block_length(...).value`, the replicate Sharpe vector as hex, ESS values per horizon, and G-10 variances.
  - Add one case that is designed to be unavailable, e.g. a G-2 or G-10 refusal.

**FE-4 MAJOR — rundef.py:162; scripts/d19_run_definition.py:46**
- **Problem:** the image digest is whatever `AQT_IMAGE_DIGEST` says. The spec gates libc only through the digest (BF5-1), and nothing measured backs the env var up.
- **Failure scenario:** the image is rebuilt or patched, so libc/libm changes while Python, NumPy and OpenBLAS stay identical, and the old digest is passed with `-e`. The gate passes. Only the libm canary, 512 scalar and 4,096 vector points, stands in the way.
- **Repair:** have the owner's launcher take the digest from `docker inspect` on the host, not from typed input. Or record a hash of the libc and libm files the process has loaded (`/proc/self/maps`) as disclosed provenance next to the digest. Either way, document it in the run procedure. Making libc a gated field would be an amendment, so it is not a code repair.

**FE-5 MINOR — chunks.py:72-86; rundef.py:152**
- **Problem:** nothing ties chunk acceptance to the run definition. `_check` compares against the caller-supplied `Chain.binding` and `Chain.gating`, and nothing requires a passed `start_gate` before `chunks.run`. There is no driver yet.
- **Repair:** in the coming driver, build the `Chain` only from `binding=definition_sha256(defn)` and `gating=start_gate(defn)`, and test that order.

**FE-6 MINOR — classifier.py:93-98**
- **Problem:** in `within`, the finite and K/T checks run before the field-set check. A diagnostic dict with a missing field plus a NaN, or with K/T missing, comes back as a refusal (`False`) instead of an engine error. That miscounts an engine fault as a DSR-availability event.
- **Repair:** do the `set(values) != required(int(upper["K"]))` check first. An actual K/T mismatch still returns `False`.

**FE-7 MINOR — classifier.py:128-129 (process)**
- **Problem:** one non-finite diagnostic among the 300,000 threshold draws stops the whole threshold run. This fails closed and is documented as unsettled.
- **Risk:** zero-variance or zero-periodogram draws are plausible in Q5/QJ, which use exploration data.
- **Repair:** have the owner decide how non-finite threshold draws are treated, or have the re-pilot measure their rate, before the threshold run.

**FE-8 MINOR — tests/unit/test_calibration_rundef.py**
- **Tests that FE-1 to FE-3 need, and the cover they lack now:**
  - No test changes `identity`, which is the `v_runtime_check` "runtime differs" path.
  - No test shows the gate refusing a code change; this follows from FE-1.
  - No reference-vector test would fail if U_G numerics changed; this follows from FE-3.
- **Also untested:** a tie at a lower bound (`min_skewness == lower`).
- **Pinning:** the prereg is pinned only by a commit string. Optionally also record the SHA-256 of the PREREGISTRATION.md content.

**Q2 checks that passed**
- The gating identity contents match the spec: A-V1 identity, image digest, both canaries and the reference vectors.
- "Platform" is system plus machine only.
- Host provenance is recorded but not in gating and not in the chunk hash, so it is never compared.
- Gate order is `v_runtime_check` (environment, canaries, identity), then the image digest, then the reference vectors. All of it runs before any chunk and fails closed with exit 1.
- Method V outputs (block, z, s0, length_ratio) are hashed bit-exactly as float hex.
- The run definition contains every item the spec lists.

Files: `D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/rundef.py`, `calibration/classifier.py`, `calibration/chunks.py`, `calibration/gates.py`, `calibration/dsr.py`, `scripts/d19_run_definition.py`, `tests/unit/test_calibration_rundef.py`.

The repository was not modified. This report is not committed; under AGENTS.md its findings must be written to a review record and committed before anyone cites it.
