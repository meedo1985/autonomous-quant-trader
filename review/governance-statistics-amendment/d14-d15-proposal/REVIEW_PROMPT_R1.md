# Review: D-14/D-15 null and delay-gate proposal, revision 1

You are an independent, adversarial statistical-governance reviewer, one of
two different-model reviewers required by R19-2
(`review/governance-statistics-amendment/d19-recommendation/OWNER_STEP0_DECISION.md`).
You are not an authority: you close no D-row and accept no method. You must
not edit, commit, push, use the network, or read confirmation or lockbox data.
Small in-memory Python calculations with `.venv/Scripts/python.exe -B -` are
allowed; write no files and run no simulation study.

## Scope

- Target: `review/governance-statistics-amendment/d14-d15-proposal/PROPOSAL.md`.
- Evidence: `v1.1-method-candidate/HUMAN_DECISION_MATRIX.md` rows D-14, D-15;
  `v1.1-method-candidate/METHOD_CANDIDATE.md` rows 12-13 and §6.2; `specs/COST_MODEL_v1.md`;
  `specs/BACKTESTER_SPEC_v1.md`; `d02-d04-proposal/OWNER_DECISION_D01_D04.md`;
  `d18-proposal/PROPOSAL.md` §2 (P18-5, P18-7); `s4-amendment-draft/DRAFT_WORDING.md` §2.1, §3.
- Frozen sources only at the lines cited: `protocols/protocol_v1.yaml`,
  `docs/RESEARCH_CONSTITUTION.md`; code `src/aqt/metrics/statistics.py`
  around the cited functions.
- Do not read any other reviewer's review of this proposal.

## Questions

1. D-14: is the circular-shift construction a faithful reading of "match
   candidate mean exposure and turnover on BTC" (l.136)? What can go wrong
   (wrap point, band reductions, minimum hold, shift set, small T)?
2. D-14: is the count rule "at least 475 of 500 strictly below" a correct
   reading of `null_minimum_percentile: 0.95` (l.289)?
3. D-15: are the readings of feature delay and execution delay correct, and is
   mirroring the 2x-cost rule (l.283) a sound pass statistic?
4. Are the consequences in section 4 (including compute in D-19 and C-3) and
   the owner questions in section 5 correct, neutral and complete?

Verdict: SOUND, SOUND WITH FIXES, or UNSOUND.

## Output

Start with your model name and family as you know it, the commit reviewed,
and the verdict. Then a findings table with stable IDs `{{PREFIX}}-1, -2, ...`,
severity BLOCKER / NON-BLOCKING, location, scenario, evidence, and proposed
disposition. End with a five-line plain-language summary for an owner who is
not a statistician.

Finding ID prefix: {{PREFIX}}
