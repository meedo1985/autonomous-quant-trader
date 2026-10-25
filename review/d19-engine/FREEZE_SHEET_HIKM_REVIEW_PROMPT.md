# Independent review: freeze sheet steps H, I, K, M (laptop node, FP3) and the drand verifier

You are an independent adversarial reviewer (read-only), not an authority. Review the change
`git diff ace34e4 d5e7843 -- deploy/calibration/FREEZE_HELDOUT.md` (below) and the verifier
`deploy/calibration/drand-verify/` (verify.mjs, package.json, package-lock.json, README.md) with its test
record `review/fp3/verifier-test-2026-10-25/RESULTS.txt`.

Governing inputs: the bound FP3 text `review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md` (quicknet; no time
limit); the open FP4 items it must close (`review/fp4-node/ADJUDICATION_FP4_NODE.md`,
`ADJUDICATION_FP4_NODE_REREVIEW.md`, `SOL_FP4_NODE_REREVIEW2.md` adjudication: FP4N-R2/FP4N2-R2 node acceptance
time, FP4N-R3 scan gate incl. scanblocks completed:true, FP4N-R4 fee); GOV-FP3-6 (drand check apart from the
O-6a record); FP3S4-G2 (bound on the gap between the drand output and the run start); the preregistration
§4 (DF5-2 two records, failure boundary) and §8; O-6a SPEC §4-§7; the laptop node steps
`review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt`.

Check: (1) are those items now correctly and completely handled; (2) is any step wrong for Bitcoin Core 31.1
on Windows (RPC names/arguments: scanblocks, getdescriptoractivity, getindexinfo, getblock, estimatesmartfee;
debug.log UpdateTip format; shrinkdebugfile), or for drand (endpoints, verification); (3) does the verifier
really verify (offline use of fetchBeacon, the pre-checks, randomness, exit codes), and is the test adequate;
(4) does anything conflict with the preregistration, the FP3 text or O-6a, or create a selective-outcome
route; (5) any other defect. Verify against official Bitcoin Core / drand sources where possible.
Findings: IDs `HK-R1`, ... with severity, place, failure scenario, minimal repair. Verdict: ACCEPT or FIX.

## Sheet diff

```diff
diff --git a/deploy/calibration/FREEZE_HELDOUT.md b/deploy/calibration/FREEZE_HELDOUT.md
index 5d82ff5..ca37f02 100644
--- a/deploy/calibration/FREEZE_HELDOUT.md
+++ b/deploy/calibration/FREEZE_HELDOUT.md
@@ -1,6 +1,6 @@
 # Freeze, `AQTQ1` post and held-out certification (D-19 attempt 1)
 
-**Status: DRAFT, 2026-10-24. Not usable yet.** Three preconditions are open (FP2, FP3, FP4, §0), and FP3 needs a formal governance step that the AI cannot author or activate. Every `<<...>>` blank is filled only when its input exists. Prepared while the development run (FULL_RUN.md step E) goes; nothing here touches the server until you start step G, except step G0 (installing the build checkout), which may run as soon as PR #77 is merged (FS2-R1).
+**Status: DRAFT, 2026-10-24, updated 2026-10-25. Not usable yet.** FP2 holds, and FP3 is bound by the owner's signed supplementary acceptance. FP1 (development run) and FP4 (laptop node, syncing) are open (§0). Every `<<...>>` blank is filled only when its input exists. Prepared while the development run (FULL_RUN.md step E) goes; nothing here touches the server until you start step G, except step G0 (installing the build checkout), which may run as soon as PR #77 is merged (FS2-R1).
 
 **What it is.** Freeze-order steps 5, 6 and 7 of the preregistration (§4): build and commit the qualification object, post its hash on Bitcoin (`AQTQ1`, O-6a SPEC rev 5 `84fca9c` §3-§7 by substitution), read the freeze point, fix the drand round, run the held-out certification (§6, §13 rev 7g items 3 and 6) and certify. Step G and everything after it start only after FULL_RUN.md step F. Forward paper keeps running, and nothing here touches it.
 
@@ -15,7 +15,7 @@
 |---|---|---|---|
 | FP1 | FULL_RUN.md steps E and F done: `Exited (0)`, all 104 ids at `24 dev/`, and `choices.json` received with `qualifies` true and `margin_ok` true (`d19.sh choose` exit 0). Exit 3 (`margin_failed`) goes to you to decide (I1-6) | FULL_RUN.md E, F; `calibration/qobj.py` `build` | open (run going) |
 | FP2 | A merged build change, with its independent review and **your §16 PR review** (PR #77; Astra reviews `ASTRA_FP2_BUILD_*.md`, last ACCEPT at `05321c5`): (a) `d19.sh freeze <build commit>`, which runs `qobj.build` inside the pinned image with the run's checkout `/opt/aqt-d19/app` (`eeaa728`) as `run_root`, and as `root` a disposable clone, owned by uid 990, of a second, root-owned checkout of the merged build commit (`build` fetches the live remote into the clone, QO-2, so `freeze` is the one engine command with network, BUILD-1). It refuses unless that checkout is at exactly the commit you name, unmodified, and writable by root only; (b) `d19.sh heldout <attempt> <posted hash> <round> <randomness>` and `d19.sh certify <attempt> <posted hash>`, which run `scripts/d19_heldout.py run` and `certify` from `/app`, plus a `heldout-status` that shows state, times and chunk counts only (P18-6); `certify` runs once per attempt and prints its report; (c) `review/d19-engine/FREEZE_REVIEWS.json`, listing `mapping.py`, `screen.py` and `heldout.py` with their SHA-256 and a committed review record each. Without (c), `build` refuses (BO-4, QO-5). (d) **Installed** by step G0: `/opt/aqt-d19/build` at `ed0bfbfa7a544f6e925d72d77734007a51d2c77e`, verified as the full commit there, root-owned, with the repository's GitHub origin, while `/opt/aqt-d19/app` stays at `eeaa728`; FP2 holds only once G0's checks pass and their output is recorded (FH-5, FP2-R2) | `calibration/qobj.py` (`LATER`, `REVIEWED`, `FREEZE_REVIEWS`); `d19.sh` has none of these commands at `eeaa728`; PR #77 | **holds** (2026-10-25): PR #77 merged as `ed0bfbf` after your §16 review (`review/d19-engine/OWNER_REVIEW_PR77.md`) and Astra delta review ACCEPT; (d) step G0 passed, `review/d19-engine/G0_EVIDENCE.md` |
-| FP3 | **The drand chain is fixed, by chain hash and public key, before step G.** Prereg §8 takes the round from "the C2 drand chain (DRAFT §2.0)", and DRAFT §2.0 leaves that chain as `<<SIGNING: chain hash, public key>>` in the unsigned C2 draft; a draft placeholder binds nothing. Until a formal step binds it, the held-out anchor has no defined input. It must be bound before the post at the latest: a chain chosen once beacon outputs are known would let its choice pick the outcome. The same step settles whether DRAFT §2.0's failure rule (no verifying output within 7 days of the round's scheduled time) applies to D-19 (step K) | prereg §8; `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md` lines 161, 165, 340 | **open, governance** (Constitution amendment process or C2 signing; AI cannot author, merge or activate it) |
+| FP3 | **The drand chain is fixed, by chain hash and public key, before step G.** Prereg §8 takes the round from "the C2 drand chain (DRAFT §2.0)", and DRAFT §2.0 leaves that chain as `<<SIGNING: chain hash, public key>>` in the unsigned C2 draft; a draft placeholder binds nothing. Until a formal step binds it, the held-out anchor has no defined input. It must be bound before the post at the latest: a chain chosen once beacon outputs are known would let its choice pick the outcome. The same step settles whether DRAFT §2.0's failure rule (no verifying output within 7 days of the round's scheduled time) applies to D-19 (step K) | prereg §8; `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md` lines 161, 165, 340 | **bound** (2026-10-25): quicknet and "no time limit", by the owner's signed supplementary acceptance `review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md` (commit `d7720be`, GitHub-verified, pushed 11:31:06Z; evidence `review/fp3/FP3_BINDING_EVIDENCE.md`). Step K still to be updated to it before G |
 | FP4 | A verifier Bitcoin Core node, version 30.0 or later, `-blockfilterindex=1`, keeping every block from height 972,269 (`F_Q1`) to the freeze read. A pruned node is enough if its prune target keeps that range (block filters with pruning: upstream PR #15946; confirm in the 30.x docs before use). It needs an initial sync of the whole chain, about 1-3 days of download. It also gives the fee estimate for the post (step H). Where it runs: **your laptop** (your decision Q-F1, 2026-10-25), set up by `review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt` (Codex review `SOL_FP4_NODE_REVIEW.md`, adjudication `ADJUDICATION_FP4_NODE.md`; FP4N-R2, R3 scan gate and R4 stay open and block step H) | O-6a SPEC §4, §7 | **open**: syncing; holds once synced with `pruneheight <= 972269` and the filter index synced |
 | FP5 | The Electrum 4.8.2 wallet holding `A_Q1`'s key is on your laptop, and both explorers show `A_Q1` never spent from and holding only `F_Q1` (OF1-3), checked on the day of the post | KEY_RECORD_DRAFT.md; ACCEPTANCE_RECORD.md §2 | checked on the day |
 | FP6 | The post can be included by `D_Q1` = 1,000,000. `F_Q1` (5,500 sat) covers a fee rate up to about 30 sat/vB with change above dust, so the post waits for fees below that | ACCEPTANCE_RECORD.md | checked on the day |
@@ -58,7 +58,18 @@ I check the copy before anything else: the file list is exactly the object's, ev
 
 ## H. The `AQTQ1` post (you, on your laptop; about 1 hour)
 
-1. Check FP5 and FP6 on mempool.space and blockstream.info (I give you the two links).
+**H0. Node ready (the day before, and again just before the post; FP4N-R3, FP4N-R2).** I run these on the laptop node and record each output:
+- **Sync and retention.** `getblockchaininfo` shows `chain` = `main`, `initialblockdownload` = false, `blocks` = `headers`, and the height equal to both explorers' tip (within 2 blocks). It also shows `pruneheight` ≤ 972,269.
+- **Filter index.** `getindexinfo` shows `basic block filter index` `synced` = true, at `best_block_height` = `blocks`.
+- **Oldest block readable.** `getblock` of the block at height 972,269 succeeds.
+- **Wallet history from the node.** `scanblocks start ["addr(A_Q1)"] 972269` with `filter_false_positives=true` returns `completed` = true, with `from_height` 972,269 and `to_height` = the tip. Then `getdescriptoractivity` over the blocks it found, with `include_mempool=false`, succeeds. The node shows only `F_Q1` at `A_Q1`.
+- **Laptop setup.** I add `shrinkdebugfile=0` to `D:\Bitcoin\bitcoin.conf` and restart the node, so its log keeps the acceptance line (step I).
+- **Clock.** The laptop clock is checked against a time server (`w32tm /stripchart /computer:time.windows.com /samples:3 /dataonly`). The offset must be under 2 seconds.
+- **Power.** Sleep is turned off from the broadcast until step I.2 is done.
+
+If any of these fails, the post waits.
+
+1. Check FP5 and FP6 on mempool.space and blockstream.info (I give you the two links), as well as on the node (H0).
 2. In the `A_Q1` Electrum wallet, Send, "Pay to" exactly this one line (I fill the hash in a Notepad file; copy it from there):
 
    ```
@@ -66,7 +77,7 @@ I check the copy before anything else: the file list is exactly the object's, ev
    ```
 
    Electrum turns it into the 39-byte script `6a 25 41 51 54 51 31` followed by the 32 bytes of the hash (its `script(...)` output syntax, `electrum/payment_identifier.py` at 4.8.2). The whole coin minus the fee goes to a change address of the same wallet, never `A_Q1` itself.
-3. Fee: at least the verifier node's `estimatesmartfee 6` (FP4; I give you the command and record its output), and no more than the coin allows (FP6). Electrum's or an explorer's estimate does not count (O-6a §7, FH-6). Keep "Replace-by-fee" on. If the node's estimate is above what the coin allows, wait.
+3. Fee: at least the verifier node's `estimatesmartfee 6`, run within the hour before you sign (FP4, FP4N-R4). I record its output. It must contain a number `feerate` and no `errors`, or we wait. The fee rate in sat/vB is `feerate` × 100,000. The fee is no more than the coin allows (FP6). Electrum's or an explorer's estimate does not count (O-6a §7, FH-6). Keep "Replace-by-fee" on. If the node's estimate is above what the coin allows, wait.
 4. **Do not broadcast yet.** Use Preview, then Export, copy the transaction hex and send it to me. It is public data: it holds no key. I decode it and check: it spends `F_Q1` only; exactly one OP_RETURN output, value 0, script exactly as above; the change is not `A_Q1`; the fee rate. Only on my "OK" do you sign and broadcast.
 5. Send me the txid. A fee bump may replace it only with the identical OP_RETURN script (O-6a §7).
 
@@ -79,12 +90,18 @@ At 6 confirmations the post is accepted. Inclusion height `h` = <<h>>; acceptanc
    - `https://blockstream.info/api/block-height/<<h+5>>`
 
    Never request removal of any capture (O-6a §5, OF4-1).
-2. **On the node** (commands given then): `scanblocks` over `addr(A_Q1)` from 972,269 to the tip with `filter_false_positives=true`, then `getdescriptoractivity` over the blocks found with `include_mempool=false`; the raw post, the funding transaction, the inclusion block hash, `gettxoutproof`, the acceptance-tip hash, and the time the node first saw the post accepted. **Send me** the output. I cross-check both explorers, write the post record (O-6a §4) and commit it. A disagreement blocks the attempt until it is resolved.
+2. **On the node** (I run these on the laptop; the laptop stays on, awake and caught up from the broadcast until this is done):
+   - **The node's own acceptance time (FP4N-R2, FP4N2-R2).** The `UpdateTip` line in `D:\Bitcoin\debug.log` whose `best=` is the acceptance-tip hash at height `h + 5`. Its log-prefix UTC timestamp is "the time the node first saw the post accepted". It is never the block's own `date` field. I commit that line and the lines around it, with the SHA-256 of the whole log file. The acceptance tip must descend from the inclusion block, which `gettxoutproof` and the raw post tie to `h`.
+     - If the laptop was not caught up continuously from the broadcast to that line, or the line is missing, or the clock check of H0 was not met, the attempt stops before step J, for your decision. The time is never rebuilt from an explorer.
+   - **The scan gate (FP4N-R3).** All of H0's checks again, run with the post included. `scanblocks` over `addr(A_Q1)` from 972,269 to the tip with `filter_false_positives=true` must return `completed` = true, with the heights it covered recorded. Then `getdescriptoractivity` over the blocks found, with `include_mempool=false`, must succeed. `pruneheight` must be ≤ 972,269.
+   - **The post itself:** the raw post, the funding transaction, the inclusion block hash, `gettxoutproof` and the acceptance-tip hash.
+
+   I cross-check both explorers, write the post record (O-6a §4) and commit it. A disagreement blocks the attempt until it is resolved.
 3. After the record is committed, destroy `A_Q1`'s key (O-6a §7, AI default). Keep `A_Q2`'s wallet safe: attempt 2 may need it.
 
 ## J. Freeze read (7 days after the node first saw the post accepted)
 
-On <<FREEZE_READ_TIME>> (I compute it from step I). The read is made **once**. Nothing here needs you: the Internet Archive's index is public, so I make the read from your laptop with `curl`, which keeps the exact bytes (FH-1). For each of the two URLs, I save and commit:
+On <<FREEZE_READ_TIME>>: the node's acceptance time from step I.2 plus exactly 7 days. The laptop must be on and online at that time. The read is made **once**. Nothing here needs you: the Internet Archive's index is public, so I make the read from your laptop with `curl`, which keeps the exact bytes (FH-1). For each of the two URLs, I save and commit:
 - the exact CDX query URI (exact URL match, no collapsing), and every page of the reply, until the index reports no further page;
 - for every page: the complete raw response bytes, the response headers and status, the retrieval time (UTC) and the SHA-256 of the bytes;
 - the candidates: every CDX row of either URL with an exact URL match and archived status 200, in timestamp order across both URLs (FH2-1). From the earliest, each gets its `id_` fetch of that exact row's original URL and timestamp: the raw body, headers and status (including `x-archive-src` and `x-archive-orig-date`) and the body's SHA-256. A candidate qualifies when that fetch's URL, timestamp and digest equal its CDX row's (O-6a §5, OS3-1) and its body equals the frozen acceptance-tip block hash. Every candidate before the first that qualifies keeps its fetch evidence and the reason it does not qualify.
@@ -95,15 +112,32 @@ Then, in the same committed record:
 
 No qualifying capture: the attempt is void (§4 failure boundary); go to attempt 2.
 
-## K. Before the held-out run: the two committed records (DF5-2)
-
-**Record 1, the invalidation check.** A check of **every** O-6a invalidation condition for attempt 1, each with its evidence, made from the node and both explorers on the day:
+## K. Before the held-out run: the drand record, then the two committed records (DF5-2)
+
+**The drand record (FP3; kept apart from the O-6a records, GOV-FP3-6).** FP3 binds `quicknet` with no time limit (`review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md`, Rules 2-6).
+- **Fetching.** From the freeze read onward, and also after the round's scheduled time, I fetch the round from at least two drand endpoints with `curl`. Any source is allowed, for example `api.drand.sh` and `drand.cloudflare.com`. I save each raw response, with its source and retrieval time.
+- **Verifying.** `deploy/calibration/drand-verify/verify.mjs` (pinned `drand-client` 1.4.2, tested in `review/fp3/verifier-test-2026-10-25/`) must exit 0 on the stored chain info `review/fp3/drand-info-2026-10-25/52db9ba7….info.json`. I record:
+  - the round and its scheduled time (1692803367 + (round − 1) × 3);
+  - the signature;
+  - the randomness, computed as the SHA-256 of the raw signature bytes;
+  - the verifier's output.
+- **Committed and pushed** before record 1.
+- **If no verifying output can be obtained yet:** the run waits, with no time limit, and I record one fetch attempt per day. A missing or late output never voids the attempt and never permits another round or source (Rule 5). If the chain stops for good, the attempt waits for your new formal decision (Rule 6).
+
+**Timing limit (FP3S4-G2).**
+- Record 1 is made, committed and pushed within 24 hours after the drand record's commit.
+- Record 2's `S` is at least 1 hour and at most 24 hours after record 1's commit.
+- If either limit is missed, record 1 is made again, fresh, before a new `S`.
+- Record 1's checks are the full list below, never a selection.
+
+**Record 1, the invalidation check.** A check of **every** O-6a invalidation condition for attempt 1, each with its evidence, made from the node (H0's checks with `pruneheight` ≤ 972,269, and the scan gate of step I.2) and from both explorers on the day:
 - the first post is well-formed, spends `F_Q1`, and carries the committed object's hash;
 - no later spend from `A_Q1`;
 - the inclusion block, the order of posts and the acceptance tip are unchanged on the main chain;
 - inclusion at height ≤ `D_Q1`;
-- a qualifying capture was listed at the freeze read, and no earlier one giving a different round has been shown;
-- the round's output: I fetch it from drand with `curl` and record the round, its scheduled time, the raw response, the randomness, the signature, the retrieval time, and that the signature verifies against the FP3 public key (not checked by the engine, HO-4). The fetch is made after the freeze read **and** after the round's scheduled time, whichever is later (usually the same day as the freeze read; later if the first qualifying capture came late, FH3-1), and within 7 days of the scheduled time. Its recorded retrieval time is the evidence that a verifying output existed within those 7 days (FH2-3). How a missing output is treated is fixed by FP3's formal outcome, before step G: where DRAFT §2.0's rule binds, no verifying output retrieved within the 7 days invalidates the attempt before evaluation, so it is void (§4 failure boundary); otherwise the rule FP3 settles applies.
+- a qualifying capture was listed at the freeze read, and no earlier one giving a different round has been shown.
+
+The drand output is not an O-6a condition. It is the drand record above (FP3 Rule 5: there is no void for a missing output).
 
 An invalidation not listed in this record counts as found at or after the start (DF5-2).
 
@@ -116,7 +150,7 @@ cd /opt/aqt-d19/build/deploy/calibration
 until [ "$(date -u +%s)" -ge <<START_EPOCH>> ]; do sleep 5; done; sudo sh d19.sh heldout 1 <<QUALIFICATION_OBJECT_SHA256>> <<ROUND>> <<RANDOMNESS>>
 ```
 
-The first part waits until record 2's time `S` (`<<START_EPOCH>>` is `S` in seconds; I fill both). Run it in good time before `S` and leave the window open until it prints that the run started.
+The first part waits until record 2's time `S` (`<<START_EPOCH>>` is `S` in seconds; I fill both). `<<ROUND>>` and `<<RANDOMNESS>>` are the round and the computed randomness from the drand record (step K), copied exactly. Run it in good time before `S` and leave the window open until it prints that the run started.
 
 `docker.io`, `containerd` and `runc` stay on hold until step M (DEV_RUN_START_EVIDENCE.md). Weekly check: `heldout-status` (chunk counts only) and forward paper status. **Nothing shows held-out event content before `certify`** (§13 item 6, P18-6); do not run any other command on the held-out store. On `Exited` with a code other than 0, collect and stop, as in FULL_RUN.md D: a resume continues from the last finished chunk.
 
@@ -131,7 +165,7 @@ sudo sh d19.sh certify 1 <<QUALIFICATION_OBJECT_SHA256>>
 
 Exit 0: every test is within its target (§6). Exit 2: not. Either way, **send me** the report; I commit it.
 
-**Before your decision, the invalidation check again (FH-2).** I repeat record 1's chain and capture checks (not the CDX freeze read itself, which is never repeated) and commit them. Anything found now, or reported at any time from the run's start until your decision, was found at or after the start: the attempt has **failed**, whatever `certify` said (§4 failure boundary).
+**Before your decision, the invalidation check again (FH-2).** I repeat record 1's chain and capture checks (not the CDX freeze read itself, which is never repeated) and commit them. The node part needs H0's checks and the scan gate again, with `pruneheight` ≤ 972,269. The node's storage is sized for this (FP4 retention; your choice to free space on D:). If the node can no longer scan from 972,269, nothing is decided: it stops here for your decision. Anything found now, or reported at any time from the run's start until your decision, was found at or after the start: the attempt has **failed**, whatever `certify` said (§4 failure boundary).
 
 Then you accept or reject the certification result (§12 item 4). A failure leaves promotion blocked; attempt 2 needs a recorded change. After step M, unhold Docker: `sudo apt-mark unhold docker.io containerd runc`.
 
```
