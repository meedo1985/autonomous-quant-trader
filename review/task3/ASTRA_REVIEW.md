# Task 3 — Astra review

Reviewed HEAD: 853cb62b199d0f8f6c3ab5844eba3657285927af
Reviewer: explicitly dispatched gpt-6-astra, high reasoning, independent read-only agent.
Task 4: NOT PRESENT; no reviewable implementation or authorized scope found.
Verdict: LOCAL GATE BLOCKED. No code changes applied by this review.

## Findings

1. BLOCKER — src/aqt/backtest/costs.py:505 (_bars_through). A historical data gap silently discards every earlier observation and restarts volatility initialization once three later bars exist. No frozen reset rule authorizes this. Reproduced with 175 hourly bars, first 170 alternating between 100 and 100*exp(.03), then constant 100; decision at hour174. Complete history: 173 returns, sigma 299.03310481340367 bps, slippage 14.951655240670185 bps. Removing hour170: only 2 returns, sigma 0, slippage 1 bps. Proposed correction: reject unresolved historical gaps; any alternative reset policy needs scientific disposition. Add a regression with sufficient post-gap bars.

2. BLOCKER — src/aqt/backtest/costs.py:395 (resolve_execution). Exported execution resolver accepts daily BarSeries; delay_bars=1 then delays 24h instead of the specified additional 1h. trade_cost later rejects daily inputs, but direct resolver calls do not. Enforce hourly interval at resolver entry and test daily-series rejection.

3. QUESTION blocking scientific sign-off — costs.py:261,310. The uncentered zero-mean EWMA recursion is an unresolved statistical convention. Constant 100 bps returns produce sigma 0 at 168 returns, 6.416678534649073 at 169, and 70.71067811865494 at 336. This demonstrates an interpretation difference, not proof that zero-mean EWMA is wrong. Obtain scientific disposition; do not silently substitute an estimator. Log returns have supporting authority in FEATURE_FACTORY_v1.md (hourly log returns throughout) and are not a separate defect.

4. NON-BLOCKING — CostBreakdown.cost_quote:361. Large finite notional 1e308 with sigma=100 produces inf through intermediate multiplication even though the final cost 1.7e305 is representable. Scale bps before multiplication and reject genuinely nonfinite results; add numeric edge tests.

## Parent-run validation

- .venv/Scripts/pytest.exe -q: exit0, 106 passed.
- .venv/Scripts/ruff.exe check .: exit0.
- .venv/Scripts/ruff.exe format --check .: exit0,22 files formatted.
- .venv/Scripts/mypy.exe src: exit0,18 source files.
- .venv/Scripts/lint-imports.exe: exit0,4 kept,0 broken.
- .venv/Scripts/pre-commit.exe validate-config: exit0.
- git diff --check: exit0.
- verify_task1.py governance() and configuration() invoked via runpy with existing project libraries: exit0; 28 protected files/inventory,14 sidecars,Constitution canonical hash and bindings,five schemas/protocol/rejection controls,hook and CI configuration PASS.
- Full verify_task1.py was not run: its boundaries() rewrites historical boundary-probes.json. Current import contracts were checked independently; historical mutation probes remain unrerun.

Execution note: project .venv/Scripts/python.exe is absent. Existing pytest/ruff/mypy/import-linter launchers work with approved permissions. Governance checks used the existing temporary Python 3.12.10 and .venv/Lib/site-packages. Initial sandbox attempts failed; successful results above are from the approved reruns. No dependency was installed.

Successful tests do not resolve the reproduced gaps. This report is diagnostic evidence, not human approval or a claim that Task3 passes. Task2 independent review is not included in this request.

