Implement Task 8 in D:\PMP-programs-for-sharawi\autonomous-quant-trader using
Claude Opus 5 high effort. Read AGENTS.md, review/task8/AUTHORIZED_SPEC.md, all
frozen governance/specification files relevant to backtesting, the approved
Task 3/5/6 decisions, the existing production bar/cost/benchmark modules, and
the accepted Task 6 and Task 7 artifacts before editing.

Build only the smallest complete production backtester v0 authorized by the
Task 8 specification. Reuse existing production semantics rather than cloning
the oracle/reference. Keep the engine pure, deterministic, typed, and free of
network/filesystem/clock/random/credential access. Preserve complete auditable
segment records. Compare it independently to the frozen exact oracle and NumPy
reference on synthetic fixtures. Never edit the accepted oracle/canary or
reference files.

If the delay-stress interaction with exposure scheduling is not fully bound,
do not invent it: finish the baseline engine, document the precise unresolved
question, and exclude only that unbound behavior. Do not implement Task 9 or
any strategy, validation, governor, executor, exchange, or live path.

Before finishing, run every check required by AUTHORIZED_SPEC.md and write
`review/task8/LOCAL_REPORT.md` with exact commands, exits, environment, hashes,
scope, assumptions, and blockers. Inspect all changed/untracked files. Do not
commit or push. Return a concise completion report.
