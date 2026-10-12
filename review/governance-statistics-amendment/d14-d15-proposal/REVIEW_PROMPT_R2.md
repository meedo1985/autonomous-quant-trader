# Review: D-14/D-15 null and delay-gate proposal, revision 2

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

Also read, in the same folder: `FABLE_REVIEW_0F16E97.md`, `SOL_REVIEW_0F16E97.md`,
`ADJUDICATION_0F16E97.md` (revision 1 was withdrawn; this is a redesign), and
`../n1-n2-proposal/OWNER_DECISION_N1_N2.md`. Do not read any other reviewer's
review of revision 2.

## Questions

1. D-14 ratio-to-benchmark null (section 1.2): does shifting `r = a/b` and
   reapplying it to the benchmark at each hour remove revision 1's
   vol-misalignment defect? Check with a small exact example. What new
   defects arise (clipping, zero or tiny `b`, initial state, wrap point,
   bands, minimum hold)? Is rewording "match" the right treatment?
2. Section 1.3 shifts and 1.5 pass rule: are the formulas correct and the
   availability condition exact?
3. Section 2: are the execution- and feature-delay contracts complete and
   executable? Is the section 2.3 benchmark-under-stress question correctly
   posed for G-5, G-6, G-7 under Constitution section 10?
4. Section 3 workload and section 5 questions: correct, neutral, complete?
   For each revision-1 finding (FN1-1..FN1-14, SN1-1..SN1-9) give one line:
   RESOLVED, PARTLY, UNRESOLVED or DEFERRED.

Verdict: SOUND, SOUND WITH FIXES, or UNSOUND.

## Output

Start with your model name and family as you know it, the commit reviewed,
and the verdict. Then a findings table with stable IDs `{{PREFIX}}-1, -2, ...`,
severity BLOCKER / NON-BLOCKING, location, scenario, evidence, and proposed
disposition. End with a five-line plain-language summary for an owner who is
not a statistician.

Finding ID prefix: {{PREFIX}}
