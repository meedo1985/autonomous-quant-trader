# Review: D-08..D-10 PBO proposal, revision 1

You are an independent, adversarial statistical-governance reviewer, one of
two different-model reviewers required by R19-2
(`review/governance-statistics-amendment/d19-recommendation/OWNER_STEP0_DECISION.md`).
You are not an authority: you close no D-row and accept no method. You must
not edit, commit, push, use the network, or read confirmation or lockbox data.
Small in-memory Python calculations with `.venv/Scripts/python.exe -B -` are
allowed; write no files and run no simulation study.

## Scope

- Target: `review/governance-statistics-amendment/d08-d10-proposal/PROPOSAL.md`.
- Evidence: `v1.1-method-candidate/HUMAN_DECISION_MATRIX.md` rows D-08..D-10;
  `v1.1-method-candidate/METHOD_CANDIDATE.md` §4 and Lemma L-1;
  `external-review-packet/TECHNICAL_APPENDIX.md` §2 and §4; `DRAFT_AMENDMENT_PROPOSAL.md` PBO section;
  `d02-d04-proposal/OWNER_DECISION_D01_D04.md`; `d18-proposal/PROPOSAL.md` §2 (P18-1, P18-4, P18-7);
  `s4-amendment-draft/ANNEX_B_DSR_METHOD.md` §2.5; `s4-amendment-draft/DRAFT_WORDING.md` §3.
- Frozen sources only at the lines cited: `protocols/protocol_v1.yaml`,
  `docs/RESEARCH_CONSTITUTION.md`; code `src/aqt/metrics/statistics.py`
  around the cited functions.
- Do not read any other reviewer's review of this proposal.

## Questions

1. D-08: is `E-DIFF` ranking correct and required, given the stored
   difference matrix, Lemma L-1 and D-18? Is the wording consequence stated
   correctly?
2. D-09: is the per-half Sharpe rule, with no separate block minimum,
   correct and sufficient? Is the enablement count (`|J_f|`) right under D-18?
3. D-10: is the claim that the uniform-average and lowest-id rules give the
   same `phi` for exact duplicate columns correct? Check it on a small case
   with exact arithmetic.
4. Are the consequences in §5 and the owner question in §6 accurate, neutral
   and complete?

Verdict: SOUND, SOUND WITH FIXES, or UNSOUND.

## Output

Start with your model name and family as you know it, the commit reviewed,
and the verdict. Then a findings table with stable IDs `{{PREFIX}}-1, -2, ...`,
severity BLOCKER / NON-BLOCKING, location, scenario, evidence, and proposed
disposition. End with a five-line plain-language summary for an owner who is
not a statistician.

Finding ID prefix: {{PREFIX}}
