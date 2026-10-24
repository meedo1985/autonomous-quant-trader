# Freeze, `AQTQ1` post and held-out certification (D-19 attempt 1)

**Status: DRAFT, 2026-10-24. Not usable yet.** Three preconditions are open (FP2, FP3, FP4, §0), and FP3 needs a formal governance step that the AI cannot author or activate. Every `<<...>>` blank is filled only when its input exists. Prepared while the development run (FULL_RUN.md step E) goes; nothing here touches the server until you start step G, except step G0 (installing the build checkout), which may run as soon as PR #77 is merged (FS2-R1).

**What it is.** Freeze-order steps 5, 6 and 7 of the preregistration (§4): build and commit the qualification object, post its hash on Bitcoin (`AQTQ1`, O-6a SPEC rev 5 `84fca9c` §3-§7 by substitution), read the freeze point, fix the drand round, run the held-out certification (§6, §13 rev 7g items 3 and 6) and certify. Step G and everything after it start only after FULL_RUN.md step F. Forward paper keeps running, and nothing here touches it.

**What can end it early, and how (§4).**
- `choices.json` says the method does not qualify (§5 step 6): there is no freeze and no post. The result is recorded; it is a valid result.
- An O-6a invalidation found **before** the held-out run starts: the attempt is **void**. No held-out run, the namespace is not burned, and the same object may be posted again with key `A_Q2` under namespace `d19-heldout-v2`, with no recorded change. A void attempt still uses up its key (DF5-1).
- An invalidation found **at or after** the start, or a certification that does not pass: the attempt **fails**. Its namespace is burned, nothing is retuned (P18-6), and attempt 2 needs a recorded change.

## 0. Preconditions: all are checked and recorded before step G

| # | Precondition | Source | State |
|---|---|---|---|
| FP1 | FULL_RUN.md steps E and F done: `Exited (0)`, all 104 ids at `24 dev/`, and `choices.json` received with `qualifies` true and `margin_ok` true (`d19.sh choose` exit 0). Exit 3 (`margin_failed`) goes to you to decide (I1-6) | FULL_RUN.md E, F; `calibration/qobj.py` `build` | open (run going) |
| FP2 | A merged build change, with its independent review and **your §16 PR review** (PR #77; Astra reviews `ASTRA_FP2_BUILD_*.md`, last ACCEPT at `05321c5`): (a) `d19.sh freeze <build commit>`, which runs `qobj.build` inside the pinned image with the run's checkout `/opt/aqt-d19/app` (`eeaa728`) as `run_root`, and as `root` a disposable clone, owned by uid 990, of a second, root-owned checkout of the merged build commit (`build` fetches the live remote into the clone, QO-2, so `freeze` is the one engine command with network, BUILD-1). It refuses unless that checkout is at exactly the commit you name, unmodified, and writable by root only; (b) `d19.sh heldout <attempt> <posted hash> <round> <randomness>` and `d19.sh certify <attempt> <posted hash>`, which run `scripts/d19_heldout.py run` and `certify` from `/app`, plus a `heldout-status` that shows state, times and chunk counts only (P18-6); `certify` runs once per attempt and prints its report; (c) `review/d19-engine/FREEZE_REVIEWS.json`, listing `mapping.py`, `screen.py` and `heldout.py` with their SHA-256 and a committed review record each. Without (c), `build` refuses (BO-4, QO-5). (d) **Installed** by step G0: `/opt/aqt-d19/build` at `<<BUILD_COMMIT>>`, verified as the full commit there, root-owned, with the repository's GitHub origin, while `/opt/aqt-d19/app` stays at `eeaa728`; FP2 holds only once G0's checks pass and their output is recorded (FH-5, FP2-R2) | `calibration/qobj.py` (`LATER`, `REVIEWED`, `FREEZE_REVIEWS`); `d19.sh` has none of these commands at `eeaa728`; PR #77 | **open** (PR #77 awaits your review) |
| FP3 | **The drand chain is fixed, by chain hash and public key, before step G.** Prereg §8 takes the round from "the C2 drand chain (DRAFT §2.0)", and DRAFT §2.0 leaves that chain as `<<SIGNING: chain hash, public key>>` in the unsigned C2 draft; a draft placeholder binds nothing. Until a formal step binds it, the held-out anchor has no defined input. It must be bound before the post at the latest: a chain chosen once beacon outputs are known would let its choice pick the outcome. The same step settles whether DRAFT §2.0's failure rule (no verifying output within 7 days of the round's scheduled time) applies to D-19 (step K) | prereg §8; `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md` lines 161, 165, 340 | **open, governance** (Constitution amendment process or C2 signing; AI cannot author, merge or activate it) |
| FP4 | A verifier Bitcoin Core node, version 30.0 or later, `-blockfilterindex=1`, keeping every block from height 972,269 (`F_Q1`) to the freeze read. A pruned node is enough if its prune target keeps that range (block filters with pruning: upstream PR #15946; confirm in the 30.x docs before use). It needs an initial sync of the whole chain, about 1-3 days of download. It also gives the fee estimate for the post (step H). Where it runs is your decision (Q-F1) | O-6a SPEC §4, §7 | **open, your decision** |
| FP5 | The Electrum 4.8.2 wallet holding `A_Q1`'s key is on your laptop, and both explorers show `A_Q1` never spent from and holding only `F_Q1` (OF1-3), checked on the day of the post | KEY_RECORD_DRAFT.md; ACCEPTANCE_RECORD.md §2 | checked on the day |
| FP6 | The post can be included by `D_Q1` = 1,000,000. `F_Q1` (5,500 sat) covers a fee rate up to about 30 sat/vB with change above dust, so the post waits for fees below that | ACCEPTANCE_RECORD.md | checked on the day |

Until FP1-FP4 hold, nothing below runs, except step G0, which is how FP2 (d) comes to hold; it runs only after PR #77 is merged. That is the intended guard.

**Run every line on its own, one at a time; never paste a block. If any line fails, or prints an error, `refused`, `STOP` or `FAIL`, stop there and send me the output.**

## G0. Install the build checkout (minutes; FP2 (d))

After PR #77 is merged, I fill `<<BUILD_COMMIT>>` with its full merge commit. One line at a time:

```sh
sudo git clone --quiet https://github.com/meedo1985/autonomous-quant-trader.git /opt/aqt-d19/build
sudo git -C /opt/aqt-d19/build checkout --quiet <<BUILD_COMMIT>>
sudo chmod -R go-w /opt/aqt-d19/build
sudo git -C /opt/aqt-d19/build rev-parse HEAD
sudo git -C /opt/aqt-d19/app rev-parse HEAD
sudo git -C /opt/aqt-d19/build remote get-url origin
sudo git -C /opt/aqt-d19/build --no-optional-locks status --porcelain --untracked-files=all
sudo find /opt/aqt-d19/build \( ! -user 0 -o -perm /022 \) -print -quit
```

Check: the first `rev-parse` prints `<<BUILD_COMMIT>>`; the second prints `eeaa7282e3b7c87790c162d679016c290d5f4ea5`; the origin is the GitHub address above; the last two lines print nothing. **Send me** the output. I record it, and FP2 holds from then. `/opt/aqt-d19/app` is not touched.

## G. Build and commit the qualification object (hours)

```sh
cd /opt/aqt-d19/build/deploy/calibration
sudo sh d19.sh freeze <<BUILD_COMMIT>>
```

It checks the build checkout again (the same commit, unmodified, root-only), prints `build checkout ..., unmodified`, then `qualification_object_sha256` and writes the object directory `/var/lib/aqt-d19/qobj-1`, or refuses with no object published (only its own scratch clone `/var/lib/aqt-d19/freeze-root` may change). It needs the server's Internet connection: it reads the repository's branches from GitHub. **Send me** the hash. Then copy the directory to your laptop, in a Windows terminal (FH-7; the same `scp` as the dashboard's copy, with your server's address):

```bat
scp -r root@<<SERVER>>:/var/lib/aqt-d19/qobj-1 "%USERPROFILE%\Desktop\qobj-1"
```

I check the copy before anything else: the file list is exactly the object's, every file matches `manifest.json`, and the manifest gives the hash you sent (`qobj.read`). Then I commit the object in a PR and check that the committed bytes give the same hash. You merge it after your review. **The post (step H) waits for that merge** (§4 step 5: hash and commit, then post).

## H. The `AQTQ1` post (you, on your laptop; about 1 hour)

1. Check FP5 and FP6 on mempool.space and blockstream.info (I give you the two links).
2. In the `A_Q1` Electrum wallet, Send, "Pay to" exactly this one line (I fill the hash in a Notepad file; copy it from there):

   ```
   script(OP_RETURN 4151545131<<QUALIFICATION_OBJECT_SHA256>>), 0
   ```

   Electrum turns it into the 39-byte script `6a 25 41 51 54 51 31` followed by the 32 bytes of the hash (its `script(...)` output syntax, `electrum/payment_identifier.py` at 4.8.2). The whole coin minus the fee goes to a change address of the same wallet, never `A_Q1` itself.
3. Fee: at least the verifier node's `estimatesmartfee 6` (FP4; I give you the command and record its output), and no more than the coin allows (FP6). Electrum's or an explorer's estimate does not count (O-6a §7, FH-6). Keep "Replace-by-fee" on. If the node's estimate is above what the coin allows, wait.
4. **Do not broadcast yet.** Use Preview, then Export, copy the transaction hex and send it to me. It is public data: it holds no key. I decode it and check: it spends `F_Q1` only; exactly one OP_RETURN output, value 0, script exactly as above; the change is not `A_Q1`; the fee rate. Only on my "OK" do you sign and broadcast.
5. Send me the txid. A fee bump may replace it only with the identical OP_RETURN script (O-6a §7).

## I. Acceptance and the post record (about 1 hour after inclusion, then same day)

At 6 confirmations the post is accepted. Inclusion height `h` = <<h>>; acceptance tip = block `h + 5`.

1. **You, once each, no more:** a Save Page Now capture (web.archive.org/save) of
   - `https://mempool.space/api/block-height/<<h+5>>`
   - `https://blockstream.info/api/block-height/<<h+5>>`

   Never request removal of any capture (O-6a §5, OF4-1).
2. **On the node** (commands given then): `scanblocks` over `addr(A_Q1)` from 972,269 to the tip with `filter_false_positives=true`, then `getdescriptoractivity` over the blocks found with `include_mempool=false`; the raw post, the funding transaction, the inclusion block hash, `gettxoutproof`, the acceptance-tip hash, and the time the node first saw the post accepted. **Send me** the output. I cross-check both explorers, write the post record (O-6a §4) and commit it. A disagreement blocks the attempt until it is resolved.
3. After the record is committed, destroy `A_Q1`'s key (O-6a §7, AI default). Keep `A_Q2`'s wallet safe: attempt 2 may need it.

## J. Freeze read (7 days after the node first saw the post accepted)

On <<FREEZE_READ_TIME>> (I compute it from step I). The read is made **once**. Nothing here needs you: the Internet Archive's index is public, so I make the read from your laptop with `curl`, which keeps the exact bytes (FH-1). For each of the two URLs, I save and commit:
- the exact CDX query URI (exact URL match, no collapsing), and every page of the reply, until the index reports no further page;
- for every page: the complete raw response bytes, the response headers and status, the retrieval time (UTC) and the SHA-256 of the bytes;
- the candidates: every CDX row of either URL with an exact URL match and archived status 200, in timestamp order across both URLs (FH2-1). From the earliest, each gets its `id_` fetch of that exact row's original URL and timestamp: the raw body, headers and status (including `x-archive-src` and `x-archive-orig-date`) and the body's SHA-256. A candidate qualifies when that fetch's URL, timestamp and digest equal its CDX row's (O-6a §5, OS3-1) and its body equals the frozen acceptance-tip block hash. Every candidate before the first that qualifies keeps its fetch evidence and the reason it does not qualify.

Then, in the same committed record:
- `T_Q1` = the 14-digit UTC timestamp of the first qualifying candidate in that order;
- the round = the first round of the FP3 chain whose scheduled time is at or after `T_Q1 + 24h` (prereg §8), and that scheduled time.

No qualifying capture: the attempt is void (§4 failure boundary); go to attempt 2.

## K. Before the held-out run: the two committed records (DF5-2)

**Record 1, the invalidation check.** A check of **every** O-6a invalidation condition for attempt 1, each with its evidence, made from the node and both explorers on the day:
- the first post is well-formed, spends `F_Q1`, and carries the committed object's hash;
- no later spend from `A_Q1`;
- the inclusion block, the order of posts and the acceptance tip are unchanged on the main chain;
- inclusion at height ≤ `D_Q1`;
- a qualifying capture was listed at the freeze read, and no earlier one giving a different round has been shown;
- the round's output: I fetch it from drand with `curl` and record the round, its scheduled time, the raw response, the randomness, the signature, the retrieval time, and that the signature verifies against the FP3 public key (not checked by the engine, HO-4). The fetch is made after the freeze read **and** after the round's scheduled time, whichever is later (usually the same day as the freeze read; later if the first qualifying capture came late, FH3-1), and within 7 days of the scheduled time. Its recorded retrieval time is the evidence that a verifying output existed within those 7 days (FH2-3). How a missing output is treated is fixed by FP3's formal outcome, before step G: where DRAFT §2.0's rule binds, no verifying output retrieved within the 7 days invalidates the attempt before evaluation, so it is void (§4 failure boundary); otherwise the rule FP3 settles applies.

An invalidation not listed in this record counts as found at or after the start (DF5-2).

**Record 2, the start time (FH-4, FH2-2).** Committed after record 1, it states one concrete start time `S` = <<START_UTC>> (a UTC minute, at least an hour after its commit). Step L's launch line waits until `S` and then starts the run, so the run starts at the recorded time. After the launch you send me `heldout-status`; I add docker's recorded container start time to the evidence in a second commit. It must fall within the UTC minute `S` (from `S` to `S` + 59 s), as the record states (FH3-2); the launch line starts it seconds after `S`. A start outside that minute, or a second launch before that commit, stops the attempt before any held-out result is read, for your decision.

## L. Held-out run (weeks)

```sh
cd /opt/aqt-d19/build/deploy/calibration
until [ "$(date -u +%s)" -ge <<START_EPOCH>> ]; do sleep 5; done; sudo sh d19.sh heldout 1 <<QUALIFICATION_OBJECT_SHA256>> <<ROUND>> <<RANDOMNESS>>
```

The first part waits until record 2's time `S` (`<<START_EPOCH>>` is `S` in seconds; I fill both). Run it in good time before `S` and leave the window open until it prints that the run started.

`docker.io`, `containerd` and `runc` stay on hold until step M (DEV_RUN_START_EVIDENCE.md). Weekly check: `heldout-status` (chunk counts only) and forward paper status. **Nothing shows held-out event content before `certify`** (§13 item 6, P18-6); do not run any other command on the held-out store. On `Exited` with a code other than 0, collect and stop, as in FULL_RUN.md D: a resume continues from the last finished chunk.

**Finished** when it shows `Exited (0)` and every final cell is at its `N_i / 500` chunks (40 or 80).

## M. Certify, then your decision

```sh
cd /opt/aqt-d19/build/deploy/calibration
sudo sh d19.sh certify 1 <<QUALIFICATION_OBJECT_SHA256>>
```

Exit 0: every test is within its target (§6). Exit 2: not. Either way, **send me** the report; I commit it.

**Before your decision, the invalidation check again (FH-2).** I repeat record 1's chain and capture checks (not the CDX freeze read itself, which is never repeated) and commit them. Anything found now, or reported at any time from the run's start until your decision, was found at or after the start: the attempt has **failed**, whatever `certify` said (§4 failure boundary).

Then you accept or reject the certification result (§12 item 4). A failure leaves promotion blocked; attempt 2 needs a recorded change. After step M, unhold Docker: `sudo apt-mark unhold docker.io containerd runc`.

## What this sheet does not do

- No change to the preregistration, its accepted hash, or any frozen artifact. FP3 is resolved only by the formal process.
- No key in the repository, a log, a prompt or an artifact. The AI never holds or signs with a key; it checks only public data (O-6a §7).
- No look at held-out content before `certify`.
- No trading, no cycle start, no read of confirmation or lockbox data.
