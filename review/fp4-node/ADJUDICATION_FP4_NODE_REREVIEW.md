# Adjudication: Codex re-review of the FP4 laptop node steps, revision 2

Review record: `SOL_FP4_NODE_REREVIEW.md` (gpt-6-sol, high, read-only, web search; verdict FIX).
Adjudicated by Claude Opus 5.5 (the author of the steps), 2026-10-25.
Repaired steps: `FP4_LAPTOP_NODE_STEPS.txt` revision 3.

The reviewer found the R1 sliding-window approach conditionally sound, the
R5 and R7 repairs acceptable, and the deferral of FP4N-R2, the R3 scan gate
and R4 acceptable while they remain explicit blockers of step H (they do).

| ID | Severity | Adjudication | Repair / disposition |
|---|---|---|---|
| FP4N2-R1 | HIGH | **Accepted.** "Warn you weeks ahead" was a forecast, not a rule. | Stop rule S2: margin = 972,269 - `pruneheight`; below 3,000 blocks (~3 weeks) the author declares MARGIN LOW and the node is not started again until a joint decision (raise the target only if measured disk allows, or the post first); after MARGIN LOW, a laptop off for more than 7 days is not started without asking; `pruneheight` above 972,269 means FP4 fails for this node and step H stays blocked. The 13,000-block and mid-January figures are labelled projections. Daily photos during the first sync. Resync is a recovery only if target and disk can then hold F_Q1 through the freeze read (reviewer's wording, adopted). |
| FP4N2-R2 | HIGH | **Accepted.** A human check time is not the node's first observation. | **Open, blocks step H/I** (with FP4N-R2). Direction for step I: the node's own log line for the acceptance-tip block (`UpdateTip` in `debug.log`, which carries the node's UTC timestamp, block hash and height) is the event record; before the post, `debug.log` must be kept from shrinking at restart (`shrinkdebugfile=0`) and the laptop clock checked against a time source; the laptop stays on, awake and caught up from broadcast until 6 confirmations; a missing or unproved log line is a stop. To be written into step H/I and reviewed before step H. |
| FP4N2-R3 | MEDIUM | **Accepted.** | Stop rule S1: below 8 GB free on D:, stop the node until reviewed. New line 13 measures the whole data directory (not only `size_on_disk`, which covers block and undo files). Daily checks during the first sync. |

Carried forward to step H/I, from the reviewer: the scan must check `scanblocks` `completed: true` and the heights it covered, and a successful `getdescriptoractivity`, not merely an RPC without error.

Still open, blocking step H: FP4N-R2 with FP4N2-R2, FP4N-R3 scan gate (with the item above), FP4N-R4.
