# Fable adversarial review: slice 6b part 1 (cc197be) and slice 6a final repair (025ba5c), at HEAD 3765910

- Reviewer model: `claude-fable-5-2` (Claude Fable 5.2), as stated by the session's
  system context; run as a Claude Code subagent, read-only on the repository, no network.
- Date: 2026-11-10. Branch `confirmation-module`, HEAD `3765910`, worktree clean before and
  after the review.
- This is an independent adversarial review. It approves nothing, closes no owner item and
  is not the Constitution section 16 human review.
- Skills applied: `.agents/skills/quant-code-review/SKILL.md`,
  `.agents/skills/scientific-reproducibility-review/SKILL.md`.

## 1. Commits and records reviewed

| Commit | Content | Reviewed against |
|---|---|---|
| `cc197be` | Slice 6b part 1: `check_confirmation_read`, `trial_path`, `trial_result`, `completed_entry` (`calibration/c2_confirmation.py` l.2736-2848), `tests/unit/test_c2_confirmation_run.py` | `DESIGN_SLICE6B.md` (1e6e672) 6B-3, 6B-4; `SOL_DESIGN_SLICE6B_1E6E672.md` (8a22cb6) R14D6B-S-1..9; `ADJUDICATION_DESIGN_SLICE6B_1E6E672.md` (3765910) |
| `025ba5c` | Slice 6a: import gate refuses every finder lookup in the line-266 load; gate installed inside `try` | `SOL_CONFIRMATION_SLICE6A_RECHECK2_EB00731.md`, `SOL_CONFIRMATION_SLICE6A_RECHECK3_9C5D5DF.md`, `ADJUDICATION_SLICE6A_9F6135D.md` |

No frozen artifact (`docs/`, `protocols/`, `schemas/`, `specs/`, `FROZEN_HASHES.json`) is
touched by either commit (`git show --stat`). No confirmation or lockbox data was read:
the part 1 functions are pure, they never call a read gate, and the tests use the synthetic
screen fixtures (`ts._source`, `screen.null_path`).

## 2. Commands and results

Environment: Windows 11, `.venv` Python 3.14.7 (pyproject targets 3.12). Run from the
repository root.

| Command | Result |
|---|---|
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider tests/unit/test_c2_confirmation_run.py tests/unit/test_c2_confirmation_start.py` | 64 passed in 13.43s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider tests/unit/test_c2_confirmation_seeds.py tests/unit/test_c2_confirmation_seal.py` | 82 passed in 85.97s |
| `.venv/Scripts/python -m pytest -q -p no:cacheprovider` (full suite, 2718 tests collected) | **Not completed.** The run had produced no result after about 25 minutes and I stopped it. The full-suite result is unknown; this mandatory check is unverified by this review |
| `.venv/Scripts/ruff check src tests calibration` | All checks passed |
| `.venv/Scripts/ruff format --check src tests calibration` | 164 files already formatted |
| `.venv/Scripts/python -m mypy src` | Success: no issues found in 56 source files |
| `.venv/Scripts/python -m mypy --strict calibration/c2_confirmation.py tests/unit/test_c2_confirmation_start.py` | Success: no issues found in 2 source files |
| `.venv/Scripts/python -m mypy --strict tests/unit/test_c2_confirmation_run.py` | 10 errors, all in the imported `tests/unit/test_calibration_screen.py` (older file); 0 in the new test file. See R14S6-F-9 |
| `.venv/Scripts/lint-imports` | Contracts: 7 kept, 0 broken |

Adversarial probes (scratch scripts outside the repository, synthetic values only, each in
a fresh `python -I` process):

| Probe | Result |
|---|---|
| Import `calibration.c2_confirmation` alone; which line-266 modules are preloaded | none (`aqt.core.paths`, `aqt.core.preregistration` are not loaded by the module's own imports) |
| `load_line266()` ungated vs `load_line266(sources)` gated, disk hashes | both add exactly `aqt.core.paths`, `aqt.core.preregistration`; gate removed; `jsonschema` placeholders removed |
| Sources in the wrong order (preregistration before paths) | refused `line 266 imports unauthenticated aqt.core.paths`; gate removed; no partial module left |
| A listed module whose code swallows the refusal with `except Exception` | load continues, nothing unauthenticated executed (`zipapp` never loaded) |
| `import aqt.core.preregistration` before `load_line266(sources)` with hashes `"0"*64` | **loaded, `_TRIAL_SEED` set** (R14S6-F-1) |
| `completed_entry` with upper-case hex, spaced hex, NaN/inf, non-canonical day strings, `d: null` with a `d_sha256`, `d` with a `reason`, missing id fields, extra fields, a `d` moved under another trial id and hash | **all accepted** (R14S6-F-2, F-3) |
| `completed_entry` with a 7-byte hex value | refused with `struct.error`, not `CycleError` |
| `trial_path` with `w0` 30 minutes off the hour | **accepted** (R14S6-F-6) |
| `check_confirmation_read`: naive `start`, a gap with the same bar count, swapped symbols | refused |

Not done: the full test suite (see the table); the other confirmation suites (`bls`,
`cpcv`, `cycle`, `gates`, `runs`) were not run separately; no byte-for-byte rerun of `trial_result` across two processes (the test compares
two computations in one process only); no run on the qualified Linux image; no check
against a signed C2, a real store, a launcher or a real ledger, none of which exist yet.

## 3. Verdict

**FIX.**

- `025ba5c` does close R14S6AR2-S-1 (rest) and R14S6AR3-S-1 as Sol stated them, and the
  gate itself has no bypass that I could find for code going through the import system.
  One hole next to the gate remains (F-1): a listed line-266 module that is already loaded
  is never hash-checked.
- `cc197be` matches design 6B-3 and 6B-4 as written at 1e6e672, but the pre-look record
  it defines cannot carry what the accepted rev-2 directions need (F-3, F-4), and its
  decoder accepts malformed and non-canonical records (F-2). The adjudication's sentence
  "6b part 1 stays; rev 2 extends it" is too strong: the record schema and
  `completed_entry` must change, not only be extended around.

Nothing in either commit reads protected data, and nothing has a consumer yet, so no
finding has caused harm. F-1 to F-4 must be repaired before the 6b orchestration is built
on these functions.

## 4. Findings

Severity uses the review skills' classes. "Proposal" marks items that are not plain code
fixes and need the owner or the governance process.

### R14S6-F-1 — BLOCKER (6a) — a preloaded line-266 module skips its hash check

- Where: `calibration/c2_confirmation.py:1050` (`if name not in sys.modules:` in
  `load_line266`).
- What: with `sources`, a listed module that is already in `sys.modules` is skipped. Its
  hash is never compared, the gate is not involved (no finder lookup happens), and the
  final check only looks at modules *added* in the window. The docstring's claim "no
  unauthenticated line-266 code executes" is true only if nothing loaded the two modules
  earlier.
- Failure scenario (reproduced): a launcher, or any module imported before `start`, runs
  `import aqt.core.preregistration` (or `aqt.core.code_identity`, which imports
  `aqt.core.paths`) from disk. `load_line266` is then called with sources whose hashes
  match nothing (`"0"*64`). It returns normally and `_TRIAL_SEED` is the function from the
  unverified disk bytes. With altered disk bytes this is a different `trial_seed`, so
  different estimator seeds, with a passing `start`. `verify_code` later hashes the file
  on disk at that time, not the bytes that ran.
- Relation to earlier records: the adjudication's recorded residual (launch route,
  LG6A-2) names `aqt.core.ledger`, `aqt.data.manifest` and this module's own imports. It
  does not name the two listed modules, which the repair explicitly claims to
  authenticate. So this is not covered by that residual.
- Suggested repair (code): when `sources` is given, refuse (`SeedError`) if a listed name
  is already in `sys.modules`, instead of skipping it. `start` is specified as the first
  act of a fresh process, so no legitimate caller loses anything; a second `start` in one
  process then refuses, which matches "fresh process". Add a fresh-process test: preload
  the module, pass wrong hashes, expect refusal.

### R14S6-F-2 — BLOCKER (6b, before any consumer) — `completed_entry` accepts malformed and non-canonical records

- Where: `calibration/c2_confirmation.py:2834-2848`.
- What (each reproduced):
  1. hex values are decoded with `bytes.fromhex`, which accepts upper case and embedded
     whitespace. Several different byte strings decode to the same record;
  2. day strings are parsed with `strptime`, which accepts `2022-1-1T0:0:0Z`;
  3. non-finite `d` values (NaN, inf) are accepted;
  4. `d: null` with a non-null `d_sha256` and `reason: null` is accepted as an
     unavailable run; `d` present together with a `reason` is accepted as a result;
  5. missing fields (`cycle_id`, `trial_id`, `attempt_id`, `window_id`, `family`) and
     unknown extra fields are accepted; `window_id` is never compared with `days`;
  6. a wrong-length hex value raises `struct.error`, and a wrong type raises
     `ValueError`/`TypeError`/`KeyError`, not `CycleError`.
- Failure scenario: rev 2 stores this record as a ledger entry and matches it at the look.
  Two byte-different entries (one canonical, one with upper-case hex) decode to the same
  values, so "exactly one entry, matching ..." cannot be decided on decoded values alone,
  and a record whose stored hash differs from the canonical form's hash still passes.
  Item 4 lets a record that has no reason for its missing `d` stand as an unavailable run.
  `nominate` and `dsr.evaluate` catch item 3 and length errors later, but as U_ops or
  U_proc outcomes of a family, where the truth is a corrupt record that should refuse the
  evaluation.
- Suggested repair (code): make the decoder exact. Keys must equal the schema's set; every
  hex value must pass the module's own `_hex(x, 16)` (lower case, 16 characters); each day
  must round-trip through `_time`; values must be finite; `d`, `d_sha256` and `reason`
  must be either (list, hash, null) or (null, null, non-empty string); `len(d) ==
  len(days)`; `window_id` must equal `window_id(days[0], days[-1] + DAY)`. Any breach is a
  `CycleError`. One parametrized test over these cases.

### R14S6-F-3 — BLOCKER (6b design conflict, already accepted in direction as R14D6B-S-2) — the pre-look record binds nothing but `d` to itself

- Where: `calibration/c2_confirmation.py:2805-2831` (record), `2845-2847` (check);
  `tests/unit/test_c2_confirmation_run.py:166` (`test_a_tampered_pre_look_d_is_refused`).
- What: `d_sha256` covers only `d`, and it sits in the same record. It does not cover
  `trial_id`, `configuration_hash`, `attempt_id`, `window_id` or `days`. Reproduced: the
  `d` and `d_sha256` of one trial placed under another trial's id and configuration hash
  are accepted. The test named "tampered d is refused" only proves that a careless edit is
  caught; anyone who edits `d` also edits `d_sha256`.
- Status: this is R14D6B-S-2, accepted, with the ledger entry as the rev-2 direction. It
  is listed here so the record is complete, and because the part 1 test name overstates
  what is proven. No new decision is needed.
- Suggested repair: as adjudicated (ledger entry between the attempt's start and outcome).
  In addition, define one canonical hash of the whole record (`sha(cj(record))`) as what
  the ledger entry and the evaluation record refer to, and rename the test to say what it
  checks (internal consistency, not authenticity).

### R14S6-F-4 — BLOCKER (6b design conflict with rev-2 directions S-2 and S-3) — the record lacks the fields rev 2 must match

- Where: `calibration/c2_confirmation.py:2786-2831` (`trial_result`).
- What:
  1. The record has no `estimator_seed` (nor `seed_l266`, `trial_index`). The adjudicated
     S-2 direction requires the look to match each entry's "window and estimator seed".
     `trial_result` takes `estimator_seed` as a bare caller integer and does not record it.
  2. The record has no data identity (the manifest hash that S-3 says the read gate
     returns and the module checks) and no code identity (`protocol_hash`,
     `engine_commit`, module hashes). `path` is a bare array with no link to
     `check_confirmation_read`'s output.
- Failure scenario: `evaluate_trial` runs months before the look, in another process. A
  trial evaluated with a wrong estimator seed, or on bars from another manifest, yields a
  well-formed record. At the look, `seal_family` recomputes `d` only for the nominee and
  only on the status (a) path; every other trial's `d` enters `dsr.evaluate` unchecked and
  moves S0, the dispersion and the choice of nominee. Without the seed and the data
  identity in the record, the look cannot check them for non-nominee trials at all.
- Suggested repair (code plus proposal): add `estimator_seed` (and the seed fields
  `seal_family` already compares), the served data's manifest hash and the `Started`
  code identity to the record; have `trial_result` take them from verified values, not
  bare caller arguments; at the look require every completed trial's recorded seed to
  equal `derive_seeds`' value. **Proposal:** the exact field list is part of the S4 output
  contract (owner), as the adjudication already notes for S-3 and S-7. The schema name
  `aqt.c2.trial_result.v1` is not yet signed, so changing it now costs nothing; say so in
  rev 2.

### R14S6-F-5 — QUESTION / proposal — an unavailable run is recorded at nomination as `MISALIGNED_SERIES` (U_ops)

- Where: `calibration/c2_confirmation.py:2821-2830`, `2843-2844`; `nominate` l.886-892;
  `U_OPS_REASONS` l.637-640.
- What: `completed_entry` turns an unavailable run into an empty series, and `nominate`
  then reports `"<id>: MISALIGNED_SERIES"` with cause U_ops. The real reason
  (`TRIAL_CODE_ERROR`, `OVERLAY_VIOLATION`, `EventContractError`, ...) stays only in the
  pre-look record. The comment on `U_OPS_REASONS` says infrastructure or governance
  reasons are U_ops and "every other unavailability is a procedure no-result (U_proc)". A
  registered trial's own code failing deterministically on the data is not infrastructure.
- Why it matters: P18-7 fixes the cause code by precedence; the family's recorded cause
  and reason are what a later reader sees. Design 6B-4 says U_ops "as for an incomplete
  trial" and Sol did not object, so this may be intended.
- **Proposal (owner/statistical binding, not a code fix):** state in rev 2 which cause a
  recorded-unavailable trial gives, and carry the pre-look `reason` into the nomination's
  reason instead of `MISALIGNED_SERIES`. Do not change `U_OPS_REASONS` without the
  binding.
- Side note, consistent, no action: the code catches `CostModelError`,
  `FeatureFactoryError` and `SealError("DAYS_INCOMPLETE")` in addition to the two
  exceptions design 6B-4 names. This matches the module's existing convention (l.2204-2206)
  and should simply be written into rev 2.

### R14S6-F-6 — NON-BLOCKING — `trial_path` floors a `w0` that is not on the hour

- Where: `calibration/c2_confirmation.py:2780`.
- What: `offset = (w0 - warmup - start) // HOUR` is a floor division with no remainder
  check. Reproduced: `w0` 30 minutes past the hour is accepted and the path is cut as if
  `w0` were on the hour. Later `baseline_d` builds bars from `w0 - warmup` and
  `Bar` refuses an unaligned time, so today this fails closed downstream, but as a
  `BarSemanticsError` crash, not as a C-T refusal.
- Suggested repair (code): refuse when `(w0 - start) % HOUR` is non-zero or `warmup` is
  not a non-negative `int`. One line and one test case.

### R14S6-F-7 — NON-BLOCKING — part 1 tests leave branches of the read contract unproven

- Where: `tests/unit/test_c2_confirmation_run.py:42-70`, `136-155`.
- What: no test covers (a) a gap or a duplicate hour inside a series of the right length
  (my probe shows the code refuses it), (b) `interval != HOUR`, (c) the
  `except screen.TrialError` branch at l.2769 (the test comment says `Bar` already refuses
  bad OHLC, so this branch is never exercised), (d) `CostModelError` and
  `FeatureFactoryError` in `trial_result`. The contract clauses "each exactly once" and
  "finite, positive OHLC" are therefore asserted by code that no test would notice being
  removed.
- Suggested repair (tests): four small cases; for (c) pass rows through a `BarSeries`
  whose bar fields are set past `Bar`'s constructor, or drop the branch's claim.

### R14S6-F-8 — NON-BLOCKING — gate evidence is from Windows and Python 3.14.7 only

- Where: `calibration/c2_confirmation.py:1036-1043`; `ADJUDICATION_SLICE6A_9F6135D.md`
  third re-check row.
- What: the gate now refuses every lookup, so its safety rests on the fact that a real
  load asks for no new module. I confirmed that fact here (adds exactly two modules), but
  the set of modules an import pulls in depends on the Python version and platform (lazy
  standard-library imports), and the qualified image is Linux. If the fact fails there,
  `start` refuses and the refusal is final for the process. That is fail-closed, not a
  bypass, but it would block every evaluation.
- Suggested step: run the authenticated-load test on the qualified image before signing,
  and record the Python version with it. No code change.
- Recorded limit, no action: the gate governs the import system only. Verified (signed)
  code that loads a file by path (`spec_from_file_location`, `exec`, `runpy`) or swallows
  the refusal is outside it; that code is hash-bound, so this is inside the trust model.

### R14S6-F-9 — NON-BLOCKING — the new test file is not clean under the strict type check the adjudications cite

- Where: `tests/unit/test_c2_confirmation_run.py:13` (`import test_calibration_screen as ts`).
- What: `mypy --strict tests/unit/test_c2_confirmation_run.py` reports 10 errors, all in
  the imported older test file. The 6a adjudication records "strict mypy on the module and
  the start test clean"; cc197be has no recorded validation at all (F-10), and the same
  claim cannot be made for its test file as it stands.
- Suggested repair: either fix the 10 errors in `test_calibration_screen.py` or record the
  strict check for this file as not applicable with the reason. Do not silence them.

### R14S6-F-10 — NON-BLOCKING (process) — cc197be has no committed validation or review record, and was built before the design review

- Where: `review/r14a-modules/` (no file names cc197be except the adjudication's one
  sentence).
- What: `DESIGN_SLICE6B.md` says it is "for Sol's design review before the orchestration
  is built". Part 1 was committed after the design and before Sol's review, and Sol's
  review covered the design only. AGENTS.md asks for exact commands and results per task
  and a committed record for each review. For cc197be there is neither a command record
  nor a local gate record. This review is the first record of it, and it only counts once
  committed.
- Suggested repair: commit this record, and add the validation commands for part 1 to the
  6b local gate record when 6b is closed. No code change.

## 5. Checks with no finding

- **Protected data:** no path in either commit reads confirmation or lockbox data.
  `check_confirmation_read` validates what it is handed and calls nothing.
- **Read contract (6B-3) as written:** symbols and order, interval, exact bar count, each
  bar at `start + i` hours (so ascending, once each, identical times on both series), OHLC
  rules through `screen.confirmation_path`, no fill or repair. Naive datetimes refuse.
  The binding of the served bytes to a manifest is R14D6B-S-3 (accepted, rev 2) and is not
  repeated as a finding.
- **Silent correction:** none found. Unavailable runs are recorded with a reason, never
  dropped; a caller input error is re-raised, not recorded as unavailability.
- **Determinism:** no new randomness, no unordered iteration into a record, floats stored
  as big-endian float64 hex. A cross-process rerun was not done (section 2).
- **Look-ahead:** `trial_path` ends at w1 and the bar at w1 is never read (derived terminal
  row); `d` is `baseline_d`, unchanged frozen logic.
- **Rev-2 directions S-1, S-4..S-9:** part 1 code neither implements nor contradicts them.
  `trial_result`'s `record` parameter is compatible with "the verified declaration's
  entries". S-6 keeps `d` and `d_sha256` in the pre-look record, as built.
- **R14S6AR3-S-1:** closed. The insertion is inside `try`; the test fails on the old code.
- **R14S6AR2-S-1 (rest):** closed for the three cases Sol named (listed module early,
  reload, other name); each refused before any code runs, gate removed afterwards. See
  F-1 for the neighbouring hole.

## 6. Proposals needing the owner or governance (not code fixes)

| Item | Why it is a proposal |
|---|---|
| F-4 field list of the pre-look record | Part of the S4 output contract and the signed C2 bindings |
| F-5 cause code and reason for a recorded-unavailable trial | P18-7 binding; a statistical/governance definition |
| F-8 qualified-image run | Needs the image and the launch route (LG6A-2), both open |
| F-10 record discipline | AGENTS.md process; the owner decides how part 1 is gated |

Code fixes the author can make now, subject to the usual review: F-1, F-2, F-6, F-7, F-9,
and the test rename in F-3. `calibration/c2_confirmation.py` is the confirmation module;
if it counts as a Constitution section 16 protected component, each of these still needs
the different-model and human PR review before merge.
