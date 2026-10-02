# Task 28 owner behavioural review (Constitution section 16)

Date: 2026-10-02. Reviewed state: `c79e0e3` on `task28-telegram-alerts` (PR #38).

Guided walkthrough by Claude Opus 5.5 (`claude-opus-5-5`) in a Claude Code
session, four yes/no questions, the same form as Tasks 17, 21-24 and 27.
Questions quoted as asked; answers are the owner's selections.

1. **Telegram alerts.** "Only CRITICAL events (e.g. HALT, FREEZE, loss-stop,
   a channel problem) go to your private bot. If Telegram can't be reached
   or refuses a message, the app never stops because of it: the failure is
   written to the screen and the local tamper-evident log as its own
   CRITICAL alert. The bot token is read only from Windows Credential
   Manager and never appears in any message, log or report. Is that what
   you want?" — **Yes**
2. **Weekly test before start.** "A run that uses Telegram refuses to start
   unless you have confirmed a test message within the last 7 days, by
   typing its 6-digit code (alert_channel.py ack <code>). The test counts
   only for the bot and chat it was sent to: if you change the bot token or
   chat, you must test again. Is that what you want?" — **Yes**
3. **During a run.** "When more than 7 days have passed since the last test,
   the running app sends a new test itself. Until you type its code, it
   sends a CRITICAL reminder at most once an hour, and keeps trading
   normally (no HALT or FREEZE because of the test). Is that what you
   want?" — **Yes**
4. **Problems with the test record or clock.** "If the computer clock is set
   back before the last test, the test record is damaged or edited, or the
   clock is unreadable, the app does not trust the test: at start it
   refuses, and during a run it alerts every hour and keeps going. The
   credential reader works on Windows only for now; the Ubuntu server
   version comes with Task 30. Is that what you want?" — **Yes**

## Reviews

GPT-6 Astra: `ASTRA_REVIEW_3F23E14.md` (FIX, A28-1..A28-9), re-review of
`816cd26` attempt 1 cut off by the usage limit
(`ASTRA_REREVIEW_816CD26_ATTEMPT_1.md`), attempt 2 **ACCEPT**
(`ASTRA_REREVIEW_816CD26.md`, four non-blocking findings A28-10..A28-13).
`c79e0e3` repairs A28-10..A28-13 as the reviewer suggested, with tests that
fail before and pass after; it was not sent for a third review. Every
finding is adjudicated in `LOCAL_REPORT.md`. Owner answers: `OWNER_ANSWERS.md`.
The owner's real bot was tested end to end (two acknowledged tests), recorded
in `LOCAL_REPORT.md`.

This review covers behaviour, not code. It authorizes no real money, no
Binance credentials and no deployment; forward paper (Task 29) stays
unauthorized. Merge happens only on the owner's instruction.
