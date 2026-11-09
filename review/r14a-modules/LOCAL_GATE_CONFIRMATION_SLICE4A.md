# Local gate: R-14a confirmation module, slice 4a (seeds)

- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-09, applying the repository
  skills `task-gate-review`, `scientific-reproducibility-review` and `quant-code-review`.
  The same model wrote the code; this is a self-review, not the independent
  different-model review R-14a item 1 requires (Sol, prompt
  `SLICE4A_CONFIRMATION_PROMPT_SOL.md`).
- Scope: DESIGN.md §5.1 and §5.2 step 3: `beacon_round`, `check_beacon`,
  `annex_b_seed`, `beacon_family_seed`, `derive_seeds` and their types in
  `calibration/c2_confirmation.py`; tests `tests/unit/test_c2_confirmation_seeds.py`.
  Base `15941ad` (slices 1-3 accepted, R14C7). Governing text: S4 DRAFT_WORDING R-7,
  R-13, `seed_disclosure` (l.146, 151, 154-166); Annex B §2.4; protocol_v1.yaml
  `random_seed_policy` (line 266); owner decision D20/D13 B2 (named-object R-7 encoding).
- Out of scope (later slices): the BLS signature verifier itself (slice 4b), sealing, the
  A4 copy, C-14, the loader and records (slice 6).
- Finding IDs: LG4-n. **LOCAL GATE: PASS** (no open blocker), with the items in §5.

## 1. Changed files

`calibration/c2_confirmation.py` (+261 lines, appended after `seeds_record`; no new
import),
`tests/unit/test_c2_confirmation_seeds.py` (new). No other code path. Slices 1-3 bytes
unchanged (diff hunks only at the import and after `seeds_record`).

## 2. Validation (Windows 11, repo `.venv`, Python 3.14)

| Command | Result |
|---|---|
| `pytest tests/unit/test_c2_confirmation_seeds.py` (after LG4-6) | 25 passed |
| CI engine job `pytest tests/unit/test_calibration_*.py test_c2_lockbox*.py test_c2_confirmation*.py test_d19_deploy.py` (first version) | 696 passed, 1 skipped, **1 failed** (LG4-6), 24:56 |
| after the LG4-6 repair: `pytest test_c2_confirmation*.py test_c2_lockbox*.py` | 217 passed |
| after the LG4-6 repair: `pytest test_c2_confirmation_seeds.py test_d19_deploy.py` | 36 passed |
| `pytest test_binance_public test_calibration_chunks test_dashboard test_monitoring` | 130 passed |
| `ruff format --check`, `ruff check .` | clean |
| `mypy src` | no issues (56 files) |
| `mypy --strict` module and new tests | no issues in these files |
| `lint-imports` | 7 contracts kept, 0 broken |

## 2a. Engine job

The first version imported `aqt.core.preregistration` to call line 266's `trial_seed`.
`test_d19_deploy::test_the_engine_loads_no_third_party_package_but_numpy` failed: that
module imports `jsonschema` (plus attrs, referencing, rpds, typing_extensions), none in
the pinned image. Repaired as LG4-6. The other `calibration` engine tests are unaffected by
this slice (nothing imports the new functions); the deploy test and every confirmation and
lockbox test were rerun after the repair. Note: during the first run the author briefly
stashed the working tree for a type-check comparison; the confirmation and lockbox suites
were therefore rerun in the foreground after the repair (217 passed).

## 3. Frozen artifacts

`git diff --stat 15941ad` touches only the two files of §1; no path under `docs/`,
`protocols/`, `schemas/`, `specs/`, no `FROZEN_HASHES.json` or sidecar. No hash
regenerated.

## 4. Self-review

- Determinism: every seed is SHA-256 of canonical JSON (`calibration.seeds.cj`: sorted
  keys, no whitespace, UTF-8) or line 266's `preregistration.trial_seed`; no clock, no
  randomness, no I/O.
- R-7 encoding: the test compares against the literal bytes
  `{"annex_b_seed":…,"beacon_randomness":…,"round":N}`; all three inputs validated first.
- Annex B §2.4: independent `json.dumps` re-encoding in the test; trial order is the
  declared order (a reversed list changes the seed).
- Beacon: the module checks the fixed round (first at or after capture + 24 h, drand
  round r at genesis + (r − 1)·period), lowercase hex, and randomness = SHA-256(signature)
  locally; verified on a real quicknet vector (round 1,000,000). The BLS check is an
  injected `Verifier`; any non-`True` result or exception is a `SeedError`.
- Fail-closed: every failure is `SeedError` (a `CycleError`): the evaluation is invalid
  and no gate runs (`seed_disclosure.failure`, DESIGN §7.2).
- Records: each declared trial has one record, same order, distinct non-negative
  `trial_index`, 64-hex `hypothesis_hash`, `configuration_hash` = `screen.trial_sha256`.
- `estimator_seed` uses `screen.estimator_seed` (frozen object copy); 0 is kept (A1b).

## 5. Items left open (not blockers for this slice)

- **LG4-1 (slice 4b, before C2 signing):** the real BLS verifier. No BLS library is in
  the pinned image (`deploy/calibration/requirements.lock`) and
  `deploy/calibration/drand-verify` does not exist; adding either reopens the image
  (FE-4). Owner decision; options to be written up.
- **LG4-2 (slice 6):** `window_id`, `cycle_id`, `hypothesis_hash`, `trial_index`, the
  chain values and the capture timestamp are taken as inputs; the loader must read them
  from the signed C2, the declaration and the immutable trial records, and check
  `window_id` is the C-0 window id.
- **LG4-3 (QUESTION):** `trial_index` is required distinct within a family; whether it
  must also be distinct across families is not stated in the governing text.
- **LG4-4:** the 7-day "no verifying output" rule and the invalidation causes of
  `seed_disclosure.failure` are operational (outside the module).
- **LG4-5:** `Beacon` models unchained schemes (quicknet). A chained mainnet chain would
  also need `previous_signature` for verification; the signed chain is quicknet (FP3).

- **LG4-6 (owner decision with LG4-1):** line 266's frozen `preregistration.trial_seed`
  (R-8) cannot be imported in the image (jsonschema). Repair: `derive_seeds` takes it as an
  injected `line266` callable (like the verifier); tests inject the real frozen function;
  a non-hex result or an error is a `SeedError`; a test keeps the module free of that
  import. R-14a item 4 ("frozen functions are called, not re-implemented") is kept, but
  how the real run reaches the frozen function (add jsonschema to the image with the
  4b rebuild, or a reviewed alternative) is the owner's, together with LG4-1.

Claude/Sol status: NOT SENT.
