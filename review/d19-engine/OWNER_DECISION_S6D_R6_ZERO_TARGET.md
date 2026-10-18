# Owner decision: a zero target is class "not up" for logistic models (S6D-R6)

- Date: 2026-10-17
- Context: screen S6 design revision 2, reading WF-1; Sol design reviews S6D-R6 (`SOL6_SCREEN_S6_DESIGN_REVIEW_5892A4A.md`, and the re-review of revision 2) found that the protocol's "sign objective" (l.153) does not settle which class an exactly zero vol-scaled target belongs to, so the choice is the owner's.
- Asked (verbatim): "An up/down (logistic) model is trained to predict whether the price goes up over its horizon. Rarely, the price ends exactly where it started, a change of exactly zero. Which group should that case count as when training the model?"
- Options offered: "Count it as 'not up' (Recommended)": up means strictly higher, no rows dropped; "Count it as 'up'": up means higher or equal.
- Owner's answer, verbatim: "Count it as 'not up' (Recommended)"
- Recorded meaning: in the screen's walk-forward pipeline (S6, WF-1), the logistic class is `1` if `y_t > 0` and `0` otherwise; a zero target is class 0, is never dropped and never makes a run unavailable. This binds the screen's sign objective for C2. It does not amend Annex C or the protocol.
- Recorded by the AI from the owner's answer; the AI did not choose for the owner.
