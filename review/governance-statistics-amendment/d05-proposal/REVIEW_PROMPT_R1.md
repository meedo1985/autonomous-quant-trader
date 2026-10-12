# Review: D-05 plateau-sign proposal, revision 1

You are an independent, adversarial statistical-governance reviewer, one of
two different-model reviewers required by R19-2
(`review/governance-statistics-amendment/d19-recommendation/OWNER_STEP0_DECISION.md`).
You are not an authority: you close no D-row and accept no method. You must
not edit, commit, push, use the network, or read confirmation or lockbox data.
Small in-memory Python calculations with `.venv/Scripts/python.exe -B -` are
allowed; write no files and run no simulation study.

## Scope

- Target: `review/governance-statistics-amendment/d05-proposal/PROPOSAL.md`.
- Evidence: `review/governance-statistics-amendment/external-review-packet/TECHNICAL_APPENDIX.md`
  §3; `v1.1-method-candidate/HUMAN_DECISION_MATRIX.md` row D-05;
  `d02-d04-proposal/OWNER_DECISION_D01_D04.md` and `PROPOSAL.md` rev 2 (C-4);
  `d18-proposal/PROPOSAL.md` §2 (P18-3, P18-7); `s4-amendment-draft/DRAFT_WORDING.md` §3.
- Frozen sources only at the lines cited: `protocols/protocol_v1.yaml`,
  `docs/RESEARCH_CONSTITUTION.md`; code `src/aqt/metrics/statistics.py`
  around the cited functions.
- Do not read any other reviewer's review of this proposal.

## Questions

1. Is the defect in §1 stated correctly for `v > 0`, `v = 0` and `v < 0`?
2. Is each reason in §3 correct? In particular, point 2: under D-04
   (`E-IMPROV`), does G-1 almost always fail when `v <= 0`, given the
   percentile interval in `src/aqt/metrics/statistics.py:591-660`? Point 3:
   is the claim about `U_proc` under option (b) correct?
3. Are the consequences in §4 correct and complete, including neighbour
   availability and `U_proc`?
4. Is the owner question in §5 accurate, neutral and complete?

Verdict: SOUND, SOUND WITH FIXES, or UNSOUND.

## Output

Start with your model name and family as you know it, the commit reviewed,
and the verdict. Then a findings table with stable IDs `{{PREFIX}}-1, -2, ...`,
severity BLOCKER / NON-BLOCKING, location, scenario, evidence, and proposed
disposition. End with a five-line plain-language summary for an owner who is
not a statistician.

Finding ID prefix: {{PREFIX}}
