# GPT-6 Sol re-review of the D-19 engine at 90c64df

- Prompt: `review/d19-engine/REREVIEW_PROMPT_90C64DF.md`.
- CLI metadata: codex exec v0.160.0, model: gpt-6-sol, reasoning effort: high, sandbox: read-only, session 01a10be4-e45d-7e13-b25b-df1205da7e91, 84,161 tokens.
- Verdict FIX (R3-1..R3-4). Final answer verbatim:

---

Reviewer model: GPT-6 (exact variant not exposed)  
FIX

RR-1 and RR-4 are repaired. The `u_g` rewrite restores the eager gate order from `aa3457b`; the trace records intermediate values without changing availability comparisons. RR-2, RR-3, and RR-5 remain incomplete:

- **R3-1 — MAJOR — [d19_run_definition.py:91](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_run_definition.py:91):** `record` accepts `--prereg-commit HEAD` and stores `"HEAD"`. After HEAD moves, that field no longer identifies the preregistration commit. Resolve and store the full commit ID before reading its file.
- **R3-2 — MAJOR — [rundef.py:145](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/rundef.py:145), [d19_run_definition.py:44](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_run_definition.py:44):** The HEAD comparison covers only the code inventory. A dirty executable script outside `scripts/d19_*.py` can pass `record` and later serve as a driver. Hash the actual driver and launcher, and make their inclusion a required condition before recording.
- **R3-3 — BLOCKER before a full run — [rundef.py:239](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/rundef.py:239):** `loaded_outside` checks only the process calling `start_gate`. FE-5’s stated call before starting workers does not establish which code each worker imports or executes. Require each worker to pass the gate before computing chunks and build its `Chain` from the definition hash and returned gating identity. FE-4 likewise still requires the launcher to obtain the image digest from host inspection.
- **R3-4 — MINOR — [test_calibration_rundef.py:151](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_calibration_rundef.py:151), [test_calibration_rundef.py:257](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_calibration_rundef.py:257):** The new tests would fail on a full RR-1 or RR-4 revert, but not on every claimed repair revert. Removing the `start_gate` call to `loaded_outside`, excluding a `d19_` script from the inventory, or dropping G-10/G-12 values from the final `reference_vectors()` hash leaves the corresponding helper tests passing. Test those gate and hash outcomes directly.

The focused pytest command could not start: this read-only sandbox has no writable temporary directory. No repository files were changed.
