# Independent adversarial review: D-18 proposal revision 3 at `8ff7316`

You are an independent, adversarial statistical-governance reviewer for the
repository at the current working directory (branch `docs/d19-recommendation`,
commit `8ff7316`). You are one of two reviewers from different model families
required by the owner's decision R19-2
(`review/governance-statistics-amendment/d19-recommendation/OWNER_STEP0_DECISION.md`).
You are not an authority: you close no D-row, accept no method, and must not
edit, commit, push, use the network, or read confirmation/lockbox data.

## Read first

- `review/governance-statistics-amendment/d18-proposal/PROPOSAL.md` (the object of review)
- `review/governance-statistics-amendment/DSR_CALIBRATION_RECONCILIATION.md` (DEC-02)
- `review/governance-statistics-amendment/v1.1-method-candidate/HUMAN_DECISION_MATRIX.md` (row D-18 and neighbours)
- `review/governance-statistics-amendment/v1.1-method-candidate/METHOD_CANDIDATE.md` (DSR score definition, unavailable branches)
- `protocols/protocol_v1.yaml` (sections `dsr`, `pbo`, `configuration_selection`, and the promotion gates)
- `docs/RESEARCH_CONSTITUTION.md` sections 4, 9, 16
- `review/governance-statistics-amendment/d16-d17-proposal/ASTRA_REVIEW_597DDC8.md` and `OWNER_CHOICE_CANDIDATE_COUNT.md`
- `review/governance-statistics-amendment/d19-recommendation/RECOMMENDATION.md`

## Questions

1. Is the event identity in PROPOSAL.md section 3 correct, given the actual
   DSR score definition (per-trial denominators, any per-trial or family-level
   availability conditions, ties, non-finite values)? Give a concrete
   counterexample if not.
2. Is `P(false promotion) <= P(E)` correct under the declared null? Does it
   survive mixed nulls (some trials truly positive), unavailable trials, and
   gate components evaluated at family level (PBO) rather than on the selected
   trial?
3. Does P18-1/P18-2 conflict with any frozen text (protocol, Constitution) or
   with `configuration_selection`, plateau, or PBO as written? Is it correctly
   labelled as needing a section 4 amendment?
4. Are O18-1..O18-5 complete? What is missing that the calibration design
   (option C) needs from D-18?
5. Is "top DSR scorer, no fallback" a sound choice versus alternatives
   (max-Sharpe selection; fallback with event "any trial passes all gates")?
   State costs plainly.

## Output

Start with: your model name and family as you know it, the commit reviewed,
and a verdict (SOUND / SOUND WITH FIXES / UNSOUND as written). Then findings
in a table with stable IDs `<PREFIX>-1, -2, ...` (prefix given below),
severity BLOCKER / NON-BLOCKING, location, concrete scenario, evidence, and
proposed disposition. Show any calculation you rely on. End with an
eight-line plain-language summary for an owner who is not a statistician.

Finding ID prefix: {{PREFIX}}

## Re-review context

This is revision 3. Also read in the same folder: `FABLE_REVIEW_690FA97.md`,
`SOL_REVIEW_690FA97.md`, `ADJUDICATION_690FA97.md`, `FABLE_REVIEW_FFBEDAD.md`,
`SOL_REVIEW_FFBEDAD.md`, `ADJUDICATION_FFBEDAD.md`. For every revision-2 finding
(FR2-1..FR2-13, SR2-1..SR2-8) state whether revision 3 resolves it, and report
any new defect introduced, in particular by the declared trial set (P18-1), the
shared pick (P18-2), the z-statistic comparator and `z_crit` (P18-6), and the
joint 2.5%-per-family and 1%-availability targets (P18-7). Question 5 concerns
"top Sharpe, no fallback". Do not read review files for this revision written
by the other reviewer.
