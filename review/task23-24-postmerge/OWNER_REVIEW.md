# PR #35 owner behavioural review (Constitution section 16)

Date: 2026-09-29. Reviewed state: `9ef2bd4` on
`review/task23-24-astra-postmerge`. Guided walkthrough by Claude Opus 5.5;
questions quoted as asked, answers the owner's. Given **before** the
different-family (Astra) re-review, at the owner's choice to save time: if
that review changes the behaviour asked about, the affected question is
asked again before merge.

1. **Unsure orders.** "If the system doesn't know whether an order went
   through, it now asks Binance twice, 10 seconds apart, and only treats the
   order as 'never happened' after two 'not found' answers (with a check that
   the 10 seconds really passed). Until then it stays frozen. Is that what you
   want?" — **Yes**
2. **Dust alert.** "The 20% loss alert now fires even when you hold only a
   crumb of BTC too small to sell (in HALT: alert only; while trading: alert,
   try to sell, then HALT). Is that what you want?" — **Yes**
3. **Start-up.** "If the start-up check has to wait (for an unsure order),
   the app places no trade until the check finishes, and any HALT or FLATTEN
   you gave for that hour is applied as soon as it finishes. Is that what you
   want?" — **Yes**

Reviews so far: Astra post-merge FIX (`ASTRA_REVIEW_1E02472.md`); Astra
re-review attempt 1 cut off (`ASTRA_REREVIEW_ATTEMPT_1.md`); Fable 5.1
stand-in FIX (`FABLE_REREVIEW_C9E4C44.md`), repaired at `9ef2bd4`.
Outstanding: a complete Astra re-review. Merge only on the owner's
instruction.
