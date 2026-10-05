# GPT-6 Sol re-review of the D-19 engine at a1d04e8

- Prompt: `review/d19-engine/REREVIEW_PROMPT_A1D04E8.md`.
- CLI metadata: codex exec, model: gpt-6-sol, reasoning effort: high, sandbox: read-only, session 01a10c13-6bdd-7642-9d01-40999bdbc235, 72,502 tokens.
- Verdict FIX (R6-1, R6-2). Final answer verbatim:

---

Reviewer model: GPT-6 (exact variant not exposed)  
FIX

**R6-1 — BLOCKER — `calibration/rundef.py:193–203, 268–270`.** The gate checks an engine module’s `__file__` and hashes its `.py` source, but Python can execute an unchecked or timestamp-spoofed `.pyc` with different code while `__file__` still names that source. A preloaded altered `calibration.chunks` could pass the gate because the reference vectors do not exercise it. **Repair:** make workers load hashed engine modules from verified source without reusable bytecode caches; add a mismatched-bytecode regression test.

**R6-2 — MAJOR — `scripts/d19_run_definition.py:39–65`.** `_git` inherits `GIT_DIR` and `GIT_WORK_TREE`. They can direct `git -C ROOT` to another repository whose engine files match the working files, causing `record` to accept that repository’s HEAD as this checkout’s. **Repair:** clear repository-override Git environment variables for every Git call and test the override.

R5-1 and R5-2 are repaired for their stated cases; each new test would fail if its corresponding repair were reverted. `u_g` retains the eager gate order and first unavailable reason from `aa3457b`; tracing does not change availability. POSIX inventory paths and CRLF-to-LF hashing make the source hash stable across those checkout differences. R3-3, FE-4, FE-5, and FE-7 remain driver requirements. I could not execute the new tests: the read-only sandbox denied writes to the temporary directory.
