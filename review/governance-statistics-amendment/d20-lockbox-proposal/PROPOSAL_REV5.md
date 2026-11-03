# D-20 lockbox bindings: proposal, revision 5 (delta on revision 4)

**Author:** the `senior-statistical-governance` agent. Observed model: Claude Opus 5.5, model ID `claude-opus-5-5` (this session's environment metadata). I am an AI reviewer, not an authority. I propose and check bindings; I cannot decide, accept, activate or amend anything.

**Status: INACTIVE PROPOSAL.** Nothing frozen changed. No row binds until the owner decides and signs the C2 §4 amendment. This is a **delta**: `PROPOSAL_REV4.md` (itself a delta on revisions 3 and 2) stands except where a section below says "replaces". Revisions 1-4 stay as history.

**VERDICT: `AMENDMENT_REQUIRED`.**

**Answers** (both read in full): `SOL_REREVIEW3_DF28EE6.md` (gpt-6-sol, FIX, D20LR4-S-1..3) and `ASTRA_REREVIEW3_DF28EE6.md` (gpt-6-astra, FIX, D20LR4-A-1..2), plus the author errata E4-1..E4-3 in `REREVIEW3_PROMPT.md` l.13.

**Review status:** revision 5 is unreviewed. R19-2 requires a focused re-check by two model families before any owner decision. No human statistician has reviewed it.

**Checkout and mode:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch `freeze-sheet`. I wrote this one file only and ran **no git command**. No confirmation or lockbox data, network, credentials, keys or simulation were used.

## 0. Verification

**Read this session:** revision 4 in full; revision 3 l.176-222, l.280-312, l.353-397; both re-check records; `REREVIEW3_PROMPT.md`; `d12-proposal/PROPOSAL_REV7.md` l.78-100 (D-12 steps 1-5, P-7, P-5, P-6); DRAFT_WORDING l.243; `event_contract.py` l.148-158; `costs.py` l.245-259.

**Checks (read, not run):**
1. **E4-2.** `event_contract.py` l.151-155 computes `sigma` through `hourly_log_returns_bps` only when `sigma_bps is None`. That function raises `CostModelError` for any series whose interval is not one hour (`costs.py` l.252-254). Astra ran both paths (report l.109). I did not re-run them.
2. **E4-1.** Revision 4 §1a has eight note rows (l.59-62 and l.65-68), not five; l.63-64 are errata rows.
3. **Rev 4's B4.3 line** (l.175) replaced revision 3's whole release-entry line (rev 3 l.306), which carried "`attestation` is non-null iff `result = PASS` and `R_j < C`". Revision 4 did not restate that rule, and its B1 row (l.92) enforces only one direction. D20L-51 is therefore introduced by revision 4, not inherited.

**Exact boundary arithmetic (integer seconds, by hand):** `r0 = t_s + 604,800`, `d_w = r0 − 43,200`, so `R_0 − 21,600 = d_w + 21,600`. Worked example for D20L-52: `t_s = C − 3,600` gives `r0 = C + 601,200`, `d_w = C + 558,000`, and `D* = min(d_w, C) = C`. The worker has 3,600 s, not 7 days. A read starting at or after C is refused, so `D* > t_s` always holds for an admitted read.

## 1a. Dispositions

| ID | Disposition | Evidence | Repair (where; finding) |
|---|---|---|---|
| **D20LR4-S-1** = E4-3 (null attestation on a pre-cap PASS) | **Accepted** | P-7 l.90: a PASS is inserted only "referencing" a validated attestation; a signer refusal is a missed release, "never" an unsigned row. Rev 4's `insert_release` (l.92) refused a wrong attestation but not a missing one. | B1, B3a, B4.3; D20L-51 |
| **D20LR4-S-2** and **D20LR4-A-2** (cap does not end processing) | **Accepted** (they converge) | P-6 l.99: "At day 255 processing ends." Rev 4 step 2 returned an existing entry, and steps 3-4 could write a rejection, all before the cap check at step 5 (l.121-130). The read gate (l.136-139) and worker completion had no time limit except `d_w`, which can exceed C. | B4.1 order, read gate, worker writes; D20L-52 |
| **D20LR4-A-1** (shared lock is a timing channel) | **Accepted** | Rev 4 l.115 put `state` and `begin_read` under the same lock as `write_bundle` and `mark_finished`. Lock waits then reveal sealed write activity, even with a constant payload. Introduced by rev 4's D20L-46 repair. | B4.1 locks, public snapshot, fixed schedule, B1 `state`; D20L-53 |
| **D20LR4-S-3** = E4-1, E4-2 | **Accepted** | Checks 1-2. | §2 below; D20L-54 |
| Astra: Q5 "No code change" wording | **Accepted** | Q2(ii)'s adapter must still go into the frozen object (D20L-48). | Q5; D20L-55 |
| Sol: Q1 and Q4 need owner-facing summaries | **Accepted** | | Q1, Q4; D20L-55 |
| Sol: `DEFERRED {earliest}` is derivable | **Accepted, deleted** | `earliest` is derivable from the other family's public `r0′` (Sol l.38). Nothing consumes it. | B4.1 step 5; D20L-55 |
| Sol: `CAP_REACHED` as the uniform answer at C | **Accepted** | It follows from D20L-52's order. | D20L-52 |
| Astra: R-14 permits another eligible later-object file for the Q2(ii) adapter | **Accepted, wording** | Astra report l.67. | Q2(ii); D20L-55 |
| Astra: consolidate the effective bindings into one document | **Declined for now** | This revision is to change only what the findings require. A consolidated text is better made once, for the S4 draft after the owner's answers. Nothing is lost by waiting. | none |
| All other rev 4 rows | ACCEPT by both reviewers (Sol l.17-24; Astra l.32-53), except the rows above | | none |

## 1. Bindings (replacements)

**Worker deadline, adds to D-12 step 5 as bound by revision 3 (D20L-52) [DERIVED from P-6 l.99].** `D* = min(d_w, C)`. Every worker-side time check uses `D*` in place of `d_w`:
- `write_bundle` and `mark_finished` are refused at `store_now ≥ D*`;
- the effective commitment is the finished record's iff `finished_at < D*`, else the DEFAULT's;
- the signer guard's "finished … with `finished_at < D_w`" becomes `< D*`.

The DEFAULT's reason code `DEADLINE:NOT_FINISHED_BY_D_W` is read as "not finished by the worker deadline `D*`". Consequence: a read cut off by C is published as FAIL/DEADLINE, which is "failed technically" under D-12 Q2a, and the nominee expires `U_ops` (P-6). Letting authorised work continue after C would need an explicit owner/S4 exception through §4. It is **not** a default here and not proposed.

**B1 publisher row, replaces revision 4's row (D20L-51, D20L-53).**

| Role | Allowed store operations | Never |
|---|---|---|
| publisher | `begin_read` (B4.1). `insert_release(evaluation_id, j, attestation \| null)`: the store fills `result` and the effective commitment from the public snapshot. It requires a non-null attestation **iff** the effective result is PASS and `R_j < C`, and refuses every other combination. A required attestation must verify under the C2 public key, and must name this evaluation ID and `cooling_off_start = R_j`. `state(evaluation_id)`: `{"fixed": false, "store_now": t}` while `t < R_0 − 21,600`; from then on `{"fixed": true, "released": bool, "result": "PASS" \| "FAIL", "store_now": t}`. Every answer is given on the fixed schedule (B4.1). | commitments, nonces, sealed bundles, cause classes, finished-record presence or time, lockbox bars, any sealed-side lock |

`state`'s boundary moves from `d_w` to `R_0 − 21,600 = d_w + 21,600`, which is when the publisher's first window opens (rev 4 l.50). The publisher needs nothing earlier. The six hours absorb the fix step's wait for in-flight sealed writes (B4.1). Without them, an early `fixed: false` after `d_w` would reveal that a worker was finishing near its deadline.

**B3a comparisons, replaces revision 4's "Attestation" and "PASS released with `R_j ≥ C`" rows (D20L-51).**

| Action | Valid iff |
|---|---|
| Release insert with an attestation | effective result PASS; `R_j < C`; attestation verifies, with this evaluation ID and `cooling_off_start = R_j`; plus the insert row's conditions |
| Release insert with `attestation: null` | effective result FAIL, or `R_j ≥ C`; plus the insert row's conditions |

A PASS with `R_j < C` and no valid attestation inserts nothing. This is a missed release (P-7 l.90, l.92).

**Added tests:**
- PASS, `R_j = C − 86,400`, null: refused, nothing inserted;
- PASS, `R_j ≥ C`, with an attestation: refused;
- FAIL with an attestation: refused;
- an attestation with a bad signature, another evaluation ID, or `cooling_off_start ≠ R_j`: refused.

**B4.3 release entry, adds to revision 4's line:** "`attestation` is non-null iff `result = PASS` and `R_j < C`; the store enforces both directions at insert" (revision 3 l.306, restored).

**B4.1, replaces revision 4's "store lock" paragraph, steps 2-5, read gate and test list additions (D20L-52, D20L-53, D20L-55). Steps 1, 6 and 7 and the pre-read check record stand.**

*Two locks, never held together.*
- **`L_store`** (public side) is held by `begin_read`, `insert_release`, no-read inserts, `record_pre_read_check`, snapshot writes, `verify_replay` and reconciliation.
- **`L_seal`** (sealed side) is held by `write_bundle`, `mark_finished`, `guard_state`, the read gate and the fix step.
- No operation holds both, so neither lock nests. Each is on its own lock file, distinct from the ledger's sidecar lock (D20L-46 stands).
- Public operations never wait on sealed work.

*Public snapshot `P`.* After every index append, and after each fix step, the store writes `P` under `L_store` and replaces it atomically (write a temporary file, fsync, rename, fsync the directory). `P` holds:
- the index entries;
- for each evaluation, the fixed `{result, commitment}` once its fix step has run.

`state`, readers' visible rows, `insert_release`'s result and commitment, and the read gate's pre-read entry check are all read from `P`. `P` only ever contains durable entries, so the read gate cannot see a partial or unsynced line. This replaces rev 4's "read gate under `L_store`" as the D20L-46 repair.

*Fix step.* At `D*` the store's scheduler does three things:
1. under `L_seal`, reads the finished record if `finished_at < D*`, otherwise the DEFAULT;
2. releases `L_seal`;
3. writes `{result, commitment}` into `P` under `L_store`.

If this has not happened by `R_0 − 21,600`, that is a §26 incident. `state` then stays `fixed: false`, which gives a missed release, never a changed result.

*Fixed response schedule.* Every answer to the publisher or a reader, including `DEFERRED`, `CAP_REACHED`, refusals and errors, is released exactly `Δ` after the store received the request, by the store's monotonic clock. `Δ` is a store constant fixed in configuration and set above the measured worst-case public operation time under load [NEW DEFAULT; value set at build qualification]. An operation still running at `Δ` answers when it finishes and logs a §26 incident.

*`begin_read(evaluation_id)`*, under `L_store`. First sample `t_s` = the store clock floored to the second; it is used for both the cap check and `r0`.
1. Verify the index (unchanged).
2. **Read-only reconciliation**, allowed at any time, including after C. If a pre-read entry exists, check that its default verifies (otherwise a §26 incident, stop), and return the entry unchanged. If a rejection entry for this nominee exists, return it unchanged. Nothing is written.
3. **Cap:** if `t_s ≥ C`, answer `CAP_REACHED` and write nothing. This precedes every admission or rejection write.
4. Entitlement, as rev 4 step 3.
5. Budget, as rev 4 step 4.
6. Order and cooldown, as rev 4 step 5, without the cap bullet. The cooldown answer is `DEFERRED`, with no `earliest` field.

Rev 4's steps 6-7 follow, renumbered 7-8.

`record_pre_read_check` is also refused at `store_now ≥ C`.

*The read gate*, under `L_seal`, serves bars over `[S_pre, L1)` only to `lockbox_eval`, and only while `store_now < D*`. Rev 4's three conditions also apply, with the pre-read entry read from `P`. At `D*` it stops serving mid-stream. No bar is served after C. This holds for an entry made before C and reconciled after it.

*Added tests:*
- **cap order:** at `t_s = C`, a failed check, an exhausted budget and a fresh request each give `CAP_REACHED`, and nothing is written. At `C − 1` they behave as in rev 4.
- **reconciliation after C:** an entry made at `C − 1`, then a crash, then `begin_read` at `C + 1` returns the entry unchanged. The gate serves no bar, `write_bundle` and `mark_finished` are refused, and the release later shows FAIL/DEADLINE.
- **worker deadline:** `write_bundle` and `mark_finished` at `D* − 1` (accepted) and at `D*` (refused), for both `D* = d_w` and `D* = C`. Bars at `D* − 1` (served) and at `D*` (refused).
- **contention:**
  - Hold `L_seal` indefinitely, and separately run a worker loop doing `write_bundle`/`mark_finished` with fsync. Meanwhile issue every public operation and every answer kind at least 1,000 times in total: `state` before and after the fix, an entry, `DEFERRED`, `CAP_REACHED`, a rejection, an accepted and a refused `insert_release`, and reader rows.
  - Every latency must lie in `[Δ, Δ + ε]` (`ε` = the test timer's resolution). The bytes must equal an idle run's.
  - Run the same with a worker that finishes and one that crashes before finishing. The two must be indistinguishable by this band.
  - An instrumented `L_seal` raises if any public operation acquires it.
  - An injected public operation slower than `Δ` logs an incident.

## 2. Findings

**Changes to revision 4 text (E4-1, E4-2):**
- **§4:** "five notes" becomes "eight note rows".
- **§0, code facts:** "checks the interval only through the default volatility path (l.152-156); `sigma_bps` bypasses that check" becomes "checks the interval only through its default volatility path (`event_contract.py` l.151-156), which refuses a two-hour series with `CostModelError` (`costs.py` l.252-254); a supplied `sigma_bps` bypasses that path". The A6 guard is unchanged.

**Changes to earlier findings:**
- **D20L-46:** repaired by the public snapshot, not by `L_store` (D20L-53).
- **D20L-50:** it was a partial repair. D20L-52 completes it.

**New findings:**
- **D20L-51 BLOCKER (repaired, B1, B3a, B4.3).** `insert_release` accepted a null attestation for a PASS with `R_j < C`, which would publish an uncertified PASS. Introduced by revision 4 (check 3). (D20LR4-S-1, E4-3.)
- **D20L-52 BLOCKER (repaired, B4.1, worker deadline).** The cap guarded only new reservations. Reconciliation and rejection writes came before it, and bars and worker completion could run after C, against P-6's "processing ends". (D20LR4-S-2, D20LR4-A-2.)
  - *Not repaired, by choice:* the store still admits a read whose `D*` leaves the worker too little time. Such a read is published FAIL/DEADLINE (worked example in §0). A cutoff would be a new choice, which revision 4 declined (D20L-50) and Astra advised against (report l.24).
- **D20L-53 BLOCKER (repaired, B4.1, B1).** The shared lock let public answer timing reveal sealed write and finish activity. Repaired by splitting the locks, answering from a public snapshot, and a fixed answer delay `Δ`, with a contention test. (D20LR4-A-1.)
  - *Residual:* shared disk and CPU can still delay an answer past `Δ`. That case is logged as an incident, not hidden.
- **D20L-54 NON-BLOCKING (applied).** Errata E4-1 and E4-2. (D20LR4-S-3.)
- **D20L-55 NON-BLOCKING (applied).** Owner wording (Q1, Q4 and Q5 summaries; Q2(ii) placement), and the deletion of `DEFERRED {earliest}`. (Sol and Astra notes.)

## 3. Owner questions (replace revision 4's Q1, Q2(ii), Q4 and Q5; Q2(i) and Q3 unchanged; each has "Keep blocked")

**Q1. Adopt the detail rows and the new defaults?**

*In short:* this adopts the AI-drafted rule book for running, sealing and posting the lockbox test. With it, the builds can start, each needing §16 review. Without it, the lockbox cannot run.

Two rules added in this revision matter to you:
- **Work stops at day 255.** A test still running then is posted as a technical fail, and the pick expires unpromoted. This follows from the day-255 rule you decided. A test started shortly before day 255 will usually end this way, and its one try is spent.
- **Public answers come at a fixed delay.** This stops the timing of an answer from hinting at a result.

The list is revision 4's Q1 list, plus:
- the worker deadline `D*`;
- the two-lock store with the public snapshot;
- the fixed answer delay `Δ`.

Adopting Q1 does **not** settle D11-15. The D20L-36 sentence (rev 4 Q1) stands.
- **"Adopt (Recommended)."** Cost: several builds, each needing §16 review. A lost key can cost a good PASS.
- **"Keep blocked."**

**Q2(ii)**, as revision 4, except that "in the reviewed `screen.py`" becomes "in the reviewed `screen.py`, or another file that R-14 allows in the frozen object".

**Q4. Where does the lockbox code live?**

*In short:* the frozen rules say evaluation code must be inside the frozen engine. The lockbox checker comes later, so either it gets a narrow written exception, or part of it goes into the engine before the freeze. Both need the exception for the lockbox service.
- **"One separate reviewed lockbox module, its fingerprint in the signed C2, with a narrow R-14 exception (Recommended)."** Cost: one amendment row, and the build and review must be done before you sign C2.
- **"The forecast code inside `screen.py` before the freeze."** Cost: the freeze waits for it, and the exception is still needed.
- **"Keep blocked."**

**Q5**, as revision 4, except that the second option's "No code change" becomes "No estimator-seed change; Q2(ii)'s confirmation adapter is still required."

## 4. Remaining, unauthorised, self-check

**Remaining:**
- the R19-2 re-check of this revision;
- owner Q1-Q5;
- the S4 items of revision 4;
- the C2 rows of revision 4;
- the builds of revision 4, plus `L_seal`, the snapshot, the fix step and the fixed schedule, each under §16 review (Constitution l.147-153).

**Unauthorised:** frozen edits; activation; acceptance; any code; key generation; simulation; confirmation or lockbox access; promotion; deployment; trading. `KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.

**Self-description check** (done after the last edit):
- one file written, no git command run;
- re-check findings answered: 5 of 5 (D20LR4-S-1..3, A-1..2), plus errata E4-1..E4-3 and six note rows;
- new findings D20L-51..55, with no gaps;
- no new owner question; Q1, Q2(ii), Q4 and Q5 are re-worded.
