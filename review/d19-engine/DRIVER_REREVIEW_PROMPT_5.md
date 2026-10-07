You are an independent, adversarial code reviewer (Codex GPT-6, different model from the implementer, Claude Opus 5.5). Read-only: do not edit or commit; no network.

Status: READY FOR HUMAN RELAY; NOT SENT.

Repository in your working directory, branch `review/d19-driver-claude-8936859`. Review the repairs after your ACCEPT at 8936859: `git diff 4f15402 HEAD -- calibration scripts tests`. Findings repaired: FD-1/CRD-1, FD-2/CRD-2, FD-4/CRD-3, FD-6. Findings left unrepaired, with reasons: FD-3, FD-5, CRD-4. Sources:
- `review/d19-engine/CLAUDE_REVIEW_DRIVER_8936859.md` and `FABLE_REVIEW_DRIVER_8936859.md` (the findings);
- `review/d19-engine/REPAIRS_DRIVER_8936859.md` (adjudication, validation, mutation results).

Spec: `git show origin/docs/d19-recommendation:review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md` §8 and §13 rev 7g, items 4 and 6.

Check:
0. Is FD-1 repaired?
   - Is `fast.mean_var` now bit-identical to `dsr._mean_var` and to production on every runtime, including Linux AVX-512?
   - Is `self_check` meaningful, i.e. not tautological?
   - Do recording (`gating`) and every start (`start_gate`) refuse when it fails?
   - Does anything else in `fast`, `dsr` method V or `gates` still depend on NumPy operations that are not the reference's operations?
1. `run_all` (FD-2):
   - Does at most one job per worker reach the pool?
   - Is the first exception raised as soon as the other running job ends?
   - Are heads returned in job order?
   - Does a killed worker still give `BrokenProcessPool` promptly?
   - Can a job be lost or run twice?
2. `lock` (FD-4):
   - Is the lock taken before any worker starts and held until the pool ends?
   - Is it released on crash?
   - Is the Windows `msvcrt.locking` branch correct (byte 0, a file opened `a+b`, LK_NBLCK)?
   - Can `.lock` collide with chunk-chain stray checks?
3. FD-6: is the error handling complete, and is the bytecode directory cleanup safe in spawn workers?
4. Would each new test fail if its property were broken? Mutation results are claimed in the repairs record; verify them.
5. Are R3-3, FE-5 and R6-1 still met? Can the threshold driver still be accepted (pilot runs only; qualification refused)?

You may run read-only Python with `.venv/Scripts/python.exe`, writing only to a temp directory.

Output:
- first line "Reviewer model: <model id>";
- then the verdict, ACCEPT or FIX;
- then findings DR6-1, DR6-2, ..., each with severity, file:line, failure scenario and minimal repair.

Be concise.
