# GPT-6 Sol re-review of the D-19 engine at c889a48

- Prompt: `review/d19-engine/REREVIEW_PROMPT_C889A48.md`.
- CLI metadata: codex exec, model: gpt-6-sol, reasoning effort: high, sandbox: read-only, session 01a10c05-9e71-7b30-bd7b-ec6fa431ea5d, 145,248 tokens.
- Verdict FIX (R5-1, R5-2). Final answer verbatim:

---

Reviewer model: GPT-6 (exact variant not exposed)  
FIX

**R5-1 — MAJOR — `calibration/rundef.py:189–200`.** R4-1’s `sys.prefix` exclusion skips *every* module in the virtual environment, including an `aqt` or `calibration` module absent from the code hash. A read-only check confirmed that such a module is neither reported nor hashed. A worker could pass `start_gate` while executing it. Exclude only runtime dependencies covered by the pinned runtime, and always check loaded engine modules against the hashed inventory. Add a regression test for an engine module under `sys.prefix`.

**R5-2 — MAJOR — `scripts/d19_run_definition.py:93–121`.** R4-2 prevents replacement refs and detects HEAD movement, but `record` does not recheck the working files before writing. If an engine file changes after `_checkout_problem` and before `generator_sha256`, the record can name commit A while hashing and later running different code B. Recompare the final inventory with the captured commit immediately before writing.

The `u_g` rewrite preserves aa3457b’s eager gate evaluation and first unavailable reason; tracing does not change the availability comparisons. POSIX inventory paths and LF/CRLF normalization make the code hash stable across the stated checkout differences. Each new test would fail if its targeted R4 repair were reverted, but neither tests the `sys.prefix` bypass or the recording race. R3-3, FE-4, FE-5 and FE-7 remain driver requirements. Focused pytest could not start because the read-only environment has no writable temporary directory.
