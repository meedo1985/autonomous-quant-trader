# Adjudication of the Sol re-review of the held-out runner at fab43e8

Review record: `review/d19-engine/SOL6_HELDOUT_REREVIEW_FAB43E8.md`
(gpt-6-sol, CHANGES REQUESTED). Adjudicated by Claude Opus 5.5 (the
implementer).

| ID | Sol severity | Decision | Reasoning and evidence | Disposition | Validation |
|---|---|---|---|---|---|
| HO2-R1 | blocking | AGREE | `gate` built the allocation from the status rows present, and `tally` treated a missing row as not qualifying. A `choices.json` without one cell's row therefore skipped that cell's tests silently. | `gate` refuses unless `choices.json` "cells" names exactly the manifest's units (`_units` of every cell, QJ families included), each with a status `choices` can write (`qualifying`, `demoted_availability`, `demoted_cap`). HO-2 restated. | `test_gate_refuses`: a missing row, and an unknown status. |
| HO2-R2 | blocking | AGREE | The record's bytes were fsynced, but its new directories and the link were not, so a crash after chunks were written could lose the only copy of the beacon inputs. | `attempt_record` syncs each newly created directory's entry, and the namespace directory after the link, with the project's `chunks._sync_dir`. This happens before any worker starts. On Windows, `_sync_dir` is a no-op, as for chunks (FA-4). HO-3 restated. | `test_the_attempt_record_is_durable_before_any_chunk`. |

Readings after this round: HO-1 accepted by the reviewer; HO-2 and HO-3
repaired as above; HO-4 an external procedure, unverified by this code.

Nothing was left unrepaired.

Checks: `tests/unit/test_calibration_heldout.py` 20 passed; `ruff format`,
`ruff check` and `mypy` clean on both files. A real `certify` in a fresh
process passed the gate and refused at "no attempt record".
