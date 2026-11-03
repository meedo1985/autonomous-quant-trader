# Adjudication of Sol's lockbox re-check (`SOL_LOCKBOX_RECHECK_471144C.md`)

- Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-02, the module's author,
  against the code at `471144c` and the cited governing text. Repairs are in the commit
  that adds this file.
- Format: `ID | Sol severity | AGREE / PARTIAL / DISAGREE | reasoning and evidence |
  disposition | validation`.

| ID | Sol | Verdict | Reasoning and evidence | Disposition | Validation |
|---|---|---|---|---|---|
| R14L2-S-1 | BLOCKER | AGREE | The R14L-S-1 repair moved the trust to `Request.trial_index`, which is still the caller's. The only trial record the start chain has verified is the posted declaration. | Repaired: `Started` now carries the verified declaration, and `pre_read_check` refuses (`IDENTITY_MISMATCH`) unless the declaration's single entry for the nominee has the request's cycle, family, hypothesis hash, configuration hash and `trial_index`. **[DESIGN]**, to be bound in the S4 text: the declaration has top-level `cycle_id` and `trials` of `{family, trial_id, hypothesis_hash, configuration_hash, trial_index}`. Annex B §2.4 lists `{trial_id, hypothesis_hash, configuration_hash}`; `trial_index` and `family` per entry are additions the S4 text must state. | `test_request_and_artifact_coherently_wrong_index_refused` (Sol's scenario; shown to return `PASS` with the check disabled and `IDENTITY_MISMATCH` with it); `test_declared_entry_binds_the_nominee` (7 cases). |
| R14L2-S-2 | BLOCKER | PARTIAL | Agreed: `block_hash: null` and a non-integer height passed. Agreed also that the record's assertions can be fabricated by whoever supplies it. Not repairable in the module: who vouches for the record and how its provenance is checked before `start()` is a governance design (O-6a SPEC §4 runs on the verifier's own node). | Repaired the field checks: `block_hash` 64 lowercase hex, `height` a positive int (not bool). **Open, owner decision before signing:** an authoritative acceptance-evidence handoff (for example a record hash fixed by a governance step the evaluation can verify), to be specified and reviewed under §16. Docstring states this. | `test_acceptance_record_must_accept_this_post` (now 11 cases). |
| R14L2-S-3 | NON-BLOCKING | AGREE | `start()` passed the caller's `image_digest` to `record_startup` unchecked. | Repaired: `start()` refuses before any append unless the digest equals the signed one. How the actual image digest is measured belongs to the launch route (LG-8). | `test_start_refuses_a_running_image_that_is_not_signed`. |

**Status of earlier findings** (from Sol's re-check, which this adjudication accepts):
R14L-S-4, S-5 and S-7 closed; S-6 open before signing; S-2's start chain sound for the
files on disk, with the launch route open; S-1 now closed by R14L2-S-1's repair; S-3
partially repaired, residual as R14L2-S-2.

**Open before signing C2 (none can be closed inside this module):**
1. Launch route (LG-8, R14D3-S-2, R14D4-A-3): that the running bytes are the verified
   files, how the image digest is measured, and that `Started` comes only from `start()`.
2. Acceptance-evidence provenance (R14L2-S-2): owner decision.
3. Reference vectors on the qualified image (LG-6, R14L-S-6).
4. **[DESIGN]** format bindings in the S4 text: the module, `outpoint_F` and four signed
   rows; the acceptance record schema; the declaration layout above; A1a item kinds.

Validation (Windows, repo `.venv`, Python 3.14.7): lockbox tests and the five fast
calibration-tree test files 269 passed; `test_calibration_rundef` in the commit message;
ruff, ruff format, mypy strict per file and lint-imports (7 kept) clean.
