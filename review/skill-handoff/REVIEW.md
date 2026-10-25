# Quant model handoff skill: local gate and Claude packet

Date: 2026-10-25. Base commit: `ff1af4ce8fb6f61cc5707507165e976c6edf4a2a`.
Scope: add a small shared Codex/Claude Code handoff skill. No project code, dependencies, governance, or frozen files changed.

## Local review

Reviewer: Codex session; exact runtime model ID was not exposed by a model-metadata tool. Finding IDs: none. No findings were deliberately left unrepaired. This is a local review, not an independent Claude review.

LOCAL GATE: PASS. Both new skill directories passed `quick_validate.py` (exit 0). `git diff --check` and `git diff --cached --check` passed (exit 0). `review/task6/verify_frozen.ps1` passed under PowerShell 7 (exit 0): 28/28 baseline bytes and exact protected inventory, 14/14 sidecars, Constitution self-hash, seven manifest/protocol bindings, and nested protocol bindings. The first attempt under Windows PowerShell 5.1 failed because its .NET runtime lacks `[Convert]::ToHexString`; no protected file was changed. Tests, Ruff, mypy, and import-linter: N/A; the change is Markdown skill instructions only. Scientific/quant/Binance reviews: N/A; no scientific method, data path, exchange behavior, or trading code changed.

Changed files: `.agents/skills/quant-model-handoff/SKILL.md` and `.claude/skills/quant-model-handoff/SKILL.md`. The latter is a short pointer to the former, avoiding two copies of the procedure. Both will be available in new local Codex and Claude Code sessions. The skill does not itself send content or run a model.

## Claude adversarial review packet — READY FOR HUMAN RELAY

Review the two complete new files at the commit containing this record, using the base commit above for comparison. Their full paths are listed above; the actual text follows so the packet also works without repository access.

### `.agents/skills/quant-model-handoff/SKILL.md`

```markdown
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
```

### `.claude/skills/quant-model-handoff/SKILL.md`

```markdown
---
name: quant-model-handoff
description: Prepare a compact, evidence-based handoff between Claude Code and Codex for this repository's implementation or independent review. Use when the user requests cross-model work or a project review requires it.
---

# Quant model handoff

Read `.agents/skills/quant-model-handoff/SKILL.md` and follow it for this task. Keep the repository copy as the shared workflow for Codex and Claude Code.
```

Questions for Claude: (1) Does the handoff keep the required independent review genuinely independent while reducing redundant calls? (2) Does any instruction conflict with `AGENTS.md` or the existing `claude-adversarial-review` gate? (3) Is there a concrete scenario where the pointer skill fails to load the shared instructions? Return each finding with a stable ID, severity, file/function, evidence, impact, and minimal correction. Say explicitly when evidence is missing. No strategy logic or governance amendment.

Claude status: NOT SENT. No Claude model reviewed these files. If sent later, record observed model metadata, all returned finding IDs, dispositions, and any unrepaired findings in a committed review record before claiming the review complete.
