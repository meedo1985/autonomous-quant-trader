# Loss bounds `L-01`–`L-04` — proposed defaults

**Status:** `AI-PROPOSED DEFAULTS — NOT AN AMENDMENT — NOT ACTIVE — NOT OWNER-ADOPTED`
**Prepared:** 2026-09-22 by Claude, observed model ID `claude-opus-5`, AI author
**Responds to:** `review/pre-deployment/LOSS_BOUNDS_AND_OPEN_DECISIONS.md` §4

## 0. Why this document exists and what it is not

The owner was asked to set `L-01`–`L-04` and answered that he has no background
in the subject and asked the AI to choose. This document is that choice, made
explicitly and with reasoning, so that the reasoning can be disputed later by
someone who does have the background.

It is **not** an amendment. It changes no frozen artifact, closes no `D-nn` row,
does not satisfy §25, and authorizes no calibration, simulation, trial,
confirmation or lockbox access, promotion, deployment, shadow trading, or live
trading. The statistical verdict remains `KEEP_BLOCKED`.

These are the owner's **own self-imposed bounds**, not governance. The frozen
Constitution and `protocol_v1.yaml` are untouched. Every default below is
*stricter* than the frozen text, never looser; none of them relaxes an existing
control. A default here that conflicts with a frozen clause loses to the frozen
clause.

An AI proposing these is legitimate. An AI **adopting** them on the owner's
behalf is not. Until the owner records adoption in §6, they are proposals.

## 1. The standing condition all four are set under

Three facts set the risk posture, and they should be restated whenever these
numbers are revisited, because if they change the numbers should be re-derived:

1. **No qualified human has reviewed the method.** `D-16` and `D-17` are
   `BLOCKING — no candidate`, and Astra `B1` holds that no effective-trial-count
   construction in play is validated for selection over a maximum. `A(N)` is
   monotone in `N`, so an undercount *lowers* the hurdle: the failure direction
   is toward promoting noise, not toward rejecting a real edge.
2. **The owner cannot independently verify statistical output.** An overstated
   result reaches him unchallenged.
3. **The capital is the owner's own.**

Together these mean the backtest evidence is worth **less** than a clean
promotion record would normally be worth, and that the consequence-capping
controls have to carry more weight than they otherwise would. Every default
below follows from that, and each resolves its uncertainty toward the higher
safety hurdle.

## 2. `L-01` — the deployable amount: **default `0`, owner must set**

**The AI declines to choose the figure, and the default is zero.**

This is the one decision where the missing input is not expertise. `L-02` to
`L-04` turn on how selection, drawdown and change control behave — those are
answerable from the subject matter. `L-01` turns on the owner's savings, his
obligations, and what he is willing to have change in his life. No statistical
competence supplies that. A figure invented here would be a guess presented as
advice, and by fact (2) above the owner could not catch the error.

Zero is the correct default rather than a placeholder: it is the only value that
is safe when unset, it blocks nothing today because nothing can deploy in any
case, and it ensures the amount can only ever rise by a deliberate, dated act of
the owner's rather than by drift or omission.

**The test to apply when setting it.** Not "could I afford to lose this?" in the
abstract, which invites optimism, but: *if this entire amount went to zero in one
week, through a mechanism no backtest showed, would anything in my life change
that I am not willing to have change?* Anything other than a flat no means the
figure is too large.

**Recommended form: one fixed absolute figure in USD**, not a percentage of net
worth or of the account. A percentage rises automatically as the account grows,
which is precisely when the temptation to raise it is least resistible and the
evidence for raising it is weakest. A fixed figure has to be raised on purpose.

§25 already freezes the *principle* that only fully-loss-acceptable capital may
be deployed. This row supplies the *amount*, which §25 deliberately leaves open.

## 3. `L-02` — forward paper-trading period: **default ≥ 240 effective decisions**

**Chosen: at least 240 effective decisions of forward paper trading, with no real
capital deployed during the period.**

"Effective decisions" is the protocol's own unit, not trades and not bars:
`protocol_v1.yaml:242–243` defines it as
`newey_west_autocorrelation_adjusted_ESS_on_BTC_OOS_strategy_returns`. It
discounts for the fact that consecutive decisions are correlated, so 240
effective decisions requires materially more than 240 calendar decisions.
Constitution §23 makes the same point: *bar count is never sample size*.

One caveat on the unit: `protocol_v1.yaml:244` supplies a fallback,
`raw_decisions / ceil(horizon_hours/24)`, which is a cruder discount than the
Newey-West ESS. If the fallback is what actually gets computed, 240 under the
fallback is not the same quantity as 240 under the primary method. Whichever is
used should be named in the record when this row is applied.

**Why a forward period at all.** It is the only evidence in the project that
selection cannot have contaminated. The data did not exist when the strategy was
chosen, so no amount of trying-many-things can have fitted it. That property is
worth more here than usual, because the machinery meant to correct for
try-many-things — the effective trial count — is exactly what `D-16` leaves
unresolved.

**Why 240 rather than the cited 120.** `protocol_v1.yaml:290` sets
`minimum_effective_decisions: 120` for promotion, and that is the only figure
with a frozen citation; it is the floor, and anything below it would require
*less* forward evidence than the backtest itself must satisfy. The doubling is a
judgment, not a citation, and rests on condition (1) of §1: the selection
correction that would normally justify trusting the backtest is not validated, so
the uncontaminated evidence has to carry a load it was not originally sized for.
Under fact (3) the cost of waiting is opportunity; the cost of not waiting is
capital.

Note also `protocol_v1.yaml:216`, `enabled_if_effective_decisions_gte: 250`,
which gates a separate check at a comparable magnitude. 240 is not calibrated to
it, but it is not out of family with the protocol's own scale either.

**Honest limitation.** A forward period is uncontaminated but not powerful. 240
effective decisions will not resolve a marginal edge, and it is not a substitute
for the statistician review that `D-16` and `D-17` need. It rules out gross
overfitting and implementation error; it does not establish an edge.

## 4. `L-03` — absolute live stop: **default 20% drawdown from peak live equity**

**Chosen: if live equity falls 20% below its highest previously attained live
value, HALT, and require §14's incident process before any resumption.**

**Why an absolute stop is needed at all.** The frozen protocol's drawdown
control, `btc_drawdown_constraint` at `protocol_v1.yaml:276–278`, requires confirmation OOS
max drawdown to be no worse than the benchmark's by more than 0.05. That is
*relative* and it is a *promotion gate evaluated on backtest data*. It can be
satisfied in full while the owner loses a great deal of real money, provided BTC
is losing too. There is currently no live stop expressed in money at all.

**Why 20%.** The stop's job under fact (3) is to cap consequence, not to
maximize expected return. With `L-01` set so that total loss is survivable, a 20%
stop engages early enough to leave most of the deployed amount intact while the
cause is diagnosed. A wider stop buys room for a strategy that might recover, but
that argument assumes the edge is real — which is the very thing not established.

**What it is not.** This is a halt-and-review trigger, not abandonment. §14
already makes risk reductions immediate and unilateral, and requires a written
incident record, an identified or bounded cause, successful reconciliation,
explicit owner action, and a timestamp before a HALT is overridden. The stop
routes into that existing machinery rather than inventing new machinery.

**State the cost plainly.** A 20% stop on a long-only unlevered spot crypto
strategy will probably trigger at some point, including in cases where holding on
would have recovered. In a sustained bear market it may trigger even if the
strategy is working as designed, because exposure in `[0,1]` limits how far
returns can decouple from the asset. That is an accepted cost, not an oversight:
converting an open-ended drawdown into a bounded realized loss plus a mandatory
review is the entire purpose. The alternative — no absolute stop — has no bound.

**Measurement.** Peak live equity means the highest value attained since real
capital was first deployed, not since the start of the year and not a rolling
window. Paper-trading equity under `L-02` does not contribute to the peak.

## 5. `L-04` — risk increases: **default written record, no increase while below peak, plus the frozen cooling-off floors**

**Chosen: a risk increase — of deployed capital or of exposure limits — requires
all three of the following.**

1. **A dated written record**, made before the increase, naming the specific
   evidence that changed since the last increase and why it bears on risk. §14
   requires "formal review" for risk increases, but the owner is simultaneously
   owner, researcher and operator, so the reviewer and the person wanting the
   increase are the same person. The written record is what stops "formal review"
   from being a thought. It is not reviewed by anyone else; it is reviewed by the
   owner later, which is the only adversarial reader available.
2. **No increase while live equity is below its prior peak.** A drawdown is the
   moment the case for increasing exposure feels strongest and is weakest. This
   removes averaging-down as an available action rather than relying on
   resisting it. Note it interacts with `L-03`: below-peak blocks increases long
   before the 20% stop engages.
3. **The frozen floors, unchanged.** ≥72h capital-increase cooling-off and ≥72h
   risk-loosening cooling-off (§4 line 52, `protocol_v1.yaml:303–304`); increases
   only at 00:00 UTC and only if 24h since the last (§14,
   `protocol_v1.yaml:56–58`); intraday actions safety-direction only
   (`protocol_v1.yaml:59–61`). These already bind and are restated, not modified.

**Why not also a minimum decision count between increases.** It was considered
and rejected as redundant: condition (2) already paces increases by realized
outcome, and a decision-count rule would license an increase purely because time
passed, which is the failure mode the rule is meant to prevent.

**Asymmetry preserved.** None of this applies to risk *reductions*. §14 makes
those immediate and unilateral, and nothing here slows them down. Reducing
capital, tightening limits, killing, HALT and FREEZE remain available at any
moment without record, cooling-off, or justification.

## 6. Owner adoption — unsigned

These are AI proposals. They take effect as the owner's self-imposed bounds only
when he records adoption here, in his own hand, with a date. An AI cannot supply
this and has not.

| Row | Proposed default | Owner decision | Date |
| --- | --- | --- | --- |
| `L-01` | `0` until the owner sets a figure; fixed absolute USD recommended | | |
| `L-02` | ≥ 240 effective decisions forward, no real capital deployed | | |
| `L-03` | 20% drawdown from peak live equity → HALT + §14 incident process | | |
| `L-04` | Written record + no increase below peak + frozen 72h floors | | |

Adoption of these rows is **not** the §25 acknowledgment, which is a separate,
still-unsigned requirement with its own nine clauses and must be signed before
the first equity curve. Adopting `L-01`–`L-04` does not satisfy it and does not
substitute for it.

## 7. What remains open after this

Nothing in this document addresses `D-16`, `D-17`, `D-15`, `D-18` or `D-19`; the
unsigned §25 acknowledgment; the missing §19 deployment protocol; or the absence
of any independent review of `.agents/skills/sharpe-selection-statistics/`.
These defaults cap the consequence of being wrong. They do not reduce the
probability of being wrong, and they are not evidence of anything.
