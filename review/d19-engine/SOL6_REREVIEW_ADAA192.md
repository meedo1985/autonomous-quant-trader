# GPT-6 Sol re-review of the D-19 engine at adaa192

- Prompt: `review/d19-engine/REREVIEW_PROMPT_ADAA192.md`.
- CLI metadata: codex exec, model: gpt-6-sol, reasoning effort: high, sandbox: read-only, session 01a10bf4-870d-7f81-9f09-1a6045a0965d, 80,986 tokens.
- Verdict FIX (R4-1, R4-2). Final answer verbatim:

---

Reviewer model: GPT-6 (exact variant not exposed)  
FIX

R3-1 and R3-4 are repaired. R3-2 closes the unhashed entry-script case, but the code inventory still has a gap. Deferring R3-3, FE-4, FE-5 and FE-7 to the driver and re-pilot is acceptable **only if no full run starts before those requirements pass review**. The `u_g` rewrite preserves the earlier eager gate outcomes; tracing does not change availability decisions. LF/CRLF normalization and POSIX inventory paths make the code hash stable across the stated checkout difference.

- **R4-1 — MAJOR — [rundef.py:145](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/rundef.py:145), [rundef.py:181](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/rundef.py:181):** A worker can load `calibration/extra/worker.py` from inside the checkout. `is_code` excludes it from the hash, while `loaded_outside` accepts its location. I confirmed both predicates in a read-only Python check. An imported script helper is likewise outside the module check. **Repair:** hash all executable engine modules and reject loaded module paths absent from that inventory; test a nested helper added after recording.

- **R4-2 — MAJOR — [d19_run_definition.py:49](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_run_definition.py:49):** A local Git replacement ref can make `ls-tree HEAD` and `show HEAD:path` read a replacement tree while `rev-parse HEAD` retains the original commit ID. A working tree matching that replacement can be recorded under an engine commit that cannot reconstruct it; preregistration reads have the same exposure. Separate `HEAD` reads also allow movement during recording. **Repair:** disable replacement objects for these Git calls, use the captured full commit ID for every blob read, and reject HEAD movement before writing. Add a replacement-ref regression test.

Each new test would fail on the specific R3 repair it targets; none covers R4-1 or R4-2. The focused pytest command could not start because this read-only sandbox has no writable temporary directory. No repository files were changed.
