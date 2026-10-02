# Task 30 owner behavioural review (Constitution section 16)

Date: 2026-10-02. Reviewed state: `70c1991` on `task30-runbook-design` (PR #40).

Guided walkthrough by Claude Opus 5.5 (`claude-opus-5-5`) in a Claude Code
session, four yes/no questions, the same form as Tasks 17, 21-24, 27 and 28.
The owner first asked for an agent to give the answers; that was declined,
because section 16 requires the owner's own review, and the owner then
answered each question. Questions quoted as asked; answers are the owner's
selections.

1. **Approval.** "Only the code you approve runs. On the server, you approve
   one exact commit (that you merged on GitHub) with your name and a
   statement. The app refuses to start, logs it, and does not retry, if the
   code is anything else: a changed, added or hidden file, a broken config,
   a different commit, or a commit not on main. Is that what you want?" —
   **Yes**
2. **Separation.** "The app cannot change itself. The code, its history and
   its Python belong to root (you, with sudo). The app runs as its own
   account that can read and run the code but not change it, cannot write
   your approval record, and writes only to its own data folder
   (/var/lib/aqt). Is that what you want?" — **Yes**
3. **Runbook.** "You do every step by hand. You rent the server and run the
   runbook commands yourself: install, approve, store the Telegram key in a
   file only the app can read, start, update (stop, fetch, switch to the new
   commit, approve, start). The AI never logs in or sees the server's
   address or keys. A GitHub test machine repeats install, approve and a
   refused start on every change. Is that what you want?" — **Yes**
4. **Limits.** "Known limits, accepted for paper trading. The approval is
   your name in a tamper-evident record protected by root-only access, not a
   cryptographic signature. Library versions are not pinned. Today the
   service replays the exploration data and stops; turning on 'start on
   boot' waits for Task 29. Fixing the first two is planned before real
   money. Is that acceptable?" — **Yes**

## Reviews

GPT-5.6 Sol, high effort (owner's choice of reviewer):
`SOL_REVIEW_3C41F70.md` (FIX, S30-1..S30-6), re-reviews
`SOL_REREVIEW_57A3B40.md` (FIX, S30-7, S30-8), `SOL_REREVIEW_B7611A0.md`
(FIX, S30-9), `SOL_REREVIEW_CA68EEE.md` (FIX, S30-10) and
`SOL_REREVIEW_1C90663.md` (**ACCEPT**). Every finding is adjudicated in
`LOCAL_REPORT.md`. The CI runbook dry run passes on a fresh Ubuntu
machine. Owner answers to the design: `OWNER_ANSWERS.md`.

This review covers behaviour, not code. It rents no server and authorizes
no real money, no Binance credentials and no forward paper trading (Task
29 stays unauthorized). Merge happens only on the owner's instruction.
