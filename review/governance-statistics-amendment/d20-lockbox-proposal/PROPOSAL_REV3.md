# D-20 lockbox bindings: proposal, revision 3 (replaces revision 2 for the owner)

**Author:** the `senior-statistical-governance` agent. Observed model: Claude Opus 5.5, model ID `claude-opus-5-5` (taken from this session's own metadata, not from an instruction). I am an AI reviewer, not an authority. I propose and check bindings. I cannot decide, accept, activate or amend anything.

**Status: INACTIVE PROPOSAL.** Nothing frozen changed. No row binds until the owner decides and signs the C2 §4 amendment. `PROPOSAL.md` (revision 1) and `PROPOSAL_REV2.md` (revision 2) stay as history only.

**VERDICT: `AMENDMENT_REQUIRED`.**

**Answers** (both read in full):
- `SOL_REREVIEW_3DCA780.md` (gpt-6-sol, FIX, D20LR2-S-1..6);
- `ASTRA_REREVIEW_3DCA780.md` (gpt-6-astra, FIX, D20LR2-A-1..6).

**Review status:** revision 3 is unreviewed. R19-2 requires a focused re-check by two model families before any owner decision. No human statistician has reviewed it.

**Checkout and mode:**
- Checkout: `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch `freeze-sheet`.
- Files: I wrote this one file only. **I ran no git command.** The caller also asked for `REREVIEW2_PROMPT.md`; my authority covers creating one new report file, so I returned that prompt's full text to the caller instead of writing it.
- Access: no confirmation or lockbox data, network, credentials, keys or simulation. The calculations are deterministic Python on made-up numbers, run from a scratch directory outside the repository.

**Row labels** (unchanged from revision 2):
- **[DECIDED]**: the owner already decided it; the source is cited.
- **[DETAIL]**: a proposed implementation convention. It still needs adoption (Astra A-5 note, report l.25). It is not a value that only one correct implementation could use.
- **[NEW DEFAULT]**: a recommended new choice. The owner adopts it through Q1 unless it has its own question.

## 0. Verification

**Read this session:**
- `PROPOSAL.md`, `PROPOSAL_REV2.md` and both re-check records;
- `OWNER_DECISION_D12.md` and `d12-proposal/PROPOSAL_REV7.md` §3-§5 (l.62-147);
- `d11-proposal/PROPOSAL_REV3.md` l.50-60;
- Constitution l.70-90, l.120-126, l.145-153 and l.189-200;
- `protocols/protocol_v1.yaml` l.64-91, l.262-268 and l.290-302;
- DRAFT_WORDING R-6..R-14 (l.145-153) and l.254; Annex C l.42-60, l.139-160 and l.403-414.

**Code read this session:**
- `src/aqt/backtest/event_contract.py` l.93-221;
- `src/aqt/data/bars.py` l.181-200 and l.273-282;
- `src/aqt/core/ledger.py` l.282-308 and l.369-415;
- `src/aqt/core/preregistration.py` l.257-286;
- `calibration/screen.py` l.302-306, l.716-721, l.1009-1029, l.1465-1477, l.1499-1556 and l.1408-1425;
- `calibration/seeds.py` l.11-19;
- `src/aqt/metrics/statistics.py` l.159-166, l.345-359, l.435 and l.554-566.

**Code facts that the repairs depend on:**
1. `EventResult.start` is an `int`, an index into the bars (`event_contract.py` l.98). The result holds no reference to its series.
2. `run_event_contract` calls `series.require_contiguous()` (l.136). It refuses unless `start ≥ 3` and `start + n < len(bars)` (l.139), because the last hour's return reads `bars[j + 1].open` (l.206). So the run needs one bar after its window.
3. `append_entry` takes its timestamp *before* it takes the lock (`ledger.py` l.388, lock at l.391). It checks chain integrity only; it checks neither evaluation uniqueness nor budget (l.391-414). `verify_ledger` returns only chain metadata (l.282-298). `read_entries` (l.301-308) returns the verified entries.
4. `TRIAL_FIELDS` has no seed field (`screen.py` l.302-306), and `walk_forward` passes seed 0 to the nominee's fit (l.1547). R-14 (DRAFT l.152) requires every C2 evaluation module to be either the engine commit's copy of the file or the qualification object's copy.
5. `BlockLength.clipping` is `"LOWER"`, `"UPPER"` or `None` (`statistics.py` l.435).

**Governing text found by searching on each topic** (checklist item 1):
- Constitution l.73 ("Only lockbox_eval reads it") and l.79 ("Research receives PASS/FAIL only"). Both bear on D20L-23 and D20L-34.
- D-11 REV3 l.57 lets `lockbox_eval` read bars over `[S_pre, L1)` only. This bears on D20L-34.
- Annex C l.412 says "the model seed its declaration fixes", but no declaration field holds a seed. This bears on D20L-31.
- D-12 P-6 l.99 and the owner's Q6(ii) answer (`OWNER_DECISION_D12.md` l.18) bear on D20L-36.

**Calculations** (exact integers or exact float bit patterns; Python 3 run from the main checkout's venv with `-I -B`). The bare `python` command is not installed on this host.
- **Lockbox run indices.** Bars `[2022-11-13, 2026-09-01)` give `start` = 22,344 and `n` = 10,968, so `len(bars)` = 33,312. Then `start + n ≥ len(bars)` holds, and the bound runner refuses the run (D20L-34).
- **Cap boundary.** In integer seconds, with no outage: `R_j = C − 259,201` gives `E = C − 1`, and a decision is possible. `R_j = C − 259,200` gives `E = C`, and no decision is possible.
- **Cause precedence.** Take conditions (L1 false, L2 false, L3 true, L4 null). Revision 2's rule makes this TECHNICAL; revision 3's rule makes it PERFORMANCE. The two rules give different labels (D20L-26).
- **Seed mapping.** For seed `"a"*64`: `% 2**31` gives 715,827,882. The first 8 hex digits and `% 2**32` both give 2,863,311,530, which is above `2**31 − 1`. The mapping is therefore a choice (D20L-30).
- **Replay.** Two bundles with the same science and different `operational` fields have different whole-bundle bytes and identical projections (D20L-28). Astra reproduced the first half (report l.79).
- **Hex ordering.** Lexicographic order of hexf strings is wrong for negative numbers (−1 against −2). `unhexf(hexf(q)) == q` holds.
- **Ties.** `k` with a tie: in `[0.1, 0.2, 0.2, 0.3]` with `T_L` = 0.2, `k` = 1.

**Carried from revision 2 and not re-read this session:**
- the R-14 facts of revision 2 §0 (engine commit `eeaa728`, `qobj.py` l.56-63);
- D-11 REV3 l.89-98 (sealing timing) and l.103 (day 0);
- DRAFT l.162 (archive timestamp T);
- the A4 generator.

## 1a. Disposition of the re-check findings

**Overlaps:**
- A-1 ~ S-2 (schemas and nulls);
- A-2 ~ S-1 (the step-2 transaction);
- A-6 = S-3 + S-5 (the cap).

**One disagreement between the reviewers.** Astra judged the seed mapping resolved (report l.22, l.70). Sol called it a new default (S-4). I side with Sol, for the reason under S-4 below. Astra's technical points (the mapping is deterministic, its range is `0..2**31−1`, and it matches B4's range without using B4's RNG) are correct and are kept.

| ID | Disposition | Evidence and repair | Where |
|---|---|---|---|
| **S-1** (step 2 not durable) | **Accepted.** | Revision 2 claimed that one fsynced ledger line makes step 2 atomic. That covered the line's own fields only; the nonce and the default bundle were written separately. Repair: the store runs step 2 as one serialized transaction. It writes and fsyncs the sealed default before appending the ledger entry, and it samples `t_s` inside the lock. A read is allowed only if both records exist. Reconciliation is also bound. | B4.1; D20L-22 |
| **S-2** (read_start null, upside fields) | **Accepted.** | Typed schemas and canonical examples are given. The default has `read_start` null. Both forms of `upside` are given in full. `q` is hexf. | B4.2; D20L-25 |
| **S-3** (blanket `t < C` bars post-cap publication) | **Accepted.** | D-12 P-7 l.94 ("A result first released after the cap shows PASS or FAIL and nothing more") makes publication after the cap a duty. Each action now has its own comparison: inserts have no cap, signing needs `R_j < C`, and decisions need `E ≤ t_dec < C`. | B3a; D20L-27 |
| **S-4** (mapping is a choice; the seed-0 test is unsound) | **Accepted, with a further correction.** | Right answer, wrong reason, in revision 2. Its "same range as `getrandbits(31)`" shows the mapping is *compatible*, not *required*: other mappings give other values (§0). Its "bit-identical with seed 0" test claimed determinism, but determinism only means the same seed reproduces a fit. It does not mean different seeds give the same fit. Repair: the mapping becomes [NEW DEFAULT] in its own question, Q5. The seed-0 comparison is replaced by a same-seed reproduction test, plus a rule that nothing fitted with seed 0 is C2 evidence. A further correction (D20L-31): under R-14, the confirmation fit can take the new seed only through `screen.py`, before the freeze. | A1b; Q5; D20L-30, D20L-31 |
| **S-5** (`>` should be `≥`) | **Accepted.** | The integer check in §0 confirms it. Promotion is impossible iff `E ≥ C`; with no outage, that is iff `R_j ≥ C − 72 h`. Reader-path outages, which push `E` later, are included. | B3a; D20L-21 corrected |
| **S-6** (`start` is an index) | **Accepted, modified.** | The UTC instant is now resolved through the series. Sol also asked to bind "the complete hourly timestamp sequence". That is not stored separately, because it already follows from what is checked: a `BarSeries` is strictly increasing and interval-aligned (`bars.py` l.181-186), `run_event_contract` requires it to be contiguous (l.136), and the start instant is checked. Together these fix `open_time(start + i) = start instant + i h`. A test asserts this. | A6; D20L-33 |
| **A-1** (no legal PASS cause; default precedence; read_start) | **Accepted, modified.** | A PASS has `cause_class` null. Precedence is explicit: a DEFAULT bundle is always DEADLINE. Conditions use three-valued AND. One choice in this changes revision 2: a definite false outranks a null. This is labelled [NEW DEFAULT] because it changes the cycle label that D-12 Q2a discloses (D20L-26). The encodings of `q` and the block fields are stated. While repairing this I also found that revision 2's `times.finished` was circular (D20L-24). | B4.2; A7; D20L-24..26 |
| **A-2** (two publishers, no uniqueness; `verify_ledger` is not a lookup) | **Accepted.** | Code fact 3 confirms both points. Repair: in the same transaction the store checks that the evaluation is absent and that budget remains, under its lock, by scanning `read_entries`. Repeating the call returns the existing entry, so a retry is always safe (D20L-12 retired). A duplicate and interleaving test is added. | B4.1; D20L-22 |
| **A-3** (replay against the whole bundle) | **Accepted, modified.** | The store checks the sealed bundle against the **release entry's** commitment (Sol's first-round S-9 note, re-check l.23). It then compares a defined projection. The projection drops the whole `operational` section. That section holds the times and also `startup_check_id`, which a replay would change too; Astra's repair did not name it. | B4.4; D20L-28 |
| **A-4** (publisher authentication; signer guard state; compromise) | **Accepted, modified.** | The ACL is now role-based: OS service identities on a local channel, and one table of allowed operations. The signer gets its guard state only from the store. After a compromise, a certificate is retained only if it reconciles against trusted records; because signing is deterministic, reconciliation can check content even though it cannot prove who signed. Key replacement is dropped outright, not left open "unless C2 preauthorizes" one (Astra's own suggestion, report l.87). | B1; D20L-29 |
| **A-5** (old-seed branch rejected by A7) | **Accepted.** | A closed `seed_source` enum, a check that branches on the signed choice, and one test vector per branch. | A7; D20L-32 |
| **A-6** (equality case; post-cap visibility) | **Accepted** (same as S-3 + S-5). | As above. | B3a; D20L-27 |

**Astra's notes on first-round findings, all accepted:**
- **A-7.** "Every route" in D20L-19 means the two offered layouts. It is not a claim that R-14 forbids service code in every existing file.
- **A-9.** The point that V is unnecessary covers the statistical calculation only. The lockbox refit still runs on the qualified image.
- **A-6.** `EventResult.start` resolution is handled in A6.

**Simplifications adopted, as suggested** (Sol l.40; Astra l.87). I found no evidence against them.
1. **The reference-vector check moves to startup** (A5). The lockbox module checks the A5 vectors once per process start, on the qualified image, and the store logs the result. Each evaluation references that record. D-12's P-4 replicate check stays in the pre-read check; it is a different check.
2. **The provenance job folds into sealing** (A7). The independent recomputation and the pre-look `d_sha256` check are kept.
3. **Mid-cycle key replacement is dropped.** Revision 2's Q5 had only one real option left, so it moves into Q1.
4. **The retry rule disappears.** Step 2 can be repeated safely, so no separate rule is needed.

## 1. Bindings

These rows are unchanged from revision 2 unless stated. Rows not repeated here stand as written in `PROPOSAL_REV2.md`. They are:
- the shared encodings (l.98-103);
- A1a;
- A2;
- A3;
- A4;
- A5 except the "checked every run" bullet;
- B2;
- B3;
- B5;
- B6.

### 1.1 D-11 items

**A1b. The nominee's model seed (S-4; Q5).**
- **[DECIDED]** `seed_l266 = trial_seed(protocol_hash, hypothesis_hash, trial_index)`, per R-13 (DRAFT l.151).
- **[NEW DEFAULT, Q5]** `estimator_seed = int(seed_l266, 16) % 2**31`, passed as B4 passes `model_seed` (Annex C l.405-411). Both seeds are stored in the nominee identity (A7).
- **One seed throughout C2.** The confirmation fit, the A7 sealing re-run and the lockbox refit all use `estimator_seed`. No result fitted with seed 0 counts as C2 evidence. The D-19 screen used seed 0 (MR-2, l.1473-1477), but only to choose the nominee; it is not reused.
- **Tests:**
  - Two fits with the same `estimator_seed` give bit-identical predictions, for each allowed class.
  - The stored seeds re-derive from the trial record.
  - A test with seed 0 against another seed is **not** required. If one is run, it is evidence about MR-2 only and has no effect on C2 validity.
- **Where the code must change (D20L-31).** R-14 places the confirmation fit in `screen.py`'s `walk_forward`, which hard-codes 0 (l.1547). So the seed parameter must be merged into `screen.py` before the qualification-object freeze (`FREEZE_HELDOUT.md` step G). The lockbox refit can live in the lockbox module (Q4).
- **Wording.** Annex C l.412's "the model seed its declaration fixes" names a field no declaration has. The C2 wording should read "the l.266 seed, mapped per A1b".

**A5, changed bullet [NEW DEFAULT].** At each start of the lockbox process on the qualified image, the module computes the A5 reference vectors and compares them bit for bit. The store appends `aqt.lockbox.startup.v1` = `{startup_check_id, lockbox_module_sha256, image_digest, vectors_sha256, result}` to its own append-only log. A process without a `PASS` record for its own module hash and image is refused at the pre-read check, with reason `REFERENCE_VECTOR_MISMATCH`.

**A6. Runner-to-metric interface (S-6; D20L-33, D20L-34).** Revision 2's A6 stands, with these additions:
- **Conversion [DETAIL].** The adapter takes `(series, result)` pairs, never a bare `EventResult`. For each leg it checks:
  - `series.symbol` is the leg's asset, and both legs of a pair used the same series and the same `start`;
  - `series.bars[result.start].open_time` is L0 for the lockbox, or w0 for the confirmation source;
  - `len(result.equity) == 24 · m_days`.

  Contiguity is already enforced by the runner (l.136), so this fixes every hourly instant.
- **Error mapping [DETAIL].** An `EventContractError` raised for equity (l.211-212, l.176-177) becomes `RUN:NONFINITE_EQUITY`. Any other runner error becomes `RUN:RUN_FAILED`. A failed BTC run makes L-1..L-3 null; a failed ETH run makes L-4 null.
- **The final hour [NEW DEFAULT, Q2(ii); S4].** The last hour of a window needs the price at the window's end instant.
  - *Lockbox run:* the runner reads it as the open of the bar at L1, which is outside the bars D-11 authorises (`[S_pre, L1)`, REV3 l.57). So the bound runner refuses every full-length lockbox run (§0).
  - *Confirmation source:* the same rule reads the open of the bar at L0. That is a lockbox byte, and Constitution l.73 forbids reading it outside `lockbox_eval`.
  - *Recommended:* the price at a window's end instant is the **close of the window's last bar**. This uses C-6 (1)'s identity close(t) = open(t+1) (Annex C l.144) as a definition, and it applies to both runs. The adapter supplies it by appending one derived terminal bar whose open equals that close. A test must show that the derived bar changes nothing except the last hour's return.
  - *This governs every C2 confirmation run*, not only D-20's. The S4 draft should therefore state it in C-0/C-6. D-20's A6 and A7 must use the same rule as the C2 evaluation record, because A7's check compares hashes of `d` (D20L-34).
- **Test.** For each leg, the hourly instants are `start instant + i h` for i = 0..24·m − 1.

**A7. Prediction artifact (A-5; simplification 2).**
- **Schema changes [DETAIL],** `aqt.lockbox.prediction.v1`:
  - `stream.seed_source` ∈ {`R13_TRIAL_SEED`, `L266_TRIAL_SEED`}, equal to the value in the signed C2 (Q3);
  - `block` = `{psi_sha256, value: hexf, raw: hexf | null, clipping: "LOWER" | "UPPER" | null}`;
  - `q`: hexf;
  - `replicates_sorted`: 2,000 hexf strings, sorted by decoded value.
- **Sealing [NEW DEFAULT; replaces the separate job].** In the sealing run, the authorised experiment engine:
  1. re-runs the nominee's BTC baseline pair from the confirmation bars, with the registered code, `estimator_seed` and the A6 final-hour rule;
  2. requires the SHA-256 of the A5 float bytes of `d` to equal the pre-look `d_sha256` in the C2 evaluation record (D20L-20);
  3. computes ψ, b, the replicates and q;
  4. stores the artifact and writes `artifact_sha256` into `aqt.lockbox.sealing.v1`.

  If any step fails, the status is (d), "prediction artifact UNAVAILABLE". The check against an independent value is the pre-look hash, which was recorded before the look.
- **Pre-read checks [DETAIL].** As in revision 2, except that the `seed_hex` check branches on `seed_source`:
  - `R13_TRIAL_SEED`: `seed_hex == SHA256(cj({"family_seed": family_seed_f, "trial_id": trial_id}))`;
  - `L266_TRIAL_SEED`: `seed_hex == seed_l266`.

  A `seed_source` that differs from the signed value gives `IDENTITY_MISMATCH`. There is one test vector per branch.

### 1.2 D-12 groups (P-1..P-8 [DECIDED], `OWNER_DECISION_D12.md` l.22-26)

**B1. Signing, custody, identities (A-4).** Revision 2's B1 stands (Ed25519 through `cryptography`; key generated before C2; raw public key in the signed C2), with these changes:
- **Identities and ACL [NEW DEFAULT].**
  - The store is one service. It alone holds the sealed store, the index ledger and the clock.
  - Callers reach it only over a local channel that tells it the caller's OS service account, for example peer credentials on a Unix socket. The exact mechanism goes to §16 review.
  - Four accounts are mapped to roles: `publisher`, `lockbox_eval` (worker and signer), `replay` and `reader`. Any other caller is refused and logged.

| Role | Allowed store operations | Never |
|---|---|---|
| publisher | `begin_read` (B4.1); `insert_release`; `state(evaluation_id)` → pre-read entry, finished `{result, commitment}`, release presence, store time | sealed bundles, nonces, cause classes, lockbox bars |
| lockbox_eval | lockbox bars for an evaluation that has passed B4.1's read gate; `write_bundle`; `mark_finished`; `guard_state`; its own sealed bundle; its startup record | index writes |
| replay | `verify_replay` (B4.4), only after the segment has become confirmation data | nonces, diagnostics |
| reader | visible rows only (`t ≥ visible_from`) | everything else |

- **Signer guard [DETAIL; P-7 l.90].** The signer takes its state only from the store's `guard_state(evaluation_id)`, never from the publisher's request. It signs for `R_j` only if all of these hold:
  - the finished record says PASS, with `finished_at < D_w`;
  - the sealed bundle verifies against that record's commitment (the store checks this);
  - P-2 holds on the bundle;
  - `R_j = R_0 + j·86,400` for an integer `j ≥ 0`;
  - `store_now < R_j` and `R_j < C` (C is the store's configured value);
  - no release entry exists;
  - the identity fields equal the pre-read entry.
- **Loss or compromise [NEW DEFAULT; replaces revision 2's Q5].**
  - **There is no key replacement during C2.**
  - *Lost key:* certificates already effective stay valid. A PASS not yet certified expires `U_ops` (P-6).
  - *Suspected compromise:* this is a §26 incident, and no further signing with the key is allowed. A certificate stands only if it has a recorded owner approval **and** incident reconciliation on the store's records shows two things:
    - first, its signed message equals the message the guard rules would produce from those records;
    - second, a committed release entry with `visible_from = cooling_off_start` references it.

    Ed25519 signing is deterministic (RFC 8032, per the reviewers; not available locally), so the legitimate signer would have produced identical bytes. Reconciliation therefore checks the content, not who signed. Every other certificate is void. If the store's own records are in doubt, every certificate without a completed promotion is void.
- **Tests (added):**
  - a caller from an unmapped account is refused;
  - each role is refused each operation outside its row;
  - the signer refuses when `guard_state` and the publisher's request disagree;
  - the reconciliation cases: approved and consistent, approved and inconsistent, and unapproved.

**B3a. The day-255 boundary (S-3, S-5, A-6).**
- **Anchor [NEW DEFAULT]:** A = T, as in revision 2 (D20L-18).
- **Cap [NEW DEFAULT, provisional; D11-15 stays with S4]:** `C = min(A + 255 × 86,400 s, look + 75 × 86,400 s)`. C is computed once and held in the store's configuration. The signer and the store use that one value.

**Comparisons [DETAIL], each action separately.** All times are integer store-clock seconds.

| Action | Valid iff | Source |
|---|---|---|
| Release insert, any `j` (also after C) | `store_now < R_j`; at most one per evaluation | P-7 l.91, l.94 |
| Attestation on a PASS release | the signer guard, including `R_j < C` | P-7 l.90, l.94 |
| PASS released with `R_j ≥ C` | inserted with `attestation: null` and `attestation_ref: null` ("PASS or FAIL and nothing more") | P-7 l.94 |
| Row visible | `t ≥ visible_from` | P-7 l.91 |
| Cooling-off end `E` | first second with 72 available reader-path hours in `[R_j, E)` | P-5 l.96 |
| Owner decision accepted | `E ≤ t_dec < C` | P-6 l.99 |
| Promotion possible | iff `E < C`; with no outage, iff `R_j < C − 259,200 s` | derived |

- **D20L-21, corrected:**
  - A PASS released with `R_j ≥ C − 72 h` cannot be promoted. Nor can one whose reader-path outages make `E ≥ C`.
  - It is still signed if `R_j < C`, because P-7 l.90 says "not after day 255". It is published, and then it expires `U_ops`.
  - A result first released at or after C is published without a certificate. Its status follows P-6.
- **Equality tests,** each at the boundary second and at one second before it:
  - `R_j = C − 259,200` and `C − 259,201`;
  - signing at `R_j = C` and `C − 1`;
  - an insert at `R_j` and `R_j − 1`, with `R_j` both before and after C;
  - a read at `visible_from` and one second before;
  - a decision at `E − 1`, `E`, `C − 1` and `C`.

**B4. Records and the step-2 transaction (S-1, S-2, A-1..A-3). [DETAIL] unless marked.**

**B4.1 `begin_read`: one serialized store transaction.** The publisher calls it. The store runs it under its exclusive lock, which is the same lock that serialises every index append:
1. Verify the index (`read_entries`; damage stops the process as a §26 incident).
2. If a pre-read entry for `evaluation_id` exists, return it unchanged and stop. Repeating the call is therefore safe.
3. If the family's budget is used up (`budget_before = 1 − #pre-read entries for this cycle and family`), record a pre-read rejection with `BUDGET_EXHAUSTED` (B4.3) and stop.
4. Sample `t_s` = the store clock, floored to a whole second. Set `r0 = t_s + 604,800` and `d_w = r0 − 43,200`. `t_s` is the logical read-authorisation time. D-12 step 2's "read start" (l.81) is read as this time.
5. Pick `attempt` = 1 + the highest attempt in the sealed store for this `evaluation_id`. Create a 32-byte nonce (`secrets.token_bytes`) and the DEFAULT bundle (B4.2), with `sealed_at = t_s`. Write `{nonce, bundle, commitment}` under `(evaluation_id, attempt)`, and fsync the file and its directory.
6. Append `aqt.lockbox.pre_read.v1` = `{evaluation_id, attempt, family, nominee_trial_id, prediction_artifact_sha256, eligibility_result_id, lockbox_evaluation_id, budget_before: 1, budget_after: 0, segment_status: "EXPOSED", t_s, r0, d_w}`, and fsync it.

**The read gate.** The store serves lockbox bars only if both of these exist:
- the pre-read entry;
- the sealed default under its `(evaluation_id, attempt)`, verifying against its stored commitment.

**Reconciliation, under the same lock:**
- A sealed default whose attempt has no pre-read entry is an orphan. It is logged as void and binds nothing.
- A pre-read entry whose sealed default is missing or does not verify is a §26 incident. No read takes place, and the process stops until a human reconciles it.

**Tests:**
- two concurrent `begin_read` calls produce one entry;
- a crash after step 5 leaves an orphan, and the next call succeeds with `attempt + 1`;
- a crash after step 6 is followed by a call that returns the existing entry;
- the budget is refused;
- a damaged index stops the process.

**Change from revision 2 (D20L-23).** The pre-read entry no longer carries `default_commitment`. The release entry carries the effective commitment. When the deadline default applies, the two would be equal, so publishing both would tell everyone which FAILs were deadline FAILs. That is more than PASS/FAIL (Constitution l.79).

**B4.2 Sealed bundle, `aqt.lockbox.sealed_bundle.v1` (S-2, A-1; D20L-24..26).**

| Field | Type and rule |
|---|---|
| `schema` | `"aqt.lockbox.sealed_bundle.v1"` |
| `evaluation_id` | string |
| `kind` | `"RESULT"` (written by the worker) or `"DEFAULT"` (written by the store in step 2) |
| `result`, `cause_class` | see the rules below |
| `values` | `t_l, q, mdd_btc_cand, mdd_btc_bench, eth_e_improv, mdd_eth_cand, mdd_eth_bench`: each hexf or null. In a DEFAULT, only `q` is non-null. |
| `conditions` | `L1..L4`: true, false or null. All null in a DEFAULT. |
| `reasons` | sorted, unique `<scope>:<code>` strings (revision 2's enums). `[]` if none. |
| `upside` | if `t_l` is finite: `{status:"COMPUTED", k:int, exceeds_p95:bool, reason:null}`. Otherwise `{status:"NOT_COMPUTED", k:null, exceeds_p95:null, reason:"T_L_UNAVAILABLE"}`. |
| `capture` | `{engine_commit, image_digest, input_manifest_sha256, lockbox_module_sha256, prediction_artifact_sha256}`. The seeds, stream and block are captured through the artifact hash. All are known before the read, so a DEFAULT carries the same values. |
| `operational` | `{read_start, sealed_at, startup_check_id}`, all filled in by the store. `read_start` is the store second at which the first lockbox byte was served, or null in a DEFAULT. `sealed_at` is the store second of the bundle write (`t_s` for a DEFAULT). |

**Rules [DETAIL, except the marked precedence]:**
- `L1 = t_l ≥ q`; `L2 = t_l > 0.0`; `L3 = (mdd_btc_cand − mdd_btc_bench) ≤ 0.05`.
- `L4 = AND(eth_e_improv > 0.0, (mdd_eth_cand − mdd_eth_bench) ≤ 0.05)`, using three-valued AND: false if any part is false, else null if any part is null, else true. A condition is null if any of its inputs is null.
- **Precedence:**
  1. `kind = DEFAULT` gives FAIL/DEADLINE.
  2. Otherwise, any false condition gives FAIL/PERFORMANCE **[NEW DEFAULT, D20L-26]**.
  3. Otherwise, any null condition gives FAIL/TECHNICAL.
  4. Otherwise, PASS with `cause_class` null.
- For D-12 Q2a's cycle label, "failed technically" means `cause_class` ∈ {TECHNICAL, DEADLINE}.
- A finished record, `aqt.lockbox.finished.v1` = `{evaluation_id, result, commitment, finished_at}`, is kept by the store only. The **effective commitment** is this record's commitment if `finished_at < d_w`; otherwise it is the DEFAULT's commitment.
- `commitment = SHA256(nonce ‖ cj(bundle))`.

**Canonical example: PASS.** Made-up values. Placeholder hashes: `0…`, `1…`, `2…` and `3…` stand for 64 hex characters. The bytes are exactly as `cj` writes them:

```
{"capture":{"engine_commit":"eeaa7282e3b7c87790c162d679016c290d5f4ea5","image_digest":"sha256:0…","input_manifest_sha256":"1…","lockbox_module_sha256":"2…","prediction_artifact_sha256":"3…"},"cause_class":null,"conditions":{"L1":true,"L2":true,"L3":true,"L4":true},"evaluation_id":"C2/trend/1","kind":"RESULT","operational":{"read_start":"2026-12-01T00:00:05Z","sealed_at":"2026-12-01T03:10:00Z","startup_check_id":"C2/startup/1"},"reasons":[],"result":"PASS","schema":"aqt.lockbox.sealed_bundle.v1","upside":{"exceeds_p95":false,"k":1275,"reason":null,"status":"COMPUTED"},"values":{"eth_e_improv":"3fc70a3d70a3d70a","mdd_btc_bench":"3fceb851eb851eb8","mdd_btc_cand":"3fcae147ae147ae1","mdd_eth_bench":"3fd51eb851eb851f","mdd_eth_cand":"3fd3333333333333","q":"bfe7645a1cac0831","t_l":"3fda5e353f7ced91"}}
```

The values are `t_l` = 0.412, `q` = −0.731, MDDs 0.21/0.24 (BTC) and 0.30/0.33 (ETH), and `eth_e_improv` = 0.18. `k` = 1,275 is counted against a made-up sorted vector of 2,000 values.

**The other kinds,** given only as their differences from the PASS example:

| Kind | `t_l` | `eth_e_improv` | conditions | `result` / `cause_class` | `reasons` | `upside` | `operational.read_start` |
|---|---|---|---|---|---|---|---|
| performance FAIL | `bfee666666666666` (−0.95) | as PASS | L1 false, L2 false, L3 true, L4 true | FAIL / PERFORMANCE | `[]` | COMPUTED, k 367 | as PASS |
| technical FAIL | as PASS | null | L1-L3 true, L4 null | FAIL / TECHNICAL | `["ETH_EIMPROV:ZERO_VARIANCE"]` | COMPUTED, k 1275 | as PASS |
| mixed (shows the precedence) | −0.95 | null | L1 false, L2 false, L3 true, L4 null | FAIL / PERFORMANCE (revision 2: TECHNICAL) | `["ETH_EIMPROV:ZERO_VARIANCE"]` | COMPUTED, k 367 | as PASS |
| DEFAULT | null (every value null except `q`) | null | all null | FAIL / DEADLINE | `["DEADLINE:NOT_FINISHED_BY_D_W"]` | NOT_COMPUTED, `T_L_UNAVAILABLE` | null; `sealed_at` = `t_s`; `kind` = `"DEFAULT"` |

**B4.3 Other records** (D20L-35; D-12 P-3, Q2b).
- **Release entry:** as in revision 2, `{evaluation_id, result, visible_from, commitment, attestation | null, attestation_ref | null}`. `commitment` is the effective commitment. `attestation` is non-null iff `result = PASS` and `R_j < C`.
- **Rejection entry,** `aqt.lockbox.no_read.v1` = `{family, nominee_trial_id, kind, reason, ancestor_evaluation_id | null, visible_from}`:
  - `kind` ∈ {`PRE_READ_REJECTION`, `BARRED_DESCENDANT`};
  - `reason` is a pre-read reason code (Q2b), or `"BARRED_DESCENDANT"`;
  - for a barred descendant, `visible_from` is the ancestor's release `visible_from`, and never earlier (P-3 l.73). For a pre-read rejection, it is the store second of the insert.
  - Neither kind consumes budget or creates an evaluation ID.

**B4.4 Replay under R-a (A-3; D20L-28).** The store offers `verify_replay(evaluation_id, projection_bytes)` to the `replay` role only. It applies only to an evaluation whose release is PASS, and only after the segment has rolled into confirmation (P-6 R-a, PROPOSAL_REV7 l.110). Inside the store:
1. Load the sealed bundle B and its nonce. Check that `SHA256(nonce ‖ cj(B))` equals the commitment in the committed release entry.
2. Compare `cj(B without "operational")` with `projection_bytes`.

It returns only `MATCH` or `MISMATCH`. If step 1 fails, it returns `MISMATCH` and logs a §26 incident. It never returns a nonce or a diagnostic. The replay job builds its projection by re-running under the recorded `capture`. If it cannot load the bars under `input_manifest_sha256`, the result is MISMATCH. A MISMATCH voids the promotion (§27, Constitution l.194).

**Tests:**
- identical science with different `operational` fields gives MATCH;
- one flipped bit in `values` gives MISMATCH;
- a tampered stored bundle gives MISMATCH plus an incident.

## 2. Findings

**Earlier findings D20L-1..21.** Their text stands as revision 2 left it, with these changes:
- **D20L-12** is **retired**: it is superseded by D20L-22, whose repeatable `begin_read` removes the retry rule. The number is kept.
- **D20L-15** is corrected by D20L-31.
- **D20L-19** means "every offered layout" (Astra note).
- **D20L-21** is corrected to `R_j ≥ C − 72 h`, or `E ≥ C` (B3a).

**New findings:**
- **D20L-22 BLOCKER (repaired in B4.1).** Revision 2's step 2 was not one transaction. Its nonce and default bundle were written outside the fsynced line. `t_s` was defined as the commit instant, which cannot be known when the entry is built. `append_entry` takes its timestamp before the lock (l.388 against l.391) and checks neither uniqueness nor budget. `verify_ledger` cannot look up an evaluation. (S-1, A-2.)
- **D20L-23 BLOCKER (new; repaired in B4.1).** Revision 2's pre-read entry published `default_commitment` (revision 2 l.294). The release entry's commitment equals it exactly when the deadline default applies. Any reader could therefore tell a DEADLINE FAIL from any other FAIL on every read, which breaks Constitution l.79. D-12's pre-read record has no commitment (REV7 l.105), so this defect came from revision 2, not from D-12. Neither re-check found it.
- **D20L-24 BLOCKER (new; repaired in B4.2).** Revision 2's bundle held `times.finished` (l.305). But the bundle is written and committed in step 4, and the finished mark comes in step 5 (REV7 l.83-84). The field could not be filled honestly. It is replaced by the store-filled `operational` section and a separate finished record.
- **D20L-25 BLOCKER (repaired in B4.2).** Revision 2 gave no legal `cause_class` for a PASS. The DEFAULT's precedence, the `read_start` null rule and the full `upside` objects were undefined. (S-2, A-1.)
- **D20L-26 QUESTION (owner, in Q1; new).** Revision 2's rule ("TECHNICAL iff any null") let a null outrank a definite false, and it did not label that as a choice. The label matters because D-12 Q2a discloses "failed technically" in the cycle outcome (REV7 l.57). In the mixed example the two rules give different labels. Recommended: a definite false is PERFORMANCE, because the missing value could not have changed the FAIL.
- **D20L-27 BLOCKER (repaired in B3a).** Revision 2's blanket rule "valid only if `t < C`" contradicted P-7 l.94's duty to publish after the cap. Its equality case also missed `R_j = C − 72 h`. (S-3, S-5, A-6.)
- **D20L-28 BLOCKER (repaired in B4.4).** Revision 2's replay compared whole bundles, so every faithful replay would fail on its timestamps and its startup ID, and R-a would void a valid promotion. (A-3.)
- **D20L-29 BLOCKER (repaired in B1).** Revision 2 had no caller authentication and no trusted source for the signer's guard state. It also kept approvals after a compromise without reconciliation. (A-4.)
- **D20L-30 QUESTION (owner, Q5).** The `% 2**31` mapping is a new default, not a necessary detail. Revision 2's seed-0 equivalence test confused determinism with seed invariance. (S-4.)
- **D20L-31 BLOCKER (new; scheduling).** R-14 (DRAFT l.152) puts the C2 confirmation fit in `screen.py`, so revision 2's alternative of "a fit path in the lockbox and C2 code" does not exist for that fit. Q5's recommended option needs a reviewed `screen.py` seed parameter merged **before the qualification-object freeze** (FREEZE_HELDOUT step G). After the freeze, only seed 0 everywhere remains consistent, and that requires a C2 row overriding R-13's sentence on the nominee's fit. Separately, Annex C l.412 names a declaration seed that does not exist (`TRIAL_FIELDS`, l.302-306), so its wording needs correcting (A1b).
- **D20L-32 NON-BLOCKING (repaired in A7).** The `L266_TRIAL_SEED` alternative was always rejected by A7's check. (A-5.)
- **D20L-33 NON-BLOCKING (repaired in A6).** `EventResult.start` is an index. The instant is now resolved through the series. (S-6.)
- **D20L-34 BLOCKER (new; owner Q2(ii) and S4).** The runner reads the open of the bar after a window (l.139, l.206; RN-1, `screen.py` l.719-720).
  - For the lockbox, that bar is outside D-11's authorised range, so the bound runner refuses every full-length run (§0).
  - For the confirmation source, that bar is the first lockbox bar (Constitution l.73).

  This defect is inherited from the C-6/RN-1 convention combined with D-11 REV3 l.57; it was not introduced by revision 2. Neither re-check found it. It governs every C2 confirmation run, so the end-price rule belongs in S4 (C-0/C-6). D-20 must follow that rule, or A7's hash check fails.
- **D20L-35 NON-BLOCKING (repaired in B4.3).** D-12 requires D-20 to bind `BARRED_DESCENDANT` and its publication-time rule (REV7 l.136). Revision 2 gave pre-read reason codes but no record for either.
- **D20L-36 QUESTION (inherited from D-12; not repaired here; owner or S4 wording).** The owner's Q6(ii) answer reads "results already finished keep their outcome" (`OWNER_DECISION_D12.md` l.18). The decided P-6 text says a result "not yet visible" at day 255 expires `U_ops` (REV7 l.99). The two differ for a FAIL that is finished before C but first released after C. That case is possible whenever `t_s + 7 d ≥ C > d_w`. D-20's publication path is the same either way; only the nominee's status label differs. This is left unrepaired, because the fix changes the wording of an owner decision. Recommended: P-6's text governs, because D-12 was decided as "P-1..P-8" (l.22); the owner should confirm this when signing C2.

## 3. Owner questions (each has "Keep blocked")

**Q1. Adopt the detail rows and the new defaults?**
- **[DETAIL]:**
  - A1a, A3, A4, A5, A6's conversion and error mapping, A7's schema and checks;
  - B2, B3, B3a's comparisons, B4 (the transaction, schemas, records and replay), B5.
- **[NEW DEFAULT]:**
  - the startup vector check;
  - sealing that includes the recomputation;
  - Ed25519 through a maintained library, with the key made before C2;
  - **no key replacement during C2**, and the compromise rule (B1);
  - service identities on a local channel (B1);
  - the anchor A = T;
  - the provisional cap `min(A + 255 d, look + 75 d)`, until S4 settles D11-15;
  - "a definite fail outranks a missing value" (D20L-26).

In plain words, the last one decides this: if the Bitcoin test clearly failed but the Ethereum check could not be computed, the result is recorded as a normal failure, not as a technical breakdown. Only a technical breakdown can appear in the cycle label.

- **"Adopt (Recommended)."** Cost: several builds, each needing §16 review. A lost or stolen key can cost a good PASS in this cycle.
- **"Keep blocked."** The lockbox cannot run, so C2 cannot promote anything.

**Q2. How do the runs that feed and make up the lockbox test start and end?**
- **(i) Start:**
  - **"Strategy and benchmark start with no position on the first day, each paying its entry cost (Recommended)."** This matches the lockbox start you already decided. Cost: an entry cost on the first day.
  - **"Carry positions over from the warm-up."** Cost: the forecast and the lockbox start differently, and D-11's stated reason no longer holds.
- **(ii) End:** the last hour needs a closing price.
  - **"Use the last hour's own closing price (Recommended)."** The lockbox checker never needs data from after its period, and the confirmation runs never touch the first lockbox price. Cost: the S4 draft must state this for every confirmation run, and the code needs one small, tested adapter.
  - **"Read one more price, just after the period."** No adapter is needed for the lockbox. Cost: it changes the data permission you gave in D-11. For the confirmation runs it would mean reading a lockbox price, which is forbidden, so those runs would still need the closing-price rule.
- **"Keep blocked."**

**Q3. Which seed drives the lockbox forecast's random draws?** (Unchanged; it is now workable either way.)
- **"The post-protected seed, as for G-1 (Recommended)."** Cosmetic edits before the public post cannot pick it. Cost: one more C2 row.
- **"The old protocol seed (l.266)."** No wording change. Cost: the seed is known before the post, so cosmetic edits can be tried offline. This must be disclosed.
- **"Keep blocked."**

**Q4. Where does the lockbox code live?** (Unchanged.)
- **"One separate reviewed lockbox module, its hash in the signed C2, with a narrow R-14 exception (Recommended)."** Cost: one amendment row, and the build and review must happen before you sign C2.
- **"The forecast code inside `screen.py` before the freeze."** Cost: the freeze waits for it, and the exception is still needed for the lockbox service.
- **"Keep blocked."**

**Q5. Which number seeds the chosen strategy's own model fit?** This is time-sensitive (D20L-31).
- **"The protocol's seed, turned into an ordinary number in a fixed way (Recommended)."** This follows the rule you kept in D-20/D-13 (R-13). Every C2 fit uses it, and nothing fitted the old way counts as C2 evidence. Cost: a small reviewed change to `screen.py` must be merged **before the freeze (step G)**. If the freeze comes first, this option is gone.
- **"Keep the screen's seed 0 everywhere."** No code change, and the freeze is not delayed. Cost: a C2 row must override part of your R-13 decision. The results are unaffected only if the model fits truly ignore the seed. The screen assumes they do (MR-2), but that is not proven.
- **"Keep blocked."**

## 4. What changed in revision 3, and what remains

**Changed:**
- the step-2 transaction, the read gate and reconciliation;
- the commitment leak removed;
- the circular `finished` field removed;
- typed schemas with canonical examples, and an explicit precedence;
- the cap split by action, with `≥`;
- replay by projection;
- identities, the ACL, the signer's guard source and the compromise rule;
- the seed mapping moved to its own question, the unsound test replaced, and the R-14 timing stated;
- the `seed_source` enum;
- the series-resolved start;
- the final-hour rule;
- the rejection and barred-descendant records;
- the simplifications in §1a.

Nothing in D-11, D-12 or D20_D13 is reopened. D20L-36 is a question about D-12's existing wording, not a change to it.

**Remaining:**
- the R19-2 re-check of this revision;
- owner Q1-Q5;
- the S4 items: D11-15, D20L-18 (the anchor for day 180), D20L-34 (the end-price rule) and the Annex C l.412 wording;
- the owner confirmation in D20L-36;
- C2 rows for R-8, R-13 (Q3), R-14 (Q4), `added_purposes`, the public key and the anchor;
- builds, each a later authorised task under §16 review (Constitution l.147-153; lockbox ACL tooling and promotion gate): the store with `begin_read` and `verify_replay`, the publisher, the signer, the lockbox module and its vectors, the C2 evaluation record with `d_sha256`, the `screen.py` seed parameter (Q5), the A6 adapter, and the tests.

**Unauthorised:**
- frozen edits, activation and acceptance;
- any code;
- key generation;
- simulation;
- confirmation or lockbox access;
- promotion, deployment and trading.

`KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.

**Self-description check** (done after the last edit):
- one file written, no git command run;
- re-check findings answered: 12 of 12 (S-1..S-6, A-1..A-6);
- new findings D20L-22..36, with no gaps; D20L-12 is retired with its number kept;
- five owner questions.
