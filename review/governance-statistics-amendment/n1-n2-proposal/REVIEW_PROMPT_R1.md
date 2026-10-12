# Review: N-1/N-2 effective-decisions and shuffled-labels proposal, revision 1

You are an independent, adversarial statistical-governance reviewer, one of
two different-model reviewers required by R19-2
(`review/governance-statistics-amendment/d19-recommendation/OWNER_STEP0_DECISION.md`).
You are not an authority: you close no D-row and accept no method. You must
not edit, commit, push, use the network, or read confirmation or lockbox data.
Small in-memory Python calculations with `.venv/Scripts/python.exe -B -` are
allowed; write no files and run no simulation study.

## Scope

- Target: `review/governance-statistics-amendment/n1-n2-proposal/PROPOSAL.md`.
- Evidence: `review/task12/IMPLEMENTATION_CONVENTIONS.md` (Newey-West ESS);
  `review/inactive-paired-evaluation-proposal/SCIENTIFIC_DECISION_PACKET.md` R3;
  `specs/BACKTESTER_SPEC_v1.md`; `d14-d15-proposal/PROPOSAL.md`; `d18-proposal/PROPOSAL.md` P18-7;
  `s4-amendment-draft/DRAFT_WORDING.md` §3, §4; `s4-amendment-draft/FABLE_REVIEW_FCC0CF2.md` FA3-1, FA3-2;
  `src/aqt/metrics/statistics.py` (`effective_sample_size`).
- Frozen sources only at the lines cited: `protocols/protocol_v1.yaml`,
  `docs/RESEARCH_CONSTITUTION.md`; code `src/aqt/metrics/statistics.py`
  around the cited functions.
- Do not read any other reviewer's review of this proposal.

## Questions

1. N-1: is adopting the Task 12 ESS convention, on the stated series, a sound
   binding of l.242-244 and l.290? Check the arithmetic claim about `L` at
   n = 1219 and the fallback behaviour against the code.
2. N-2: is option (a) a correct reading of l.141-145 and l.289? Are the
   alternatives fairly presented? Is the shuffle and IC definition complete?
3. Is the D-19 problem in section 3 real and correctly stated?
4. Are the owner questions accurate, neutral and complete?

Verdict: SOUND, SOUND WITH FIXES, or UNSOUND.

## Output

Start with your model name and family as you know it, the commit reviewed,
and the verdict. Then a findings table with stable IDs `{{PREFIX}}-1, -2, ...`,
severity BLOCKER / NON-BLOCKING, location, scenario, evidence, and proposed
disposition. End with a five-line plain-language summary for an owner who is
not a statistician.

Finding ID prefix: {{PREFIX}}
