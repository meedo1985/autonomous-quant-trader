# Review prompt: D-19 engine item 2a (skew-t, Q2m, Q4 generators)

You are an independent, adversarial reviewer (not an authority). Your command
runner does not work in this environment, so everything is attached below:
the item note `ITEM2A_SYNTHETIC_LAWS.md`, `git diff <base> HEAD -- calibration
scripts tests` (base = the commit before item 2a), the HEAD text of
`calibration/generator.py`, `calibration/seeds.py`, the reference-case list
of `calibration/rundef.py`, and `tests/unit/test_calibration_generator.py`,
plus the accepted preregistration text §3.1-§3.2 and §13 items 1-2. Review
from the attachments only and say so.

Check, against the accepted text:
1. The Azzalini skew-t: the construction, draw order and determinism, the
   exact product-moment formula, the standardisation (mean exactly 0,
   variance 1), α_s = 0.9224371221852867 and its sign convention, and
   whether "standardised skewness of ±1" is met.
2. Q2m: which columns are t5, the scales c_j, independence, the market.
3. Q4: the single AR(1) column, φ, burn-in, the market.
4. The three interpretations in the note, and the pre-existing AR(1)
   question it raises (ε not AR in `ar0.2`/`ar0.5`): is the existing code
   faithful to §3.1, and if not, what should change (a proposal; it is
   reviewed code)?
5. Manifest validation, `AGNOSTIC_LAWS`, and the new reference cases.
6. Whether the tests prove what they claim, and anything else.

Output a complete review record in markdown, ready to commit verbatim:
title, reviewer model metadata (as you observe it), commit reviewed (as
given), scope, commands run (none possible), verdict (ACCEPT / FIX /
UNSOUND for pilot use), findings with stable IDs I2A-1, I2A-2, ...
(severity, file:line, concrete failure scenario, proposed repair; mark any
finding that would change the accepted preregistration as a proposal for
the owner), or "no findings".
