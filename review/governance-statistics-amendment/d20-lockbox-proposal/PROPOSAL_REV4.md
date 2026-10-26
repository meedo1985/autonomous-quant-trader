# D-20 lockbox bindings: proposal, revision 4 (delta on revision 3)

**Author:** the `senior-statistical-governance` agent. Observed model: Claude Opus 5.5, model ID `claude-opus-5-5` (this session's own metadata, not an instruction). I am an AI reviewer, not an authority. I propose and check bindings; I cannot decide, accept, activate or amend anything.

**Status: INACTIVE PROPOSAL.** Nothing frozen changed. No row binds until the owner decides and signs the C2 §4 amendment. This is a **delta**: `PROPOSAL_REV3.md` stands except where a section below says "replaces". Revisions 1-3 stay as history.

**VERDICT: `AMENDMENT_REQUIRED`.**

**Answers** (both read in full): `SOL_REREVIEW2_C86EA8D.md` (gpt-6-sol, FIX, D20LR3-S-1..6) and `ASTRA_REREVIEW2_C86EA8D.md` (gpt-6-astra, FIX, D20LR3-A-1..6; its body labels them `D20LR3-S-n`, its header maps them to A-n, and A-n is used here).

**Review status:** revision 4 is unreviewed. R19-2 requires a focused re-check by two model families before any owner decision. No human statistician has reviewed it.

**Checkout and mode:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch `freeze-sheet`. I wrote this one file only and ran **no git command**. The caller also asked for `REREVIEW3_PROMPT.md`. My standing authority covers one new report file per task (owner decision 2026-10-25), as in revision 3, so I returned that prompt's full text to the caller. No confirmation or lockbox data, network, credentials, keys or simulation were used.

## 0. Verification

**Read this session:** revision 3 in full; revision 2 l.95-154 and l.225-324; both re-check records; `REREVIEW2_PROMPT.md`; `d12-proposal/PROPOSAL_REV7.md` l.55-149; `OWNER_DECISION_D12.md`; `OWNER_DECISION_D11.md`; `d11-proposal/PROPOSAL_REV3.md` l.48-107; Constitution l.73, 75, 79, 81, 147-153, 194; `protocols/protocol_v1.yaml` l.70-80; DRAFT_WORDING l.145-153, l.218-224, l.240-246; Annex C l.403-414; `deploy/calibration/FREEZE_HELDOUT.md` l.1-50.

**Code read this session:** `event_contract.py` l.90-221; `bars.py` l.120-135, l.181-209, l.273-295; `ledger.py` l.280-416; `screen.py` l.300-306, l.714-723, l.1470-1478, l.1540-1550; `seeds.py` l.11-19; `calibration/qobj.py` l.40-64, l.198-210.

**Calculations** (main checkout's venv Python, `-I -B`, script and lock file in the session scratch directory, worktree `src` on `sys.path`; nothing written to the repository):
1. **Interval (S-4/A-5).** A `BarSeries` of 28 two-hour bars, with `sigma_bps` supplied, ran through `run_event_contract`. It returned 24 equity points starting at 2025-06-01T00:00Z and spanning **48 h**. This reproduces Astra's counterexample.
2. **Nested lock (D20L-46).** With `msvcrt.locking` held on one descriptor of a lock file, a second descriptor of the same file in the same process was **refused** (errno 13). POSIX `flock` on a second open file is expected to conflict in the same way: `UNVERIFIED_EXTERNAL_ASSUMPTION`, not run here.
3. **L4 (A-2).** With L1-L3 true: parts (false, null) give `AND3` = false, so PERFORMANCE; the rule "null if any input is null" gives null, so TECHNICAL. Parts (true, null) give null and TECHNICAL under both rules. The two rules therefore differ only on the first case.
4. **Seed zero (A-3).** `int(s,16) % 2**31` is 0 for any 64-hex `s` whose last 8 hex digits are `00000000` or `80000000`. Example: `"0"*56 + "80000000"` gives 0. The probability is 2^-31 per seed, which is legitimate and nonzero.
5. **Fixture (S-5).** The rebuilt PASS bytes (B4.2 below) are 1,053 bytes, with SHA-256 `d64d228b84a1aaf6015a6860af7f69f2315cc77865e0afad4547822ab54ba520`. All seven hexf values equal revision 3's. Discriminating check: replacing one capture hash with `"1"*64` changes the digest.
6. `hexf(−0.1)` = `bfb999999999999a`, and `hexf(−0.95)` = `bfee666666666666`.

**Code facts the repairs depend on:**
- `BarSeries.interval` may be any positive interval (`bars.py` l.192, l.200).
- `run_event_contract` checks the interval only through the default volatility path (l.152-156); `sigma_bps` bypasses that check.
- `append_entry` takes `_exclusive_lock` on a sidecar file (l.391, l.340-366). `read_entries` takes no lock (l.301-308).
- `walk_forward` hard-codes seed 0 (`screen.py` l.1547).
- `qobj._reviewed` refuses a later file whose SHA-256 is not listed in `review/d19-engine/FREEZE_REVIEWS.json` with a committed review record (l.198-210). That file is absent in this worktree. Step G names build commit `ed0bfbf…` (FREEZE_HELDOUT l.29-50).

**Governing text found by searching on each topic** (item 1):
- DRAFT l.241 ("order: trend nominee, then volatility nominee") and l.243 (`lockbox_cooldown_days: 30`, "between the two families' reads"). Revision 3 did not cite either; both bear on D20L-45.
- DRAFT l.244 and P-6 ("At day 255 processing ends"). Revision 3's `begin_read` has no cap guard (D20L-50).
- R-14's last sentence (DRAFT l.152) bears on D20L-48.
- `OWNER_DECISION_D11.md` l.11 ("first permitted entry") bears on D20L-42.

**Carried, not re-read:** revision 3 §0's carried items; the lockbox index arithmetic (start 22,344, n 10,968, length 33,312), which Astra reproduced independently (report l.95); the claim that the confirmation source ends at L0.

## 1a. Dispositions

**Overlaps:** S-1 = A-1; S-3 = A-6; S-4 = A-5. Four rows were marked FIX. Sol marked A-4 FIX; it is answered by S-1/A-1 (D20L-37). Astra marked S-4 FIX (answered by A-3, D20L-44), A-1 FIX (answered by A-2, D20L-43) and A-2 FIX (answered by A-4, D20L-45).

| ID | Disposition | Evidence | Repair (where; finding) |
|---|---|---|---|
| **S-1 = A-1** (publisher `state` leaks finish) | **Accepted, modified** | Revision 3's B1 row (l.180) gave the publisher "finished `{result, commitment}`" with no time condition. Before `d_w`, the presence of a finished record separates a deadline FAIL from a finished FAIL. The publisher never needs state before `d_w`: its first window opens at `R_0 − 6 h = d_w + 6 h`. E-3 is applied, and narrowed further: the publisher never receives a commitment, because the store fills the commitment in itself at insert. | B1 table; D20L-37 |
| **S-2** (`begin_read` lacks an entitlement) | **Accepted** | Revision 3's B4.1 checked the index, uniqueness and budget only (l.236-242), and its gate required only two records (l.244-246). D-12 step 1 (REV7 l.80) and D-11 sealing ("only status (a) requests a read", REV3 l.96) were not checked by the store. Step 2 also returned an existing entry without verifying its default. | B4.1 steps 2-4; D20L-38 |
| **S-3 = A-6** (no release lower bound) | **Accepted** (Astra's complete form) | P-7 (REV7 l.88) sets the window `[R_j − 6 h, R_j)`. Revision 2's B3 kept it (l.271), and revision 3 left B3 standing (l.109-119), but revision 3's B3a table said "valid iff `store_now < R_j`" (l.215). Implemented literally, the table admits early inserts. The signer guard had the same gap (l.189-190). | B3a; signer guard; D20L-39 |
| **S-4 = A-5** (interval) | **Accepted** | Calculation 1 reproduces the 48 h "day". | A6; D20L-40 |
| **S-5** (fixture placeholders; `k`) | **Accepted** | Calculation 5. `k` and `exceeds_p95` cannot be recounted without the vector, so they are labelled illustrative. | B4.2; D20L-41 |
| **S-6** (entry-cost wording) | **Accepted** | `OWNER_DECISION_D11.md` l.11 says "at its first permitted entry". The wrong wording is **inherited**: it came from revision 2's Q2 (l.389), was carried into revision 3 (l.376), and D-11 REV3 l.70 says "at L0". Revision 2's A2 row (l.142) is already correct. The owner decision governs. Committed history is not edited. | Q2(i); D20L-42 |
| **A-2** (L4 contradiction) | **Accepted** | Calculation 3. Revision 3's l.278 contained both rules. | B4.2 rules; D20L-43 |
| **A-3** (Q5 seed-0 branch; numeric zero) | **Accepted** | Revision 3's A1b gave the modulo mapping unconditionally (l.125) and said "nothing fitted with seed 0 counts" (l.126). Both contradict Q5's alternative (l.395), and calculation 4 shows that the mapping itself can return 0. Swept to Annex C l.412-413: "null draws never reuse it" must also mean derivation, not value inequality. | A1b; Annex C wording; D20L-44 |
| **A-4** (cross-family cooldown) | **Accepted, modified** | DRAFT l.241 and l.243 were not checked under the lock. A refusal for cooldown or order now **defers** the call; it is not a final rejection. A pre-read rejection is permanent (REV7 l.80, l.99), so revision 1-3's `COOLDOWN_NOT_ELAPSED` rejection code could have ended a family's test over a scheduling slip. That code was an AI detail; it is not in D-11 item 3. The cap was added as a third shared condition (D20L-50). | B4.1 step 5; D20L-45, D20L-50 |
| Astra note: read gate during append | **Accepted, extended** | `read_entries` takes no lock, so a gate run without the lock could see a partial line (a false §26 incident) or a line not yet fsynced. A separate defect also surfaced: revision 3's "the same lock that serialises every index append" (l.236), if taken literally, nests `append_entry`'s own sidecar lock, and that nested lock is refused (calculation 2). | B4.1 lock; D20L-46 |
| Astra note: D20L-36 is not a contradiction | **Accepted** | P-6 distinguishes the result, which is kept and published (P-7 l.94), from the nominee's status, which is `U_ops` if the result was not visible at C. The owner's "results already finished keep their outcome" holds for the result. Sol wanted the wording clarified; the sentence in §2 does that without changing an owner decision. | D20L-36 reclassified |
| Astra note: Q5 timing is operational | **Accepted** | Step G names a fixed build commit, and `qobj._reviewed` binds `screen.py` by hash. "Gone" means unavailable under the retained R-14 frozen-object route. | Q5; D20L-47 |
| Astra note: the Q2 adapter needs R-14 placement | **Accepted, promoted to a finding** | R-14's last sentence puts C2 evaluation code in the engine commit or a later object file. The confirmation-run end-price rule is C2 evaluation code, so D20L-31's timing applies to it too (item-5 sweep). | Q2(ii); D20L-48 |
| E-1, E-2 | **Applied** (both reviewers confirmed them) | REV7 l.109-110 puts R-a under "Reproduction (Q4)", and `OWNER_DECISION_D12.md` l.15 records it. RN-1 is at `screen.py` l.720-721. | D20L-49 |
| E-3 | **Applied** | As in the first row. | D20L-37 |
| Sol note: drop `attestation_ref` | **Accepted, modified** | `attestation_ref` = SHA-256(cj(attestation)) (revision 2, l.316) can be derived from the embedded object, and no operation looks it up (revision 3, l.217, l.306). D-12's Records list names `attestation_ref` (REV7 l.106), so D-20 binds that name **as** the embedded attestation; the hash is computed when needed. | B4.3 |
| Astra note: duplicate derivable fields | **Accepted, in part** | `t_s` and `d_w` are dropped from the pre-read entry, because both are derivable from `r0`, which D-12 requires (REV7 l.105). `budget_before`/`budget_after` are kept, because D-12 step 2 requires the decrement to be durably written. | B4.1 |
| Sol note: Q1 must not settle D11-15 | **Accepted** | Q1 states it. | Q1 |
| Astra notes on D20L-24 ("circular" is imprecise) and D20L-31 ("under the retained R-14") | **Accepted** | Wording only. | §2 |

## 1. Bindings (replacements)

**A1b, replaces revision 3's A1b (D20L-44).**
- **[DECIDED]** `seed_l266 = trial_seed(protocol_hash, hypothesis_hash, trial_index)`, per R-13.
- **[Q5]** The signed C2 fixes `estimator_seed_policy` ∈ {`L266_MOD_2_31`, `ZERO`}:
  - `L266_MOD_2_31`: `estimator_seed = int(seed_l266, 16) % 2**31`. A value of 0 is legitimate and is accepted;
  - `ZERO`: `estimator_seed = 0`. This needs a C2 row overriding R-13's "including the nominee's own fit".
- **Recorded.** The nominee identity (A7) stores `seed_l266`, `estimator_seed_policy` and `estimator_seed`. The pre-read check re-derives `estimator_seed` from the signed policy; any difference gives `IDENTITY_MISMATCH`.
- **What counts as C2 evidence.** A fit counts only if its record names the signed policy and the seed derived under it. The check is on the recorded policy and derivation, **never on the numeric value 0**. The D-19 screen's fits (seed 0, MR-2) only chose the nominee and are not C2 evidence under either policy. The confirmation fit, the A7 sealing re-run and the lockbox refit all use `estimator_seed`.
- **Tests:**
  - same-seed reproduction, for each allowed class;
  - one re-derivation vector per policy, including an `L266_MOD_2_31` seed that maps to 0, which is accepted;
  - a fit recorded under the other policy is refused.
- **Code location.** As revision 3 (D20L-31), with D20L-47's operational condition.
- **Annex C l.412-413 proposed wording (S4):** "The nominee's own fit uses the estimator seed of the signed estimator-seed policy (D-20 A1b). Null-draw seeds come from their own stream and are never derived from it; an equal value arising by chance is not reuse."

**A6, adds to revision 3 (D20L-40).** For each leg, the adapter also checks `series.interval == timedelta(hours=1)`. `BarSeries` already forces every bar's interval to equal the series interval (l.205). With contiguity and the resolved start, this fixes every hourly instant. Test: calculation 1's two-hour series is refused.

**B1 publisher and lockbox_eval rows, replace revision 3's rows (D20L-37, D20L-38).**

| Role | Allowed store operations | Never |
|---|---|---|
| publisher | `begin_read` (B4.1). `insert_release(evaluation_id, j, attestation \| null)`: the store fills `result` and the effective commitment from its own records, and refuses an attestation unless the effective result is PASS, `R_j < C`, and the attestation's evaluation ID and `cooling_off_start = R_j` match. `state(evaluation_id)`: `{"fixed": false, "store_now": t}` while `t < d_w`; from then on `{"fixed": true, "released": bool, "result": "PASS" \| "FAIL", "store_now": t}`, with the effective result and the same shape for every FAIL. | commitments, nonces, sealed bundles, cause classes, finished-record presence or time, lockbox bars |
| lockbox_eval | `record_pre_read_check` (B4.1). Lockbox bars through the read gate. `write_bundle`, `mark_finished`, `guard_state`. Its own sealed bundle and startup record. | index writes |

**Signer guard, replaces revision 3's two time bullets (D20L-39):**
- `R_j = R_0 + j·86,400` for an integer `j ≥ 0`;
- `R_j − 21,600 ≤ store_now < R_j`, and `R_j < C`.

**B3a comparisons, replaces revision 3's first three table rows (D20L-39).** Each row now states complete validity conditions. The other rows stand.

| Action | Valid iff |
|---|---|
| Release insert, any `j`, also after C | `R_j = R_0 + j·86,400` with integer `j ≥ 0`; `R_j − 21,600 ≤ store_now < R_j`; no release entry yet exists for the evaluation |
| Attestation on a PASS release | the signer guard above |
| PASS released with `R_j ≥ C` | inserted with `attestation: null` |

**Added equality tests:**
- inserts at `R_j − 21,601` (refused), `R_j − 21,600` (accepted), `R_j − 1` (accepted) and `R_j` (refused);
- `j = −1` and a non-whole-day `R_j` (both refused);
- a second insert (refused);
- the same four instants for signing.

**B4.1, replaces revision 3's B4.1 (D20L-38, D20L-45, D20L-46, D20L-50).**

*The store lock.* `L_store` is one lock on the store's own lock file, **not** the ledger's sidecar lock. Every store operation holds it for its whole duration: `begin_read`, `insert_release`, no-read inserts, `record_pre_read_check`, `write_bundle`, `mark_finished`, `state`, `guard_state`, the read-gate check, `verify_replay` and reconciliation. Inside it the store calls `append_entry` unchanged. Because the store is the only index writer (B1), that call's inner sidecar lock is never contended.

*The pre-read check record.* `lockbox_eval` runs D-12 step 1 (D-11 item 3 and the P-4 vector check), then calls `record_pre_read_check`. The store keeps `aqt.lockbox.pre_read_check.v1` = `{check_id, evaluation_id, family, nominee_trial_id, prediction_artifact_sha256, eligibility_result_id, lockbox_evaluation_id, sealing_id, startup_check_id, lockbox_module_sha256, image_digest, result: "PASS" | <reason code>, checked_at}`. It keeps at most one per `evaluation_id`, because there is no retry in C2 (D-11 REV3 l.55). The record is not on the index.

*`begin_read(evaluation_id)`* is called by the publisher and runs under `L_store`:
1. Verify the index with `read_entries`. Damage stops the process as a §26 incident.
2. If a pre-read entry for `evaluation_id` exists, check that its sealed default exists and verifies (otherwise a §26 incident, stop). Then return the entry unchanged. If a rejection entry for this nominee exists, return it unchanged.
3. **Entitlement.**
   - Sealing records exist for every declared family. This family's record is status (a) for this nominee and this artifact hash.
   - A check record exists whose identity fields equal the sealing record and the request.
   - Its `startup_check_id` names a `PASS` startup record for the same module hash and image.
   - If there is no check record, or the identities differ, the call is refused, nothing is written, and an incident is logged.
   - If the check's result is a reason code, append a rejection entry with that reason (B4.3) and stop.
4. **Budget.** If this family already has a pre-read entry this cycle, append a rejection entry with `BUDGET_EXHAUSTED` and stop.
5. **Shared conditions.** Sample `t_s` = the store clock, floored to the second. Then:
   - **cap:** if `t_s ≥ C`, refuse with `CAP_REACHED` and write nothing; P-6 already gives the nominee `U_ops`;
   - **order** (DRAFT l.241): for the volatility family, while the trend family is status (a) and has neither a pre-read entry nor a rejection entry, return `DEFERRED` and write nothing;
   - **cooldown** (DRAFT l.243): if the other family has a pre-read entry with `r0'`, and `t_s < r0' − 604,800 + 2,592,000`, return `DEFERRED {earliest}` and write nothing.
6. `r0 = t_s + 604,800`. `t_s = r0 − 604,800` is the logical read-authorisation time, and `d_w = r0 − 43,200`. Pick `attempt`, create the nonce and the DEFAULT bundle (`sealed_at = t_s`), write them with the commitment, and fsync the file and its directory. This is revision 3's step 5.
7. Append `aqt.lockbox.pre_read.v1` = `{evaluation_id, attempt, family, nominee_trial_id, prediction_artifact_sha256, eligibility_result_id, lockbox_evaluation_id, pre_read_check_id, budget_before: 1, budget_after: 0, segment_status: "EXPOSED", r0}`, fsynced before `L_store` is released.

*The read gate* is checked under `L_store`. It serves lockbox bars over `[S_pre, L1)` under the manifest only to `lockbox_eval`, and only if three things hold:
- the pre-read entry exists;
- its sealed default verifies;
- the caller holds a `PASS` startup record for the check record's module hash and image.

Step 7 fsyncs before the lock is released, so a passed check only ever sees a durable entry.

*Reconciliation* is as in revision 3, under `L_store`.

*Pre-read reason codes:* revision 2's list without `COOLDOWN_NOT_ELAPSED`.

*Tests:* revision 3's list, plus these:
- two families calling concurrently, and in sequence, inside the cooldown: one entry, then `DEFERRED`;
- cooldown at `earliest − 1` and at `earliest`;
- order deferral, and its release by a trend entry and by a trend rejection;
- `t_s` at `C − 1` and at `C`;
- a read-gate check racing step 7's write and fsync: it gets no bars, and raises no false incident;
- a call with no check record (refused, nothing written);
- a failed check called twice (exactly one rejection);
- an existing entry whose default is damaged (an incident, not a return).

**B4.2 rules, replaces revision 3's first two rule bullets (D20L-43).**
- Atomic comparisons: `c1 = t_l ≥ q`, `c2 = t_l > 0.0`, `c3 = (mdd_btc_cand − mdd_btc_bench) ≤ 0.05`, `c4a = eth_e_improv > 0.0`, `c4b = (mdd_eth_cand − mdd_eth_bench) ≤ 0.05`. **Each comparison is null iff one of its own inputs is null.**
- `L1 = c1`, `L2 = c2`, `L3 = c3`, `L4 = AND3(c4a, c4b)`: false if either part is false, else null if either is null, else true.
- This follows D20L-26's principle that a definite false outranks a null. If Q1 rejects that principle, `L4` uses null-dominant AND as well.

**Two added rows for revision 3's "other kinds" table:**

| Kind | `eth_e_improv` | `mdd_eth_cand` | conditions | `result` / `cause_class` | `reasons` |
|---|---|---|---|---|---|
| ETH false/null | `bfb999999999999a` (−0.10) | null | L1-L3 true, L4 false | FAIL / PERFORMANCE | `["ETH_MDD:NONFINITE_RESULT"]` |
| ETH true/null | as PASS | null | L1-L3 true, L4 null | FAIL / TECHNICAL | `["ETH_MDD:NONFINITE_RESULT"]` |

**PASS fixture, replaces revision 3's example (D20L-41).** The capture hashes are the SHA-256 of the ASCII labels `example-image`, `example-input-manifest`, `example-lockbox-module` and `example-prediction-artifact`. `k` = 1,275 and `exceeds_p95` = false are **illustrative**; no vector is supplied. The bytes, exactly as `cj` writes them (1,053 bytes, SHA-256 `d64d228b84a1aaf6015a6860af7f69f2315cc77865e0afad4547822ab54ba520`):

```
{"capture":{"engine_commit":"eeaa7282e3b7c87790c162d679016c290d5f4ea5","image_digest":"sha256:7ba451133c403e85ee98073f28fd640bc9aa5000f0d6fce0f0b06ff7ac4cd9c5","input_manifest_sha256":"68d61e030a16f878cc1b64844f3602b5b82fcea34b543043c8b4cca9e3bbccdb","lockbox_module_sha256":"fec433994ce42c7661a8899f324daba51a5ea2c015be1f1835caf3de2c8b4688","prediction_artifact_sha256":"cfff21297950845616f31804663f1bb37ec7417d0653242e0b8cd1bdf591cf94"},"cause_class":null,"conditions":{"L1":true,"L2":true,"L3":true,"L4":true},"evaluation_id":"C2/trend/1","kind":"RESULT","operational":{"read_start":"2026-12-01T00:00:05Z","sealed_at":"2026-12-01T03:10:00Z","startup_check_id":"C2/startup/1"},"reasons":[],"result":"PASS","schema":"aqt.lockbox.sealed_bundle.v1","upside":{"exceeds_p95":false,"k":1275,"reason":null,"status":"COMPUTED"},"values":{"eth_e_improv":"3fc70a3d70a3d70a","mdd_btc_bench":"3fceb851eb851eb8","mdd_btc_cand":"3fcae147ae147ae1","mdd_eth_bench":"3fd51eb851eb851f","mdd_eth_cand":"3fd3333333333333","q":"bfe7645a1cac0831","t_l":"3fda5e353f7ced91"}}
```

**B4.3 release entry, replaces revision 3's line:** `{evaluation_id, result, visible_from, commitment, attestation | null}`. The `attestation_ref` field of D-12's Records is bound as the embedded `attestation`. Its SHA-256(cj(...)) is derived when a reference is needed. "A committed release entry … references it" (P-7 l.93) means that the entry embeds it.

**B4.4:** "P-6 R-a, PROPOSAL_REV7 l.110" becomes "D-12 Q4 route R-a (PROPOSAL_REV7 l.109-110; `OWNER_DECISION_D12.md` l.15)" (E-1).

## 2. Findings

**Changes to earlier findings:**
- **D20L-24:** "circular" becomes "recorded a later event in bytes already committed".
- **D20L-31:** it holds "under the retained R-14 route".
- **D20L-34:** "l.719-720" becomes "l.720-721".
- **D20L-36** is **reclassified NON-BLOCKING** (S4 wording). The two texts are reconciled. A result finished before C but first released at or after C is published as its result (P-7 l.94) and counts under P-3. The nominee's status is `U_ops` (P-6 l.99). T-6's "a visible FAIL never receives `U_ops`" concerns FAILs visible before C. The S4 draft should say this in one sentence, which Q1 shows the owner. No owner decision is re-worded.

**New findings:**
- **D20L-37 BLOCKER (repaired, B1).** Publisher `state` exposed finished-record presence and the commitment before `d_w`. (S-1, A-1, E-3.)
- **D20L-38 BLOCKER (repaired, B4.1).** `begin_read` bound no verified pre-read entitlement, and it returned an existing entry without reconciling it. (S-2.)
- **D20L-39 BLOCKER (repaired, B3a and signer guard).** The store and the signer accepted actions before P-7's six-hour window, and the table did not state the `j` or uniqueness conditions. (S-3, A-6.)
- **D20L-40 NON-BLOCKING (repaired, A6).** No one-hour interval check. (S-4, A-5.)
- **D20L-41 NON-BLOCKING (repaired, B4.2).** The fixture had placeholder hashes, and its `k` could not be checked. (S-5.)
- **D20L-42 NON-BLOCKING (repaired, Q2(i)).** The entry-cost wording misstated D-11. It was inherited from revision 2's l.389. (S-6.)
- **D20L-43 BLOCKER (repaired, B4.2).** The L4 rule contradicted itself, and the contradiction changes the disclosed cycle label. (A-2.)
- **D20L-44 BLOCKER (repaired, A1b; S4 wording).** The seed derivation and the evidence rule ignored Q5's alternative, and the evidence rule tested the value 0. (A-3.)
- **D20L-45 BLOCKER (repaired, B4.1).** Order and cooldown were not rechecked under the lock. The cooldown was a permanent rejection. (A-4.)
- **D20L-46 BLOCKER (repaired, B4.1).** The read gate ran without the transaction lock, so it could serve bars against a pre-read entry not yet fsynced. Revision 3's lock wording would also nest the ledger's own lock, which is refused (calculation 2). (Astra note; the nesting was found here.)
- **D20L-47 NON-BLOCKING (Q5 wording).** "Merge before G" is not enough. The freeze must name a build commit whose `screen.py` is the reviewed seed version, with its SHA-256 listed in `FREEZE_REVIEWS.json` (`qobj.py` l.198-210). The sheet's G0/G commit `ed0bfbf…` must be replaced, and G0 re-run, before step G. (Astra note.)
- **D20L-48 BLOCKER (new; scheduling; Q2(ii)).** Under R-14 (DRAFT l.152, last sentence), the Q2(ii) end-price rule for **confirmation** runs is C2 evaluation code, so it must also be in the reviewed `screen.py` in the frozen object. If the freeze comes first, confirmation runs can end only by reading the L0 bar, which is forbidden (Constitution l.73). C2 then stays blocked unless a formal amendment changes this. This is revision 3's D20L-31 argument, swept onto D20L-34's repair, which revision 3 did not do. (Astra note, report l.103.)
- **D20L-49 NON-BLOCKING (applied).** Citation errata E-1 and E-2.
- **D20L-50 BLOCKER (new; repaired, B4.1).** `begin_read` had no cap guard, so a read could start after C, after "processing ends" (P-6 l.99; DRAFT l.244). Found while sweeping A-4's "shared admission conditions". Not proposed: refusing reads that start too late to be promoted (`r0 + 72 h ≥ C`). That would be a new choice. Under P-6 such a read is still processing, and it still yields a published result.

## 3. Owner questions (replace revision 3's; each has "Keep blocked")

**Q1. Adopt the detail rows and the new defaults?** These are revision 3's Q1 list plus:
- the pre-read entitlement and the store lock;
- the release window;
- the ETH rule inside the "definite fail outranks missing" choice.

They also include one new default: **a family that asks too early waits; it does not lose its test** (D20L-45).
- Adopting Q1 uses the provisional cap only until S4 settles D11-15. Adopting Q1 does **not** settle D11-15.
- In plain words, the D20L-36 sentence is this: "if a test finished before day 255 but is posted after it, the post shows its PASS or FAIL, and the pick is still recorded as expired."
- **"Adopt (Recommended)."** Cost: several builds, each needing §16 review. A lost key can cost a good PASS.
- **"Keep blocked."** The lockbox cannot run.

**Q2. How do the runs that feed and make up the lockbox test start and end?**
- **(i) Start:**
  - **"Strategy and benchmark start with no position; each pays its entry cost at its first permitted entry (Recommended)."** This matches the lockbox start you decided. Cost: the entry costs fall inside the measured period.
  - **"Carry positions over from the warm-up."** Cost: the forecast and the lockbox start differently, and D-11's stated reason no longer holds.
- **(ii) End:**
  - **"Use the last hour's own closing price (Recommended)."** No run ever needs data from after its period. Cost: the S4 draft must state this rule. The confirmation-run part must be in the reviewed `screen.py` **before the freeze (step G)**, in the same change as Q5. If the freeze comes first, the confirmation runs cannot end without a forbidden lockbox price, and C2 stays blocked until a formal amendment.
  - **"Read one more price, just after the period."** Cost: it changes your D-11 data permission. The confirmation runs still cannot use it.
- **"Keep blocked."**

**Q3** and **Q4** are unchanged.

**Q5. Which number seeds the chosen strategy's own model fit?** This is time-sensitive (D20L-31, D20L-47).
- **"The protocol's seed, turned into an ordinary number in a fixed way (Recommended)."** It follows your R-13 decision. Cost: a small reviewed `screen.py` change, listed in the freeze review file. The freeze must then be built from the commit that contains it. If the freeze is built first, this option is unavailable on the current route; only a later formal amendment could bring it back.
- **"Seed 0 everywhere."** No code change. Cost: a C2 row overrides part of R-13. The results are unaffected only if the fits truly ignore the seed, which the screen assumes (MR-2) but has not proven.
- **"Keep blocked."**

## 4. Remaining, unauthorised, self-check

**Remaining:**
- the R19-2 re-check of this revision;
- owner Q1-Q5;
- the S4 items: D11-15, D20L-18, D20L-34/48 (the end-price rule), the Annex C l.412-413 wording, and the D20L-36 sentence;
- the C2 rows of revision 3, plus `estimator_seed_policy` and, under `ZERO`, the R-13 override;
- the builds of revision 3, plus `record_pre_read_check` and `L_store`, each under §16 review (Constitution l.147-153).

Revision 3 also listed "the owner confirmation in D20L-36". That item is withdrawn.

**Unauthorised:** frozen edits; activation; acceptance; any code; key generation; simulation; confirmation or lockbox access; promotion; deployment; trading. `KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.

**Self-description check** (done after the last edit):
- one file written, no git command run;
- re-check findings answered: 12 of 12, plus four FIX rows, five notes and errata E-1..E-3;
- new findings D20L-37..50, with no gaps; D20L-36 reclassified;
- five owner questions.
