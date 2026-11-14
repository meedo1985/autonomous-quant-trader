# Slice 6b design, rev 11: the confirmation evaluation run and the C2 evaluation record

- Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-14. History: rev 1 `1e6e672`
  (Sol FIX R14D6B-S-1..9); rev 2 `9d34615` (Fable FIX R14D6B2-F-1..19); rev 3 `5cd2a29`
  (Fable FIX R14D6B3-F-1..13); rev 4 `9f45303` (Astra FIX R14D6B4-A-1..6); rev 5 `24ba994`
  (Astra FIX R14D6B5-A-1..4); rev 6 `4b6e6e0` (Astra ACCEPT WITH NOTES `a282449`; final
  Fable FIX R14D6B-FINAL-F-1..9, record `97ff99d`). Rev 7 applies
  `ADJUDICATION_FINAL_DESIGN_SLICE6B_4B6E6E0.md` (all accepted) and the owner's decisions in
  `OWNER_DECISIONS_DESIGN_SLICE6B_REV6.md` (C-1..C-3), on top of `..._REV3.md` (B-1..B-5)
  and `..._REV2.md`. Rev 8 applies `ADJUDICATION_RECHECK_DESIGN_SLICE6B_E2DDCB4.md`
  (Astra FIX R14D6B7-A-1..3, record `7c29af4`, all accepted). Rev 9 applies the three wording
  notes of the Astra ACCEPT WITH NOTES re-check of rev 8 (`2f4c5f3`). Rev 10 applies
  `ADJUDICATION_FINAL_DESIGN_SLICE6B_9CA4DE5.md` (final Fable FIX R14D6B9-F-1..6, record
  `9cc082d`, all accepted). Rev 11 applies `ADJUDICATION_RECHECK_DESIGN_SLICE6B_99FBAC3.md`
  (Astra FIX R14D6B10-A-1, record `bc1fc66`, accepted).
- A proposal for review before the orchestration is built. It approves nothing and closes
  no owner item. **[OWNER]** marks bindings for the signed C2 or the S4 text. Owner
  decisions recorded as direction still need the Constitution's process where they touch
  P18 or S4 wording (listed by name in the owner table).
- **§16 (fact, R-14a item 1):** `calibration/c2_confirmation.py` is merged only under
  Constitution §16 review with an independent different-model review record and the
  owner's PR review (R14D6B2-F-8). Rev 7 changes **no** code in the section pinned to
  `calibration/c2_lockbox.py` (`tests/unit/test_c2_confirmation_start.py`), so the lockbox
  module is not touched (FINAL-F-1).
- **R-14a item 4:** the module loads data, checks, **calls** frozen code and records. It
  computes no statistic of its own (owner decision on F-8: record only frozen output).
- Scope: DESIGN §5.2 steps 2-8 and §7.2, after slice 6a's `start`. 6b part 1 (`cc197be`
  .. `b350264`) stays and is extended.

Rule: the caller passes **handles** (paths, a read gate, the beacon, the six block headers,
the capture record bytes); every value the module can read or verify from a governing
record it reads and verifies itself (R14D6B-S-1).

## 1. Entry points (6B-1)

- `evaluate_trial(started, sources, trial_id, attempt_id, read)`: steps 2-4 for one
  attempt; the caller names the attempt, and before any protected-data read the module requires it to
  satisfy the attempt-binding rule (§3) for `trial_id` and to be `running` (no result entry,
  no outcome); appends the attempt's result entry under the look lock (§3 rule 4). It
  writes no outcome.
- `evaluate_look(started, sources, read, persist)`: steps 2-8; appends the look entry (§4)
  before any protected-data read; builds the evaluation and sealing records, hands their exact bytes to
  the caller's `persist` (R14D6B7-A-1; §12), and only after `persist` returns appends the
  closing entry (§4) as its last act. It also returns both records.

Each runs in a fresh process that first calls `start` (6a, final on refusal) and passes
the `Started` it returned; it repeats steps 2-3 from the governing records (R14D6B9-F-5).

`sources` (R14D6B9-F-5) holds exactly: `ledger_path`; `acceptance_record` (bytes; must hash
to `started.chain_log["acceptance_record_sha256"]` before use, then gives `block_hash` and
height `h`); `headers` (six 80-byte headers); `beacon`; `capture_record` (bytes); and
`object_dir` (the qualification object). `evaluate_trial` uses `ledger_path`,
`acceptance_record`, `headers`, `beacon`, `capture_record` (for the seeds) and `object_dir`
only as steps 2-4 need.

## 2. Sources

| Input | Source | Check |
|---|---|---|
| Signed C2 rows | `protocol_row` (§7) | `start` verified the bytes |
| Declared trials, configuration hashes | `Started.declaration` (as lockbox `_check_declared`) | `start` verified the chain |
| `data_manifest_sha256`, `last_seen`, `embargo_days`, ledger anchor `{head_hash, entry_count}` | **the declaration only** (one source each) **[OWNER] A-1, A-2** | declaration verified by `start` |
| Ledger path | caller handle (a path is a property of one machine) | the ledger must extend the declared anchor |
| `cycle_start` (P18-2 day 0), `tip_block_hash` | **header time of the block that includes the post** (owner B-2, C-1). The six 80-byte headers of heights `h..h+5` are a **separate caller handle** (owner C-1); the acceptance record and the pinned chain code are unchanged. The module requires `hash(headers[0]) == acceptance["block_hash"]` (display form `SHA256d(header)[::-1].hex()`, also used for the tip and the capture body) and, on decoded bytes, `headers[i][4:36] == SHA256d(headers[i-1])` in internal byte order; reads day 0 from `headers[0]` bytes 68-71 (little-endian, UTC seconds); sets `tip_block_hash = hash(headers[5])`; logs `headers_sha256` = SHA-256 of the 480 concatenated header bytes | 6b `headers_check`, after `start` |
| Attempt starts and outcomes, result entries, look, closing and termination entries | the attempt ledger | `read_entries` (it verifies the chain) + extension of the anchor + every entry of this cycle after the anchor |
| `now` for the look | one module clock read before step 5, truncated to whole seconds, also passed as `recorded_at_utc` of the look entry | **recorded, not verified**; floor: refused if before `cycle_start` or before the last ledger entry's `recorded_at_utc` (FINAL-F-9) |
| Beacon | caller handle | `derive_seeds` (BLS, 4a) and `drand_chain_hash` (§7) |
| Capture record (fixes the O-6a SPEC §5 capture time `T` and the beacon round) | caller bytes (owner B-1) | schema and offline checks, §2.1 |
| Classifier thresholds | `final_thresholds` of the qualification object | 6b `qualification_report` reads the object directory (caller handle), requires `sha(json.loads(manifest.json)) == protocol_row(started.protocol, "qualification_object_sha256")` (the row `verify_code` checked at `start`, l.2714-2716; not `screen_object_sha256`, R14D6B9-F-1; canonical JSON, as `verify_code` l.2592-2594) and each file's raw-byte SHA-256 equal to its manifest digest as `verify_code` does (l.2592-2600), then takes the report from `qobj.read`; `verify_code` is unchanged (C-1) |
| Bars | `read` gate | §6 |

**A-1 (restated).** The declaration carries the ledger head at declaration time. The
module checks that the ledger it reads **extends** that anchor and that every entry of
this cycle lies after it; a start for this cycle before the anchor is refused. An outcome
entry has no cycle field, so it belongs to a cycle through its start (FINAL-F-6). It
cannot detect a ledger replaced or forked after the anchor by someone who can write the
store; that is a store obligation in the `Store` docstring.

**Residuals (stated, not corrected).**
- *Day 0 (B-2).* A block's header time is set by its miner. Consensus requires it to
  exceed the median time of the previous 11 blocks and to be at most two hours ahead of
  validating nodes' clocks; nothing bounds how far it may lag real time. That the headers
  are on the main chain with valid work stays the verifier's chain-provenance obligation.
- *Non-nominee `d` (FINAL-F-9).* The look takes every trial's `d` from the ledger. Sealing
  recomputes the nominee's, but no non-nominee `d` is recomputed, and every identity field
  is derivable once the beacon is public. A store writer could shape the family matrix
  that G-9 and G-10 use. Same trust as the fork residual, a different act.
- *Clock.* A clock set forward still opens the look early; that only fails families with
  unfinished trials (U_ops).
- *Capture time (R14D6B9-F-6, R14D6B10-A-1).* No offline floor is enforced. Bitcoin's
  two-hour future rule is checked against each node's own clock, so a genuine earliest
  capture can precede `headers[5]` time minus two hours; refusing it would be permanent
  (the SPEC fixes the earliest capture). The evaluation record logs a diagnostic
  `capture_before_tip_window` (true when `timestamp` < `headers[5]` time − 2 h); it
  refuses nothing. A hard floor would need an accepted clock-bound rule
  (**[OWNER]**, S4/SPEC wording), not an invented tolerance. That the capture is genuine and
  earliest stays the store and verifier obligation (§2.1).
- *Unbreached U_proc→U_ops route (R14D6B9-F-6).* In an unbreached family, leaving a sibling
  trial unfinished at day 180 makes the family U_ops even after a U_proc result (§5 rule
  2, as decided). `u_proc_present` is recorded for every family, so this stays countable.
- *Extra start (R14D6B9-F-6).* An extra `start_attempt` in an unbreached family is still a
  cycle-level `CycleError` (`trial_states` l.806-809); it is not one of B-4's three breach
  kinds. The runner's look-lock rule (§3) makes it a runner fault, not a race.
- *Unpersisted outcome (R14D6B9-F-4).* `persist` sees the outcome before the closing
  entry; if it fails or is withheld, the ledger records only `LOOK_WITHOUT_RECORD`, and a
  family-level U_proc known only from the look (e.g. `UNSUPPORTED_LAW`) is not recorded.
  No pick is possible either way. How a `LOOK_WITHOUT_RECORD` cycle is counted is
  **[OWNER] P18-7 wording**.

### 2.1 The capture record (owner B-1, FINAL-F-7)

The capture record is made after the post is accepted (O-6a SPEC §5); the declaration,
already hashed into the post, **cannot** bind it. **[DESIGN schema]**
`aqt.c2.capture_record.v1`, canonical JSON, exact field set
`{schema, url, timestamp, status, digest, body, acceptance_record_sha256}`. The module
checks, offline:
1. `url` is exactly one of the two qualifying URLs for height `h+5`; `timestamp` is 14
   digits; `status == "200"`; the SPEC §5 capture time `T` is `timestamp` (it fixes the beacon round only; `w0` and the window length `T` of §8 come from the signed `c2_start`/`c2_end`, `check_eligibility`);
2. `body` is a string; its ASCII-encoded bytes are hashed for item 3, and it equals `tip_block_hash` exactly (no trailing newline allowed unless the
   known-answer test shows the endpoint returns one);
3. `body` hashes to `digest` (CDX digest: base32 SHA-1 of the payload). **[VERIFY]** the
   digest form with a known capture before signing;
4. `acceptance_record_sha256` equals the acceptance record's SHA-256.

It logs `capture_record_sha256`. **Residual** (store and verifier obligation, next to
R14L2-S-2): that the record is genuine and is the earliest qualifying capture; the SPEC's
earlier-capture invalidation rule covers a wrong choice.

**Order** inside `evaluate_look`, all before any protected-data read:
1. `start`;
2. `headers_check`; `check_declaration`, `check_screen_record`, `check_eligibility` (signed
   `confirmation_start`, `confirmation_end`);
3. capture-record checks (§2.1), then `derive_seeds` (failure is read-free, S-8);
4. take the exclusive look lock (§4); ledger: `read_entries`, anchor rules, termination
   and look checks (§5.1), well-formed look/closing/termination payloads (malformed →
   `CycleError`), each start's `protocol_hash` equal to the signed protocol hash,
   `family_attempts`, the result-entry rules of §3 (which set each attempt's completion),
   then `trial_states` on the rewritten attempts of unbreached families; breached families
   get §3 rule 1's states;
5. clock read and floor; `look_allowed` (day 180 from `cycle_start`; breached families are
   not waited for, owner C-2);
6. classifier thresholds for each family's `(K_f, T)` (§8);
7. append the look entry (§4) with `recorded_at_utc` = the step-5 value, release the look
   lock, then re-read the ledger (§4 rule on intervening entries);
8. only now `read`, the manifest check and C-T (§6).

`evaluate_trial` runs 1-4 without the look lock (no look, closing or termination entry may
exist; its family must have no order breach), reads, then appends under the look lock
(§3 rule 4).

## 3. The result entry and attempt completion (owner B-4)

The pre-look record `aqt.c2.trial_result.v2` is written **as the payload** of one ledger
entry, `record_type = "aqt.c2.trial_result_entry.v1"`:

```
{schema, cycle_id, trial_id, family, configuration_hash, attempt_id,
 trial_index, seed_l266, estimator_seed, data_manifest_sha256,
 protocol_hash, engine_commit, confirmation_module_sha256, image_digest,
 window_id, days, d, d_sha256, reason}
```

`seed_l266`, `estimator_seed`, `trial_index` are this process's own values from line 266
and `derive_seeds`. `record_sha256 = SHA256(cj(payload))` is the record's identity.
Appended with `aqt.core.ledger.append_entry`. An unavailable run writes `d: null` and its
reason; it is still a result entry.

**Attempt binding (FINAL-F-6).** A result entry's `attempt_id` must be a start of this
cycle, after the anchor and before the entry, whose `(hypothesis_hash, trial_index)` maps
to the entry's `trial_id`; otherwise `CycleError`. Outcomes are matched to starts of this
cycle only; duplicate outcomes of other cycles are ignored; an outcome with no start is a
`CycleError` (as `finish_attempt` cannot write one).

**Completion is derived from the result entry, not the runner's outcome word.** An attempt
is **completed** when it has exactly one result entry, after its start and before any
outcome entry. Any outcome may follow. An attempt with no result entry before its first
outcome is a crash (`CRASH_NO_ARTIFACT`, P18-1), whatever its outcome says **[OWNER]
P18-1 wording: today a `failed` with another code is `final`, not a crash**. The module
rewrites each attempt before calling `trial_states` (§13):
- completed: `outcome="completed"`, `end` = the result entry's ledger position;
- crash: `outcome="failed"`, `reason_code=CRASH_NO_ARTIFACT`, `end` = the first outcome's
  position (so `trial_states` recognises it and the slot order uses the real position).

**Runner rule (Store docstring).** The store's runner writes `start_attempt`, and writes an
outcome only for an attempt with no result entry (crash codes). No one writes a
`completed` outcome for an attempt with a result entry. The runner takes the cycle's look
lock around **every** start and outcome write (look lock, then append lock; R14D6B9-F-3),
and makes its eligibility checks for that write (no look, closing or termination entry;
attempt state) inside the same locked operation (R14D6B10 note), so no runner write lands inside a look's steps 4-7 or between `evaluate_trial`'s locked
re-read and its append.

**Entry rules** at the look:
1. *Order breach* (owner B-4): a result entry after its attempt's outcome, a second result
   entry, or a second outcome for one attempt of this cycle. `family_attempts` reports it
   for that family instead of raising (§13). The family is recorded failed, reason
   `LEDGER_ORDER:<attempt_id>` (the first breaching attempt in ledger order; all breaches
   are listed in the record); cause per §5 (owner C-3). It is not passed to
   `trial_states`; its full attempt history is kept for the record and its states are
   (FINAL-F-2): per trial, last attempt derived-completed → `completed`; last attempt with
   no result entry and no outcome → `running`; no attempt → `unstarted`; anything else →
   `final`; no re-run slot. No
   slot or attempt-count refusal for it can become a cycle-level `CycleError`. The look
   does not wait for a breached family (owner C-2). [OWNER] P18-1/P18-2/P18-7 wording.
2. *Identity breach*: for each result entry, **every** identity field is compared with what
   the module derives now: `cycle_id`, `trial_id`, `family`, `configuration_hash` (the
   declaration's), `trial_index`, `seed_l266`, `estimator_seed`, `data_manifest_sha256`,
   the four code-identity fields (`Started`) and `window_id`; `attempt_id` by the binding
   rule above. A malformed entry or a mismatch: `CycleError`, no read, nothing written; the
   cycle ends by the store's termination entry (§5.1). Then `completed_entry` decodes `d`
   exactly. Well-formed `days` that differ from the window's are **not** an identity
   breach: that family is U_ops `MISALIGNED_SERIES` (§5). `completed_entry` changes:
   `window_id` against the governing window; days checked for form only (canonical UTC,
   consecutive, non-empty; malformed → `CycleError`); its days-own-window check removed;
   `d`/`d_sha256` integrity kept.
3. A result entry after the look entry is ignored by that look (the trial was `running`
   at the look); it stays in the ledger as a recorded late result.
4. `evaluate_trial` refuses, before any protected-data read, when its attempt already has a result entry
   or an outcome, when a look, closing or termination entry exists for the cycle, or when
   its family has an order breach (C-2). After its read it takes the look lock, re-reads
   the ledger, refuses without appending if any of these now holds, appends, and releases
   (FINAL-F-4). So no result lands inside a look's steps 4-7, and a double launch gives one
   entry and one refusal.

Tests: honest sequences (unavailable run; outcome racing the result entry; crash after the
entry; A writes its result and dies with no outcome while B crashes → A completed, B has
the slot and may re-run; a `failed` with another code and no result entry → crash) give
the stated states and never a `CycleError`; an order breach (double outcome; duplicate
crash outcome after a legitimate re-run) gives that family `LEDGER_ORDER`, the stated
states, no wait at the look, `evaluate_trial` refusal, and leaves the other family; shifted
`days` give U_ops `MISALIGNED_SERIES`; a moved record, wrong seed, other manifest, other
`window_id`, unknown or early `attempt_id`, start with another `protocol_hash` each refuse;
a double `evaluate_trial` launch gives one entry.

## 4. The look entry and the closing entry

`record_type = "aqt.c2.look_entry.v1"`, payload `{cycle_id, families, ledger_head_before,
now, confirmation_module_sha256}`, appended at §2 step 7, before any protected-data read. `look_allowed`
uses the step-5 clock value, so a premature call is refused **before** any entry is
written. `look_allowed` and `evaluate_look` refuse when a look entry already exists for
the cycle: **one look per cycle, no second look** (P18-2).

**Look lock.** An exclusive OS file lock on its own sidecar (`<ledger>.look.lock`, distinct
from `append_entry`'s lock), held by `evaluate_look` from step 4 through the step-7 append
and by `evaluate_trial` around its final re-check and append; released in a `finally`.
Order is always look lock → append lock. A dead process releases the OS lock; the sidecar
file's existence is not itself a lock. A second concurrent look waits, then sees the look
entry at step 4 and refuses without appending. Store obligation: every caller for a cycle
uses the same ledger path on one host.

**Intervening entries.** After the append the module re-reads the ledger. Entries of other
cycles between step 4's head and the look entry are allowed. An intervening entry of this
cycle means step 4 did not see the cycle's final ledger; the look stops with no records.

**Closing entry (FINAL-F-5).** `record_type = "aqt.c2.look_closing_entry.v1"`, payload
`{cycle_id, evaluation_record_sha256, sealing_record_sha256}`, appended by `evaluate_look`
as its last act, only after `persist` has returned for both records' exact bytes
(R14D6B7-A-1). A closing entry therefore means both records were durably stored. A crash
after `persist` and before the closing entry leaves stored records but no closing entry:
`LOOK_WITHOUT_RECORD`, no pick (conservative). A verifier treats a closing entry whose
hashes match no stored record as a store failure.

**A look entry without a closing entry** (intervening entry, or any abort after the look
entry, including between the evaluation and the sealing record) ends the research phase of
the cycle with **no pick and no promotion**. The store appends a termination entry (§5.1)
with kind `LOOK_WITHOUT_RECORD` (owner B-3; rev 7 reads it as "no closing entry", which
also covers an evaluation record without a sealing record **[OWNER] confirm**). Tests:
early look leaves no entry; an intervening entry of another cycle is allowed; one of this
cycle stops the look; two concurrent looks give one look entry and one refusal; an abort
after the evaluation record leaves no closing entry.

## 5. Unavailable runs and their cause (A-3, B-5, owner C-3)

- `completed_entry` returns `(configuration_hash, days, d, reason)`.
- `nominate` examines **all** trials of the family before coding, with this precedence:
  1. **order-breached family only** (owner C-3, R14D6B7-A-3): if `u_proc_present` →
     **U_proc**, else **U_ops** (a breach cannot move a procedure failure out of
     `U_proc^R`);
  2. otherwise (unbreached), unchanged from rev 6: any trial not completed (state
     `running`, `unstarted`, `rerun`, `undetermined`, `final`) or well-formed `days` that
     differ from the window's (`MISALIGNED_SERIES`) → **U_ops** (P18-7 infrastructure
     first; DESIGN l.110: unfinished at day 180 is U_ops);
  3. else any failing trial whose reason is in `U_OPS_REASONS` → **U_ops**;
  4. else any failing trial → **U_proc**.
  **`u_proc_present`** (R14D6B7-A-2) is computed **before** any state or result
  collapsing: the OR, over **every** identity-valid result entry of the family before the
  look entry (duplicate, superseded and post-outcome ones included), of "an unavailable
  result whose reason is not in `U_OPS_REASONS`". The family record keeps each such
  result as `{attempt_id, result_entry_hash, reason}` in `u_proc_results`.
  Its message lists every failing trial as `"<id>: <reason or state>"`. The family record
  also carries `failing{id: reason or state}` (last attempt), `u_proc_results` and
  `u_proc_present`, so a verifier can count either way. Tests: a `DAYS_INCOMPLETE` result
  followed by a duplicate result (breach) → U_proc; in a breached family, a superseded
  attempt's U_proc result → U_proc (in an unbreached family a start after a result entry
  is a `CycleError`, l.806-809); an unbreached family with one running trial and one `DAYS_INCOMPLETE` → U_ops
  (as rev 6). **[OWNER] C-3 changes P18-7's "infrastructure first" ordering for breached
  families only; S4 wording needed.**
- `U_OPS_REASONS` is **unchanged** (owner B-5): `DAYS_INCOMPLETE` stays U_proc. The reason
  list itself remains `[DESIGN: list for review]` and an S4 contract item (A-7).
- The configuration-hash mismatch is a `CycleError` at §3 rule 2; `nominate` keeps its own
  check as a defence.
- `family_attempts` returns `attempt_id` too.

### 5.1 Termination and invalidation entries

`record_type = "aqt.c2.termination_entry.v1"`, payload `{cycle_id, kind, reason}`, in the
same anchored ledger, appended by the store on human action (invalidation under SPEC §5,
pre-pick termination, `LOOK_WITHOUT_RECORD`). Both entry points refuse when one exists for
the cycle. Residual: the module cannot know of an invalidation nobody recorded.

## 6. Reading and the data manifest (S-3) **[OWNER] A-4 (restated)**

`read` returns only the cycle's composite manifest and the BTC and ETH `BarSeries` for the
**whole** partitions the trials touch (confirmation, and exploration where a warm-up
reaches back into it). The module:
1. verifies the composite with `verify_composite_manifest`; requires its hash to equal the
   declaration's `data_manifest_sha256`, its `cycle_id` the cycle's, and its
   `protocol_sha256` the signed C2 protocol hash `start` verified;
2. takes each partition manifest from `composite.partitions` (by partition and symbol) and
   calls `verify_partition_manifest(entry, series=served)`; no separately served manifest
   is accepted;
3. cuts `[w0 − W, w1)` itself, then runs `check_confirmation_read` (C-T). Bars it holds
   before `w0 − W` (whole partitions) are not used.

The lockbox enters only as the composite's sealed reference (hash only). Tests: a true
composite beside other self-consistent manifests and bars; the right manifest with other
bars; a cut that misses the warm-up; another `cycle_id`. Who may call `read` is the
store's and image's obligation.

## 7. Signed C2 rows (OD-4)

Read only through `protocol_row`, each once, no defaults, with an exact parse per type:
integers as `[0-9]+` with no sign or leading zero; times as `YYYY-MM-DDTHH:MM:SSZ`;
decimals as the D-19 decimal-string form, **compared as strings**; hashes as 64 lower-case
hex; enumerations by exact string membership.

| Row | Feeds |
|---|---|
| `drand_public_key`, `drand_genesis_time`, `drand_period`, `drand_chain_hash` | `Chain`; `drand_chain_hash` must equal drand's chain-info hash. **[VERIFY]** chain-info layout pinned with a known-answer test before signing |
| `drand_scheme` | must equal `SCHEME` exactly |
| `confirmation_start`, `confirmation_end` | `check_eligibility` (S-9) |
| `t_min`, `g_days` | `check_eligibility`, `nominee_gates` |
| `z_crit` | G-9; must equal the qualification object's `z_crit` as a decimal string |
| `family_block_rule` | `nominate`; must be in `choices.RULES` and equal the qualification object's `family_block_rule` (`dsr.family_block` treats any other value as median) |
| `canonical_benchmark_sha256` | G-13 |

## 8. The supported-law classifier (S-5)

Thresholds come from the qualification report 6b re-reads (§2):
`frozen = final_thresholds["T=<T>"]`, `pool = ({n: float(v) for n, v in frozen[s].items()}
for s in ("upper", "lower"))` exactly as `scripts/d19_heldout.py:188-191`, then
`upper, lower = reduce.for_k(pool, K_f)`; the local check is
`within_law = lambda x, lengths: classifier.within(classifier.diagnostics(x), upper,
lower)`. No re-pooling, no caller bytes, no extra row. `nominate` never runs without it.

**Chosen reading:** a missing `T=<T>` key or a `for_k` error refuses the whole look before
any read (both families, no record). Because `T` and each `K_f` are known at declaration,
the store's declaration builder must check both have thresholds before posting (Store
docstring).

## 9. What the DSR part records (F-8 owner decision)

Only what the frozen code returns: per family, `dsr.evaluate`'s `FamilyResult`
(`reason`, `block`, `capped`, `nominee`, `z`, `s0`, `length_ratio`, `columns`), for method V
and for the Task 12 numerics `nominate` already runs. `decision` is the Task 12
`FamilyResult.reason` and nominee; `differs` is true when the nominee, the availability
reason or the G-9 result differ between V and Task 12 (A-V1). No per-trial S_j, D_j or z_j
is computed. Nothing reads the C-14 CPCV report (diagnostic only, LG5B-6).

DESIGN §5.2 step 4 is corrected: the pre-look record keeps `d` and `d_sha256`; the
nominee's z exists only at the look.

## 10. Two records (S-7) **[OWNER] A-7**

- **Evaluation record** `aqt.c2.evaluation.v1`, built after steps 1-8:
  `{schema, cycle_id, chain_log, signed{rows used}, declaration_sha256, headers_sha256,
  capture_record_sha256, capture_before_tip_window, eligibility{w0, T, cycle_start}, seeds, ledger{anchor, head_hash,
  entry_count, look_entry_hash}, trials{id: record_sha256}, families{f: {states, A_f,
  reason, cause, failing, u_proc_results, u_proc_present, nominee, dsr{V, task12, decision, differs},
  gates{G-n: {result, reason, values}}, outcome, cpcv (diagnostic_only)}}}`. Floats hexf.
  `evaluation_record_sha256 = SHA256(cj(record))`.
- **Sealing record**: `seal_family` per declared family and `sealing_record(declared)`,
  taking `evaluation_record_sha256`; every status (a)-(d) and sealing failure lives only
  here.

Both are passed to `persist` and returned; the closing entry (§4), appended after
`persist` returns, binds their hashes in the ledger.

## 11. Failure (P18-7, R-14a item 7)

- Before the look entry (§2 steps 1-6): `CycleError`, nothing read, nothing written. A
  pre-pick termination is the store's termination entry (§5.1), not an evaluation record.
- After the look entry: a family whose gates, order rule or sealing fail is recorded with
  its cause, never dropped. Any other abort leaves the look entry without a closing entry:
  no pick, no second look, termination entry `LOOK_WITHOUT_RECORD` (§4).

## 12. Not in 6b

No storage of its own (the module calls the caller's `persist` and appends ledger entries
only), no lockbox, no promotion, no lockbox data. Store obligations are written in a
`Store` docstring, as the lockbox does, including: `persist(evaluation_bytes,
sealing_bytes)` returns only after both exact byte strings are durably written (fsync)
and raises otherwise (R14D6B7-A-1); and (R14D6B9-F-2) a stored evaluation or sealing record
is released to anything, the lockbox `begin_read` included, only when the ledger holds
this cycle's closing entry whose two hashes equal the stored bytes' hashes and no
termination entry for the cycle; `persist` writes where nothing is released before that.
No change to `c2_lockbox.py`. Store-build test: persisted records, no closing entry →
release refused.

## 13. Contract changes to reviewed code

- **None** in the section pinned to `c2_lockbox.py`: `ACCEPTANCE_FIELDS`, `verify_chain`,
  `verify_code` and the rest of the start chain stay byte-identical (owner C-1,
  FINAL-F-1). New 6b functions: `headers_check`, the qualification re-read, the capture
  record check.
- `family_attempts`: per-family order-breach report instead of `CycleError` for a second
  outcome; outcomes matched to this cycle's starts only; outcome without a start →
  `CycleError`.
- `trial_states`: takes attempts rewritten by §3 (completed and crash rewrites, `outcome`,
  `reason_code`, `end`); called only for unbreached families.
- `completed_entry`: takes the governing window; `window_id` against it; days form-only;
  returns `(configuration_hash, days, d, reason)`.
- `family_attempts`: also returns `attempt_id`.
- `nominate`: new inputs (the per-family breach report and every pre-look result entry);
  new shape of `completed` per §5.
- `trial_result`: new inputs for the v2 fields (§3).
- `look_allowed`: `looked` from the look entry, `terminated` from termination entries,
  `now` from the step-5 clock read with its floor; breached families not waited for.
- `TRIAL_RESULT_SCHEMA` v2 and `_TRIAL_RESULT_KEYS` as §3.
- `nominate`: §5 precedence (C-3 for breached families only), `failing`, `u_proc_results`,
  `u_proc_present` over all pre-look results, the order-breach reason.

## Owner items after rev 11

| ID | Item | Status |
|---|---|---|
| A-1 | Ledger anchor (head, count) in the declaration; replacement/fork after it a store obligation | recommendation as §2 |
| A-2 | `last_seen`, `embargo_days` in the declaration | recommendation as §2 |
| A-4 | Composite manifest + whole partitions served by `read` | recommendation as §6 |
| A-7 | Two-record output contract; U_ops reason list | recommendation as §10, §5 |
| OD-4 | Row names and parse rules | recommendation as §7 |
| B-1 | Capture record offline checks; record genuine/earliest is a store obligation | decided as direction; **S4/SPEC wording** |
| B-2, C-1 | Day 0 = block time; six headers as a separate caller handle (extends the one-header selection) | decided as direction; **S4 wording** |
| B-3 | `LOOK_WITHOUT_RECORD`; read as "no closing entry", covering evaluation without sealing and records stored with no closing entry (never released, §12) | decided; the "no closing entry" reading **to confirm**; how such a cycle is counted **[OWNER]**; **P18-2/P18-7 wording** |
| B-4, C-2 | Order breach fails only that family; look does not wait for it; `evaluate_trial` refuses for it | decided as direction; **P18-1/P18-2/P18-7 wording** |
| C-3 | Breached family with any pre-look U_proc result counts as U_proc (unbreached families keep rev 6 precedence); `u_proc_present` recorded | decided as direction; **P18-7 wording** |
| — | No result entry before the first outcome = crash whatever the outcome says (changes who may get the P18-1 slot) | design proposal; **P18-1 wording, to confirm** |
| B-5 | `DAYS_INCOMPLETE` U_proc | decided |
| A-3, F-8 | split by reason; record only frozen output | decided |
| A-5, A-6 | capture hash in declaration; separate thresholds | withdrawn |
