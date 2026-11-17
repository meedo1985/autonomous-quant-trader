# Adjudication of the Astra review of the store design rev 1 at 1633831

- Review record: `ASTRA_DESIGN_STORE_REV1_1633831.md` (committed `644558a`, verbatim),
  Codex CLI `gpt-6-astra` (log header), verdict FIX, findings ST1-A-1..5.
- Author and adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-17. The adjudicator
  is the author: these are the author's decisions, not an independent check. Repairs are
  in `DESIGN_STORE.md` rev 2.

| ID | Decision | Repair (rev 2) |
|---|---|---|
| ST1-A-1 (blocker) | Accepted | New §1.1: the store reads cycle-ledger facts only while holding the cycle's look lock (all cycle-ledger writers append under it), verifies, fsyncs the cycle-ledger file and directory, then uses them. Lock order D-7 (`L_store`, look lock, append lock; writers never take `L_store`). Two tests: a writer stalled before fsync; a crashed writer's complete un-fsynced closing line. Two ledgers (D-1) kept. |
| ST1-A-2 (blocker) | Accepted with a stated limit | D-5 rewritten: in-process stop at once, marker persistence attempted, exit 26 whatever happens, supervisor must not restart after 26 (deployment obligation, ST-O-9), fault injection at every marker step, `STOPPED` for every operation while a marker stands. **Limit (not repaired, cannot be):** a marker that cannot be persisted, followed by a machine crash and reboot, is lost; the durable state is then one of crash rows 2 and 4, which Annex D already defines (row 4 is itself a stop). Astra's "remain blocked until human clearance" cannot hold across a lost marker and a reboot by any store-side mechanism; the residual is disclosed. |
| ST1-A-3 (blocker) | Accepted | §4.1 is now an obligation-to-operation-to-test table covering every line of the `c2_confirmation.Store` docstring and 6b §12: ledger identity (anchor and seen-prefix check, else §26 stop), runner, one process per attempt, launch route, persist, termination, release, read gate, capture (genuineness and earliest-capture assigned to the external verifier), and the declaration builder assigned to a cycle-setup preflight tool `scripts/c2_preflight.py`, which also carries the F-11 pre-signing `signed_c2` check. |
| ST1-A-4 (blocker) | Accepted | Verified that `guard_state` was removed (option C rev 5 item 6). The guard and TC-7 are assigned to the promotion gate (a separate §16 enumerated build); the store adds `promotion_evidence(evaluation_id)` with its tests. Where an owner decision is recorded: ST-O-8. |
| ST1-A-5 (non-blocking) | Accepted | §5 now enumerates the effective tests and crash rows per slice from §D-3.8 (T-S1 and T-S2 split into read-side halves in S3 and cross-operation halves in S4; rows 1-9, 11, 12 and C1-C15 listed; rev 8 T-S3, T-S5, rows 10 and 13 named as not effective). |

Astra's other conclusions are noted: D-2, D-3, D-4, D-6 compatible at design level; the
lookup-fsync-use order and `L_store` scope match Annex D; ST-O-5's reading of C is right
(rev 2 states it).

No finding was rejected. Rev 2 goes to an Astra re-check.
