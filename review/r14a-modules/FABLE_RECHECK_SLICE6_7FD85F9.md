# Fable re-check of the R14S6-F-1..10 repairs (7fd85f9)

- Reviewer model: `claude-fable-5-2` (Claude Fable 5.2), as stated by the session's
  system context; Claude Code subagent, read-only on the repository, no network.
- Date: 2026-11-10. Branch `confirmation-module`, HEAD `9a74bd1`, worktree clean before
  and after.
- Diff range reviewed: `git diff a74dddf 7fd85f9` (`calibration/c2_confirmation.py`,
  `tests/unit/test_c2_confirmation_run.py`, `tests/unit/test_c2_confirmation_start.py`,
  `review/r14a-modules/ADJUDICATION_FABLE_SLICE6_3765910.md`, the last as updated in
  `9a74bd1`), and the code those lines call.
- Earlier record: `review/r14a-modules/FABLE_REVIEW_SLICE6_3765910.md`.
- This is an independent adversarial re-check. It approves nothing, closes no owner item
  and is not the Constitution section 16 human review. No frozen artifact is touched by
  the diff. No confirmation or lockbox data was read.

## 1. Commands and results

Windows 11, `.venv` Python 3.14.7, from the repository root.

| Command | Result |
|---|---|
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider tests/unit/test_c2_confirmation_run.py tests/unit/test_c2_confirmation_start.py` | 85 passed in 15.98s |
| `.venv/Scripts/ruff check src tests calibration` | All checks passed |
| `.venv/Scripts/mypy --strict --follow-imports=silent calibration/c2_confirmation.py tests/unit/test_c2_confirmation_run.py tests/unit/test_c2_confirmation_start.py` | Success: no issues found in 3 source files |

Not run (low memory, as instructed): the full suite, the other confirmation suites,
`ruff format --check`, `mypy src`, `lint-imports`. The adjudication's "2729 passed, 10
skipped" is therefore not verified by this re-check.

Probes (scratch scripts outside the repository, synthetic values, fresh `python -I`
processes; mutants were executed in memory only, no repository file was written):

| Probe | Result |
|---|---|
| New tests against the a74dddf module (old source executed in place of the module) | 14 of the new run-file tests fail: 12 of the 13 malformed-record cases, the empty-reason case, the off-hour `w0` test. The `d_length` case passes on the old code |
| Mutants of the 7fd85f9 module, one clause removed each, run-file tests | Caught: `reason is not None` (d with reason), finite check, `interval != HOUR`, bar-at-its-hour, `not whole` warm-up, the two added exception classes. **Survive (all tests pass):** `digest is not None`, `len(d) != len(days)`, the `configuration_hash` check, the consecutive-days check, the id-string loop, `not raw_days` |
| Import `calibration.c2_confirmation` alone | neither listed module loaded; `aqt`, `aqt.core`, `aqt.core.ledger`, `aqt.data.manifest` are loaded (the recorded launch-route residual) |
| `load_line266` (both sources) with `aqt.core.paths` set to `None` in `sys.modules` | refused |
| `load_line266` twice in one process | second call refused, `_TRIAL_SEED` left `None` |
| A listed module imported, then deleted from `sys.modules`, then `load_line266` (both sources) | loads; `trial_seed` and its `REPOSITORY_ROOT` come from the verified bytes (`from aqt.core.paths import ...` resolves through `sys.modules`); the stale `aqt.core.paths` attribute on the parent package is the old module but nothing in line 266 reads it |
| `import aqt.core.preregistration`, then `load_line266({})` | **loads; `_TRIAL_SEED` is the preloaded, unverified function** (R14S6R-F-3) |
| `import aqt.core.paths`, then `load_line266({preregistration only})` | **loads; the verified preregistration uses the preloaded, unverified paths** (R14S6R-F-3) |
| `load_line266` with an extra unlisted name in `sources` (`evil` -> the paths file) | loads; `evil` stays in `sys.modules` (R14S6R-F-3) |
| `completed_entry`: `-0.0`, a subnormal, the largest float64, days at 05:00, a dict subclass | accepted (correct) |
| `completed_entry`: 34 malformed forms (types, unhashable values, non-ASCII digits, trailing space, upper-case hashes, tuples for lists, duplicate, reversed and gapped days, inf) | all `CycleError` |
| `completed_entry` with days ending `9999-12-31T00:00:00Z` | **`OverflowError` escapes** (R14S6R-F-1) |
| `completed_entry` with one day; with a whitespace-only `reason` or `cycle_id` | accepted. `trial_result` cannot write a one-day record (`baseline_d` needs 48 hours or more); still one byte form per record, so no finding |
| `trial_path` with `window_hours` `-1`, `50.0`, `True`; with a naive `w0` | first three pass the check; the naive `w0` raises `TypeError` (R14S6R-F-4) |

## 2. Verdict

**ACCEPT WITH NOTES.**

- F-1 is closed on the only production route. `start` builds `sources` from
  `LINE266_MODULES` (`line266_sources`), so both names are always present and a preloaded
  one refuses. A `None` entry, a second call and a mid-window import all refuse. The hole
  remains only for a caller that passes `load_line266` a mapping that is not the listed
  set (R14S6R-F-3); no such caller exists.
- F-2 is exact for every form I tried except one escaping exception at the date range's
  end (R14S6R-F-1). No valid `trial_result` record is refused: `baseline_d` already
  refuses a window under 48 hours or not a multiple of 24 before any record is written,
  and `-0.0` and subnormals pass.
- F-6 and F-7 repairs are correct and their tests fail without the code they cover.
- The F-2 test is weaker than the repair: six of its clauses can be deleted with every
  test still passing (R14S6R-F-2).

None of the notes blocks the 6b design rev 2. R14S6R-F-1 to F-3 should be repaired before
anything consumes these functions.

## 3. Findings

### R14S6R-F-1 — NON-BLOCKING — `completed_entry` lets `OverflowError` escape

- Where: `calibration/c2_confirmation.py:2868` (`days[-1] + DAY`).
- Scenario: a record whose last day is `9999-12-31T00:00:00Z` parses, round-trips and
  then overflows in `days[-1] + DAY`. The docstring and the adjudication say any breach
  is a `CycleError`; a rev-2 look that catches `CycleError` to refuse the evaluation
  would crash instead. Reproduced with one day and with two days.
- Repair: compute `days[-1] + DAY` inside the existing `try` and add `OverflowError` to
  its `except`; one test case.

### R14S6R-F-2 — NON-BLOCKING (tests) — six clauses of the F-2 repair are pinned by no test

- Where: `tests/unit/test_c2_confirmation_run.py:186-229`; clauses at
  `calibration/c2_confirmation.py:2852`, `2854`, `2857`, `2865`, `2872`, `2877`.
- Scenario: the parametrized test uses a bare `pytest.raises(cf.CycleError)`, so a case
  refused for another reason still passes. `d_length` is refused by the hash check (it
  passes on the pre-repair code too); `null_d_with_hash` also sets `reason` to null, so
  the reason clause refuses it. Removing any one of these leaves all 35 tests green:
  `digest is not None` for an unavailable run, `len(d) != len(days)`, the
  `configuration_hash` check, the consecutive-days check, the id-string loop, the
  empty-days check (without which `days[0]` raises `IndexError`).
- Repair: add `match=` per case and these cases: unavailable with a reason and a
  `d_sha256`; a shorter `d` with its own recomputed hash; an upper-case
  `configuration_hash`; a gap in the days with a matching `window_id`; an empty
  `attempt_id`; `days: []`.

### R14S6R-F-3 — NON-BLOCKING — `load_line266` does not require `sources` to be the listed modules

- Where: `calibration/c2_confirmation.py:1050-1061`.
- Scenario: the F-1 refusal only fires for names that are in `sources`. With `{}` and a
  preloaded `aqt.core.preregistration`, or with only preregistration in `sources` and a
  preloaded `aqt.core.paths`, the load succeeds on unverified code, with the gate on and
  the final check passing (both reproduced). An extra name in `sources` is executed and
  left in `sys.modules`. `start` cannot do this, so the F-1 scenario as recorded is
  closed; the function's own docstring claim is still wider than the code.
- Repair: when `sources` is given, refuse unless `list(sources)` equals the names of
  `LINE266_MODULES` in order (one line); one fresh-process test (`{}` after a preload).

### R14S6R-F-4 — NON-BLOCKING — `trial_path` checks the warm-up but not `window_hours`, and a naive `w0` raises `TypeError`

- Where: `calibration/c2_confirmation.py:2784-2789`.
- Scenario: `window_hours` of `-1`, `50.0` or `True` passes the length check when the
  sum happens to match, and a naive `w0` raises `TypeError`, not a C-T refusal.
  `baseline_d` refuses a bad window afterwards (`SealError`, re-raised by
  `trial_result`), so this fails closed; it is the same class as F-6, half repaired.
- Repair: require `window_hours` to be an `int` (not `bool`) above zero in the same
  line, and refuse a `w0` without a time zone as C-T.

### R14S6R-F-5 — NOTE — `trial_result` can write a record its own decoder now refuses

- Where: `calibration/c2_confirmation.py:2838` (and `2812-2824`).
- Scenario: `trial_result` does not check `cycle_id` or `attempt_id`, and `baseline_d`
  does not check that `d` is finite. Such a record is written without complaint and is
  refused by `completed_entry` only at the look, possibly months later, when the
  evaluation can no longer be rerun pre-look. I did not find a real input that produces
  a non-finite `d`; this is a cheap guard, not a reproduced failure.
- Repair: end `trial_result` with a `completed_entry(...)` call on what it returns, so
  an undecodable record is refused when it is made. Whether a non-finite `d` is a
  refusal or a recorded unavailability belongs with the F-5 owner question.

### R14S6R-F-6 — NOTE — the fixture change hides nothing, with two limits to record

- Where: `tests/unit/test_c2_confirmation_start.py:83-84`, `calibration/c2_confirmation.py:2710`.
- The per-test unload is consistent with the fixture's existing "each test is its own
  process" (`_START_FAILED`). It does not mask the repair: the refusal is proven in a
  real fresh process (`test_a_preloaded_line_266_module_is_refused_not_skipped`).
- Limits: (a) no in-process test shows that `start` itself refuses on a preloaded listed
  module and then stays refused; (b) `start` reports this as `line 266 did not load:
  SeedError`, so the operator does not see "was loaded before start". Both are
  suggestions, not defects. (c) Deleting the entries leaves the parent package attribute
  pointing at the old module; nothing in line 266 reads it.

## 4. Adjudication decisions

| Decision | View |
|---|---|
| F-3 deferred to rev 2 (test renamed, comment added) | Agree. The rename and comment are accurate |
| F-4 deferred to rev 2 as an owner/S4 proposal | Agree. Note for rev 2: `_TRIAL_RESULT_KEYS` now fixes the key set, so adding fields means changing the set and the schema name together; the schema is unsigned, so this costs nothing now |
| F-5 open owner question | Agree. `completed_entry`'s docstring still states `MISALIGNED_SERIES` (U_ops) as the behaviour; correct until the owner decides |
| F-8 pre-signing step | Agree. Nothing in this diff changes it |
| F-9 recorded N/A | Agree. The cited command is clean here; the 10 errors in `tests/unit/test_calibration_screen.py` remain as recorded, not silenced |
| F-10 | Agree; the record is committed (`a74dddf`) |
| "Any breach is a `CycleError`" (F-2 row) | Not quite: see R14S6R-F-1 |
| "13 cases" pin the repair (F-2 row) | Overstated: see R14S6R-F-2 |

## 5. Not checked

The full suite and the other confirmation suites; the fresh-process F-1 test against the
old code (in-memory substitution does not reach a subprocess; the original review
reproduced the old behaviour directly); Linux and the qualified image; anything in rev 2.
