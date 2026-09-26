# Task 18 review adjudication

Review: `review/task18/REVIEW.md`, saved unedited from the reviewer's reply.
Reviewer: GPT-6 Astra (`gpt-6-astra`, reasoning effort high), Codex CLI 0.154.0,
session `01a0de28-525d-77f0-981b-309df54ac27c`, read-only sandbox, no tools,
2026-09-26. Input: the full `main...HEAD` diff (including `LOCAL_REPORT.md`),
implementer-run check output at `cbde71d`, the unchanged `trade_cost` source,
and the frozen cost model spec. The reviewer did not rerun the checks.
Verdict: **FIX**. Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the
implementing model.

All four findings were reproduced with a script before being accepted.

| ID | Severity | Adjudication | Reproduction |
|---|---|---|---|
| R-1 | BLOCKER | **Accepted.** | Step `0.00001000`, quantity `0.5`, fill fraction `0.33333333` executed `0.16666666`, not a multiple of `0.00001`. `quantize` rounds to the step's exponent, not to the step. |
| R-2 | BLOCKER | **Accepted.** | BTC balance `0.2`, sell `0.3` with fill fraction `0.5`: accepted, `0.15` sold. The balance check ran only on the executed part. |
| R-3 | BLOCKER | **Accepted.** | The `0.5` buy under a caller context of precision 6 left USDT at `949.434` instead of `949.43435`; the balance no longer reconciles with the recorded notional and cost. |
| R-4 | BLOCKER | **Accepted.** | A `NOTIONAL` filter with `maxNotional` 40 and `applyMaxToMarket` true parsed to a minimum only, and a 50 USDT order filled. |

Deviation assessment: agreed on T18-01, T18-02 and T18-04. On T18-03 the
reviewer is right that calling the decision close a "causal equivalent" of
Binance's recent average price overstates it: it is a causal approximation at
1h resolution, not an equivalent. `LOCAL_REPORT.md` is corrected to say so.

All four are to be repaired in a later commit on this branch.
