# Task 26 owner behavioural review

Date: 2026-09-29. Reviewed state: `5c39ac1` on `task26-live-public-bars`
(PR #36). Guided walkthrough by Claude Opus 5.5; question quoted as asked,
answer the owner's. Given **before** the Astra review; if that review changes
this behaviour, the question is asked again before merge.

1. **Live prices.** "The app reads Binance's public hourly prices (no
   account, no key), keeps only finished hours (finished on both your clock
   and Binance's), refuses if your clock is more than 5 s off, refuses any
   gap or repeat, and never stores data from before 1 Sep 2026 (the
   protected test period). Is that what you want?" — **Yes**

Reviews so far: Fable 5.1 FIX (`FABLE_REVIEW_EA14844.md`), repaired at
`5c39ac1`. Outstanding: an Astra review. Apart from the one key-free
server-time request the Fable reviewer made through the CLI against its
instructions (recorded in `FABLE_REVIEW_EA14844.md`), no live call has been
made; the first real price fetch is the owner's. Merge only on the owner's
instruction.
