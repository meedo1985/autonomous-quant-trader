# Slice 6b design, rev 2: the confirmation evaluation run and the C2 evaluation record

- Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-13. Rev 1 is `1e6e672` (reviewed:
  `SOL_DESIGN_SLICE6B_1E6E672.md`, FIX, R14D6B-S-1..9; adjudicated in
  `ADJUDICATION_DESIGN_SLICE6B_1E6E672.md`, all accepted). Rev 2 also takes in Fable's
  R14S6-F-3, F-4 and F-5 (`FABLE_REVIEW_SLICE6_3765910.md`,
  `ADJUDICATION_FABLE_SLICE6_3765910.md`).
- Owner choice recorded: R14D6B-S-6 option **(b)** (recompute the per-trial columns with
  `dsr`'s own frozen functions; no change to the protected `dsr.evaluate`). The owner
  asked for rev 2 "with option (b)" (session of 2026-11-13).
- A proposal for review before the orchestration is built. It approves nothing and closes
  no owner item. Items marked **[OWNER]** are bindings for the signed C2 or the S4 text.
- Scope: DESIGN §5.2 steps 2-8 and §7.2, after slice 6a's `start`. 6b part 1 (`cc197be`,
  repaired through `b350264`: `check_confirmation_read`, `trial_path`, `trial_result`,
  `completed_entry`) stays and is extended as below.

Each section names the finding it answers. "Caller" means whoever invokes the entry point;
rev 2's rule is that the caller supplies **handles to governing records, never values the
module could read or verify from them** (R14D6B-S-1).

## 1. Two entry points, each a fresh process after `start` (6B-1, unchanged)

- `evaluate_trial(started, sources, trial_id, read)`: steps 2-4 for one trial; writes the
  trial's pre-look record (§4) and its ledger entry (§3).
- `evaluate_look(started, sources, read, bounds)`: steps 2, 3, 5-8; refuses unless
  `look_allowed` holds; writes the evaluation record, the artifacts and the sealing record.

Both start with `start` (6a, final on refusal) and repeat steps 2-3 from the governing
records, never from an earlier call's output.

## 2. What the module reads itself, and from where (R14D6B-S-1, S-4)

| Input | Rev 1 | Rev 2 source | Verified how |
|---|---|---|---|
| Signed C2 values | `protocol_row` | unchanged (§6 lists the rows) | `start` verified the bytes |
| Declared trials and their configuration hashes | caller "trial records" | the verified declaration (`Started.declaration`), as the lockbox's `_check_declared` | `start` verified the declaration chain |
| Attempt history (starts, outcomes) | caller entries | the attempt ledger file, read by the module | `verify_ledger(path).require_intact()`, then `read_entries` |
| Pre-look entries and look records | caller | the same ledger (§3) | as above |
| Ledger head | none | **anchored**: the head hash and entry count the module reads must extend an anchor it cannot forge | **[OWNER] A-1** below |
| Data-manifest hash | caller | signed C2 row `data_manifest_sha256` if bound there, else the declaration's field | equality with the served bars (§5) |
| `last_seen`, `embargo_days` | caller | declaration fields if present; otherwise store obligation | **[OWNER] A-2** |
| `now` for the look | caller | the store's look record time (ledger entry), not the caller's clock | ledger order |
| Beacon, capture CDX | caller | unchanged: `derive_seeds` verifies the beacon (BLS, 4a) and the chain hash (§7) | in-module |
| D-19 bounds document | caller bytes | unchanged: bytes whose SHA-256 equals the signed row (§8) | hash |

**A-1 [OWNER]: ledger anchor.** Options: (a) the store writes a signed or hash-committed
*cycle record* at declaration time naming the ledger path and the then-head; the module
requires the read chain to extend it, and requires that every entry after it belongs to
this cycle or is irrelevant to it (`family_attempts` already filters); (b) the head is
posted with the declaration (same posting route as the declaration). **Recommendation (a)**,
because the declaration is posted before any attempt exists and the anchor must cover
appends made later. Either way the module can only check extension; it cannot prove that
no second ledger exists. That residual is a store obligation, written in a `Store`
docstring as the lockbox does.

**Order (S-4)** inside `evaluate_look`, every step before any `read`:
1. `start` (6a);
2. declaration (`check_declaration`), screen record (`check_screen_record`), eligibility
   (`check_eligibility` with the signed `confirmation_start`, `confirmation_end`);
3. seeds (`derive_seeds`; a failure here is read-free, R14D6B-S-8);
4. ledger: `verify_ledger`, anchor check, then `family_attempts`, `trial_states`, the
   pre-look entries (§3), the termination and look records;
5. `look_allowed`;
6. bounds document hash and its cell (§8);
7. only now `read`, then the C-T and manifest checks (§5).

`evaluate_trial` runs 1-4 (without the look records) and then reads.

## 3. The pre-look record and its ledger entry (R14D6B-S-2, R14S6-F-3, F-4)

**Record** `aqt.c2.trial_result.v2` (v1 fields plus the identity fields F-4 asks for):

```
{schema, cycle_id, trial_id, family, configuration_hash, attempt_id,
 trial_index, seed_l266, estimator_seed,          # F-4 (1)
 data_manifest_sha256,                            # F-4 (2), §5
 protocol_hash, engine_commit,
 confirmation_module_sha256, image_digest,        # F-4 (2), from Started
 window_id, days, d, d_sha256, reason}
```

- `seed_l266`, `estimator_seed`, `trial_index` are the values `derive_seeds` and line 266
  produced in this process (never caller integers). `estimator_seed` is what
  `baseline_d` used.
- `record_sha256 = SHA256(cj(record))` is **the** identity of the record (F-3 suggestion).
  `d_sha256` stays as the hash of `d` alone, for A7 step 2.

**Ledger entry.** `evaluate_trial` appends one entry with `record_type =
"aqt.c2.trial_result_entry.v1"` and payload
`{attempt_id, cycle_id, trial_id, configuration_hash, window_id, estimator_seed,
data_manifest_sha256, record_sha256}`, using `aqt.core.ledger.append_entry` (frozen; it
verifies the whole chain under the lock before appending). It must lie between the
attempt's start entry and its outcome entry. The frozen `finish_attempt` has no result
field, so the entry is its own record type.

**At the look**, for every completed attempt (`trial_states` says completed):
- exactly one such entry exists in `(start, end)` of that attempt, else `CycleError`;
- its payload equals the record's own fields, its `record_sha256` equals
  `SHA256(cj(record))` of the record the store hands over, and `completed_entry` passes;
- its `configuration_hash` equals the declaration's for that trial, its `estimator_seed`
  equals what `derive_seeds` gives for that trial now, its `data_manifest_sha256` equals
  the cycle's, its `window_id` equals the eligibility window's;
- every other trial's `d` therefore enters `dsr.evaluate` bound to its trial, seed, data
  and window (closes the F-4 failure scenario).

Test obligations: a record moved under another trial id is refused (F-3 reproduction);
a wrong estimator seed, another manifest, a second entry, or an entry outside the
attempt's span is refused; the part 1 test name stays honest (renamed in `7fd85f9`).

## 4. Unavailable runs and their cause (R14S6-F-5) **[OWNER] A-3**

Today `completed_entry` turns an unavailable run into empty values, and `nominate`
reports `"<id>: MISALIGNED_SERIES"`, cause U_ops; the real reason stays only in the
pre-look record. Proposal:
- `nominate` carries the record's `reason` into its message: `"<id>: <reason>"`.
- Cause by reason:
  - **U_ops** (infrastructure, data or governance): `MISSING_DAY`, `DUPLICATED_DAY`,
    `IRREGULAR_DAY`, `MISALIGNED_SERIES`, `SIGMA_UNBOUND`, `DAYS_INCOMPLETE`;
  - **U_proc** (the registered trial's own deterministic failure on valid data):
    `TRIAL_CODE_ERROR`, `OVERLAY_VIOLATION`, `EventContractError`, `CostModelError`,
    `FeatureFactoryError`, and any other `RunUnavailable` reason not listed above.
- Either way the family has no promotable trial (A_f fails); only the recorded cause
  differs. This is the P18-7 precedence wording the owner must accept, or choose to keep
  everything U_ops (today's behaviour, simpler, but it calls a trial's own bug
  "infrastructure").

**Recommendation:** the split above, because P18-7's own comment defines U_ops as
infrastructure or governance.

## 5. Reading and the data manifest (R14D6B-S-3)

`read` returns `(btc, eth, manifest)`: the two `BarSeries` and the manifest it served
under. Before any use the module:
1. runs `check_confirmation_read` (C-T contract, part 1);
2. recomputes the served bars' hash with the repository's bar-series encoding
   (`aqt.data` `encode_bar_series` / `canonical_hash`, the same bytes the exploration
   manifest uses) and requires the manifest to list exactly that hash;
3. requires `SHA256(manifest)` to equal the cycle's `data_manifest_sha256` (§2).

Consumer-boundary test: valid-shaped bars from another manifest are refused, and so is
the right manifest with other bars. Who may call `read`, under which identity, stays a
store and image obligation **[OWNER] A-4: manifest format and access path**.

## 6. Signed C2 rows (6B-2, R14D6B-S-8, S-9) **[OWNER, OD-4]**

Read only through `protocol_row`, each once, no defaults:

| Row | Feeds |
|---|---|
| `drand_public_key`, `drand_genesis_time`, `drand_period`, `drand_scheme`, **`drand_chain_hash`** | `Chain`; the parameters must hash to `drand_chain_hash` (drand chain-info hash), S-8 |
| `confirmation_start`, `confirmation_end` | `check_eligibility` (S-9: the S4 binding states them **only** as these unique rows, or requires them equal to the nested `partitions.confirmation` values when signing; the module has no YAML parser) |
| `t_min`, `g_days` | `check_eligibility`, `nominee_gates` |
| `z_crit` (decimal string) | `family_gates` G-9 |
| `family_block_rule` | `nominate` |
| `canonical_benchmark_sha256` | G-13 |
| `classifier_bounds_sha256` | §8 |
| `data_manifest_sha256` (if bound in C2; else declaration) | §2, §5 |

The capture time for `derive_seeds` comes from its frozen capture record (the
seed-disclosure capture source), never from the caller **[OWNER] A-5: capture-record
source**.

## 7. Per-trial S, T, D, z at the look: option (b) (R14D6B-S-6)

`dsr.evaluate` returns the nominee's z, S0, block and the column lengths, not every
column's S_j, D_j, z_j. Option (b): after `evaluate` returns available, the module
recomputes with `dsr`'s own frozen functions and the same inputs:
- `draws = [dsr.indices(family_seed, T, b, result.block) for b in range(BOOTSTRAP_ATTEMPTS)]`;
- `s_star, s_null = dsr._replicates_v(x, draws)` (the numerics `evaluate` used);
- `S_j = dsr._sharpe_exact(column j)`, `D_j = dsr._mean_var(s_star column j)[1]`,
  `S0 = fsum(max(row) for row in s_null) / BOOTSTRAP_ATTEMPTS`, `z_j = (S_j - S0) / sqrt(D_j)`.

Checks, each a `CycleError` on mismatch (never a silent difference):
`S0 == result.s0` and `z[result.nominee] == result.z`, both bit for bit
(`float.hex` equality). A test proves it on the existing DSR fixtures.

Why (b): it leaves the protected `dsr.evaluate` untouched (no §16 review for that file),
and the bit-for-bit check makes any drift loud. Cost: the bootstrap runs twice at the look
(`BOOTSTRAP_ATTEMPTS` replicates over K columns); acceptable once per cycle.

DESIGN §5.2 step 4 is corrected: the pre-look record keeps `d` and `d_sha256`; S, T, D,
z exist only at the look (D_j needs the family's draws).

## 8. The supported-law classifier (R14D6B-S-5) **[OWNER] A-6: which document**

The caller supplies the D-19 bounds document as bytes; its SHA-256 must equal the signed
`classifier_bounds_sha256`. Then, before any read:
- `pool = reduce.pooled(cells)[T]` for the window's T (a missing T refuses);
- `upper, lower = reduce.for_k(pool, K_f)` (its `ValueError` refuses);
- the document's own `z_crit` and T levels must equal the signed `z_crit` and include T;
- `classifier = lambda x, lengths: classifier.within(diagnostics(x), upper, lower)`.

`nominate` never runs without it (D-18 O18-2).

## 9. Two records with a stated boundary (R14D6B-S-7) **[OWNER] A-7: S4 output contract**

- **Evaluation record** `aqt.c2.evaluation.v1`: steps 1-6 only:
  `{schema, cycle_id, chain_log, signed{rows used}, inputs{name: sha256},
  eligibility{w0, T}, seeds, ledger{path, head_hash, entry_count, anchor},
  trials{id: record_sha256}, families{f: {states, A_f, reason, cause, nominee,
  dsr{block, S0, columns[{trial_id, S_j, D_j, z_j}], T}, gates{G-n: {result, reason,
  values}}, outcome, cpcv (diagnostic_only)}}}`.
  Floats are hexf, recursively. `evaluation_record_sha256 = SHA256(cj(record))`.
- **Sealing record**: `seal_family` per declared family and `sealing_record(declared)`,
  taking `evaluation_record_sha256`. Every status (a)-(d) and every sealing failure lives
  only here. DESIGN §5.2 and §7.2 wording is reconciled to say so.

Nothing reads the C-14 CPCV report (test, LG5B-6).

## 10. Failure (P18-7, R-14a item 7, 6B-8 unchanged in substance)

A failure in §2 steps 2-6 is evaluation-invalid: `CycleError`, nothing read, no record.
After the read, a family whose gates or sealing fail is recorded with its cause, never
dropped. Any other exception aborts with no record; P18-1 crash accounting covers it.

## 11. What 6b will not do (unchanged)

No storage, no lockbox, no promotion, no lockbox data. It authenticates the store's
records only by the checks above; the rest are written as store obligations.

## Owner items from rev 2

| ID | Question | Recommendation |
|---|---|---|
| A-1 | Ledger anchor source | (a) a hash-committed cycle record at declaration time |
| A-2 | `last_seen`, `embargo_days`: declaration field or store obligation | declaration field |
| A-3 | Cause of a recorded-unavailable trial (R14S6-F-5) | split U_ops / U_proc as §4 |
| A-4 | Manifest format and access path of `read` | the exploration-manifest format; access in the store build |
| A-5 | Capture-record source for `derive_seeds` | the seed-disclosure capture record |
| A-6 | Which D-19 bounds document | the one certified with `z_crit` (A-B7) |
| A-7 | S4 two-record output contract | as §9 |
| OD-4 | Signed row names | as §6 |

Next: an independent design review of rev 2, then the orchestration code
(`evaluate_trial`, `evaluate_look`) in thin slices with tests.
