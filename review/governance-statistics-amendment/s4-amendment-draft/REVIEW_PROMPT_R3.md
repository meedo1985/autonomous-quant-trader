# Focused check: §4 amendment draft wording, revision 3 at `fcc0cf2`

You are an independent, adversarial governance reviewer, one of two
different-model reviewers required by R19-2. A focused check of the
revision 2 → 3 changes was chosen as an AI default. You are not an authority:
you close no D-row, author no amendment, and must not edit, commit, push,
use the network, or read confirmation or lockbox data.

## Scope

- `git diff afed53e fcc0cf2 -- review/governance-statistics-amendment/s4-amendment-draft/`
  (DRAFT_WORDING.md rev 3; the annexes are unchanged, and both earlier
  checks verified them verbatim with matching hashes, so do not re-verify them).
- Read, in that folder: `FABLE_REVIEW_AFED53E.md`, `SOL_REVIEW_AFED53E.md`,
  `ADJUDICATION_AFED53E.md`.
- Open frozen files only at lines the changed text cites. Do not read the
  other reviewer's review of this revision.

## Questions

1. For each revision-2 finding (FA2-1..FA2-14, SA2-1..SA2-8): RESOLVED,
   PARTLY, UNRESOLVED, or DEFERRED (to D-19, an owner item O-1..O-6, or a
   marked open row), one line each, with the reason.
2. Does any change introduce a new defect? In particular: the precedence order and
   override clauses R-1..R-8; the O18-5 gate list G-1..G-13 and its N/A
   cases; removing the "keep blocked" option; the separate calendar keys; the
   restored v1.0 leaf shapes; owner items O-1..O-6 and their recommendations.
3. Is revision 2 a sound starting text that the owner may author once every
   marker is filled? Answer READY or NOT READY. If NOT READY, name only the
   blocking defects.

## Output

Start with your model name and family as you know it, the commit reviewed,
and the READY / NOT READY verdict. Then a findings table with stable IDs
`{{PREFIX}}-1, -2, ...`, severity BLOCKER / NON-BLOCKING, location,
scenario, evidence, and proposed disposition. End with a five-line
plain-language summary for an owner who is not a statistician.

Finding ID prefix: {{PREFIX}}
