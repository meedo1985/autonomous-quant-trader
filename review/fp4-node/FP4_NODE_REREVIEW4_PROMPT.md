# Independent re-review 4: FP4 laptop node steps, revision 5

You are an independent adversarial reviewer (read-only), not an authority.
Your re-review 3 (`review/fp4-node/SOL_FP4_NODE_REREVIEW3.md`, with its adjudication) found FP4N4-R1, R2. Check only: are they resolved by the repair below (in particular: does `-connect=0` with `listen=0` prevent any block download and pruning in Bitcoin Core 31.1, and does `getblockchaininfo` then report the stored `pruneheight`); any new defect. New findings `FP4N5-R1`, ... Verdict: ACCEPT or FIX. Do not re-open resolved findings unless the repair broke them.

## Repair diff

```diff
diff --git a/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt b/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt
index 0584b00..843d1dc 100644
--- a/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt
+++ b/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt
@@ -1,6 +1,6 @@
 FP4 - Bitcoin verifier node on your LAPTOP (Bitcoin Core 31.1, pruned, block filters)
 Run each line in PowerShell on the laptop, ONE LINE AT A TIME. No keys or wallet go on this node.
-(Revision 4, after Codex reviews FP4N-R1..R7, FP4N2-R1..R3 and FP4N3-R1..R2; see ADJUDICATION_FP4_NODE*.md.)
+(Revision 5, after Codex reviews FP4N-R1..R7, FP4N2-R1..R3, FP4N3-R1..R2 and FP4N4-R1..R2; see ADJUDICATION_FP4_NODE*.md.)
 
 === ONCE: install ===
 
@@ -53,8 +53,8 @@ Start-Process "C:\Program Files\Bitcoin\daemon\bitcoind.exe" "-datadir=D:\Bitcoi
 11) Block-filter index state (I read: synced, best_block_height):
 & "C:\Program Files\Bitcoin\daemon\bitcoin-cli.exe" -datadir=D:\Bitcoin getindexinfo
 
-12) Disk space left on D: (GB, one decimal):
-[math]::Round((Get-PSDrive D).Free/1GB, 1)
+12) Disk space low? Prints True if D: has LESS than 8 GB free (then S1 applies), False if enough:
+(Get-PSDrive D).Free -lt 8GB
 
 13) Whole node folder size (GB; takes a few seconds):
 [math]::Round((Get-ChildItem D:\Bitcoin -Recurse -File | Measure-Object Length -Sum).Sum/1GB)
@@ -63,15 +63,20 @@ Start-Process "C:\Program Files\Bitcoin\daemon\bitcoind.exe" "-datadir=D:\Bitcoi
 
 === STOP RULES (they win over everything above) ===
 
-S1) Disk: if line 12 shows LESS THAN 8.0 GB free, run line 9 (stop) and do not start the node again until I say.
-S2) Keeping block 972,269. A caught-up node always keeps about the last W blocks (W = "blocks" minus "pruneheight",
-    which I read from your photos). So it drops block 972,269 when the PUBLIC chain reaches height 972,269 + W,
-    whether your laptop was on or off in between. From that, I write here a fixed date:
-      MARGIN LOW DATE: ____________ (I fill it after the first sync: the forecast date of public height
-                                    972,269 + W - 3,000, about 3 weeks early; I only ever move it EARLIER)
-    - On the MARGIN LOW DATE, or earlier if I say so: if the node is running, stop it (line 9). Do not start it
-      again until we decide together: raise the setting (only if disk allows), or the post must happen first.
-    - Until I have filled the date: if your last photo of line 10 is more than 14 days old, ask me before starting.
+S1) Disk: if line 12 prints True, run line 9 (stop) and do not start the node again until I say.
+S2) Keeping block 972,269. A caught-up node keeps about the last W blocks (W = "blocks" minus "pruneheight").
+    W is not fixed (the node keeps a size in bytes, so bigger blocks mean a smaller W). Three rules:
+    a) Every photo of line 10: I compute margin = 972,269 minus "pruneheight". If it is below 3,000 blocks,
+       I tell you STOP: run line 9 now, and do not start again until we decide together (raise the setting
+       only if disk allows, or the post must happen first).
+    b) A forecast only, never a permission:
+         MARGIN LOW DATE: ____________ (filled after the first sync; forecast date of public height
+                                       972,269 + W - 3,000; I only ever move it EARLIER)
+       On that date, the same as a STOP in (a).
+    c) SAFE START. Once I fill the date, and ALSO any time your last photo of line 10 is more than 7 days old,
+       never use line 8 directly. Instead start the node WITHOUT network (it cannot download or prune anything):
+       Start-Process "C:\Program Files\Bitcoin\daemon\bitcoind.exe" "-datadir=D:\Bitcoin","-connect=0"
+       wait one minute, run line 10, send me the photo, then run line 9. Use line 8 only after I reply GO.
     - If pruneheight ever goes ABOVE 972,269: the node no longer meets FP4. Step H stays blocked; only a fresh sync
       whose window can hold block 972,269 through the freeze read can fix it.
 S3) Never change bitcoin.conf yourself.
```
