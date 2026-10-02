# Owner answers to the Task 28 design questions

Date: 2026-10-02. Asked by Claude Opus 5.5 from `DESIGN.md` section 4 in a
Claude Code session; question and option texts as asked, answers the
owner's selections.

- **Q28-1.** "Once a week the app sends a test message to your Telegram, and
  you must confirm you got it (otherwise it refuses to start). How do you
  want to confirm?" — **"Type the code (Recommended)"**: "The test message
  shows a short code; you type `python scripts/alert_channel.py ack <code>`
  on the app's computer. Simple, no extra network use, and it proves the
  message really reached you."
- **Q28-2.** "A forward-paper run lasts months, so 7 days will pass while it
  is running. What should happen when the weekly test is overdue during a
  run?" — **"Remind, keep running (Recommended)"**: "The app sends the
  weekly test itself. While it is overdue, it sends a critical alert every
  hour but keeps running. The next start is refused until you confirm."

## Effect on Task 28

The app never reads messages from Telegram; acknowledgment is a local
command with the code. Inside a run, a due test is sent automatically and an
overdue one raises a CRITICAL alert each hour without changing the mode; the
start check refuses. No loss bound or frozen file changes.
