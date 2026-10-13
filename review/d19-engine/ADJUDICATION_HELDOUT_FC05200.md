# Adjudication of the Sol review of the held-out runner at fc05200

Review record: `review/d19-engine/SOL6_HELDOUT_REVIEW_FC05200.md` (gpt-6-sol,
CHANGES REQUESTED). Adjudicated by Claude Opus 5.5 (the implementer); the
re-review decides whether the repairs hold.

| ID | Sol severity | Decision | Reasoning and evidence | Disposition | Validation |
|---|---|---|---|---|---|
| HO-R1 | blocking | AGREE | Chunks were bound to the object hash only, and `attempt_record` was check-then-write with one shared temporary name. A lost `attempt.json` let a resume with another anchor extend the chain unnoticed, and `certify` never read the record. | Every chunk's binding is now `SHA256(cj({anchor, qualification_object_sha256}))` (`binding`). The record is written to a unique temporary file and published by `os.link`, which fails if the record exists (atomic, complete). `certify` rebuilds the anchor from the record (`recorded_anchor`: the inputs must give the recorded anchor, and the record must name the posted object) and verifies chains under that binding. HO-3 restated. | `test_run_then_certify`: with the record deleted, a run with another round is refused at "binding does not match". `test_certify_rebuilds_the_anchor_from_the_attempt_record`, `test_certify_refuses_an_incomplete_chain` ("no attempt record"). |
| HO-R2 | blocking | AGREE | `tally` treated every test without replications as "not run", and the gate never rebuilt the test manifest, so a short or reduced manifest, or a missing qualifying unit, could still give `accepted: true`. | The gate refuses unless `tests` equals `choices.test_manifest` of the whole cell manifest and `m` its length. `tally` runs a test iff its units are qualifying (by `choices.json` status), and refuses a qualifying unit without replications, or a joint test of a half-qualifying cell. `tally` now runs inside the refusal handler, so no report is written. HO-2 restated. | `test_gate_refuses` (`m`, `tests`); `test_tally_counts_each_test_and_skips_demoted_cells`; `test_tally_accepts_when_every_run_test_is_within`. |

Readings: HO-1 was left unconfirmed because the reviewer's shell failed. The
re-review should read `calibration/mapping.py` `check_engine`/`check_runtime`
and `calibration/rundef.py` `bytecode_problem`. HO-2 and HO-3 are amended as
above. HO-4 is accepted as an external procedure: the attempt procedure must
check the drand signature, the T_Qn + 24h round rule, the O-6a freeze read
and the DF5-2 records before `run`.

Nothing was left unrepaired.

Checks after the repairs: `tests/unit/test_calibration_heldout.py` 17 passed;
`ruff format --check`, `ruff check` and `mypy` clean on both files. A real
`certify` in a fresh process, against an object holding this runner, passed
the gate and refused at "no attempt record".
