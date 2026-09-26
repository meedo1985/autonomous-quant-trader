# Task 20 review adjudication

Review: `review/task20/REVIEW.md`, saved unedited from the reviewer's reply.
Reviewer: GPT-6 Astra (`gpt-6-astra`, reasoning effort high), Codex CLI 0.154.0,
session `01a0de32-7b0a-7191-ba25-3c6f02eef06b`, read-only sandbox, no tools,
2026-09-26. Input: the full `main...HEAD` diff (the draft, its citation test and
`REVIEW_NOTES.md`), implementer-run check output at `cca2750`, the complete
frozen Constitution, and frozen protocol lines 50-62, 240-245 and 298-307. The
reviewer did not rerun the checks. Verdict: **FIX**.
Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the author of the draft.

| ID | Severity | Adjudication | Evidence |
|---|---|---|---|
| R-1 | BLOCKER | **Accepted.** | Draft §3 matches local orders to the exchange but not exchange orders to local ones; an orphan exchange order, or balance locked by it, passes. |
| R-2 | BLOCKER | **Accepted.** | Draft §2 lets paper use historical data, and §2.2(2) accepts any `L-02` paper period, so a historical replay could satisfy what `L-02` defines as **forward** evidence. |
| R-3 | BLOCKER | **Accepted.** | Draft §10(1) calls any return to an earlier stage an immediate risk reduction, with no step for canary orders already accepted by Binance, which can still fill after the order-sending adapter is removed. |
| R-4 | NON-BLOCKING | **Accepted.** | Draft §4(7) refuses start for **any** secret outside the executor identity; §28 restricts **production keys** to it. An alert channel's own credential would wrongly trigger it. |
| R-5 | NON-BLOCKING | **Accepted, reproduced.** | The quotation pattern did not match `[FROZEN §19 "Startup reconciliation required"]` (11 quotations checked, not that one); a reversed range such as `304-303` iterates over nothing. |

Deviation T20-01: the reviewer finds the relocation justified, while noting it
did not inspect the verifier itself. Agreed.

All five are to be repaired in a later commit on this branch.
