# Fable re-check: slice 6b design rev 3 (verdict FIX)

- Reviewer: Claude Fable 5.2, model ID `claude-fable-5-2` (as reported by the session; run as
  a Claude Code subagent, read-only except for this file). Independent adversarial reviewer,
  not an authority. This record approves nothing, closes no owner item and makes no edit;
  every correction below is a proposal for the author and the owner.
- Date: 2026-11-14.
- Reviewed: `review/r14a-modules/DESIGN_SLICE6B.md` at commit `5cd2a29` (rev 3), branch
  `confirmation-module`, against my rev 2 review `FABLE_DESIGN_SLICE6B_9D34615.md`.
- Read:
  - `DESIGN_SLICE6B.md` rev 3, whole file (l.1-221); `git diff 9d34615 5cd2a29` for it;
  - `FABLE_DESIGN_SLICE6B_9D34615.md` (whole), `ADJUDICATION_DESIGN_SLICE6B_9D34615.md`
    (whole), `OWNER_DECISIONS_DESIGN_SLICE6B_REV2.md` (whole); `DESIGN.md` l.110 (P18-2 row);
  - `calibration/c2_confirmation.py` l.329-337, 625-956, 1489-1700, 1845-1893, 2358-2364,
    2440-2902;
  - `calibration/dsr.py` l.60-260; `calibration/reduce.py`, `calibration/classifier.py`
    (whole); `calibration/qobj.py` l.40-298; `scripts/d19_heldout.py` l.172-197;
  - `src/aqt/core/ledger.py` l.100-123, 296-415; `src/aqt/core/attempts.py` l.290-402;
    `src/aqt/data/manifest.py` l.636-838;
  - from `origin/freeze-sheet`: `DRAFT_WORDING.md` l.151-174 (R-7, R-13, R-14a,
    `seed_disclosure`); `ANNEX_A_SELECTION_RULE.md` l.51-100, 144-160, 189-190 (P18-1, P18-2,
    P18-7, A-U1, A-V1); `o6a-channel/SPEC.md` l.51-116 (§4 record, §5 acceptance and capture).
- Not run: no test, lint or type check (design document only, no code changed). Not re-read
  for this check: `calibration/c2_lockbox.py`, Constitution §16/§26/§27 and
  `protocols/protocol_v1.yaml` (read for the rev 2 review; rev 3 changes nothing that turns
  on them beyond what is cited here).

## Verdict: FIX

Rev 3 applies most of the rev 2 findings correctly: the classifier thresholds (F-1), the
record-in-the-entry (F-3), the full identity comparison (F-11), the owner's F-8 decision and
the Task 12 fields are sound. It is not ready to build from, because two listed sources do
not exist (the capture-record hash in the declaration, the posting time in the chain log),
the look entry's clock is circular, and several rules leave a cycle permanently refused or
miscoded with nothing recorded.

## 1. Status of R14D6B2-F-1..19

| ID | Status | Evidence |
|---|---|---|
| F-1 | PARTIAL | §8 l.160-168: `final_thresholds["T=<T>"]`, pool as `d19_heldout.py:188-191` (checked, same expression), `reduce.for_k`; no re-pooling, row removed (§7 l.157). `z_crit` equality stated. `family_block_rule` equality with the object is not stated (see R14D6B3-F-10). |
| F-2 | PARTIAL | §4 l.104-110 and §2 step 7: module-written look entry before any read, second look refused. The clock is circular and the aborted-look outcome is undefined (R14D6B3-F-3, F-4). |
| F-3 | APPLIED (as adjudicated) | §3 l.67-102: record is the entry payload; rules 1-4; runner writes start/outcome. The adjudicated "refuse" choice has consequences not stated (R14D6B3-F-5). |
| F-4 | PARTIAL | A-1 l.46-50 states the residual plainly and withdraws the cycle record. Not stated: every entry of this cycle must lie after the anchor. The anchor still carries a `path` (l.37). |
| F-5 | PARTIAL | §6 l.125-139 uses `verify_partition_manifest`, `verify_composite_manifest`, whole partitions, own cut. The served partition manifests are not bound to the composite (R14D6B3-F-6). The embargo-day bars the module then holds are not mentioned. |
| F-6 | SUPERSEDED-BY-OWNER | §9 l.176-178: no `D_j` recorded; the note for a later version is Annex B's form. |
| F-7 | PARTIAL | §5 l.115-122: all trials examined, U_ops first, `DAYS_INCOMPLETE` in the one set. The rule covers reason strings only (R14D6B3-F-7); the list is presented as decided (R14D6B3-F-8). |
| F-8 | APPLIED | l.9-13: §16 stated as fact; item 4 stated; §9 records only `FamilyResult` (fields checked against `dsr.py:184`). Owner decision followed. |
| F-9 | NOT APPLIED (source does not exist) | §2 l.38 names "the declaration's posting time, from `start`'s chain log". The chain log has no time (R14D6B3-F-2). Not in the owner items table. |
| F-10 | APPLIED | §9 l.174-175, §10 l.189: `dsr{V, task12, decision, differs}`. `decision` and `differs` are not defined (note in F-13). |
| F-11 | APPLIED | §3 rule 5 l.94-98 lists every identity field. |
| F-12 | APPLIED (deferred as adjudicated) | §7 l.150 `[VERIFY]` with a known-answer test before signing. |
| F-13 | NOT APPLIED (not possible as written) | §2 l.37, l.42: capture-record hash in the declaration (R14D6B3-F-1). |
| F-14 | APPLIED | §2 l.40 "recorded, not verified". |
| F-15 | APPLIED | One source (l.37, l.157-158); parse rules l.143-146. No rule for enumerated rows (R14D6B3-F-10). |
| F-16 | APPLIED | §2 l.39, step 4: `read_entries` only. |
| F-17 | APPLIED | §5 l.114, 123. New unnamed changes in R14D6B3-F-11. |
| F-18 | APPLIED | §11 l.198-200: pre-pick "no pick" is the store's termination record. The post-look-entry case is R14D6B3-F-4. |
| F-19 | SUPERSEDED-BY-OWNER | Option (b) removed. |

## 2. New findings

| ID | Severity | Section | Short |
|---|---|---|---|
| R14D6B3-F-1 | blocker | §2 l.37, l.42; A-5 | The capture record is made after the post is accepted; the declaration is hashed into the post. The declaration cannot carry the capture record's hash. |
| R14D6B3-F-2 | major | §2 l.38 | `cycle_start` "from `start`'s chain log": the chain log and the acceptance record hold no time. |
| R14D6B3-F-3 | major | §2 steps 5, 7; l.40 | `look_allowed` (step 5) needs `now`; `now` is the time of an entry written at step 7. |
| R14D6B3-F-4 | major | §4 l.109-110, §11 l.202-203 | A look that aborts after its entry ends the cycle's one look with no record and no stated recorder; "P18-1 crash accounting" is about trial attempts. An ordinary concurrent append triggers it. |
| R14D6B3-F-5 | major | §3 rules 2-4 | Sequences an honest runner produces make every later look a `CycleError`, for ever, with nothing recorded. The runner's outcome rule is not stated. |
| R14D6B3-F-6 | major | §6 l.129-135 | Nothing requires the served partition manifests to be the composite's entries. |
| R14D6B3-F-7 | major | §5 l.115-117 | U_ops is decided by reason string only; trials with no record (crashed twice, unfinished at day 180) have no reason and fall to U_proc. |
| R14D6B3-F-8 | major (governance) | §5 l.118-122; owner table l.220 | The U_ops reason list, with `DAYS_INCOMPLETE` added, is shown as decided. The owner chose the principle, not the list. |
| R14D6B3-F-9 | major | §2 table, step 5; §3 rule 4 | Termination and invalidation records have no source and no check; `evaluate_trial` does not refuse after one. |
| R14D6B3-F-10 | minor | §7, §8 | `family_block_rule` is not required to equal the qualification object's; no exact parse for enumerated rows; `dsr.family_block` treats any value other than `"largest"` as median. |
| R14D6B3-F-11 | minor | §2, §3, §8 | Contract changes needed but not named; step order inside step 4; anchor rule. |
| R14D6B3-F-12 | minor | §8 l.163-164 | A missing `T=` key or a `for_k` error refuses both families with no record; it is knowable at signing. |
| R14D6B3-F-13 | info | §9, §10 | Small wording points. |

### R14D6B3-F-1 (blocker): the declaration cannot carry the capture record's hash

- Where: §2 l.37 ("capture-record hash ... the declaration only"), l.42 ("the capture record,
  whose SHA-256 the declaration carries (F-13)"), owner item A-5 l.217.
- Evidence. `verify_chain` (`c2_confirmation.py:2527-2530`): the post carries
  `SHA256(declaration)`. SPEC §5 l.91-98: a qualifying capture is an Internet Archive capture
  of the acceptance-tip block hash URL; "no qualifying capture can predate the frozen
  6-confirmation chain state". SPEC l.105: `T` is frozen at the freeze point, 7 days after
  acceptance. So the capture record exists only after the post is accepted, and the post
  already fixes the declaration's bytes.
- Failure scenario. A-5 goes to the owner as "as §2" and cannot be built. The implementer
  must then take the capture time from somewhere else; the nearest value is a store-supplied
  one, which is what S-1 and F-13 were meant to remove. `capture_cdx` fixes the beacon round
  (`beacon_round`, l.1489-1514), so it fixes every seed.
- Proposed correction. Say plainly that the capture record is created after the declaration
  and cannot be bound by it. Options for the owner: (a) the module takes the capture record
  as bytes, checks what it can offline (the body equals the acceptance record's tip block
  hash; the CDX row has the 14-digit form; the record names the acceptance record's hash),
  logs its SHA-256 in the evaluation record, and the residual (the record's truth and that it
  is the earliest capture) is a stated store and verifier obligation next to R14L2-S-2; or
  (b) a second posted commitment after the freeze point, which is a new channel rule and an
  S4 change. Neither is the reviewer's or the author's to pick.

### R14D6B3-F-2 (major): `cycle_start` has no source in the chain log

- Where: §2 l.38; step 5 l.59.
- Evidence. `verify_chain` returns `{acceptance_record_sha256, post_txid,
  declaration_sha256, protocol_hash, <two module rows>}` (l.2541-2553). `ACCEPTANCE_FIELDS`
  is the exact set `{schema, txid, raw_tx, block_hash, height, confirmations, first_post}`
  (l.2451-2454, enforced l.2474). A raw Bitcoin transaction has no timestamp. `Started`
  (l.2661-2673) has no time field.
- Failure scenario. `look_allowed` cannot be given a verified day 0. An implementer adds a
  parameter or a store field; a `cycle_start` 180 days early opens the look while trials run
  (the rev 2 F-9 scenario, unchanged).
- Also: which instant is P18-2's day 0 (the post's block time, acceptance, the freeze point,
  the first `EVALUATION_STARTED`) is a binding. The adjudication says "part of A-1"; the
  owner table's A-1 row (l.214) does not mention it.
- Proposed correction. Name a real source and its check, for example the inclusion block's
  80-byte header supplied with the acceptance record, required to hash to a block hash the
  record names, its time field read as day 0 (the acceptance schema is a DESIGN schema, so
  it can gain the field); or a declaration field `cycle_start` (the declarer's claim, bound
  by the post). Put the choice and the day-0 definition in the owner items.

### R14D6B3-F-3 (major): `now` is read from an entry that does not yet exist

- Where: §2 l.40 ("the module's own look entry time"), step 5 l.59, step 7 l.61-62.
- `look_allowed(states, cycle_start, now, ...)` runs at step 5. The look entry is appended
  at step 7. Two readings, both wrong:
  1. The entry is appended first and `now` read from it. Then a call made before day 180,
     with trials still running, appends the look entry and only afterwards learns the look is
     not allowed. The cycle's one look is used by a premature call.
  2. `look_allowed` uses a clock value taken at step 5. Then `now` is not "the look entry
     time", and the recorded time and the deciding time can differ.
- Proposed correction. The module reads its clock once, before step 5; uses that value in
  `look_allowed`; and passes the same value as `recorded_at_utc` to `append_entry` at step 7
  (the parameter exists, `ledger.py:374`; it is truncated to whole seconds, so compare the
  truncated value). State it in §2 and §4. Test: a look requested before day 180 with a
  running trial is refused and leaves no look entry.

### R14D6B3-F-4 (major): what an aborted look leaves is not defined

- Where: §4 l.109-110; §11 l.201-203; §2 step 7.
- "An aborted look leaves its look entry and no evaluation record; that is the P18-1 crash
  accounting's case." P18-1's re-run is for a trial attempt that "ends without writing any
  result artifact", once per family. It says nothing about the look. P18-2 says exactly one
  look per cycle. So either the phrase permits a second look (against §4's own first
  sentence and P18-2), or it means nothing. Rev 2 F-2 and F-18 asked who records the cycle
  outcome in this case; rev 3 does not say.
- It is reachable without any fault. Step 7 appends the look entry, then re-reads and
  refuses if any other entry was appended since step 4. `append_entry` cannot append
  conditionally (`ledger.py:391-414`). A trial that finishes, or a runner that records an
  outcome, between step 4 and step 7 therefore consumes the look: the entry is in the
  ledger, the look refuses, no evaluation record, no sealing record, both families silent.
  The post-read `CycleError`s (C-T, manifest, `seal_family`) end the same way. P18-7 and
  §11's own "never dropped" then do not hold for the cycle.
- Proposed correction (proposal; the cycle-outcome wording is the owner's). State: (1) a
  look entry without an evaluation record ends the research phase with no pick and no
  promotion, and the store records the cycle outcome with a fixed label; no second look;
  delete the P18-1 reference. (2) A store obligation that no runner writes to the ledger
  while a look runs; or, to make the race harmless, let step 7 accept intervening entries
  that are not of this cycle and treat an intervening entry of this cycle as case (1).
  (3) Tests for both.

### R14D6B3-F-5 (major): honest sequences that refuse every later look

- Where: §3 l.82-93 (start and outcome by the store's runner; rules 2-4; "any breach is
  `CycleError`, no read").
- The ledger is append-only, so a breach found at the look is found at every look. Three
  sequences need no bad intent:
  1. `evaluate_trial` records an unavailable run (`d: null`, a reason). The runner, seeing a
     run without a result, records outcome `failed`. Rule 3: a result entry for an attempt
     that is not completed refuses the look. Rev 3 does not say which outcome the runner
     must write for an unavailable run (rev 2 F-3 item 1).
  2. `evaluate_trial` passes rule 4 (no outcome yet), reads and computes; a recovery process
     records an outcome meanwhile; the result entry lands after the outcome. Rule 2 breach.
     `evaluate_trial` has no re-read, and a re-read could not undo the append.
  3. The process dies after appending the entry; recovery codes `CRASH_NO_ARTIFACT`. Rule 3
     breach.
- In each, before the look entry exists the cycle can never be looked at, and nothing is
  recorded: no U_ops family, no outcome. P18-7 expects the family recorded with a cause.
- Second point, same rules. Rule 2 turns an outcome `completed` without a result entry into
  a `CRASH_NO_ARTIFACT` crash, which can win the family's re-run slot. `trial_states`
  (l.771-824) reads `outcome` and `reason_code` as recorded, and step 4 lists
  `trial_states` before the entry rules. The rewrite must happen before `trial_states`, and
  that changed contract is not named.
- Proposed correction. Smallest: the module derives "completed" from the result entry, not
  from the runner's outcome word (an attempt with exactly one valid result entry before any
  outcome is completed; any outcome may follow), and `evaluate_trial` itself calls
  `finish_attempt(completed)` after its append. For the remaining breaches (entry after an
  outcome, entry in an attempt already coded as a crash), record that family's `A_f` as
  failed with a U_ops reason naming the attempt, and deny the re-run slot, instead of
  refusing the cycle. The second part touches P18-1 and P18-7 wording, so it is the owner's.
  If "refuse" is kept, write the consequence in §11 (the cycle ends by a store termination
  record, no pick) and the runner's outcome rule in the `Store` docstring. Tests for 1-3.

### R14D6B3-F-6 (major): the served manifests are not tied to the composite

- Where: §6 steps 1-3, l.129-135.
- Evidence. `verify_partition_manifest` checks a manifest against itself and, with `series`,
  against the bars (`manifest.py:641-656`). `verify_composite_manifest` checks the composite
  against its own embedded entries (l.822-837). Rev 3's `read` returns the series "together
  with their partition manifests and the cycle's composite manifest" and never requires the
  two to be the same objects.
- Failure scenario. `read` serves the true composite (its hash equals the declaration's)
  and, beside it, four other self-consistent partition manifests with other bars. Step 1
  passes (each verifies alone), step 2 passes, step 3 passes (the bars match the manifests
  served with them). The module evaluates bars the cycle's manifest does not name. The §6
  test "bars from another manifest" then passes or fails depending on how the implementer
  reads the sentence.
- Proposed correction. `read` returns only the composite and the series. The module takes
  each partition manifest from `composite.partitions` (by partition and symbol) and calls
  `verify_partition_manifest(entry, series=served)`; step 3 is then redundant and can go.
  Also require `composite.cycle_id` to equal the cycle's id, and state which protocol hash
  `composite.protocol_sha256` must equal. State that the lockbox enters only as the sealed
  reference (hash only; `manifest.py:779-785`), and that the module holds, and does not use,
  the confirmation bars before `w0 − W`.

### R14D6B3-F-7 (major): trials without a record are coded U_proc by the text

- Where: §5 l.115-117: "If any failing trial's reason is in `U_OPS_REASONS`, the family is
  U_ops; otherwise U_proc."
- Evidence. `nominate` today returns U_ops for three cases that carry no reason code
  (l.890-897): a trial not completed ("no completed evaluation (final)", also `running`,
  `unstarted`, `rerun`, `undetermined` at day 180), a configuration-hash mismatch, and a
  day index other than the window's. `DESIGN.md` l.110: "Trials unfinished at day 180 are
  `U_ops` (timeout)".
- Failure scenario. Family with trial `a` crashed twice (`final`, no record) and every other
  trial completed. No failing trial has a reason in `U_OPS_REASONS`, so by rev 3's sentence
  the family is U_proc. An infrastructure crash is then counted as a procedure no-result,
  against P18-7's "infrastructure or governance cause first" and against today's code.
- Proposed correction. State the full rule: a trial that is not completed (any state), and a
  day-index mismatch, are U_ops and take precedence; then a recorded reason in the U_ops
  set; otherwise U_proc. Note that the configuration-hash case is now a `CycleError` at §3
  rule 5 and say whether `nominate` keeps its own check. One test per case and ordering.

### R14D6B3-F-8 (major, governance): the U_ops list is shown as decided

- Where: §5 l.118-122; owner table l.220 ("A-3 ... decided (split by reason ...)").
- Evidence. The owner's recorded answer on A-3 is "Split by reason": data or infrastructure
  reasons U_ops, a trial's own deterministic failure on valid data U_proc. It lists no
  reason. `U_OPS_REASONS` carries the marker "[DESIGN: list for review]" (l.637-640). Rev 2
  F-7 said the list is the owner's binding; the adjudication answered "No (follows A-3)".
- Why it matters. A-U1 puts the calibrated at-most-0.01 target on `U_proc^R`. A reason moved
  to U_ops leaves that accounting. `DAYS_INCOMPLETE` is raised by `baseline_d` (l.1891-1892)
  when the run yields too few daily returns, after `check_confirmation_read` has already
  accepted complete hourly bars; by the owner's own principle that reads as the trial's
  failure on valid data, which is U_proc. Putting it under U_ops is the direction that hides
  a procedure failure. An AI design should not settle that by default.
- Proposed correction. Move the reason list, and `DAYS_INCOMPLETE` by name, to the owner
  items and the A-7 / S4 contract, with both placements shown. Until decided, leave
  `U_OPS_REASONS` unchanged.

### R14D6B3-F-9 (major): termination and invalidation records have no source

- Where: §2 table l.33-44 (no row); step 5 l.59 ("termination records"); §3 rule 4 l.92-93;
  §11 l.199-200.
- Rev 2's step 4 read "the termination and look records" from the ledger. Rev 3 dropped the
  phrase and added no row. `look_allowed`'s `terminated` (l.827-833) is then an input with
  no governing record, no record type and no stated writer, under a design whose rule is
  "handles, never values". `evaluate_trial` refuses on a look entry but not on a termination
  (rev 2 F-3 item 6).
- Failure scenario. The cycle is invalidated (for example an earlier qualifying capture is
  shown, SPEC l.106). The caller passes `terminated=False`, or the store has not written its
  record where the module looks. The look runs and seals artifacts for an invalidated cycle;
  or a trial reads confirmation bars after the cycle ended.
- Proposed correction. Add the row: record type, payload `{cycle_id, kind, reason}`, that it
  lives in the same anchored ledger, who appends it (the store, by human action), and that
  both entry points refuse when one exists for the cycle. State the residual: the module
  cannot know of an invalidation nobody recorded.

### R14D6B3-F-10 (minor): `family_block_rule` and enumerated rows

- Where: §7 l.143-146, 154; §8 l.167.
- §8 requires the object's `z_crit` to equal the signed row but not `family_block_rule`
  (rev 2 F-1, F-15). `dsr.family_block` (l.100-105) returns the median for any value that is
  not exactly `"largest"`; `evaluate` does not validate `rule`. A signed row `"Largest"` or
  `"max"` gives the median silently. The parse rules cover integers, times, decimals and
  hashes, not enumerations (`family_block_rule`, `drand_scheme`).
- Proposed correction. Require `family_block_rule == report["family_block_rule"]` and
  membership in `choices.RULES`; `drand_scheme == SCHEME` exactly. State how `z_crit`
  equality is compared (string equality of the decimal strings, not floats).

### R14D6B3-F-11 (minor): contract changes not named, and two rules not stated

- `verify_code` discards the report (`_, defn = qobj.read(files)`, l.2601) and `Started`
  has no field for it. §8 needs `start` to keep `final_thresholds`, `z_crit` and
  `family_block_rule`. That is a change to reviewed 6a code and should be named.
- `trial_states` input changes (F-5 above); `look_allowed`'s `looked` now comes from the
  look entry; `TRIAL_RESULT_SCHEMA` goes to v2 with a new key set (`_TRIAL_RESULT_KEYS`).
- Rev 2 F-4 asked for "every entry of this cycle lies after the anchor; a start with this
  cycle before it is refused". Rev 3 says "extension of the anchor" only.
- The anchor still includes a `path` in the posted declaration. A file path is a property
  of one machine; head hash and entry count are enough to check extension.

### R14D6B3-F-12 (minor): a missing T level is knowable before the cycle starts

- Where: §8 l.163-164.
- `T` is fixed by `check_eligibility` from signed rows (l.703-711). If `final_thresholds`
  has no `T=<T>` key, or `for_k` fails for a family's K, rev 3 refuses the whole evaluation
  before any read, both families, no record, at every call. `classifier.within` would treat
  another T or K as that family's refusal (`UNSUPPORTED_LAW`). Refusing before the read is
  the safe direction; state it as the chosen reading, and add a declaration-time check
  (store or builder obligation) that the window's T and each family's K have thresholds, so
  an unevaluable cycle is not declared.

### R14D6B3-F-13 (info)

- §10 l.185 still says "steps 1-6"; rev 3 has eight steps.
- `dsr{..., decision, differs}`: say what `decision` holds and that `differs` is true when
  the nominee, the availability reason or the G-9 result differ between V and Task 12.
- Rev 2's line "Nothing reads the C-14 CPCV report (test, LG5B-6)" was dropped; keep it.
- `evaluate_trial` can append its result after a look entry written while it was running.
  The look is unaffected (the trial was `running`, U_ops at day 180), but confirmation bars
  are then read and a result written after the pick. State that it is harmless and recorded.
- §8's `classifier = lambda ...: classifier.within(...)` reuses the module's name; rename
  the local when built.

## What holds in rev 3

- Thresholds from the verified qualification object, built exactly as the frozen held-out
  runner builds them; no caller bytes and no new signed row.
- The record as the ledger entry's payload; `record_sha256` as its one identity; every
  identity field compared at the look.
- §9 records `FamilyResult` only, for V and Task 12; the module computes no statistic
  (owner decision on F-8, R-14a item 4). The §16 statement at the top is a statement of
  fact from R-14a item 1 and waives nothing.
- No frozen artifact in `docs/`, `protocols/`, `schemas/` or `specs/` needs an edit for
  rev 3. The new rows, the declaration fields and the output contract are proposals for the
  unsigned S4 text.
- Seed failures stay read-free; the look entry precedes every read.

## What I could not check

- drand's chain-info layout (no network; still `[VERIFY]`, F-12 of rev 2).
- The declaration layout, the store, the runner and the signed C2: none exists yet. The
  findings are against the design text and the code it cites.
- I did not re-review slices 1-6a code; I read it only to check the design's claims.
