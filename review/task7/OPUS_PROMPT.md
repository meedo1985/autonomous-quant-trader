You are implementing Task 7 in the trusted repository
D:\PMP-programs-for-sharawi\autonomous-quant-trader. Work directly in the
current checkout. Read AGENTS.md, review/task7/AUTHORIZED_SPEC.md, the frozen
Constitution/protocol/specifications, and all accepted Task 6 files before
editing.

Implement the smallest complete independent NumPy float64 reference and its
comparison tests required by AUTHORIZED_SPEC.md. Keep the reference test/
research-only; do not import src/aqt and do not create a production backtester.
The reference must distinguish requested target exposure from actual held
weight, clip targets to [0,1], drift fractional actual weight between trades,
hold forbidden intraday/min-hold increases as Task 5 does, execute eligible
reductions and scheduled increases at the next open, charge absolute turnover
cost before the following return, and preserve the accepted additive and
compounded diagnostics. Reuse no implementation code from the exact Task 6
kernel except test fixtures/expected values; comparisons may import both.

Use a deterministic synthetic fixture matrix covering binary identities,
fractional drift, adverse drift HOLD, clipping, exact 10pp boundary, scheduled
increase, cost stress, and a causal/leakage-safe path. Derive/document the
float64 comparison bound from machine epsilon and operation count. If a
scientific policy is genuinely unbound, record it in the Task 7 report instead
of silently choosing it. Add no NumPy dependency unless the project already
provides one; if it must be added, explain why and keep scope minimal.

Before finishing, run focused and full tests, Ruff check/format, mypy, import
contracts, git diff --check, and the read-only frozen audit. Inspect every
changed and untracked file. Do not modify any file under docs/, protocols/,
schemas/, specs/, FROZEN_HASHES.json, or the accepted Task 6 tests/canaries or
hash manifest. Do not commit, push, or start Task 8. Write a complete
review/task7/LOCAL_REPORT.md with exact commands, exits, evidence, assumptions,
and remaining human decisions. Return a concise summary with changed files and
validation results.
