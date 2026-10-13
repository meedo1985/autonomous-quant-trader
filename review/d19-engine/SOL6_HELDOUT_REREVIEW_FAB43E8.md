# §16 different-model re-review of the held-out runner at fab43e8

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a133ca-2ac4-7542-b70a-fcb3b3a92fd6)
- Date: 2026-10-13
- Reviewed: a self-contained packet (its previous review, the adjudication `ADJUDICATION_HELDOUT_FC05200.md`, prereg §4/§6/§8 excerpts, `git diff main...fab43e8` for scripts and tests, and the reused helpers' source)
- Limitation (the reviewer's own): its local shell failed again, so it reviewed the packet only and gave approximate line numbers.
- Findings: HO2-R1 (blocking), HO2-R2 (blocking). Readings: HO-1 accept, HO-2 reject pending HO2-R1, HO-3 accept with durability open (HO2-R2), HO-4 external procedure. Verdict: CHANGES REQUESTED.
- The reviewer's final output follows verbatim.

---

**Verdict: CHANGES REQUESTED.** The supplied code repairs HO-R1’s anchor-mixing race and HO-R2’s shortened test manifest, but two blocking gaps remain.

| ID | Severity | Finding |
|---|---|---|
| **HO2-R1** | **Blocking** | In `scripts/d19_heldout.py`, `gate` builds the allocation from *present* qualifying rows (around lines 145–155), while `tally` treats `status.get(unit) is None` as nonqualifying (around lines 340–350). With two cells in the full manifest, an omitted `report["cells"]` row for one cell, and a clean 20,000-replication chain for the other, the omitted cell’s tests become `run: false` and the report can say `accepted: true`. Require exactly one valid status row for every manifest unit; refuse missing or unknown statuses before planning or tallying. This is a remaining HO-R2 failure path. |
| **HO2-R2** | **Blocking** | `attempt_record` (around lines 195–220) fsyncs the temporary file but does not sync the newly created directory entry or the hard link to `attempt.json`. A crash after a successful run can leave durable chunks but lose the sole record of the beacon inputs; `certify` then refuses, and the anchor inputs cannot be recovered from the binding hash. Sync directory creation and the published link before starting workers, using the project’s directory-durability routine. |

| Reading | Decision |
|---|---|
| **HO-1** | **Accept on the supplied source.** `check_engine` checks the recorded code inventory, loaded `calibration`/`aqt` sources and bytecode provenance; the runner separately checks `d19_run.py` and itself. `check_runtime` checks the recorded runtime, image digest and reference vectors. |
| **HO-2** | **Reject pending HO2-R1.** `tests` and `m` now match the full cell manifest, but a missing cell status can still suppress required tests. |
| **HO-3** | **Accept the concurrency and binding repair; durability remains open under HO2-R2.** Atomic publication and per-chunk anchor binding prevent the reported mixed-anchor acceptance path. |
| **HO-4** | **External procedure, unverified.** The supplied code does not establish the drand, timing, freeze-read or DF5-2 checks. |

The local shell failed before launching a process, so I could not independently confirm `fab43e8`, read files beyond the packet, run checks, or verify exact line numbers. The two findings use approximate positions in the supplied diff. I also could not read the project review skills or verify reviewer model metadata and §16 compliance. This read-only review made no edits or committed review record.
