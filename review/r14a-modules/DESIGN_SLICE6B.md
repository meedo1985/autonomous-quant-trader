# Slice 6b design, rev 4: the confirmation evaluation run and the C2 evaluation record

- Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-14. History: rev 1 `1e6e672`
  (Sol FIX R14D6B-S-1..9); rev 2 `9d34615` (Fable FIX R14D6B2-F-1..19); rev 3 `5cd2a29`
  (Fable re-check FIX R14D6B3-F-1..13, record `2a7e17a`, adjudication
  `ADJUDICATION_RECHECK_DESIGN_SLICE6B_5CD2A29.md`, all accepted). Rev 4 applies that
  adjudication and the owner's decisions in `OWNER_DECISIONS_DESIGN_SLICE6B_REV3.md`
  (B-1, B-2, B-4, B-5) on top of `OWNER_DECISIONS_DESIGN_SLICE6B_REV2.md`.
- A proposal for review before the orchestration is built. It approves nothing and closes
  no owner item. **[OWNER]** marks bindings for the signed C2 or the S4 text. Owner
  decisions recorded as direction still need the Constitution's process where they touch
  P18 or S4 wording.
- **§16 (fact, R-14a item 1):** `calibration/c2_confirmation.py` is merged only under
  Constitution §16 review with an independent different-model review record and the
  owner's PR review (R14D6B2-F-8).
- **R-14a item 4:** the module loads data, checks, **calls** frozen code and records. It
  computes no statistic of its own (owner decision on F-8: record only frozen output).
- Scope: DESIGN §5.2 steps 2-8 and §7.2, after slice 6a's `start`. 6b part 1 (`cc197be`
  .. `b350264`) stays and is extended.

Rule: the caller passes **handles** (paths, a read gate, the beacon, the capture record
bytes); every value the module can read or verify from a governing record it reads and
verifies itself (R14D6B-S-1).

## 1. Entry points (6B-1)

- `evaluate_trial(started, sources, trial_id, read)`: steps 2-4 for one attempt; appends
  the attempt's result entry and then its `completed` outcome (§3).
- `evaluate_look(started, sources, read)`: steps 2-8; appends the look entry (§4) before
  any read; writes the evaluation and sealing records.

Each runs in a fresh process whose first act is `start` (6a, final on refusal), and
repeats steps 2-3 from the governing records.

## 2. Sources

| Input | Source | Check |
|---|---|---|
| Signed C2 rows | `protocol_row` (§7) | `start` verified the bytes |
| Declared trials, configuration hashes | `Started.declaration` (as lockbox `_check_declared`) | `start` verified the chain |
| `data_manifest_sha256`, `last_seen`, `embargo_days`, ledger anchor `{head_hash, entry_count}` | **the declaration only** (one source each) **[OWNER] A-1, A-2** | declaration verified by `start` |
| Ledger path | caller handle (F3-11: a path is a property of one machine) | the ledger must extend the declared anchor |
| `cycle_start` (P18-2 day 0) | **header time of the block that includes the post** (owner B-2). The acceptance record gains `block_header` (80 bytes, hex); `start` requires `SHA256d(header)` byte-reversed to equal `block_hash` and reads the time field (bytes 68-71, little-endian, UTC seconds) | `start` (6a change, §13) |
| Attempt starts and outcomes, result entries, look entry, termination entries | the attempt ledger | `read_entries` (it verifies the chain) + extension of the anchor + every entry of this cycle after the anchor |
| `now` for the look | one module clock read before step 5, truncated to whole seconds, also passed as `recorded_at_utc` of the look entry (F3-3) | **recorded, not verified**: it is the appender's clock |
| Beacon | caller handle | `derive_seeds` (BLS, 4a) and `drand_chain_hash` (§7) |
| Capture record (fixes `T` and the beacon round) | caller bytes (owner B-1) | offline checks, §2.1 |
| Classifier thresholds | `final_thresholds` of the qualification object `start` verified | `start` keeps the report (§13) |
| Bars | `read` gate | §6 |

**A-1 (restated).** The declaration carries the ledger head at declaration time. The
module checks that the ledger it reads **extends** that anchor and that every entry of
this cycle (start, outcome, result, look, termination) lies after it; a start for this
cycle before the anchor is refused. It cannot detect a ledger replaced or forked after the
anchor by someone who can write the store; that is a store obligation in the `Store`
docstring.

**Day 0 residual (B-2).** A block's header time is set by its miner; consensus allows it
to differ from real time by up to about two hours. The 180-day count therefore carries
that tolerance. Stated, not corrected.

### 2.1 The capture record (owner B-1, F3-1)

The capture record is made after the post is accepted (O-6a SPEC §5); the declaration,
already hashed into the post, **cannot** bind it. The module takes the record as bytes
and checks, offline:
1. its original body equals the acceptance record's tip block hash;
2. its CDX row has the 14-digit UTC timestamp form, an exact qualifying URL for height
   `h+5`, archived status `200`, and the `id_` fetch names the same URL, timestamp and
   digest;
3. it names the acceptance record's SHA-256.

It logs `capture_record_sha256` in the evaluation record. **Residual** (store and verifier
obligation, next to R14L2-S-2): that the record is genuine and is the earliest qualifying
capture; the SPEC's earlier-capture invalidation rule covers a wrong choice.

**Order** inside `evaluate_look`, all before any read:
1. `start`;
2. `check_declaration`, `check_screen_record`, `check_eligibility` (signed
   `confirmation_start`, `confirmation_end`);
3. capture-record checks (§2.1), then `derive_seeds` (failure is read-free, S-8);
4. ledger: `read_entries`, anchor rules, termination check (§5.1), `family_attempts`,
   the result-entry rules of §3 (which set each attempt's completion), then
   `trial_states` on the rewritten outcomes;
5. clock read; `look_allowed` (day 180 from `cycle_start`);
6. classifier thresholds for each family's `(K_f, T)` (§8);
7. append the look entry (§4) with `recorded_at_utc` = the step-5 value, then re-read the
   ledger (§4 rule on intervening entries);
8. only now `read`, the manifest check and C-T (§6).

`evaluate_trial` runs 1-4 (no look entry and no termination may exist), then reads,
appends its result entry and calls `finish_attempt(outcome="completed")`.

## 3. The result entry and attempt completion (F3-5, owner B-4)

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

**Completion is derived from the result entry, not the runner's outcome word.** An attempt
is **completed** when it has exactly one result entry, after its start and before any
outcome entry. Any outcome may follow. An attempt with no result entry before its first
outcome is a crash (`CRASH_NO_ARTIFACT`, P18-1), whatever its outcome says. The module
rewrites each attempt's outcome this way and then calls `trial_states` (contract change,
§13).

**Runner rule (Store docstring).** The store's runner writes `start_attempt`, and writes an
outcome only for an attempt with no result entry (crash codes). `evaluate_trial` writes the
`completed` outcome itself.

**Entry rules** at the look:
1. *Order breach* (owner B-4): a result entry after its attempt's outcome, or a second
   result entry for one attempt. The family is recorded failed, cause **U_ops**, reason
   `LEDGER_ORDER:<attempt_id>`; the breaching attempt does not take the family's re-run
   slot; the other family is unaffected. [OWNER] P18-1/P18-7 wording.
2. *Identity breach*: for each result entry, **every** identity field is compared with what
   the module derives now: `cycle_id`, `trial_id`, `family`, `configuration_hash` (the
   declaration's), `attempt_id`, `trial_index`, `seed_l266`, `estimator_seed`,
   `data_manifest_sha256`, the four code-identity fields (`Started`), `window_id` and `days`.
   A mismatch is not an honest sequence: `CycleError`, no read, nothing written; the cycle
   ends by the store's termination entry (§5.1). Then `completed_entry` decodes `d` exactly.
3. A result entry after the look entry is ignored by that look (the trial was `running` at
   the look and is U_ops by §5); it stays in the ledger as a recorded late result (F3-13).
4. `evaluate_trial` refuses when its attempt already has a result entry or an outcome, or
   when a look or termination entry exists for the cycle.

Tests: honest sequences (unavailable run; outcome racing the result entry; crash after the
entry) give the stated states and never a `CycleError`; an order breach gives that family
U_ops `LEDGER_ORDER` and leaves the other family; a moved record, wrong seed, other
manifest each refuse.

## 4. The look entry (F3-3, F3-4)

`record_type = "aqt.c2.look_entry.v1"`, payload `{cycle_id, families, ledger_head_before,
now, confirmation_module_sha256}`, appended at §2 step 7, before any read. `look_allowed`
uses the step-5 clock value, so a premature call is refused **before** any entry is
written. `look_allowed` and `evaluate_look` refuse when a look entry already exists for
the cycle: **one look per cycle, no second look** (P18-2).

**Intervening entries.** After the append the module re-reads the ledger. Entries of other
cycles between step 4's head and the look entry are allowed. An intervening entry of this
cycle means step 4 did not see the cycle's final ledger; the look stops with no evaluation
record (next paragraph). Store obligation: no runner writes this cycle's entries while a
look runs.

**A look entry without an evaluation record** (intervening entry, or any abort after the
append) ends the research phase of the cycle with **no pick and no promotion**. The store
appends a termination entry (§5.1) with kind `LOOK_WITHOUT_RECORD` **[OWNER] B-3: label
and wording proposed by the author, not decided**. Tests: early look leaves no entry; an
intervening entry of another cycle is allowed; one of this cycle stops the look.

## 5. Unavailable runs and their cause (A-3, F3-7, owner B-5)

- `completed_entry` returns `(configuration_hash, days, d, reason)`.
- `nominate` examines **all** trials of the family before coding, with this precedence:
  1. any trial not completed (state `running`, `unstarted`, `rerun`, `undetermined`,
     `final` without result), an order breach (§3 rule 1), or a day-index mismatch →
     **U_ops** (P18-7 infrastructure first; DESIGN l.110: unfinished at day 180 is U_ops);
  2. else any failing trial whose reason is in `U_OPS_REASONS` → **U_ops**;
  3. else any failing trial → **U_proc**.
  Its message lists every failing trial as `"<id>: <reason or state>"`.
- `U_OPS_REASONS` is **unchanged** (owner B-5): `DAYS_INCOMPLETE` stays U_proc, as a
  trial's own failure on accepted bars. The reason list itself remains `[DESIGN: list for
  review]` and an S4 contract item (A-7).
- The configuration-hash mismatch is a `CycleError` at §3 rule 2; `nominate` keeps its own
  check as a defence.
- `family_attempts` returns `attempt_id` too.

### 5.1 Termination and invalidation entries (F3-9)

`record_type = "aqt.c2.termination_entry.v1"`, payload `{cycle_id, kind, reason}`, in the
same anchored ledger, appended by the store on human action (invalidation under SPEC §5,
pre-pick termination, `LOOK_WITHOUT_RECORD`). Both entry points refuse when one exists for
the cycle. Residual: the module cannot know of an invalidation nobody recorded.

## 6. Reading and the data manifest (S-3, F3-6) **[OWNER] A-4 (restated)**

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

## 7. Signed C2 rows (OD-4, F3-10)

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

## 8. The supported-law classifier (S-5, F3-12)

Thresholds come from the qualification report `start` keeps:
`frozen = final_thresholds["T=<T>"]`, `pool = ({n: float(v) for n, v in frozen[s].items()}
for s in ("upper", "lower"))` exactly as `scripts/d19_heldout.py:188-191`, then
`upper, lower = reduce.for_k(pool, K_f)`; the local check is
`within_law = lambda x, lengths: classifier.within(classifier.diagnostics(x), upper,
lower)`. No re-pooling, no caller bytes, no extra row. `nominate` never runs without it.

**Chosen reading:** a missing `T=<T>` key or a `for_k` error refuses the whole look before
any read (both families, no record). Because `T` and each `K_f` are known at declaration,
the store's declaration builder must check both have thresholds before posting, so an
unevaluable cycle is not declared (Store docstring).

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

- **Evaluation record** `aqt.c2.evaluation.v1`, written after steps 1-8:
  `{schema, cycle_id, chain_log, signed{rows used}, declaration_sha256,
  capture_record_sha256, eligibility{w0, T, cycle_start}, seeds, ledger{anchor, head_hash,
  entry_count, look_entry_hash}, trials{id: record_sha256}, families{f: {states, A_f,
  reason, cause, nominee, dsr{V, task12, decision, differs}, gates{G-n: {result, reason,
  values}}, outcome, cpcv (diagnostic_only)}}}`. Floats hexf.
  `evaluation_record_sha256 = SHA256(cj(record))`.
- **Sealing record**: `seal_family` per declared family and `sealing_record(declared)`,
  taking `evaluation_record_sha256`; every status (a)-(d) and sealing failure lives only
  here.

## 11. Failure (P18-7, R-14a item 7)

- Before the look entry (§2 steps 1-6): `CycleError`, nothing read, nothing written. A
  pre-pick termination is the store's termination entry (§5.1), not an evaluation record.
- After the look entry: a family whose gates, order rule or sealing fail is recorded with
  its cause, never dropped. Any other abort leaves the look entry without an evaluation
  record: no pick, no second look, termination entry `LOOK_WITHOUT_RECORD` (§4).

## 12. Not in 6b

No storage, no lockbox, no promotion, no lockbox data. Store obligations are written in a
`Store` docstring, as the lockbox does.

## 13. Contract changes to reviewed code (F3-11)

- 6a `start`/`verify_code`: keep the qualification report (`final_thresholds`, `z_crit`,
  `family_block_rule`) in `Started`; today `verify_code` discards it (l.2601).
- 6a acceptance record: `ACCEPTANCE_FIELDS` gains `block_header`; `start` checks it and
  puts `cycle_start` in `Started` (B-2).
- `trial_states`: takes outcomes already rewritten by §3's completion rule.
- `look_allowed`: `looked` from the look entry, `terminated` from termination entries,
  `now` from the step-5 clock read.
- `TRIAL_RESULT_SCHEMA` v2 and `_TRIAL_RESULT_KEYS` as §3.
- `nominate`: §5 precedence and the order-breach cause.

## Owner items after rev 4

| ID | Item | Status |
|---|---|---|
| A-1 | Ledger anchor (head, count) in the declaration; replacement/fork after it a store obligation | recommendation as §2 |
| A-2 | `last_seen`, `embargo_days` in the declaration | recommendation as §2 |
| A-4 | Composite manifest + whole partitions served by `read` | recommendation as §6 |
| A-7 | Two-record output contract; U_ops reason list | recommendation as §10, §5 |
| OD-4 | Row names and parse rules | recommendation as §7 |
| B-3 | Label and wording for a look entry without an evaluation record | **open**, proposal `LOOK_WITHOUT_RECORD` (§4) |
| B-1, B-2, B-4, B-5 | capture record offline checks; day 0 = block time; order breach → family U_ops; `DAYS_INCOMPLETE` U_proc | decided 2026-11-14 as direction; B-2 and B-4 need S4/P18 wording |
| A-3, F-8 | split by reason; record only frozen output | decided |
| A-5 | capture record hashed in the declaration | **withdrawn** (impossible, F3-1; replaced by B-1) |
| A-6 | separate thresholds | withdrawn |
