# Owner answer to T22-Q3 (pre-fill slippage enforcement, Astra R-5)

Date: 2026-09-27.

## The question as asked (by Claude Opus 5.5)

"Every approved trade has a price limit: the worst price we accept, for
example 0.15% worse than the last price. Right now orders are 'market' orders:
they always fill at whatever the price is. If the price jumps, the system
freezes afterwards, but the bad trade has already happened. The reviewer says
the rules require the limit to be respected, not only noticed afterwards.
Which do you want?"

The options were:

- **Cap the price (Recommended):** each order carries the worst price we
  accept, and if the market has moved further nothing trades. The downside is
  that a trade is sometimes skipped, so paper results can differ a little
  from the backtest.
- **Keep market orders:** a bad fill freezes the system afterwards. The
  reviewer considers this a breach of section 20.

## The owner's answer

Selected: **"Cap the price (Recommended)"**.

## Effect

The executor sends an immediate-or-cancel order capped at the authorization's
`max_slippage_bps` from the mark price. If the fill price would be worse, the
order fills nothing and expires. The fill price itself is unchanged: the next
bar's open under the frozen cost model. Nothing trades beyond the cap. The
difference from the backtest's always-fill assumption is disclosed in the
Task 22 report. `max_slippage_bps` itself is still an unset owner value.
