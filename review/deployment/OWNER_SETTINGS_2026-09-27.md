# Owner settings, 2026-09-27 (five operating values)

Asked one at a time by Claude Opus 5.5, at the owner's request ("let do it
one by one"). The owner selected these answers. Each option text is quoted as
offered.

| # | Question (short) | Owner's selection | Value |
|---|---|---|---|
| S-1 | Price limit for normal trades (worst acceptable price per order) | "0.05%" ("Tighter: fewer bad prices, but more trades skipped when the price jumps a little.") | `max_slippage_bps = 5` |
| S-2 | Approval lifetime | "2 minutes (Recommended)" | `authorization_ttl = 120 s` |
| S-3 | Cooling-off after a HALT before any safety-rule change | "72 hours (Recommended)", the frozen minimum (section 4) | 72 hours |
| S-4 | Automatic FLATTEN | "Only at the 20% loss stop (Recommended)": at the L-03 breach the system sells everything in FLATTEN steps, then HALTs; otherwise FLATTEN only on owner command | trigger = L-03 breach |
| S-5 | Health checks | "Yes, use these (Recommended)" | stale data > 2 h, clock skew > 5 s, loop lag > 5 min, each CRITICAL and blocking trading |

Notes:

- S-1 was tighter than the AI's recommendation (0.15%). The AI told the
  owner it would skip more trades when the price jumps a little. That is the
  safer direction: a skipped trade is refused, never a worse fill.
- S-4 extends the proposed HALT-on-L-03 entry in the deployment draft: an
  L-03 breach now enters FLATTEN (bounded de-risking by T23-Q1), which ends
  in HALT. Implementing the automatic trigger is follow-up work on Task 24.
- These are the owner's operating values. They adopt no document as a whole
  and amend nothing frozen.
