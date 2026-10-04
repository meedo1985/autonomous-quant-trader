# Review of the REG-1, REG-2, O-8 proposal, revision 1

You are one of two different-model reviewers (R19-2). You are not an
authority, and you may not decide any owner item. Do not edit, commit or
push. Do not use the network, and do not read confirmation or lockbox data.
You may run small in-memory Python calculations or toy simulations with
`.venv/Scripts/python.exe -B -`.

## Scope

- `review/governance-statistics-amendment/reg-o8-proposal/PROPOSAL.md` at
  the commit named in the request.
- For context:
  - `s4-amendment-draft/DRAFT_WORDING.md` rev 6 and `ANNEX_C_GATE_DEFINITIONS.md` rev 2 (C-6, C-10);
  - `d14-d15-proposal/OWNER_DECISION_D14_D15_ADDENDUM.md`;
  - `d14-d15-proposal/PROPOSAL.md` at `411e1af` §1;
  - `review/owner-input/TRADING_RULE_2026-09-27.md`.
- Code cited: `src/aqt/backtest/engine.py` and `src/aqt/benchmarks/canonical.py`.
- Frozen files only at the cited lines.
- Do not read the other reviewer's review.

## Questions

1. **REG-2.** Is the misalignment mechanism in §1 correct? Can option (a)
   be enforced as written? How large is the residual through other
   volatility features?
2. **REG-1.** Is the claim that Sharpe-based gates are scale-invariant
   correct, given clipping, the 0.10 band, costs and the event contract?
   Is the G-2 drawdown point right? Does option (a) faithfully allow the
   owner's idea to be tested? Is anything about the owner's rule lost?
3. **O-8.** Is the claim that, at baseline, the contract equals current
   engine behaviour plus N-4 correct against the code? Is the claim that N-4
   cannot change the canonical benchmark values correct?
4. **Questions.** Are the §5 owner questions neutral, complete and accurate,
   given that the owner is not a statistician?

Verdict: READY FOR OWNER, SOUND WITH FIXES, or UNSOUND.

## Output

Start with your model name and family as you know them, the commit checked,
and the verdict. Then give a findings table with stable IDs `{{PREFIX}}-1, ...`.
Each row has the severity (BLOCKER or NON-BLOCKING), the location, the
scenario, the evidence and a proposed disposition. End with a five-line
plain-language summary for the owner.

Finding ID prefix: {{PREFIX}}
