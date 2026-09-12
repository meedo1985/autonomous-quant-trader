# Codex collaboration

- Preserve frozen v1.0 artifacts in `docs/`, `protocols/`, `schemas/`, and `specs/`, plus `FROZEN_HASHES.json` and every SHA-256 sidecar. Never casually edit, normalize, regenerate, or update hashes to hide changes. Amendments require the Constitution's formal process; AI cannot author, merge, activate, or self-approve them.
- Before scientific implementation, read `docs/RESEARCH_CONSTITUTION.md`, `protocols/protocol_v1.yaml`, and the applicable frozen specifications. These instructions and skills do not amend governance.
- No secrets in the repository, logs, prompts, artifacts, or tests. No Binance credentials during Milestone 0.1.
- No trading, ML, or LLM implementation before its scheduled task. Do not skip tasks or silently expand scope. Implement only the currently authorized task.
- Prefer simple deterministic implementations. No silent data deletion or correction. `NO_EDGE_FOUND` is a valid scientific result.
- Tests and fixtures use synthetic or exploration data only. Respect confirmation and lockbox access restrictions.
- Every task finishes with applicable tests, lint, type, and import-boundary checks. Record exact commands and results; justify N/A checks. Failed or unavailable mandatory validation blocks completion.
- Invoke `task-gate-review` at every task end, before declaring a major task complete. For scientific/quant tasks also invoke `scientific-reproducibility-review` and `quant-code-review`.
- After local review passes, prepare a `claude-adversarial-review` packet. Claude is an independent adversarial reviewer, not an authority; adjudicate feedback with evidence instead of applying it blindly. Use human relay when no authorized connection exists.
- Architecture, protocol, statistical, safety, or frozen-governance changes from review are proposals, never automatic edits. Follow the applicable owner/human approval process. Constitution section 16 requires different-model and human PR review before merging its enumerated protected components.
- Repository skills live in `.agents/skills/<name>/SKILL.md`. Read the relevant skill before using it; if discovery has not refreshed, open that file directly.
- Consider new external skills only when needed: inspect source, provenance, permissions, dependencies, and relevance first. Prefer OpenAI-maintained skills. Do not install arbitrary third-party skills automatically; stop and report any proposed third-party skill before installation.
