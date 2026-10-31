# Freeze, `AQTQ1` post and held-out certification (D-19 attempt 1)

**Status: DRAFT, 2026-10-24, updated 2026-10-25. Not usable yet.** FP2 holds, and FP3 is bound by the owner's signed supplementary acceptance. FP1 (development run) and FP4 (laptop node, syncing) are open (§0). Every `<<...>>` blank is filled only when its input exists. Prepared while the development run (FULL_RUN.md step E) goes; nothing here touches the server until you start step G, except step G0 (installing the build checkout), which may run as soon as PR #77 is merged (FS2-R1).

**What it is.** Freeze-order steps 5, 6 and 7 of the preregistration (§4): build and commit the qualification object, post its hash on Bitcoin (`AQTQ1`, O-6a SPEC rev 5 `84fca9c` §3-§7 by substitution), read the freeze point, fix the drand round, run the held-out certification (§6, §13 rev 7g items 3 and 6) and certify. Step G and everything after it start only after FULL_RUN.md step F. Forward paper keeps running, and nothing here touches it.

**What can end it early, and how (§4).**
- `choices.json` says the method does not qualify (§5 step 6): there is no freeze and no post. The result is recorded; it is a valid result.
- An O-6a invalidation found **before** the held-out run starts: the attempt is **void**. No held-out run, the namespace is not burned, and the same object may be posted again with key `A_Q2` under namespace `d19-heldout-v2`, with no recorded change. A void attempt still uses up its key (DF5-1).
- An invalidation found **at or after** the start, or a certification that does not pass: the attempt **fails**. Its namespace is burned, nothing is retuned (P18-6), and attempt 2 needs a recorded change.

## 0. Preconditions: all are checked and recorded before step G

| # | Precondition | Source | State |
|---|---|---|---|
| FP1 | FULL_RUN.md steps E and F done: `Exited (0)`, all 104 ids at `24 dev/`, and `choices.json` received with `qualifies` true and `margin_ok` true (`d19.sh choose` exit 0). Exit 3 (`margin_failed`) goes to you to decide (I1-6) | FULL_RUN.md E, F; `calibration/qobj.py` `build` | open (run going) |
| FP2 | A merged build change, with its independent review and **your §16 PR review** (PR #77; Astra reviews `ASTRA_FP2_BUILD_*.md`, last ACCEPT at `05321c5`): (a) `d19.sh freeze <build commit>`, which runs `qobj.build` inside the pinned image with the run's checkout `/opt/aqt-d19/app` (`eeaa728`) as `run_root`, and as `root` a disposable clone, owned by uid 990, of a second, root-owned checkout of the merged build commit (`build` fetches the live remote into the clone, QO-2, so `freeze` is the one engine command with network, BUILD-1). It refuses unless that checkout is at exactly the commit you name, unmodified, and writable by root only; (b) `d19.sh heldout <attempt> <posted hash> <round> <randomness>` and `d19.sh certify <attempt> <posted hash>`, which run `scripts/d19_heldout.py run` and `certify` from `/app`, plus a `heldout-status` that shows state, times and chunk counts only (P18-6); `certify` runs once per attempt and prints its report; (c) `review/d19-engine/FREEZE_REVIEWS.json`, listing `mapping.py`, `screen.py` and `heldout.py` with their SHA-256 and a committed review record each. Without (c), `build` refuses (BO-4, QO-5). (d) **Installed** by step G0: `/opt/aqt-d19/build` at `ed0bfbfa7a544f6e925d72d77734007a51d2c77e`, verified as the full commit there, root-owned, with the repository's GitHub origin, while `/opt/aqt-d19/app` stays at `eeaa728`; FP2 holds only once G0's checks pass and their output is recorded (FH-5, FP2-R2) | `calibration/qobj.py` (`LATER`, `REVIEWED`, `FREEZE_REVIEWS`); `d19.sh` has none of these commands at `eeaa728`; PR #77 | **holds** (2026-10-25): PR #77 merged as `ed0bfbf` after your §16 review (`review/d19-engine/OWNER_REVIEW_PR77.md`) and Astra delta review ACCEPT; (d) step G0 passed, `review/d19-engine/G0_EVIDENCE.md` |
| FP3 | **The drand chain is fixed, by chain hash and public key, before step G.** Prereg §8 takes the round from "the C2 drand chain (DRAFT §2.0)", and DRAFT §2.0 leaves that chain as `<<SIGNING: chain hash, public key>>` in the unsigned C2 draft; a draft placeholder binds nothing. Until a formal step binds it, the held-out anchor has no defined input. It must be bound before the post at the latest: a chain chosen once beacon outputs are known would let its choice pick the outcome. The same step settles whether DRAFT §2.0's failure rule (no verifying output within 7 days of the round's scheduled time) applies to D-19 (step K) | prereg §8; `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md` lines 161, 165, 340 | **bound** (2026-10-25): quicknet and "no time limit", by the owner's signed supplementary acceptance `review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md` (commit `d7720be`, GitHub-verified, pushed 11:31:06Z; evidence `review/fp3/FP3_BINDING_EVIDENCE.md`). Step K still to be updated to it before G |
| FP4 | A verifier Bitcoin Core node, version 30.0 or later, `-blockfilterindex=1`, keeping every block from height 972,269 (`F_Q1`) to the freeze read. A pruned node is enough if its prune target keeps that range (block filters with pruning: upstream PR #15946; confirm in the 30.x docs before use). It needs an initial sync of the whole chain, about 1-3 days of download. It also gives the fee estimate for the post (step H). Where it runs: **your laptop** (your decision Q-F1, 2026-10-25), set up by `review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt` (Codex review `SOL_FP4_NODE_REVIEW.md`, adjudication `ADJUDICATION_FP4_NODE.md`; FP4N-R2, R3 scan gate and R4 stay open and block step H) | O-6a SPEC §4, §7 | **open**: syncing; holds once synced with `pruneheight <= 972269` and the filter index synced |
| FP5 | The Electrum 4.8.2 wallet holding `A_Q1`'s key is on your laptop, and both explorers show `A_Q1` never spent from and holding only `F_Q1` (OF1-3), checked on the day of the post | KEY_RECORD_DRAFT.md; ACCEPTANCE_RECORD.md §2 | checked on the day |
| FP6 | The post can be included by `D_Q1` = 1,000,000. `F_Q1` (5,500 sat) covers a fee rate up to about 30 sat/vB with change above dust, so the post waits for fees below that | ACCEPTANCE_RECORD.md | checked on the day |

Until FP1-FP4 hold, nothing below runs, except step G0, which is how FP2 (d) comes to hold; it runs only after PR #77 is merged. That is the intended guard.

**Run every line on its own, one at a time; never paste a block. If any line fails, or prints an error, `refused`, `STOP` or `FAIL`, stop there and send me the output.**

## G0. Install the build checkout (minutes; FP2 (d))

PR #77 was merged as `ed0bfbfa7a544f6e925d72d77734007a51d2c77e` (filled 2026-10-25). One line at a time:

```sh
sudo git clone --quiet https://github.com/meedo1985/autonomous-quant-trader.git /opt/aqt-d19/build
sudo git -C /opt/aqt-d19/build checkout --quiet ed0bfbfa7a544f6e925d72d77734007a51d2c77e
sudo chmod -R go-w /opt/aqt-d19/build
sudo git -C /opt/aqt-d19/build rev-parse HEAD
sudo git -C /opt/aqt-d19/app rev-parse HEAD
sudo git -C /opt/aqt-d19/build remote get-url origin
sudo git -C /opt/aqt-d19/build --no-optional-locks status --porcelain --untracked-files=all
sudo find /opt/aqt-d19/build \( ! -user 0 -o -perm /022 \) -print -quit
```

Check: the first `rev-parse` prints `ed0bfbfa7a544f6e925d72d77734007a51d2c77e`; the second prints `eeaa7282e3b7c87790c162d679016c290d5f4ea5`; the origin is the GitHub address above; the last two lines print nothing. **Send me** the output. I record it, and FP2 holds from then. `/opt/aqt-d19/app` is not touched.

## G. Build and commit the qualification object (hours)

```sh
cd /opt/aqt-d19/build/deploy/calibration
sudo sh d19.sh freeze ed0bfbfa7a544f6e925d72d77734007a51d2c77e
```

It checks the build checkout again (the same commit, unmodified, root-only), prints `build checkout ..., unmodified`, then `qualification_object_sha256` and writes the object directory `/var/lib/aqt-d19/qobj-1`, or refuses with no object published (only its own scratch clone `/var/lib/aqt-d19/freeze-root` may change). It needs the server's Internet connection: it reads the repository's branches from GitHub. **Send me** the hash. Then copy the directory to your laptop, in a Windows terminal (FH-7; the same `scp` as the dashboard's copy, with your server's address):

```bat
scp -r root@<<SERVER>>:/var/lib/aqt-d19/qobj-1 "%USERPROFILE%\Desktop\qobj-1"
```

I check the copy before anything else: the file list is exactly the object's, every file matches `manifest.json`, and the manifest gives the hash you sent (`qobj.read`). Then I commit the object in a PR and check that the committed bytes give the same hash. You merge it after your review. **The post (step H) waits for that merge** (§4 step 5: hash and commit, then post).

## H. The `AQTQ1` post (you, on your laptop; about 1 hour)

**Retention plan, before H (HK-R3).** The node must still hold block 972,269 at the step-M recheck, weeks after the post, while staying current. Its `prune=25000` is a moving size target, so before H:
1. From the measured window after the first sync (`blocks` − `pruneheight`) and the projected step-M date plus 30 days, I compute the prune target that keeps 972,269 until then.
2. You free that space on D: (your choice, `review/fp4-node/OWNER_ANSWERS_2026-10-25.md`).
3. With your OK, I raise `prune=` in `D:\Bitcoin\bitcoin.conf` and restart the node, while `pruneheight` is still ≤ 972,269. Raising the target stops further deletion; it restores nothing.
4. I commit the calculation and the node's readings.

If the space cannot be found, the post waits. The node's stop rules (S1-S3 of `FP4_LAPTOP_NODE_STEPS.txt`) stay in force.

**H0. Node ready (the day before, and again just before the post; FP4N-R3, FP4N-R2).** I run these on the laptop in Git Bash, with `B="C:/Program Files/Bitcoin/daemon/bitcoin-cli.exe"`. Each output is recorded. The command forms were tested on this node on 2026-10-25.
- **Sync and retention.** `"$B" -datadir=D:/Bitcoin getblockchaininfo` shows:
  - `chain` = `main`;
  - `initialblockdownload` = false;
  - `blocks` = `headers`, and equal to both explorers' tip (within 2 blocks);
  - `pruneheight` ≤ 972269.
- **Filter index.** `"$B" -datadir=D:/Bitcoin getindexinfo` shows `basic block filter index` with `synced` = true and `best_block_height` = `blocks`.
- **Oldest block readable.** `H=$("$B" -datadir=D:/Bitcoin getblockhash 972269)`, then `"$B" -datadir=D:/Bitcoin getblock $H 0`, which must return the block.
- **Wallet history from the node.** `"$B" -datadir=D:/Bitcoin -rpcclienttimeout=0 scanblocks start '["addr(<A_Q1>)"]' 972269 null basic '{"filter_false_positives":true}'` must return `completed` = true, `from_height` 972269 and `to_height` = the tip. Then `"$B" -datadir=D:/Bitcoin getdescriptoractivity '<relevant_blocks array from scanblocks>' '["addr(<A_Q1>)"]' false` must succeed and show only `F_Q1` received at `A_Q1`, and before the post nothing spent.
- **Laptop setup.** I add `shrinkdebugfile=0` to `D:\Bitcoin\bitcoin.conf` and restart the node, so its log keeps the acceptance line (step I).
- **Clock.** The laptop clock is checked against a time server (`w32tm /stripchart /computer:time.windows.com /samples:3 /dataonly`). The offset must be under 2 seconds.
- **Power.** Sleep is turned off from the broadcast until step I.2 is done.

If any of these fails, the post waits.

1. Check FP5 and FP6 on mempool.space and blockstream.info (I give you the two links), as well as on the node (H0).
2. In the `A_Q1` Electrum wallet, Send, "Pay to" exactly this one line (I fill the hash in a Notepad file; copy it from there):

   ```
   script(OP_RETURN 4151545131<<QUALIFICATION_OBJECT_SHA256>>), 0
   ```

   Electrum turns it into the 39-byte script `6a 25 41 51 54 51 31` followed by the 32 bytes of the hash (its `script(...)` output syntax, `electrum/payment_identifier.py` at 4.8.2). The whole coin minus the fee goes to a change address of the same wallet, never `A_Q1` itself.
3. Fee: at least the verifier node's `estimatesmartfee 6` (FP4, FP4N-R4, HK-R4). It is run twice, and both outputs are recorded:
   - once to set the fee before you sign;
   - again **immediately before each broadcast**, including any replacement.

   Each output must contain a number `feerate` and no `errors`, or we wait. The fee rate in sat/vB is `feerate` × 100,000. The **signed** transaction's actual rate must be at least the rate from the check just before broadcast; if not, it is not broadcast (step 4). The actual rate is the fee ÷ its virtual size, from the node's `decoderawtransaction` of the signed hex; signing adds witness data, so an unsigned decode does not count. The fee is no more than the coin allows (FP6). Electrum's or an explorer's estimate does not count (O-6a §7, FH-6). Keep "Replace-by-fee" on. If the node's estimate is above what the coin allows, wait.
4. **Do not broadcast yet: two checks (HK2-R2).**
   - **(a) Before signing:** Use Preview, then Export. Copy the unsigned transaction hex and send it to me. It is public data and holds no key. I decode it and check:
     - it spends `F_Q1` only;
     - it has exactly one OP_RETURN output, value 0, with the script exactly as above;
     - the change does not go to `A_Q1`.

     Only on my "OK (a)" do you **sign**.
   - **(b) After signing, before broadcasting:** in the same Preview window, Export, then "Save to file" as `D:\Bitcoin\signed-post.txn` on the laptop. **The signed transaction stays on the laptop (HK3-R1).** Anyone holding it could broadcast it, so:
     - it is not sent, pasted or committed anywhere before it is broadcast;
     - I only read that file on the laptop, with the laptop node's `decoderawtransaction` and `testmempoolaccept` (which only test; neither broadcasts);
     - I never use `sendrawtransaction`.

     The checks:
     - `decoderawtransaction` shows the same inputs and outputs as in (a);
     - the fee (`F_Q1`'s value minus the outputs) divided by its `vsize` is at least the fresh `estimatesmartfee 6` rate, run right then;
     - `testmempoolaccept` accepts it.

     I record a report: txid, inputs and outputs, fee, `vsize`, the fresh estimate and the `testmempoolaccept` result. Only on my "OK (b)" do **you** press **Broadcast** in Electrum. After the broadcast, the file is deleted; the transaction is then public on the network. **If this signed attempt ends without a broadcast** (a check fails, the fee must change, or the post is put off), the file is deleted at once, before any retry, and the retry is signed fresh (HK4-R1). Electrum is not asked to save the signed transaction in the wallet.
5. Send me the txid. A fee bump may replace it only with the identical OP_RETURN script (O-6a §7), and the replacement goes through 4 (a) and 4 (b) again.

## I. Acceptance and the post record (about 1 hour after inclusion, then same day)

At 6 confirmations the post is accepted. Inclusion height `h` = <<h>>; acceptance tip = block `h + 5`.

1. **You, once each, no more:** a Save Page Now capture (web.archive.org/save) of
   - `https://mempool.space/api/block-height/<<h+5>>`
   - `https://blockstream.info/api/block-height/<<h+5>>`

   Never request removal of any capture (O-6a §5, OF4-1).
2. **On the node** (I run these on the laptop; the laptop stays on, awake and caught up from the broadcast until this is done):
   - **The node's own acceptance time (FP4N-R2, FP4N2-R2).** The `UpdateTip` line in `D:\Bitcoin\debug.log` whose `best=` is the acceptance-tip hash at height `h + 5`. Its log-prefix UTC timestamp is "the time the node first saw the post accepted". It is never the block's own `date` field. I commit that line and the lines around it, with the SHA-256 of the whole log file. The acceptance tip must descend from the inclusion block, which `gettxoutproof` and the raw post tie to `h`.
     - If the laptop was not caught up continuously from the broadcast to that line, or the line is missing, or the clock check of H0 was not met, the attempt stops before step J, for your decision. The time is never rebuilt from an explorer.
   - **The scan gate (FP4N-R3).** All of H0's checks again, run with the post included. `scanblocks` over `addr(A_Q1)` from 972,269 to the tip with `filter_false_positives=true` must return `completed` = true, with the heights it covered recorded. Then `getdescriptoractivity` over the blocks found, with `include_mempool=false`, must succeed. `pruneheight` must be ≤ 972,269.
   - **The post itself:** the raw post, the funding transaction, the inclusion block hash, `gettxoutproof` and the acceptance-tip hash.

   I cross-check both explorers, write the post record (O-6a §4) and commit it. A disagreement blocks the attempt until it is resolved.
3. After the record is committed, destroy `A_Q1`'s key (O-6a §7, AI default). Keep `A_Q2`'s wallet safe: attempt 2 may need it.

## J. Freeze read (7 days after the node first saw the post accepted)

On <<FREEZE_READ_TIME>>: the node's acceptance time from step I.2 plus exactly 7 days. The laptop must be on and online at that time. **Every CDX index request** of the read (every page of both URLs) is made within the hour after that time. Each request's recorded retrieval time is the proof. The `id_` fetches of individual captures that follow are not index requests.

**If any CDX index request cannot be completed within that hour, or its timing cannot be proved, the attempt stops there for your decision (HK-R1, HK2-R1).** A later CDX query is never treated as the freeze read, because the index may have changed in between.

The read is made **once**. Nothing here needs you: the Internet Archive's index is public, so I make the read from your laptop with `curl`, which keeps the exact bytes (FH-1). For each of the two URLs, I save and commit:
- the exact CDX query URI (exact URL match, no collapsing), and every page of the reply, until the index reports no further page;
- for every page: the complete raw response bytes, the response headers and status, the retrieval time (UTC) and the SHA-256 of the bytes;
- the candidates: every CDX row of either URL with an exact URL match and archived status 200, in timestamp order across both URLs (FH2-1). From the earliest, each gets its `id_` fetch of that exact row's original URL and timestamp: the raw body, headers and status (including `x-archive-src` and `x-archive-orig-date`) and the body's SHA-256. A candidate qualifies when that fetch's URL, timestamp and digest equal its CDX row's (O-6a §5, OS3-1) and its body equals the frozen acceptance-tip block hash. Every candidate before the first that qualifies keeps its fetch evidence and the reason it does not qualify.

Then, in the same committed record:
- `T_Q1` = the 14-digit UTC timestamp of the first qualifying candidate in that order;
- the round = the first round of the FP3 chain whose scheduled time is at or after `T_Q1 + 24h` (prereg §8), and that scheduled time.

No qualifying capture: the attempt is void (§4 failure boundary); go to attempt 2.

## K. Before the held-out run: the drand record, then the two committed records (DF5-2)

**The drand record (FP3; kept apart from the O-6a records, GOV-FP3-6).** FP3 binds `quicknet` with no time limit (`review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE.md`, Rules 2-6).
- **Fetching.** From the freeze read onward, and also after the round's scheduled time, I fetch the round with `curl` from at least two endpoints, always with the chain hash in the path. A bare `/public/<round>` is a different chain. With `Q` = `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971`, the URLs are:
  - `https://api.drand.sh/v2/chains/$Q/rounds/<round>`
  - `https://api.drand.sh/$Q/public/<round>`
  - `https://drand.cloudflare.com/$Q/public/<round>`

  Another relay serving the same round of this chain is allowed (FP3 Rule 4). I save each raw response, with its source and retrieval time.
- **Verifying.** `deploy/calibration/drand-verify/verify.mjs` (pinned `drand-client` 1.4.2, tested in `review/fp3/verifier-test-2026-10-25/`) must exit 0 on the stored chain info `review/fp3/drand-info-2026-10-25/52db9ba7….info.json`. I record:
  - the round and its scheduled time (1692803367 + (round − 1) × 3);
  - the signature;
  - the randomness, computed as the SHA-256 of the raw signature bytes;
  - the verifier's output.
- **Committed and pushed** before record 1.
- **If no verifying output can be obtained yet:** the run waits, with no time limit, and I record one fetch attempt per day. A missing or late output never voids the attempt and never permits another chain, round or randomness source (Rule 5). If the chain stops for good, the attempt waits for your new formal decision (Rule 6).

**Timing limit (FP3S4-G2).**
The anchor is the first commit of the drand record. It is never reset (HK-R2).
- Record 1 is made, committed and pushed within 24 hours after that anchor.
- Record 2's `S` is at least 1 hour after record 1's commit, and at most 48 hours after the anchor.
- If either limit is missed, the attempt stops there for your decision. A fresh record 1 does not restart the clock.
- Record 1's checks are the full list below, never a selection.

**Record 1, the invalidation check.** A check of **every** O-6a invalidation condition for attempt 1, each with its evidence, made from the node (H0's checks with `pruneheight` ≤ 972,269, and the scan gate of step I.2) and from both explorers on the day:
- the first post is well-formed, spends `F_Q1`, and carries the committed object's hash;
- no later spend from `A_Q1`;
- the inclusion block, the order of posts and the acceptance tip are unchanged on the main chain;
- inclusion at height ≤ `D_Q1`;
- a qualifying capture was listed at the freeze read, and no earlier one giving a different round has been shown.

The drand output is not an O-6a condition. It is the drand record above (FP3 Rule 5: there is no void for a missing output).

An invalidation not listed in this record counts as found at or after the start (DF5-2).

**Record 2, the start time (FH-4, FH2-2).** Committed after record 1, it states one concrete start time `S` = <<START_UTC>> (a UTC minute, at least an hour after its commit). Step L's launch line waits until `S` and then starts the run, so the run starts at the recorded time. After the launch you send me `heldout-status`; I add docker's recorded container start time to the evidence in a second commit. It must fall within the UTC minute `S` (from `S` to `S` + 59 s), as the record states (FH3-2); the launch line starts it seconds after `S`. A start outside that minute, or a second launch before that commit, stops the attempt before any held-out result is read, for your decision.

## L. Held-out run (weeks)

```sh
cd /opt/aqt-d19/build/deploy/calibration
until [ "$(date -u +%s)" -ge <<START_EPOCH>> ]; do sleep 5; done; sudo sh d19.sh heldout 1 <<QUALIFICATION_OBJECT_SHA256>> <<ROUND>> <<RANDOMNESS>>
```

The first part waits until record 2's time `S` (`<<START_EPOCH>>` is `S` in seconds; I fill both). `<<ROUND>>` and `<<RANDOMNESS>>` are the round and the computed randomness from the drand record (step K), copied exactly. Run it in good time before `S` and leave the window open until it prints that the run started.

`docker.io`, `containerd` and `runc` stay on hold until step M (DEV_RUN_START_EVIDENCE.md). Weekly check: `heldout-status` (chunk counts only) and forward paper status. **Nothing shows held-out event content before `certify`** (§13 item 6, P18-6); do not run any other command on the held-out store. On `Exited` with a code other than 0, collect and stop, as in FULL_RUN.md D: a resume continues from the last finished chunk.

**Finished** when it shows `Exited (0)` and every final cell is at its `N_i / 500` chunks (40 or 80).

## M. Certify, then your decision

```sh
cd /opt/aqt-d19/build/deploy/calibration
sudo sh d19.sh certify 1 <<QUALIFICATION_OBJECT_SHA256>>
```

Exit 0: every test is within its target (§6). Exit 2: not. Either way, **send me** the report; I commit it.

**Before your decision, the invalidation check again (FH-2).** I repeat record 1's chain and capture checks (not the CDX freeze read itself, which is never repeated) and commit them. The node part needs H0's checks and the scan gate again, with `pruneheight` ≤ 972,269. The node's storage is sized for this (FP4 retention; your choice to free space on D:). If the node can no longer scan from 972,269, nothing is decided: it stops here for your decision. Anything found now, or reported at any time from the run's start until your decision, was found at or after the start: the attempt has **failed**, whatever `certify` said (§4 failure boundary).

Then you accept or reject the certification result (§12 item 4). A failure leaves promotion blocked; attempt 2 needs a recorded change. After step M, unhold Docker: `sudo apt-mark unhold docker.io containerd runc`.

## What this sheet does not do

- No change to the preregistration, its accepted hash, or any frozen artifact. FP3 is resolved only by the formal process.
- No key in the repository, a log, a prompt or an artifact. The AI never holds or signs with a key; it checks only public data (O-6a §7).
- No look at held-out content before `certify`.
- No trading, no cycle start, no read of confirmation or lockbox data.
