# Task 29: owner behavioural review (Constitution §16 human review)

**Date:** 2026-10-04
**Reviewer:** the owner (meedo1985), answering in the Claude Code session
**Asked by:** Claude Opus 5.5 (`claude-opus-5-5`). The questions and the owner's selected answers are recorded verbatim below. This file records the owner's answers; it is not a review written on his behalf.

The owner was asked about behaviour, not code. Sol's code review (§16 different-model review) is recorded separately in `SOL_REVIEW_*.md`.

| # | Question (as asked) | Owner's answer |
|---|---|---|
| 1 | Forward paper uses play money only: 10,000 USDT of simulated balance, real Binance prices, and the baseline strategy (volatility-targeted buy-and-hold). It never touches your Binance account or keys, and refuses to start if any Binance key is set on the machine. Is that what you want? | Yes, play money only |
| 2 | Every hour, a minute after the hour closes, the app downloads the new price bar and makes that hour's decision. If the computer was off or offline, then when it comes back it runs the missed hours late, as a replay would. It also sends you a CRITICAL alert listing those hours. Is that right? | Yes, catch up + alert |
| 3 | If something looks unsafe, the app stops for good and alerts you: a damaged state file, an order whose outcome is unknown, unapproved code, or a Telegram setup failure. It waits for you to fix the problem; it does not keep retrying. A failed price download is the exception: it is retried the next hour. Is that right? | Yes |
| 4 | Each hour's result goes into a report file, along with a progress count toward the 240 effective decisions needed before real money can even be discussed. The baseline decides once a day, so that is roughly 8+ months of running. Is that understood? | Yes, understood |

The walkthrough was answered while Sol's third re-review (`0ddddae`) was running. The S29R3-1 repair that followed changes no behaviour asked about here: it only removes a false alarm.

**Merge:** not authorized by this record. PR #42 merges only on the owner's explicit words "merge PR 42".
