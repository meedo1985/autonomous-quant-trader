# Slice 6b design, rev 3: the confirmation evaluation run and the C2 evaluation record

- Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-13. History: rev 1 `1e6e672`
  (Sol FIX R14D6B-S-1..9); rev 2 `9d34615` (Fable FIX R14D6B2-F-1..19, record `2ca9a33`,
  adjudication `ADJUDICATION_DESIGN_SLICE6B_9D34615.md`, all accepted). Rev 3 applies that
  adjudication and the owner's decisions in `OWNER_DECISIONS_DESIGN_SLICE6B_REV2.md`.
- A proposal for review before the orchestration is built. It approves nothing and closes
  no owner item. **[OWNER]** marks bindings for the signed C2 or the S4 text.
- **§16 (fact, R-14a item 1):** `calibration/c2_confirmation.py` is merged only under
  Constitution §16 review with an independent different-model review record and the
  owner's PR review (R14D6B2-F-8).
- **R-14a item 4:** the module loads data, checks, **calls** frozen code and records. It
  computes no statistic of its own (owner decision on F-8: record only frozen output).
- Scope: DESIGN §5.2 steps 2-8 and §7.2, after slice 6a's `start`. 6b part 1 (`cc197be`
  .. `b350264`) stays and is extended.

Rule: the caller passes **handles** (paths, a read gate, the beacon); every value the
module can read or verify from a governing record it reads and verifies itself
(R14D6B-S-1).

## 1. Entry points (6B-1)

- `evaluate_trial(started, sources, trial_id, read)`: steps 2-4 for one attempt; appends
  the attempt's result entry (§3).
- `evaluate_look(started, sources, read)`: steps 2, 3, 5-8; appends the look entry (§4)
  before any read; writes the evaluation and sealing records.

Each runs in a fresh process whose first act is `start` (6a, final on refusal), and
repeats steps 2-3 from the governing records.

## 2. Sources

| Input | Source | Check |
|---|---|---|
| Signed C2 rows | `protocol_row` (§6) | `start` verified the bytes |
| Declared trials, configuration hashes | `Started.declaration` (as lockbox `_check_declared`) | `start` verified the chain |
| `data_manifest_sha256`, `last_seen`, `embargo_days`, ledger anchor `{path, head_hash, entry_count}`, capture-record hash | **the declaration only** (F-15: one source each) **[OWNER] A-1, A-2, A-5** | declaration verified by `start` |
| `cycle_start` (P18-2 day 0) | the declaration's posting time, from `start`'s chain log (F-9) | `start` |
| Attempt starts and outcomes, result entries, look entry | the attempt ledger at the anchored path | `read_entries` (it verifies the chain; F-16) + extension of the anchor |
| `now` for the look | the module's own look entry time (§4) | **recorded, not verified** (F-14): it is the appender's clock |
| Beacon | caller handle | `derive_seeds` (BLS, 4a) and `drand_chain_hash` (§6) |
| Capture time for seeds | the capture record, whose SHA-256 the declaration carries (F-13) | hash |
| Classifier thresholds | `final_thresholds` of the qualification object `start` verified (F-1) | `start` |
| Bars | `read` gate | §5 |

**A-1 (restated, F-4).** The declaration carries the ledger path and its head at
declaration time. The module can check only that the ledger it reads **extends** that
anchor. It cannot detect a ledger replaced or forked after the anchor by someone who can
write the store; that is a store obligation, written into a `Store` docstring with the
others. Rev 2's reason for a separate cycle record is withdrawn.

**Order** inside `evaluate_look` (S-4), all before any read:
1. `start`;
2. `check_declaration`, `check_screen_record`, `check_eligibility` (signed
   `confirmation_start`, `confirmation_end`);
3. `derive_seeds` (failure is read-free, S-8);
4. ledger: `read_entries`, anchor extension, `family_attempts`, `trial_states`, the result
   entries under the rules of §3;
5. `look_allowed` (day 180 from `cycle_start`, termination records);
6. classifier thresholds for each family's `(K_f, T)` (§8);
7. append the look entry (§4), then re-read the ledger and require that the only entry
   after step 4's head is that look entry;
8. only now `read`, the C-T check, the manifest check (§5).

`evaluate_trial` runs 1-4 (no look entry may exist yet), then reads and appends.

## 3. The result entry (S-2, F-3, F-11, R14S6-F-3, F-4)

The pre-look record `aqt.c2.trial_result.v2` is written **as the payload** of one ledger
entry, `record_type = "aqt.c2.trial_result_entry.v1"` (F-3: no separate store object):

```
{schema, cycle_id, trial_id, family, configuration_hash, attempt_id,
 trial_index, seed_l266, estimator_seed, data_manifest_sha256,
 protocol_hash, engine_commit, confirmation_module_sha256, image_digest,
 window_id, days, d, d_sha256, reason}
```

`seed_l266`, `estimator_seed`, `trial_index` are this process's own values from line 266
and `derive_seeds`, never caller integers. `record_sha256 = SHA256(cj(payload))` is the
record's identity in the evaluation record. Appended with the frozen
`aqt.core.ledger.append_entry`. Start and outcome entries are written by the store's
runner through `aqt.core.attempts` (`start_attempt`, `finish_attempt`), not by this module.

**Entry rules** (checked at the look; any breach is `CycleError`, no read):
1. At most one result entry per `attempt_id`, and it lies after that attempt's start.
2. If the attempt has an outcome, the result entry lies before it. An outcome with no
   result entry before it makes the attempt **not completed** (P18-1 crash path,
   `CRASH_NO_ARTIFACT`), whatever the outcome says.
3. A result entry for an attempt whose state is not completed, or one after the look
   entry, refuses the look.
4. `evaluate_trial` refuses when its attempt already has a result entry or an outcome, or
   when a look entry exists.
5. For each completed attempt, **every** identity field is compared with what the module
   derives now (F-11): `cycle_id`, `trial_id`, `family`, `configuration_hash` (the
   declaration's), `attempt_id`, `trial_index`, `seed_l266`, `estimator_seed`,
   `data_manifest_sha256`, the four code-identity fields (`Started`), `window_id` and
   `days` (eligibility window). Then `completed_entry` decodes `d` exactly.

Tests: a record moved to another trial, a wrong seed, another manifest, a second entry,
an entry after the outcome, an entry in a crashed attempt, an entry after the look: each
refused.

## 4. The look entry (F-2)

`record_type = "aqt.c2.look_entry.v1"`, payload `{cycle_id, families, ledger_head_before,
confirmation_module_sha256}`, appended by `evaluate_look` at §2 step 7, before any read.
`look_allowed` and `evaluate_look` refuse when a look entry already exists for the cycle,
so a look that aborts after the read cannot be run again. An aborted look leaves its
look entry and no evaluation record; that is the P18-1 crash accounting's case.

## 5. Unavailable runs and their cause (A-3, F-7, F-17)

- `completed_entry` returns `(configuration_hash, days, d, reason)`.
- `nominate` examines **all** trials of the family before coding (F-7). If any failing
  trial's reason is in `U_OPS_REASONS`, the family is U_ops (P18-7: U_ops first);
  otherwise U_proc. Its message lists every failing trial as `"<id>: <reason>"`.
- `U_OPS_REASONS` gains `DAYS_INCOMPLETE`, so trials and gates code it alike:
  `MISSING_DAY`, `DUPLICATED_DAY`, `IRREGULAR_DAY`, `MISALIGNED_SERIES`, `SIGMA_UNBOUND`,
  `DAYS_INCOMPLETE`. Every other reason (`TRIAL_CODE_ERROR`, `OVERLAY_VIOLATION`,
  `EventContractError`, `CostModelError`, `FeatureFactoryError`, other `RunUnavailable`
  reasons) is U_proc.
- `family_attempts` returns `attempt_id` too (F-17).

## 6. Reading and the data manifest (S-3, F-5) **[OWNER] A-4 (restated)**

`read` returns the BTC and ETH `BarSeries` for the **whole** partitions the trials touch
(confirmation, and exploration where a model trial's warm-up reaches back into it),
together with their partition manifests and the cycle's composite manifest. The module:
1. verifies each partition manifest (`verify_partition_manifest`) and the composite
   (`verify_composite_manifest`) with the repository's frozen functions;
2. requires the composite's hash to equal the declaration's `data_manifest_sha256`;
3. requires each served series to encode (`encode_bar_series`) to the hash its partition
   manifest lists;
4. cuts `[w0 − W, w1)` itself, then runs `check_confirmation_read` (C-T).

Consumer-boundary tests: bars from another manifest; the right manifest with other bars;
a cut that misses the warm-up. Who may call `read`, under which identity, is the store's
and image's obligation.

## 7. Signed C2 rows (OD-4, S-8, S-9, F-12, F-15)

Read only through `protocol_row`, each once, no defaults, with an exact parse per type
(F-15): integers as `[0-9]+` with no sign or leading zero; times as
`YYYY-MM-DDTHH:MM:SSZ`; decimals as the D-19 decimal-string form; hashes as 64 lower-case
hex.

| Row | Feeds |
|---|---|
| `drand_public_key`, `drand_genesis_time`, `drand_period`, `drand_scheme`, `drand_chain_hash` | `Chain`; `drand_chain_hash` must equal drand's chain-info hash of the chain parameters. **[VERIFY] F-12:** the exact chain-info layout (it may include the genesis seed and beacon id) is pinned with a known-answer test from drand's published chain info before signing |
| `confirmation_start`, `confirmation_end` | `check_eligibility` (S-9: S4 states them only as these unique rows, or requires equality with the nested values at signing) |
| `t_min`, `g_days` | `check_eligibility`, `nominee_gates` |
| `z_crit` | G-9 |
| `family_block_rule` | `nominate` |
| `canonical_benchmark_sha256` | G-13 |

Removed from rev 2: `classifier_bounds_sha256` (F-1), `data_manifest_sha256` (declaration
only, F-15).

## 8. The supported-law classifier (S-5, F-1)

Thresholds come from the qualification object `start` already verified:
`frozen = final_thresholds["T=<T>"]` for the window's T (missing key refuses), `pool = ({n: float(v) for n, v in frozen[s].items()} for s in ("upper", "lower"))` exactly as `scripts/d19_heldout.py:188-191` builds it, then
`upper, lower = reduce.for_k(pool, K_f)` (its `ValueError` refuses);
`classifier = lambda x, lengths: classifier.within(classifier.diagnostics(x), upper, lower)`.
No re-pooling (re-pooling `cell_bounds` would give the wider development thresholds), no
caller bytes, no extra row. The object's `z_crit` must equal the signed `z_crit`.
`nominate` never runs without a classifier (D-18 O18-2).

## 9. What the DSR part records (F-8 owner decision, F-6, F-10)

Only what the frozen code returns: per family, `dsr.evaluate`'s `FamilyResult`
(`reason`, `block`, `capped`, `nominee`, `z`, `s0`, `length_ratio`, `columns` = per-trial
`(L_j, capped)`), for method V and for the Task 12 numerics that `nominate` already runs,
with the Task 12 decision and any difference from V disclosed (A-V1, F-10). No per-trial
S_j, D_j or z_j is computed by the module. (Should a later version record them, D_j is
`(T−1)·var_b(S*_j)` per Annex B, and z_j uses `var_b`, F-6; that needs a frozen-code
change, option (a).)

DESIGN §5.2 step 4 is corrected: the pre-look record keeps `d` and `d_sha256`; the
nominee's z exists only at the look.

## 10. Two records (S-7) **[OWNER] A-7**

- **Evaluation record** `aqt.c2.evaluation.v1`, steps 1-6:
  `{schema, cycle_id, chain_log, signed{rows used}, declaration_sha256,
  eligibility{w0, T, cycle_start}, seeds, ledger{path, anchor, head_hash, entry_count,
  look_entry_hash}, trials{id: record_sha256}, families{f: {states, A_f, reason, cause,
  nominee, dsr{V: FamilyResult, task12: FamilyResult, decision, differs}, gates{G-n:
  {result, reason, values}}, outcome, cpcv (diagnostic_only)}}}`. Floats hexf.
  `evaluation_record_sha256 = SHA256(cj(record))`.
- **Sealing record**: `seal_family` per declared family and `sealing_record(declared)`,
  taking `evaluation_record_sha256`; every status (a)-(d) and sealing failure lives only
  here.

## 11. Failure (P18-7, R-14a item 7, F-18)

- Before the pick (§2 steps 2-6): evaluation invalid, `CycleError`, nothing read, nothing
  written. Where DESIGN §2 speaks of a pre-pick termination, the record says "no pick";
  rev 3 reads that as the termination record the store writes, not an evaluation record.
- After the look entry: a family whose gates or sealing fail is recorded with its cause,
  never dropped. Any other exception aborts with no evaluation record; the look entry
  stays (§4) and P18-1 crash accounting applies.

## 12. Not in 6b

No storage, no lockbox, no promotion, no lockbox data. Store obligations are written in a
`Store` docstring, as the lockbox does.

## Owner items after rev 3

| ID | Item | Recommendation |
|---|---|---|
| A-1 | Ledger anchor in the declaration; replacement/fork after it is a store obligation | as §2 |
| A-2 | `last_seen`, `embargo_days` in the declaration | as §2 |
| A-4 | Whole partition + composite manifests served by `read` | as §6 |
| A-5 | Capture record hashed in the declaration | as §2 |
| A-7 | Two-record output contract | as §10 |
| OD-4 | Row names and parse rules | as §7 |
| A-3, F-8 | decided (split by reason; record only frozen output) | — |
| A-6 | withdrawn (thresholds from the qualification object) | — |
