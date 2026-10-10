# Focused re-review prompt: repairs of I2A-1..I2A-5 (engine item 2a)

You are an independent reviewer (not an authority). Your command runner does
not work in this environment, so everything is attached below: your previous
review (`SOL6_ITEM2A_REVIEW_93BDC60.md`), the adjudication
(`ADJUDICATION_ITEM2A_93BDC60.md`), the updated item note, `git diff
93bdc60 HEAD -- calibration scripts tests`, the HEAD text of
`calibration/generator.py` and `tests/unit/test_calibration_generator.py`,
and the accepted preregistration §3.1-§3.2. Review from the attachments only
and say so.

Check:
1. I2A-1, I2A-2, I2A-3 and I2A-5 are closed as adjudicated; the I2A-4
   carry to item 3 is safe given qualification runs are refused.
2. `generator.market`: GARCH recursion and its use of one shock; AR(1) ε
   with stationary start and burn-in; burn-in for every law; stream use
   and determinism; that the common σ still scales the columns.
3. Whether the new tests would fail on the previous code and prove what
   they claim (including the quadrature check).
4. Anything else these repairs introduce.

Output a complete review record in markdown, ready to commit verbatim:
title, reviewer model metadata (as you observe it), commit reviewed (as
given), scope, commands run (none possible), verdict (ACCEPT / FIX /
UNSOUND for pilot use), findings with stable IDs I2AR-1, ... (severity,
file:line, concrete failure scenario, proposed repair), or "no findings".
