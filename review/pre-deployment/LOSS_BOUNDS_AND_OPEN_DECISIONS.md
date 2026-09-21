# Loss bounds — what already binds you, and what only you can set

**Status:** `ORIENTATION AND DECISION REQUEST — NOT AN AMENDMENT — NOT ACTIVE`
**Prepared:** 2026-09-21 by Claude, observed model ID `claude-opus-5`, AI author
**Subject:** the controls that hold whether or not the statistics are right

## 1. Why this is separate from the statistics

Everything blocked in `review/governance-statistics-amendment/` is about whether
an apparent edge is real. `D-16` and `D-17` are open, Astra `B1` says neither
effective-trial-count construction is validated for selection over a maximum, and
no qualified human has reviewed any of it. That work reduces the *chance* of
being wrong.

This document is about the other thing: what it *costs* you when you are wrong
anyway. Those controls do not depend on any statistic being correct, which is
exactly why they are worth understanding before the statistics are settled rather
than after.

A statistician lowers the probability. Loss bounds cap the consequence. Only one
of the two is available to you today.

## 2. What is already frozen, and therefore already binds you

You do not need to invent a risk framework. Most of one is in v1.0 already. This
is a survey of what is binding, with citations, so that nothing here is mistaken
for a new proposal.

| Control | Where | What it means |
| --- | --- | --- |
| Only fully-loss-acceptable capital may be deployed | `RESEARCH_CONSTITUTION.md` §25 | The principle is frozen. The **amount is not** — see §4 |
| Total deployed allocation can be lost via risks no backtest captures | §25 | You must acknowledge this in writing before the first equity curve |
| Long-only, unlevered spot; exposure per asset in `[0,1]` | §2 line 34, `protocol_v1.yaml:62` | No shorting, margin, futures, leverage, or withdrawals |
| Risk **reductions** are immediate | §14 | Reduce capital, tighten limits, kill, HALT, FREEZE — no waiting period |
| Risk **increases** are slow and scheduled | §14, `protocol_v1.yaml:56-58` | Only at 00:00 UTC, only if 24h since the last one, formal review required |
| Capital-increase cooling-off ≥ 72 hours | §4 line 52, `protocol_v1.yaml:303` | No protocol may set it lower |
| Risk-loosening cooling-off ≥ 72 hours | §4 line 52 | Same floor |
| Intraday actions are safety-direction only | `protocol_v1.yaml:59-61` | Intraday may only *reduce* exposure, and only by ≥ 0.10 |
| HALT override needs an incident record | §14 | Written record, identified or bounded cause, successful reconciliation, explicit owner action, timestamp |
| Trading resumes only after incident closure and reconciliation | §14 | Not at your discretion in the moment |
| `REFUSE_START` on config or hash mismatch | §19 | The live path refuses to start rather than starting wrong |
| No LLM in the live decision path | §2 line 34 | An AI cannot be in the loop when money moves |
| Safety amendments cannot be made during an incident | §4 line 56 | You cannot loosen the rules while something is going wrong |

The asymmetry running through all of it is deliberate and correct: **reducing
risk is instant and unilateral; increasing it is slow, scheduled, and reviewed.**
That design survives your statistics being wrong, because it does not consult
them.

## 3. Three hard blockers on live trading that have nothing to do with `D-nn`

Worth knowing, because they are independent layers. Even if a statistician
signed off on every open row tomorrow, none of these would be satisfied.

1. **§25 owner acknowledgment is unsigned.** It must be signed and dated *before
   the first equity curve*. No equity curve has been produced; cycle `C1` never
   started. This is the single cheapest safety control in the whole project and
   it costs you nothing but reading it properly.
2. **No deployment protocol exists.** §19: "Separate deployment protocol required
   before shadow." `protocols/` contains `protocol_v1.yaml` and nothing else.
   Shadow trading is therefore blocked by a missing document, independently of
   everything statistical.
3. **`dsr_minimum: 0.95` is unsatisfied and promotion is blocked** under the
   owner `DEFER` decision of 2026-09-18 (`OWNER_DSR_DEFER_DECISION.md`).

## 4. What is *not* decided, and only you can decide

The frozen text gives principles and floors. It gives no numbers for the things
below. These are the decisions that actually bound your loss.

### `L-01` — the deployable amount

§25 says only fully-loss-acceptable capital may be deployed. It does not say how
much that is, because only you know.

The honest test is not "could I afford to lose this?" in the abstract. It is:
**if this entire amount went to zero in a week, through a mechanism no backtest
showed, would anything in my life change that I am not willing to have change?**
If the answer is anything other than a flat no, the number is too big.

Write the figure down before you are in a position to be tempted to revise it.

### `L-02` — forward paper-trading period before any real money

Nothing in the frozen text requires one, and nothing in it forbids you requiring
one of yourself. A forward period is the only test that is not contaminated by
selection: the data did not exist when the strategy was chosen, so no amount of
trying-many-things can have fitted it.

The relevant number is not weeks but **decisions**. `protocol_v1.yaml:290`
already requires `minimum_effective_decisions: 120` for promotion. A forward
period short enough to contain a handful of decisions tests almost nothing.

### `L-03` — the loss limit that does not consult any statistic

A drawdown level at which you stop, expressed in money, decided in advance, and
not conditional on the model's opinion at the time. The frozen protocol has a
*relative* drawdown constraint (`btc_drawdown_constraint`, line 276-277: OOS max
drawdown no worse than benchmark by more than 0.05) — but that is a
**promotion gate**, evaluated on backtest data. It is not a live stop.

The distinction matters: a relative constraint can be satisfied while you lose a
great deal of money, if the benchmark is losing too.

### `L-04` — who can increase risk, and how

You are the owner, the researcher, and the operator. The frozen text assumes
those roles argue with each other — risk increases require "formal review", and
the reviewer is you. Decide now what evidence you would require of yourself, and
write it down, because deciding it while looking at a drawdown is not the same
exercise.

## 5. The one thing worth internalising

The controls in §2 protect you **because they do not depend on the statistics
being right**. The statistics tell you whether to deploy at all. The loss bounds
determine whether being wrong is a setback or a catastrophe.

You cannot currently obtain the first kind of protection: no statistician has
reviewed the method, `D-16` and `D-17` are open, and the AI reviews explicitly
carry no authority. That makes the second kind more important than it would
otherwise be, not less.

Set `L-01` to a number you can genuinely lose entirely, and the worst case
becomes survivable regardless of how the open statistical questions eventually
resolve.

## 6. What this document does not do

It amends nothing, sets no number, and authorizes nothing. It proposes no change
to the frozen Constitution or protocol, closes no `D-nn`, and does not satisfy
§25, which requires the owner's own signature and dated acknowledgment. It
authorizes no calibration, simulation, trial, confirmation or lockbox access,
promotion, deployment, shadow trading, or live trading. The statistical verdict
remains `KEEP_BLOCKED`.

`L-01` to `L-04` are decision requests addressed to the owner of record. They are
recorded here unanswered.
