# Sol review DS1 of the D-19 preregistration rev 1 at `aa981d8`: UNSOUND

Date: 2026-10-04. This is an R19-2 independent statistical review by the different model family. The prompt was the same as Fable DF1's, with the ID prefix `DS1`.

Command: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high`. The CLI header records `model: gpt-5.6-sol`, `reasoning effort: high` and session `01a106e3-3475-78a0-8382-1c4714e01b72`. The final message is reproduced below unchanged.

---

Model: OpenAI GPT-5 family, Codex runtime; exact served model identifier is not exposed.  
Commit reviewed: `aa981d88c7222623519a083f885c6f842f860592` on `docs/d19-recommendation`  
Verdict: **UNSOUND**

The high-level development/held-out separation is sensible, and the per-family allocations numerically sum to 0.01. However, the current preregistration cannot certify the stated claim.

| ID | Severity | Location | Problem | Evidence | Required fix |
|---|---|---|---|---|---|
| DS1-1 | BLOCKER | `PREREGISTRATION.md` §3.5; A-B7; Design §4 | No real-data classifier or domination rule. | It explicitly says the real window has “no classifier”; qualitative properties such as short memory and stationarity cannot establish that a simulated cell dominates C2. | Supply a mechanical, declaration-time support/domination rule, or state that calibration is simulation-conditional and cannot authorize C2 promotion. |
| DS1-2 | BLOCKER | §§2, 3.1–3.4, 7 | Most qualifying cells do not define the full joint data needed by route R. | Q1/Q2 specify laws for `X=C−b`, but G-1, G-2, G-4 and G-12 require separate candidate/benchmark legs, equity paths and candidate returns. BTC/ETH joint resampling is also unspecified. | Preregister complete joint generators for BTC, ETH, candidate and benchmark legs, including shared indices, common-factor heteroskedasticity and every gate input. |
| DS1-3 | BLOCKER | §2 versus §3.4 | The semi-empirical cell is not the claimed location-shift null. | §2 requires exactly zero column means; §3.4 estimates and subtracts a pilot mean, tolerating residual mean up to `0.01·sd`. At `T=1247`, that permits an approximate standardized shift of `sqrt(1247)·0.01 = 0.353`. | Construct the null exactly, or freeze an independent pilot and propagate a much tighter uncertainty bound into certification. Bind its seed and artifact before held-out work. |
| DS1-4 | BLOCKER | §§6–7, route S | Route S is both statistically impossible at its stated budget and non-generalizable. | With `N=1000`, zero failures, and `α=0.05/550`, the one-sided CP upper bound is **0.00926**, not ≤0.001; even unadjusted 95% gives 0.00299. “Most resembles” is subjective, and an uncovered strategy is merely disclosed rather than rejected. | Reject route S as written. Evaluate the actual declared strategy, or define an exhaustive mechanically checked class and fail closed outside it. At the stated multiplicity, even zero failures needs roughly 9,300 replications. |
| DS1-5 | MAJOR | §6 | The 40% availability margin arithmetic is false. | At `M=550`, `N=20000`: true `p=.0012` against `.003` passes only **95.34%**, not >99%; true `p=.0004` against `.001` passes only **19.12%**. The error-rate calculation is sound: `p=.018` against `.025` passes about **99.88%**. | Freeze an exact power table and increase `N`, reduce development targets, or reallocate shares. |
| DS1-6 | MAJOR | §§3.2, 3.3, 6, 9 | The cell boundary and confidence family are ambiguous. | If `T_min=365`, Q1 makes `K=80,T=365` qualifying while §3.3 calls it a challenge. The stated 400–550 tests appear to omit the two-family dimension unless “cell” silently includes family. Power and mixed-null designs use unfrozen terms such as “several.” | Produce a disjoint, family-labelled manifest and enumerate every statistical test in `M`; fully specify all power and mixed-null cells. |
| DS1-7 | MAJOR | §§7, 11; Draft gate list | R/D/S do not exhaustively and operationally cover mandatory gates and failure causes. | G-13 is absent. “Complete and finite manifest” does not by itself prove availability of all derived/stressed/model outputs. Cause-level overlap and ownership among routes are undefined. | Add a gate-by-reason matrix covering G-1 through G-14, including frozen N/A cases, with a proof or simulated event for every unavailability cause. |
| DS1-8 | BLOCKER | §§4, 8; Draft R-7 | Held-out seeds are not bound to the frozen qualification object, and the inner seed is not demonstrably the production construction. | The outer seed binds only the preregistration hash, not the development-selected rule, `T_min`, `z_crit`, manifest or generator hashes. The family-seed fields/trials are incomplete, and Draft R-7’s `round` and beacon extension is omitted. | Bind held-out seeds to `qualification_object_sha256`; specify canonical JSON exactly; include every Annex B/R-7 field and domain-separate generator, pilot and inner streams. The dev/held-out namespaces otherwise provide useful separation. |
| DS1-9 | MINOR | §10 | The operation count is plausible, but the runtime estimate is unsupported and likely optimistic. | `10^14` values in 300–1,000 core-hours implies roughly 28–93 million values/core-second despite indexing, multiple matrix passes and deterministic summation. Route S also entails up to hundreds of thousands of reruns/refits. | Benchmark representative maximum and median cells, including G-11/G-14, before requesting compute approval. |

Route assessment: R is acceptable in principle once full joint generators exist. D is acceptable only for narrowly enumerated deterministic conditions with reviewed proofs. S is a certification hole as written. The `0.003 + 0.001 + 0.001` per-family allocation is coherent, but only after the component events are exhaustive and actually certifiable.

Commands run:

- `rtk git rev-parse HEAD`, branch and tracked-only status checks.
- `rtk git show aa981d8:<path>` for all requested records, governing files, owner decisions and applicable skills; targeted `git grep -n`.
- `.venv\Scripts\python.exe -` with an in-memory standard-library binomial/Clopper–Pearson calculation. An initial SciPy attempt failed because SciPy is not installed.
- `rtk git diff --name-only` and cached equivalent: both empty.

No network, edits, commits, untracked-folder enumeration, confirmation data, lockbox data, or `data/` access occurred. Under the repository rule, this relay is not a completed review record until its model metadata and all findings are committed by an authorized party.

Do not accept this preregistration yet.
The largest holes are route S, absent real-data coverage, and incomplete joint-generator and seed bindings.
A revised preregistration can be reviewed without touching confirmation or lockbox data.
