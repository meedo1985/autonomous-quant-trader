# Initial independent Codex candidate — preserved negotiation evidence

**Status:** superseded private candidate; no repository or owner authority.

The initial candidate proposed the name `Task 13A — Inactive Synthetic
Paired-Evaluation Assembly` and a pure deterministic layer accepting candidate
and benchmark `BacktestResult` values. It would aggregate existing descriptive
metrics, drawdown, daily paired returns, paired Sharpe statistics, effective
sample size, and the paired 90% percentile interval into an immutable in-memory
diagnostic record.

It excluded DSR/PBO, eligibility, promotion, pass/fail, trials, lockbox and
confirmation access, Binance/network/credentials, models, strategies, trading,
schema/frozen changes, and governance activation. It recommended preserving the
two Sharpe estimands, keeping the percentile interval diagnostic-only,
preserving ESS behavior, and deferring fold logic for human review.

Claude's independent review identified five material corrections: avoid the
Task 13 name; account for identities absent from `BacktestResult`; make the
replicate stream optional and caller-supplied; prohibit verdicts,
serialization, thresholding, and identity-resolution imports; and distinguish
fixed fold rules from unresolved anchoring/completeness. The adjudicated
proposal applies every correction.
