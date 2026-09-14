# Task 11 review adjudication

The owner accepted the routine integrity corrections from the Fable review.

| Finding | Decision | Resolution |
|---|---|---|
| T11-NB-1 | AGREE | Validate `equity_after_cost == equity_before * (1 - cost)`. |
| T11-NB-2 | AGREE | Correct the total-cost docstring to describe cost fractions. |
| T11-NB-3 | AGREE | Clarify that returns are fractions, not percentage points. |
| T11-NB-4 | AGREE | Add a test covering drawdown after a new peak. |
| T11-Q-1 | AGREE | Require timezone-aware, strictly ordered execution/end timestamps. |
| T11-Q-2 | RESOLVED | Keep the explicit closing-equity sampling convention for Task 11. |

The review decision is PASS and no blocker remains for the Task 11 gate.
