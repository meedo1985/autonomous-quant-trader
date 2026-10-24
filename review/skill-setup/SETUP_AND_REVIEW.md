# Skill setup and local review

Date: 2026-09-17
LOCAL GATE: PASS for skill installation/configuration.
Claude status: NOT SENT; READY FOR HUMAN RELAY.
Base/HEAD: bc82a42d6babbbe4997633309ae3f5552263b382.

## Scope and source inspection

User requested Ponytail as the default, find-skills, and useful project additions.
Five user-level skills are installed under ~/.codex/skills; no plugin hooks,
MCP servers, exchange clients, or trading dependencies were installed.
Ponytail full is the coding preference in project AGENTS.md and the newly
created ~/.codex/AGENTS.md. User mode changes and all required project checks
take precedence. Other skills remain task-specific.

| Skill | Inspected source revision and path | Purpose / runtime |
| --- | --- | --- |
| ponytail | DietrichGebert/ponytail @ e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156, skills/ponytail | Minimal complete implementations; Markdown only |
| ponytail-review | Same revision, skills/ponytail-review | Complexity review; Markdown only |
| find-skills | vercel-labs/skills @ 7407f3893ad4dceab546ac002c3ef806e4000c73, skills/find-skills | Discovery; Markdown instructions using npx skills when invoked |
| gh-fix-ci | openai/skills @ 49f948faa9258a0c61caceaf225e179651397431, skills/.curated/gh-fix-ci | GitHub Actions diagnosis; Python stdlib and authenticated gh |
| security-best-practices | Same revision, skills/.curated/security-best-practices | Requested security reviews; Markdown and language/framework references |

Sources:
- https://github.com/DietrichGebert/ponytail
- https://github.com/vercel-labs/skills
- https://github.com/openai/skills
- https://github.com/ml4t/skills was considered but not installed: existing local
  quant/reproducibility skills cover immediate needs; generic statistical advice
  cannot establish the project's unresolved DSR calibration.

Read both Ponytail skills, find-skills, both OpenAI SKILL.md files, their
agent metadata, and the complete CI helper before installation. The installed
directories have no lifecycle hooks. The CI helper invokes git/gh read
commands with argument lists, not shell strings. It can expose fetched CI logs
to the assistant when invoked; existing no-secrets rules still apply.
find-skills can invoke a networked npm CLI later; installation of its Markdown
did not run that CLI or grant blanket approval for future downloads.
Node/npx, Python and gh are present. No external service connections added.

Ponytail's minimal-test preference conflicts with this project's broader
mandatory checks if read as a ceiling. Both default instruction files explicitly
preserve project tests, reviews, scientific requirements and requested scope.
Its complexity review is not a correctness or scientific review.
Security references chiefly cover web frameworks; for plain Python without a
matching reference, the skill must disclose that limitation and use appropriate
primary documentation. No security audit was performed by installing it.

## Reproduce installation on another computer

Use the Codex skill-installer helper; these are the exact successful commands
on this environment (exit 0 each). Adjust /root/.codex to your Codex home.
Pinning preserves the inspected versions; updates require fresh inspection.

```bash
python3 /root/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo DietrichGebert/ponytail --ref e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156 --path skills/ponytail skills/ponytail-review
python3 /root/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo vercel-labs/skills --ref 7407f3893ad4dceab546ac002c3ef806e4000c73 --path skills/find-skills
python3 /root/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo openai/skills --ref 49f948faa9258a0c61caceaf225e179651397431 --path skills/.curated/gh-fix-ci skills/.curated/security-best-practices
```

These are local installations, not files vendored into this repository. Cloning
the project on another computer alone will not install them. They are already
listed in the current session's refreshed skill catalog; future sessions can
read the saved default instructions.

## Validation and review

Acceptance: requested skills installed; useful additions inspected; default
saved; existing project rules and frozen files preserved; review packet prepared.
All are satisfied locally. No independent review is claimed.

- Source comparison and YAML metadata validation below: exit 0; all 22 files
  byte-identical to inspected revisions and five names/descriptions valid.
- Existing AGENTS.md requirements are an unchanged suffix of the new file.
- `python3 /root/.codex/skills/gh-fix-ci/scripts/inspect_pr_checks.py --help`:
  exit 0; local startup/argument parsing only, no GitHub request.
- Re-ran the exact frozen/schema verification command in
  ../governance-statistics-amendment/DSR_DRAFT_REVIEW_PACKET.md: exit 0.
  28 protected files/inventory match the recorded Task 1 snapshot and pre-task
  HEAD; 14 sidecars, Constitution self-hash, seven manifest bindings, protocol
  and nested bindings, five schemas and rejection controls passed.
  No independent signed historical baseline was available.
- `git diff --check`, `git diff --cached --stat`, and
  `git status --short`: exit 0. Staged diff empty. Final formatting checks
  separately cover this untracked report and the user-level instructions.
- Tests/Ruff/mypy/import-linter: N/A for project behavior; no program source,
  Python project configuration or import edges changed. Bundled third-party
  code is unchanged from the inspected source; only its local --help path ran.
- Scientific/quant/Binance review: N/A for installation and coding preferences;
  no estimator, market behavior, data access, or trading logic changed.
- Local task-gate and Claude packet workflows were applied by this assistant.
  All scientific activation blockers in the earlier DSR packet remain open.

Pre-existing work: the two untracked DSR draft/review files from the previous
task are unchanged. This task adds this report, changes project AGENTS.md, and
installs user-level skills and user AGENTS.md outside the repository.
No commit, push, independent review, or scientific activation performed.

## Independent review handoff

Review the configuration diff and user instructions attached below, and the
installed skills at the exact upstream revisions identified above. Report
stable BLOCKER/NON-BLOCKING/QUESTION IDs with file/line, evidence, impact and
minimal correction. Check that default coding guidance cannot waive required
tests/reviews, discovery does not imply blanket future installation permission,
and the installed files agree with their inspected sources.
This packet is ready for human relay; it has not been sent to Claude.

## Exact installation verification command

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib, json, yaml, subprocess
r=Path("/root/autonomous-quant-trader")
sources={
"ponytail":"/tmp/aqt-ponytail-inspect/skills/ponytail",
"ponytail-review":"/tmp/aqt-ponytail-inspect/skills/ponytail-review",
"find-skills":"/tmp/aqt-find-skills-inspect/skills/find-skills",
"gh-fix-ci":"/tmp/aqt-openai-skills-inspect/skills/.curated/gh-fix-ci",
"security-best-practices":"/tmp/aqt-openai-skills-inspect/skills/.curated/security-best-practices"}
for name,source in sources.items():
    target=Path("/root/.codex/skills")/name
    def inventory(root):
        return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
    expected=inventory(Path(source))
    assert inventory(target)==expected, name
    meta=yaml.safe_load((target/"SKILL.md").read_text().split("---",2)[1])
    assert meta["name"]==name and meta["description"], name
    print(name, "PASS",len(expected),"files", "SKILL.md SHA256",expected["SKILL.md"])
old=subprocess.check_output(["git","show","HEAD:AGENTS.md"],cwd=r,text=True)
new=(r/"AGENTS.md").read_text()
assert new.endswith(old.split("\n\n",1)[1])
assert "## Default coding skill" in new
assert "full intensity" in Path("/root/.codex/AGENTS.md").read_text()
print("PASS: existing project instructions preserved; project/user Ponytail defaults present")
PY
```

## Project configuration diff

```diff
diff --git a/AGENTS.md b/AGENTS.md
index fb141e1..2673e8c 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -1,5 +1,25 @@
 # Codex collaboration

+## Default coding skill
+
+- Use `ponytail` at **full** intensity for coding, debugging, refactoring, and
+  design tasks. Read its installed `SKILL.md` before applying it; look in
+  `$CODEX_HOME/skills/ponytail/` (default `~/.codex/skills/ponytail/`).
+- Ponytail is the default implementation style: understand the code first,
+  reuse existing solutions, prefer the standard library, and make the smallest
+  complete change. It does not replace any project rule or required review below.
+- Preserve all required tests, scientific checks, error handling, frozen
+  artifacts, data-access boundaries, and task scope. Ponytail's test minimum
+  and brevity preferences never reduce these requirements or requested work.
+- Use `ponytail-review` for complexity review, `find-skills` for requested skill
+  discovery, `gh-fix-ci` for GitHub Actions failures, and
+  `security-best-practices` when security guidance or review is requested.
+- Respect explicit user changes to Ponytail mode. If a skill is absent, report
+  it; see `review/skill-setup/SETUP_AND_REVIEW.md` for the inspected sources and
+  installation commands. Installation does not authorize trading or promotion.
+
+## Project requirements
+
 - Preserve frozen v1.0 artifacts in `docs/`, `protocols/`, `schemas/`, and `specs/`, plus `FROZEN_HASHES.json` and every SHA-256 sidecar. Never casually edit, normalize, regenerate, or update hashes to hide changes. Amendments require the Constitution's formal process; AI cannot author, merge, activate, or self-approve them.
 - Before scientific implementation, read `docs/RESEARCH_CONSTITUTION.md`, `protocols/protocol_v1.yaml`, and the applicable frozen specifications. These instructions and skills do not amend governance.
 - No secrets in the repository, logs, prompts, artifacts, or tests. No Binance credentials during Milestone 0.1.
```

## User-level instructions

```markdown
# Default coding preference

Use the installed `ponytail` skill at full intensity by default for coding,
debugging, refactoring, and software design. Read its SKILL.md from
`$CODEX_HOME/skills/ponytail/` (default `~/.codex/skills/ponytail/`).
Understand the affected code, reuse existing solutions, prefer standard-library
and native features, and make the smallest complete change.

Project-specific requirements, correctness, security, required tests/reviews,
and the user's requested scope take precedence over Ponytail simplification,
minimal-test, and brevity preferences. Do not use it to skip requested work.
Respect explicit user mode changes, including stopping Ponytail. Use other
installed skills only when relevant; installing them does not run them.
```

## Configuration snapshot hashes

/root/autonomous-quant-trader/AGENTS.md: 2411a4cb8dcd97f57682f58f578b4b4172b46d081de790d2b79951e94e4cfc7d

/root/.codex/AGENTS.md: e7a5580ba6ca1fbac8b5d1a183c5709aec4d07b47b86a226b1a60e228d8ebc6d

## Update 2026-10-20: ponytail skills to 5.3.2

Requested by the owner ("check if there is any update for the plugin and skill and make it").
Done by Claude Opus 5.5 (`claude-opus-5-5`).

- Source: DietrichGebert/ponytail @ `09c434ab73ca43761c5d8b0c5d341926c2fba710`, the Claude Code plugin release 5.3.2 (`claude plugin update ponytail@ponytail`). `~/.codex/skills/ponytail/SKILL.md` and `~/.codex/skills/ponytail-review/SKILL.md` were replaced with that release's `skills/ponytail/SKILL.md` and `skills/ponytail-review/SKILL.md`. The old copies are backed up locally (not in the repository).
- SHA-256 after the update: `ponytail/SKILL.md` `f18008471528f0adde90a560d053f85935eed5cee26c447b7177ad24472bcf32`; `ponytail-review/SKILL.md` `affa0eedca467b58699fafbea28f6f85352aa3e7f23785964bf42f029a291504`.
- Inspection (fresh, as this record requires for updates): both files read in full against the old ones. Markdown only; no scripts, hooks, network calls or dependencies. `ponytail` is shorter and adds an `off` level. `ponytail-review` widens from complexity-only to a full quality review (correctness, safety, load, tests, speed, leanness).
- Project rule unchanged: a `ponytail-review` is still not a substitute for `task-gate-review`, `scientific-reproducibility-review`, `quant-code-review`, the Sol or Claude adversarial reviews, or any §16 review. AGENTS.md's wording ("Use `ponytail-review` for complexity review") stays correct as a use; it is not a limit on the skill.
- Same day, Claude Code plugins: `ponytail` 4.10.1 → 5.3.2 and `agent-skills` 0.6.12 → 0.6.13 (user scope). The agent-skills update needed git's `url.https://github.com/.insteadOf git@github.com:` for that one command (no GitHub SSH host key on this computer); no git configuration was changed. `document-skills`, `playwright`, `pyright-lsp` were already current. find-skills, gh-fix-ci and security-best-practices are not installed in this Windows Codex home, so nothing was updated for them.

Reproduce on another computer (replaces the ponytail line above):

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo DietrichGebert/ponytail --ref 09c434ab73ca43761c5d8b0c5d341926c2fba710 --path skills/ponytail skills/ponytail-review
```

## Install 2026-10-24: graphify and Obsidian skills (owner request)

Owner asked: "install graphify and obsidian skill". Inspected before installation and reported to the owner, who chose the options below (AskUserQuestion, 2026-10-24). Inspected and installed by Claude Opus 5.5 (`claude-opus-5-5`).

**graphify**: source `github.com/Graphify-Labs/graphify` (Apache-2.0, not a fork, about 134k stars); PyPI `graphifyy` 0.9.95, whose project URLs point to that repository; release v0.9.95 published 2026-10-23. I recommended pinning v0.9.83 (2026-10-09) because 0.9.95 was one day old; the owner chose "Yes, latest 0.9.95".
- Commands: `uv tool install graphifyy==0.9.95`, then `graphify install` from the home directory (global, Claude Code platform).
- Effects, checked against `graphify/install.py` and on disk: the skill at `~/.claude/skills/graphify/` (`SKILL.md` sha256 `8736200e6b7d131d937d8ed4b8d84bf74ef7760aa58de80c9df9f2ba8a67e106`, plus `references/`), and a 4-line `# graphify` registration block appended to `~/.claude/CLAUDE.md` (backed up first). No hooks: `settings.json` has no graphify entry. `graphify claude install`, which adds PreToolUse hooks and writes a project `CLAUDE.md`, was **not** run.
- Data: code is parsed locally (tree-sitter); docs, PDFs and media get a semantic pass by the assistant's own model. Running it writes `graphify-out/` into the target folder. It is not run on this repository; if it ever is, `graphify-out/` must stay untracked and out of the server checkout (the deployment check refuses untracked files).
- Remove: `graphify uninstall`, then `uv tool uninstall graphifyy`.

**Obsidian skills**: source `github.com/kepano/obsidian-skills` (Steph Ango, Obsidian; MIT; about 50k stars), plugin `obsidian@obsidian-skills` 1.0.1, user scope.
- Commands: `claude plugin marketplace add kepano/obsidian-skills`, `claude plugin install obsidian@obsidian-skills`.
- Contents: instruction files only (obsidian-markdown, obsidian-bases, obsidian-cli, json-canvas, defuddle, knap). `defuddle` and `knap` tell the agent to `npm install -g` their CLIs when used; nothing was installed with npm now.
- Remove: `claude plugin uninstall obsidian@obsidian-skills`.

Neither install authorizes trading, promotion, or a change to the frozen governance. AGENTS.md rules take precedence over both.
