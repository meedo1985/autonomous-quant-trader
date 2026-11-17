# Fable final review: slice 6b design rev 6 at 4b6e6e0 (verdict FIX)

- Reviewer: Claude Fable 5.2, model ID `claude-fable-5-2` (as reported by the session; run as
  a Claude Code subagent, read-only except for this file). Independent adversarial reviewer,
  not an authority. This record approves nothing, closes no owner item and makes no edit;
  every correction below is a proposal for the author and the owner.
- Date: 2026-11-14.
- Reviewed: `review/r14a-modules/DESIGN_SLICE6B.md` at commit `4b6e6e0` (rev 6), branch
  `confirmation-module` (checkout HEAD `19a6951`; the only later change is the review prompt).
- Prompt: `DESIGN_SLICE6B_FINAL_PROMPT_FABLE.md`.

## Files and line ranges read

| File | Lines |
|---|---|
| `review/r14a-modules/DESIGN_SLICE6B.md` (rev 6) | 1-339 (whole); diff `5cd2a29..4b6e6e0` by stat only (261+/143-, read as the whole new file) |
| `FABLE_RECHECK_DESIGN_SLICE6B_5CD2A29.md` | 1-335 |
| `OWNER_DECISIONS_DESIGN_SLICE6B_REV3.md`; `ASTRA_DESIGN_SLICE6B_9F45303.md`; `ASTRA_RECHECK_DESIGN_SLICE6B_24BA994.md`; `ASTRA_RECHECK_DESIGN_SLICE6B_366E504.md` | whole |
| `ADJUDICATION_RECHECK_DESIGN_SLICE6B_5CD2A29.md`; `ADJUDICATION_DESIGN_SLICE6B_9F45303.md`; `ADJUDICATION_RECHECK_DESIGN_SLICE6B_24BA994.md` | whole |
| `calibration/c2_confirmation.py` | 600-969, 1617-1700, 2436-2902; grep of 1489-1510, 1845, 1903-2075 |
| `calibration/c2_lockbox.py` | grep only: 1036-1077, 1098-1128, 1291-1306 (the copied start chain) |
| `tests/unit/test_c2_confirmation_start.py` | 18-60 |
| `src/aqt/core/ledger.py` | 90-415 |
| `src/aqt/core/attempts.py` | 270-487 |
| `src/aqt/data/manifest.py` | 636-838 |
| `calibration/dsr.py` 95-110, 180-200; `calibration/reduce.py` 60-80; `calibration/classifier.py` 86-104; `calibration/qobj.py` 66-67 (grep) | as listed |
| `review/governance-statistics-amendment/o6a-channel/SPEC.md` | 40-125 (§3 end, §4, §5) |
| `docs/RESEARCH_CONSTITUTION.md` | 140-157 (§16) |
| `review/r14a-modules/DESIGN.md` | grep: 106-110, 218-228, 333 |

Not run: tests, lint, types (design document only). Not re-read: `protocols/protocol_v1.yaml`
(rev 6 cites no line of it beyond what `c2_confirmation.py` l.632-634 already quotes),
`scripts/d19_heldout.py` (checked for rev 3, §8 unchanged since), drand layout (no network).

## Verdict: FIX

The Astra-round changes are sound in themselves: the header byte orders and offsets are
right, derived completion with `end` fixes the slot, the look lock and its order are
correct, the composite binding is complete, and the U_ops/U_proc precedence matches
`nominate` today. No path was found that lets AI approve or amend governance, and
`evaluate_look` reads no bars before its look entry.

It is not yet buildable as written for two reasons. §13 does not name that two of its
changes hit code that is pinned text-for-text to the lockbox module (F-1), and the rule
that a breached family skips `trial_states` leaves that family with no defined states on
the look-timing path and the bar-read path (F-2). Both are text-level repairs. F-3 is an
owner wording point that belongs with B-4.

## 1. Status of R14D6B3-F-1..13 in rev 6

| ID | Status | Evidence |
|---|---|---|
| F-1 | APPLIED | §2.1 l.67-80: capture record as bytes, three offline checks, hash logged, residual stated; A-5 withdrawn (l.338). Tip hash now has a source (`headers[5]`, l.46). Schema of the record still undefined: FINAL-F-7. |
| F-2 | APPLIED | §2 l.46: day 0 from `headers[0]` bytes 68-71 LE; `hash(headers[0]) == block_hash`; §13 l.313-315. Layout checked: version 4 + prev 32 + merkle 32 = 68. Consequence not named: FINAL-F-1. |
| F-3 | APPLIED | §2 l.48, steps 5 and 7 (l.91-94), §4 l.170-172: one clock read, same value as `recorded_at_utc`; early look leaves no entry. `ledger.py:123` truncates to seconds as the design says. |
| F-4 | APPLIED | §4 l.183-194, §11 l.300-302: P18-1 reference gone; intervening entries split by cycle; `LOOK_WITHOUT_RECORD` (owner B-3). Remaining edges: FINAL-F-4, F-5. |
| F-5 | APPLIED | §3 l.117-130: completion from the result entry, `outcome` and `end` rewritten before `trial_states`, runner rule; order breach is family U_ops (owner B-4). New gap from the breach rule: FINAL-F-2. |
| F-6 | APPLIED | §6 l.223-233: only composite + series served; entries taken from `composite.partitions`; `cycle_id` and `protocol_sha256` bound. Matches `manifest.py:641-656, 822-838`. |
| F-7 | APPLIED | §5 l.199-206: not-completed, order breach, misaligned days first; then U_ops reasons; else U_proc. |
| F-8 | APPLIED | §5 l.207-209: `U_OPS_REASONS` unchanged, `DAYS_INCOMPLETE` U_proc (owner B-5), list still `[DESIGN: list for review]`. Matches code l.639-640. |
| F-9 | APPLIED | §2 l.47, §5.1 l.214-219, §3 rule 4: record type, payload, writer, both entry points refuse, residual stated. |
| F-10 | APPLIED | §7 l.244-245, 250, 253-254: enumerations by exact membership; `family_block_rule` equal to the object's; `z_crit` as strings. |
| F-11 | PARTIAL | §13 names eight changes; anchor has no path (l.44-45); entries after the anchor (l.54-57). Not named: the lockbox copies (FINAL-F-1) and the smaller items in FINAL-F-6. |
| F-12 | APPLIED | §8 l.266-269: chosen reading and the declaration-time check. |
| F-13 | APPLIED | §10 l.285 "steps 1-8"; §9 l.275-278 `decision`, `differs`, CPCV line; §3 rule 3; `within_law`. |

## 2. Owner decisions B-1..B-5

| Item | Recorded selection | In rev 6 | Note |
|---|---|---|---|
| B-1 | offline checks, hash logged, residual stated | §2.1 | As decided. The design adds URL, status 200 and `id_` binding checks, which are SPEC §5's own conditions. |
| B-2 | day 0 = inclusion block header time; record gains **the** 80-byte header | §2 l.46 | Day 0 as decided. The record gains **six** headers and the tip is derived from them (Astra A4-1). That is an AI extension of the owner's selection, not shown to him: FINAL-F-8. |
| B-3 | `LOOK_WITHOUT_RECORD` | §4, §5.1, §11 | As decided. |
| B-4 | order breach: family U_ops, cycle continues | §3 rule 1 | As decided; marked [OWNER] P18-1/P18-7 wording. See FINAL-F-2, F-3. |
| B-5 | `DAYS_INCOMPLETE` stays U_proc | §5 | As decided. |

Nothing is shown as owner-decided that he did not decide, apart from the marking points in
FINAL-F-8. The header (l.13-15) and the table (l.336) say the wording still needs the
Constitution's process.

## 3. New findings

| ID | Severity | Where | Short |
|---|---|---|---|
| R14D6B-FINAL-F-1 | major | §13 l.311-315 | Two changes hit code pinned text-for-text to `c2_lockbox.py`; the lockbox module must change too and would refuse the new acceptance record. Not named. |
| R14D6B-FINAL-F-2 | major | §3 rule 1 l.138-142; §2 steps 4-5; l.97-98 | A breached family has no defined trial states: look timing and `evaluate_trial`'s right to read bars are undefined for it, and its attempt limits no longer apply. |
| R14D6B-FINAL-F-3 | major (governance) | §5 l.199-205; §3 rule 1 | Order breach is U_ops and takes precedence, and anyone who can append can create one after seeing a U_proc result. A procedure failure can be recoded. |
| R14D6B-FINAL-F-4 | minor | §2 l.97-98; §3 rule 4; §4 l.183-187 | `evaluate_trial` appends outside the look lock: a result landing between step 4 and step 7 at day 180 ends the whole cycle; a double launch breaches its own family. |
| R14D6B-FINAL-F-5 | minor | §1 l.32-33; §10; §11 l.300-302; §12 | An abort between the evaluation record and the sealing record has no stated outcome; the look's completion is not in the ledger; "writes" vs "no storage". |
| R14D6B-FINAL-F-6 | minor | §3, §13 | Ledger cases with no stated disposition, and rewrites not named. |
| R14D6B-FINAL-F-7 | minor | §2.1 | The capture record has no schema; body is not bound to the CDX digest. |
| R14D6B-FINAL-F-8 | minor (governance marking) | owner table l.336; §3 l.119-120 | Six headers, the `LOOK_WITHOUT_RECORD` cycle outcome and "no result entry = crash whatever the outcome says" touch P18/S4 wording but only B-2 and B-4 are marked. |
| R14D6B-FINAL-F-9 | info | §2 A-1; §2 l.48 | Two residuals to state: non-nominee `d` is never recomputed; the look clock has no floor. |

### R14D6B-FINAL-F-1 (major): §13 changes pinned lockbox copies and does not say so

- Where: §13 l.311-312 (`verify_code` keeps the report) and l.313-315 (`ACCEPTANCE_FIELDS`
  gains `headers`).
- Evidence. `c2_confirmation.py:2617-2619`: the start chain is "the lockbox module's ...
  copied text for text ... a test pins the copies equal".
  `tests/unit/test_c2_confirmation_start.py:25-50` pins the source of `check_acceptance`,
  `verify_chain`, `verify_code` and the value of `ACCEPTANCE_FIELDS` to
  `calibration/c2_lockbox.py` (same names at l.1036-1077), plus the whole section text.
  `check_acceptance` requires `set(acceptance) == ACCEPTANCE_FIELDS` (l.2474; lockbox
  l.1060). The lockbox `start` takes the same acceptance record (l.1291-1306).
- Failure scenario. The builder adds `headers` to the confirmation copy only. Either the
  pin tests fail, or they are loosened and the two modules now accept different records:
  the lockbox module refuses every acceptance record that has `headers`, so no cycle
  evaluated under rev 6 can ever start its lockbox. The other route, editing
  `c2_lockbox.py` to match, changes a second §16 file whose hash is a signed C2 row, with
  no design or review record for it.
- Proposed correction. Name it in §13. Two ways, the second needs the owner because B-2's
  recorded text says "acceptance record gains the 80-byte header":
  (a) change both copies identically, state that `c2_lockbox.py` gets its own §16 review
  for it, and say what the lockbox does with `headers` (at least the same form and link
  checks, so the copies stay equal);
  (b) leave the acceptance record and the pinned code untouched: pass the six headers as a
  separate caller handle, checked by `hash(headers[0]) == acceptance["block_hash"]` and the
  links, with their SHA-256 logged; `start` re-reads the qualification report itself rather
  than changing `verify_code`'s return. Day 0 is pinned as strongly, because
  `block_hash` already fixes `headers[0]`.

### R14D6B-FINAL-F-2 (major): a breached family has no defined trial states

- Where: §3 rule 1 l.138-142 ("not passed to `trial_states`' admissibility checks ... its
  states are reported with §3's derived completion"); §2 step 4 l.89-90, step 5 l.91;
  l.97-98 (`evaluate_trial` runs 1-4, then reads); §5 l.200-201.
- Evidence. The six state words exist only inside `trial_states` (l.810-824), and four of
  them (`rerun`, `undetermined`, `final`, slot logic) depend on the slot computation the
  breached family now skips. `look_allowed` (l.836) needs a state for every declared trial
  of both families. Nothing in rev 6 says how a breached family's states are computed, and
  rule 4 (l.157-158) does not make `evaluate_trial` refuse in a breached family.
- Failure scenarios.
  1. Look timing. Day 20: `vol` is all completed; `trend` has a duplicate outcome on one
     attempt and trial `t3` still running. One implementer reports the breached family's
     trials as `final` and looks on day 20; another reports `t3` as `running` and waits for
     day 180. P18-2's trigger is "every declared trial finished or day 180". The design
     picks neither.
  2. Bar reads. After a breach the family is already failed, but `evaluate_trial` for its
     trials still passes steps 1-4 and reads confirmation bars. Because the admissibility
     checks are skipped for that family, a third or fourth attempt of one trial is also
     accepted. Each is a confirmation read that serves no evaluation.
- Proposed correction. State a small explicit rule for a breached family, for example:
  per trial, last attempt derived-completed gives `completed`; last attempt with no result
  entry and no outcome gives `running`; anything else `final`; no slot. Say which of these
  `look_allowed` waits for (the P18-2 reading is the owner's; mark it [OWNER] with B-4).
  Add to rule 4: `evaluate_trial` refuses, before any read, for a trial of a family with an
  order breach. Tests for both.

### R14D6B-FINAL-F-3 (major, governance): an order breach can recode a procedure failure

- Where: §5 precedence 1 l.199-203 (order breach is U_ops, before any U_proc); §3 rule 1.
- Evidence. Result entries are plain ledger payloads with `reason` and `d` (§3 l.105-110),
  readable before the look by whoever holds the ledger. `finish_attempt`
  (`attempts.py:384-400`) does not refuse a second outcome. Up to rev 3 a second outcome was
  a cycle `CycleError`; from rev 4 (B-4) it fails only that family, as U_ops. A-U1 puts the
  calibrated at-most-0.01 target on `U_proc^R` (my rev 3 F-8).
- Failure scenario. A `trend` trial records `DAYS_INCOMPLETE` (U_proc). Before the look,
  a second outcome is appended for any `trend` attempt. The family is now U_ops
  `LEDGER_ORDER`, the other family is untouched, and the procedure failure has left the
  U_proc accounting. The reason is still in the message string, but the cause code, which
  is what is counted, has changed. This costs the writer nothing; the old behaviour cost
  the whole cycle.
- This does not dispute P18-7's "infrastructure or governance cause first". It is about a
  cause that can be created at will after the result is known.
- Proposed correction (owner wording, with B-4). Record, as a structured field of the
  family and not only in the message, every failing trial's own reason and whether any is
  a U_proc reason (for example `u_proc_present: true`), and put to the owner whether a
  family with an order breach **and** a recorded U_proc reason counts in `U_proc^R`. Until
  decided, the field alone keeps the fact countable by a verifier.

### R14D6B-FINAL-F-4 (minor): `evaluate_trial` appends outside the look lock

- Where: l.97-98 ("without the look lock"); §3 rule 4; §4 l.183-187.
- Evidence. The look lock is held from step 4 to the step-7 append, but only by looks.
  `append_entry` takes only its own lock (`ledger.py:391`). Rule 4 is a check, then a long
  read and computation, then an append with no re-check.
- Failure scenarios. (1) Day 180, one trial still running: its result entry lands between
  the look's step 4 and step 7. That is an intervening entry of this cycle, so the look
  stops and the cycle ends `LOOK_WITHOUT_RECORD`, both families, although the same entry a
  moment later is harmless by rule 3. The stated store obligation ("no runner writes while
  a look runs") does not obviously cover the module's own process. (2) A runner that
  retries on a timeout launches `evaluate_trial` twice for one attempt; both pass rule 4,
  both append; the second result entry is an order breach and fails the family.
- Proposed correction. `evaluate_trial` takes the same look lock just for its final step:
  lock, re-read the ledger, refuse without appending if a look entry, a termination entry,
  or a result or outcome for its attempt now exists, append, release. Lock order stays
  look lock then append lock. Then no result entry can land inside steps 4-7 and a double
  launch gives one entry and one refusal.

### R14D6B-FINAL-F-5 (minor): the end of the look is not pinned down

- Where: §1 l.32-33 ("writes the evaluation and sealing records"); §12 l.306 ("No
  storage"); §10; §11 l.300-302.
- Evidence. `seal_family` and `sealing_record` take `evaluation_record_sha256`
  (l.1903-1904, 1964-1965, 2057-2059), so the evaluation record exists before sealing
  starts. §11 defines only "look entry without an evaluation record".
- Failure scenarios. (1) The process dies after the evaluation record and before the
  sealing record is complete. The cycle has a look entry and an evaluation record, possibly
  saying `PROCEEDS_TO_LOCKBOX`, and no sealing record. A second look is refused; no
  termination kind applies; nothing says whether sealing may be repeated. (2) Whether a
  look finished is known only to the store. If the module returns the records and the store
  loses them, or the store appends `LOOK_WITHOUT_RECORD` beside a record that does exist,
  the ledger cannot show which is true.
- Proposed correction. Say whether the module returns the two records or writes them
  through a handle. Have the module append one closing entry
  (`{cycle_id, evaluation_record_sha256, sealing_record_sha256}`) as its last act, so a
  finished look is a ledger fact and `LOOK_WITHOUT_RECORD` means "look entry with no
  closing entry". Put the evaluation-record-without-sealing case under the same termination
  (or a second kind; the label is the owner's, with B-3).

### R14D6B-FINAL-F-6 (minor): cases and rewrites §3 and §13 leave open

1. A result entry whose `attempt_id` matches no start of this cycle, or that lies before
   its start. Rule 1 lists three order breaches and this is none of them; rule 2 says
   `attempt_id` is compared "with what the module derives now", but an attempt id is not
   derivable, it comes from the start entry. State: the entry's `attempt_id` must be a
   start of this cycle, after the anchor and before the entry, whose
   `(hypothesis_hash, trial_index)` maps to the entry's `trial_id`; otherwise `CycleError`.
2. "An attempt with no result entry before its first outcome is a crash, whatever its
   outcome says" (l.119-120). `trial_states` recognises a crash only by
   `outcome in NOT_COMPLETED and reason_code == CRASH` (l.794-795). So the rewrite must
   also set `outcome` and `reason_code` for such attempts (a `completed` or a `failed`
   with another code). §13's `trial_states` line names only the completed rewrite.
3. `family_attempts` collects outcomes over the whole ledger (l.745-751). The per-family
   report must ignore duplicate outcomes of other cycles, and say what an outcome with no
   start is. Likewise "an entry of this cycle" (§4) must resolve an outcome entry through
   its start, since an outcome payload has no cycle (`attempts.py:391`).
4. A start entry's `protocol_hash` (`attempts.py:340`) is not compared with the signed
   one. One line in step 4.
5. A malformed look or termination payload: state `CycleError`.

### R14D6B-FINAL-F-7 (minor): the capture record has no schema

- Where: §2.1 l.69-80.
- The three checks name parts (original body, CDX row, `id_` fetch, acceptance hash) but
  no record type, field list or byte form, and SPEC §4 lists evidence, not a schema. `T`
  (`capture_cdx`) feeds `beacon_round` (l.1489-1510) and so every seed; the builder would
  have to invent the layout inside a §16 file.
- Proposed correction. Give it as a [DESIGN schema] like the acceptance record: canonical
  JSON, exact field set, the row's URL / 14-digit timestamp / status / digest, the body
  bytes, the acceptance record hash; say `T` is the row's timestamp and that the body is
  compared exactly (say whether a trailing newline is allowed). Also check offline that the
  body hashes to the row's digest (CDX digests are base32 SHA-1 of the payload), which ties
  the body to the row without the network. **[VERIFY]** the digest form with a known
  capture before signing.

### R14D6B-FINAL-F-8 (minor, governance marking)

- The owner's B-2 text is one header checked against `block_hash`. Rev 5 made it six
  headers and derives the acceptance tip from them; the adjudication says "within B-1/B-2
  direction; no new owner item". It is a reasonable reading, but it changes the acceptance
  schema further than he selected and (F-1) reaches the lockbox module. List it in the
  owner table as an extension for his confirmation.
- The table marks only "B-2 and B-4 need S4/P18 wording". `LOOK_WITHOUT_RECORD` (B-3) is a
  cycle outcome under P18-2/P18-7; the capture-record residual (B-1) is S4/SPEC text; and
  "no result entry before the first outcome is a crash whatever its outcome says"
  (l.119-120) changes who may get the P18-1 re-run slot (today a `failed` with another
  code is `final`). The general sentence at l.13-15 covers them; the table should name
  them so none is read as settled.

### R14D6B-FINAL-F-9 (info)

- Residual to state beside A-1: the look takes every trial's `d` from the ledger. Sealing
  recomputes the nominee's and requires its hash (`DESIGN.md` l.226-228; l.1913), but a
  non-nominee's `d` is never recomputed, and every identity field is derivable by anyone
  once the beacon is public. A writer of the store can therefore shape the family matrix
  that G-9 and G-10 use. It is the same trust as the fork residual, but it is a different
  act and is not written down.
- The look clock is "recorded, not verified" (l.48). A cheap floor costs one line: refuse
  when `now` is before `cycle_start` or before the `recorded_at_utc` of the ledger's last
  entry. A clock set forward still opens the look early; that only fails families whose
  trials are unfinished, and stays a stated residual.

## 4. The Astra-round changes, as a whole

| Change | Finding |
|---|---|
| Six-header day 0 and tip hash | Byte layout, link direction and display form are right. No proof of work or Merkle inclusion is checked; the design says so (l.64-65). Reaches the lockbox copy: F-1. |
| Derived completion (`outcome` + `end`) and the runner rule | Sound against `trial_states` l.792-824: a result-then-died attempt no longer blocks the slot. Crash-side rewrite not named: F-6 item 2. |
| Per-family order breach skipping `trial_states` | Cannot let a failed family pass (it is U_ops by §5 whatever its states). Leaves states, look timing and reads undefined: F-2. Opens the recode path: F-3. |
| `days` vs identity; `completed_entry` change | Sound. Shifted days now reach `MISALIGNED_SERIES`; `window_id` is checked against the governing window; `d` integrity kept. |
| Look lock and intervening entries | Sound for two looks. Distinct sidecar avoids the nested append lock (`ledger.py:347, 391`). Does not cover the module's own trial appends: F-4. |
| `LOOK_WITHOUT_RECORD` | As the owner decided. Edge between the two records: F-5. |
| Termination entries | Sound; both entry points refuse. |
| Composite-bound manifests | Sound and complete against `manifest.py`. |
| U_ops / U_proc precedence | Matches `nominate` l.890-897 and DESIGN l.110. |

Check 4 summary: look early, F-2 (one reading) and the unverified clock (stated); bars
before the look entry in `evaluate_look`, none found; drop a family, none found (F-4 loses
both, recorded by termination); hide a crash, F-5; hide a procedure failure, F-3; AI
approving or amending governance, none found.

## What I could not check

- drand chain-info layout and the CDX digest form (no network).
- The declaration layout, the store, the runner and the signed C2 do not exist yet; the
  findings are against the design text and the code it cites.
- `c2_lockbox.py` was read only by grep, enough to confirm the copied names and the pin.
- No code was run; Astra's synthetic probes were not repeated.
