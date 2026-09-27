# Senior trading advisor check of the owner's 2026-09-27 answers

Reviewer: the `senior-trading-advisor` agent definition
(`.claude/agents/senior-trading-advisor.md`, branch
`agents/senior-trading-advisor`), run as a general-purpose subagent with those
instructions. Model reported: Claude Opus 5.5 (`claude-opus-5-5`), not Opus
5.1. Read-only. Exploration BTCUSDT data only: 38,166 bars from 2017-08-17 to
2021-12-31, 31 gaps. This is advice to the owner, not an owner decision. It
changes no setting.

## Verdicts

| Item | Answer checked | Verdict | Advisor's point |
|---|---|---|---|
| S-1 | 0.05% price cap | **CONCERN** | Fails safe. In the simulator it skips about 4% of 00:00 entries (next open more than 5 bps adverse: buys 4.02%, sells 4.33%, n=1592). With live timing it skips an estimated 20–35% at 1–5 minutes (random-walk estimate, robust hourly vol 46 bps). A skipped entry waits 24 h. After a >2% falling hour, 11.5% of sells are skipped even in the simulator. Suggests 0.15% before shadow. |
| S-2 | 2-minute approval | PASS | Fits inside the 5-minute window, and the TTL is capped by it (`governor/authorization.py:46,109-110`). |
| S-3 | 72 h cooling-off | PASS | Equals the frozen floor (`RESEARCH_CONSTITUTION.md:52,56`). |
| S-4 | Automatic FLATTEN at L-03 | **CONCERN** | The policy is sound but **not implemented**: `safety.py` sends `LOSS_STOP` to HALT, and `paper_loop.py` has no L-03 check. |
| S-5 | Health 2 h / 5 s / 5 min | **CONCERN** | Fails safe, but **not wired into the loop**. The advisor recalls, from memory and **not verified** (no network), that Binance rejects signed requests when the clock is about 1 s ahead. If true, 5 s is too loose for live. Must be checked against official Binance docs. |
| T23-Q1 | FLATTEN 50% steps, 1% cap | PASS | The 1% cap fails to fill 0.042% of hours overall, 0.47% after a >2% drop, 2.4% after a >5% drop. Halving takes about 8–11 hours to flatten; 100% per step is an option while size is small. |
| T23-Q2 | Tolerance 0 on the simulator | PASS | Exact arithmetic means any difference is a bug. |
| T22-Q1 | 10 s × 2 | PASS | About 20 s total, well inside 2 minutes. A hidden fill is still caught by reconciliation. |

## Interactions flagged

1. A 5 bps cap combined with the once-a-day entry rule means a skipped entry is lost for 24 h, and skips cluster in fast markets.
2. The 5 bps cap delays normal risk-reducing sells. Only the L-03 FLATTEN uses the 1% cap.
3. At the owner's stated 10% position size, the L-03 20% stop can never fire (the maximum loss is about 10%). That rule is not adopted.
4. Loop lag (5 min) = decision window (5 min) ≥ TTL (2 min): consistent.
5. The L-03 → FLATTEN trigger and the health checks are missing from `paper_loop.py`.

## Adjudication by the coding AI (Claude Opus 5.5)

- The code gaps in S-4 and S-5 are **confirmed**: `safety.py` maps
  `LOSS_STOP` to HALT, and `paper_loop.py` calls neither an L-03 check nor
  `aqt.monitoring.health`. Both are follow-up work on Task 24.
- The Binance clock tolerance claim is **unverified** and stays unverified
  until checked against official Binance documentation. It is irrelevant to
  simulator runs.
- The S-1 concern is **the owner's decision**. His 0.05% answer stands until
  he changes it.
