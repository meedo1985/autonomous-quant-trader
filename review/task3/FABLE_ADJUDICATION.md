# Task 3 — disposition after Fable 5.1 review

Scope: review only, HEAD 853cb62b199d0f8f6c3ab5844eba3657285927af. No implementation or frozen artifact changes. LOCAL GATE remains BLOCKED.

A1 | HIGH | AGREE on the reproduced unapproved estimator reset. PARTIAL on generalization: a gap does not always collapse slippage to its floor; that depends on post-gap returns. The synthetic example does. Fable correctly warns that rejecting every historical gap indefinitely is only a conservative blocking behavior, not a complete scientific outage policy. No specific carry/reset/warm-up policy is approved by either review.
A2 | MEDIUM | AGREE defect; PARTIAL on severity. The public hourly contract is violated, though trade_cost currently rejects daily history and no direct downstream caller exists. Fix before consumers are added; severity downgrade does not resolve the finding.
A3 | QUESTION | AGREE unresolved centered-seed/uncentered-recursion interpretation. Reject the review's unsupported real-market numerical reassurance: the quoted hourly mean and sigma have no source or authorized data evidence, so numerical immateriality has not been established. Constants demonstrated by Astra establish a convention difference only.
A4 | LOW | AGREE intermediate overflow on the reproduced finite input; ordinary proposed numerical correction, no edit applied.

New suggestions: shared-estimator consistency and explicit delay-sigma timing are useful design questions for future consumers, not proven current cross-module bugs. Docstring/report overstatements are supported. Runtime complexity is a future integration concern, not a benchmarked current blocker.

Authority: both models propose scientific dispositions, not approve them. Fable's blanket statement that no amendment is required is not adopted automatically; determine compatibility against frozen governance for the specific proposed rule. No frozen amendment, policy, merge, or implementation is authorized by this report.

Evidence: previous Astra synthetic reproductions and parent-run 106 passing tests, lint/format/type/import/precommit/governance checks remain the executable evidence. Fable explicitly reports only code reading and hand calculations because its execution requests were denied. No second test pass is claimed. Task4 absent. Fable model provenance is saved in FABLE_MODEL_PROOF.json.
