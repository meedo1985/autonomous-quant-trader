# Fable final review: slice 6b design rev 12 at a116077 (verdict FIX)

- Reviewer: Claude Fable 5.2, model ID `claude-fable-5-2` (as reported by the session; run as
  a Claude Code subagent, read-only except for this file). Independent adversarial reviewer,
  not an authority. This record approves nothing, closes no owner item and makes no edit;
  every correction below is a proposal for the author and the owner.
- Date: 2026-11-14.
- Reviewed: `review/r14a-modules/DESIGN_SLICE6B.md` at commit `a116077` (rev 12), branch
  `confirmation-module` (checkout HEAD `cbc5509`; the only later change is the review prompt).
  `git diff --stat 9ca4de5 a116077` over `calibration`, `src`, `tests`, `docs`, `protocols`,
  `schemas`, `specs`, `FROZEN_HASHES.json` is empty: no code or frozen file changed.
- Prompt: `DESIGN_SLICE6B_REV12_PROMPT_FABLE.md`.

## Files and line ranges read

| File | Lines |
|---|---|
| `review/r14a-modules/DESIGN_SLICE6B.md` (rev 12) | 1-450 (whole); diff `9ca4de5..a116077` (71+/22-, whole) |
| `FABLE_FINAL_DESIGN_SLICE6B_9CA4DE5.md`, `ADJUDICATION_FINAL_DESIGN_SLICE6B_9CA4DE5.md`, `ASTRA_RECHECK_DESIGN_SLICE6B_99FBAC3.md`, `ADJUDICATION_RECHECK_DESIGN_SLICE6B_99FBAC3.md`, `ASTRA_RECHECK_DESIGN_SLICE6B_1A65A50.md`, `ADJUDICATION_RECHECK_DESIGN_SLICE6B_1A65A50.md` | whole |
| `calibration/c2_confirmation.py` | 600-975, 1480-1705, 1940-2105, 2340-2375, 2430-2560, 2570-2765, 2776-2902; list of all top-level definitions |
| `calibration/c2_lockbox.py` | 560-600, 700-796, 1205-1300; grep for the artifact inputs of `pre_read_check` / `run_evaluation` (l.759-792, 1372-1438) |
| `src/aqt/core/ledger.py` | 270-415 |
| `src/aqt/core/attempts.py` | 290-410 |
| `review/governance-statistics-amendment/o6a-channel/SPEC.md` | 60-145 (§4 end, §5, §6-§7 start) |
| `docs/RESEARCH_CONSTITUTION.md` | 136-160 (§16) |
| `protocols/protocol_v1.yaml` | 60-68, 190-194 |
| `review/r14a-modules/DESIGN.md` | 107, 192-232, 326-336 (§5, §5.2, §5.3, §7.2 output rows) |
| Other `review/r14a-modules/*SLICE6B*.md` | grep only (prediction artifact; relaunch / retry) |

Not read this round: `dsr.py`, `classifier.py`, `qobj.py` (no rev 10-12 change cites them
newly; they were checked in my rev 9 review). Not run: tests, lint, types, import-boundary
checks (design document only, no code changed).

## Verdict: FIX

Rev 10-12 repaired what the rev 9 review and the two Astra re-checks raised, and the
repairs hold against the code. Removing the capture floor is right. I found no second look,
no bar read before the look entry in `evaluate_look`, no dropped family, no lock-order
cycle, and nothing that lets AI approve or amend governance.

One thing still stops it being buildable as written, and it sits in the very contract rev
8-10 rebuilt (`persist`, closing entry, release): the sealed prediction artifact has no way
out of the module (F-1). It is a one-paragraph text repair, not a redesign. The other three
findings are minor.

## 1. Status of R14D6B9-F-1..6 in rev 12

| ID | Status | Evidence |
|---|---|---|
| F-1 | APPLIED | §2 l.70 compares with `protocol_row(started.protocol, "qualification_object_sha256")`. `Started.protocol` exists (code l.2670); `start` reads the same row by the same function and gives it to `verify_code` (l.2707, 2714-2716); `verify_code` compares it with the manifest hash (l.2592-2594). No reviewed code changes. |
| F-2 | APPLIED | §12 l.403-408: release only with this cycle's closing entry whose two hashes match the stored bytes, and no termination entry; `begin_read` named; store-build test. The lockbox `Store` docstring (l.1221-1240) still does not say it, as chosen; see F-4 note 1. The rule does not cover the prediction artifact: R14D6B12-F-1. |
| F-3 | APPLIED | §3 l.185-191: runner takes the look lock around every start and outcome write, look lock then append lock, eligibility checks inside the same locked operation. `append_entry` takes only its own lock (ledger.py l.391), so the order is one-way. |
| F-4 | PARTIAL (minimum applied; optional entry not applied) | Residual l.105-109; B-3 row l.444 names "records stored with no closing entry" and marks the counting for the owner. The pre-`persist` hash entry is deliberately omitted. Judged below. |
| F-5 | APPLIED | `sources` listed l.50-55; acceptance bytes hash-checked before use; `evaluate_trial` takes `attempt_id`, bound and `running` before any protected-data read (l.37-41, rule 4 l.218-223); `start`/`Started` wording l.47-48; §13 l.421-426; first breach l.197; scoped test l.293-295. Three inputs are still missing: R14D6B12-F-3. |
| F-6 | APPLIED (floor withdrawn, correctly) | Residuals l.91-104. The hard floor I proposed is gone; a diagnostic is logged instead. |

**The unapplied F-4 entry.** Soundly justified, with the rev 11 qualifier. The omission no
longer rests on recomputation (which would need a second read of the confirmation bars and
cannot prove the first run finished). It rests on two things that do hold: unclosed records
are never released (§12), and how a `LOOK_WITHOUT_RECORD` cycle is counted is left to the
owner. One thing the owner should know when he decides that count: a `persist` that is
withheld on purpose cannot be told apart from one that failed, so the count should not be
kinder than a recorded U_proc. This is advice for the P18-7 wording, not a finding.

**Removing the F-6 capture floor (R14D6B10-A-1).** Right. My rev 9 proposal was wrong on
this point. Bitcoin's two-hour rule is checked against each node's own clock, and O-6a SPEC
§5 fixes `T` as the earliest qualifying capture and lets it predate the verifier's own
observation. A genuine earliest capture could therefore fall under the floor, and the
refusal could never be cured. No floor based on header times is safe without an accepted
clock assumption. The capture time itself stays in the evaluation record
(`seeds.beacon.capture_cdx`, code l.1689-1691), so the diagnostic can be checked.

## 2. Rev 10-12 changes, as a whole

| Change | Finding |
|---|---|
| `protocol_row(..., "qualification_object_sha256")` | Sound. Same row, same parser, same bytes as `start`. Step 2's `check_screen_record` needs the same value; the design does not say so, but there is only one such row. |
| Store release obligation | Sound for the two records. Missing for the prediction artifact: F-1. |
| Runner writes and checks under the look lock | Sound. Every holder takes look lock then append lock; the append lock holder never takes the look lock; no cycle. The one writer not under the look lock is the store's termination entry; every order of it against a look or a trial ends conservatively (intervening-entry stop, or release refused). Whether the look lock waits forever or times out is not said: F-4 note 3. |
| `sources`, acceptance bytes, `attempt_id` before any protected-data read | Sound as far as listed. Not listed: F-3. A second launch for the same attempt is not seen: F-2. |
| `capture_before_tip_window` | Sound. Strict comparison, refuses nothing, no consumer. What a verifier does when it is true is not said: F-4 note 2. |
| §13 | The four additions match the functions that must change (`completed_entry` l.2852, `family_attempts` l.730, `nominate` l.854, `trial_result` l.2801). `seal_family`, `sealing_record` and `derive_seeds` need no change. |
| "protected-data read" wording | Consistent in all places now. |

Check 4 summary: look early, only the stated clock and header-time residuals and the
owner's C-2; look twice, none; bars before the look entry, none in `evaluate_look`; drop a
family, none; hide a crash, F-2; hide a procedure failure, only the stated residuals;
release or pick without a closed look, none for the records, F-1 for the artifact; AI
approving or amending governance, none.

## 3. Owner table

- Every row that touches P18 or S4 wording names the clause in bold, and the header
  (l.18-20) ties those marks to the Constitution's process.
- Nothing is shown as decided that the owner did not decide. B-1..B-5 and C-1..C-3 are not
  misstated.
- One mark in the text has no row: the hard capture floor (l.96-97, "[OWNER], S4/SPEC
  wording"). See F-4 note 2.

## 4. New findings

| ID | Severity | Where | Short |
|---|---|---|---|
| R14D6B12-F-1 | major (buildability; fails closed) | §1 l.42-45; §4 l.255-258; §10 l.382-387; §12 l.401-408 | The sealed prediction artifact is never persisted, returned or covered by the release rule; the lockbox cannot run without its bytes. |
| R14D6B12-F-2 | minor | §1 l.37-41; §3 runner rule l.185-191, rule 4 l.218-223 | A trial process that dies before its result entry can be launched again on the same `attempt_id` with no trace: an unrecorded crash and an uncounted extra read. |
| R14D6B12-F-3 | minor (buildability) | §1 l.50-55; §2 l.62-63, l.132; §3 l.169-171 | Inputs still not defined: the screen record bytes, the trial objects, the declaration's field names; the attempt binding does not name the partition and family. |
| R14D6B12-F-4 | info | §12; §2 l.91-98; §4 l.243-249; owner table | Three notes: the lockbox `Store` text is silent on the release rule; what a true `capture_before_tip_window` asks of the verifier, and its missing owner row; the look lock's wait is not specified. |

### R14D6B12-F-1 (major): the prediction artifact has no way out of the module

- Where: §1 l.42-45 ("builds the evaluation and sealing records ... returns both records");
  §4 l.255-258 (closing entry binds two hashes); §10 l.382-387; §12 l.401-408
  (`persist(evaluation_bytes, sealing_bytes)`; release rule for "a stored evaluation or
  sealing record"). The word "artifact" does not occur in the design.
- Evidence. `seal_family` returns `(entry, artifact)`; for status (a) the artifact is the
  `aqt.lockbox.prediction.v1` object and the sealing record keeps only its hash,
  `prediction_artifact_sha256` (code l.1950-2054). The parent design says the module
  "returns only the C2 evaluation record, the prediction artifacts and the sealing record"
  and that sealing must "write the artifact" (`DESIGN.md` l.198-200, §5.3). The lockbox
  takes the artifact's exact canonical bytes: `pre_read_check(artifact_bytes=...)` gives
  `ARTIFACT_NOT_FOUND` when they are absent and requires
  `SHA256(artifact_bytes) == request.prediction_artifact_sha256` and `cj(artifact) ==
  artifact_bytes` (`c2_lockbox.py` l.776-791). The artifact can only be made from the
  confirmation bars (`baseline_d`), which are read once, at the look.
- Failure scenario. Built as written, a look ends with a nominee at
  `PROCEEDS_TO_LOCKBOX`. Both records are persisted and the closing entry is written. The
  artifact was computed inside `seal_family` and then dropped. The lockbox refuses with
  `ARTIFACT_NOT_FOUND`, and the artifact cannot be rebuilt without a second read of the
  confirmation bars, which the one-look rule forbids. The cycle's only successful outcome
  is lost. The other way it can go: the builder adds a third return value by himself,
  inside a §16 file, outside `persist`. Then a crash after the closing entry leaves a
  closed, releasable look with status (a) and no artifact, with the same end.
- Proposed correction. Say in §1, §10 and §12: `persist` also receives, for every status
  (a) family, the artifact's exact bytes `cj(artifact)`, and returns only when they too are
  durable; the closing entry is appended after that. No new hash is needed in the closing
  entry, because the sealing record already carries `prediction_artifact_sha256`. Extend
  the release rule: an artifact is released only under the same closing-entry condition and
  only if its bytes hash to the value in the stored sealing record. Add the store-build
  test: status (a), artifact missing or not matching, release refused. Say who writes the
  `aqt.c2.artifacts.v1` list the lockbox also needs (the store, from the declaration, or
  "not in 6b").

### R14D6B12-F-2 (minor): a second launch on the same attempt is invisible

- Where: §1 l.37-41 and rule 4 l.218-223 (the attempt must be `running`: no result entry,
  no outcome); runner rule l.185-191.
- Evidence. `evaluate_trial` writes nothing before its read. If its process dies after the
  read (or after `d` is computed) and before the append, the ledger shows only the start.
  A new `evaluate_trial` for the same `attempt_id` passes every check. The runner rule says
  the runner writes an outcome "only for an attempt with no result entry"; it does not say
  the runner must write one when the process dies, or that it may launch only once per
  attempt. Rule 4 covers two launches at the same time, not one after the other.
- Failure scenario. A trial's process is killed by the machine twice. The runner starts it
  again each time on the same attempt. P18-1 gives the family one re-run, after a recorded
  crash; here there were two crashes, none recorded, no slot used, and the bars were read
  three times for one counted attempt. A family that P18-1 would have ended as unfinished
  (U_ops) completes instead. The same route lets a runner stop a process once it has seen
  something it dislikes. The result is deterministic (seeds and manifest are bound), so
  this gives no choice of `d`; what is lost is the crash record and the re-run limit.
- Proposed correction. At least: add to the runner rule that there is one `evaluate_trial`
  process per `attempt_id`, and that a process that ends without a result entry gets the
  crash outcome before anything else is started for that trial; state as a residual that
  the module cannot see a second launch. Optional and stronger: `evaluate_trial` appends a
  one-line "read begun" entry for the attempt under the look lock before its read, and
  refuses if one exists; then "begun, no result" is a crash the look can see by itself.
  That would be a new entry type and belongs under the P18-1 wording row.

### R14D6B12-F-3 (minor): inputs still not defined

1. The screen record. Step 2 calls `check_screen_record(record, record_sha256, trials,
   object_sha256)` (code l.714-727). The declaration carries the hash; the record's bytes
   must come from somewhere (`DESIGN.md` l.107: "the listed record's bytes match the hash
   in the declaration"). `sources` "holds exactly" six things (l.50-53) and the screen
   record is not one of them. Add it, or say the declaration embeds the record. Say also
   that `object_sha256` is the same `protocol_row` value as §2's classifier row.
2. The trial objects. `check_declaration` runs `screen.check_trial` on each trial object,
   and `trial_result` and `seal_family` take the object and check
   `screen.trial_sha256(trial) == configuration_hash` (l.2813-2816, 2001). §2 l.62 says the
   declared trials come from `Started.declaration` "as lockbox `_check_declared`", but that
   layout lists hashes only (`c2_lockbox.py` l.722-723). Say whether the declaration embeds
   the objects or the caller hands them and the module checks each hash.
3. The declaration's field names. §2 reads `data_manifest_sha256`, `last_seen`,
   `embargo_days`, the ledger anchor, the screen record hash and the cycle id from the
   declaration, and the parser is written in this build. Give the `[DESIGN layout]` field
   list, as the lockbox did, to be bound in the S4 text.
4. Attempt binding (l.169-171) says "a start of this cycle". `family_attempts` counts only
   starts of this family, this cycle and the confirmation partition (l.757-760). Say the
   same in the binding rule. Otherwise `evaluate_trial` can read bars and write a result
   for a start recorded under another partition word, and the look then finds a result
   entry with no attempt and refuses the whole cycle.

### R14D6B12-F-4 (info): three notes

1. The release rule lives only in the confirmation `Store` docstring. The lockbox `Store`
   docstring, the text the lockbox store build is tested against, still says `begin_read`
   needs only that sealing records exist (l.1221-1240). Not changing `c2_lockbox.py` is a
   fair choice (its section is pinned), but then the store build's test list is the only
   thing that carries the rule. Say in §12 that the release test is a required test of the
   one store build that serves both modules.
2. `capture_before_tip_window`. A true value means either a node clock that was ahead or a
   capture time that is not genuine; in the second case the beacon round could have been
   public before the trials were declared. The design rightly refuses nothing. Add one
   sentence: a true value is a point the verifier must clear against the archive (SPEC §4
   record) before the cycle's result is relied on. The "[OWNER]" mark for a hard floor
   (l.96-97) has no row in the owner table; add it to the B-1 row.
3. The look lock (l.243-249) does not say whether a waiter blocks or times out. If it
   copies the append lock's timeout (ledger.py l.350-360), an `evaluate_trial` that
   finished its computation can lose its result while a look or another writer holds the
   lock. With F-2 unrepaired that loss is silent. Say which it is; a blocking wait is the
   simple choice, because every holder's locked section is short and a dead holder
   releases the lock.

## What I could not check

- The drand chain-info layout and the CDX digest form (no network; both stay `[VERIFY]`).
- The Bitcoin Core source Astra cites for the clock rule (no network); the argument is
  consistent with SPEC §5 l.99 and I accept it on that basis.
- The store, the runner, the declaration layout and the signed C2 do not exist yet; the
  findings are against the design text and the code it cites.
- No code was run.
