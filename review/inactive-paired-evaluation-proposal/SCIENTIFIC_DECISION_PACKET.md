# Scientific decision packet

**Status:** `PROPOSAL SUPPORT — NO SCIENTIFIC OR GOVERNANCE APPROVAL`
**Related decision:** `OD-PEA-001`

## Decisions ranked by consequence

### R1 — meaning of paired delta Sharpe

**Conservative default:** preserve both existing quantities with distinct names:
scaled Sharpe of candidate minus scaled Sharpe of benchmark, and scaled Sharpe
of the candidate-minus-benchmark return series. Designate neither as primary.

An AI may preserve and recommend this separation. A qualified human statistician
must approve any governed interpretation or gate binding because the frozen
protocol uses `paired_delta_sharpe` without resolving the two estimands.

### R2 — meaning of the paired 90% percentile interval

**Conservative default:** diagnostic only; never compare it with zero or any
eligibility threshold; do not silently substitute a null-recentered, BCa, or
other interval.

An AI may preserve the implemented interval and recommend further coverage
study. A qualified human statistician must approve any governed use or gate
binding.

### R3 — effective sample size role

**Conservative default:** preserve the existing Newey-West and explicit horizon
fallback behavior exactly, record the input series for each result, and never
compare it with the protocol minimum of 120. Do not add a new clamp.

An AI may preserve and recommend this behavior. A qualified human statistician
must approve the series role, floor, or any governed use.

### R4 — three-month reporting folds

The frozen protocol already specifies a three-month fold length, partial-block
handling, and a minimum passing fraction. It does not fully settle anchoring,
UTC completeness, or minimum days per fold.

**Conservative default:** implement no fold logic in this proposal. A qualified
human statistician and governance review must resolve the remaining semantics
before any later implementation.

### R5 — multiplier scope

**Conservative default:** one record represents one symbol and one stress
multiplier. It performs no cross-multiplier aggregation. This is a structural
recommendation that an AI may make; governed use still requires human review.

### R6 — maximum drawdown

**Conservative default:** expose only the existing nonnegative descriptive
magnitude for each leg. Never evaluate the protocol drawdown constraint. This is
a structural recommendation that an AI may make.

### R7 — annualization and sample variance

The current `sqrt(365)` scaling and sample-variance convention are already
approved for Task 12. They are fixed inputs to this proposal, not parameters.
Changing them requires human approval and a separate governed process.

## Sequencing recommendation

A strictly passthrough, inactive assembler could be implemented after a distinct
owner authorization while preserving R1–R3. Statistician approval is mandatory
before governed interpretation or gate binding. R4 blocks all fold work now.
No AI review can substitute for that human scientific acceptance.
