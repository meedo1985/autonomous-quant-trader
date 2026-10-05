You are an independent, adversarial code reviewer (different model from the implementer, Claude Opus 5.5). Read-only: do not edit or commit; no network.

Repository in your working directory, branch d19-calibration-engine, HEAD adaa192 (plus this prompt file).
Spec: `git show origin/docs/d19-recommendation:review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md` section 13 (rev 7g), items 4 and 6.
Prior reviews and adjudications: review/d19-engine/CODEX_REVIEW_2E77F45.md, ADJUDICATION_2E77F45.md, FABLE_REVIEW_AA3457B.md, ADJUDICATION_AA3457B.md, SOL_REREVIEW_C8942DB.md, ADJUDICATION_C8942DB.md, SOL6_REREVIEW_90C64DF.md, ADJUDICATION_90C64DF.md.

Check `git diff 90c64df adaa192 -- calibration scripts tests`:
1. Are R3-1, R3-2 and R3-4 repaired as ADJUDICATION_90C64DF.md claims? Is carrying R3-3, FE-4, FE-5, FE-7 as driver requirements (no full run before the driver passes review) acceptable for accepting this run-definition component?
2. New holes: does the gates.u_g short-circuit rewrite change any outcome vs aa3457b? Does the trace change any availability logic? Is the code hash deterministic across processes/OS (path separators, line endings: note the repo has CRLF conversion on Windows checkouts)? Can `record` be fooled about HEAD/clean tree? Any way a chunk runs on mismatched code or runtime?
3. Would each new test fail if its repair were reverted?

You may run read-only Python with `.venv/Scripts/python.exe` (set OPENBLAS_NUM_THREADS=1, OPENBLAS_CORETYPE=Haswell for method V), writing only to a temp dir.

Output: first line "Reviewer model: <model id>", then verdict ACCEPT or FIX, then findings R4-1, R4-2, ... with severity, file:line, failure scenario, minimal repair. Concise.
