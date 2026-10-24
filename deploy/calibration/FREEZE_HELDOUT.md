# Freeze, `AQTQ1` post and held-out certification (D-19 attempt 1)

**Status: DRAFT, 2026-10-24. Not usable yet.** Three preconditions are open (FP2, FP3, FP4, §0), and FP3 needs a formal governance step that the AI cannot author or activate. Every `<<...>>` blank is filled only when its input exists. Prepared while the development run (FULL_RUN.md step E) goes; nothing here touches the server until you start step G.

**What it is.** Freeze-order steps 5, 6 and 7 of the preregistration (§4): build and commit the qualification object, post its hash on Bitcoin (`AQTQ1`, O-6a SPEC rev 5 `84fca9c` §3-§7 by substitution), read the freeze point, fix the drand round, run the held-out certification (§6, §13 rev 7g items 3 and 6) and certify. It starts only after FULL_RUN.md step F. Forward paper keeps running, and nothing here touches it.

**What can end it early, and how (§4).**
- `choices.json` says the method does not qualify (§5 step 6): there is no freeze and no post. The result is recorded; it is a valid result.
- An O-6a invalidation found **before** the held-out run starts: the attempt is **void**. No held-out run, the namespace is not burned, and the same object may be posted again with key `A_Q2` under namespace `d19-heldout-v2`, with no recorded change. A void attempt still uses up its key (DF5-1).
- An invalidation found **at or after** the start, or a certification that does not pass: the attempt **fails**. Its namespace is burned, nothing is retuned (P18-6), and attempt 2 needs a recorded change.

## 0. Preconditions: all are checked and recorded before step G

| # | Precondition | Source | State |
|---|---|---|---|
| FP1 | FULL_RUN.md steps E and F done: `Exited (0)`, all 104 ids at `24 dev/`, and `choices.json` received with `qualifies` true and `margin_ok` true (`d19.sh choose` exit 0). Exit 3 (`margin_failed`) goes to you to decide (I1-6) | FULL_RUN.md E, F; `calibration/qobj.py` `build` | open (run going) |
| FP2 | A merged build change, with Sol's review and **your §16 PR review**: (a) `d19.sh freeze`, which runs `qobj.build` inside the pinned image with the run's checkout `/opt/aqt-d19/app` (`eeaa728`) as `run_root` and a second, read-only checkout of the merged build commit as `root`; (b) `d19.sh heldout <n> <round> <randomness>` and `d19.sh certify <n>`, which run `scripts/d19_heldout.py run` and `certify` the same way, plus a `heldout-status` that shows chunk counts only (P18-6); (c) `review/d19-engine/FREEZE_REVIEWS.json`, listing `mapping.py`, `screen.py` and `heldout.py` with their SHA-256 and a committed review record each. Without (c), `build` refuses (BO-4, QO-5) | `calibration/qobj.py` (`LATER`, `REVIEWED`, `FREEZE_REVIEWS`); `d19.sh` has none of these commands at `eeaa728` | **open** |
| FP3 | **The drand chain is fixed, by chain hash and public key, before the post (step H).** Prereg §8 takes the round from "the C2 drand chain (DRAFT §2.0)", and DRAFT §2.0 leaves that chain as `<<SIGNING: chain hash, public key>>` in the unsigned C2 draft. Until a formal step binds it, the held-out anchor has no defined input. It must be bound before the post: a chain chosen after the round times are known would let its choice pick the beacon outcome | prereg §8; `review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md` lines 161, 340 | **open, governance** (Constitution amendment process or C2 signing; AI cannot author, merge or activate it) |
| FP4 | A verifier Bitcoin Core node, version 30.0 or later, `-blockfilterindex=1`, keeping every block from height 972,269 (`F_Q1`) to the freeze read. A pruned node is enough if its prune target keeps that range (block filters with pruning: upstream PR #15946; confirm in the 30.x docs before use). It needs an initial sync of the whole chain, about 1-3 days of download. Where it runs is your decision (Q-F1) | O-6a SPEC §4 | **open, your decision** |
| FP5 | The Electrum 4.8.2 wallet holding `A_Q1`'s key is on your laptop, and both explorers show `A_Q1` never spent from and holding only `F_Q1` (OF1-3), checked on the day of the post | KEY_RECORD_DRAFT.md; ACCEPTANCE_RECORD.md §2 | checked on the day |
| FP6 | The post can be included by `D_Q1` = 1,000,000. `F_Q1` (5,500 sat) covers a fee rate up to about 30 sat/vB with change above dust, so the post waits for fees below that | ACCEPTANCE_RECORD.md | checked on the day |

Until FP1-FP4 hold, nothing below runs. That is the intended guard.

**Run every line on its own, one at a time; never paste a block. If any line fails, or prints an error, `refused`, `STOP` or `FAIL`, stop there and send me the output.**

## G. Build and commit the qualification object (hours)

```sh
cd /opt/aqt-d19/app/deploy/calibration
sudo sh d19.sh freeze <<BUILD_COMMIT>>
```

It prints `qualification_object_sha256` and writes the object directory under `/var/lib/aqt-d19/qobj-1`, or refuses with nothing written. **Send me** the hash and copy the directory to your laptop (Notepad file then). I recompute the hash from the files with `qobj.read`, commit the object in a PR, and check that the committed bytes give the same hash. You merge it after your review. **The post (step H) waits for that merge** (§4 step 5: hash and commit, then post).

## H. The `AQTQ1` post (you, on your laptop; about 1 hour)

1. Check FP5 and FP6 on mempool.space and blockstream.info (I give you the two links).
2. In the `A_Q1` Electrum wallet, Send, "Pay to" exactly this one line (I fill the hash in a Notepad file; copy it from there):

   ```
   script(OP_RETURN 4151545131<<QUALIFICATION_OBJECT_SHA256>>), 0
   ```

   Electrum turns it into the 39-byte script `6a 25 41 51 54 51 31` followed by the 32 bytes of the hash (its `script(...)` output syntax, `electrum/payment_identifier.py` at 4.8.2). The whole coin minus the fee goes to a change address of the same wallet, never `A_Q1` itself.
3. Fee: at least the fee estimate for 6 blocks, and no more than the coin allows (FP6). Keep "Replace-by-fee" on.
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

On <<FREEZE_READ_TIME>> (I compute it from step I), I give you the exact CDX queries for both URLs (exact URL match, no collapsing, every page). **Send me** the raw responses. I record them (O-6a §4) and fix:
- `T_Q1` = the 14-digit UTC timestamp of the earliest capture whose CDX row matches the URL exactly with status 200 and whose `id_` body equals the acceptance-tip hash, bound to that row;
- the round = the first round of the FP3 chain whose scheduled time is at or after `T_Q1 + 24h` (prereg §8).

No qualifying capture: the attempt is void (§4 failure boundary); go to attempt 2.

## K. Before the held-out run: two committed records (DF5-2)

1. The round's randomness, fetched from drand, with its signature checked against the FP3 public key (not checked by the engine, HO-4).
2. A check of **every** O-6a invalidation condition for attempt 1, each with its evidence: the first post is well-formed and spends `F_Q1`; its hash is the committed object's; no later spend from `A_Q1`; the inclusion block, the order of posts and the acceptance tip are unchanged on the main chain; inclusion at height ≤ `D_Q1`; a qualifying capture exists and none earlier changes the round. An invalidation not listed here counts as found at or after the start (DF5-2).
3. The record of the time the run starts.

Both records are committed before you start step L.

## L. Held-out run (weeks)

```sh
sudo sh d19.sh heldout 1 <<ROUND>> <<RANDOMNESS>>
```

`docker.io`, `containerd` and `runc` stay on hold until step M (DEV_RUN_START_EVIDENCE.md). Weekly check: `heldout-status` (chunk counts only) and forward paper status. **Nothing shows held-out event content before `certify`** (§13 item 6, P18-6); do not run any other command on the held-out store. On `Exited` with a code other than 0, collect and stop, as in FULL_RUN.md D: a resume continues from the last finished chunk.

**Finished** when it shows `Exited (0)` and every final cell is at its `N_i / 500` chunks (40 or 80).

## M. Certify, then your decision

```sh
sudo sh d19.sh certify 1
```

Exit 0: every test is within its target (§6). Exit 2: not. Either way, **send me** the report; I commit it. Then you accept or reject the certification result (§12 item 4). A failure leaves promotion blocked; attempt 2 needs a recorded change. After step M, unhold Docker: `sudo apt-mark unhold docker.io containerd runc`.

## What this sheet does not do

- No change to the preregistration, its accepted hash, or any frozen artifact. FP3 is resolved only by the formal process.
- No key in the repository, a log, a prompt or an artifact. The AI never holds or signs with a key; it checks only public data (O-6a §7).
- No look at held-out content before `certify`.
- No trading, no cycle start, no read of confirmation or lockbox data.
