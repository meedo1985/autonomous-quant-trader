---
name: quant-model-handoff
description: Prepare a compact, evidence-based handoff between Codex and Claude Code for this repository's implementation or independent review. Use when the user requests cross-model work or a project review requires it.
---

# Quant model handoff

Read the repository `AGENTS.md` and the current task's acceptance criteria. Follow its model preference, review gates, restricted-data rules, and authorization boundaries. This skill coordinates work; it does not authorize a model call, trading, promotion, a governance change, or a merge.

1. Use the current working tree and local checks first. Pick one implementer and one independent reviewer only when a second model is required or likely to catch a consequential error. Do not run parallel reviews that ask the same question.
2. Give the receiving model a short contract: goal; exact commit and changed paths or relevant diff; governing constraints; checks already run with exit codes; one to three specific questions; required output shape. Supply a full file only when the diff lacks needed context. Exclude secrets, confirmation or lockbox data, and unrelated repository content.
3. Before direct CLI transmission, confirm this session authorizes sending the identified material to that model. Otherwise prepare a packet for human relay using `claude-adversarial-review`. Use the model choice in `AGENTS.md`; verify observed model metadata instead of inferring it from a requested flag.
4. Ask for findings with stable IDs, severity, file or function, evidence, impact, and minimal correction. A reviewer returns findings, not permission to change frozen or protected components.
5. Reproduce material findings with local evidence. Record every finding, including rejected or deferred ones and why, with observed model metadata in a repository review record. Commit that record in or before any repair commit as required by `AGENTS.md`. Re-run only checks relevant to a changed patch and the mandatory end-of-task gate.
6. If a major dispute survives a focused evidence check, use `ai-negotiation` for that dispute. Stop after a resolved finding or a clearly stated deadlock; do not spend extra rounds to obtain agreement.

Report which model actually worked, what was sent, exact validation results, and unresolved findings. Never describe a prepared packet as a completed external review.
