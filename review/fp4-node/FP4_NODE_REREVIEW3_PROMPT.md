# Independent re-review 3: FP4 laptop node steps, revision 4

You are an independent adversarial reviewer (read-only), not an authority.
Your re-review 2 (`review/fp4-node/SOL_FP4_NODE_REREVIEW2.md`, with its adjudication) found FP4N3-R1, R2. Check only: are they resolved by the repair below; any new defect or other problem. New findings `FP4N4-R1`, ... Verdict: ACCEPT or FIX. Do not re-open resolved findings unless the repair broke them.

## Repair diff (`git diff db63261 ceaf0bc -- review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt`)

```diff
diff --git a/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt b/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt
index 52bf58d..0584b00 100644
--- a/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt
+++ b/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt
@@ -1,6 +1,6 @@
 FP4 - Bitcoin verifier node on your LAPTOP (Bitcoin Core 31.1, pruned, block filters)
 Run each line in PowerShell on the laptop, ONE LINE AT A TIME. No keys or wallet go on this node.
-(Revision 3, after Codex reviews FP4N-R1..R7 and FP4N2-R1..R3; see ADJUDICATION_FP4_NODE*.md.)
+(Revision 4, after Codex reviews FP4N-R1..R7, FP4N2-R1..R3 and FP4N3-R1..R2; see ADJUDICATION_FP4_NODE*.md.)
 
 === ONCE: install ===
 
@@ -53,8 +53,8 @@ Start-Process "C:\Program Files\Bitcoin\daemon\bitcoind.exe" "-datadir=D:\Bitcoi
 11) Block-filter index state (I read: synced, best_block_height):
 & "C:\Program Files\Bitcoin\daemon\bitcoin-cli.exe" -datadir=D:\Bitcoin getindexinfo
 
-12) Disk space left on D: (GB):
-[math]::Round((Get-PSDrive D).Free/1GB)
+12) Disk space left on D: (GB, one decimal):
+[math]::Round((Get-PSDrive D).Free/1GB, 1)
 
 13) Whole node folder size (GB; takes a few seconds):
 [math]::Round((Get-ChildItem D:\Bitcoin -Recurse -File | Measure-Object Length -Sum).Sum/1GB)
@@ -63,12 +63,17 @@ Start-Process "C:\Program Files\Bitcoin\daemon\bitcoind.exe" "-datadir=D:\Bitcoi
 
 === STOP RULES (they win over everything above) ===
 
-S1) Disk: if line 12 shows LESS THAN 8 GB free, run line 9 (stop) and do not start the node again until I say.
-S2) Keeping block 972,269: from your photos I compute the margin = 972,269 minus "pruneheight" (in blocks).
-    - margin below 3,000 (about 3 weeks of blocks): I tell you "MARGIN LOW". From then on, do not start the node (line 8)
-      until I say; we decide together: raise the setting (only if disk allows), or the post must happen first.
-    - If the laptop was off for more than 7 days after "MARGIN LOW": ask me before starting it (catching up can prune).
-    - If pruneheight ever goes ABOVE 972,269: the node no longer meets FP4. Step H stays blocked; only a fresh sync can fix it.
+S1) Disk: if line 12 shows LESS THAN 8.0 GB free, run line 9 (stop) and do not start the node again until I say.
+S2) Keeping block 972,269. A caught-up node always keeps about the last W blocks (W = "blocks" minus "pruneheight",
+    which I read from your photos). So it drops block 972,269 when the PUBLIC chain reaches height 972,269 + W,
+    whether your laptop was on or off in between. From that, I write here a fixed date:
+      MARGIN LOW DATE: ____________ (I fill it after the first sync: the forecast date of public height
+                                    972,269 + W - 3,000, about 3 weeks early; I only ever move it EARLIER)
+    - On the MARGIN LOW DATE, or earlier if I say so: if the node is running, stop it (line 9). Do not start it
+      again until we decide together: raise the setting (only if disk allows), or the post must happen first.
+    - Until I have filled the date: if your last photo of line 10 is more than 14 days old, ask me before starting.
+    - If pruneheight ever goes ABOVE 972,269: the node no longer meets FP4. Step H stays blocked; only a fresh sync
+      whose window can hold block 972,269 through the freeze read can fix it.
 S3) Never change bitcoin.conf yourself.
 
 Notes:
```
