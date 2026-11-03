# Negotiation brief v1 (2026-10-25)

## Goal
Decide the best ordered next actions to reach a TRUSTWORTHY go/no-go on real-money
trading, as soon as is safely possible, for the repository
`autonomous-quant-trader` (you may read it: the working directory is a checkout of
branch `freeze-sheet`, which holds the freeze sheet and recent records; `main`
content is the same except for files under deploy/calibration/FREEZE_HELDOUT.md,
review/fp4-node/, review/d19-engine/G0_EVIDENCE.md that live on this branch).

## Deliverable
An ordered plan in three lists: (A) what the OWNER must do now / soon, (B) what the
AI (Claude Code, with Codex as reviewer) must do now, (C) what must be checked or
verified, plus the critical path to the first moment real money could lawfully be
risked under the project's own governance, with honest calendar estimates and
what can run in parallel. Also: anything in the current state that has been missed
or mis-stated.

## Acceptance criteria (priority order)
1. Respects hard constraints: frozen v1.0 artifacts untouched; AI cannot author,
   merge, activate or self-approve governance amendments (FP3 is one); Constitution
   §16 owner PR reviews before protected merges; no trading/ML/LLM work before its
   authorized task; only currently authorized tasks; NO_EDGE_FOUND is a valid result.
2. Correct about what actually stands between today and real money, grounded in
   repository documents (cite paths), including what step M "certify" does and does
   not establish.
3. Finds anything missed or wrong in the current state below.
4. Minimizes calendar time without lowering safety; uses parallelism.
5. Actionable for this owner (constraints below): few, concrete steps.

## Owner constraints
Not a statistician; cannot share the work outside; trades only his own capital;
budget about $3-10/month for compute; laptop (Windows 11, 8 GB RAM) is not on all
the time; cannot copy text from chat (uses Notepad files, screenshots); runs all
server commands himself (AI never logs in to the server).

## Current state (2026-10-25, from the session)
- Server (Hetzner CX23, 2 vCPU, 4 GB): forward paper service `aqt-paper` running
  since 2026-10-04 (baseline, paper only). D-19 calibration: threshold run finished
  10-22 (104/104); development run (FULL_RUN.md step E) running since 10-24 11:31Z;
  owner's weekly status about 10-31 decides FP1 (step F `choose`).
- PR #77 (FP2 build: d19.sh freeze/heldout/heldout-status/certify,
  FREEZE_REVIEWS.json) MERGED today as ed0bfbfa7a544f6e925d72d77734007a51d2c77e after
  Astra reviews and owner §16 review (review/d19-engine/OWNER_REVIEW_PR77.md).
  Step G0 done today (review/d19-engine/G0_EVIDENCE.md): FP2 holds.
- FP3 (drand chain binding, governance): open, owner-only formal step.
- FP4 Bitcoin verifier node: owner chose the laptop; installed Core 31.1 today
  (signed hash verified), syncing (review/fp4-node/*). Codex reviewed the node
  steps 5 rounds; open items FP4N-R2/FP4N2-R2 (event-based acceptance time),
  FP4N-R3 scan gate, FP4N-R4 fee check all block step H; the sheet's steps H/I are
  not yet rewritten for a laptop node.
- PR #76 (freeze sheet, draft) open; PR #78 (quant-model-handoff skill) open.
- Weekly Telegram alert test due today (2026-10-25).
- Records mention: owner loss bound L-01 = 0 "for now" (2026-09-26); a deployment
  protocol draft with OPEN values (Task 20); a §4 amendment draft for cycle C2
  (review/governance-statistics-amendment/s4-amendment-draft/); D-rows decisions.
  Verify these in the repo rather than trusting this summary.

## Evidence available
The repository (docs/, protocols/, review/, deploy/calibration/, src/),
especially deploy/calibration/FREEZE_HELDOUT.md, FULL_RUN.md, docs/RESEARCH_CONSTITUTION.md,
review/governance-statistics-amendment/, review/roadmap/, review/fp4-node/.
