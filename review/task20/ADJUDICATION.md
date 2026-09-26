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

All five are repaired below.

## Repairs (Claude Opus 5.5, 2026-09-26)

| ID | Change in the draft or test |
|---|---|
| R-1 | §3 now reconciles **both directions**: every exchange open order must match a local record (an unmatched one is an incident and `REFUSE_START`), and free **and locked** balances must match, with every locked amount explained by a matched open order. |
| R-2 | §2 splits paper into **replay** (historical data, machinery test only) and **forward paper** (live data as it arrives). Only forward paper counts toward `L-02`; §2.2(2) says so. |
| R-3 | §10 now says returning from canary starts from HALT: resolve every outstanding order by `clientOrderId`, cancel any still open, decide whether to hold or FLATTEN the remaining position (a new `[OPEN]` value, added to §11), reconcile, and only then remove the order-sending adapter. It states that a stage label change alone is not a risk reduction. |
| R-4 | §4(7) now refuses start only for a **production trading key** outside the executor identity, citing §28; other credentials, such as an alert channel's, fall under §8 and §28's "no secrets in repo/..." rule instead. |
| R-5 | The citation test recognizes all four quotation forms the draft uses (`[FROZEN §n: "..."]`, `[FROZEN §n]: "..."`, `[FROZEN §n] "..."`, `[FROZEN §n "..."]`), rejects a reversed line range, and a new test requires that every quotation after a FROZEN marker is checked. Quotations checked rose from 11 to 15; two had been escaping (`"Startup reconciliation required"` and the §19 pipeline order). |

Mutation checks on R-5, each planted in a copy of the draft and then
restored: changing `"Startup reconciliation required"` to `"... optional"`,
reversing `protocol:303-304` to `304-303`, and dropping `governor` from the
§19 pipeline quotation each make a test fail. (The last was first attempted
with a plain string match that missed a line break, which changed nothing;
it was redone with a whitespace-tolerant match.)

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1297 passed, 4 skipped in 62.54s (0:01:02);
ruff, format and `lint-imports` pass; `git diff --check main...HEAD` clean
(after commit); no change under the frozen paths. The draft now has 13
distinct `[OPEN]` values (one added by R-3).

These repairs have not been re-reviewed by a different model.
