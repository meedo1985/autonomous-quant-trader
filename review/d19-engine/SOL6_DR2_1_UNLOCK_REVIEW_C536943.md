# Sol review: DR2-1 unlock mechanism at c536943

Reviewer: OpenAI Codex v0.162.1, model `gpt-6-sol`, reasoning effort high, sandbox read-only, session `01a152d0-3e2d-7ff1-8837-6d525b6ec358`, 2026-10-19. Prompt `DR2_1_UNLOCK_REVIEW_PROMPT.md` (c536943). Its shell failed on most calls; it could not rerun tests.

Final answer, verbatim:

codex
**Verdict: FIX.** The unset pin refuses qualification plans on the supplied CLI, worker, `dev_bounds`, and direct `run_plan` paths, including missing, empty, case changed, and whitespace changed hashes. Pilot admission is unchanged. The run paths pass the definition’s `prereg_sha256`, and the worker checks its seed anchor against that value.

- **DR21-R1 — High — [scripts/d19_run.py:254](D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_run.py:254):** After pinning hash `H`, a hand-edited definition can name a preregistration commit whose bytes hash to a different value while asserting `prereg_sha256: H` and `seed_spec` anchored to `H`. The run and start gates accept the asserted value without checking the named commit’s bytes. That permits qualification with false preregistration provenance. Verify the commit’s preregistration bytes against the definition hash before chunks run.
- **DR21-R2 — Medium — [tests/unit/test_calibration_rundef.py:1524](D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_calibration_rundef.py:1524):** The test asserts the pin is `None`. Setting the constant to an accepted hash therefore fails the suite, so the claimed later one-line pin is not currently possible. Test the unset state by temporarily setting the pin to `None`, then test the pinned state separately.

The supplied passing test output supports **462 passed**; the added admission test would fail on the old code and rejects a wrong hash. The cell-list test compares the JSON with `grid.manifest(T_C2, PRESCRIBED)` and pins 104 cells and the stated counts. The supplied diff changes no frozen file. I could not rerun checks because local command execution failed during review. This is read-only feedback; no review record was committed.
