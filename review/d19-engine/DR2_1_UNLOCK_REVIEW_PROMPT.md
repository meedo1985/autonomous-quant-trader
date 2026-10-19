# Review prompt: DR2-1 unlock mechanism and qualification cell list (full-run precondition P3)

You are an independent adversarial reviewer working read-only, not an authority. This is a §16 review: the change touches the gate that refuses qualification runs. Everything is attached: the diff `0a2957d..7ac7beb`, the gate record `GATE_DR2_1_UNLOCK.md`, `calibration/rundef.py`, `scripts/d19_run.py`, `scripts/d19_run_definition.py`, the tests, and the build-order decision.

Check:
1. **Refusal holds today:** with `ACCEPTED_PREREG_SHA256 = None`, can any path (CLI, worker, `dev_bounds`, a direct `run_plan` call, a missing or empty hash, case or whitespace variants) admit a qualification manifest? Pilot plans must be unchanged.
2. **One binding value:** is the hash every caller passes the same `prereg_sha256` the run definition records and the DR2-2 seed check uses? Could a worker pass a hash from a different source than the job set-up, so admission and seeds bind different preregistrations?
3. **Cell list:** does `deploy/calibration/qualification-cells.json` equal `grid.manifest(T_C2, PRESCRIBED)` (104 cells, 300,000 threshold, 12,000 dev), and does the test pin it so a drift fails?
4. **Pinning later:** is setting the constant a one-line change that cannot be satisfied by anything other than the accepted preregistration's bytes?
5. **Tests and gate record:** do the tests fail on the old code and on a wrong hash? Is the gate record accurate (462 passed, no frozen file changed)?

Out of scope: the full-run sheet (`FULL_RUN.md`, reviewed separately, ACCEPT at rereview 3) and the engine's statistics.

Verdict ACCEPT or FIX. Findings get stable IDs DR21-Rn with severity, file:line and a concrete failure scenario.
