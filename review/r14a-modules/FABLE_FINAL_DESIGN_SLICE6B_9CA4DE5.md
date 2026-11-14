# Fable final review: slice 6b design rev 9 at 9ca4de5 (verdict FIX)

- Reviewer: Claude Fable 5.2, model ID `claude-fable-5-2` (as reported by the session; run as
  a Claude Code subagent, read-only except for this file). Independent adversarial reviewer,
  not an authority. This record approves nothing, closes no owner item and makes no edit;
  every correction below is a proposal for the author and the owner.
- Date: 2026-11-14.
- Reviewed: `review/r14a-modules/DESIGN_SLICE6B.md` at commit `9ca4de5` (rev 9), branch
  `confirmation-module` (checkout HEAD `3e8aa2e`; the only later change is the review prompt).
  `git diff --stat 4b6e6e0 9ca4de5` over `calibration`, `src`, `tests`, `docs`, `protocols`,
  `schemas`, `specs`, `FROZEN_HASHES.json` is empty: no code or frozen file changed.
- Prompt: `DESIGN_SLICE6B_REV9_PROMPT_FABLE.md`.

## Files and line ranges read

| File | Lines |
|---|---|
| `review/r14a-modules/DESIGN_SLICE6B.md` (rev 9) | 1-401 (whole); diff `4b6e6e0..9ca4de5` by stat (216+/154-, read as the whole new file); rev 6 text by grep for the store obligations |
| `FABLE_FINAL_DESIGN_SLICE6B_4B6E6E0.md`, `ADJUDICATION_FINAL_DESIGN_SLICE6B_4B6E6E0.md`, `OWNER_DECISIONS_DESIGN_SLICE6B_REV6.md`, `..._REV3.md`, `..._REV2.md` | whole |
| `ASTRA_RECHECK_DESIGN_SLICE6B_E2DDCB4.md`, `ADJUDICATION_RECHECK_DESIGN_SLICE6B_E2DDCB4.md`, `ASTRA_RECHECK_DESIGN_SLICE6B_2D607A1.md`, `ADJUDICATION_RECHECK_DESIGN_SLICE6B_2D607A1.md` | whole |
| `calibration/c2_confirmation.py` | 600-974, 1480-1515, 1617-1700, 1826-1840, 2345-2366, 2430-2902 |
| `calibration/c2_lockbox.py` | 505-535, 719-731, 1216-1250; grep for sealing / ledger / signed rows |
| `tests/unit/test_c2_confirmation_start.py` | 1-70; grep 114, 212-213 |
| `src/aqt/core/ledger.py` | 90-415 |
| `src/aqt/core/attempts.py` | 270-487 |
| `calibration/qobj.py` 66-67, 215-225, 275-307; `classifier.py` 86-92; `reduce.py` 66-72; `dsr.py` 95-110, 126-154 (grep); `scripts/d19_heldout.py` 180-195 | as listed |
| `review/governance-statistics-amendment/o6a-channel/SPEC.md` | 60-140 (§4 end, §5, §6 start) |
| `docs/RESEARCH_CONSTITUTION.md` | 138-158 (§16) |
| `protocols/protocol_v1.yaml` | grep: l.66 (confirmation partition), l.193 (180 days) |
| `review/r14a-modules/DESIGN.md` | grep: 107-116, 200, 216-221, 231, 329-333 |

Not run: tests, lint, types, import-boundary checks (design document only, no code changed).

## Verdict: FIX

Rev 7-9 repaired all nine of my rev 6 findings and Astra's three, and the owner decisions
C-1..C-3 are implemented as recorded. The header check, the breached-family states, the
look lock around `evaluate_trial`'s append, the attempt binding, the crash rewrite, the
`u_proc_present` aggregation, the §5 precedence, the clock floor and the capture schema are
sound against the code. I found no path to a second look, no bar read before the look entry
in `evaluate_look`, no dropped family, and nothing that lets AI approve or amend governance.

Two points stop it being buildable and safe as written. Both are one-paragraph text repairs,
not a redesign:

- F-1: the new `qualification_report` checks the object against the wrong signed hash.
- F-2: since rev 8 the records are stored before the look is closed, and nothing says the
  store must keep unclosed records away from the lockbox.

## 1. Status of R14D6B-FINAL-F-1..9 in rev 9

| ID | Status | Evidence |
|---|---|---|
| F-1 | APPLIED | §2 l.51 (six headers as a separate caller handle, checked against `acceptance["block_hash"]` and the links), l.56 (`qualification_report`), §13 l.368-371 (pinned section byte-identical). `ACCEPTANCE_FIELDS` (code l.2451-2454) and the pin test (test l.40-53) need no change. The new function cites the wrong hash: R14D6B9-F-1. |
| F-2 | APPLIED | §3 rule 1 l.160-166 (explicit states incl. `unstarted`, no slot, no cycle-level refusal), §2 step 5 l.108-109 (not waited for), rule 4 l.180-182 (`evaluate_trial` refuses). |
| F-3 | APPLIED (as the owner decided) | §5 l.238-258: breached family with any pre-look U_proc result is U_proc; `u_proc_present` and `u_proc_results` over every identity-valid pre-look result, recorded for every family. The unbreached route stays open and is not stated: R14D6B9-F-6. |
| F-4 | APPLIED | §3 rule 4 l.182-185, §4 l.205-208: look lock, re-read, refuse or append. The runner's own writes are still outside the lock: R14D6B9-F-3. |
| F-5 | APPLIED | §1 l.35-38, §4 l.217-232, §10 l.347-348, §12: records returned and passed to `persist`; closing entry binds both hashes; no closing entry = `LOOK_WITHOUT_RECORD`. New gaps from the rev 8 ordering: R14D6B9-F-2, F-4. |
| F-6 | APPLIED | Attempt binding l.136-140; crash rewrite l.147-150 and §13 l.375-376; outcomes matched to this cycle's starts l.138-140, §13 l.372-374; start `protocol_hash` l.104; malformed look/closing/termination payloads l.103-104. |
| F-7 | APPLIED | §2.1 l.81-91: `aqt.c2.capture_record.v1`, exact field set, body equals the tip hash, body hashed to the CDX digest, `[VERIFY]` kept. |
| F-8 | APPLIED | Owner table l.393-398 names B-1, B-2/C-1, B-3, B-4/C-2, C-3 and the crash rule with their P18/S4 wording; header l.14-16 says they need the Constitution's process. |
| F-9 | APPLIED | §2 l.53 (clock floor), l.71-76 (non-nominee `d` and clock residuals). |

## 2. Owner decisions C-1..C-3 and the owner table

| Item | Recorded selection | In rev 9 | Note |
|---|---|---|---|
| C-1 | six headers as a separate handle; acceptance record and lockbox untouched | §2 l.51, §13 | As decided. |
| C-2 | look does not wait for a breached family; `evaluate_trial` refuses for it | §2 step 5, §3 rules 1 and 4 | As decided. |
| C-3 | breached family with a procedure-failure reason counts as U_proc; `u_proc_present` recorded | §5 rule 1, l.257-258, table l.397 | As decided, and limited to breached families (Astra A-3). `u_proc_results` is an AI addition to the record only. |

- Nothing is shown as decided that the owner did not decide.
- Every row that touches P18 or S4 wording is marked in bold with the clause, and the
  header ties those marks to the Constitution's process.
- One row is behind the text: B-3's "to confirm" reading (l.395) names "evaluation without
  sealing", but rev 8 added a second case, both records stored and no closing entry
  (l.220-222). That case should be named in the row too (see F-4).
- The design does not misstate B-1..B-5.

## 3. New findings

| ID | Severity | Where | Short |
|---|---|---|---|
| R14D6B9-F-1 | major (buildability, fails closed) | §2 l.56 | `qualification_report` compares the object's manifest hash with `Started.screen_object_sha256`; the object is posted under the other signed row, `qualification_object_sha256`. |
| R14D6B9-F-2 | major (safety) | §4 l.217-223; §12 l.360-364 | Records are stored before the closing entry; nothing obliges the store to keep unclosed or terminated records from the lockbox. |
| R14D6B9-F-3 | minor | §4 l.205-215; §3 rule 4 | The runner's start and outcome writes are outside the look lock, and the rev 6 obligation that covered this was dropped. |
| R14D6B9-F-4 | minor (governance marking) | §1 l.36-38; §4 l.220-222; table l.395 | `persist` sees the outcome before the look is closed; a failing `persist` leaves nothing about the outcome in the ledger; how `LOOK_WITHOUT_RECORD` is counted is not stated. |
| R14D6B9-F-5 | minor (buildability) | §1 l.33-41; §3; §5; §13 | Inputs not defined: `sources`, the attempt id of `evaluate_trial`, the acceptance record; small §13 omissions. |
| R14D6B9-F-6 | info | §5 l.241-246; §2.1; §3 rule 1 | Residuals to state: the recode route for unbreached families; no floor on the capture time; an extra start is still cycle-level. |

### R14D6B9-F-1 (major): `qualification_report` checks the wrong signed hash

- Where: §2 l.56, "requires `sha(json.loads(manifest.json)) == Started.screen_object_sha256`
  ... as `verify_code` l.2592-2594". The same wording is in
  `ADJUDICATION_FINAL_DESIGN_SLICE6B_4B6E6E0.md` ("Evidence checked", second bullet).
- Evidence. `verify_code` compares the manifest hash with its `posted_sha256` argument
  (l.2592-2594). `start` passes `rows["qualification_object_sha256"]` for it (l.2714-2716).
  `Started.screen_object_sha256` is a different signed row, `rows["screen_object_sha256"]`
  (l.2733), used as a sealing code field (l.1835-1838). `SIGNED_ROWS` lists both
  (l.2358-2363). The start tests give them different values: `"5" * 64` and `"9" * 64`
  (`test_c2_confirmation_start.py:212-213`). `Started` has no
  `qualification_object_sha256` field (l.2661-2673).
- Failure scenario. Built as written, `qualification_report` refuses every look and every
  trial of a real cycle, because the object `start` just accepted does not hash to the
  screen row. The builder then has to choose a fix inside a §16 file with no design text:
  the right one, or a wrong one such as loosening the check or accepting a second object
  directory that does hash to the screen row, whose `final_thresholds` would then set the
  classifier.
- The same value is needed by step 2's `check_screen_record(..., object_sha256)` (l.714-727),
  which compares the screen record's `qualification_object_sha256`.
- Proposed correction. Say: the hash is `protocol_row(started.protocol,
  "qualification_object_sha256")`, read from the protocol bytes `start` verified, the same
  row `verify_code` used. That changes no reviewed code. (Adding the field to `Started` also
  works, but it changes reviewed 6a code and would have to be named in §13.)

### R14D6B9-F-2 (major): stored records without a closing entry can still reach the lockbox

- Where: §4 l.217-223 ("A crash after `persist` and before the closing entry leaves stored
  records but no closing entry: `LOOK_WITHOUT_RECORD`, no pick"); §12 l.360-364 (the only
  `persist` obligation is durability).
- Evidence. Up to rev 7 the closing entry was written before the records left the module.
  Since rev 8 (R14D6B7-A-1) both records are durably stored first. The lockbox side takes
  sealing records from the store: its `Store` obligation is that `begin_read` "refuses
  unless sealing records exist for every declared family" and the family is status (a)
  (`c2_lockbox.py:1221-1240`). It does not read the attempt ledger, a closing entry or a
  termination entry. The termination entry itself is written later, "by the store on human
  action" (§5.1 l.268).
- Failure scenario. The look computes `PROCEEDS_TO_LOCKBOX` for a nominee, `persist`
  returns, and the process dies before the closing entry. By the design this cycle has no
  pick. The store, however, holds a complete status (a) sealing record, and every condition
  the lockbox `Store` docstring states is met. A lockbox read can start for a look the
  design calls no pick. The same holds for a cycle invalidated by a termination entry after
  a finished look.
- Proposed correction. Add to the confirmation `Store` obligations (§12), and to the list
  the store build is tested against: a sealing or evaluation record is released to anything
  (the lockbox `begin_read` included) only when the ledger holds this cycle's closing entry
  whose two hashes equal the stored bytes' hashes, and no termination entry for the cycle
  exists; `persist` writes to a place that is not released before that. No change to
  `c2_lockbox.py` is needed. Add a test line: persisted records, no closing entry, release
  refused.

### R14D6B9-F-3 (minor): the runner's writes are outside the look lock

- Where: §4 l.205-215; §3 rule 4 l.182-185; runner rule l.152-154.
- Evidence. `start_attempt` and `finish_attempt` append with the ledger's own lock only
  (`attempts.py:357-362, 395-400`; `ledger.py:391`). Rev 6 had "Store obligation: no runner
  writes this cycle's entries while a look runs" (rev 6 l.186). Rev 9 keeps only "every
  caller for a cycle uses the same ledger path on one host" (l.210-211).
- Failure scenarios. (1) Day-180 look with one trial still running: the runner records that
  trial's crash outcome, or starts its re-run, between the look's step 4 and step 7. That is
  an intervening entry of this cycle, so the look stops and both families end
  `LOOK_WITHOUT_RECORD`. (2) The runner times out a slow attempt and writes its crash
  outcome between `evaluate_trial`'s locked re-read and its append. The result entry then
  follows the outcome: an order breach, and the family fails. The test list (l.187) names
  "outcome racing the result entry" as an honest sequence; in this order it is a breach.
- Proposed correction. Put back the obligation, in the stronger form: the store's runner
  takes the same look lock around every start and outcome write for the cycle (look lock,
  then append lock). Then neither race exists. If only the weaker rev 6 sentence is
  restored, say that scenario 2 remains.

### R14D6B9-F-4 (minor, governance marking): `persist` sees the outcome before the look is closed

- Where: §1 l.36-38; §4 l.217-223; §10 l.347-348; owner table l.395.
- Evidence. `persist` is caller code and receives both records, with nominee, z and every
  cause code, before the closing entry exists. If it raises, the cycle is
  `LOOK_WITHOUT_RECORD` and the ledger holds a look entry and nothing about the result.
  Before rev 8 the hashes were in the ledger first.
- Failure scenario. A look ends with a family `U_proc` from `dsr.evaluate` (for example
  `UNSUPPORTED_LAW`), which is not visible in any result entry. `persist` fails, by fault
  or by choice. The cycle is recorded as an aborted look. No second look is possible, so
  nothing can be picked this way; what is lost is the recorded cause, and A-U1's target is
  on `U_proc^R`. The design does not say how a `LOOK_WITHOUT_RECORD` cycle is counted.
- Proposed correction. At least: state this as a residual, name the "records stored, no
  closing entry" case in the B-3 row for the owner's confirmation, and mark for the owner
  how `LOOK_WITHOUT_RECORD` is counted (P18-7 wording). Optional and cheap: append one
  entry with the two record hashes before calling `persist`, and the closing entry after
  it. The evaluation is deterministic from the ledger, the look entry's `now` and the
  served bars, so a verifier could then tell a finished look whose records were dropped
  from one that never finished.

### R14D6B9-F-5 (minor): inputs and contract changes still not defined

1. `sources` (§1 l.33, l.35) is never defined. From §2 it must hold at least: the ledger
   path, the six headers, the beacon, the capture record bytes and the object directory.
   List it.
2. The acceptance record. `headers_check` needs `block_hash`, and the capture check needs
   the height (`h+5` in the URL), but `Started` carries only the record's hash
   (`chain_log["acceptance_record_sha256"]`, l.2542, l.2673). Say the record bytes are
   passed again and must hash to that value before use.
3. `evaluate_trial(started, sources, trial_id, read)` has no attempt id, but §3 writes
   `attempt_id` and rule 4 speaks of "its attempt". Say whether the caller passes it or the
   module takes the trial's last start with no result and no outcome. Either way the
   attempt-binding rule (l.136-140) and a `running` state must hold for it **before** the
   read, so the module never reads bars for, or writes, an entry the look would refuse.
4. §1 l.40 says each entry point's "first act is `start`", but both signatures take
   `started`. Pick one.
5. §13 does not name: `completed_entry` returning `reason` and taking the governing window
   (§5 l.236, §3 l.174-177); `family_attempts` returning `attempt_id` (§5 l.263);
   `nominate`'s new inputs (the breach report and all pre-look results) and the new shape
   of `completed`; `trial_result`'s new inputs for the v2 fields.
6. `LEDGER_ORDER:<attempt_id>` (l.160): say which attempt when a family has several
   breaches (first in ledger order).
7. §5 test "a superseded attempt's U_proc result → U_proc" (l.255-256) can only happen in a
   breached family; in an unbreached one a second start after a result entry is a
   `CycleError` from `trial_states` (l.806-809). Say so in the test line.

### R14D6B9-F-6 (info): residuals to state

- Unbreached families keep the route C-3 closed for breached ones. After a `DAYS_INCOMPLETE`
  result is in the ledger, leaving any sibling trial unfinished at day 180 makes the family
  U_ops (§5 rule 2), with no breach. This is what the owner decided and I do not reopen it.
  `u_proc_present` is recorded for every family, so the fact stays countable; say that in
  the residual list and in the C-3 row.
- The capture time has no offline floor. `timestamp` picks the beacon round (code
  l.1489-1513) and is checked for form only. A time before the post would name a round that
  was public when the trials were declared. One line next to the clock floor: refuse when
  the capture time is earlier than the header time of `headers[5]` minus two hours (a block
  cannot be seen more than two hours before its header time). That the record is genuine
  and the earliest stays the stated store and verifier obligation.
- An extra `start_attempt` in an unbreached family (for example a restarted runner) is
  still a cycle-level `CycleError` at every later call (`trial_states` l.806-809), while a
  duplicate outcome fails only its family. B-4 covers three breach kinds and this is not
  one of them. Worth one sentence so the owner sees the difference.

## 4. Rev 7-9 changes, as a whole

| Change | Finding |
|---|---|
| `headers_check`, pinned section untouched | Sound. Offsets, byte orders and the display form are right; six headers match 6 confirmations and the `h+5` tip of SPEC §5. No proof of work is checked, as stated (l.69-70). |
| `qualification_report` | Right method (manifest as canonical JSON, files by raw bytes, `qobj.read` returns `(report, defn)`, `final_thresholds` is a report key). Wrong hash: F-1. |
| Breached-family states; look not waiting | Sound and complete. With both families breached the look opens at once and records both failed; no pick results. |
| `evaluate_trial` under the look lock | Sound for the module's own appends and for a double launch. Runner writes: F-3. |
| `persist` before the closing entry; `LOOK_WITHOUT_RECORD` | A closing entry now implies stored records. The reverse case is not covered: F-2, F-4. |
| Crash rewrite and attempt binding | Sound against `trial_states` l.792-824 and `finish_attempt` l.384-400. |
| `u_proc_present` / `u_proc_results` | Sound: computed before collapsing, over identity-valid entries only, so no cross-family or cross-cycle result can enter. |
| §5 precedence | Matches `nominate` l.890-897 for unbreached families; C-3 for breached ones only. |
| Clock floor | Sound; `append_entry` takes the same whole-second value (`ledger.py:111-123, 374`). |
| Capture schema; capture time vs window `T` | Sound and consistent after N-1: the capture time feeds `beacon_round` only; `w0` and the window `T` come from `check_eligibility` (l.675-711). Floor: F-6. |

Check 4 summary: look early, only the stated clock and header-time residuals and the
owner's C-2; look twice, none found; bars before the look entry, none; drop a family, none;
hide a crash, none; hide a procedure failure, F-4 and the F-6 residual; pick without the
closing entry, F-2; AI approving or amending governance, none found.

## What I could not check

- The drand chain-info layout and the CDX digest form (no network; both stay `[VERIFY]`).
- The store, the runner, the declaration layout and the signed C2 do not exist yet; the
  findings are against the design text and the code it cites.
- `c2_lockbox.py` was read only where listed, enough for the `Store` obligation in F-2.
- No code was run.
