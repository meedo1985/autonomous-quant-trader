# Adjudication of Sol's lockbox review (`SOL_LOCKBOX_REVIEW_6047BC1.md`)

- Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-02, the module's author.
  Each finding was checked against the code at `6047bc1` and the cited governing text
  before repair. Repairs are in the commit that adds this file.
- Format: `ID | Sol severity | AGREE / PARTIAL / DISAGREE | reasoning and evidence |
  disposition | validation`.

| ID | Sol | Verdict | Reasoning and evidence | Disposition | Validation |
|---|---|---|---|---|---|
| R14L-S-1 | BLOCKER | AGREE | `_check_identity` derived `seed_l266` from the artifact's own `nominee.trial_index`, so an artifact sealed with a wrong but self-consistent index passed. Annex D §D-3.2: `trial_index` "is the one in the nominee's C2 trial record". | Repaired: `Request.trial_index` comes from the immutable C2 trial record; the artifact's index must equal it and the seed is derived from the record's index. | `test_coherent_wrong_trial_index_refused` (index 4 with both seeds and the hash recomputed → `IDENTITY_MISMATCH`). |
| R14L-S-2 | BLOCKER | AGREE | `run_evaluation` took a caller's `Signed` and could reach `open_read` with no chain or code check. | Repaired: new `start()` runs `verify_chain` over the two module files on disk, reads every signed value from the verified protocol bytes (new **[DESIGN]** rows `engine_commit`, `screen_object_sha256`, `qualification_object_sha256`, `image_digest`), runs `verify_code`, checks the object's engine commit is the signed one, then records startup; any failure raises before any store call. `run_evaluation` now takes only the `Started` that `start()` returns. **Not resolved:** that the *running* bytes are those files needs the launch route (LG-8, R14D3-S-2, R14D4-A-3), which this module cannot provide; a Python caller can still construct `Started` by hand. Open pre-signing item. | `test_start_reads_signed_values_from_the_verified_protocol`, `test_start_refuses_before_any_append` (engine mismatch; module file swapped). |
| R14L-S-3 | BLOCKER | PARTIAL | Agreed: the record was only hashed, never related to the post. Not agreed: that the module can itself verify node-backed acceptance. O-6a SPEC §4 needs a fully validating node, `scanblocks` over the address and two explorers; that is the governance procedure and cannot run inside the evaluation. | Repaired what the module can do: `check_acceptance` requires a canonical **[DESIGN]** `aqt.c2.post_acceptance.v1` record naming this exact raw transaction and its txid, `first_post: true` and at least 6 confirmations, and logs the record's hash. Residual, disclosed in code: the record's truth rests on the O-6a §4 procedure. Whether R-14a item 2's "verifies ... the accepted C2 post" is met by this is a question for the owner's §16 review. | `test_acceptance_record_must_accept_this_post` (6 cases), `test_acceptance_record_must_be_canonical`. |
| R14L-S-4 | BLOCKER | AGREE | `verify_code` checked only `len(modules) == 2`. | Repaired: the key set must be exactly `MODULE_PATHS` (`calibration/c2_lockbox.py`, `calibration/c2_confirmation.py`, DESIGN §5-§6); in `start()` the bytes are the same ones `verify_chain` checked against the signed rows. | `test_verify_code_extends_reviewed_by_exactly_the_modules` (two files, wrong second name → refused). |
| R14L-S-5 | BLOCKER | AGREE | `files.get(item["sha256"])` raised `TypeError` for an unhashable value before any reason code; reproduced by reading the code path. | Repaired: kind, sha256 (64 lowercase hex) and size (int, not bool) are type-checked before any lookup; a malformed item is `IDENTITY_MISMATCH`. | `test_malformed_ledger_item_is_a_reason_code` (5 cases). |
| R14L-S-6 | BLOCKER | AGREE | Same as LG-6: `FROZEN_VECTORS_SHA256 = None`, so startup cannot pass. | Not repairable here: the value must be computed on the qualified image. Open pre-signing item; the module cannot be signed before it. | — |
| R14L-S-7 | NON-BLOCKING | AGREE | The vector test compared two computations; the Ridge test never observed the seed. | Repaired: fixed literal vectors for the seed material and index draws (integer and stdlib-random only, so platform-independent); a spy on `screen.build_model` shows all 32 fits (16 refits × 2 assets) receive the estimator seed. The full A5 hash stays with S-6. | `test_generator_pinned_vectors`; `test_model_trial_refits_with_estimator_seed`. |

**Local blocker after repair:** none in the code. Open before signing (not repairable in
this module): R14L-S-6 / LG-6 (vectors on the qualified image), R14L-S-2's launch-route
residual / LG-8, R14L-S-3's acceptance-truth residual (owner question), and the
**[DESIGN]** format bindings (LG-7, now also the four `SIGNED_ROWS` and the acceptance
record schema) to be stated in the S4 text.

**Re-review:** the repairs change the module; R-14a item 1's independent review should
re-check them (R14L2-S-n) before the owner's §16 PR review.

Validation of the repairs (Windows, repo `.venv`, Python 3.14.7): lockbox tests 105
passed; calibration-tree tests 150 passed plus `test_calibration_rundef` (result in the
commit message); ruff, ruff format, mypy strict (each file) and lint-imports (7 kept)
clean.
