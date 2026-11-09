# Design: closing the two seed checks the evaluation cannot run (R14S4-S-1, LG4-1, LG4-6)

- Status: **DRAFT for review**, rev 2, 2026-11-09 (reuses the FP3 drand verifier from `origin/freeze-sheet`). Author: Claude Opus 5.5
  (`claude-opus-5-5`). Owner's route: "go with 1" then "go with rev 2" (2026-11-09).
  No code until this design is reviewed and the owner decides §9.
- Rev 1 (8317145) was reviewed by Sol: FIX, SV1-S-1..8, all accepted
  (`SOL_SEED_VERIFIER_DESIGN_8317145.md`, `ADJUDICATION_SEED_VERIFIER_8317145.md`).
- Governing text cited from `origin/freeze-sheet` `DRAFT_WORDING.md` (R-8 l.152, R-13
  l.156, R-14 l.157, R-14a l.159 items 2-4 and 7, seed_disclosure); this branch carries
  rev 9 without R-14a.

## 0. What changed from rev 1

| Finding | Rev 2 |
|---|---|
| SV1-S-3 (R-8 binds `trial_seed` on the qualified image) | **Line 266 moves back inside the evaluation** (§2): the module calls the real frozen `trial_seed` on the qualified image. No exception needed for line 266. The external verifier keeps only BLS. |
| SV1-S-2 (record asserts its own verification) | The external claim shrinks to one fact: "this signature verifies for this round under this key". It is checked by the **existing FP3-reviewed drand verifier** (drand's own client) and **re-run from its lock on a CI host** (§3.3-§3.4); the verifier's file and lock hashes are pinned in the module. |
| SV1-S-1 (no authoritative hash source) | A `beacon_verification` entry in the repository's existing hash-chained, append-only ledger is the authority, named by the signed C2 (§4, owner item OD-3). |
| SV1-S-4 (inputs not authenticated) | Each value has a named governing source, checked by the loader (§4 table); chain hash and scheme added. |
| SV1-S-5 (BLS message bytes) | Specified (§3.2); done by drand's own client, no new BLS code. |
| SV1-S-6 (lockbox handoff) | Sealing record carries the verification hash and seeds; lockbox request filled from it (§6). |
| SV1-S-7 (numpy; `check_beacon` mixed) | No new verifier environment (reuse, §3.3); `check_beacon` split (§5). |
| SV1-S-8 (7-day evidence) | Dated evidence named (§4, OD-3). |

## 1. Problem (narrowed)

1. **Line 266** (R-8, R-13): `seed_l266` is `aqt.core.preregistration.trial_seed`, bound
   "on that object's pinned runtime and image" (R-8). Its module does
   `from jsonschema import Draft202012Validator` and `from jsonschema.exceptions import
   SchemaError, ValidationError` at top level; `jsonschema` is not in the image.
2. **BLS** (seed_disclosure `verification`; R-14a item 7): the round's signature must verify
   against the fixed key. No BLS library is in the image, and the image cannot change (prereg
   §13 rev 7g item 6; the full run started on it, `cb76232`).

## 2. Line 266 inside the evaluation

`trial_seed` → `seed_material` → `_require_sha256`, `_require_trial_index`, `json`,
`hashlib`. None of it touches `jsonschema`; the three names are used only by
`_validate_against_schema`, which the evaluation never calls. The module's other
imports (`aqt.core.ledger`, `aqt.core.paths`, `aqt.data.manifest`, `aqt.data.bars`) use only
the standard library and engine modules already loaded in the image.

So `derive_seeds` imports the frozen module **lazily** (inside the function, so the engine
import test is unaffected) through one helper:

- if `jsonschema` is importable, import normally (repository test environment);
- otherwise, for the duration of that one import only, place an **inert placeholder** named
  `jsonschema` (and `jsonschema.exceptions`) in `sys.modules` whose three names are classes
  that raise `SeedError` if ever instantiated or called; import
  `aqt.core.preregistration`; then remove the placeholder entries from `sys.modules`.
- R-14's byte check (each loaded `aqt` module equals the engine commit's file) applies to
  `preregistration.py`, `ledger.py`, `paths.py` as to every other loaded module.

`derive_seeds` then calls `preregistration.trial_seed` directly. The `line266` parameter is
deleted: the caller cannot choose it (closes R14S4-S-1's line-266 half). The placeholder
holds no rule and computes nothing; it is disclosed in the module contract (R-14a item 5).
Whether it is consistent with R-14 "nothing is loaded from outside these" and R-14a item 3 is
**owner item OD-2**, with a recommendation.

## 3. BLS: the external verifier

### 3.1 Scope

One fact only: the signature of round r verifies under the fixed chain's public key. It
computes no seed.

### 3.2 The exact check (drand quicknet, `bls-unchained-g1-rfc9380`)

- message = SHA-256 of r as an **8-byte unsigned big-endian** integer;
- signature: 48-byte compressed G1 point; public key: 96-byte compressed G2 point; both
  decoded with curve and subgroup checks, refusing the point at infinity;
- hash-to-G1 per RFC 9380 with DST `BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_`;
- check e(sig, g2) = e(H(m), pk).
- Chain identity: chain hash `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971`,
  genesis 1692803367, period 3 s (to be confirmed at build against drand's published chain
  info and fixed in the signed C2, OD-4).

drand's own client implements exactly this; §3.3 uses it, so no BLS code is written here.

### 3.3 Implementation A: the existing FP3 verifier (reuse, no new verifier)

The held-out certification already has this procedure (`origin/freeze-sheet`,
`deploy/calibration/FREEZE_HELDOUT.md` step K, "the drand record"; FP3
`review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md` Rules 2-6):

- `deploy/calibration/drand-verify/verify.mjs`: drand's own `drand-client` 1.4.2, every
  dependency pinned in `package-lock.json`, `npm ci --ignore-scripts`, runs offline on saved
  responses; exit 0 only if the chain info equals the bound hash, key, scheme, period and
  genesis, the round is the expected round, and the BLS signature verifies; randomness is
  computed as SHA-256 of the raw signature, ignoring the response's field. Tested with real
  rounds and negatives in `review/fp3/verifier-test-2026-10-25/`, and reviewed under FP3.
- Fetch the round from at least two relays with the chain hash in the path; save each raw
  response with source and retrieval time.

C2 uses the same verifier and the same fetch rules; only the record and its authority (§3.5,
§4) are C2's. This drops rev 1's new Python verifier, its image and the BLS library choice
(rev 1 Q1, SV1-S-7's numpy point): nothing new is pinned.

### 3.4 Implementation B: independent re-run

A CI job (a different host and identity) re-installs `drand-verify` from its lock with
`npm ci --ignore-scripts` (an independent rebuild of the reviewed bytes, Sol's Q4) and re-runs
it on the committed raw responses and chain info. Its job id, runner identity, lock SHA-256
and output go into the record. **Both must exit 0.** If the owner wants a different code base
as well, drand's Go CLI can be added as a third check (not proposed; OD-1).

### 3.5 Output

`aqt.c2.beacon_verification.v1`, canonical JSON (`seeds.cj`): `{schema, chain{hash, scheme,
public_key, genesis_time, period}, capture_cdx, round, scheduled_time, randomness, signature,
message_sha256, responses[{source, retrieved_at, sha256}], verified_by[{implementation:
"drand-verify", verify_mjs_sha256, package_lock_sha256, host_or_ci_identity, output}] (A then
B)}`, committed with the raw responses and the chain-info file. Anything else (either fails, errors, round not available) writes no record:
`seed_disclosure.failure`, no fallback.

## 4. Authoritative sources (SV1-S-1, S-4, S-8)

Every value the module or the verifier uses comes from one named governing record, resolved
by the slice-6 loader before any gate, never from the caller:

| Value | Governing source |
|---|---|
| chain hash, scheme, public key, genesis, period | the signed C2 protocol bytes (seed_disclosure `beacon` `<<SIGNING>>`; genesis and period added there, OD-4) |
| T (capture CDX) | the frozen O-6a acceptance record (SPEC §5) |
| declaration, `protocol_hash`, ordered trials | the accepted post → declaration bytes → protocol bytes (R-14a item 2's chain) |
| trial records (`hypothesis_hash`, `trial_index`) | the immutable C2 trial records (LG4-2) |
| the verification record's SHA-256 | a `beacon_verification` entry in the repository's existing hash-chained append-only ledger (`aqt.core.ledger`), appended after the round and before the evaluation, the entry type named by the signed C2 (OD-3) |
| 7-day availability evidence | that ledger entry's commit pushed to GitHub within 7 days of the round's scheduled time; GitHub's push record is the dated third-party evidence (OD-3) |

The module refuses missing or extra fields in the record and compares every field to these
sources. The ledger entry is append-only and hash-chained, so a later swap is detectable; the
signed C2 naming the entry type removes the caller's choice of manifest.

## 5. The confirmation module (slice 4a change)

- `check_beacon` is split: `check_beacon_local(beacon, round_, chain)` keeps the fixed round,
  lowercase hex and randomness = SHA-256(signature) checks; the `Verifier` type and `verify`
  argument are deleted.
- `derive_seeds(*, ..., beacon_record: bytes, beacon_record_sha256: str)` (both from the
  loader, §4): refuses unless the hash matches; the bytes are canonical (`cj(json.loads(b)) ==
  b`); schema is v1; chain, T, round (recomputed by `beacon_round`), randomness and signature
  equal the governing values and pass `check_beacon_local`; `message_sha256` equals
  SHA-256(8-byte big-endian r); `verified_by` holds exactly A then B, each output `ok: true` with
  the same round, signature and randomness, and each `verify_mjs_sha256` and
  `package_lock_sha256` equal constants pinned in the module (the FP3-reviewed files' hashes;
  `None` until set at build, refusing every evaluation).
- Line 266 per §2. Annex B, R-7, R-13 and `estimator_seed` as today. The record SHA-256 is
  recorded as the provenance of the signature check (§27).

## 6. Lockbox handoff (SV1-S-6)

The sealing record carries the beacon record's SHA-256, each family's `family_seed` and each
trial's `seed_l266` from the confirmation record. The slice-6/store handoff fills the lockbox
`Request` from the immutable sealing entry, never from a caller. A test substitutes a coherent
fabricated request and artifact and must be refused. R14S4-S-3 (lookup by `(family,
trial_id)`) goes in the same lockbox change, with its own review.

## 7. Tests

- §2: the seed through the lazy import equals the frozen function, in the normal environment
  and in a subprocess where `import jsonschema` is blocked; calling a placeholder name raises
  `SeedError`; the placeholder is gone from `sys.modules` afterwards; `test_d19_deploy` still
  prints `['numpy']`; the AST test now allows only the lazy helper's import.
- §3: reuse of FP3's verifier tests (`review/fp3/verifier-test-2026-10-25/`); the CI job
  re-runs it on the committed responses and fails on any non-zero exit.
- §5: one refusal test per check; a valid record gives today's seeds.
- §6: the coherent-substitution test.

## 8. Not changed

The calibration image and the full run; the seed formulas and round rule; the lockbox's rule
that `seed_l266` comes from the sealing record (R14L5-S-2 (a)).

## 9. Owner decisions (governance proposals; AI cannot decide them)

- **OD-1 (R-14a item 7, "verifies itself"):** accept that the module meets item 7 for the
  beacon signature by checking an authoritative record of the FP3 verifier's run and its CI
  re-run (§3-§4), with S4 wording saying so. *Recommendation: accept; the alternative is a
  pure-Python BLS implementation inside the module, a large unreviewed cryptographic rule
  R-14a item 4 does not allow.*
- **OD-2 (line 266 placeholder):** accept the inert, temporary `jsonschema` placeholder (§2)
  as consistent with R-14 and R-14a item 3, disclosed in the module contract. *Recommendation:
  accept; it lets the frozen function run on the qualified image exactly as R-8 binds it,
  so no exception is needed. Alternative: an explicit R-8 exception for an external
  line-266 computation (rev 1), which is weaker.*
- **OD-3 (authority and deadline):** the signed C2 names the `beacon_verification` ledger
  entry as the authority, and its GitHub-pushed commit within 7 days as the dated evidence.
  *Recommendation: accept.*
- **OD-4:** add the chain's genesis time and period (with hash, scheme, key) to the signed C2
  `<<SIGNING>>` row. *Recommendation: accept.*

## 10. Open for review

Q1 is closed by reuse (§3.3): whether reusing the FP3 verifier and fetch rules for C2 needs
anything beyond FP3's own review (C2's 7-day rule vs FP3's no time limit; the C2 chain
wording, `review/fp3/C2_BEACON_WORDING_PROPOSAL.md`); Q3 treat the module change and the CI
re-run job as §16 protected (proposed yes); whether §2's placeholder has any import-time side
effect not seen here.
