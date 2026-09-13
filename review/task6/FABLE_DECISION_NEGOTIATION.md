# Task 6 — Fable 5.1 accounting-decision negotiation

Date: 2026-09-13

Status: **REVISED DECISIONS ACCEPTED BY THE HUMAN OWNER**

Claude Fable 5.1 reviewed the four proposed accounting conventions in two
evidence-focused rounds. Both completed responses were identified by Claude
Code metadata as `claude-fable-5-1`. No repository tool or write permission was
granted to Claude.

## Outcome

| Decision | Fable | Coordinator adjudication | Recommended disposition |
|---|---|---|---|
| D1 compounded production equity | REVISE | AGREE. Cost-before-return and retained additive diagnostics are correct. A fractional held weight must drift with asset return on a no-trade segment; otherwise the engine implies free rebalancing. | Track target and actual held weight separately. Use actual drifted weight for PnL and next turnover. |
| D2 flat start and charged entry | ACCEPT | AGREE. This prevents a free initial position and makes runs comparable. | Accept unchanged. |
| D3 no forced terminal liquidation | ACCEPT | AGREE. Mark-to-market matches the frozen hold baseline. A hypothetical liquidation cost is useful but must remain a separate diagnostic. | Accept unchanged; add the diagnostic in the later reporting layer. |
| D4 uniform inclusive 10pp band | REVISE | AGREE in part. Compare a target with actual drifted held weight. Reuse Task 5's existing inclusive, ULP-aware comparator; do not add Fable's initially suggested `1e-9` tolerance or integer-bps quantization. | Accept the inclusive Task 5 comparator and change only the comparison quantity. |

## Exact revised equations

For actual held weight `w_i`, asset simple return `r_i`, zero cash return, and
no trade during the segment:

```text
portfolio_return_i = w_i * r_i
w_after_i = w_i * (1 + r_i) / (1 + w_i * r_i)
```

At the next eligible execution:

```text
target = clip(requested_target, 0, 1)
signed_change = target - w_after_i
turnover = abs(signed_change)
cost_fraction = frozen_cost_rate * turnover
E_next = E_current * (1 - cost_fraction) * (1 + executed_weight * next_return)
```

The band compares `abs(target - w_after_i)` with 0.10 through Task 5's existing
inclusive ULP-aware helper. Below-band decisions hold the drifted actual weight
and incur zero turnover. Binary weights remain fixed under drift, so the current
0/1 analytic identities remain valid.

## Material disagreement with Fable

Fable recommended recording the drift identities now but deferring their tests
to the NumPy reference task. The coordinator rejects that timing. Constitution
section 16 fixes `oracle tests -> NumPy reference`; implementing a reference
before its fractional drift and next-rebalance turnover identities are accepted
would reverse that trust order. If the owner accepts the revised convention,
Task 6 should add the two exact rational oracle identities before freezing:

1. `w_after = w*(1+r)/(1+w*r)` for a fractional no-trade segment.
2. next turnover equals `abs(target-w_after)`, not
   `abs(target-prior_target)`.

This is a Task 6 oracle clarification, not a NumPy reference or production
implementation.

## Model evidence

- Round 1: session `c8f9b4a1-f377-4078-a1b2-1914556377e3`, model
  `claude-fable-5-1`, reported cost USD 0.277665, no permission denials.
- Round 2: session `b0d5ac7f-6e90-43f7-a51b-beb21d70b4e7`, model
  `claude-fable-5-1`, reported cost USD 0.17266575, no permission denials.
- An earlier `claude-fable-5` response was discarded after the user required
  5.1 and is not used as decision evidence.
