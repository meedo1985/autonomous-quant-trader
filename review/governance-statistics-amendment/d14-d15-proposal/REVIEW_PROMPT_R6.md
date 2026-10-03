# Focused check: D-14/D-15 proposal, revision 6 at `4c8648f`

You are an independent, adversarial statistical-governance reviewer. You are one of two
different-model reviewers required by R19-2. A focused check of the
revision 5 to 6 changes was chosen as an AI default. You are not an authority:
you close no D-row and you accept no method. Do not edit, commit, push, use the network,
or read confirmation or lockbox data. Small in-memory Python calculations with
`.venv/Scripts/python.exe -B -` are allowed. Do not write files and do not run a simulation study.

## Scope

- `git diff 0c16c35 4c8648f -- review/governance-statistics-amendment/d14-d15-proposal/PROPOSAL.md`.
  Review only the changed text.
- Read `FABLE_REVIEW_0C16C35.md`, `SOL_REVIEW_0C16C35.md` and `ADJUDICATION_0C16C35.md`
  in that folder.
- Open frozen files only at the lines the changed text cites. Do not read the other
  reviewer's review of revision 6.

## Questions

1. For each revision-5 finding (FN5-1..FN5-8, SN5-1..SN5-3), give one line:
   RESOLVED, PARTLY, UNRESOLVED or DEFERRED.
2. Does any change introduce a new defect? In particular: the three trial
   classes and Q2/Q2b; the treatment of the owner's recorded rule; the
   reduction clamp and the clock; the section 2.2 input list and model-output
   rule; the section 2.3 rows; the section 3 split.
3. Is revision 6 ready to be put to the owner? Answer READY or NOT READY. If NOT
   READY, name only the defects that block the owner questions.

## Output

Start with your model name and family as you know it, the commit reviewed,
and the verdict. Then give a findings table with stable IDs `{{PREFIX}}-1, ...`,
the severity (BLOCKER or NON-BLOCKING), the location, the scenario, the evidence and the
proposed disposition. End with a five-line plain-language summary.

Finding ID prefix: {{PREFIX}}
