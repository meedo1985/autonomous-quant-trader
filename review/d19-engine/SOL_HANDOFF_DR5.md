# Handoff to Codex (GPT-6 Sol): finish the DR5 repairs of the D-19 run driver

Written by Claude (Opus 5.5) on 2026-10-05 at the owner's request ("let the sol
make the next"). Follow AGENTS.md. Branch `d19-calibration-engine`.

## State

- Last pushed commit: `25f6b31` (record of GPT-6 Sol re-review 4,
  `SOL6_DRIVER_REREVIEW_C71554B.md`: DR5-1 blocker, DR5-2 non-blocking).
- **Uncommitted in the working tree** (Claude's repairs, not yet validated in full):
  - `scripts/d19_run.py`: `WORKERS = 2` constant (§13 rev 7g item 6); the
    `--workers` option is removed (DR5-1).
  - `tests/unit/test_calibration_rundef.py`: `--workers` removed from driver
    calls; new test `test_the_parent_hands_its_definition_hash_to_every_worker`
    (DR5-1 pool size 2, DR5-2 parent-to-worker hash propagation with a
    definition replaced after the parent's gate).
- Already run on the uncommitted tree: the calibration tests (81 passed),
  `ruff check .` clean, `mypy calibration src` clean. The rest of the suite was
  stopped by the owner before it finished.

## Steps

1. Run the mandatory checks. The laptop is short of memory, so run the suite
   in two parts:
   - `.venv/Scripts/python.exe -m pytest tests/unit/test_calibration_rundef.py tests/unit/test_calibration_chunks.py tests/unit/test_calibration_engine.py -q -p no:cacheprovider`
   - `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --ignore=tests/unit/test_calibration_rundef.py --ignore=tests/unit/test_calibration_chunks.py --ignore=tests/unit/test_calibration_engine.py`
   - `.venv/Scripts/python.exe -m ruff check .` and `.venv/Scripts/python.exe -m ruff format --check .`
   - `.venv/Scripts/python.exe -m mypy calibration src`
   - `.venv/Scripts/lint-imports.exe`
   - `pwsh -NoProfile -File review/task6/verify_frozen.ps1` (pwsh is at
     `C:\Users\PMP Cordination\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`)
2. If any check fails, stop and report; do not commit.
3. If all pass, write `review/d19-engine/ADJUDICATION_DRIVER_C71554B.md` in the
   style of `ADJUDICATION_DRIVER_4A7FCB2.md`: DR5-1 AGREE repaired (WORKERS = 2,
   option removed; test checks pool size 2); DR5-2 AGREE repaired (the new test);
   requirements still carried FE-4, FE-7; a table of the exact commands and
   results from step 1. Commit the two changed files and the adjudication
   together, ending the message with your own attribution, and push.
4. Then review the whole driver (`git diff 96a223e HEAD -- calibration scripts tests`)
   as an independent reviewer of Claude's code, using
   `review/d19-engine/DRIVER_REREVIEW_PROMPT_4.md` as the checklist (findings
   DR6-1, ...). Write the verdict, your model metadata, and every finding with
   its ID to `review/d19-engine/SOL6_DRIVER_REREVIEW_<short HEAD>.md` and commit
   it. ACCEPT means the threshold-namespace driver is accepted for pilot runs
   only (qualification stays refused; FE-4 and FE-7 stay carried).

Do not run any calibration, do not touch the server, frozen artifacts,
`src/aqt`, or any other branch.
