# Owner §16 PR review of PR #66 (DR2-1 unlock mechanism, qualification cell list, full-run sheet)

- PR: #66, branch d19-unlock, reviewed head 572bb3d (Sol re-review 2 ACCEPT; local gate 463 passed)
- Date: 2026-10-19
- Asked, with options:
  1. "PR #66, part 1: Qualification runs stay REFUSED until you sign your acceptance record and a later small PR writes the accepted preregistration's fingerprint into the code. Then only a run whose preregistration matches that fingerprint exactly (checked against the real file at a full commit ID before any computing) may start. Do you accept this rule?"
  2. "PR #66, part 2: The qualification run will compute exactly 104 cells, each with 300,000 threshold and 12,000 development replications (the grid fixed by the preregistration), and a test keeps that list from drifting. The full-run sheet (FULL_RUN.md) is included as a DRAFT with blanks filled only after the wallet steps. Do you accept this?"
  3. "Merge PR #66 when its CI is green? (Nothing changes on your server: qualification runs remain refused after the merge.)"
- Owner's answers, verbatim (the option labels chosen): 1. "Yes, accept"; 2. "Yes, accept"; 3. "Yes, merge".
- GitHub does not let the owner approve a PR opened from his own account, so the review is recorded here.
- Recorded by the AI from the owner's answers; the AI did not write the review.
- Merge condition: CI green on the head that carries this record.
