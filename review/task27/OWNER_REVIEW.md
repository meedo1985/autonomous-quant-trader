# Task 27 owner behavioural review (Constitution section 16)

Date: 2026-10-02. Reviewed state: `ccc2715` on `task27-persistent-state` (PR #37).

Guided walkthrough by Claude Opus 5.5 (`claude-opus-5-5`) in a Claude Code
session, four yes/no questions, the same form as Tasks 17 and 21-24.
Questions quoted as asked; answers are the owner's selections.

1. **Restart memory.** "The app now keeps a saved state file for the account
   and saves after every important step. After a crash, reboot or update it
   comes back in the same mode (a HALT stays a HALT, a FREEZE stays a FREEZE,
   never RUNNING), with the same 20% loss-stop peak and the same unfinished
   orders, which it checks with the exchange before doing anything. If the
   saved state is damaged, it refuses to start. Is that what you want?" —
   **Yes**
2. **Price falls while it was off.** "When the app restarts, it goes through
   the hours it missed. If the price fell more than 20% below the peak in
   that time, it records each such fall now (an alert and an incident each,
   never twice for the same hour). If it was trading normally, it then
   starts selling in steps, as if it had been running. Is that what you
   want?" — **Yes**
3. **Getting out of FREEZE and HALT.** "FREEZE ends only when you send
   FREEZE_EXIT and the app's records match the exchange; it then goes to
   HALT, never straight to trading. To go from HALT back to trading, you
   send an override that lists every open incident, with a written record,
   a cause and your name. If anything is missing it is refused and logged.
   If accepted, the 20% stop is reset to your equity at that moment. Is that
   what you want?" — **Yes**
4. **Gaps in Binance prices.** "If Binance itself is missing an hour of
   prices, the live price store stops until you add a record with your name
   and a statement that the gap is real. It then continues after the gap and
   never makes up the missing prices. The record is checked every time but
   is not tamper-proof (fine for paper, to strengthen before real money). Is
   that what you want?" — **Yes**

## Reviews

GPT-6 Astra: `ASTRA_REVIEW_2B94313.md` (FIX), re-reviews at `bca6984`,
`c6c8f06`, `9363171`, `ad24b7d`, `c3c4f4e` (each FIX) and `8fa1311`
(**ACCEPT**, `ASTRA_REREVIEW_8FA1311.md`). The first five were text-only;
the last two ran on a PC with read-only commands. Every finding is
adjudicated in `LOCAL_REPORT.md`. Owner answers: `OWNER_ANSWERS.md`.
`ccc2715` adds only review records to `8fa1311`.

This review covers behaviour, not code. It authorizes no real money, no
credentials and no deployment; forward paper (Task 29) stays unauthorized.
Merge happens only on the owner's instruction.
