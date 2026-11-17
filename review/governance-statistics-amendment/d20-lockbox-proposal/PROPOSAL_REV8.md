# D-20 lockbox bindings: proposal, revision 8 (delta on revision 7; §1.2, §1.3 and §1.4 are self-contained)

**Author:** the `senior-statistical-governance` agent. Observed model: Claude Opus 5.5, model ID `claude-opus-5-5` (this session's environment metadata). I am an AI reviewer, not an authority. I propose and check bindings. I cannot decide, accept, activate or amend anything.

**Status: INACTIVE PROPOSAL.** Nothing frozen changed. No row binds until the owner decides and signs the C2 §4 amendment. Revisions 1-7 stay as history.

**How to read it:** this is a **delta on `PROPOSAL_REV7.md`**, not a self-contained proposal. Three sections are self-contained and replace revision 7's text whole: **§1.2 (the store)** replaces rev 7 §1.2 (l.71-209), **§1.3 (R5)** replaces rev 7 §1.3 (l.211-231), and **§1.4 (§7 row)** replaces rev 7 §1.4 (l.233-241). §1.1 replaces rev 7 §1.1 (l.61-69). Q1, Q6 and Q7 replace rev 7's. Everything else rev 7 left standing (the A-rows, B2, B3, B3a, B4.2-B4.4, B5, B6, the fixture, Q2(i), Q2(ii), Q3-Q5) stays. The consolidated S4 signing text remains an obligation (D20L-59).

**VERDICT: `AMENDMENT_REQUIRED`.**

**Answers** (both read in full): `SOL_REREVIEW6_F50838F.md` (gpt-6-sol, FIX, D20LR7-S-1..5) and `ASTRA_REREVIEW6_F50838F.md` (gpt-6-astra, FIX, D20LR7-A-1..6; its header l.7 maps the convergence).

**Owner direction:** simplify rather than patch; prefer deleting mechanism; claim only what is true and testable; keep the rev 7 architecture. Revision 8 **deletes** the fixed-result index entry, the first-fixing rule, the post-append `t2` outage entry and Q7's second rule. It **moves** one step (the finish's clock check and record) under the existing lock and **reorders** one fsync (after lookup, not before). It adds no record type, no lock and no scheduler.

**Review status:** revision 8 is unreviewed. R19-2 requires a focused re-check by two model families before any owner decision. No human statistician has reviewed it.

**Checkout and mode:** `D:\PMP-programs-for-sharawi\aqt-freeze-sheet`, branch `freeze-sheet`. I wrote this one file only and ran **no git command**. No confirmation or lockbox data, network, credentials, keys or simulation were used.

## 0. Verification

**Read this session:** revision 7 in full; both re-check records in full; `REREVIEW6_PROMPT.md`; `d12-proposal/PROPOSAL_REV7.md` l.50-150 (step 2 l.81, step 5 l.84, P-7 l.86-94, P-5 l.96, l.113, R3 l.129, T-1..T-8 l.140-147); `OWNER_DECISION_D12.md` in full; Constitution l.66-90 and l.185-196; `src/aqt/core/ledger.py` l.84, l.300-307, l.340, l.350, l.409-415; revision 6 l.48, l.62, l.107, l.160, l.163, l.169, l.183, l.196; revision 5 l.32, l.49, l.114-116; revision 4 l.23, l.59, l.117, l.134, l.145, l.147, l.155, l.197; revision 3 l.186, l.248-258, l.285; Sol's rev-5 record l.24; DRAFT_WORDING l.75, l.244; Constitution l.147-153; protocol l.76.

**Governing text found by searching each topic (both directions):**
- D-12 step 5 (l.84): the worker records the read as finished "only while the store clock is before `D_w`. After `D_w` the result is fixed". D-12 P-7 (l.92): "if no row is committed before `R_j`, the release moves to `R_{j+1}` … The result was fixed at `D_w`, so a miss can never change it." Both turn on *when a save counts*; govern D20L-69 and Q7.
- D-12 P-5 (l.96), R3 (l.129, "its availability log (P-5) are trusted") and T-7 (l.146); `OWNER_DECISION_D12.md` l.29: "D-20 must bind … tests T-1..T-8". So availability measurement is an existing **D-20 obligation**, not optional. Governs D20L-70.
- **Precedent against sealed work under the shared lock**, which revision 7 did not cite and which D20L-69 partly reverses: rev 5 l.32 (D20LR4-A-1: lock waits reveal sealed write activity) and rev 6 l.48 (D20LR5-S-3 ~ D20LR5-A-1: deleted `L_seal` and made availability independent of sealed work). Both removals served timing protection, which revision 7 abandoned (rev 7 l.219, l.271). D20L-69 states the cost.
- Constitution §6 l.70 ("no silent deletion/correction") and §26 l.191 ("append-only/tamper-evident"): the §26 stops. §7 l.79: the row of §1.4.
- Rev 3 l.250: "the process stops until a human reconciles it". Who that human is, and what they may see, is unbound (D20L-75, inherited).

**Code facts (read, not run).** `read_entries` takes no lock and raises on damage (l.301-307). `append_entry` writes, flushes and fsyncs in separate steps (l.411-414) under its own sidecar lock (l.340, l.350; timeout l.84). The "every index reader holds `L_store`" rule is therefore an implementation obligation of the store, not a property of the existing code (Sol l.29).

**Exact integer arithmetic** (main checkout venv Python, `-I -B`, heredoc writing nothing). `R_0 = t_s + 604,800`, `d_w = R_0 − 43,200`, `D* = min(d_w, C)`.
- `(R_0 − 21,600) − D* = max(21,600, t_s + 583,200 − C)`, so its minimum is **21,600**, reached at every `t_s ≤ C − 648,000`; at `t_s = C − 1` it is 583,199 (sweep in steps of 997 plus edge points agrees).
- **Discriminating case (Sol's D20LR7-S-1 scenario).** `D* = 0`, a PASS finish with clock check `t_f = −1` whose record becomes durable at `L`; first asks at 21,600, 21,602, 90,001.
  - `L = 21,601`: revision 7 answers **FAIL, PASS, PASS**: the outcome depends on when the first ask comes. Revision 8 answers **PASS, PASS, PASS**: the ask at 21,600 waits for the finish's lock hold and then sees the record.
  - `L = 90,000`: revision 7 **FAIL, FAIL, PASS**; revision 8 **PASS ×3**.
  - A finish whose clock check is 21,600 (after an ask's hold): both refuse it, **FAIL ×3**.
  - This model encodes the lock serialisation, so it shows the difference between the rules; it does not prove revision 8's rule. The proof is the argument under "The result" in §1.2.

**The impossibility claim, narrowed (D20L-71).** After a crash, the durable records of a save that reached disk just before a deadline and of one that reached disk just after can be identical. So **no policy can both accept every on-time save and refuse every late one.** A strict policy that refuses every save it cannot confirm as on time *is* possible; its cost is that some saves that were in fact on time are thrown away. Revision 7 l.41 and l.297 said the strict rule "cannot be enforced"; that was too strong (Sol l.33, Astra l.65). The choice goes to the owner (Q7).

## 1a. Dispositions

| ID | Disposition | Evidence | Repair (where; finding) |
|---|---|---|---|
| **D20LR7-S-2 = D20LR7-A-1** (BLOCKER; name linked after the fsync, then used) | **Accepted.** The sealed-directory fsync now comes **after** the lookup and before any use. The selection point is the lookup made under `L_store`. | rev 7 l.86-92 fsyncs before reading | §1.2 durable before use; crash row 6; T-S4 interleaving; D20L-68 |
| **D20LR7-S-1** (BLOCKER) and Astra's step-5 check (l.102) | **Accepted. The first-fixing rule is deleted**, not routed. The finish's clock check, record and directory fsync run under `L_store`, so the first ask can no longer change the outcome (§0). What remains is the *commit-point* reading of step 5 and P-7, which is a proposed meaning of the decided D-12 rules and goes to the owner and C2 as Q7. Step 5 is **not** claimed preserved unconditionally. | rev 7 l.116, l.124-138; D-12 l.84, l.92 | §1.2 finishing, the result; Q7; D20L-69 |
| **D20LR7-S-3 = D20LR7-A-2** (BLOCKER; partial outage entry) | **Accepted, by the simpler route.** The `t2` outage entry is deleted; no claim is made that this draft extends cooling-off. Availability measurement (P-5, T-7) is a **mandatory S4/build carry-forward** with the required test schedule listed; until it is bound and tested, no promotion can rely on the 72 hours, and Q7 does not offer the compensation for decision. The binding route was not chosen: it would design a new log under review pressure, and D-12 already assigns that log to the trusted store (R3). | rev 7 l.107, l.192; D-12 l.96, l.129, l.146 | §1.2 carry-forward; Q7; D20L-70 |
| **D20LR7-S-5 = D20LR7-A-3** (Astra BLOCKER; Sol NON-BLOCKING) | **Accepted, at BLOCKER.** Claim narrowed to the tradeoff; both policies offered plainly. | rev 7 l.41, l.297 | §0; Q7; D20L-71 |
| **D20LR7-S-4** (BLOCKER) **~ D20LR7-A-5** (NON-BLOCKING) | **Accepted, at BLOCKER.** The §7 row covers delayed or missed releases and the cap expiry they cause; "no added log entry" becomes "no added research-visible disclosure". Both record types the reviewers asked to list are **deleted** (D20L-69, D20L-70), so revision 8 adds no index record type; S4 must list the availability record it designs. | rev 7 l.239, l.74, l.107 | §1.4; D20L-72 |
| **D20LR7-A-4** (NON-BLOCKING; crash coverage) | **Accepted.** Rows cover survival, loss and partial persistence, before and after a completed fsync; the mock is described as validating the algorithm under its model. | rev 7 l.173-180, l.202 | crash table; T-S4; D20L-73 |
| **D20LR7-A-6** (NON-BLOCKING; Q1, "briefly") and Astra's T-S1 note (l.104) | **Accepted.** | rev 7 l.215, l.267, l.269, l.191 | Q1; §1.3; T-S1; D20L-74 |
| Sol: D20LR6-S-3 note, a delay before `t1` can miss a release (l.19) | **Accepted**; already in R5 item 4 | | §1.3 |
| Sol: reader-lock rule is an obligation, not a property of `read_entries` (l.29) | **Accepted** | ledger l.301-307 | §0; §1.2 one lock |
| Sol and Astra: the mock cannot verify the platform (l.27; l.75) | **Accepted** | | T-S4 |
| Astra: T-S3 needs the fixture to supply admission prerequisites (l.106) | **Accepted** | | T-S3 |
| E7-1, E7-2, E7-3 confirmed by both (Sol l.35; Astra l.112) | **Applied as stated in §4** | | §4 |

## 1. Bindings

### 1.1 Replacements outside the store section (replace rev 7 §1.1)

**B1 publisher row.** Revision 6's row (rev 6 l.62) with one change: `state`, `guard_state` and `insert_release` take the result from **the result rule** (§1.2). After a release, `state` answers `{"fixed": true, "released": true, "result": <release entry's result>, "store_now": t}`; the release entry carries the same result (§1.2 shows the rule cannot change after `D*`).

**Worker deadline.** `D* = min(d_w, C)` and the reading of `DEADLINE:NOT_FINISHED_BY_D_W` (rev 5 l.49) stand. `write_bundle` has no time check. `mark_finished` follows §1.2. The signer guard's "finished … `finished_at < D_w`" bullet (rev 3 l.186) becomes "the result rule gives PASS".

### 1.2 The store (self-contained; replaces revision 7's §1.2)

**Records.** Only these are authoritative.
- **The index:** the append-only ledger, with pre-read, rejection, no-read and release entries. **Revision 8 adds no index record type**; rev 7's `aqt.lockbox.fixed.v1` is deleted.
- **Sealed files**, each written once and never replaced (§26): the DEFAULT bundle with its nonce and commitment, under `(evaluation_id, attempt)`; RESULT bundles; at most one finished record per evaluation (`aqt.lockbox.finished.v1` = `{evaluation_id, result, commitment, finished_at}`, rev 3 l.285); the pre-read check record (rev 4 l.117); `lockbox_eval`'s startup records. A sealed file is created as: write a temporary file, fsync it, link it to its final name **without replacing**, fsync the directory. Temporary files are never read; reconciliation logs them. All sealed files are in one directory.

There is no snapshot, no scheduler, no scheduled step and no stored copy of the result.

**One lock.** `L_store` is the store's own lock file (D20L-46). The store takes it for: `begin_read`, rejection appends, `insert_release`; `state`, reader rows, `guard_state`; `verify_replay`, reconciliation, startup; the read gate's entitlement check; and **steps 2-4 of `mark_finished`** (below). Nothing reads the index except through these operations; `read_entries` itself takes no lock, so this is an obligation on the store code, checked by T-S1 and §16 review. The worker and the signer never hold `L_store` themselves. `write_bundle` and every other sealed create take no lock.

**Durable before use (D20L-64 as amended by D20L-68).** Holding `L_store`, an operation first does its lookups (index entries, sealed names). **Then** it fsyncs the index file, the index's directory and the sealed directory. **Only then** does it answer, append, create, serve a bar or authorise a signature. The rule it guarantees: *no output depends on an index line or sealed name unless an fsync of its file or directory completed after the lookup that found it.* A name a lock-free writer links after the lookup was not found and is not used. An fsync error is a §26 stop. An index line can appear only under `L_store`, so the only un-fsynced index bytes an operation can find are those of a crashed process.

*Platform assumptions:* an fsync makes durable whatever is already written to that file or directory, whichever process wrote it; and the OS releases `L_store` when its holder exits. Both are `UNVERIFIED_EXTERNAL_ASSUMPTION` for the target OS and filesystem.

**Time rules (D20L-63 as amended by D20L-69 and D20L-70; the convention is Q7).** One rule for every save with a deadline: **a save counts as made at the clock reading `t1` taken while holding `L_store`, immediately before it starts, if `t1` is before the deadline.** Every reader waits for `L_store`, so no one can read between `t1` and the moment the save is durable; no bound on that wait is claimed. A save lost in a crash before it is durable never happened.
- *Index appends:* the appends inside `begin_read` (deadline C) and `insert_release` (window `R_j − 21,600 ≤ t1 < R_j`). If `t1` misses, nothing is written: `CAP_REACHED`, or a missed release (P-7). Otherwise `append_entry` runs with `L_store` still held. A `LedgerError` before writing (lock timeout, damaged chain) means nothing was written; a timeout is refused, damage is a §26 stop. Any error after the write starts is a §26 stop with no retry and no repair.
- *Finishing,* `mark_finished(evaluation_id)`, deadline `D*`:
  1. Without the lock: verify the RESULT bundle against its commitment; fsync the bundle and the sealed directory.
  2. Take `L_store`; look up the pre-read entry (for `D*`) and any finished record; the fsyncs; then read the clock, `t_f`.
  3. If `t_f ≥ D*`, or a finished record exists, refuse: the bundle is late output, void, logged by reconciliation, never published.
  4. Otherwise create the finished record with `finished_at = t_f`, including its directory fsync, and only then release `L_store`.

  Because `t_f` is read after the result is durable and the record is durable before the lock is released, a counted finish is never seen half-made.
- *Start checks* (no weight; unchanged from rev 7 l.118-120): `record_pre_read_check` (deadline C) and each bar (deadline `D*`) read the clock before starting and refuse at or after the deadline. A check record landing after C admits nothing (`begin_read` answers `CAP_REACHED`); a bar received at or after `D*` cannot reach a counted result, since any finish using it reads `t_f ≥ D*`.
- *Cap scope:* from C on, no operation limited by C or `D*` starts: no pre-read check, read authorisation, rejection append, bar or counted finish. Release inserts are limited by their own window and continue after C (D-12 l.94). `write_bundle`, reads, reconciliation and replay also continue. This is how §1.2 reads "at day 255 processing ends" (DRAFT l.244).

**The result (replaces rev 7's fixed result, D20L-62).** `state`, `guard_state` and `insert_release` answer only at store time `≥ R_0 − 21,600`; before that `state` answers `fixed: false` and the other two refuse. From then on, under `L_store` and after the fsyncs: if a finished record exists for the pre-read entry's attempt, the result is its `{result, commitment}`, and its RESULT bundle must verify (if it does not, that is a **§26 stop**, never a silent FAIL, §6 l.70); otherwise it is the DEFAULT's (FAIL/DEADLINE). After a release, `state` reads the release entry.

*Why it cannot change (the proof).* Take any answering call A at clock `≥ R_0 − 21,600` and any finish F. Both hold `L_store`, so their holds do not overlap. If F's hold came first, its record was durable before A began, and A counts it. If A's hold came first, F's `t_f ≥ R_0 − 21,600 ≥ D* + 21,600 > D*` (§0), so F is refused. Hence every answer from `R_0 − 21,600` on sees the same set of finished records, whatever the call order: the first ask cannot alter the outcome, and `state` cannot contradict a release. This needs only that the store clock never steps back by 21,600 s or more (R3: the store clock is trusted).

**How D-12 step 5 and P-7 read under this (not claimed unchanged).** Step 5's "records the read as finished … only while the store clock is before `D_w`" becomes "`t_f < D*`, read under `L_store` after the result is durable". "After `D_w` the result is fixed" holds in this sense: after `D*` no new finish can count, and the only later event that can matter is a crash that loses a finish whose clock check was before `D*`, which then counts as unfinished (a technical FAIL) and was never visible to anyone. P-7's "committed before `R_j`" likewise becomes "`t1 < R_j` under `L_store`". This is the Q7 convention. It is a **proposed meaning** of decided D-12 rules, for the owner (Q7) and for C2 to write into step 5 and P-7 explicitly.

**`begin_read(evaluation_id)`, under `L_store`.** As revision 7 (l.140-152), with step 1 changed: the lookups (index verification, reconciliation, entitlement, budget, order and cooldown) come first, then the fsyncs, then any answer, append or sealed create. Damage is a §26 stop. Steps 7-8 and the void-orphan rule (rev 3 l.249) are unchanged; the step-8 append follows the time rule with deadline C. A no-read entry's `visible_from` is `t1`.

**The read gate.** When `lockbox_eval` opens a read session, the store, under `L_store`, looks up the pre-read entry, its DEFAULT and a `PASS` startup record for the check record's module hash and image; then the fsyncs; then verifies the DEFAULT; then opens the session. Bars are served without the lock, each under the start check against `D*`. After C the gate serves nothing (`D* ≤ C`).

**Startup.** Before serving anything, under `L_store`: index verification and revision 3's reconciliation (l.248-250, which also logs temporary files and void bundles); then the fsyncs. Nothing is rebuilt or replayed.

**Availability (carry-forward, D20L-70).** This draft does **not** measure reader-path availability and does **not** claim that any wait or crash extends cooling-off. P-5 requires it, D-12 assigns the log to the trusted store (R3, l.129), and T-7 is a D-20 test obligation (`OWNER_DECISION_D12.md` l.29). S4/build must bind it, and T-7 must cover at least:
- a release append whose `t1 < R_j` but which is durable after `R_j` (readers wait from `R_j` to the end of the hold);
- a store down across `R_j` through crash and restart, and a §26 stop after `R_j`;
- a crash while the availability record itself is being written, and recovery of that record;
- overlapping intervals counted once;
- what counts as "unavailable" (a call that waits, for how long).

Until the owner's earliest decision time can be computed from reconciled records, no promotion can rely on it (P-5: "at least 72 hours of actual access"). The S4 text must list the availability record type with its payload, visibility, replay and recovery.

**Crash points (D20L-64, D20L-73).** P = process crash, M = machine crash. Under M, un-fsynced data may **survive whole, be lost, or (an index tail) be partly written**; a link is atomic, so a name is present or absent; data whose fsync completed survives.

| # | Crash at | After restart | Effect |
|---|---|---|---|
| 1 | DEFAULT linked, directory not fsynced, before the step-8 append | P: name present. M: present or absent | void orphan either way; no budget spent; next call uses a new attempt |
| 2 | step-8 line written, fsync not completed | P: line whole. M: whole, lost, or partial | whole: counts (made at `t1 < C`), made durable by the next operation's fsync; lost: as row 1; partial: row 4. No one was served from it |
| 3 | step-8 fsync completed, before the reply | durable | `begin_read` returns it; after C the gate serves nothing |
| 4 | partial last index line | index damaged | **§26 stop** until a human reconciles it (§6 l.70, §26 l.191; who, D20L-75) |
| 5 | sealed create before the link | temporary file only | record absent; temp logged |
| 6 | lock-free sealed link done (startup record, RESULT bundle), creator's directory fsync not done | P: present. M: present or absent | if any operation looked it up, that operation fsynced the directory before using it, so the name survives; if absent, nothing used it |
| 7 | `mark_finished` after `t_f < D*`, before the record's link | no finished record | unfinished; a retry reads a fresh `t_f`, refused from `D*` |
| 8 | `mark_finished` link done, directory fsync not completed | P: present. M: present or absent | present: counts (startup fsyncs it before anyone reads); absent: unfinished. Decided before any answer, since no one could read during the hold |
| 9 | `mark_finished` directory fsync completed, before unlock | durable | counts |
| 10 | release append with `t1 < R_j`, fsync not completed | P: whole. M: whole, lost, or partial | whole: counts at `t1`; lost: missed release (P-7 l.92), retried at `R_{j+1}`; partial: row 4. Reader waits after `R_j` are P-5 unavailability, for the carry-forward to measure |
| 11 | `append_entry` I/O error after the write starts | durability unknown | §26 stop |
| 12 | restart after C, entry made before C | entry durable | gate serves nothing; `mark_finished` refused; result is DEFAULT unless a counted finished record exists |
| 13 | restart after a release | release durable | answers read it |

Apart from the §26 stops, every row leaves one set of durable records, read directly by every operation. Rev 7's rows for the fixed entry and for "a finished record present after fixing" are deleted: by the proof above, no counted finished record can appear after an answer.

**Pre-read reason codes:** revision 2's list without `COOLDOWN_NOT_ELAPSED` (rev 4 l.145).

**Tests.** Revision 3's list (l.253-257), revision 4's list (l.147-155), revision 6's cooldown boundary and revision 5's cap-order test (l.114). Revision 5's reconciliation-after-C and worker-deadline tests (l.115-116) are replaced by T-S2 and T-S4. Clock and fault injection throughout.
- **T-S1, index appends at their deadlines.** `begin_read`: `t1 = C − 1` accepted, `t1 = C` refused. `insert_release`: `t1 = R_j − 21,601` refused, `t1 = R_j − 21,600` (lower bound) **accepted**, `t1 = R_j − 1` accepted, `t1 = R_j` (upper bound) **refused**; refused means nothing written. With an accepted `t1`, the clock is advanced past the deadline at each point inside `append_entry` (waiting for its lock, after verification, between write and flush, between flush and fsync, after fsync): the entry counts, and each concurrent `state`, reader-row, `guard_state` and `begin_read` call returns only after the append and shows it. An injected write, flush or fsync error gives a §26 stop, nothing served.
- **T-S2, finishing and start checks,** for `D* = d_w` and `D* = C`. `t_f = D* − 1` counts; `t_f = D*` refused. A crossing between the bundle's fsync and the `t_f` read is refused. With `t_f < D*`, the clock is advanced past `D*` and past `R_0 − 21,600` at each point inside the hold (temp write, its fsync, link, directory fsync): the finish counts, and a concurrent `state` waits and then shows it. A second `mark_finished` is refused. `write_bundle` after `D*` is accepted as bytes and never counts. Bars and `record_pre_read_check` as rev 7 l.199-200.
- **T-S3, lock independence of everything but the finished record.** An instrumented `L_store` raises if `write_bundle`, any sealed create outside `mark_finished`'s steps 2-4, or the worker or signer process acquires it. The fixture supplies the admission prerequisites. Two runs: a `write_bundle` stalled at the function level (no disk load), and a crashed worker; in both, `state` at `R_0 − 21,600` returns the result and `insert_release` succeeds in its window. **Not tested and not claimed:** availability under disk or CPU contention, or while a finish holds `L_store` (§1.3).
- **T-S4, crash points.** One test per row, under P and under M, including restart after C and after a release. The M runs use a test file layer that, at the crash, applies **each** permitted outcome to un-fsynced data (survive whole, lose, and for the index tail write partly) and keeps all fsynced data. **Interleaving test (D20L-68):** a lock-free writer links a startup record (and, separately, a RESULT bundle) after an earlier directory fsync and stalls before its own; the read gate (or `mark_finished`) looks it up and uses it; an M crash follows; after restart the name is present. The same test run against rev 7's order (fsync before lookup) must fail, which shows the test discriminates. The layer validates the algorithm **under its model only**; it does not verify the platform assumptions, which stay `UNVERIFIED_EXTERNAL_ASSUMPTION`. If the build cannot provide the layer, the M rows are **not available** and block completion; they are not N/A.
- **T-S5, one result.** A PASS finish with `t_f < D*` stalled inside its hold across `R_0 − 21,600`: `state` (waiting), `guard_state`, `insert_release` and `state` after the release all give PASS, and the release's result equals the rule's. A finish whose lock acquisition comes after the first ask: refused, every answer FAIL. An M crash at rows 8 and 9: every answer after restart agrees with whether the record survived. A finished record whose RESULT bundle is corrupted: §26 stop, not FAIL.
- **T-S6, payload shape:** unchanged (rev 6 l.169).

None of these tests measures timing. No timing or latency property is claimed.

### 1.3 The timing residual R5 (self-contained; replaces revision 7's §1.3)

**What is separated, and nothing more.** No sealed write takes a lock except the finished record (`mark_finished` steps 2-4); the worker and signer never hold `L_store` themselves. The store holds `L_store`, for an unbounded time, once per read session for the gate check, for each `guard_state`, and **once per finish** (§1.2, `mark_finished` steps 2-4). The result depends only on finishes whose clock check was before `D*`. The release time is `R_j`; every FAIL answer has the same bytes and shape (T-S6).

**Resource assumptions: none.** Public calls and sealed work share one machine: CPU, memory and disk, including the filesystem journal every fsync uses. Sealed work can slow any public call, with no bound.

**What can leak or happen** (to anyone who can call the store or watch it: the publisher, and the reader account, i.e. the owner and through him research, D-12 l.117):
1. **During a read**, from `t_s` until the worker stops: whether it is running, stopped early or restarted, and when it finished. A finish now holds `L_store`, so public calls wait **at that moment**: this re-admits, inside R5, the lock channel that rev 5 l.32 and rev 6 l.48 removed. It reveals that a read ran to the end (PASS or performance FAIL) and when. I have **not** shown that R5 cannot hint at **PASS versus performance FAIL**: compute paths differ by outcome (for example, `upside` is computed only for a finite `T_L`), although the finished record has one shape for both.
2. **After `D*`:** a worker can compute until refused, and late writes are void but use the disk. A finish whose check was before `D*` can still be holding `L_store` after `D*`.
3. **In the release window** `[R_j − 6 h, R_j)`: the signer is asked only for a **PASS with `R_j < C`**, so its activity can reveal such a PASS up to six hours early.
4. **Missed releases:** sealed activity, including a stalled finish holding `L_store`, can delay `insert_release` past its `t1` check: a missed release (P-7: incident, one-day delay, possibly repeated). Near day 255 it can make a finished PASS expire `U_ops` (P-6). A slip is visible and can correlate with the result. A slow machine can also make a worker miss `D*` (a deadline FAIL).

**How much:** not measured; no bound is claimed. **What it cannot do:** change a result or a counted try. It **can** move a release by whole days and, near day 255, cause an expiry.

**Compared with D-12's R1-R4:** R1 needs a signing fault and hints only at a PASS. R5 needs no fault. The owner's acceptance of R1-R4 (`OWNER_DECISION_D12.md` l.31) does not cover it; §1.4 and Q6.

### 1.4 Proposed Constitution §7 row (self-contained; replaces revision 7's §1.4; proposal only)

Carried in C2's Constitution table (DRAFT §1, l.75-95) **only if the owner chooses "Accept" in Q6**, through the S4 drafting and the required human review. The first sentence is the row already required by the owner's D-12 Q2a decision (D-12 l.57; `OWNER_DECISION_D12.md` l.12).

| Ref | Current v1.0 text | Proposed v1.1 text |
|---|---|---|
| §7 l.79 | "Research receives PASS/FAIL only." | "Research receives PASS/FAIL only, except that the cycle outcome of §5 may show that a family had no result because its lockbox read failed technically. How quickly the lockbox service answers, a delayed or missed lockbox release, and an expiry at the processing cap caused by such a delay are not results under this rule, even where they allow a guess about a result. This exception covers only these timing and delay effects of the lockbox service specified in the protocol. It permits no added research-visible field, message, record or diagnostic: audit, incident and availability records required by the protocol may exist, and what research can see of them is limited to a release's time and day index and the earliest owner decision time. No component may vary its timing to convey a result." |

**Matching protocol wording (optional; for S4):** protocol l.76 keeps `value: "PASS_FAIL_ONLY"`; its justification would add "Timing and delay effects of the lockbox service are governed by Constitution §7." The last clause is checkable by §16 code review, not by a test. Like Q2a's row, the exception applies to later cycles until amended.

## 2. Findings

**Changes to earlier findings:**
- **D20L-62** is superseded by D20L-69: the fixed-result entry is deleted; one result now follows from lock serialisation.
- **D20L-63** is amended by D20L-69 (one time rule, now also for finishing), D20L-70 (`t2` outage entry deleted) and D20L-71 (impossibility claim narrowed).
- **D20L-64** is amended by D20L-68 (fsync after lookup) and D20L-73 (crash outcomes).
- **D20L-65** is narrowed further by D20L-69: lock independence no longer covers the finished record (`mark_finished` steps 2-4).
- **D20L-66** is answered by D20L-72; **D20L-67** is qualified by D20L-74.

**New findings:**
- **D20L-68 BLOCKER (repaired; §1.2 durable before use, crash row 6, T-S4).** Rev 7 fsynced the sealed directory before looking names up, so a name linked between that fsync and the lookup could be used and then lost. The fsync now follows the lookup. (D20LR7-S-2 = D20LR7-A-1.)
- **D20L-69 BLOCKER (repaired by deletion; the remaining convention goes to Q7 and C2).** Rev 7's result depended on whether a finished record landed before the first ask, which changes D-12 step 5's fixation at `D_w`. The finish's clock check and record now run under `L_store`; the fixed-result entry, the first-fixing rule and Q7's second rule are deleted. **Cost:** a finish now holds the shared lock, re-admitting inside R5 the channel removed by rev 5 and rev 6, and a stalled finish can delay a release. **Alternative not chosen:** keep rev 7's lock-free finish and put the step-5 change to the owner; reviewers may prefer it, and it is compatible with the rest of §1.2. (D20LR7-S-1; Astra l.102.)
- **D20L-70 BLOCKER (repaired by deleting the claim; measurement carried forward).** Rev 7's `[R_j, t2)` entry undercounted and could be lost in a crash. It is deleted; P-5 measurement and T-7 are a mandatory S4/build carry-forward with a listed schedule; no promotion relies on it until bound. (D20LR7-S-3 = D20LR7-A-2.)
- **D20L-71 BLOCKER (repaired; §0, Q7).** "Strict durability cannot be enforced" overstated an ambiguity. (D20LR7-S-5 = D20LR7-A-3.)
- **D20L-72 BLOCKER (repaired; §1.4).** The §7 wording forbade the records the protocol needs and missed the cap expiry. (D20LR7-S-4 ~ D20LR7-A-5.)
- **D20L-73 NON-BLOCKING (applied).** Crash rows and the mock now cover survival, loss and partial persistence. (D20LR7-A-4.)
- **D20L-74 NON-BLOCKING (applied).** Q1 wording, "briefly" deleted, T-S1 boundaries stated. (D20LR7-A-6; Astra l.104.)
- **D20L-75 QUESTION (carry-forward to S4; inherited from rev 3 l.250, extended by rev 7 l.175).** A §26 stop needs "a human" to reconcile the index or sealed store. If that human is the owner, he could see a release row before its `visible_from`, or a sealed result. Who reconciles, and under what access, is unbound. Not repaired here, because choosing the person is an owner/S4 decision.

## 3. Owner questions (Q1, Q6, Q7 replaced; Q2(i), Q2(ii), Q3-Q5 as in revision 5; each has "Keep blocked")

**Q1. Adopt the detail rows and the new defaults?**

*In short:* this adopts the AI-drafted rule book for running, sealing and posting the lockbox test. With it, the builds can start, each needing §16 review. Without it, the lockbox cannot run.

What changed since revision 7, in plain terms:
- **From day 255, no new test is admitted and no test can be counted as finished.** A test still running is posted as a technical fail, and the pick expires unpromoted; one admitted shortly before day 255 may fail this way. A worker may go on writing sealed output, but it can never count. Posting of results continues after day 255. A step already under way may end after day 255; no time limit is claimed.
- **A test's result is settled at its worker deadline** (in the sense of Q7) and cannot change later. Nobody sees it until six hours before its posting time.
- **Before relying on any record, the service makes sure that record is safely on disk.** A damaged log stops everything until a person sorts it out (who that person is, is still open).
- While a finished test is being saved, other callers of the service wait (Q6).
- **How waiting time is added back to your 72 hours is not designed yet.** It must be designed and tested before anything can be promoted.

Adopting Q1 does **not** settle D11-15. The D20L-36 sentence (revision 4 Q1) stands.
- **"Adopt (Recommended)."** Cost: several builds, each needing §16 review. A lost key can cost a good PASS.
- **"Keep blocked."**

**Q6. May the lockbox service's speed and delays give hints?**

*In short:* the hidden test and the parts that answer you and the posting job run on one computer and share its disk. How fast they answer, and whether a posting comes on time, can depend on the hidden work. Someone timing the service closely (you, or the research AI working with you) might guess, before a result is posted:
- that a test broke down or stopped early rather than running to the end, and when it finished (the service makes callers wait while it saves a finished test);
- possibly whether it **passed or failed on performance**. Nobody has shown that it cannot;
- in the six hours before a posting, that a PASS is coming, because only a PASS posted before day 255 gets signed;
- something about the result from a posting that **slips by a day** because the computer was busy, or from a PASS that **expires at day 255** because of such slips.

These hints cannot change a settled result or a counted try. Nobody has measured how clear they are, and this draft claims nothing. The Constitution says research receives PASS/FAIL only, so allowing these hints needs **a written exception**, which you would sign in C2 after a person reviews it. Like your Q2a exception, it would apply to later cycles until changed. The words are in §1.4.
- **"Accept: sign the timing exception in C2 (Recommended)."** Cost: the hints above, allowed in writing.
- **"Keep blocked."** The lockbox cannot run until someone designs stronger separation, for example separate machines. This draft does not propose that.

**Q7. When does a save count as made in time?**

*In short:* saving to disk takes a moment nobody can bound, so a rule must say at which instant a save "happened". The rule covers three saves: starting a test (before day 255), finishing a test (before the worker deadline) and posting a result (before the posting time). Your answer also fixes how your D-12 rules "finished before the deadline" and "posted before the posting time" are read; C2 would write that meaning into them.
- **Draft rule:** a save counts at the moment the service checks its clock, if that is before the deadline. During the save the service lets nobody read its records, so nobody can see anything in between. If a crash loses the save, it never happened: no test, a technical fail, or a posting moved to the next day.
  - *Cost:* a save may reach the disk after the deadline. For a posting, anyone reading in that gap waits past the posting time; under your D-12 decision your 72 hours do not count that wait, but how it is measured is not designed yet (Q1).
- **Stricter rule (possible; not drafted):** a save counts only if the service confirmed, after the disk finished, that the deadline had not passed; a save it cannot confirm after a crash is thrown away.
  - *Cost:* some saves that were in fact on time are thrown away, so a test that finished in time can become a technical fail, or a posting can slip a day. It needs one more record per save and new design work.
- No rule can both keep every on-time save and refuse every late one, because after a crash the records can look the same either way.

Options:
- **"Accept the draft rule (Recommended)."**
- **"Ask for the stricter rule."** A new draft would be needed.
- **"Keep blocked."**

## 4. Remaining, unauthorised, errata, self-check

**Remaining:**
- the R19-2 re-check of this revision (focused on D20L-68 and D20L-69's lock trade);
- owner Q1-Q7;
- the S4 items of revision 4, plus D20L-66/72 and the §1.4 row if Q6 is accepted, the step-5/P-7 meaning chosen in Q7, the availability record and T-7 schedule (D20L-70), and who reconciles a §26 stop (D20L-75);
- the single consolidated S4 signing text (an obligation), used by both signing and implementation;
- the C2 rows of revision 4;
- the builds: revision 4's builds plus the time rule, durable-before-use ordering, the availability log, tests T-S1..T-S6 and T-7 with the crash test file layer, each under §16 review (Constitution l.147-153; lockbox ACL tooling, l.152).

**Unauthorised:** frozen edits; activation; acceptance; any code; key generation; simulation; confirmation or lockbox access; promotion; deployment; trading. `KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid outcomes.

**Errata (history and committed records are not edited):**
- **E7-1, applied here:** rev 6 l.160 cites "revision 3's list (l.253-258)"; the list is l.253-257 (l.258 is blank). §1.2 Tests cites l.253-257. Rev 6 is not edited.
- **E7-2, note only:** Sol's rev-5 record (`SOL_REREVIEW5_2CDBF88.md` l.24) links D-12 P-7 to `PROPOSAL_REV7.md:87`, the `R_j` definition; the "committed before `R_j`" clause is l.92. The committed record is not edited; its finding stands.
- **E7-3, applied here:** rev 6 l.107 ("within the one system call and fsync") and l.183 ("cannot change … a release time") are superseded by §1.2's time rule and §1.3's "can move a release by whole days". Rev 6 is not edited.
- I noticed no further erratum in revision 7 outside the sections this revision replaces.

**Self-description check** (done after the last edit):
- one file written, no git command run;
- re-check findings answered: 11 IDs (D20LR7-S-1..5, D20LR7-A-1..6), forming 7 distinct issues, plus 4 reviewer notes and the errata confirmation;
- new findings D20L-68..75, with no gaps; D20L-62 superseded;
- owner questions: Q1, Q6, Q7 replaced; Q7 now has one rule and offers the stricter rule as an option;
- mechanisms deleted: the fixed-result index entry `aqt.lockbox.fixed.v1`, the first-fixing rule, the `t2` outage entry, Q7's second rule, and the fsync-before-lookup order;
- mechanisms added or moved: `mark_finished`'s clock check and record under `L_store`; the sealed-directory fsync after lookup; T-S4's interleaving test and three-outcome crash layer.
