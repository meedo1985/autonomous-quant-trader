# Slice 6b design: the confirmation evaluation run and the C2 evaluation record

- Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-09. A proposal, for Sol's design
  review before the orchestration is built; it approves nothing and closes no owner item.
- Scope: DESIGN §5.2 steps 2-8 and §7.2 (contract), after slice 6a's `start`. Every
  building block exists already (slices 1-5): `check_declaration`, `check_eligibility`,
  `check_screen_record`, `family_attempts`, `trial_states`, `look_allowed`, `derive_seeds`,
  `baseline_d`, `nominate`, `family_gates`, `nominee_gates`, `nominee_outcome`, `cpcv_report`,
  `seal_family`, `sealing_record`. 6b only binds their inputs to verified sources and writes
  the record.
- Items marked **[OWNER]** need the owner. They are bindings for the signed C2 or the S4
  text, so this design can propose them but not settle them.

## 1. Two entry points, each a fresh process after `start`

The evaluation is not one call. Each trial is evaluated when its attempt runs (P18-1), and
the look comes later (P18-2). Proposal **6B-1**:

- `evaluate_trial(started, inputs, trial_id, read)`: steps 2-4 for one trial. The output is
  the trial's pre-look record (§4). The attempt record itself is `aqt.core.attempts`', not
  this module's.
- `evaluate_look(started, inputs, read, now)`: steps 2, 3 and 5-8. It refuses unless
  `look_allowed` holds. The output is the C2 evaluation record, the prediction artifacts
  and the sealing record.

Both run in a fresh process whose first act is `start` (6a, which is final on refusal).
Both repeat steps 2-3 from the governing records, never from a previous call's output.

## 2. Signed C2 values (step 2 and others) **[OWNER, OD-4]**

They are read only from `Started.protocol` by `protocol_row`, each exactly once, with no
caller defaults. Proposed row names **6B-2**:

| Row | Feeds |
|---|---|
| `drand_public_key`, `drand_genesis_time`, `drand_period`, `drand_scheme` | `Chain` (FP3) |
| `confirmation_start`, `confirmation_end` | `check_eligibility` `c2_start`, `c2_end` (the signed `partitions.confirmation` values, restated as unique rows because `protocol_row` cannot address nested YAML keys) |
| `t_min`, `g_days` | `check_eligibility`, `nominee_gates` |
| `z_crit` (decimal string) | `family_gates` G-9 |
| `family_block_rule` (`largest` or `median`) | `nominate` |
| `canonical_benchmark_sha256` | `family_gates` G-13 |
| `classifier_bounds_sha256` | §6 |

The existing rows (`engine_commit`, `screen_object_sha256`, module hashes, `outpoint_F`,
`image_digest`, `qualification_object_sha256`) are unchanged.

## 3. Reading confirmation data (steps 4, 6) **[OWNER, DESIGN §10]**

Proposal **6B-3**: the caller passes `read`, the confirmation partition's read gate, which
returns `(btc, eth)` `BarSeries` over `[w0 − max warm-up, w1)`. `read` is called only
after `start`, step 2 and step 3 have passed: no seed failure ever reads.

Before any use, the module validates the §7.2 C-T contract:
- symbols BTCUSDT and ETHUSDT;
- contiguous hourly bars, ascending, each exactly once, both series on identical times;
- exactly `[w0 − W, w1)`, with W the declared trials' largest warm-up;
- finite, positive OHLC within the bar rules.

Then each trial's rows are the last `warmup + window` hours, plus `confirmation_path`'s
terminal row. Anything else refuses the evaluation, with no repair or fill. Who may call
`read`, and under which identity, is the store's and the image's concern (DESIGN §10).

## 4. The per-trial pre-look record (step 4)

Proposal **6B-4**: `{schema: "aqt.c2.trial_result.v1", cycle_id, trial_id, family,
configuration_hash, attempt_id, window_id, days: [ISO dates], d: [hexf], d_sha256}`.

- `d` is `baseline_d` (the BTC 1x pair at the trial's `estimator_seed`).
- `d_sha256` is `_floats_sha256(d)`, big-endian float64, which closes LG5-3.
- A run that raises `RunUnavailable` or `EventContractError` gives `d: null` with
  `reason`. `nominate` then fails A_f (U_ops), as for an incomplete trial.
- `nominate`'s `completed[id] = (configuration_hash, days, d)` is read from these records
  and checked again against the declaration hashes. At the look, `seal_family` recomputes
  `d` and checks it against this `d_sha256` (A7 step 2).

## 5. The C2 evaluation record and `evaluation_record_sha256` (steps 7-8)

Proposal **6B-5**: `aqt.c2.evaluation.v1` = `{schema, cycle_id, chain_log, signed{...},
eligibility{w0, T}, seeds (derive_seeds' record), trials{id: pre-look record}, families{f:
{states, A_f, reason, nominee, dsr{S, T, D, z, S0}, gates{G-n: {result, reason, values}},
outcome, cpcv}}}`.

- Floats are hexf (§D-3.1a), recursively. A `Gate` is `{result, reason, values}`.
- `evaluation_record_sha256 = SHA256(cj(record))` over this record. It is written **before**
  sealing, and `seal_family` and `sealing_record` take that hash (LG5-2: the record of steps
  1-6, so the hash is not circular).
- The output is three objects: the evaluation record, the artifacts, and the sealing record
  (DESIGN §5). The C-14 report sits under each nominee's family, labelled
  `diagnostic_only`. Nothing reads it (test, LG5B-6).

## 6. The supported-law classifier (step 5) **[OWNER]**

DRAFT §2.5: "The support classifier ... belongs to the D-19 preregistration that certifies
`z_crit`". The frozen code is `calibration.classifier.within(diagnostics(x), upper,
lower)`, with thresholds fit per cell `(K, T)` (`reduce.Bounds`).

Proposal **6B-6**: the caller supplies the D-19 bounds document as bytes. Its SHA-256 must
equal the signed `classifier_bounds_sha256`. Then:
- the cell is `(K_f, T)`, the family's trial count and the window's days;
- `classifier = lambda x, lengths: within(diagnostics(x), upper, lower)`;
- a missing cell refuses the evaluation, since `nominate` never runs without a classifier
  (D-18 O18-2).

The bounds document's layout is the D-19 result's, to be bound with `z_crit` (A-B7).

## 7. Other inputs and what the module trusts

Inputs taken from governing records, as before:
- the declaration (verified by the chain), and the screen record with its hash
  (`check_screen_record`);
- the attempt ledger entries (`family_attempts`);
- the immutable trial records (P18-0);
- the beacon and the capture CDX (`derive_seeds`);
- `last_seen` and `embargo_days` (`check_eligibility`), which are recorded governance
  facts the module cannot prove (its docstring already says so);
- `now` and the termination and look records (`look_allowed`);
- the data manifest hash.

Proposal **6B-7**: every such input is a parameter of the entry point, gathered in one
frozen `Inputs` value. The record logs the SHA-256 of each input object (Constitution §27),
so a reviewer can trace each one to its source. How the store vouches for them is the store
build's obligation, as for the lockbox (`Store` docstring there).

## 8. Order and failure (P18-7, R-14a item 7)

Proposal **6B-8**: inside `evaluate_look`:
1. `start` (already done);
2. declaration, screen record, eligibility, then seeds (any failure: evaluation invalid, a
   `CycleError`, nothing read, no record);
3. `look_allowed`;
4. `read` and the C-T check;
5. states, then `nominate` per family (`A_f`);
6. for each nominee: `family_gates` plus `nominee_gates`, all computed (P18-7), then
   `nominee_outcome`, then `cpcv_report`;
7. the record, then its hash, then `seal_family` per declared family, then
   `sealing_record(declared)`.

A family whose gates or sealing fail is recorded with its cause, never dropped. An
exception outside the defined unavailability paths aborts the call with no record. P18-1's
crash accounting covers it.

## 9. What 6b will not do

It does not store records, run the lockbox, decide promotion, or read any lockbox data. It
does not authenticate the store's records beyond their hashes (DESIGN §10, owner items).
