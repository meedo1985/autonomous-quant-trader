# Task 11 scientific decision

The frozen protocol names advanced statistical metrics but does not specify
enough mathematics to implement them reproducibly. In particular, it omits the
Sharpe return/annualization convention, Newey-West lag and kernel details,
Politis-White estimator variant, and DSR/PBO tie and partition conventions.

Choosing those values now would silently change scientific policy.

Task 11 is therefore limited to descriptive infrastructure that follows the
already accepted backtester equation. The advanced statistical layer remains a
later task after an owner-approved convention and, if necessary, a formal
versioned governance amendment. No verdict or eligibility decision is emitted
here.

Claude Fable 5.1 was asked for a bounded decision. Its returned holdout/
evaluation proposal was rejected because it assumed undeclared fields and
crossed the protected validation/promotion boundary. The scope in
`AUTHORIZED_SPEC.md` is the adopted decision.

