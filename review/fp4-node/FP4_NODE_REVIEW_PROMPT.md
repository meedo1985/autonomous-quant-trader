# Independent review: FP4 verifier node setup on the owner's laptop

You are an independent adversarial reviewer (read-only), not an authority.
Goal: check that the owner's laptop node, installed exactly as the steps
below say, meets FP4 of `deploy/calibration/FREEZE_HELDOUT.md` and the O-6a
SPEC, and that the steps are correct and safe for a non-technical owner on
Windows 11 (PowerShell 5.1). Real money depends on this verification later.

Owner decision (Q-F1, 2026-10-25): node on the laptop, not the server; the
laptop is NOT on all the time, so the node syncs only while it is on.
Laptop: Windows 11 Pro, 8 GB RAM, D: 62 GB free, C: 23 GB free.

## Requirements (verbatim)

- FREEZE_HELDOUT.md FP4: "A verifier Bitcoin Core node, version 30.0 or later, `-blockfilterindex=1`, keeping every block from height 972,269 (`F_Q1`) to the freeze read. A pruned node is enough if its prune target keeps that range (block filters with pruning: upstream PR #15946; confirm in the 30.x docs before use). ... It also gives the fee estimate for the post (step H)."
- `review/governance-statistics-amendment/o6a-channel/SPEC.md` lines 53-55: "The verifier runs a fully validating Bitcoin Core node, version 30.0 or later. It runs with `-blockfilterindex=1` and is not pruned below `F`'s height. It lists every spend from `A` in two steps: `scanblocks` over descriptor `addr(A)` with `filter_false_positives=true`, from `F`'s height to the current tip; then `getdescriptoractivity` over the blocks found, with `include_mempool=false` ..."
- Freeze point (SPEC line 105): 7 days after the verifier's node first saw the post accepted. Post deadline `D_Q1` = height 1,000,000. Step H fee: at least the node's `estimatesmartfee 6`.

## Facts the author checked (2026-10-25)

- Latest release Bitcoin Core 31.1 (installer Last-Modified 2026-07-07). SHA256SUMS from bitcoincore.org: `d0c6d0f3cd08689472a6f53c4ce33a5f059c092758c32c42541b47db4e193458  bitcoin-31.1-win64-setup.exe`. Signature of SHA256SUMS (SHA256SUMS.asc) NOT verified by the steps.
- Tip height 973,037 (mempool.space and blockstream.info agree), so F_Q1 is 768 blocks back.
- 31.0 RPC docs: `scanblocks` "requires blockfilterindex"; `filter_false_positives` "slower and may fail on pruned nodes". `getdescriptoractivity` documented. `BlockFilterIndex::AllowPrune()` returns true in source.
- Size estimates (not verified): filter index ~9-12 GB, chainstate ~8-12 GB, recent blocks incl. undo ~1.8 MB each; prune=25000 MB ~ 13,800 blocks.
- Not verified: that the Windows installer puts `bitcoind.exe` and `bitcoin-cli.exe` in `C:\Program Files\Bitcoin\daemon\`.

## The steps given to the owner (verbatim)

```text
FP4 - Bitcoin verifier node on your LAPTOP (Bitcoin Core 31.1, pruned, block filters)
Run each line in PowerShell on the laptop, ONE LINE AT A TIME. No keys or wallet go on this node.

=== ONCE: install ===

1) Download the installer (about 39 MB):
Invoke-WebRequest https://bitcoincore.org/bin/bitcoin-core-31.1/bitcoin-31.1-win64-setup.exe -OutFile $HOME\Downloads\bitcoin-31.1-win64-setup.exe

2) Check it. This must print True (official SHA256 from bitcoincore.org):
(Get-FileHash $HOME\Downloads\bitcoin-31.1-win64-setup.exe).Hash -eq "D0C6D0F3CD08689472A6F53C4CE33A5F059C092758C32C42541B47DB4E193458"

   If it prints False: STOP, delete the file, tell me.

3) Install it (normal Next/Next/Finish; keep the default folder C:\Program Files\Bitcoin). Do NOT start Bitcoin Core at the end (untick "Run Bitcoin Core").
Start-Process $HOME\Downloads\bitcoin-31.1-win64-setup.exe

4) Make the node's folder on D:
New-Item -ItemType Directory -Force D:\Bitcoin

5) Write its settings (keeps blocks from F_Q1 onward, block filters on, low memory, no wallet):
Set-Content -Encoding ascii D:\Bitcoin\bitcoin.conf "prune=25000","blockfilterindex=1","dbcache=300","maxmempool=100","disablewallet=1"

=== EVERY TIME the laptop is on: start it ===

6) Start the node (a black window opens and stays open; leave it open while you work):
Start-Process "C:\Program Files\Bitcoin\daemon\bitcoind.exe" "-datadir=D:\Bitcoin"

   If Windows Firewall asks: allow on Private networks.

=== BEFORE you shut down the laptop: stop it properly ===

7) Stop the node (wait until its window closes by itself, then shut down):
& "C:\Program Files\Bitcoin\daemon\bitcoin-cli.exe" -datadir=D:\Bitcoin stop

   Sleep / closing the lid is fine. Only a full shutdown needs line 7 first.

=== ANY TIME: progress check (send me a photo of the output) ===

8) Status:
& "C:\Program Files\Bitcoin\daemon\bitcoin-cli.exe" -datadir=D:\Bitcoin getblockchaininfo

   "blocks" climbs to about 973,000+ ; "verificationprogress" goes to 0.9999... when synced.
   Once synced, "pruneheight" must stay BELOW 972269. I check this from your photo.

Notes:
- Disk: about 50 GB on D: when full (you have 62 GB free). Do not fill D: with other big files.
- The first sync downloads the whole chain (~770 GB, kept only partly). It continues where it stopped each time you start line 6.
- If the laptop gets slow, it is the sync; it gets quiet once synced.
```

## Questions

1. Does this node satisfy FP4 and SPEC lines 53-55 for the whole period
   needed (F_Q1 to the freeze read), given the owner's intermittent uptime?
   Is prune=25000 enough, too much for the disk, or the wrong approach (for
   example: during the initial sync, does a pruned node ever hold the blocks
   from 972,269 and keep them, and does `pruneheight` behave as the steps
   assume)? Does `scanblocks ... filter_false_positives=true` and
   `getdescriptoractivity` work on this pruned node for that range?
2. Are the commands correct on Windows PowerShell 5.1 (paths, quoting,
   `Set-Content` writing a valid bitcoin.conf, `Start-Process` arguments,
   the daemon path), and is any setting harmful (dbcache, maxmempool,
   disablewallet; is `estimatesmartfee` reliable on a node that is often off)?
3. Is a hash check against SHA256SUMS from the same site enough here, or
   should the owner verify SHA256SUMS.asc signatures; what is the minimal
   safe procedure for him?
4. Any other defect, risk or simpler correct approach you see.

Verify against official Bitcoin Core sources (bitcoincore.org docs, release
notes, GitHub bitcoin/bitcoin) where you can, and say plainly what you could
not verify. Findings get IDs `FP4N-R1`, ... with severity, place, failure
scenario and minimal repair. Then a verdict: ACCEPT or FIX.
