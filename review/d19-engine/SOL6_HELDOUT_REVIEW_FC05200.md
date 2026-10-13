# §16 different-model review of the held-out runner at fc05200

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a133bf-a0e4-7fd0-aee0-cae1305e328f)
- Date: 2026-10-13
- Reviewed: `git diff main...d19-heldout` at fc05200 (scripts/d19_heldout.py, tests/unit/test_calibration_heldout.py), prompt `review/d19-engine/HELDOUT_REVIEW_PROMPT.md` with the diff appended
- Limitation (the reviewer's own): its local shell failed to start, so it reviewed the supplied diff only and could not read the governing text or the reused helpers, nor rerun checks. It also writes that its model metadata was unavailable to it; the CLI header above records gpt-6-sol.
- Findings: HO-R1 (blocking), HO-R2 (blocking). Readings: HO-1 unconfirmed, HO-2 amend, HO-3 reject, HO-4 accept as an external procedure. Verdict: CHANGES REQUESTED.
- The reviewer's final output follows verbatim.

---

## Findings

**HO-R1 — Blocking — an attempt can mix seed anchors.** In `scripts/d19_heldout.py:184–194`, `attempt_record` uses a check-then-write sequence with a shared temporary filename. Two `run` processes can both see no record, write different beacon inputs, and proceed with different anchors. A partial chain can also be resumed under another anchor if `attempt.json` is lost. At `:374–382`, `certify` verifies chains bound to the qualification object hash but never reads the attempt record or checks an anchor binding. **Repair:** create the attempt record atomically, bind the anchor to every chain, and make `certify` refuse a missing or mismatched binding before reduction.

**HO-R2 — Blocking — required tests can be omitted from an accepted certification.** At `scripts/d19_heldout.py:300–317`, `tally` checks only that `len(report["tests"]) == report["m"]`. It marks any test whose unit is missing from `reps` as `run: false`, without establishing that the cell was demoted. A frozen object with an omitted test and correspondingly reduced `m`, or a missing qualifying unit while another unit passes, can therefore produce `accepted: true`. The gate at `:143–150` checks allocation but does not reconstruct the full test manifest. **Repair:** validate `tests` and `m` against `choices.test_manifest` for the full cell manifest; then require every test of every qualifying cell to have replications and refuse a missing one. Continue to report demoted cells as uncertified.

## Proposed readings

| Reading | Decision | Reason |
|---|---|---|
| HO-1 | **Unconfirmed** | The runner checks the driver and its own bytes and calls the engine and runtime gates. I could not inspect `mapping.check_engine`, `mapping.check_runtime`, or `rundef.bytecode_problem`, so I cannot attest to the complete loaded-code and worker-gate claim. |
| HO-2 | **Amend** | Using the full candidate test count for `0.025/M` and leaving demoted cells uncertified is the right shape. The runner must verify that the object’s `tests` and `m` actually are that full manifest; HO-R2. |
| HO-3 | **Reject** | A write-once attempt file does not bind chunks to the anchor and has a concurrent-start race; HO-R1. |
| HO-4 | **Accept as a stated external procedure, not as verified compliance** | The CLI accepts caller-supplied round and randomness. This review provides no evidence that the launcher performed the drand, timing, freeze-read, and DF5-2 checks. |

The visible `replication` path derives one outer seed per replication and passes that seed into the reused family record; it does not visibly change the development family seed. `frozen_reps` selects the frozen block rule, and `tally` uses the frozen `z_crit` with the reused predicates, including the joint “either family” events. The visible `certify` flow calls `chunks.verify` for every planned chain before calling `frozen_reps`. These observations remain conditional on the reused functions’ behavior.

**Verdict: CHANGES REQUESTED.** The local command runner failed before starting any process, so I could not read the governing files or reused helpers, independently verify commit `fc05200`, or rerun the reported checks. Actual reviewer model metadata was unavailable, so I cannot attest that this review fulfills §16’s different-model requirement. No files were edited.
