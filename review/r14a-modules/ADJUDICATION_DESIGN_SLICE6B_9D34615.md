# Adjudication: Fable design review of slice 6b rev 2 at 9d34615 (R14D6B2-F-1..19)

- Review record: `FABLE_DESIGN_SLICE6B_9D34615.md` (`claude-fable-5-2`, verdict FIX, committed 2ca9a33).
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the design's author, 2026-11-13. The
  adjudication approves nothing. Checked before accepting: `calibration/qobj.py:67` lists
  `final_thresholds` in the qualification object (F-1); R-14a item 1 (`origin/freeze-sheet`,
  `r14-exception/PROPOSAL.md:15`) says the module "is one file, merged under Constitution
  §16 review with an independent different-model review record" (F-8).

| ID | Decision | Direction for rev 3 | Owner? |
|---|---|---|---|
| F-1 | Accepted (blocker) | Classifier thresholds from the verified qualification object: `final_thresholds["T=<T>"]` then `reduce.for_k(pool, K_f)`. No re-pooling, no `classifier_bounds_sha256` row, no caller bytes. A-6 is withdrawn. | No |
| F-2 | Accepted (blocker) | The module appends its own `look` entry (cycle, families, ledger head before it) **before** `read`, after re-verifying that nothing was appended since step 4. A second `evaluate_look` sees that entry and refuses. `now` is that entry's time (recorded, not verified: F-14 stated). | No |
| F-3 | Accepted | The whole pre-look record goes into the entry payload (no separate store object). One global rule: per attempt at most one result entry; it must come after the start and before the outcome; an outcome without a prior result entry makes that attempt not completed (P18-1 crash path); an entry in a `CRASH_NO_ARTIFACT` attempt or after the look entry refuses the look. State that the store's runner writes start/outcome via `core.attempts`. | No |
| F-4 | Accepted | A-1 changes: the anchor is in the posted declaration (head at declaration), and the module can verify extension only. The residual (a forked or replaced ledger after the anchor) is stated plainly as a store obligation; not "no second ledger" only. | A-1 restated |
| F-5 | Accepted | Manifest check redone with the repository's frozen manifest functions over whole partitions and the composite manifest; the module then cuts the span itself, including the warm-up that reaches into exploration. A-4 restated. | A-4 restated |
| F-6 | Accepted | Record `D_j = (T−1)·var_b(S*_j)` per Annex B; compute `z_j = (S_j − S0)/sqrt(var_b)` exactly as `evaluate` does (not via `D_j`). | No |
| F-7 | Accepted | Cause precedence: if any failing trial is U_ops, the family is U_ops (P18-7), so `nominate` checks all trials before coding. Add `DAYS_INCOMPLETE` to `U_OPS_REASONS` so trials and gates agree. | No (follows A-3) |
| F-8 | Accepted; **owner question** | Record that §16 review is already required (R-14a item 1). Option (b) re-composes S0, D_j, z_j in the module; R-14a item 4 limits the module to "loads data, checks, calls and records". Owner must choose again with this known (see below). | **Yes** |
| F-9 | Accepted | `cycle_start` source added: the declaration's posting time (the anchor), as P18-2 day 0. | Part of A-1 |
| F-10 | Accepted | Evaluation record gains the Task 12 fields (A-V1): the Task 12 decision and any difference disclosed. | No |
| F-11 | Accepted | At the look every recorded identity field is compared (seed_l266, estimator_seed, trial_index, family, days, code identity), not four. | No |
| F-12 | Accepted | `drand_chain_hash` layout pinned with a known-answer test from drand's published chain info, before signing; until then marked [VERIFY]. | No |
| F-13 | Accepted | The capture record gets a stated check (hash in the declaration) or moves into the declaration. A-5 restated. | A-5 restated |
| F-14 | Accepted | Stated: `now` is recorded, not verified. | No |
| F-15 | Accepted | One source for `data_manifest_sha256` (the declaration); exact parse rules for integer and time rows. | No |
| F-16 | Accepted | `read_entries` alone (it verifies). | No |
| F-17 | Accepted | Contract changes named: `family_attempts` returns `attempt_id`; `completed_entry` returns the reason; `nominate` codes U_ops/U_proc. | No |
| F-18 | Accepted | §10 reconciled with DESIGN §2: a pre-pick termination records "no pick"; an invalid step before it writes nothing. | No |
| F-19 | Noted | Option (b) is numerically sound (6 cases bit-equal). The three tightenings go into rev 3 if (b) stays. | No |

## Owner question from F-8 (plain words)

The confirmation module is only allowed to load data, check it, **call** the frozen
statistics code and record the results. Option (b) makes the module itself put together
the per-trial numbers (S0, D_j, z_j) from small pieces of the frozen DSR code. Fable says
that may go beyond "call". Choices:

1. **Record only what the frozen code returns** (nominee z, S0, block, column lengths),
   and no per-trial S_j/D_j/z_j. The module stays a pure caller. The record is less
   detailed. *(AI recommendation: smallest and inside R-14a item 4.)*
2. **Option (a):** change the frozen `dsr.evaluate` to also return the per-trial
   columns. Needs its own §16 review and re-freezing of that file.
3. **Keep option (b)**, with a written note that the owner accepts it as "calling" under
   R-14a item 4.

Next: owner answer on F-8, then design rev 3 with all directions above.
