# D-20 lockbox bindings: proposal, revision 7 (delta on revision 6; the store and residual sections are self-contained)

**Author:** the `senior-statistical-governance` agent. Observed model: Claude Opus 5.5, model ID `claude-opus-5-5` (this session's environment metadata). I am an AI reviewer, not an authority. I propose and check bindings. I cannot decide, accept, activate or amend anything.

**Status: INACTIVE PROPOSAL.** Nothing frozen changed. No row binds until the owner decides and signs the C2 §4 amendment. Revisions 1-6 stay as history.

**How to read it:** this is a **delta on `PROPOSAL_REV6.md`**. Two sections are self-contained and replace revision 6's text whole: **§1.2 (the store)** replaces revision 6's §1.2 (l.72-171), and **§1.3 (the timing residual R5)** replaces revision 6's §1.3 (l.173-185). §1.4 (proposed Constitution §7 wording) is new. Everything else revision 6 left standing (the A-rows, B2, B3, B3a, B4.2-B4.4, B5, B6, the fixture, Q2(i), Q2(ii), Q3-Q5) stays as it was. The consolidated S4 signing text remains an obligation (D20L-59).

**VERDICT: `AMENDMENT_REQUIRED`.**

**Answers** (both read in full): `SOL_REREVIEW5_2CDBF88.md` (gpt-6-sol, FIX, D20LR6-S-1..5) and `ASTRA_REREVIEW5_2CDBF88.md` (gpt-6-astra, FIX, D20LR6-A-1..5; its header l.7 maps the convergence with Sol).

**Owner direction:** simplify rather than patch; prefer deleting mechanism; claim only what is true and testable. Revision 7 deletes the deadline checks on sealed writes and revision 6's mutable on-demand result. It adds one index record (the fixed result), one ordering rule (make durable before use) and one owner question (Q7) for the one rule that cannot be both strict and crash-safe.

**Review status:** revision 7 is unreviewed. R19-2 requires a focused re-check by two model families before any owner decision. No human statistician has reviewed it.

**Checkout and mode:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch `freeze-sheet`. I wrote this one file only and ran **no git command**. No confirmation or lockbox data, network, credentials, keys or simulation were used.

## 0. Verification

**Read this session:** revision 6 in full; revision 5 l.1-75 and l.112-123; revision 4 l.40-60, l.85-112, l.156-200; revision 3 l.176-200, l.228-260, l.280-312; `REREVIEW5_PROMPT.md`; both re-check records; `d12-proposal/PROPOSAL_REV7.md` l.76-131 (actors l.77, step 5 l.84, P-7 l.86-94, P-5 l.96, P-6 l.98, l.113, R1 l.127, R3 l.129) and its §2 (l.53-60); `OWNER_DECISION_D12.md`; Constitution l.68-82, l.145-153, l.185-196; protocol l.73-80; DRAFT_WORDING l.75-95, l.244; `src/aqt/core/ledger.py` l.260-310 and l.340-416.

**Governing text found by searching each topic (both directions):**
- D-12 step 5 (REV7 l.84): "records the read as finished … only while the store clock is before `D_w`. After `D_w` the result is fixed … Late worker output is void, logged sealed, never published." Governs D20L-62.
- D-12 P-7 (l.92): "if no row is committed before `R_j`, the release moves to `R_{j+1}`". Governs D20L-63. P-5 (l.96): reader-path unavailability in `[R_j, decision)` is a §26 incident and moves the earliest decision back by its length. This is the existing rule that D20L-63's Q7 rule relies on. Revision 6 did not cite P-5.
- Constitution §6 l.70, "no silent deletion/correction", and §26 l.191, "append-only/tamper-evident". Together they govern the no-repair stop on a torn index (D20L-64). Revision 6 cited only §26.
- Constitution §7 l.79, "Research receives PASS/FAIL only"; the decided precedent for a §7 row is `OWNER_DECISION_D12.md` l.12 (Q2a) with D-12 REV7 l.57; protocol l.76 `result_to_research: PASS_FAIL_ONLY`. Govern D20L-66 and §1.4.
- D-12 l.94: "A result first released after the cap shows PASS or FAIL and nothing more." This makes post-C release inserts legitimate (D20L-67).

**Code facts (read, not run).** `append_entry` is not one system call. It takes the ledger's sidecar lock, with a 120 s timeout (`LOCK_TIMEOUT_SECONDS`, l.84; l.350). It reads and verifies the whole chain (l.391-397), builds the entry, then writes, flushes and fsyncs (l.411-414). A lock timeout or a damaged chain raises before anything is written. It never fsyncs the ledger's directory, including when `open(…, "ab")` creates the file. `read_entries` takes no lock and raises on a torn tail (l.301-307, l.274-277).

**Exact integer arithmetic.** Run with the main checkout's venv Python, `-I -B`, through a heredoc that wrote nothing. The bare `python` command is a Microsoft Store stub on this machine and did not run; that is a tooling fact, not a check result. Definitions: `r0 = t_s + 604,800`, `d_w = r0 − 43,200`, `D* = min(d_w, C)`. The earliest fixing time is `R_0 − 21,600`.
- **Claim:** `(R_0 − 21,600) − D* ≥ 21,600` for every admitted `t_s < C`. Swept over `t_s` ∈ [C − 700,000, C) in steps of 997, plus edge points. **Minimum = 21,600**, reached at `t_s = C − 648,000` (where `D* = d_w`). At `t_s = C − 1` the slack is 583,199; at `C − 3,600` it is 579,600.
- **Discriminating case (D20LR6-A-1's scenario).** Take `D* = 0`. The first ask is at 21,600, a second at 21,602 and a post-release `state` at 90,000. A PASS finished record has `finished_at = −5` and lands at 21,601.
  - Revision 6 (evaluated on demand) answers **FAIL, PASS, PASS**: the release says FAIL and later `state` says PASS.
  - Revision 7 (fixed at the first ask) answers **FAIL, FAIL, FAIL**.
  - With the landing at 21,599, revision 7 answers **PASS, PASS, PASS**.

  The two treatments therefore differ, and revision 7 never contradicts itself.

**Why "on disk before the deadline" cannot be the rule (analytic).** The moment a write became durable is known only after the write returns. To survive a crash, that moment must be recorded by a second write, whose own completion is again unbounded. After a crash between the two writes, a restart cannot tell an on-time write from a late one. Voiding the ambiguous write would void valid on-time writes, and keeping it would keep late ones. A strict rule can therefore be stated but not enforced crash-consistently. Revision 7 instead uses rules whose deciding facts are durable before anything relies on them, and routes the difference to the owner (Q7), as D20LR6-S-1 allows.

## 1a. Dispositions

| ID | Disposition | Evidence | Repair (where; finding) |
|---|---|---|---|
| **D20LR6-S-2 = D20LR6-A-1** (BLOCKER; mutable result; D20L-61 rejected) | **Accepted. D20L-61 withdrawn.** | Rev 6 l.109-113 evaluates the result on demand, and T-S5 (l.165-168) tests it changing. §0 discriminating case. | §1.2 "fixed result"; T-S5; D20L-62 |
| **D20LR6-S-1** (BLOCKER; deadline vs durable append) | **Accepted in part.** The finished rule is bound to durability. For index appends, the strict rule is shown not crash-consistent (§0), and the different rule is **routed to the owner (Q7)**. | `append_entry` l.391-414; D-12 P-7 l.92 | §1.2 time rules; T-S1, T-S2; Q7; D20L-63 |
| **D20LR6-A-2** (BLOCKER) **~ D20LR6-S-5** (NON-BLOCKING); crash points | **Accepted, at BLOCKER.** Astra's exposure-then-loss scenario holds: rev 6's startup (l.140-143) fsyncs the sealed directory, but not the index. | Ledger l.411-414; rev 6 l.140-145, l.147-156 | §1.2 durable-before-use, crash table, T-S4; D20L-64 |
| **D20LR6-S-3 = D20LR6-A-3** (BLOCKER; availability and R5 overclaim) | **Accepted.** Claims are narrowed to lock independence; resource effects, missed releases and the extended windows are disclosed. | Rev 6 l.163, l.175-183 | §1.2 T-S3; §1.3; Q6; D20L-65 |
| **D20LR6-S-4 = D20LR6-A-4** (QUESTION; §7) | **Accepted as the reviewers' recommendation, not decided.** A scoped §7 exception is drafted as a proposal. Q6 now says that "Accept" means signing it. | Sol l.30; Astra l.70-76 | §1.4; Q6; D20L-66 |
| **D20LR6-A-5** (NON-BLOCKING; commit-point wording) | **Accepted.** | Rev 6 l.107 | §1.2 cap scope; Q1; D20L-67 |
| Sol: D20LR5-S-2 and S-4 ACCEPT WITH NOTES (l.18, l.20) | **Notes applied.** The torn index is a stop, not a durable truth. Q6 now names the missed release. | | crash table; Q6 |
| Sol: the signing hint applies only to a pre-cap PASS (l.30) | **Accepted** | D-12 l.94 | §1.3; Q6 |
| Astra: the read gate verifies the DEFAULT while holding `L_store` (l.64) | **Accepted, disclosed** | | §1.3 |
| Astra: signing and implementation must use the S4 consolidated text (l.31) | **Accepted** | | §4 |
| Rev 6 rows that both reviewers accepted (D20L-59, E6-1, the S4 deferral) | **Unchanged** | Sol l.5, l.34; Astra l.5, l.29-31, l.105 | none |

## 1. Bindings

### 1.1 Replacements outside the store section

**B1 publisher row (replaces revision 6's row, l.62).** This is revision 6's row with one change: `state` and `insert_release` take the result from the fixed-result entry (§1.2), not from an on-demand evaluation. `state`'s answer after a release is `{"fixed": true, "released": true, "result": <the fixed result>, "store_now": t}`, and the release entry carries the same result.

**Worker deadline (replaces revision 5's three bullets, l.45-47).** `D* = min(d_w, C)` stands, and so does the reading of `DEADLINE:NOT_FINISHED_BY_D_W` (rev 5 l.49).
- `write_bundle` has **no time check**.
- `mark_finished` is governed by §1.2's finished rule.
- The effective result is the fixed-result entry.
- The signer guard's "finished … `finished_at < D_w`" bullet (rev 3 l.186) becomes "the fixed-result entry says PASS". Its other bullets are unchanged.

### 1.2 The store (self-contained; replaces revision 6's §1.2)

**Records.** Only these are authoritative.
- **The index:** the append-only ledger. It holds pre-read, rejection, no-read and release entries, and the **fixed-result entry** `aqt.lockbox.fixed.v1` = `{evaluation_id, attempt, result, commitment}`, at most one per evaluation. No reader account ever sees a fixed-result entry. Its result and commitment are repeated, unchanged, by the release entry.
- **Sealed files**, each written once and never replaced (§26):
  - the DEFAULT bundle with its nonce and commitment, under `(evaluation_id, attempt)`;
  - RESULT bundles;
  - at most one finished record per evaluation (`aqt.lockbox.finished.v1` = `{evaluation_id, result, commitment, finished_at}`, rev 3 l.285, with `finished_at` as defined below);
  - the pre-read check record (rev 4 l.117);
  - `lockbox_eval`'s startup records.

  A sealed file is created like this: write a temporary file, fsync it, link it to its final name **without replacing** an existing name, then fsync the directory. Temporary files are never read; reconciliation logs them. All sealed files are kept in one directory.

There is no snapshot, no scheduler and no scheduled step.

**Durable before use (D20L-64).** Every operation that takes `L_store` first fsyncs three things before it reads anything: the index file, the index's directory and the sealed directory. `mark_finished` first fsyncs the RESULT bundle and the sealed directory. An fsync error is a §26 stop.

So no answer, bar, signature, fixed result or release ever rests on bytes or names that a machine crash could still remove. That covers two cases:
- a complete index line written but not fsynced by a crashed process;
- a sealed file linked before its directory fsync.

*Platform assumption:* an fsync makes durable whatever is already written to that file or directory, whichever process wrote it. This is `UNVERIFIED_EXTERNAL_ASSUMPTION` for the chosen OS and filesystem. T-S4's machine-crash rows test it on the target.

**One lock.** `L_store` is the store's own lock file (D20L-46). The store takes it for every index read or append:
- `begin_read`, rejection appends and `insert_release`;
- `state`, reader rows and `guard_state`;
- `verify_replay`, reconciliation and startup;
- the read gate's entitlement check.

Nothing reads the index except through these operations. The worker and the signer never hold `L_store` themselves. No sealed write takes it: not `write_bundle`, not `mark_finished`, not any sealed create.

**Time rules (D20L-63; Q7).**

*(a) Index appends with a deadline:* the appends inside `begin_read` (before C) and `insert_release` (`R_j − 21,600 ≤ t < R_j`, both bounds).
- Holding `L_store`, the store re-reads its clock immediately before calling `append_entry`. If that reading `t1` misses the deadline, nothing is written and the call is refused (`CAP_REACHED` in `begin_read`; a missed release for `insert_release`, P-7).
- Otherwise `append_entry` runs with `L_store` still held. **The append counts as made at `t1`.** Every index reader holds `L_store` and fsyncs first, so no one can read the index between `t1` and the moment the line is durable. Each reader either ran before `t1` or waited and then saw the durable line. No bound on that wait is claimed.
- For `insert_release`, the store reads its clock again (`t2`) after `append_entry` returns. If `t2 ≥ R_j`, it appends a P-5 reader-path outage entry for `[R_j, t2)` before releasing `L_store`. Under P-5 (D-12 l.96) that is a §26 incident and extends cooling-off. Downtime from a crash is counted by P-5's availability log, as before (D-12 T-7).
- *Errors:* a `LedgerError` raised before writing (the lock timeout or a damaged chain) means nothing was written. A timeout is refused; damage is a §26 stop. Any error after the write starts (write, flush or fsync) leaves durability unknown, and is a §26 stop for a human, with no retry and no repair.

*(b) Finishing:* `mark_finished(evaluation_id)`.
1. The store verifies the RESULT bundle against its commitment.
2. It fsyncs the bundle and the sealed directory.
3. **Then** it reads its clock, `t_f`. If `t_f ≥ D*`, the call is refused: the bundle is late output, void, logged by reconciliation and never published.
4. Otherwise the store creates the finished record with `finished_at = t_f`.

Because `t_f` is read after the result is durable, `finished_at < D*` means that the result was on disk before `D*`. The finished record itself may land later. It counts only if it is present when the result is fixed (below); that is Q7's second rule.

*(c) Start checks:* `record_pre_read_check` (deadline C) and each bar response (deadline `D*`). The store reads its clock before starting and refuses at or after the deadline. An operation already started may end after the deadline; no bound is claimed. Neither check carries weight:
- a check record that lands after C admits nothing, because `begin_read` answers `CAP_REACHED` from C on;
- a bar received at or after `D*` cannot be part of a counted result, because any bundle using it becomes durable later, so its `t_f ≥ D*`.

*(d) Cap scope:* from C on, no operation limited by C or `D*` starts: no pre-read check, read authorisation, rejection append, bar or counted finish. **Release inserts are limited by their own window, not by C, and continue after C** (D-12 l.94). Reads, reconciliation and replay also continue. This is how §1.2 reads "at day 255 processing ends" (DRAFT l.244).

**The fixed result (D20L-62).** An evaluation's result is fixed **once**, by the first of `state`, `guard_state` or `insert_release` called at store time `≥ R_0 − 21,600`. Before that time they answer `fixed: false` or refuse. Holding `L_store`, after the fsyncs, the store does the following:
- If a finished record exists for the pre-read entry's attempt, with `finished_at < D*` and a RESULT bundle that verifies against its commitment, it takes that record's `{result, commitment}`. Otherwise it takes the DEFAULT's (FAIL/DEADLINE).
- It appends the fixed-result entry. That append has no deadline, and it is durable before any answer uses it.

From then on, every answer reads that entry:
- `state`'s result;
- `insert_release`'s result and commitment;
- the signer guard's PASS check.

A finished record that appears later is void. Reconciliation logs it, and nothing changes. A result is never computed twice, and `state` can never contradict a release, because both read the same durable entry. The fixing time is at least 21,600 s after `D*` (§0). That is slack, not a bound on how long a sealed write may take.

**How this keeps D-12 step 5 (l.84):**
- "Records … as finished only while the store clock is before `D_w`" is `t_f < D*`, read after the result is durable (Q7 confirms that the record of it may land later).
- "After `D_w` the result is fixed": after `D*` nothing the worker does can change it, and from the fixing time nothing at all can. Between those two times, only the landing of a finish already decided before `D*` matters, and its loss is treated as an unfinished read, exactly as for a crash before finishing.
- "Late worker output is void, logged sealed, never published": refused finishes, records landing after fixing, and bundles with no counted record.

**`begin_read(evaluation_id)`, under `L_store`.** Sample `t_s`, the store clock floored to the second.
1. Fsync (durable before use), then verify the index. Damage stops the process as a §26 incident.
2. Read-only reconciliation, allowed at any time: return an existing pre-read entry, after checking that its DEFAULT verifies (otherwise a §26 stop), or an existing rejection entry. Nothing is written.
3. **Cap:** if `t_s ≥ C`, answer `CAP_REACHED`.
4. **Entitlement,** as revision 4 step 3. A failed check appends a rejection under rule (a).
5. **Budget,** as revision 4 step 4, under rule (a).
6. **Order and cooldown,** as revision 6 step 6 (`DEFERRED`, nothing written).
7. `r0 = t_s + 604,800` and `d_w = r0 − 43,200`. `attempt` = 1 + the highest attempt present. Create the nonce and the DEFAULT bundle (`sealed_at = t_s`). The DEFAULT has no time check of its own; it binds only through step 8.
8. Append `aqt.lockbox.pre_read.v1` exactly as revision 4 step 7 (l.134), under rule (a).

If step 8's re-read is at or after C, the step-7 DEFAULT is a void orphan (rev 3 l.249): no budget is spent, and the answer is `CAP_REACHED`.

A no-read entry's `visible_from` "store second of the insert" (rev 3) is `t1`.

**The read gate.** When `lockbox_eval` opens a read session, the store checks entitlement once, under `L_store` and after the fsyncs. All three must hold:
- the pre-read entry exists;
- its DEFAULT verifies;
- a `PASS` startup record exists for the check record's module hash and image.

Bars are then served without the lock, each under start check (c) against `D*`. After C the gate serves nothing, because `D* ≤ C`.

**Startup.** Before serving or consuming anything, the store does three things under `L_store`:
- the fsyncs;
- index verification;
- revision 3's reconciliation (l.248-250), which also logs temporary files, late finished records and void bundles.

There is nothing to rebuild or replay.

**Crash points (D20L-64).** Process crash (P) and machine crash (M).

| Crash at | After restart | Effect |
|---|---|---|
| DEFAULT linked, before the step-8 append | orphan DEFAULT (M: possibly no DEFAULT) | void; no budget spent; the next call before C uses `attempt + 1` |
| step-8 line written, not fsynced | P: the line is made durable by the next operation's fsync. M: the line is lost, or partial (row 4) | P: the entry counts (made at `t1 < C`). M: as row 1. No one was served from it either way |
| step-8 fsync done, before the reply | entry durable | `begin_read` returns it; after C the gate serves nothing |
| partial last index line | the index is damaged | **§26 stop:** nothing is served or written until a human reconciles it (Constitution §6 l.70, §26 l.191). This is not an automatically usable state |
| sealed create, before the link | a temporary file only | the record is absent; the temp is logged |
| sealed link done, directory not fsynced | P: the name is present. M: the name may vanish | P: every user fsyncs the directory before relying on it, so the record counts as present. M: absent; nothing had used it |
| inside `mark_finished`, before the finished record's link | no finished record | the worker may retry; a fresh `t_f` is read, and the retry is refused from `D*` |
| fixed-result entry written, before or after its fsync | as rows 2-3 | durable: every later call reads it. Lost: it is fixed afresh at the next ask. No one had an answer from it |
| release append crossing `R_j`, or a crash during it | P: the row counts after the fsync (made at `t1 < R_j`). M: lost or partial | P: readers waited or the store was down, which is a P-5 outage. M lost: a missed release (P-7 l.92), retried at `R_{j+1}` |
| `append_entry` I/O error after the write starts | durability unknown | §26 stop |
| restart after C, with an entry made before C | entry durable | gate serves nothing; `mark_finished` is refused; at the first ask the fixed result is DEFAULT, unless a counted finished record already exists |
| restart after the result was fixed or released, with a finished record now present | the fixed-result entry, and the release if any | the record is void and logged; nothing changes |

Apart from the two §26 stops, every row leaves one set of durable records, which every operation reads directly.

**Pre-read reason codes:** revision 2's list without `COOLDOWN_NOT_ELAPSED` (rev 4 l.145).

**Tests.** These are revision 3's list (l.253-257) and revision 4's list (l.147-155), with revision 6's cooldown boundary and revision 5's cap-order test (l.114). Revision 5's reconciliation-after-C and worker-deadline tests (l.115-116) are **replaced** by T-S2 and T-S4, because `write_bundle` no longer has a deadline. Clock and fault injection are used throughout.
- **T-S1, index appends crossing a deadline** (every `begin_read` append against C; `insert_release` against both window bounds).
  - A re-read at the deadline is refused, and nothing is written.
  - With a re-read at deadline − 1, the clock is advanced past the deadline at each point inside `append_entry`: waiting for its lock, after verification, between write and flush, between flush and fsync, and after the fsync. In every case the entry counts. Each concurrent `state`, reader-row, `guard_state` and `begin_read` call returns only after the append and shows the entry. For a release with `t2 ≥ R_j`, the outage entry is logged.
  - An injected error in write, flush or fsync gives a §26 stop, with nothing served.
- **T-S2, finishing and start checks,** for `D* = d_w` and for `D* = C`.
  - `t_f = D* − 1` counts; `t_f = D*` is refused.
  - A crossing between the bundle's fsync and the `t_f` read is refused.
  - A crossing between `t_f` and the link, or between the link and the directory fsync, counts if the record is present at fixing.
  - `write_bundle` after `D*` is accepted as bytes and never counts.
  - Bars: one checked at `D* − 1` is served; one at `D*` is refused. A bar whose send completes after `D*` (delay injected between the clock read and the send), followed by `write_bundle` and `mark_finished`, is refused.
  - `record_pre_read_check` at `C − 1` is accepted and at C is refused. A crossing during its create still gives `CAP_REACHED` from C on.
- **T-S3, lock independence only.** An instrumented `L_store` raises if `write_bundle`, `mark_finished` or any sealed create acquires it. Two runs: a sealed create stalled at the function level (no disk load), and a crashed worker. In both, `state` at `R_0 − 21,600` returns the fixed result and `insert_release` succeeds in its window. **This does not test or claim availability under disk or CPU contention** (§1.3).
- **T-S4, crash points.** One test per row of the crash table, each under a process crash and under a machine crash, including a restart after C and one after fixing. Machine crashes use a test file layer that discards everything not fsynced, file data and directory entries separately. If the build cannot provide that layer, the machine-crash rows are **not available**, which blocks completion. They are not N/A.
- **T-S5, fixed result.** A finished PASS with `t_f < D*` whose link stalls (injected):
  - landing before the first ask: every answer is PASS;
  - landing one second after fixing: `state` before and after the landing, `guard_state`, `insert_release`, and `state` after the release all give the fixed FAIL, the record is logged void, and the release's result equals the fixed entry's;
  - a crash after the fixed-result append and before the reply: later calls read the entry.
- **T-S6, payload shape:** unchanged from revision 6 (l.169).

None of these tests measures timing. No timing or latency property is claimed.

### 1.3 The timing residual R5 (self-contained; replaces revision 6's §1.3)

**What is separated, and nothing more.**
- No sealed write takes a lock. The worker and the signer never hold `L_store` themselves.
- The store holds `L_store` for them briefly, in two places: once per read session for the gate check (which verifies the DEFAULT and runs the fsyncs), and for each `guard_state`.
- The result is fixed at a time set by the publisher's calls, not by sealed work, and from facts decided before `D*`.
- The release time is `R_j`. Every FAIL answer has the same bytes and shape (T-S6).

**Resource assumptions: none.** Public calls and sealed work share one machine: CPU, memory and disk, including the filesystem journal that every fsync uses. Sealed work can therefore slow any public call, with no bound.

**What can leak or happen.** This applies to anyone who can call the store or watch its behaviour: the publisher, and the reader account (the owner and, through the owner, research, D-12's working rule).
1. **During a read**, from `t_s` until the worker process stops: whether the worker is running, stopped early or restarted, and roughly when it finished. This hints at a technical breakdown versus a run to the end. I have **not** shown that it cannot also hint at **PASS versus performance FAIL**: compute paths differ slightly by outcome (for example, `upside` is computed only for a finite `T_L`).
2. **After `D*`:** sealed activity can continue. A worker can compute until it is refused, late writes are void but still use the disk, and a stalled finished record can land after `D*`, into the release window or after the release. The windows are therefore not limited to `[t_s, D*]`.
3. **In the release window** `[R_j − 6 h, R_j)`: the signer is asked only for a **PASS with `R_j < C`**, so its activity can reveal such a PASS up to six hours early.
4. **Missed releases:** sealed activity can slow `insert_release` past `R_j`. That is a missed release (P-7: incident, a one-day delay, possibly repeated). Near day 255 it can make a finished PASS expire `U_ops` (P-6). A slip is visible, and because sealed activity differs by outcome (a PASS adds signing work), it can correlate with the result. A slow machine can also make a worker miss `D*` (a deadline FAIL), as any worker slowness can.

**How much:** not measured, and no bound is claimed.

**What it cannot do:** change a result once fixed, or a counted try. *Corrected from revision 6 l.183:* it **can** move a release by whole days, and near day 255 it can cause an expiry.

**Compared with D-12's R1-R4:** R1 needs a signing fault and hints only at a PASS. R5 needs no fault and can hint at FAIL kind, possibly at PASS versus performance FAIL, and at outcomes through missed releases. The owner's acceptance of R1-R4 (`OWNER_DECISION_D12.md` l.31) does not cover it. Both reviewers recommend an explicit Constitution §7 exception if the owner accepts R5 (§1.4, Q6).

### 1.4 Proposed Constitution §7 row (proposal only; no frozen file is edited)

This row would be carried in C2's Constitution table (DRAFT §1, l.75-95) **only if the owner chooses "Accept" in Q6**. It needs the S4 drafting and the required human review. The first sentence is the row already required by the owner's D-12 Q2a decision (D-12 REV7 l.57; `OWNER_DECISION_D12.md` l.12). The second is new.

| Ref | Current v1.0 text | Proposed v1.1 text |
|---|---|---|
| §7 l.79 | "Research receives PASS/FAIL only." | "Research receives PASS/FAIL only, except that the cycle outcome of §5 may show that a family had no result because its lockbox read failed technically. How quickly the lockbox service answers, and a lockbox release or expiry that comes late because the service was slow or unavailable, are not results under this rule, even where they allow a guess about a result; this exception covers only such timing and delay effects of the lockbox service specified in the protocol, allows no added field, message, log entry or diagnostic, and no component may vary its timing to convey a result." |

**Matching protocol wording (optional; for S4 to decide):** protocol l.76 keeps `value: "PASS_FAIL_ONLY"`. Its justification would become "Prevents tuning feedback. Timing and delay effects of the lockbox service are governed by Constitution §7." The rule's last clause, "no component may vary its timing", is checkable by §16 code review, not by a test. Like Q2a's row, the exception would apply to later cycles until amended.

## 2. Findings

**Changes to earlier findings:**
- **D20L-56** is superseded by D20L-63. The re-read stays only for index appends. Sealed-create deadlines are deleted. Revision 6's "within the one system call and fsync" (l.107) is withdrawn.
- **D20L-57** is qualified by D20L-64. A torn index is a §26 stop, not a durable truth.
- **D20L-58** is corrected by D20L-65. Availability is claimed only as lock independence.
- **D20L-60** is answered, as a proposal, by D20L-66.
- **D20L-61 is withdrawn.** Both reviewers rejected it. It described a mutable result as an R3 residual. D20L-62 replaces it.

**New findings:**
- **D20L-62 BLOCKER (repaired; §1.2 fixed result, T-S5).** Revision 6's on-demand result could change between the first answer and the release, and after a release `state` could contradict it. The result is now fixed once, durably, at least 21,600 s after `D*`, and every later answer reads it. (D20LR6-S-2 = D20LR6-A-1.)
- **D20L-63 BLOCKER (repaired where it can be checked; the rest is routed to the owner, Q7).** The finished rule reads the clock after the result is durable. Index appends count at the re-read made under `L_store`, which is sound only because every reader holds `L_store` and fsyncs first. A crossing at `R_j` is logged as a P-5 outage. The strict rule cannot be made crash-safe (§0). T-S1 and T-S2 inject crossings inside `append_entry`, during sealing, and between a bar's clock read and its send. Revision 5's tests at l.115-116 are replaced. (D20LR6-S-1; part of D20LR6-A-5.)
- **D20L-64 BLOCKER (repaired; durable before use, crash table, T-S4).** An index line or sealed name could be used before it was durable, then lost. The index was never fsynced before use after a crash. That omission is **inherited**: revision 3's B4.1 (l.236-250) introduced it, and revisions 4-6 carried it; revision 6's startup (l.140-143) fsynced only the sealed directory. (D20LR6-A-2 ~ D20LR6-S-5.)
- **D20L-65 BLOCKER (repaired by narrowing the claims; §1.3, T-S3, Q6).** Revision 6 claimed availability "in every case" (l.163) and that R5 cannot move a release time (l.183). Neither holds on a shared machine. (D20LR6-S-3 = D20LR6-A-3.)
- **D20L-66 QUESTION (owner Q6; S4; human review).** The §7 exception wording is drafted (§1.4). The AI does not decide whether it is needed or acceptable. (D20LR6-S-4 = D20LR6-A-4.)
- **D20L-67 NON-BLOCKING (applied).** The cap statement is scoped to C- and `D*`-limited operations, post-C release inserts are kept, `append_entry` is described accurately, and no latency bound is implied. (D20LR6-A-5.)

## 3. Owner questions (Q1 and Q6 replaced, Q7 new; Q2(i), Q2(ii), Q3, Q4 and Q5 as in revision 5; each has "Keep blocked")

**Q1. Adopt the detail rows and the new defaults?**

*In short:* this adopts the AI-drafted rule book for running, sealing and posting the lockbox test. With it, the builds can start, each needing §16 review. Without it, the lockbox cannot run.

What changed since revision 6, in plain terms:
- **Work stops at day 255.** A test still running then is posted as a technical fail, and the pick expires unpromoted. A test started shortly before day 255 **may fail this way if too little time remains**. Nothing new starts at or after day 255, except the posting of results, which continues. A step already under way may finish after day 255, and no time limit is claimed for that.
- **A result is locked the first time the posting job or the signer asks** (at the earliest, six hours before its posting time). After that nothing can change it.
- **Before every action, the service makes sure its records are safely on disk.** A damaged log stops everything until a person sorts it out.
- The posting job learns a result six hours before its posting time, as in revision 6.
- No timing protection is claimed (Q6). When a save counts as made in time is your choice in Q7.

The list is revision 6's Q1 list, plus the fixed-result entry, the durable-before-use rule, the time rules (Q7) and the narrowed tests T-S1..T-S6. Adopting Q1 does **not** settle D11-15. The D20L-36 sentence (revision 4 Q1) stands.
- **"Adopt (Recommended)."** Cost: several builds, each needing §16 review. A lost key can cost a good PASS.
- **"Keep blocked."**

**Q6. May the lockbox service's speed and delays give hints?** (replaced)

*In short:* the hidden test and the parts that answer you and the posting job run on one computer and share its disk. How fast they answer, and whether a posting comes on time, can depend on the hidden work. Someone timing the service closely (you, or the research AI working with you) might guess, before a result is posted:
- that a test broke down or stopped early rather than running to the end, and roughly when it finished;
- possibly even whether it **passed or failed on performance**. Nobody has shown that it cannot;
- in the six hours before a posting, that a PASS is coming, because only a PASS posted before day 255 gets signed;
- something about the result, from a posting that **slips by a day** because the computer was overloaded. A slip is logged. Near day 255 it can make a PASS expire unpromoted.

These hints cannot change a locked result or a counted try. Nobody has measured how clear they are; earlier drafts tried to hide them and failed, so this draft claims nothing.

The Constitution says research receives PASS/FAIL only. Both reviewers advise that allowing these hints needs **a written exception to that rule**, which you would sign in C2 after a person reviews it. Like your Q2a exception, it would also apply to later cycles until changed. The proposed words are in §1.4.
- **"Accept: sign the timing exception in C2 (Recommended)."** Cost: the hints above, allowed in writing.
- **"Keep blocked."** The lockbox cannot run until someone designs and tests stronger separation, for example separate machines. This draft does not propose that.

**Q7. When does a save count as made in time?** (new)

*In short:* saving to disk takes a moment that nobody can bound, so the rules must say at which instant a save "happened". The draft uses two rules:
- **Log entries** (starting a test, posting a result): the save counts at the moment the service checks its clock while it blocks everyone else from reading its log. Nobody can read the log until the save is safely on disk, so everyone sees it as made at that check. If the disk finishes after the posting time, anyone who tried to read in that gap simply waited. The wait is logged as downtime and extends your 72 hours, as you already decided for outages.
- **A finished test** counts if its sealed result was safely on disk before the worker deadline; the service checks the clock only after the disk confirms. The short note saying so may land later, but it must be on disk when the result is locked, at least six hours after the deadline. If it is still missing then, the test counts as a technical fail, permanently, as if the worker had crashed before finishing.

The stricter rule, "fully on disk before the deadline", cannot be checked after a crash: the moment a save reached the disk can only be recorded by another save, which could itself be lost.
- **"Accept these two rules (Recommended)."** Cost: a posting can count even though its save finished after the posting time (readers wait; this is logged as downtime). A finished test whose note is held up for six hours or more counts as a technical fail.
- **"Keep blocked."**

## 4. Remaining, unauthorised, errata, self-check

**Remaining:**
- the R19-2 re-check of this revision;
- owner Q1-Q7;
- the S4 items of revision 4, plus D20L-66 and the §1.4 row if Q6 is accepted;
- the single consolidated S4 signing text (an obligation), which signing and implementation must both use;
- the C2 rows of revision 4;
- the builds: revision 4's builds plus the fixed-result entry, the durable-before-use rule, the time rules and tests T-S1..T-S6 with a machine-crash test file layer, each under §16 review (Constitution l.147-153; lockbox ACL tooling, l.152).

**Unauthorised:** frozen edits; activation; acceptance; any code; key generation; simulation; confirmation or lockbox access; promotion; deployment; trading. `KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.

**Errata noticed, not applied** (history and committed records are not edited):
- **E7-1** (rev 6 l.160): "revision 3's list (l.253-258)". The list is l.253-257; l.258 is blank. Cosmetic. §1.2 here cites l.253-257.
- **E7-2** (Sol record l.24): the D-12 P-7 link points at `PROPOSAL_REV7.md:87`, which is the `R_j` definition. The "not committed before `R_j`" clause is l.92. The finding stands.
- **E7-3** (rev 6 l.107 and l.183): misstatements, superseded here by D20L-67 and D20L-65 rather than edited.

**Self-description check** (done after the last edit):
- one file written, no git command run;
- re-check findings answered: 10 IDs (D20LR6-S-1..5, D20LR6-A-1..5), forming 6 distinct issues, plus 5 notes;
- new findings D20L-62..67, with no gaps; D20L-61 withdrawn;
- owner questions: Q1 and Q6 replaced, Q7 new;
- mechanisms deleted: the deadline checks on `write_bundle` and on sealed links, and the on-demand mutable effective result;
- mechanisms added: the fixed-result index entry, the durable-before-use fsyncs, the post-append `t2` outage entry, `t_f`-after-durability, and a test-only machine-crash file layer.
