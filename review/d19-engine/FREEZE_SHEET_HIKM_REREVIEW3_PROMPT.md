# Independent re-review 3: freeze sheet after HK3-R1

You are an independent adversarial reviewer (read-only), not an authority. Your re-review 2 `review/d19-engine/SOL6_FREEZE_SHEET_HIKM_REREVIEW2_394E4C0.md` found HK3-R1 (with adjudication). Check only whether it is resolved by the diff below and whether the repair introduced a defect. New IDs `HK4-R1..`. Verdict: ACCEPT or FIX.

```diff
diff --git a/deploy/calibration/FREEZE_HELDOUT.md b/deploy/calibration/FREEZE_HELDOUT.md
index 1b99f19..0137680 100644
--- a/deploy/calibration/FREEZE_HELDOUT.md
+++ b/deploy/calibration/FREEZE_HELDOUT.md
@@ -101,12 +101,17 @@ If any of these fails, the post waits.
      - the change does not go to `A_Q1`.
 
      Only on my "OK (a)" do you **sign**.
-   - **(b) After signing, before broadcasting:** in the same Preview window, Export again and send me the **signed** hex. It is also public data. I check with the node:
+   - **(b) After signing, before broadcasting:** in the same Preview window, Export, then "Save to file" as `D:\Bitcoin\signed-post.txn` on the laptop. **The signed transaction stays on the laptop (HK3-R1).** Anyone holding it could broadcast it, so:
+     - it is not sent, pasted or committed anywhere before it is broadcast;
+     - I only read that file on the laptop, with the laptop node's `decoderawtransaction` and `testmempoolaccept` (which only test; neither broadcasts);
+     - I never use `sendrawtransaction`.
+
+     The checks:
      - `decoderawtransaction` shows the same inputs and outputs as in (a);
      - the fee (`F_Q1`'s value minus the outputs) divided by its `vsize` is at least the fresh `estimatesmartfee 6` rate, run right then;
      - `testmempoolaccept` accepts it.
 
-     Only on my "OK (b)" do you press **Broadcast**.
+     I record a report: txid, inputs and outputs, fee, `vsize`, the fresh estimate and the `testmempoolaccept` result. Only on my "OK (b)" do **you** press **Broadcast** in Electrum. After the broadcast, the file is deleted; the transaction is then public on the network.
 5. Send me the txid. A fee bump may replace it only with the identical OP_RETURN script (O-6a §7), and the replacement goes through 4 (a) and 4 (b) again.
 
 ## I. Acceptance and the post record (about 1 hour after inclusion, then same day)
```
