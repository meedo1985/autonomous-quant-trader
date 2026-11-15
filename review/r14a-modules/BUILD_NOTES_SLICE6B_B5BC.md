# Slice 6b build, B5b and B5c (read, nomination, gates; records, sealing, persist, closing): build notes for review

- Builder: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15, branch `confirmation-module`.
- Design: `DESIGN_SLICE6B.md` rev 16 §1, §2 step 8, §4 (closing entry), §5, §6, §8, §9,
  §10, §11, §12; DESIGN.md §5.2-§5.4. B5a: `ADJUDICATION_B5A_53A4550.md`.
- §16 applies: not merged; different-model review and the owner's PR review first. The
  pinned start-chain section is unchanged.

## What B5b and B5c add

| Piece | Commit |
|---|---|
| B5b: `BENCHMARK_SPEC`, `benchmark_spec_sha256`, `within_law`, `FamilyEvaluation`, `completed_results` (+ `used_results`, B5c), `evaluate_families(inputs, look, read)` | `6e4671e` |
| B5c: `EVALUATION_SCHEMA`, `_plain`, `evaluation_record`, `seal_families`, `Persist`, `evaluate_look(started, sources, read, persist)`, `Store` obligations docstring | `4bb5084` |
| B5a repair; `of_cycle` result attribution; `cpcv` scope test narrowed; local rename `c14` | `8f05d2f` |

Tests: `test_c2_confirmation_families.py` (real family ledgers; nominate, gates, read,
C-14 replaced by recorders), `test_c2_confirmation_look_records.py` (record fields and
forms, sealing inputs, persist-then-closing order, failure paths). Mutation checks: one read
per nominee, the G-13 override, the completed-attempt selection, the breach hand-off, and
closing-before-persist each fail 1-2 tests.

## Deviation the review and the owner must accept or reject

- **B5B-D-1 (G-13 source).** Rev 16 §7 says only that `canonical_benchmark_sha256` feeds
  G-13; DESIGN.md's table says "hash equality with the v1.1 canonical benchmark hash" and
  "none found" for the computing code. Reading taken: the compared value is the SHA-256 of
  `specs/CANONICAL_BENCHMARKS_v1.1.md` in the module's own checkout (S4 DRAFT_WORDING §1a:
  the v1.1 benchmark specification, whose hash `benchmark_set_v1_1_sha256` is appended to
  `FROZEN_HASHES.json`; v1.0's `benchmark_set_sha256` is the SHA-256 of
  `specs/CANONICAL_BENCHMARKS_v1.md`, checked here). If the file is absent, G-13 is
  UNAVAILABLE (`BENCHMARK_SPEC_MISSING`) and the nominee's outcome `NO_RESULT`. The
  module's checkout is the root whose module files `start` verified; the file itself is not
  in `verify_code`'s inventory. Owner item (S4 wording).

## Readings taken

- **B5B-R-1** `read` is called once, and only when some family has a nominee (no
  protected read for nothing); each nominee's path is cut with its own warm-up from that
  one read.
- **B5B-R-2** `completed` for `nominate` holds, for each trial whose state is
  `completed`, its last derived-completed attempt's result (an earlier completed attempt
  of a trial whose last attempt runs is not used, FINAL-F-2).
- **B5B-R-3** A family with no nominee gets no gates (`gates = {}`, `outcome = None`);
  `seal_family` then gives status (b) with the nomination's reason.
- **B5B-R-4** C-14 is computed by `evaluate_families` and written by `evaluation_record`
  only; the "no code path reads it" test now allows exactly those references.
- **B5C-R-1** Evaluation record: `signed` is the §7 rows plus `engine_commit`,
  `screen_object_sha256`, `image_digest`; `trials{id: record_sha256}` covers the result
  entries the look used (`used_results`); `ledger.head_hash`/`entry_count` are the step-4
  (pre-look) ledger's; floats `hexf`, numpy scalars plain, tuples lists, instants `_time`;
  any other type refuses (`CycleError`).
- **B5C-R-2** `dsr.differs` is true when (nominee, reason, G-9 result) differ between V
  and Task 12, G-9 computed for each with the signed `z_crit`; `decision` is Task 12's
  reason and nominee (§9).
- **B5C-R-3** `seal_family` gets the nominee's declared entry as its record, the used
  result's `d_sha256`, `code` = the four `Started` code-identity hashes; the sealing
  record's `beacon_round` is `derive_seeds`' beacon round.
- **B5C-R-4** `persist` receives `cj(evaluation)`, `cj(sealing)`, `{family:
  cj(artifact)}`; the closing entry is appended under the look lock only after `persist`
  returns; a `persist` exception propagates with no closing entry.
- **B5C-R-5** The closing entry is appended even if a termination entry was written after
  the look: release then needs both a closing entry and no termination (§12), so a
  termination still blocks release.
- **B5C-R-6** The `Store` docstring gathers the store obligations of §2 A-1, §2.1, §3,
  §4, §5.1, §6, §8 and §12; it is a contract for the store build's tests, not code.

## Not in B5

The release tests of the store build (§12, required tests of that build); an end-to-end
`evaluate_look` run through the real BLS beacon, headers, capture and frozen gate code
(the per-step tests replace those with recorders; the frozen code has its own tests).
