# Independent re-review 2: FP4 laptop node steps, revision 3

You are an independent adversarial reviewer (read-only), not an authority.
Your re-review `review/fp4-node/SOL_FP4_NODE_REREVIEW.md` found FP4N2-R1..R3
(FIX). Below: the adjudication, and the repair `git diff ced3ed4 db63261 --
review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt`. Check only: (1) are FP4N2-R1 and
R3 resolved by the stop rules and line 13; (2) is FP4N2-R2's open
disposition and its stated direction for step I acceptable as a blocker of
step H; (3) any new defect or other problem. New findings `FP4N3-R1`, ...
Verdict: ACCEPT or FIX. Do not re-open findings already resolved unless the
repair broke them.

## Adjudication

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

## Repair diff

```diff
diff --git a/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt b/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt
index 7c158f8..52bf58d 100644
--- a/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt
+++ b/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt
@@ -1,6 +1,6 @@
 FP4 - Bitcoin verifier node on your LAPTOP (Bitcoin Core 31.1, pruned, block filters)
 Run each line in PowerShell on the laptop, ONE LINE AT A TIME. No keys or wallet go on this node.
-(Revision 2, after Codex review FP4N-R1..R7; see ADJUDICATION_FP4_NODE.md.)
+(Revision 3, after Codex reviews FP4N-R1..R7 and FP4N2-R1..R3; see ADJUDICATION_FP4_NODE*.md.)
 
 === ONCE: install ===
 
@@ -56,10 +56,24 @@ Start-Process "C:\Program Files\Bitcoin\daemon\bitcoind.exe" "-datadir=D:\Bitcoi
 12) Disk space left on D: (GB):
 [math]::Round((Get-PSDrive D).Free/1GB)
 
+13) Whole node folder size (GB; takes a few seconds):
+[math]::Round((Get-ChildItem D:\Bitcoin -Recurse -File | Measure-Object Length -Sum).Sum/1GB)
+
+   During the FIRST sync (until I say it is synced): send lines 10, 12 and 13 every day the laptop is on, not weekly.
+
+=== STOP RULES (they win over everything above) ===
+
+S1) Disk: if line 12 shows LESS THAN 8 GB free, run line 9 (stop) and do not start the node again until I say.
+S2) Keeping block 972,269: from your photos I compute the margin = 972,269 minus "pruneheight" (in blocks).
+    - margin below 3,000 (about 3 weeks of blocks): I tell you "MARGIN LOW". From then on, do not start the node (line 8)
+      until I say; we decide together: raise the setting (only if disk allows), or the post must happen first.
+    - If the laptop was off for more than 7 days after "MARGIN LOW": ask me before starting it (catching up can prune).
+    - If pruneheight ever goes ABOVE 972,269: the node no longer meets FP4. Step H stays blocked; only a fresh sync can fix it.
+S3) Never change bitcoin.conf yourself.
+
 Notes:
-- The node keeps only about the last 13,000 blocks (about 3 months). Block 972,269 (F_Q1) must still be kept at the freeze read.
-  From your weekly photos I compute the real date by which the freeze read must happen, and warn you weeks ahead.
-  Never change bitcoin.conf yourself.
-- Disk: expected about 50 GB on D: when synced (you have 62 GB free). Do not fill D: with other big files.
+- The node keeps only a moving window of recent blocks. By projection only (not a promise), about 13,000 blocks, so block
+  972,269 would leave the window around mid-January 2027. The real date comes from your photos.
+- Disk: projected about 50 GB on D: when synced (you have 62 GB free). Do not fill D: with other big files.
 - The first sync downloads the whole chain (~770 GB, kept only partly). It continues where it stopped each time you run line 8.
 - The post day (step H) and the freeze read (step I) need the laptop ON at set times; I give you those times in advance.
```
