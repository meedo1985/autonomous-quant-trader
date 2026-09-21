# Codex collaboration

## Default coding skill

- Use `ponytail` at **full** intensity for coding, debugging, refactoring, and
  design tasks. Read its installed `SKILL.md` before applying it; look in
  `$CODEX_HOME/skills/ponytail/` (default `~/.codex/skills/ponytail/`).
- Ponytail is the default implementation style: understand the code first,
  reuse existing solutions, prefer the standard library, and make the smallest
  complete change. It does not replace any project rule or required review below.
- Preserve all required tests, scientific checks, error handling, frozen
  artifacts, data-access boundaries, and task scope. Ponytail's test minimum
  and brevity preferences never reduce these requirements or requested work.
- Use `ponytail-review` for complexity review, `find-skills` for requested skill
  discovery, `gh-fix-ci` for GitHub Actions failures, and
  `security-best-practices` when security guidance or review is requested.
- Respect explicit user changes to Ponytail mode. If a skill is absent, report
  it; see `review/skill-setup/SETUP_AND_REVIEW.md` for the inspected sources and
  installation commands. Installation does not authorize trading or promotion.

## Project requirements

- Preserve frozen v1.0 artifacts in `docs/`, `protocols/`, `schemas/`, and `specs/`, plus `FROZEN_HASHES.json` and every SHA-256 sidecar. Never casually edit, normalize, regenerate, or update hashes to hide changes. Amendments require the Constitution's formal process; AI cannot author, merge, activate, or self-approve them.
- Before scientific implementation, read `docs/RESEARCH_CONSTITUTION.md`, `protocols/protocol_v1.yaml`, and the applicable frozen specifications. These instructions and skills do not amend governance.
- No secrets in the repository, logs, prompts, artifacts, or tests. No Binance credentials during Milestone 0.1.
- No trading, ML, or LLM implementation before its scheduled task. Do not skip tasks or silently expand scope. Implement only the currently authorized task.
- Prefer simple deterministic implementations. No silent data deletion or correction. `NO_EDGE_FOUND` is a valid scientific result.
- Tests and fixtures use synthetic or exploration data only. Respect confirmation and lockbox access restrictions.
- Every task finishes with applicable tests, lint, type, and import-boundary checks. Record exact commands and results; justify N/A checks. Failed or unavailable mandatory validation blocks completion.
- Invoke `task-gate-review` at every task end, before declaring a major task complete. For scientific/quant tasks also invoke `scientific-reproducibility-review` and `quant-code-review`.
- After local review passes, prepare a `claude-adversarial-review` packet. Claude is an independent adversarial reviewer, not an authority; adjudicate feedback with evidence instead of applying it blindly. Use human relay when no authorized connection exists.
- Invoke `binance-quant-review` for changes involving Binance Spot market data,
  exchange rules, orders, fills, fees, reconciliation, credentials, or live-path
  safety. Keep the review read-only and verify changing exchange behavior against
  official Binance sources when authorized.
- Invoke `statistical-binding-review` for unresolved definitions or bindings of
  paired Sharpe, DSR, PBO, CPCV, ESS, bootstrap intervals, lockbox prediction,
  or promotion statistics. The reviewer proposes and checks bindings but cannot
  supply human/statistician acceptance or activate governance.
- A review or adversarial check is not complete until its record is committed. Write the reviewer's model metadata, every finding with its stable ID, and every finding deliberately left unrepaired with the reason, to a file in the repository, and commit it in or before the commit that applies its repairs. A check whose findings are described only in a later document's summary, or whose report is referenced but never written, has lost the findings it chose not to repair: this has already happened once, and the loss is recorded in `review/governance-statistics-amendment/v1.1-method-candidate/README.md` section 6.5, where four findings identifiable only by a gap in the numbering are unrecoverable. Never cite a review record that is not committed.
- Architecture, protocol, statistical, safety, or frozen-governance changes from review are proposals, never automatic edits. Follow the applicable owner/human approval process. Constitution section 16 requires different-model and human PR review before merging its enumerated protected components.
- Repository skills live in `.agents/skills/<name>/SKILL.md`. Read the relevant skill before using it; if discovery has not refreshed, open that file directly.
- Consider new external skills only when needed: inspect source, provenance, permissions, dependencies, and relevance first. Prefer OpenAI-maintained skills. Do not install arbitrary third-party skills automatically; stop and report any proposed third-party skill before installation.
