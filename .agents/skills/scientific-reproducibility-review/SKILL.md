---
name: scientific-reproducibility-review
description: Review autonomous-quant-trader scientific tasks for determinism, provenance, canonical hashes, preregistration, schema enforcement, and reproducible artifacts. Use for scientific implementation and result review.
---

# Scientific reproducibility review

Read root `AGENTS.md`, the Constitution, protocol, `schemas/HASH_CANONICALIZATION_v1.md`, and applicable specifications. Review existing work against those artifacts; do not invent defaults, scientific criteria, or strategy logic. `NO_EDGE_FOUND` is valid, and must not trigger post-result tuning of success criteria.

Trace inputs through configuration, code, environment, execution, and outputs. Use synthetic or authorized exploration fixtures; never access restricted confirmation/lockbox material to reproduce a review finding.

- Check deterministic ordering, random-number generators and fixed/derived seeds, concurrency, reductions, and library nondeterminism. Seeds alone are not proof of reproducibility.
- Verify raw file SHA-256 sidecars separately from canonical content hashes. Apply the frozen self-reference rules without rewriting files. Check embedded dependency hashes, schema versions, and lineage against the actual inputs.
- Check schema enforcement at read/write boundaries, including missing/unknown/invalid values and rejection paths; parsing alone is not enforcement. Do not strengthen a frozen schema by editing it.
- Trace each scientific/configuration value to its frozen or preregistered source and binding time. Flag values existing only as code defaults, undocumented environment overrides, post-result changes, and unbound data/engine hashes before a trial. Distinguish ordinary implementation constants from scientific choices.
- Check exact dependency/runtime version pinning and recorded environment assumptions: OS, architecture, timezone/locale, numeric precision, BLAS/thread settings, serialization, newline/encoding rules, and relevant hardware.
- Require artifact traceability to code revision/hash, protocol, hypothesis, seeds, data manifest, schema, dependency versions, and execution identity where applicable. Check immutable inputs and append-only accounting; failed/aborted evaluated trials must not disappear.
- Detect silent fallback behavior: swallowed exceptions, missing dependencies/fees/data replaced by defaults, dropped rows, skipped checks, changed estimators, or nondeterministic seed selection. A fallback is acceptable only where governance authorizes it and its use is explicit and traceable.
- Run the task-required independent reruns and compare canonical artifact bytes/hashes byte-for-byte. State exactly what was reproduced and under which environment. If an applicable frozen contract prescribes numerical tolerance, report that test separately; a tolerance match is not byte-for-byte equality. Do not normalize away unexplained differences or invent tolerances.

Report `BLOCKER`, `NON-BLOCKING`, and `QUESTION` findings with file/line, governing requirement, reproducible evidence, impact, and next check. Mark checks N/A with a reason and distinguish missing evidence from passed validation. Propose changes only; required validation failures or missing mandatory reproducibility evidence block task completion. Return findings to `task-gate-review` without invoking it recursively.
