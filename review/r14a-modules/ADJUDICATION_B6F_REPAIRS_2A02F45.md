# Adjudication of the Astra short check of the Fable 6b repairs at 2a02f45

- Review record: `ASTRA_REVIEW_B6F_REPAIRS_2A02F45.md` (committed `f81056a`, verbatim),
  Codex CLI `gpt-6-astra` (log header), verdict FIX, findings B6FR-A-1..3.
- Builder and adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-17. The
  adjudicator is the builder: these are the builder's decisions, not an independent check.
  Nothing here is approved; §16 still needs the owner's PR review.

## Decisions

| ID | Decision | What was done |
|---|---|---|
| B6FR-A-1 (major) | Accepted, repaired | Confirmed: `look_allowed` refuses a look clock before the last ledger entry, and the fixture fixed `_now` at 2026-11-17 12:00Z while the attempts and results carry the real clock, so both joined tests would fail from that instant on. Repair: `World.run_trials` fixes `_now` at one second after its last append (whole seconds). One instant still serves both F-5 looks; the ledger itself keeps its real clock and hashing (Astra's alternative, freezing the ledger clock, is not needed; the ledger allows non-monotonic timestamps, so the closing entry's real time cannot refuse anything). |
| B6FR-A-2 (minor) | Accepted, repaired | `family_attempts`: an outcome whose payload is not a dict or whose `attempt_id` is not a string is a `CycleError` ("outcome entry i has no attempt id"), not a `KeyError`/`TypeError`. `family_ledger`: a result entry whose `attempt_id` is not a string is a `CycleError` before the other-cycle membership test. Fail-closed behaviour is unchanged (the old exceptions also stopped the reader); only the refusal type is now the promised one. New test `test_a_malformed_outcome_or_result_id_is_refused_by_the_readers` (3 cases: outcome `attempt_id=[]`, outcome without `attempt_id`, other-cycle result `attempt_id=[]`) fails on the pre-repair module (3 failed) and passes after. |
| B6FR-A-3 (minor) | Accepted, repaired | `DEVIATIONS_SLICE6B_REV16.md`: B6F-D-1 now records that `open_look` computes the classifier bounds outside the lock, before `look_allowed`, superseding reading B5A-R-2 (new row in §2); §4 now says the merge needs both these repairs accepted and the owner's PR review. |

No finding was rejected. Astra confirmed the three owner acceptances (`3ca103a`, `73bbc5f`,
`24f0c95`) and found the joined test's seams and stand-ins sound.

Astra could not run pytest in its read-only sandbox (no writable temp directory); the
builder's run is below.

## Checks

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest tests/unit -k c2_confirmation -q -p no:cacheprovider` | 608 passed, 2205 deselected (300 s) |
| `.venv/Scripts/ruff.exe check calibration tests/unit/` | All checks passed |
| `.venv/Scripts/ruff.exe format --check` on the three changed code/test files | already formatted |
| `.venv/Scripts/mypy.exe calibration/c2_confirmation.py` | no issues |
| `.venv/Scripts/lint-imports.exe` | 7 kept, 0 broken |

The two module changes are small refusals of the same kind as the F-4 repair. Per review
routing they go to the owner's PR review with this record; no further AI round is planned
unless the owner asks for one.
