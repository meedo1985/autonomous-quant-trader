# Local gate: confirmation slice 5a (sealing and the A4 copy)

- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-09, applying `task-gate-review`,
  `scientific-reproducibility-review`, `quant-code-review`. Self-review by the author; the
  independent review is Sol (`SLICE5A_PROMPT_SOL.md`).
- Scope: DESIGN §5.3 (sealing), §5.5 (Q-D1); Annex D §D-1.7 (statuses), §D-3.5 (artifact
  and sealing, A7 steps 1-4), from `origin/freeze-sheet` `ANNEX_D_LOCKBOX.md`. C-14
  (DESIGN §5.4, Annex C C-14) is split out as **slice 5b**: it needs model refits over 28
  purged and embargoed splits and is large enough for its own review.
- Finding IDs: LG5-n. **LOCAL GATE: PASS** (no open blocker), items in §5.

## 1. Changed files

- `calibration/c2_confirmation.py` (appended; new stdlib imports `random`, `struct`; `cj`
  from `calibration.seeds`): the A4 copy (`M_DAYS`, `ATTEMPTS`, `QUANTILE`, `PURPOSE`,
  `ASSET`, `COST`, `SEED_SOURCE`, `LockboxError`, `hexf`, `_time`, `window_id`,
  `seed_material`, `replicate_indices`, `Forecast`, `forecast`, `_floats_sha256`), extracted
  from `c2_lockbox.py` by script (AST source segments), not retyped; `SealError`,
  `baseline_d`, `prediction_artifact`, `seal_family`, `sealing_record`.
- `tests/unit/test_c2_confirmation_seal.py` (new, 33 tests).

## 2. Validation (Windows 11, repo `.venv`, Python 3.14)

| Command | Result |
|---|---|
| `pytest tests/unit/test_c2_confirmation_seal.py` | 33 passed |
| `pytest tests/unit/test_c2_confirmation*.py tests/unit/test_c2_lockbox*.py tests/unit/test_d19_deploy.py` | 295 passed (engine import test still `['numpy']`) |
| `ruff format --check .`, `ruff check .` | clean |
| `mypy src` | no issues (56 files) |
| `mypy --strict` module + new test | 10 errors, all in the imported `test_calibration_screen.py`, pre-existing |
| `lint-imports` | 7 kept, 0 broken |

## 3. Frozen artifacts

None touched. The lockbox module is read (copied from), not changed.

## 4. Self-review

- Q-D1: every copied function and class has `inspect.getsource` equal to the lockbox's; the
  constants are equal; the copy's forecast on the lockbox reference input equals the
  lockbox's (ψ, b, all 2,000 index sequences, replicates, q).
- The artifact is checked by the **lockbox's own** `_check_shape`, `_check_identity` and
  `_check_p4` with a matching request and signed values: shape, every identity field
  (seed_hex = the R-13 trial seed, policy, estimator seed, stream constants, code) and P-4.
- A7 step 2: d must hash to the pre-look `d_sha256`, else `SealError` and status (d).
- `baseline_d` builds the pair as `screen_gates`' baseline run does (cost 1.0, delay 0, lag
  0, BTC symbol 0, both legs flat at w0, terminal row from the path) and is compared with
  an independent write-out of the same frozen blocks in the test.
- Statuses: no nominee (b); a gate UNAVAILABLE (d), which governs over a FAIL; FAILED (c);
  PROCEEDS: sealed (a) or any failure (d) with its reason; unknown outcome refused.

## 5. Items left open (not blockers for this slice)

- **LG5-1 [DESIGN] sealing record layout:** `{schema, cycle_id, evaluation_record_sha256,
  beacon_round, families{f: {status, nominee_trial_id, reason, family_seed, trial_index,
  seed_l266, prediction_artifact_sha256}}}`; Annex D names only the statuses and the
  artifact hash. It carries the seeds the lockbox request takes (R14L5-S-2, SV1-S-6). To be
  bound in the S4 text.
- **LG5-2 [DESIGN] `evaluation_record_sha256`:** the artifact's `source` field names the C2
  evaluation record, which itself holds the artifact and sealing record (DESIGN §7.2).
  Reading: it is the hash of the record of steps 1-6 (before sealing), taken as an input
  here; slice 6 writes that record first.
- **LG5-3 [DESIGN] d hash encoding:** big-endian float64 concatenation (the lockbox's
  `_floats_sha256`, also its reference-vector `d_sha256`); the pre-look `d_sha256` of
  step 4 must use the same encoding (slice 6).
- **LG5-4:** the stream and source window is the C-0 window id `["<w0>","<w1>"]`,
  refused unless it equals `window_id(w0, w0 + window)`.
- **LG5-5:** "any failure gives status (d)" is implemented as catching every exception
  while sealing an ELIGIBLE nominee, recorded as `SEAL_FAILED:<code or type>`.
- **LG5-6 (slice 5b):** C-14 CPCV report.
- **LG5-7 (slice 6):** wiring: the nominee's trial object, record, path, `d_sha256` and
  seeds come from the governing records; the sealing record is written before any lockbox
  read and the lockbox request is filled from it.

Claude/Sol status: prompt `SLICE5A_PROMPT_SOL.md`, sent with this commit.
