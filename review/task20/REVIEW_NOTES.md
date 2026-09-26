# Task 20 review notes — deployment protocol draft

Date: 2026-09-26
Base commit: `ae0862d` (`main`)
Branch: `task20-deployment-protocol-draft`
Author and reviewer: Claude Opus 5.5 (`claude-opus-5-5`), coding AI. This is a
**self-review**, not an independent one.

## Authority

Authorized as a **draft for owner review** by the roadmap approval
(`review/roadmap/OWNER_APPROVAL.md`); done before Tasks 16-17 on the owner's
"go ahead" of 2026-09-26 (recorded in `review/task18/LOCAL_REPORT.md`).
Constitution §4: the AI may propose, not author, activate, or self-approve.
The draft says so in its status line and §0 and §12. Merging it does not
activate it.

## Scope

- `review/deployment/DEPLOYMENT_PROTOCOL_v1_DRAFT.md` (new): the draft.
- `tests/unit/test_deployment_protocol_draft.py` (new): 33 citation checks.
- This file.

No frozen file, sidecar, `FROZEN_HASHES.json`, code, or import contract
changed.

## Decisions and deviations

- **T20-01. Location changed from the roadmap.** The roadmap names
  `protocols/drafts/DEPLOYMENT_PROTOCOL_v1_DRAFT.md`. `protocols/` is a frozen
  path, and the frozen verifier used in earlier reviews checks its **exact file
  inventory** (`review/governance-statistics-amendment/DSR_DRAFT_REVIEW_PACKET.md`
  line 129 builds the inventory from every file under `protocols/`). A new file
  there would have failed that check. The draft is under `review/deployment/`
  instead. The roadmap was wrong; this corrects it.
- **T20-02. No invented numbers.** The frozen protocol defines nothing about
  the live path: not even the "protocol delay" that §21 refers to. Every value
  without a frozen source or a pending `L-nn` proposal is marked `[OPEN]` and
  collected in the draft's §11 table: 12 distinct values, marked in 14 places
  in the body (plus one in the legend). Proposing figures with no
  source would let a guess pass for a considered choice.
- **T20-03. Definitions of paper, shadow, and canary are proposals.** §11 names
  those gates but no frozen text defines them. The draft's §2 labels its
  definitions as proposed.
- **T20-04. Overstatements caught before commit.** A first version of the
  draft's §6 table attributed three triggers to frozen text that does not
  contain them (an incident causing HALT; a reconciliation failure causing
  FREEZE; FLATTEN ending in HALT). They are now labeled **proposed**.
- **T20-05. Citation errors caught by the new check.** The first run found a
  `§n` legend example read as a citation, and a §28 quotation broken by line
  wrapping ("Rotation/ revocation"). Both fixed.

## Acceptance (roadmap Task 20: a documentation task)

| Check | Result |
|---|---|
| Every cited Constitution section exists | 11 sections (§0, §2, §4, §11, §14, §16, §19, §21, §22, §25, §28), all present |
| Every quotation matches the frozen text | 11 quotations, verbatim after whitespace normalization |
| Every protocol line reference exists and holds the named key | lines 56-58, 303-306 |
| The check is not vacuous | planting "HALT adds little risk" and `§29` made 3 tests fail; restored |
| No frozen file or sidecar changed | `git diff main` over `docs/`, `protocols/`, `schemas/`, `specs/`, `FROZEN_HASHES.json` and its sidecar is empty |
| `git diff --check main...HEAD` | clean (after commit) |
| `task-gate-review` | this file |

## Validation

Environment: Windows 11, `.venv` Python 3.14.7.

| Command | Result |
|---|---|
| `python -m pytest -q` | 1292 passed, 4 pre-existing skips |
| `ruff check .` / `ruff format --check .` | pass |
| `mypy src` and the three scripts | no issues |
| `lint-imports` | 5 kept, 0 broken |

## What the owner must do before this can be activated

The draft's §1 and §11 list them: sign §25; adopt `L-01`–`L-04`; name the §16
reviewer; set the 12 open values; and activate through §4. Tasks 21-25 must
also exist, since the protocol governs components that are not yet written.

## Gate

LOCAL GATE: PASS. Independent review status: `NOT SENT`.
