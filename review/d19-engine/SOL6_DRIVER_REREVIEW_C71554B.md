# GPT-6 Sol re-review 4 of the D-19 run driver at c71554b

- Prompt: `review/d19-engine/DRIVER_REREVIEW_PROMPT_4.md`.
- CLI metadata: codex exec, model: gpt-6-sol, reasoning effort: high, sandbox: read-only, session 01a10ce3-cf58-7951-944e-c7ab84208c3f, 82,198 tokens.
- Verdict FIX (DR5-1 blocker, DR5-2 non-blocking). Final answer verbatim:

---

Reviewer model: GPT-6 (exact serving model ID unavailable)  
FIX

- **DR5-1 — BLOCKER — [scripts/d19_run.py:99](D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_run.py:99), [scripts/d19_run.py:121](D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_run.py:121).** Preregistration §13 item 6 specifies two workers, but `--workers 8` starts eight on the specified server. Fix the run driver at two workers; update the tests that request one. Pilot acceptance is blocked by this run-rule violation.
- **DR5-2 — NON-BLOCKING — [tests/unit/test_calibration_rundef.py:717](D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_calibration_rundef.py:717).** The DR4-1 test supplies a mismatched hash directly to `worker`. It would still pass if `main` stopped passing the hash of the definition it gated. Test parent-to-worker propagation with a controlled definition replacement.

**DR4-1 and DR4-2 are repaired in code.** In a spawn child, `sys.modules["__main__"]` points to the driver re-executed as `__mp_main__`; its bytecode settings precede engine imports, and `worker` gates before `chunks.run`. The §8 seed, bit-exact diagnostics, K=1 fields, and chain binding check out. Worker failure and malformed input exit without reporting success; a changed replication plan fails binding on resume. Qualification remains refused.

Focused tests **could not start**: this read-only environment has no usable temporary directory.
