# Focused check: broadened DSR method design, revision 2 at `020c8d0`

You are an independent, adversarial statistical-governance reviewer, one of
two different-model reviewers required by R19-2
(`review/governance-statistics-amendment/d19-recommendation/OWNER_STEP0_DECISION.md`).
A **focused check of only the revision 1 → 2 changes** was chosen as an AI
default (the owner delegated drafting choices). You are not an authority: you
close no D-row, accept no method, and must not edit, commit, push, use the
network, or read confirmation/lockbox data. Small in-memory Python
calculations with `.venv/Scripts/python.exe -B -` are allowed; no files
written; no simulation study.

## Scope

- `git diff 6481f28 020c8d0 -- review/governance-statistics-amendment/broadened-method/DESIGN.md`;
  review only the changed text.
- Read, in `review/governance-statistics-amendment/broadened-method/`:
  `SOL_REVIEW_6481F28.md`, `FABLE_REVIEW_6481F28.md`, `ADJUDICATION_6481F28.md`.
- Open other files only at lines the changed text cites.
- Do not repeat earlier findings unless a change makes them worse. Do not read
  the other reviewer's review of this revision.

## Questions

1. For each revision-1 finding (SB1-1..SB1-9, FB1-1..FB1-17): RESOLVED,
   PARTLY, UNRESOLVED, or DEFERRED (to D-19, the amendment, or the owner) —
   one line each with the reason.
2. Does any change introduce a new defect? In particular: using recentred
   resamples for `S0` but uncentred resamples on the same index sequences for
   `D_j`; `D_j`/`z_j` for every column; block length from the null influence
   `u` with the {largest, median} rule chosen in development; the
   `BLOCK_LENGTH_CAPPED` support boundary; the availability ordering and
   `U_proc`/`U_ops` split; the family seed.
3. Is the design now complete and correct enough for the owner to decide
   B-1..B-6 (D-16, D-17 and related)? Answer READY or NOT READY; if NOT READY,
   name only the defects that block those decisions.

## Output

Start with your model name and family as you know it, the commit reviewed,
and the READY / NOT READY verdict. Then a short findings table with stable IDs
`{{PREFIX}}-1, -2, ...`, severity BLOCKER / NON-BLOCKING, location, scenario,
evidence, proposed disposition. End with a five-line plain-language summary
for an owner who is not a statistician.

Finding ID prefix: {{PREFIX}}
