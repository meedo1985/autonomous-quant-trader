# Adjudication of the final Fable review of the 6b build at 24f0c95

- Review record: `FABLE_FINAL_BUILD_SLICE6B_24F0C95.md` (committed `95e5574`, verbatim),
  reviewer Claude Fable 5.2 (`claude-fable-5-2`), verdict GO WITH CONDITIONS, findings
  R14B6F-F-1..11.
- Builder and adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-16. The
  adjudicator is the builder: these are the builder's decisions, not an independent check.
  Nothing here is approved: owner items stay owner items; §16 still needs the owner's PR
  review.

## Decisions

| ID | Decision | What was done |
|---|---|---|
| F-1 (major) | Accepted, repaired (follow-up commit) | `tests/unit/test_c2_confirmation_joined.py`: real `prepare` (real `signed_c2`, `headers_check` on public mainnet headers 0-5, `check_capture_record`, `qualification_checks`, `install_code`, `derive_seeds` with quicknet round 1,000,000), real `evaluate_trial` for both declared trials (real `run_trial`, `check_read`, `trial_path`, `trial_result`) and real `evaluate_look` (`open_look`, `nominate`, `family_gates`, `seal_family`). Asserts: every result entry is accepted at the look, `trials{id: sha256(cj(payload))}`, two status (a) artifacts whose `source.d_sha256` equals the trial stage's pre-look value, the exact persisted bytes, and the closing entry's two hashes. Stated stand-ins: `nominee_gates` and `cpcv_report` (as F-1 allows), `qobj.read`, `benchmark_spec_sha256` patched to the signed value (spec file absent, B5B-D-1), a hand-built `Started`, a `persist` recorder, method V marked verified. The window is T = 30 days (signed g row). The synthetic signal was chosen so that the real G-9 passes. Mutation check: a one-day `window_id` shift in `Inputs.expected` and a 24 h shorter warm-up in the look's cut each fail the test. The merge block from F-1 is lifted once the Astra check passes. |
| F-2 (minor) | Accepted, repaired | New `qualification_checks` (report re-read, `z_crit` and `family_block_rule` equality, classifier bounds for every family) is called by `prepare` before code install and seeds, and again by `open_look` (which now takes its bounds from it, outside the look lock). Both entry points now refuse before any read. **Owner item B6F-D-1**: this is stricter than rev 16 §2 (which runs these at the look only); it reads nothing new and fails closed. |
| F-3 (minor) | Accepted, repaired | `_code_identity_ok` (shared with `completed_entry`) checks in `prepare` the form of the identity fields that come from `start` and the declaration (three 64-hex hashes, 40-hex `engine_commit`, non-empty `image_digest`). The seed fields are produced by `derive_seeds` itself and are not re-checked here. |
| F-4 (minor) | Accepted, repaired | `_starts` validates every start payload as `attempt_counts` does and turns `AttemptError`/`TypeError`/`AttributeError` into `CycleError`; used by `cycle_ledger` and `open_look`. `family_attempts` wraps `attempt_counts` the same way. `of_cycle` returns False for a non-mapping payload and treats a non-string `attempt_id` as not ours (the readers then refuse the entry). |
| F-5 (minor) | Accepted, repaired | The static guard's limits are now stated in its docstring. Behavioural test `test_cpcv_reaches_nothing_but_its_own_field` (in the joined test file): the same ledger, copied, looked at twice with `_now` fixed and two different `cpcv_report` recorders; the evaluation, sealing and artifacts are equal once `cpcv`, `evaluation_record_sha256` and `prediction_artifact_sha256` are left out. |
| F-6 (minor) | Accepted, repaired | Any exception from `cpcv_report` in `evaluate_families` is recorded as `{"role": "diagnostic_only", "status": "UNAVAILABLE", "reason": "C14_ERROR:<type>"}` instead of aborting the look (§9: nothing reads the report). The static C-14 guard allows that one dict assignment. **Owner item B6F-D-2** (design choice, Fable's proposal). |
| F-7 (minor) | Accepted, partly repaired | Repaired: `CAPTURE_PAYLOAD_MAX = 1024` bytes, checked before `gzip.decompress`. Recorded as **pre-signing items** (not code): (a) a `mempool.space` known-answer capture; (b) an owner/SPEC rule for an earliest capture the module cannot decode (`br`, `zstd`, a trailing newline), since such a refusal is permanent. |
| F-8 (minor) | Accepted, docstring | `Store` now carries a "Launch route" obligation: each process calls `start` itself and passes that call's `Started`; never hand-built, kept or reused. No 6b wrapper (`start` is pinned; a wrapper adds code for a rule the runner must keep anyway). |
| F-9 (info) | Accepted, wording | DSR nominees are column numbers in ascending trial-id order; the record does not carry the order. Goes to the deviation list as an S4 wording / §10 field item. No code change. |
| F-10 (info) | Accepted, owner wording | Status (d) `SEAL_FAILED` has no P18-7 cause. Owner wording item (U_ops or U_proc). No code change. |
| F-11 (info) | Accepted | One deviation list from rev 16 will be written before the owner's PR review, including a pre-signing step that runs `signed_c2` on the candidate C2 bytes (B4-A-1 consequence). |

No finding was rejected. Fable's view on B1-D-1 and B1-D-2 (accept both) is noted; both
stay owner decisions for the PR review, as do B6F-D-1 and B6F-D-2 above.

Fable's note on G-13: `specs/CANONICAL_BENCHMARKS_v1.1.md` is absent at this checkout, so
every nominee would be `NO_RESULT` (U_ops) today. Unchanged (owner decision B5B-D-1); the
file comes through the Constitution process, not this build.

## Tests added

- `test_c2_confirmation_prepare.py`: `test_the_qualification_checks_run_in_prepare_before_the_code_and_seeds` (F-2, real `prepare` in front of `evaluate_trial`, no read, no ledger), `test_non_canonical_identity_fields_refuse_before_any_read` (F-3, four cases).
- `test_c2_confirmation_look.py`: `test_a_malformed_start_is_a_cycle_error` (F-4, two cases), `test_an_outcome_or_result_with_an_unhashable_attempt_id_is_not_ours` (F-4).
- `test_c2_confirmation_families.py`: `test_an_error_in_the_diagnostic_does_not_abort_the_look` (F-6).
- `test_c2_confirmation_inputs.py`: `test_capture_payload_longer_than_the_cap_is_refused_before_decoding` (F-7).
- Changed: `test_c2_confirmation_open.py` lock test now holds the first opener inside `look_allowed` (bounds moved out of the lock); `test_c2_confirmation_prepare.py` `calls` fixture records `qualification_checks`; `test_c2_confirmation_cpcv.py` guard allows the F-6 fallback dict.

## Checks

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest tests/unit -k c2_confirmation -q -p no:cacheprovider` | 603 passed, 2205 deselected (250 s) |
| `.venv/Scripts/ruff.exe check calibration tests/unit/` | All checks passed |
| `.venv/Scripts/ruff.exe format --check` on the changed files | formatted |
| `.venv/Scripts/mypy.exe calibration/c2_confirmation.py` | no issues |
| `.venv/Scripts/lint-imports.exe` | 7 kept, 0 broken |

F-1 and F-5 follow-up (`test_c2_confirmation_joined.py`, 2026-11-17, Claude Opus 5.5):

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest tests/unit -k c2_confirmation -q -p no:cacheprovider` | 605 passed, 2205 deselected (266 s) |
| `.venv/Scripts/ruff.exe check calibration tests/unit/` | All checks passed |
| `.venv/Scripts/ruff.exe format --check tests/unit/test_c2_confirmation_joined.py` | already formatted |
| `.venv/Scripts/mypy.exe calibration/c2_confirmation.py` | no issues (module unchanged) |
| `.venv/Scripts/lint-imports.exe` | 7 kept, 0 broken |

These repairs have had no different-model review yet. The F-1 commit and these repairs go
to one short Astra check (per review routing) before the owner's PR review.
