# Independent re-review 2: freeze sheet after HK2-R1, HK2-R2

You are an independent adversarial reviewer (read-only), not an authority. Your re-review `review/d19-engine/SOL6_FREEZE_SHEET_HIKM_REREVIEW_CB9147A.md` found HK2-R1, HK2-R2 (with adjudication). Check only whether they are resolved by the diff below and whether the repair introduced a defect. New IDs `HK3-R1..`. Verdict: ACCEPT or FIX.

```diff
diff --git a/deploy/calibration/FREEZE_HELDOUT.md b/deploy/calibration/FREEZE_HELDOUT.md
index 9ef40dd..1b99f19 100644
--- a/deploy/calibration/FREEZE_HELDOUT.md
+++ b/deploy/calibration/FREEZE_HELDOUT.md
@@ -93,9 +93,21 @@ If any of these fails, the post waits.
    - once to set the fee before you sign;
    - again **immediately before each broadcast**, including any replacement.
 
-   Each output must contain a number `feerate` and no `errors`, or we wait. The fee rate in sat/vB is `feerate` × 100,000. The transaction's actual rate (fee ÷ virtual size, from my decode) must be at least the rate from the check just before broadcast; if not, it is not broadcast. The fee is no more than the coin allows (FP6). Electrum's or an explorer's estimate does not count (O-6a §7, FH-6). Keep "Replace-by-fee" on. If the node's estimate is above what the coin allows, wait.
-4. **Do not broadcast yet.** Use Preview, then Export, copy the transaction hex and send it to me. It is public data: it holds no key. I decode it and check: it spends `F_Q1` only; exactly one OP_RETURN output, value 0, script exactly as above; the change is not `A_Q1`; the fee rate. Only on my "OK" do you sign and broadcast.
-5. Send me the txid. A fee bump may replace it only with the identical OP_RETURN script (O-6a §7).
+   Each output must contain a number `feerate` and no `errors`, or we wait. The fee rate in sat/vB is `feerate` × 100,000. The **signed** transaction's actual rate must be at least the rate from the check just before broadcast; if not, it is not broadcast (step 4). The actual rate is the fee ÷ its virtual size, from the node's `decoderawtransaction` of the signed hex; signing adds witness data, so an unsigned decode does not count. The fee is no more than the coin allows (FP6). Electrum's or an explorer's estimate does not count (O-6a §7, FH-6). Keep "Replace-by-fee" on. If the node's estimate is above what the coin allows, wait.
+4. **Do not broadcast yet: two checks (HK2-R2).**
+   - **(a) Before signing:** Use Preview, then Export. Copy the unsigned transaction hex and send it to me. It is public data and holds no key. I decode it and check:
+     - it spends `F_Q1` only;
+     - it has exactly one OP_RETURN output, value 0, with the script exactly as above;
+     - the change does not go to `A_Q1`.
+
+     Only on my "OK (a)" do you **sign**.
+   - **(b) After signing, before broadcasting:** in the same Preview window, Export again and send me the **signed** hex. It is also public data. I check with the node:
+     - `decoderawtransaction` shows the same inputs and outputs as in (a);
+     - the fee (`F_Q1`'s value minus the outputs) divided by its `vsize` is at least the fresh `estimatesmartfee 6` rate, run right then;
+     - `testmempoolaccept` accepts it.
+
+     Only on my "OK (b)" do you press **Broadcast**.
+5. Send me the txid. A fee bump may replace it only with the identical OP_RETURN script (O-6a §7), and the replacement goes through 4 (a) and 4 (b) again.
 
 ## I. Acceptance and the post record (about 1 hour after inclusion, then same day)
 
@@ -117,9 +129,9 @@ At 6 confirmations the post is accepted. Inclusion height `h` = <<h>>; acceptanc
 
 ## J. Freeze read (7 days after the node first saw the post accepted)
 
-On <<FREEZE_READ_TIME>>: the node's acceptance time from step I.2 plus exactly 7 days. The laptop must be on and online at that time. The read starts within the hour after that time. Each request's recorded retrieval time is the proof.
+On <<FREEZE_READ_TIME>>: the node's acceptance time from step I.2 plus exactly 7 days. The laptop must be on and online at that time. **Every CDX index request** of the read (every page of both URLs) is made within the hour after that time. Each request's recorded retrieval time is the proof. The `id_` fetches of individual captures that follow are not index requests.
 
-**If the read cannot start within that hour, or its timing cannot be proved, the attempt stops there for your decision (HK-R1).** A later CDX query is never treated as the freeze read, because the index may have changed in between.
+**If any CDX index request cannot be completed within that hour, or its timing cannot be proved, the attempt stops there for your decision (HK-R1, HK2-R1).** A later CDX query is never treated as the freeze read, because the index may have changed in between.
 
 The read is made **once**. Nothing here needs you: the Internet Archive's index is public, so I make the read from your laptop with `curl`, which keeps the exact bytes (FH-1). For each of the two URLs, I save and commit:
 - the exact CDX query URI (exact URL match, no collapsing), and every page of the reply, until the index reports no further page;
```
