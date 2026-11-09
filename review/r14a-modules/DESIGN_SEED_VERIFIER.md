# Design: the separate seed verifier (closes R14S4-S-1, LG4-1, LG4-6)

- Status: **DRAFT for review**, rev 1, 2026-11-09. Author: Claude Opus 5.5
  (`claude-opus-5-5`). Owner's choice of route: "go with 1" (2026-11-09), after the
  correction in `ADJUDICATION_SLICE4A_EF33D67.md`. No code until this design is reviewed.
- Supplements `DESIGN.md` §5.1 (which already allows "a verified subprocess") and keeps
  `OWNER_DECISION_R14L5_S2.md` (the lockbox takes `seed_l266` from the sealing record).

## 1. Problem

Two seed checks cannot run inside the evaluation:

1. **BLS** (`seed_disclosure.verification`): the round's signature must verify against the
   fixed quicknet public key. No BLS library is in the pinned image.
2. **Line 266** (R-8, R-13): `seed_l266 = preregistration.trial_seed(...)`, the frozen
   function. Its module imports `jsonschema`, which is not in the image, and R-14a item 4
   forbids a copy.

The image cannot change: C2's real evaluation must run in the calibration's image (prereg
§13 rev 7g item 6, A-V1), and the full run has started on it (`cb76232`). Slice 4a now takes
both checks as injected callables, which a caller can fake (R14S4-S-1).

## 2. Route

A small **seed verifier** runs once, **outside** the evaluation, in its own pinned
environment that has the BLS library and `jsonschema`. It writes one canonical-JSON
**seed verification record**. The record is committed, its SHA-256 is bound into the
evaluation's governing inputs, and the confirmation module checks everything it can against
it and refuses any difference. No callable is passed into the module any more.

```
public inputs ──► seed verifier (own pinned env) ──► seed_verification.json (committed)
                                                             │ sha256 bound in the inputs
evaluation image: derive_seeds(record bytes, its sha256, ...) ┘ check, recompute, refuse
                         └─► confirmation record ──► sealing record (seed_l266) ──► lockbox
```

## 3. The verifier

- **Code:** one module, `calibration/seed_verify.py` (name to settle), that may import
  `aqt.core.preregistration` because it never runs in the calibration image. It calls the
  frozen `trial_seed` itself (R-14a item 4) and one BLS library call. It reuses slice 4a's
  `beacon_round` and `check_beacon` so the round rule and local checks are the same code.
- **Environment:** `deploy/seed-verify/` with a hash-pinned `requirements.lock` (numpy is
  not needed; `jsonschema` and its dependencies at the versions the repository's own
  environment uses; one BLS library) and a Dockerfile, built from the engine commit. Its
  image digest is recorded, taken from `docker image inspect` on the host, never typed
  (as FE-4).
- **BLS library: open, to choose in build review.** It must support quicknet's scheme
  (`bls-unchained-g1-rfc9380`: signature on G1, public key on G2, DST
  `BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_`). Candidates to evaluate: the `blst`
  Python binding, `py_ecc`. Choice rule: maintained, wheels or a reproducible build,
  hash-pinnable, and it passes the known-answer tests in §6. Its source and provenance are
  reported to the owner before it is pinned (AGENTS.md: no unreviewed third-party code).
- **Inputs** (all public or already-governing): the chain (public key, genesis, period,
  from the signed C2), the capture timestamp T, the beacon (round, randomness, signature,
  fetched from drand), `protocol_hash`, and each declared trial's `trial_id`,
  `hypothesis_hash`, `trial_index` (the immutable C2 trial records). No confirmation or
  lockbox data, no credentials.
- **Behaviour:** compute the round from T; refuse unless the beacon is that round; run the
  local checks; verify the BLS signature; compute every `seed_l266`. Any failure writes no
  record and exits non-zero (no fallback, `seed_disclosure.failure`).
- **Output** `aqt.c2.seed_verification.v1`, canonical JSON (`seeds.cj`):
  `{schema, chain{public_key, genesis_time, period}, capture_cdx, beacon{round, randomness,
  signature}, bls_verified: true, protocol_hash, trials[{family, trial_id, hypothesis_hash,
  trial_index, seed_l266}], verifier{engine_commit, module_sha256, lock_sha256,
  image_digest}}`. Trials in declared order.

## 4. The confirmation module (slice 4a change)

`derive_seeds` loses `verify` and `line266` and gains `verification: bytes` and
`verification_sha256: str` (the bound hash, read by the slice-6 loader from the governing
inputs, never from the caller's arguments). It refuses unless:

1. `sha256(verification) == verification_sha256`, and the bytes are exactly
   `cj(json.loads(bytes))` (canonical, no second encoding);
2. `schema` is the v1 name and `bls_verified is True`;
3. chain, capture timestamp, round (recomputed with `beacon_round`), randomness and
   signature equal the module's own inputs, and `check_beacon`'s local checks pass;
4. `protocol_hash` and the trial list (family, id, hypothesis hash, index, in declared
   order) equal the module's own validated records exactly;
5. every `seed_l266` is 64 lowercase hex;
6. `verifier.module_sha256` and `verifier.lock_sha256` equal constants pinned in the module
   at build (`None` until set, which refuses every evaluation, like
   `FROZEN_VECTORS_SHA256`).

It still computes Annex B, R-7 family seeds, R-13 trial seeds and `estimator_seed` itself,
and records the verification record's SHA-256 as the provenance of BLS and line 266
(Constitution §27).

## 5. Why a forged record does not get through

- The record is reproducible: anyone with the repository and the pinned verifier image
  re-runs it on the same public inputs and must get the same bytes. The procedure requires
  **one independent re-run, compared byte for byte, before the evaluation starts**.
- Its hash is bound in the governing inputs before the evaluation, so it cannot be swapped
  afterwards; every other value in it is re-checked by the module (§4 items 3-4), so only
  `bls_verified` and `seed_l266` rest on the verifier, and both are what the re-run checks.
- The verifier's code and lock are pinned by hash in the module (§4 item 6).

Residual trust (stated, not removed): the verifier's environment, as for any build. It is the
same trust model as the sealing record the owner already chose (R14L5-S-2 (a)).

## 6. Tests

- Verifier (in the repository's own test environment, which has `jsonschema`): the real
  quicknet round 1,000,000 verifies; one flipped signature bit, a wrong public key and a
  wrong round each fail; `seed_l266` equals the frozen `trial_seed`; a known answer for the
  record bytes.
- Module: each §4 item has a refusal test (wrong hash, non-canonical bytes,
  `bls_verified` false or missing, each mismatched field, re-ordered or missing trial, bad
  hex, unset pins); a valid record gives the same seeds as today's tests; the AST test still
  shows no `preregistration` import; the engine import test (`test_d19_deploy`) still prints
  `['numpy']`.

## 7. What it does not change

The calibration image and the running full run; the lockbox (it still takes `seed_l266` from
the sealing record); the round rule and the seed formulas. R14S4-S-3 (lockbox lookup by
`(family, trial_id)`) stays a separate lockbox item.

## 8. Open for review

- Q1: the BLS library (§3).
- Q2: where the record's hash is bound: in the slice-6 loader's governing input manifest
  (proposed), or a field of the signed C2 inputs.
- Q3: is the verifier image a Constitution §16 protected component (then: different-model
  review and the owner's PR review before merge)? Proposed: treat it as one.
- Q4: who does the independent re-run (proposed: a second host or CI job, same pinned image).
- Q5: the 7-day "no verifying output" rule stays operational (LG4-4).
