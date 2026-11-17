# Store build design, rev 1: the one store serving the confirmation and lockbox modules

- Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-17, branch `store-design` from
  `main` `92e6f52` (PR #84 merged). Not reviewed yet.
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
- **§26 stop** **[DESIGN] D-5**: a persisted stop marker (sealed create of
  `stop.<n>.json` with the cause, which the reader projection never shows). While a marker
  exists without a later human clearance record, every operation answers `STOPPED`
  (§D-2.8) and serves nothing. Who clears it and through which view is **[OWNER]/S4**
  (the reconciler, §D-2.3; §D-3.9).

## 4. Operations

Each row: caller role, lock, the Annex D or module text it implements, slice (§6).

### 4.1 Confirmation side (6b `Store` obligations; DESIGN_SLICE6B §12)

| Operation | Caller | What | Slice |
|---|---|---|---|
| `start_attempt` / `finish_attempt` (runner) | runner (store) | under the look lock, then the append lock: refuse after a look, closing or termination entry; one `evaluate_trial` process per `attempt_id`; a process that ends with no result entry gets its crash outcome before anything else starts for that trial; never a `completed` outcome for an attempt with a result entry | S2 |
| launch route | runner | each module process calls `start` itself and passes its own `Started` (R14B6F-F-8); the runner never builds or reuses one | S2 |
| `persist(evaluation, sealing, artifacts)` | `evaluate_look` | sealed create of the exact bytes; returns only after every directory fsync; raises otherwise | S2 |
| `append_termination(cycle, kind, reason)` | owner action / store | `{cycle_id, kind, reason}` on human action (SPEC §5 invalidation, pre-pick termination), and `LOOK_WITHOUT_RECORD` for a look entry with no closing entry **[OWNER]** (B-3 reading open) | S2 |
| release of C2 records | lockbox `begin_read`, reader | evaluation and sealing records only when the cycle ledger holds this cycle's closing entry whose two hashes equal the stored bytes' and no termination entry; a prediction artifact under the same condition and only if it hashes to the sealing record's `prediction_artifact_sha256`; the nominee inventory `aqt.c2.artifacts.v1` (trial, signal, overlay) served with it under the same condition | S2 |
| confirmation read gate | `evaluate_trial`, `evaluate_look` | only the cycle's composite manifest and whole BTC and ETH exploration and confirmation partitions, to module processes | S2 |
| capture record | store | the earliest qualifying capture record and its archive payload bytes, kept sealed (6b §2.1; B1-D-1) | S2 |

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

### 4.4 Identities (§D-3.6) **[DESIGN] D-6**

A local Unix-domain socket; the store reads the caller's uid with `SO_PEERCRED` and maps
it to one role (`publisher`, `lockbox_eval` worker and signer, `replay`, `reader`, owner
command, plus the runner and module processes for the cycle ledger operations of 4.1). An
unmapped caller is refused and logged. The core takes the role as an argument, so every
role-by-operation refusal is tested without sockets; the transport is a thin layer tested
on Linux in CI. Which accounts exist and on which host is **[OWNER]/S4**.

## 5. Tests (synthetic data only)

All of §D-3.8's list that falls on the store, each against `CrashFs` and a scripted clock:
`begin_read` (the 13 listed cases), T-S1..T-S6 as replaced there, TC-1..TC-7 (store side,
with publisher and signer doubles), crash rows 1-13 and C1-C15 under P and M including the
interleaving test (and its run against the wrong order, which must fail), B1 roles,
B4.2 bundles (PASS fixture 1,053 bytes, SHA-256 `d64d228b…ba520`), B4.4 replay; plus 6b
§12's required release tests (no closing entry → refused; status (a) with the prediction
missing or not matching → refused; after closure a full handoff passes the lockbox's
`_check_items`, `_check_trial` and prediction checks; before closure refused). No test
measures timing. The full row list (C12-C15 are in `_REV3`..`_REV5`) is tabulated in the
S1 build notes before any code, each row mapped to a test name.

## 6. Build slices

| Slice | Content | Gate |
|---|---|---|
| S1 | `Fs`, `PosixFs`, `CrashFs`, clock, sealed create, `L_store`, durable-before-use, §26 stop marker, index writer (byte-identical to `append_entry`), `scan_bytes`, import contracts, the row-to-test table | Astra review |
| S2 | confirmation side (4.1) and 6b §12's release tests | Astra review |
| S3 | lockbox read side (4.2), `begin_read` tests, T-S1..T-S5, rows 1-9, 11, 12 | Astra review |
| S4 | release side (4.3), T-S6, TC-1..TC-7, rows C1-C15 | Astra review |
| S5 | identities and transport (4.4), B1 role tests | Astra review |
| final | whole store: final review (owner sends to Fable), owner §16 PR review | owner |

Each slice ends with pytest, ruff, mypy, lint-imports and the task-gate review, and records
its reviews per AGENTS.md.

## 7. Owner and S4 items

| ID | Item |
|---|---|
| ST-O-1 | Host and OS of the store (this design assumes Linux: `SO_PEERCRED`, directory fsync). |
| ST-O-2 | The clock source and the R3 assumption (no backward step, no forward jump), §D-3.9. |
| ST-O-3 | Who clears a §26 stop, through which view (the reconciler, §D-2.3 S4 gate). |
| ST-O-4 | The governance action that appends revision and invalidation entries. |
| ST-O-5 | Cycle setup: who computes C and writes the store configuration (C from the declaration post's archive time `A` and the look; the look is known only later, so C is written at the look) **[DESIGN reading, to confirm]**. |
| ST-O-6 | B-3 (6b, still open): the `LOOK_WITHOUT_RECORD` reading and how such a cycle counts. |
| ST-O-7 | Accept D-1 (two ledgers) and D-3 (`scan_bytes` added to `aqt.core.ledger`). |

## 8. Not decided here

Publisher, signer, owner command and access tooling builds; deployment; the P-5
availability log is deleted by option C (T-7 deleted, §D-3.8) and is not built.
