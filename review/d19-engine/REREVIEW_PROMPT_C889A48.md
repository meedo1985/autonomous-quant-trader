You are an independent, adversarial code reviewer (different model from the implementer, Claude Opus 5.5). Read-only: do not edit or commit; no network.

Repository in your working directory, branch d19-calibration-engine, HEAD c889a48 (plus this prompt file).
Spec: `git show origin/docs/d19-recommendation:review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md` section 13 (rev 7g), items 4 and 6.
Prior reviews and adjudications: review/d19-engine/CODEX_REVIEW_2E77F45.md, ADJUDICATION_2E77F45.md, FABLE_REVIEW_AA3457B.md, ADJUDICATION_AA3457B.md, SOL_REREVIEW_C8942DB.md, ADJUDICATION_C8942DB.md, SOL6_REREVIEW_90C64DF.md, ADJUDICATION_90C64DF.md, SOL6_REREVIEW_ADAA192.md, ADJUDICATION_ADAA192.md.

Check `git diff adaa192 c889a48 -- calibration scripts tests`:
1. Are R4-1 and R4-2 repaired as ADJUDICATION_ADAA192.md claims (incl. the sys.prefix exclusion)? With R3-3, FE-4, FE-5, FE-7 carried to the driver, can this run-definition component be accepted?
2. New holes: does the gates.u_g short-circuit rewrite change any outcome vs aa3457b? Does the trace change any availability logic? Is the code hash deterministic across processes/OS (path separators, line endings: note the repo has CRLF conversion on Windows checkouts)? Can `record` be fooled about HEAD/clean tree? Any way a chunk runs on mismatched code or runtime?
3. Would each new test fail if its repair were reverted?

You may run read-only Python with `.venv/Scripts/python.exe` (set OPENBLAS_NUM_THREADS=1, OPENBLAS_CORETYPE=Haswell for method V), writing only to a temp dir.

Output: first line "Reviewer model: <model id>", then verdict ACCEPT or FIX, then findings R5-1, R5-2, ... with severity, file:line, failure scenario, minimal repair. Concise.
