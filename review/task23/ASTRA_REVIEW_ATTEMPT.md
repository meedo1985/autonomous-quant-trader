# Task 23 GPT-6 Astra review attempt

Date: 2026-09-28

Status: **INCOMPLETE — USAGE LIMIT REACHED; NO VERDICT**

## Metadata

- Requested model: exact `gpt-6-astra`, explicitly selected with Codex CLI
  `-m gpt-6-astra`.
- Thread/session ID emitted by the runtime:
  `01a0e70f-835f-7621-9aab-0b346f501d0c`.
- Codex CLI: `0.157.1`.
- Sandbox: read-only; session: ephemeral.
- Base: `edc3b39dd890f5c92c1c7542b7853ae62055b4d2`.
- Head: `7aafb6d984132c6aa73f02077dd3a4ae7d5589a0`.
- The run ended with the Codex usage-limit error before a final finding list or
  verdict. It does **not** satisfy the required Astra review.

## Diagnostic observations preserved from the incomplete run

### T23-A0-01 — FLATTEN step exceeds the owner-set fraction

The reviewer reproduced a 0.155 BTC holding with a 50% step bound. The code
sold 0.155 BTC although the approved maximum was 0.0775 BTC.

### T23-A0-02 — A max-quantity filter reject can end FLATTEN with all exposure

The reviewer reproduced a 300 BTC balance. The first computed step exceeded
`filters.max_qty`, the simulator returned `FILTER_LOT_SIZE`, and the controller
treated it as an unsellable remainder: mode became HALT with all 300 BTC still
held. This observation was not present in the Claude report.

### T23-A0-03 — Later incidents do not invalidate older reconciliation

Read-only probes reproduced both paths:

- HALT at t0, reconciliation t1, incident t2, then override returned RUNNING.
- FREEZE at t0, reconciliation t1, failure t2, then exit returned HALT.

### T23-A0-04 — Incident-write failure is not durable across restart

After a simulated incident-ledger failure, a later clean `startup_check`
returned `start=True`. In-process recovery reached HALT with no open incident,
and normal override then refused the empty incident set.

### T23-A0-05 — L-03 authority conflicts with the branch

The reviewer found that the committed L-03 adoption record says automatic
HALT, while Task 23 maps L-03 to FLATTEN and cites an absent owner-settings
file.

## Checks completed before the limit

- Ruff check: passed.
- Ruff format check: 94 files formatted.
- mypy: no issues in 48 source files.
- Ten selected no-fixture safety/reconciliation tests: passed under a read-only
  audit guard.
- Independent frozen verification: trusted 28-file inventory/bytes, 14
  sidecars, Constitution canonical hash, manifest/protocol/nested bindings all
  passed and matched `origin/main`.

The full required review must be rerun with exact Astra after repairs. Nothing
in this incomplete attempt authorizes merge.
