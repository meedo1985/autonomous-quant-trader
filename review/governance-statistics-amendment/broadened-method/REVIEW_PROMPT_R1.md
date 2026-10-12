# Independent adversarial review: broadened DSR method design, revision 1

You are an independent, adversarial statistical-governance reviewer, one of
two different-model reviewers required by R19-2
(`review/governance-statistics-amendment/d19-recommendation/OWNER_STEP0_DECISION.md`).
You are not an authority: you close no D-row, accept no method, and must not
edit, commit, push, use the network, or read confirmation/lockbox data. You may
run small in-memory Python calculations with `.venv/Scripts/python.exe -B -`
(no files written); a full calibration or simulation study is out of scope.

## Object of review

`review/governance-statistics-amendment/broadened-method/DESIGN.md` at the
commit named below.

## Read first

- `review/governance-statistics-amendment/d18-proposal/PROPOSAL.md` (decided
  D-18 definition, revision 7) and `OWNER_DECISION_D18.md`
- `review/governance-statistics-amendment/v1.1-method-candidate/METHOD_CANDIDATE.md`
- `review/governance-statistics-amendment/d16-d17-proposal/ASTRA_REVIEW_597DDC8.md`
  and `OWNER_CHOICE_CANDIDATE_COUNT.md`
- `review/governance-statistics-amendment/DSR_CALIBRATION_RECONCILIATION.md`
- `review/task12/IMPLEMENTATION_CONVENTIONS.md` and the cited functions in
  `src/aqt/metrics/statistics.py`
- `protocols/protocol_v1.yaml` and `docs/RESEARCH_CONSTITUTION.md` at the
  cited lines

## Questions

1. Is the joint recentred stationary block bootstrap a valid way to supply
   `S0` (expected null maximum of the family Sharpes) and `D` (nominee Sharpe
   variance) for the D-18 statistic? Where does it fail (small `T`, long
   memory, infinite fourth moments, recentring bias, max over many columns,
   the "largest PW length" rule, Monte-Carlo error at B = 2000)? Give a
   concrete counterexample or calculation where you can.
2. Does the design actually remove the defects listed in its §1 (AS-1, AS-2,
   AS-3, P-7, serial dependence, heavy tails)? Which remain?
3. Is the D-16 answer (no effective count) and the D-17 answer (declared
   current-cycle set in the score; lifetime count reported only) sound under
   the decided D-18 rules, especially P18-0? What is lost?
4. B-3: does redefining `D` as a bootstrap variance stay within the decided
   D-18 text, or does it reopen D-18?
5. Are the availability rules (§2.6) total, ordered and fail-closed, and are
   the AI defaults (`T_min` = 365, `L <= T/4`, largest PW length) defensible?
6. Anything in §3 (cross-cycle risk) or §5 (calibration) that is wrong or
   missing?

## Output

Start with your model name and family as you know it, the commit reviewed,
and a verdict (SOUND / SOUND WITH FIXES / UNSOUND as written). Then findings
in a table with stable IDs `{{PREFIX}}-1, -2, ...`, severity BLOCKER /
NON-BLOCKING, location, concrete scenario, evidence, proposed disposition.
Show any calculation you rely on. End with an eight-line plain-language
summary for an owner who is not a statistician.

Finding ID prefix: {{PREFIX}}

Commit reviewed: `6481f28`.
