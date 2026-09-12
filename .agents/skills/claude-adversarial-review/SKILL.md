---
name: claude-adversarial-review
description: Prepare a concise Claude adversarial review packet after major autonomous-quant-trader tasks or adjudicate returned Claude findings. Supports human relay without a Claude connector.
---

# Claude adversarial review

Read root `AGENTS.md` and the task's acceptance criteria. Claude is an independent adversarial reviewer, not an authority or an approval substitute. This skill prepares review material or adjudicates feedback; it does not authorize external transmission, implementation, merging, or governance amendments.

## Prepare a packet

Inspect the actual staged, unstaged, and relevant untracked files; record the base commit and reviewed state. Plain `git diff` omits untracked files. Separate pre-existing changes from this task. Never claim Claude saw a file or ran a check without evidence.

After local review passes, give the human a copyable packet in the response or a task-authorized review location outside frozen directories. For a blocked task, label any diagnostic packet BLOCKED, not ready for approval. Include:

- Task scope, exclusions, and exact acceptance criteria.
- Base/HEAD commit IDs, dirty-worktree status, changed file list, and diff summary. Include the actual relevant unified diff or complete new files as attachments/excerpts so the review is independently possible; a summary alone is not sufficient.
- Exact validation commands, exit codes, outcomes, and checks not run with reasons.
- Frozen-artifact verification method/results; relevant manifest, code, configuration, or artifact hashes. Hash the exact reviewed files when an uncommitted snapshot needs identification.
- Unresolved assumptions, limitations, and known blockers.
- Exact questions targeting plausible correctness, scope, reproducibility, security, or governance defects in this change.

Ask Claude to return stable finding IDs under `BLOCKER`, `NON-BLOCKING`, or `QUESTION`. Each finding should identify file/line, triggering scenario, evidence, impact, and a minimal proposed correction or clarifying question. Request explicit missing-evidence statements instead of guesses, and no new strategy logic.

Do not include secrets, raw confirmation/lockbox data, or restricted diagnostics. If Claude is not directly connected, label the packet READY FOR HUMAN RELAY and ask the human to paste Claude's full response back with its finding IDs. Direct transmission requires an available connection and explicit authorization to send the identified material; do not install a connector or claim a review occurred as part of packet preparation.

## Adjudicate feedback

For each finding, preserve its ID and Claude severity, then record:

`ID | Claude severity | AGREE / PARTIAL / DISAGREE | technical reasoning and evidence | disposition | validation`

Reproduce the alleged defect using authorized evidence. AGREE means evidence supports it; PARTIAL identifies exactly what holds and what does not; DISAGREE cites a counterexample, test, governing requirement, or faulty premise. With incomplete evidence, record the uncertainty and required check rather than inventing support. Separately state whether a local blocker remains.

Never automatically apply architecture, protocol, statistical, safety, or frozen-governance changes. Present those as proposals for the applicable human/owner decision. Frozen amendments must follow Constitution sections 3-4 and 27; AI cannot author, merge, activate, or self-approve amendments. Routine authorized corrections still require local validation and an updated packet if the reviewed snapshot changes. A Claude opinion does not satisfy missing human review or remove Constitution section 16 merge requirements.
