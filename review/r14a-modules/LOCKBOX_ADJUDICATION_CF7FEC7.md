# Adjudication of Sol's lockbox re-check 4 (`SOL_LOCKBOX_RECHECK_CF7FEC7.md`)

- Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-02, the module's author,
  against the code at `470fc66` (module bytes of `cf7fec7`) and the cited governing text.
  Repairs are in the commit that adds this file.
- Format: `ID | Sol severity | AGREE / PARTIAL / DISAGREE | reasoning and evidence |
  disposition | validation`.

| ID | Sol | Verdict | Reasoning and evidence | Disposition | Validation |
|---|---|---|---|---|---|
| R14L4-S-1 | BLOCKER | AGREE | A time-of-check/time-of-use gap: `run_evaluation` re-read the trial from the caller's ledger and files after `record_pre_read_check`, so a change during that call reached the run. | Repaired: on entry `run_evaluation` takes one immutable snapshot (a deep copy of the ledger, `bytes` copies of every file and of the artifact) and both the check and the run use only it. | `test_ledger_swapped_after_the_check_is_not_what_runs` (Sol's probe: the run computes the checked tau 0.60 trial; with the snapshot disabled the test fails). |
| R14L4-S-2 | BLOCKER | AGREE | The startup record's id was never compared with `started.startup_check_id`, so an earlier start's PASS record could stand in for this start's failed vector check. | Repaired: a startup record whose id is not `started.startup_check_id` is treated as absent, giving `REFERENCE_VECTOR_MISMATCH` and a check record with a null startup id. That the store's copy of the record is genuine is the store's obligation (below). | `test_another_startup_record_does_not_count`. |
| R14L4-S-3 | BLOCKER | PARTIAL | Agreed: `family_seed`, the prediction artifact (with its hash) and the manifest hash are compared caller-to-caller, so coherent substitutions pass this module's check. Not agreed that the module can close this alone: Annex D §D-3.7 gives these bindings to the store. `begin_read` step 4 refuses unless the check record's identity fields, including `prediction_artifact_sha256`, equal the sealing record, and the read gate serves bars only under the cycle manifest. `family_seed_f` is verified from the beacon by the confirmation module (R-14a item 7), not here. | Repaired what the module controls: `image_digest` is no longer a parameter of `run_evaluation` (it is the image `start()` verified against the signed row). The store's bindings are now written on the `Store` protocol as obligations its build must implement and test: sealing-record match at `begin_read`, artifact and ledger as the sealed records, bars only under the request's manifest, `family_seed` from the record the confirmation module verified. **Open before signing:** how the lockbox side obtains an authenticated `family_seed_f` (the sealing record, written after the confirmation module's item-7 verification, is the recommended source; the S4 text must say so). | Existing pre-read tests; the obligations are for the store build's tests. |

Sol's other observations are accepted: R14L3-S-1 is closed for a `Started` returned by
`start()`; the hand-built `Started` residual is correctly the launch route's; no further
regression in the forecast, adapter, assembly or chain paths.

**Open before signing C2 (not closable in this module):** the launch route; acceptance
provenance (owner decision); the reference vectors on the qualified image; the S4 format
bindings; and, new here, the store build's §D-3.7 obligations listed on `Store` and the
source of an authenticated `family_seed_f` on the lockbox side.

Validation (Windows, repo `.venv`, Python 3.14.7): lockbox tests and the five fast
calibration-tree test files 273 passed; `test_calibration_rundef` in the commit message;
ruff, ruff format, mypy strict per file and lint-imports (7 kept) clean.

Rundef completion (2026-11-03, on 2f062b7, node paused): `.venv\Scripts\python.exe -m
pytest -q -p no:cacheprovider tests/unit/test_calibration_rundef.py` -> 76 passed in
668.23s. With this, validation of the R14L4 repairs is complete.
