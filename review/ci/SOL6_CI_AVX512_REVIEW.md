<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-12. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a130e3-cd03-7e31-988a-7e382d2ed147. Tokens used: 30,355. Made from a packet built from commit 3962c6c (PR #52): the prompt below, CI_FINDING_XEON_8573C_AMX.md, git diff main 3962c6c, calibration/fast.py lines 1-35 and a note of the local check. -->

> # Review: CI probe marks Intel AVX-512 runners inconclusive
> 
> You are an independent adversarial reviewer working read-only, not an authority. Everything is attached. Check that the change cannot turn a real engine failure into "inconclusive" or a pass, that a green job still always means the engine tests ran and passed, and that the shell/YAML/Python quoting is correct. Verdict ACCEPT or FIX; findings get stable IDs CIA-n with severity and a concrete scenario.
> 

## Review (final message, verbatim)

**Verdict: FIX.**

- **CIA-1 — Medium:** `except RuntimeError` labels any runtime error inside `fast.self_check()` as the known NumPy power mismatch. For example, an unexpected NumPy failure in `_square()` would become “inconclusive,” obscuring a real engine failure. Match the specific expected error and known runner condition; let other errors fail normally.
- **CIA-2 — Medium:** The shell labels *any* exit code 4 from the whole Python command as that mismatch. If `rundef.gating('probe')` exits 4 before `self_check()` runs, CI gives the wrong diagnosis. Emit the inconclusive annotation only from the verified mismatch branch.

Neither issue creates a pass: exit code 4 still fails the probe, and the engine-test step runs only after a successful probe. In the shown workflow, a green job therefore still requires the engine tests to run and pass. The YAML block, shell quoting, and Python `try`/`except` syntax are sound. [GitHub’s workflow documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) confirms that the step status follows the shell’s final exit code.

This was a static, read-only review. The local command runner failed to start, so I could not independently execute the probe or inspect the full checkout.
## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-12)

| ID | Decision | Repair |
|---|---|---|
| CIA-1 Medium | AGREE, repaired | The `except` re-raises unless the message is exactly `NumPy power no longer matches Python ** on this runtime` **and** `/proc/cpuinfo` lists `avx512f`. Any other error fails the probe normally, with its traceback. |
| CIA-2 Medium | AGREE, repaired | The inconclusive annotation is printed by Python, only in that verified branch, before `sys.exit(4)`. The shell no longer labels any exit code 4 as the mismatch. A 4 from anywhere else fails without the label. |

The snippet is compiled locally from the parsed YAML, with no double quote inside the shell string.
