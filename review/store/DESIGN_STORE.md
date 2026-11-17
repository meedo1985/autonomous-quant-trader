# Store build design, rev 2: the one store serving the confirmation and lockbox modules

- Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-17, branch `store-design` from
  `main` `92e6f52` (PR #84 merged). History: rev 1 `1633831` (Astra FIX ST1-A-1..5,
  record `644558a`, adjudication `ADJUDICATION_DESIGN_STORE_REV1.md`); rev 2 repairs all
  five (A-2 with a stated limit).
- Owner instruction (2026-11-17, chat dialog): next task "Store build design".
- Nothing here is decided by writing it. **[OWNER]** marks owner or S4 decisions;
  **[DESIGN]** marks choices this design proposes for review.

## 0. Authority and what this design is

- **Annex D rev 2.1** (`freeze-sheet` `3abcafb`,
  `review/governance-statistics-amendment/s4-amendment-draft/ANNEX_D_LOCKBOX.md`):
  §D-2.3 identities, §D-2.4 release, §D-2.5 delivery, §D-2.6 signing and effectiveness,
  §D-2.7 the cap, §D-2.8 response codes and reader projection, §D-3.6 store identities,
  **§D-3.7 the store**, §D-3.8 crash rows and tests, §D-3.9 ("each build, under §16
  review: the store, publisher, signer, both modules and the access tooling").
- Crash rows and tests cited by §D-3.8: `d20-lockbox-proposal/PROPOSAL_REV8.md` (rows 1-13,
  T-S1..T-S6) and `OPTION_C_PROPOSAL_REV2.md`..`_REV5.md` (rows C1-C15, TC-1..TC-7), same
  commit.
- **Module obligations already written down:** `calibration/c2_lockbox.py` `Store` and
  `ReadSession` (l.1210-1262); `calibration/c2_confirmation.py` `Store` and `Persist`
  (end of file); `DESIGN_SLICE6B.md` rev 16 §12 (release condition, inventory, required
  release tests).
- Constitution §7 (lockbox), §16 (the store is **lockbox ACL tooling** and
  protocol-enforcement logic: different-model and human PR review before merge), §26
  (append-only, tamper-evident), §27, §28 (no secrets).
- Annex D is S4 **draft** text. The store binds only through the signed C2 and S4 as
  adopted; if S4 changes a store rule, this design is re-checked against it.

This document designs **the store build only**. Separate builds, out of scope here:
the publisher (`L_pub`, `R_0` file, outbox, backstop, P-8 validation), the signer
(Ed25519 key, `cryptography` pin), the owner's forced command, OS account provisioning,
deployment. The store exposes the operations they call and is tested against test doubles
of them.

## 1. What the store is

One store service on one host (§D-3.6) holding:

| Holding | What | Written by |
|---|---|---|
| **Cycle ledger** | the C2 cycle's `aqt.core.attempts` starts and outcomes, `aqt.c2.trial_result_entry.v1`, look, closing and termination entries, `aqt.c2.artifacts.v1` | the confirmation module processes (results, look, closing), the store's runner (starts, outcomes) and the store (termination, artifacts), each through `aqt.core.ledger.append_entry` under the cycle's look lock (6b §4, FINAL-F-4) |
| **Lockbox index** | §D-3.7's entries: pre-read, rejection, release, delivery, VOID, revision and invalidation | the store only, under `L_store` |
| **Sealed directory** | one directory; every file created once, never replaced: DEFAULT bundles (with nonce and commitment), RESULT bundles, finished records, pre-read check records, startup records, attestation files; plus the C2 evaluation and sealing records, prediction artifacts, the nominee inventory items (trial JSON, signal and overlay source) and the capture record with its archive payload | the store, except attestation files (the signer, through the store's sealed create) |
| **Store configuration** | the cap C (computed once, §D-2.7), the cycle's data-manifest hash from its governing cycle record, the uid-to-role map | set once at cycle setup **[OWNER]** procedure |
| **Clock** | host system clock, floored to integer seconds | — |

**[DESIGN] D-1, two ledgers.** The cycle ledger and the lockbox index are separate files.
Their writers and locks differ: module processes append to the cycle ledger themselves
under the look lock (6b), while §D-3.7 says only the store writes the index, the worker
never does, and every index reader goes through a store operation under `L_store`. One
file would put module writers under `L_store` or the index under the look lock, against
one of the two texts.

### 1.1 Reading the cycle ledger before use (ST1-A-1)

The store uses cycle-ledger facts (the closing entry and its hashes, termination entries,
the look entry, starts and outcomes) only under this order, inside the operation that uses
them:

1. take `L_store` (if the operation is an `L_store` operation), then the cycle's **look
   lock**; every cycle-ledger writer (module processes and the runner) appends only while
   holding the look lock (6b §4, FINAL-F-4), so no append is in progress;
2. read and verify the cycle ledger (`scan_bytes`, and the ledger-identity check of §4.1);
3. fsync the cycle-ledger file and its directory (this makes durable any complete line a
   crashed writer left un-fsynced, as §D-3.7's durable-before-use does for the index);
4. only then decide, answer, append to the index or serve.

**Lock order** **[DESIGN] D-7**: `L_store`, then the look lock, then the ledger's append
lock. Module processes and the runner never take `L_store`, so no holder of the look lock
ever waits for `L_store`; there is no cycle. Tests: a writer stalled between write and
fsync of a closing entry (the store waits on the look lock and then sees it durable); a
crashed writer leaving a complete un-fsynced closing line (the store's fsync makes it
durable before admission; under M before that fsync, the line may be lost and the store has
not used it).

## 2. Placement and reuse

- **[DESIGN] D-2, package `aqt.store`** (new, under `src/aqt/`). New import-linter
  contracts: `aqt.research`, `aqt.app`, `aqt.dashboard`, `aqt.metrics.assembly` cannot
  reach `aqt.store`; `aqt.store` cannot reach `aqt.research`, `aqt.models`,
  `aqt.execution`, `aqt.governor`. The store does not import `calibration` (the modules
  are separate signed files); the record-type names and field sets it shares with them
  are constants in `aqt.store`, with a test that they equal the modules' own
  (`c2_confirmation.RESULT_ENTRY`, `CLOSING_ENTRY`, `TERMINATION_ENTRY`, the lockbox
  record schemas), so drift fails a test.
- **Reuse:** `aqt.core.ledger` (entry format, chain verification, `LedgerError`),
  `aqt.core.attempts` (`start_attempt`, `finish_attempt`, the crash reason codes),
  `aqt.data.manifest` (`canonical_json_bytes`, composite and partition manifest
  verification), `calibration.seeds.cj` semantics via `canonical_json_bytes`.
- **[DESIGN] D-3, the index writer.** `append_entry` writes with `open`/`fsync` directly
  and takes its own `.lock` sidecar, so crash rows 2, 4, 11, C2 and C6 cannot be injected
  into it, and it does not fsync the directory on file creation (§D-3.7 "durable before
  use" requires the index directory fsync). The store's index writer therefore appends
  through the store's file layer (§3) under `L_store`, producing **byte-identical** lines
  (same `LedgerEntry`, `canonical_hash`, `GENESIS_HASH`; a test compares with
  `append_entry` on the same input) and verifying the chain first as `append_entry` does.
  One small public addition to `aqt.core.ledger` is proposed: `scan_bytes(data)` (the
  existing `_scan`), so the store verifies with the ledger's own parser instead of a copy.
  That is a change to reviewed code, listed for review.
- No new dependency. The commitment is SHA-256; Ed25519 belongs to the signer build.

## 3. The file layer and the clock **[DESIGN] D-4**

- `Fs` protocol, the only path to disk inside `aqt.store`: `read(path)`, `list(dir)`,
  `write_temp(dir, bytes) -> tmp`, `fsync_file(path)`, `link_noreplace(tmp, name)`
  (POSIX `link`, fails if the name exists), `unlink_temp(tmp)`, `fsync_dir(dir)`,
  `append(path, bytes)`, `fsync_append(path)`.
- `PosixFs` (Linux; directory fsync needs `os.open(dir, O_RDONLY)`). The store refuses to
  start on a platform without it; development on Windows runs the core against the test
  layer only.
- `CrashFs` (tests): records every write, link and fsync; at an injected crash point it
  rebuilds the directory tree under **P** (process crash: everything written survives) or
  under **M** (machine crash: each un-fsynced file or link independently survives whole or
  is lost, and an un-fsynced index tail may be partly written), and enumerates **every**
  permitted outcome. This is §D-3.8's "test file layer"; without it the M rows block
  completion. It validates the algorithm under its model only; the platform assumptions
  stay `UNVERIFIED_EXTERNAL_ASSUMPTION`.
- `Clock` callable returning an aware UTC instant, floored to the second by the store;
  tests inject a scripted clock, including advances at every step inside an append or a
  finish (T-S1, T-S2).
- **Sealed create** (§D-3.7): `write_temp`, `fsync_file`, `link_noreplace`, `fsync_dir`.
  An existing name with equal bytes is reused where Annex D says so (attestation, outbox
  is the publisher's); otherwise an existing name is a refusal.
- **`L_store`**: the store's own lock file, held by one store operation at a time; the
  worker, signer and publisher never hold it (they call the store). Instrumented in tests
  (T-S3: raises if `write_bundle` or a non-finish sealed create acquires it).
- **Durable before use**: a helper every `L_store` operation calls after its lookups and
  before any answer, append, create, bar or permit: fsync the index, the index directory
  and the sealed directory. An fsync error is a §26 stop.
- **§26 stop** **[DESIGN] D-5** (ST1-A-2): on a stop condition the store (1) sets an
  in-process stop at once, so this process serves nothing more; (2) tries to persist a stop
  marker (sealed create of `stop.<n>.json` with the cause; the reader projection never
  shows it); (3) exits with a fixed exit code (`EXIT_STOP = 26`) whether or not (2)
  succeeded. On start, a marker without a later human clearance record makes every
  operation answer `STOPPED` (§D-2.8). The supervisor must not restart the store after exit
  26 (**deployment obligation**, e.g. systemd `RestartPreventExitStatus=26`; checked in the
  access-tooling build). **Limit, stated:** if the marker cannot be persisted and the
  machine then crashes and reboots, the stop is lost; the durable state is then one of the
  crash-row outcomes (rows 2 and 4: a line survived whole, was lost, or is partial, which
  is itself a stop), all of which Annex D already defines. Nothing can block across a lost
  marker and a reboot; the residual is disclosed with R3. Tests: a fault injected at each
  step of the marker's persistence (temp write, fsync, link, directory fsync): no further
  operation served in that process, exit 26; restart with the marker: `STOPPED` for bars,
  releases, permits and every other operation until clearance; restart without the marker
  under M: the state is one of rows 2/4. Who clears a stop and through which view is
  **[OWNER]/S4** (the reconciler, §D-2.3; §D-3.9).

## 4. Operations

Each row: caller role, lock, the Annex D or module text it implements, slice (§6).

### 4.1 Confirmation side (6b `Store` obligations; DESIGN_SLICE6B §12) (ST1-A-3)

Every obligation of the `c2_confirmation.Store` docstring and 6b §12, with its operation or
owning build, and its test (slice S2 unless stated).

| Obligation (source) | Operation or owner | Test |
|---|---|---|
| Ledger identity: one ledger path per cycle on one host; never replaced or forked after the declared anchor (Store "Ledger") | the store configuration holds the cycle's ledger path and the declaration's anchor `(head_hash, entry_count)`; every cycle-ledger read (§1.1) checks the anchor at `entry_count` and that every entry the store saw before is still there unchanged (it records `(count, head_hash)` of its last read); anything else is a §26 stop | a replaced file, a truncated file, a different prefix, a second path for the same cycle: each a stop |
| Runner: `start_attempt` and outcome writes under the look lock, then the append lock; eligibility checks (no look, closing, termination; attempt state) inside the same locked operation; never a `completed` outcome for an attempt with a result entry (Store "Runner") | `runner.start(trial_id)`, `runner.finish(attempt_id, crash_code)` | after a look, closing or termination: refused, nothing written; outcome on an attempt with a result entry: refused; two runners racing: one write |
| One `evaluate_trial` process per `attempt_id`; a process that ends with no result entry gets its crash outcome before anything else starts for that trial (Store "Runner"; 6b §3 residual) | the runner's process table (attempt to process), launch and reap | second launch of one attempt refused; exit without a result: crash outcome written before the next start |
| Launch route: each process calls `start` itself and passes its own `Started` (R14B6F-F-8) | the runner launches the module entry point as a fresh process with the C2 bytes; it never builds or passes a `Started` | the launch arguments contain no `Started`; a source check that `aqt.store` never imports `calibration` (D-2) |
| `persist(evaluation, sealing, artifacts)`: durable before returning; raises otherwise (Store "persist", 6b §12) | sealed create of each exact byte string | a fault at each step raises and nothing is reported stored; byte-exact read-back |
| Termination entries on human action (SPEC §5 invalidation, pre-pick termination) and `LOOK_WITHOUT_RECORD` (Store "Termination") | `append_termination` (owner command role) under the look lock; `LOOK_WITHOUT_RECORD` when a look entry has no closing entry **[OWNER]** B-3 | appended once; an unknown cycle refused; `LOOK_WITHOUT_RECORD` only with a look and no closing entry |
| Release of evaluation and sealing records, prediction artifact and nominee inventory only under the closing condition (Store "Release", 6b §12) | `c2_records(cycle, family)`, used by `begin_read`'s entitlement and the reader, after §1.1 | 6b §12's four required tests |
| Read gate: only the cycle's composite manifest and whole BTC and ETH exploration and confirmation partitions, to module processes (Store "Read gate") | `confirmation_read(cycle)` for the module role | another partition, another cycle, a non-module role: refused |
| Capture: the record is kept with its payload bytes (Store "Capture") | sealed create at cycle setup | byte-exact read-back. **That it is genuine and the earliest capture is the external verifier's** (6b §2 residual); no synthetic test can show it |
| Declaration builder: before posting, the declaration meets `parse_declaration`'s rules and every (K_f, T) has frozen thresholds (Store "Declaration builder") | **cycle-setup preflight tool** `scripts/c2_preflight.py` (not the store service; it may import `calibration`): runs `parse_declaration`, `check_eligibility`, `check_declaration`, `qualification_checks` on the candidate declaration and object, and `signed_c2` on the candidate signed C2 bytes (the F-11 pre-signing step) | each refusal reproduced; a valid candidate passes |

### 4.2 Lockbox read side (§D-3.7; `c2_lockbox.Store`)

| Operation | Caller | Lock | Slice |
|---|---|---|---|
| startup and reconciliation | store | `L_store` | S3 |
| `append_startup(record)` → `startup_check_id` | worker | sealed create, no lock | S3 |
| `record_pre_read_check(record)` (deadline C, one per evaluation) | worker | start check against C | S3 |
| `begin_read(evaluation_id)` steps 1-9 (index damage, reconciliation, cap, entitlement incl. the C2 release condition of 4.1, lineage before budget, budget, order and cooldown, `r0`, DEFAULT and nonce, append under the time rule) | publisher | `L_store` | S3 |
| `open_read` → `ReadSession.read()` (gate check under `L_store`; bars over `[S_pre, L1)` under the cycle's manifest, each under the start check against `D*`; nothing after C) | worker | gate check only | S3 |
| `write_bundle` (adds `operational`, commits) | worker | none | S3 |
| `mark_finished` steps 1-4 with 2a | worker | steps 2-4 | S3 |

### 4.3 Release side (§D-2.4..§D-2.8)

| Operation | Caller | Slice |
|---|---|---|
| `release(evaluation_id)` | publisher | S4 |
| `record_delivery(evaluation_id, kind, hash)` incl. ATTESTATION effectiveness | publisher | S4 |
| `sign_permit(evaluation_id)` (VOID on CAP or REVISION) | publisher, for the signer | S4 |
| sealed create of the attestation file | signer | S4 |
| `append_revision(kind, at)` | governance action **[OWNER]/S4** | S4 |
| reader rows (projection, response codes, cycle report and pending-list data) | reader, owner command, publisher | S4 |
| `verify_replay(evaluation_id, projection_bytes)` | replay | S4 |
| `promotion_evidence(evaluation_id)`: under `L_store` after the fsyncs, the facts §D-2.7's guard needs (ATTESTATION delivery entry present, or VOID; `cooling_off_start` = the RESULT `delivered_at`; C; the store-clock reading) | promotion gate | S4 |

**Promotion guard (ST1-A-4).** The guard itself (accept an owner decision at `t_dec` only
if the certificate is effective, `cooling_off_start + 259,200 ≤ t_dec` and `t_dec ≤ C`) and
TC-7 belong to the **promotion gate**, a separate §16 enumerated build, not the store.
`guard_state` no longer exists (option C rev 5 item 6). The store's part is
`promotion_evidence` and its tests: correct facts before and after an ATTESTATION entry, a
VOID, and C. Where the decision is recorded is **[OWNER]/S4** (ST-O-8).

### 4.4 Identities (§D-3.6) **[DESIGN] D-6**

A local Unix-domain socket; the store reads the caller's uid with `SO_PEERCRED` and maps
it to one role (`publisher`, `lockbox_eval` worker and signer, `replay`, `reader`, owner
command, plus the runner and module processes for the cycle ledger operations of 4.1). An
unmapped caller is refused and logged. The core takes the role as an argument, so every
role-by-operation refusal is tested without sockets; the transport is a thin layer tested
on Linux in CI. Which accounts exist and on which host is **[OWNER]/S4**.

## 5. Tests (synthetic data only) (ST1-A-5)

The effective list is §D-3.8's (it replaces the cited proposals' lists). Each test runs
against `CrashFs` and a scripted clock; no test measures timing.

| Group | Effective content (source) | Slice |
|---|---|---|
| begin_read | the 13 cases of §D-3.8 (rev 3 l.253-257, rev 4 l.147-155, rev 6's cooldown boundary, rev 5's cap order) | S3 |
| T-S1 (as replaced) | `begin_read` at `t1 = C − 1` accepted, at `C` refused with nothing written; the clock advanced past C at each point inside the append: the entry counts; an injected write, flush or fsync error: §26 stop, nothing served | S3 |
| T-S1 cross-operation half | concurrent reader-row, `release` (at or after `R_0`), `sign_permit` and `begin_read` wait for the append and answer from the durable state (C5 item 2) | S4 |
| T-S2 (as replaced) | `t_f = D* − 1` counts, `t_f = D*` refused, for `D* = R_0 − 43,200` and `D* = C`; a second `mark_finished` refused; `write_bundle` after `D*` accepted as bytes and never counts; the bar and `record_pre_read_check` start checks | S3 |
| T-S2 release half | a concurrent `release` before `R_0` refused (`STOPPED`); at or after `R_0` it waits for the finish's hold and shows its result (OC rev 3 item 6) | S4 |
| T-S4 | rev 8 rows 1-9, 11, 12 under P and M, plus the interleaving test and its run against the wrong order (which must fail) | S3 |
| T-S6 (as replaced) | release entry and RESULT delivery file: one fixed shape for every FAIL cause; shared fields agree | S4 |
| TC-1..TC-6 (store side) | TC-1 (store part), TC-2, TC-3 (store part), TC-4 with the OC rev 3 and rev 5 additions, TC-5, TC-6 as replaced (no pre-read entry gives `STOPPED`, a terminated-cycle ID is served; codes and precedence; injected exceptions give `STOPPED`); publisher and signer doubles | S4 |
| TC-7 | the promotion gate's (§4.3); the store tests `promotion_evidence` | S4 (evidence only) |
| Option C crash rows | C1-C11 (OC rev 2) and C12-C15 (OC rev 3: an effectiveness check before C made durable after C; an M crash after a whole un-fsynced ATTESTATION entry with recovery after C; `sign_permit` at or after C or after a revision; a revision before `R_0`) | S4 |
| D-12 T-1..T-8 | only through option C's crosswalk (T-4 and T-7 deleted; the rest replaced by rows above) | — |
| B1 roles | an unmapped account refused; each role refused each operation outside its row; the signer refuses without, or against, a store `sign_permit`; the compromise reconciliation's three cases (store-records side) | S5 (roles), S4 (permit) |
| B4.2 bundles, B4.4 replay | byte-exact bundles per kind incl. the PASS fixture (1,053 bytes, `d64d228b…ba520`); replay MATCH and MISMATCH cases | S3 (bundles), S4 (replay) |
| Confirmation side | §4.1's tests, incl. 6b §12's four release tests | S2 |
| Two-ledger handoff, §26 stop | §1.1's two tests; D-5's fault-injection tests | S2 (handoff), S1 (stop) |

Rev 8 T-S3 and T-S5 and rows 10 and 13 are not in §D-3.8's effective list and are not
built; their content is covered by T-S2, TC-2 and the release half above.

## 6. Build slices

| Slice | Content | Gate |
|---|---|---|
| S1 | `Fs`, `PosixFs`, `CrashFs`, clock, sealed create, `L_store`, durable-before-use, §26 stop (D-5) and its tests, the index writer (byte-identical to `append_entry`), `scan_bytes`, import contracts | Astra review |
| S2 | confirmation side (§1.1, §4.1), the preflight tool, their tests | Astra review |
| S3 | lockbox read side (§4.2) and the S3 rows of §5 | Astra review |
| S4 | release side (§4.3), `promotion_evidence`, and the S4 rows of §5 | Astra review |
| S5 | identities and transport (§4.4), B1 role tests | Astra review |
| final | the whole store: final review (the owner sends it to Fable), owner §16 PR review | owner |

Each slice ends with pytest, ruff, mypy, lint-imports and the task-gate review, and records
its reviews per AGENTS.md. S3 needs only S1 and S2's `c2_records`; cross-operation
assertions wait for S4.

## 7. Owner and S4 items

| ID | Item |
|---|---|
| ST-O-1 | Host and OS of the store (this design assumes Linux: `SO_PEERCRED`, directory fsync). |
| ST-O-2 | The clock source and the R3 assumption (no backward step, no forward jump), §D-3.9. |
| ST-O-3 | Who clears a §26 stop, through which view (the reconciler, §D-2.3 S4 gate). |
| ST-O-4 | The governance action that appends revision and invalidation entries. |
| ST-O-5 | C is bound once the look exists: `C = min(A + 255 d, recorded look + 75 d)`, written into the store configuration at the look and never changed; recovery reuses the recorded value (Astra agreed with this reading). The initial configuration (ledger path, anchor, manifest hash, uid map) is written at cycle setup. Who performs both writes: **[OWNER]/S4**. |
| ST-O-6 | B-3 (6b, still open): the `LOOK_WITHOUT_RECORD` reading and how such a cycle counts. |
| ST-O-7 | Accept D-1 (two ledgers, with §1.1's handoff), D-3 (`scan_bytes` added to `aqt.core.ledger`) and D-7 (lock order). |
| ST-O-8 | The promotion gate build: where an owner promotion decision is recorded, and that it reads `promotion_evidence` (§4.3). |
| ST-O-9 | D-5's deployment obligation (no automatic restart after exit 26) and the disclosed limit of a lost stop marker across a reboot. |

## 8. Not decided here

Publisher, signer, owner command and access tooling builds; deployment; the P-5
availability log is deleted by option C (T-7 deleted, §D-3.8) and is not built.
