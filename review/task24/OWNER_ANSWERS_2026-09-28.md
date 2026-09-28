# Owner answers, 2026-09-28 (Fable review of Task 24)

Asked by Claude Opus 5.5 after the Fable 5.1 review of `646d514`
(`FABLE_REVIEW_646D514.md`). The owner was first told that in one test the
loss stop kept selling for 9 hours after he pressed HALT, and that he had
never been asked about that case. Questions and option texts as asked; the
answers are the owner's selections.

1. **F24-1.** "You pressed HALT yourself, and then the 20% loss stop is
   reached. What should happen?"
   - Selected: **"My HALT wins (Recommended)"**: "Your HALT always means
     'place no orders'. The loss stop only sells automatically when the
     system is trading normally. You decide what to do with the coins."
   - Not selected: "Loss stop still sells".
2. **F24-4.** "If the data looks broken (price feed stale, clock wrong, loop
   lagging), the system places no orders that hour. Should it also switch to
   HALT, so it waits for you instead of resuming by itself once the data
   looks fine again?"
   - Selected: **"Pause only (Recommended)"**: "Skip each hour while the data
     looks broken and resume by itself when it's fine. Nothing is ever traded
     on bad data. The loss stop is checked again as soon as the data is good."
   - Not selected: "Go to HALT".
3. **T24-Q1.** "When 3 orders in a row fill nothing (price moved past your
   limit), what should the system do?"
   - Selected: **"Alert only (Recommended)"**: "Send a critical alert every 3
     empty orders in a row, but keep trading normally."
   - Not selected: "Alert and HALT".

## Effect

- S-4 now applies from RUNNING only. `(HALT, LOSS_STOP)` stays HALT (an
  incident is still opened), and the loop fires the stop only in RUNNING.
- Health-breach hours stay a pause (no orders, no FLATTEN step, no L-03
  check), as built.
- `ZERO_FILL_ALERT_AFTER = 3`, alert only, is now owner-set.
