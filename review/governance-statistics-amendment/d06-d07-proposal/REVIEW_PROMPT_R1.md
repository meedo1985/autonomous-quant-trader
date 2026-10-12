# Review: D-06/D-07 fold-block proposal, revision 1

You are an independent, adversarial statistical-governance reviewer, one of
two different-model reviewers required by R19-2
(`review/governance-statistics-amendment/d19-recommendation/OWNER_STEP0_DECISION.md`).
You are not an authority: you close no D-row and accept no method. You must
not edit, commit, push, use the network, or read confirmation or lockbox data.
Small in-memory Python calculations with `.venv/Scripts/python.exe -B -` are
allowed; write no files and run no simulation study.

## Scope

- Target: `review/governance-statistics-amendment/d06-d07-proposal/PROPOSAL.md`.
- Evidence: `v1.1-method-candidate/HUMAN_DECISION_MATRIX.md` rows D-06, D-07;
  `v1.1-method-candidate/METHOD_CANDIDATE.md` row 7; `external-review-packet/README.md` M5;
  `review/task12/IMPLEMENTATION_CONVENTIONS.md` (daily observations);
  `d02-d04-proposal/OWNER_DECISION_D01_D04.md`; `d18-proposal/PROPOSAL.md` P18-7;
  `s4-amendment-draft/DRAFT_WORDING.md` §2.1 and §3.
- Frozen sources only at the lines cited: `protocols/protocol_v1.yaml`,
  `docs/RESEARCH_CONSTITUTION.md`; code `src/aqt/metrics/statistics.py`
  around the cited functions.
- Do not read any other reviewer's review of this proposal.

## Questions

1. Is each rule P6-1..P7-3 a faithful definition of the frozen terms
   (protocol l.197-204, 280-282), or does any rule change their meaning?
   In particular, the anchoring in P6-2 and the month-arithmetic rule.
2. Are P6-4 (missing days make the gate unavailable) and P7-2 (zero-variance
   block makes it unavailable) consistent with Constitution §6 and with the
   `U_proc` target of P18-7? Is there a better fail-closed rule?
3. Are the consequences in §4 correct and complete, including the binomial
   figure in C-2 and the availability risk in C-1?
4. Is the owner question in §5 accurate, neutral and complete?

Verdict: SOUND, SOUND WITH FIXES, or UNSOUND.

## Output

Start with your model name and family as you know it, the commit reviewed,
and the verdict. Then a findings table with stable IDs `{{PREFIX}}-1, -2, ...`,
severity BLOCKER / NON-BLOCKING, location, scenario, evidence, and proposed
disposition. End with a five-line plain-language summary for an owner who is
not a statistician.

Finding ID prefix: {{PREFIX}}
