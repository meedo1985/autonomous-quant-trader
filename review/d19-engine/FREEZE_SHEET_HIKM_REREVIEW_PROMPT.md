# Independent re-review: freeze sheet steps H/I/J/K/M after HK-R1..R6

You are an independent adversarial reviewer (read-only), not an authority. Your review `review/d19-engine/SOL6_FREEZE_SHEET_HIKM_REVIEW_D5E7843.md` found HK-R1..R6; the adjudication `review/d19-engine/ADJUDICATION_FREEZE_SHEET_HIKM_D5E7843.md` and the repair diff below followed. Check only: (1) is each HK finding resolved; (2) any new defect introduced by the repairs. New IDs `HK2-R1..`. Verdict: ACCEPT or FIX. Do not re-open resolved findings unless the repair broke them.

## Repair diff

```diff
diff --git a/deploy/calibration/FREEZE_HELDOUT.md b/deploy/calibration/FREEZE_HELDOUT.md
index ca37f02..9ef40dd 100644
--- a/deploy/calibration/FREEZE_HELDOUT.md
+++ b/deploy/calibration/FREEZE_HELDOUT.md
@@ -58,11 +58,23 @@ I check the copy before anything else: the file list is exactly the object's, ev
 
 ## H. The `AQTQ1` post (you, on your laptop; about 1 hour)
 
-**H0. Node ready (the day before, and again just before the post; FP4N-R3, FP4N-R2).** I run these on the laptop node and record each output:
-- **Sync and retention.** `getblockchaininfo` shows `chain` = `main`, `initialblockdownload` = false, `blocks` = `headers`, and the height equal to both explorers' tip (within 2 blocks). It also shows `pruneheight` ≤ 972,269.
-- **Filter index.** `getindexinfo` shows `basic block filter index` `synced` = true, at `best_block_height` = `blocks`.
-- **Oldest block readable.** `getblock` of the block at height 972,269 succeeds.
-- **Wallet history from the node.** `scanblocks start ["addr(A_Q1)"] 972269` with `filter_false_positives=true` returns `completed` = true, with `from_height` 972,269 and `to_height` = the tip. Then `getdescriptoractivity` over the blocks it found, with `include_mempool=false`, succeeds. The node shows only `F_Q1` at `A_Q1`.
+**Retention plan, before H (HK-R3).** The node must still hold block 972,269 at the step-M recheck, weeks after the post, while staying current. Its `prune=25000` is a moving size target, so before H:
+1. From the measured window after the first sync (`blocks` − `pruneheight`) and the projected step-M date plus 30 days, I compute the prune target that keeps 972,269 until then.
+2. You free that space on D: (your choice, `review/fp4-node/OWNER_ANSWERS_2026-10-25.md`).
+3. With your OK, I raise `prune=` in `D:\Bitcoin\bitcoin.conf` and restart the node, while `pruneheight` is still ≤ 972,269. Raising the target stops further deletion; it restores nothing.
+4. I commit the calculation and the node's readings.
+
+If the space cannot be found, the post waits. The node's stop rules (S1-S3 of `FP4_LAPTOP_NODE_STEPS.txt`) stay in force.
+
+**H0. Node ready (the day before, and again just before the post; FP4N-R3, FP4N-R2).** I run these on the laptop in Git Bash, with `B="C:/Program Files/Bitcoin/daemon/bitcoin-cli.exe"`. Each output is recorded. The command forms were tested on this node on 2026-10-25.
+- **Sync and retention.** `"$B" -datadir=D:/Bitcoin getblockchaininfo` shows:
+  - `chain` = `main`;
+  - `initialblockdownload` = false;
+  - `blocks` = `headers`, and equal to both explorers' tip (within 2 blocks);
+  - `pruneheight` ≤ 972269.
+- **Filter index.** `"$B" -datadir=D:/Bitcoin getindexinfo` shows `basic block filter index` with `synced` = true and `best_block_height` = `blocks`.
+- **Oldest block readable.** `H=$("$B" -datadir=D:/Bitcoin getblockhash 972269)`, then `"$B" -datadir=D:/Bitcoin getblock $H 0`, which must return the block.
+- **Wallet history from the node.** `"$B" -datadir=D:/Bitcoin -rpcclienttimeout=0 scanblocks start '["addr(<A_Q1>)"]' 972269 null basic '{"filter_false_positives":true}'` must return `completed` = true, `from_height` 972269 and `to_height` = the tip. Then `"$B" -datadir=D:/Bitcoin getdescriptoractivity '<relevant_blocks array from scanblocks>' '["addr(<A_Q1>)"]' false` must succeed and show only `F_Q1` received at `A_Q1`, and before the post nothing spent.
 - **Laptop setup.** I add `shrinkdebugfile=0` to `D:\Bitcoin\bitcoin.conf` and restart the node, so its log keeps the acceptance line (step I).
 - **Clock.** The laptop clock is checked against a time server (`w32tm /stripchart /computer:time.windows.com /samples:3 /dataonly`). The offset must be under 2 seconds.
 - **Power.** Sleep is turned off from the broadcast until step I.2 is done.
@@ -77,7 +89,11 @@ If any of these fails, the post waits.
    ```
 
    Electrum turns it into the 39-byte script `6a 25 41 51 54 51 31` followed by the 32 bytes of the hash (its `script(...)` output syntax, `electrum/payment_identifier.py` at 4.8.2). The whole coin minus the fee goes to a change address of the same wallet, never `A_Q1` itself.
-3. Fee: at least the verifier node's `estimatesmartfee 6`, run within the hour before you sign (FP4, FP4N-R4). I record its output. It must contain a number `feerate` and no `errors`, or we wait. The fee rate in sat/vB is `feerate` × 100,000. The fee is no more than the coin allows (FP6). Electrum's or an explorer's estimate does not count (O-6a §7, FH-6). Keep "Replace-by-fee" on. If the node's estimate is above what the coin allows, wait.
+3. Fee: at least the verifier node's `estimatesmartfee 6` (FP4, FP4N-R4, HK-R4). It is run twice, and both outputs are recorded:
+   - once to set the fee before you sign;
+   - again **immediately before each broadcast**, including any replacement.
+
+   Each output must contain a number `feerate` and no `errors`, or we wait. The fee rate in sat/vB is `feerate` × 100,000. The transaction's actual rate (fee ÷ virtual size, from my decode) must be at least the rate from the check just before broadcast; if not, it is not broadcast. The fee is no more than the coin allows (FP6). Electrum's or an explorer's estimate does not count (O-6a §7, FH-6). Keep "Replace-by-fee" on. If the node's estimate is above what the coin allows, wait.
 4. **Do not broadcast yet.** Use Preview, then Export, copy the transaction hex and send it to me. It is public data: it holds no key. I decode it and check: it spends `F_Q1` only; exactly one OP_RETURN output, value 0, script exactly as above; the change is not `A_Q1`; the fee rate. Only on my "OK" do you sign and broadcast.
 5. Send me the txid. A fee bump may replace it only with the identical OP_RETURN script (O-6a §7).
 
@@ -101,7 +117,11 @@ At 6 confirmations the post is accepted. Inclusion height `h` = <<h>>; acceptanc
 
 ## J. Freeze read (7 days after the node first saw the post accepted)
 
-On <<FREEZE_READ_TIME>>: the node's acceptance time from step I.2 plus exactly 7 days. The laptop must be on and online at that time. The read is made **once**. Nothing here needs you: the Internet Archive's index is public, so I make the read from your laptop with `curl`, which keeps the exact bytes (FH-1). For each of the two URLs, I save and commit:
+On <<FREEZE_READ_TIME>>: the node's acceptance time from step I.2 plus exactly 7 days. The laptop must be on and online at that time. The read starts within the hour after that time. Each request's recorded retrieval time is the proof.
+
+**If the read cannot start within that hour, or its timing cannot be proved, the attempt stops there for your decision (HK-R1).** A later CDX query is never treated as the freeze read, because the index may have changed in between.
+
+The read is made **once**. Nothing here needs you: the Internet Archive's index is public, so I make the read from your laptop with `curl`, which keeps the exact bytes (FH-1). For each of the two URLs, I save and commit:
 - the exact CDX query URI (exact URL match, no collapsing), and every page of the reply, until the index reports no further page;
 - for every page: the complete raw response bytes, the response headers and status, the retrieval time (UTC) and the SHA-256 of the bytes;
 - the candidates: every CDX row of either URL with an exact URL match and archived status 200, in timestamp order across both URLs (FH2-1). From the earliest, each gets its `id_` fetch of that exact row's original URL and timestamp: the raw body, headers and status (including `x-archive-src` and `x-archive-orig-date`) and the body's SHA-256. A candidate qualifies when that fetch's URL, timestamp and digest equal its CDX row's (O-6a §5, OS3-1) and its body equals the frozen acceptance-tip block hash. Every candidate before the first that qualifies keeps its fetch evidence and the reason it does not qualify.
@@ -115,19 +135,25 @@ No qualifying capture: the attempt is void (§4 failure boundary); go to attempt
 ## K. Before the held-out run: the drand record, then the two committed records (DF5-2)
 
 **The drand record (FP3; kept apart from the O-6a records, GOV-FP3-6).** FP3 binds `quicknet` with no time limit (`review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md`, Rules 2-6).
-- **Fetching.** From the freeze read onward, and also after the round's scheduled time, I fetch the round from at least two drand endpoints with `curl`. Any source is allowed, for example `api.drand.sh` and `drand.cloudflare.com`. I save each raw response, with its source and retrieval time.
+- **Fetching.** From the freeze read onward, and also after the round's scheduled time, I fetch the round with `curl` from at least two endpoints, always with the chain hash in the path. A bare `/public/<round>` is a different chain. With `Q` = `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971`, the URLs are:
+  - `https://api.drand.sh/v2/chains/$Q/rounds/<round>`
+  - `https://api.drand.sh/$Q/public/<round>`
+  - `https://drand.cloudflare.com/$Q/public/<round>`
+
+  Another relay serving the same round of this chain is allowed (FP3 Rule 4). I save each raw response, with its source and retrieval time.
 - **Verifying.** `deploy/calibration/drand-verify/verify.mjs` (pinned `drand-client` 1.4.2, tested in `review/fp3/verifier-test-2026-10-25/`) must exit 0 on the stored chain info `review/fp3/drand-info-2026-10-25/52db9ba7….info.json`. I record:
   - the round and its scheduled time (1692803367 + (round − 1) × 3);
   - the signature;
   - the randomness, computed as the SHA-256 of the raw signature bytes;
   - the verifier's output.
 - **Committed and pushed** before record 1.
-- **If no verifying output can be obtained yet:** the run waits, with no time limit, and I record one fetch attempt per day. A missing or late output never voids the attempt and never permits another round or source (Rule 5). If the chain stops for good, the attempt waits for your new formal decision (Rule 6).
+- **If no verifying output can be obtained yet:** the run waits, with no time limit, and I record one fetch attempt per day. A missing or late output never voids the attempt and never permits another chain, round or randomness source (Rule 5). If the chain stops for good, the attempt waits for your new formal decision (Rule 6).
 
 **Timing limit (FP3S4-G2).**
-- Record 1 is made, committed and pushed within 24 hours after the drand record's commit.
-- Record 2's `S` is at least 1 hour and at most 24 hours after record 1's commit.
-- If either limit is missed, record 1 is made again, fresh, before a new `S`.
+The anchor is the first commit of the drand record. It is never reset (HK-R2).
+- Record 1 is made, committed and pushed within 24 hours after that anchor.
+- Record 2's `S` is at least 1 hour after record 1's commit, and at most 48 hours after the anchor.
+- If either limit is missed, the attempt stops there for your decision. A fresh record 1 does not restart the clock.
 - Record 1's checks are the full list below, never a selection.
 
 **Record 1, the invalidation check.** A check of **every** O-6a invalidation condition for attempt 1, each with its evidence, made from the node (H0's checks with `pruneheight` ≤ 972,269, and the scan gate of step I.2) and from both explorers on the day:
```
