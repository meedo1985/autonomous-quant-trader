# Sol narrow re-check DS5 of the D-19 preregistration rev 5 at `327aa3d`: READY WITH FIXES

Date: 2026-10-04. This is an R19-2 independent narrow re-check by the different model family. The prompt was the same as Fable DF5's, with the ID prefix `DS5`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a1070b-6e66-7b21-918c-b30e18526fbb`. The final message is reproduced below unchanged.

---

Model: OpenAI Codex, GPT-5 family; exact served identifier unavailable  
Commit: `327aa3d0e06fb5f71206025d392a35e3c14f2088`  
Verdict: **READY WITH FIXES**

| Finding | Status | Note |
|---|---|---|
| DF4-1 | RESOLVED | Mapping now requires one cell-specific region and records matching cell IDs. |
| DF4-2 | PARTIAL | Timing/failure boundary fixed, but `D_Q2` binding contradicts itself; DS5-1. |
| DF4-3 | RESOLVED | Mechanical coverage table and Q2m added. |
| DF4-4 | RESOLVED | Covariance formulas and hourly reconstruction are specified. |
| DF4-5 | RESOLVED | Development and held-out classifier thresholds are distinguished. |
| DF4-6 | PARTIAL | Targets remain numerically correct, but `M_max` omits Q2m; DS5-3. |
| DS4-1 | RESOLVED | Cell-specific mapping implemented. |
| DS4-2 | RESOLVED | Generator formulas and fair independent signs supplied. |
| DS4-3 | RESOLVED | Pre-run void versus post-start failed-attempt boundary is sound. |
| DS4-4 | RESOLVED | Declaration mapping removed from `U_proc^R`. |
| DS4-5 | RESOLVED | OHLC chaining and seed symbol are defined. |

| ID | Severity | Location | Problem | Fix |
|---|---|---|---|---|
| DS5-1 | MAJOR | §4 lines 254, 258 | `D_Q2` is both fixed at preregistration acceptance and fixed later in the attempt-2 record. | Remove `D_Q2` from the acceptance tuple; bind it only in the attempt-2 record before posting. |
| DS5-2 | MINOR | §3.2 line 131 | “Half” t₅ and half Gaussian is undefined for `K=5`; law/scale pairing is also unstated. | Specify deterministic column indices, counts, and law/scale pairing. |
| DS5-3 | MINOR | §5 lines 275–284 | Q2m adds 8 cells and 24 tests: the stated grid becomes 379 cells and `M_max=1,167`, not approximately 1,143. | Update the count and rerun the printed calculation. The quoted τ values and critical counts remain unchanged. |

Not ready for owner acceptance in the committed form; the three narrow paper fixes should be applied and re-checked first. This read-only response is not a committed review record.

Most earlier defects are fixed, including cell-specific mapping and preventing a free retry after held-out work starts.  
Three wording corrections remain: attempt-2 deadline timing, the five-column mixed-law split, and the test count.  
After those corrections, you may decide Q-1 and accept the preregistration, authorizing only the measured pilot before any full run.
