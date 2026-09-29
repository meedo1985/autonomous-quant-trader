# Owner settings, 2026-09-29 (deployment draft open values)

Asked by Claude Opus 5.5 in two rounds of four, at the owner's request ("yes
start the deployment settings"). Question and option texts are quoted as
offered; the answers are the owner's selections. Each fills an `[OPEN]` value
of `DEPLOYMENT_PROTOCOL_v1_DRAFT.md`. They adopt no document as a whole,
activate nothing, and amend nothing frozen. The draft stays unactivated until
the owner activates it under section 4 of the Constitution.

| # | Draft | Question (short) | Owner's selection | Value |
|---|---|---|---|---|
| D-1 | §2.2, §5 | Alert channel that reaches the owner even if the computer is off | "Telegram (Recommended)": "A private Telegram bot sends messages to your phone within seconds. Free, reliable, easy to test." | External channel: private Telegram bot |
| D-2 | §4, §5 | How often a test alert must reach the owner and be acknowledged (overdue: refuse to start) | "Every 7 days (Recommended)" | Channel test interval: 7 days |
| D-3 | §2.3 | Shadow length before any real-money test | "90 days (Recommended)": "Long enough to see different market moods and catch problems, without waiting forever." | Shadow: 90 days with no open incident |
| D-4 | §2.3 | Extra above the loss limit allowed in the account for fees | "2% extra (Recommended)" | Fee headroom: 2% of `L-01` |
| D-5 | §3 | How closely records must match balances on the real exchange | "Tiny dust only (Recommended)": "Allow differences up to the smallest tradable unit (0.00001 BTC) and 0.01 USDT, from exchange rounding. Anything bigger stops the app." | Real-venue tolerance: one lot step of base (0.00001 BTC for BTCUSDT) and 0.01 USDT |
| D-6 | §10 | Coins still held when the canary ends | "Hold, you decide (Recommended)": "The app goes to HALT and keeps the coins. You decide then whether to sell, with the situation in front of you." | Canary rollback: HALT and hold; the owner decides at the time |
| D-7 | §8 | Where the live app runs (key locked to its address) | "Rented server (Recommended)": "A small cloud server (about $5-10/month) with a fixed address, always on." | Executor on a rented server with a fixed IP; the address itself is recorded when the server exists |
| D-8 | §8 | Where the Binance key lives on that machine | "System secret store (Recommended)": "The operating system's protected credential store (Windows Credential Manager, or the server's equivalent), readable only by the app's user account." | Key storage: the OS credential store, readable only by the executor's account |

Notes:

- The ninth open item, the live exchange filters (T18-06, T25-02), is not an
  owner choice: it is read from Binance's public exchange information before
  any stage using real prices.
- D-5's simulator value stays exact (T23-Q2); D-5 applies to a real venue.
- D-7 leaves one fact open: the server's IP address, filled in when the
  server is rented. Renting it is the owner's action.
- D-1 needs a Telegram bot token, a credential under §8: never in the
  repository, a log, or an AI's context.
- Nothing here raises `L-01` above 0 or authorizes shadow, keys or trading.
