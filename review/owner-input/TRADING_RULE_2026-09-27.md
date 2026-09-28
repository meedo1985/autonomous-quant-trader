# Owner's stated trading rule (input, not an adopted strategy)

Date: 2026-09-27. Recorded by Claude Opus 5.5.

## What the owner said, verbatim

> i dont want to get higher money what i want is to inter with 10% and out
> with 10% or less win and 0.5 % loss

Asked whether "0.5% loss" meant the trade or the whole account, the owner
selected **"0.5% on the trade"**: sell as soon as the position is down 0.5%.

## As a rule

- Position size: 10% of equity (exposure 0.10).
- Take profit: at most +10% on the position.
- Stop loss: -0.5% on the position.

## What the AI told the owner before the answer

- A 0.5% stop on BTC or ETH sits inside ordinary hourly noise, so most trades
  would be stopped out.
- The frozen cost model charges about 13 bps per side, so a round trip costs
  about 0.26%. A 0.5% stop therefore realizes about 0.76% per stopped trade.
- On a driftless random walk the chance of reaching +10% before -0.5% is
  about 0.5 / 10.5, roughly 1 in 21. The expected value is about zero before
  costs and negative after them.
- Stop and target levels bound losses; they do not create an edge. A profit
  needs a real entry signal, which is research work, and `NO_EDGE_FOUND`
  remains a valid outcome.

## How it fits the frozen rules (as read by the AI; not a governance ruling)

- Entry is a risk increase: only at 00:00 UTC, at most once a day, and 24h
  after the previous increase (`scope.risk_increase_rule`).
- Stop and profit exits are reductions: allowed intraday when the change is
  at least 0.10 (`scope.intraday_action_rule`). A full exit from 0.10 meets
  that exactly; a partial exit would not.
- A 10% cap is stricter than the protocol's 1.0 maximum. A risk reduction is
  allowed.
- It is a new strategy, so it is a hypothesis under section 8. It must be
  preregistered and tested in Cycle C1 before any trading use, paper
  included. This record preregisters nothing.

## Status

Recorded as the owner's preference, to be carried into research planning.
It changes no code, protocol, or roadmap task. Q5 (the paper loop's
predictor) is still unanswered.
