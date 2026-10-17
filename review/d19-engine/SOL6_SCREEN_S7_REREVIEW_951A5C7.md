# §16 different-model re-review of the screen slice S7 at 951a5c7

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a1496b-e74f-7570-889f-922749c5d57e)
- Date: 2026-10-17
- Prompt: `SCREEN_S7_REREVIEW_PROMPT.md`
- Findings: S7R-R1, S7R-R2 (High; S7-R1, S7-R2 open for edge cases), S7R-R3, S7R-R4 (Medium). S7-R3..R8 resolved. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for S7 at `951a5c7`.

| ID | Severity | Finding |
|---|---|---|
| **S7R-R1** | High | [The CLI appends the trial directory](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_screen.py:52), but neither it nor [the worker initializer](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py:1877) moves an *existing* entry to the end. If `PYTHONPATH` already puts that directory before site-packages, a trial-supplied `sklearn` or `lightgbm` can still be imported during a model screen. **S7-R1 remains open.** Remove existing occurrences before placing the directory last, and test that case. |
| **S7R-R2** | High | [The declaration compares only `source.identity["manifest_sha256"]`](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py:1956). `HourlySource` accepts caller-supplied arrays and identity, so a direct caller can pair different bars with the expected manifest hashes and, once S8 freezes the float vector, obtain an outcome from those bars. **S7-R2 remains open for direct callers.** Bind the screened arrays to a source rebuilt from the declared manifests; test changed bars with unchanged identity. |
| **S7R-R3** | Medium | [Preloading now calls `load` in the parent](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py:1897), while `code_dir` is added only in [worker setup](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py:1913). A direct `run_screen(..., code_dir=...)` caller whose trial module is absent from its existing `sys.path` fails before any worker starts. The test helper prepends the directory and misses this regression. |
| **S7R-R4** | Medium | [Exclusive creation happens after the entire screen](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_screen.py:69). With an existing output path, all jobs can run before `FileExistsError` prevents a record. Reserve the destination before starting work, while retaining exclusive creation. |

The measurement/declaration split closes **S7-R3**: in the reviewed code, `run_screen` produces no `outcome`, and `declare` calls `check_object` before adding one. The C2 constants match `T_C2 = 1240` and `g = 7`; the exact G-11/G-14 vectors are checked, and declaration correctly refuses while the float vector awaits S8. The 20-trial CLI pilot, stale-code preflight, full listed-manifest check, and atomic no-overwrite operation address **S7-R5 through R8** in their stated narrow cases.

I verified the committed files through the read-only GitHub view. The local shell failed before launch, so I could not run tests or inspect local uncommitted state. This response is read-only; **it is not a committed review record**, which the project requires before treating the review as complete.