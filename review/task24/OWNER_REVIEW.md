# Task 24 owner behavioural review (Constitution section 16)

Date: 2026-09-28. Reviewed state: `75acc92` on `task24-paper-loop-v2` (PR #30).

Guided walkthrough by Claude Opus 5.5, four yes/no questions, the same form
as Tasks 17, 21, 22 and 23. Questions quoted as asked; answers are the
owner's selections. Before recording, the AI checked that the example
configuration carries the values described (S-1 `max_slippage_bps = 5`, S-2
`authorization_ttl_s = 120`, both OWNER-SET).

1. **Normal hour.** "Every hour, on the simulator only (no real money, no
   exchange keys), the loop runs the baseline strategy (buy-and-hold at a
   target risk level). Each order needs a fresh approval from the risk
   governor that expires after 2 minutes, and never fills more than 0.05%
   worse than the price. Is that what you want?" — **Yes**
2. **Start checks.** "The loop refuses to start if a frozen rule file
   changed, an exchange key is set, there's no alert channel, the log is
   damaged, the data has a gap, its records don't match the account, an
   incident is still open, or an earlier run crashed (it leaves a marker you
   must remove). Is that what you want?" — **Yes**
3. **Loss stop.** "At 20% below the peak, while trading normally, it sells in
   steps (at most half per hour) and then HALTs. If you pressed HALT
   yourself, it sells nothing and only sends a critical alert. Is that what
   you want?" — **Yes**
4. **Problems.** "If an order's result is unknown, it FREEZEs and places
   nothing more that run. If the data looks broken, it skips that hour.
   After 3 orders in a row fill nothing, it sends a critical alert and keeps
   going. Is that what you want?" — **Yes**

## Reviews

Owner-chosen substitute for the exact GPT-6 Astra review: Claude Fable 5.1.
`646d514` FIX (`FABLE_REVIEW_646D514.md`), `2dc79ae` FIX
(`FABLE_REREVIEW_2DC79AE.md`), `20dcd42` ACCEPT
(`FABLE_REREVIEW_20DCD42.md`). The follow-up in `75acc92` (one test
assertion and text) was not re-reviewed. Dispositions: `ADJUDICATION.md`.

This review covers behaviour, not code. It authorizes no real money, no
credentials, no live prices and no deployment. Merge happens only on the
owner's instruction.
