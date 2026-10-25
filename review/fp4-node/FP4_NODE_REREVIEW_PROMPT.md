# Independent re-review: FP4 laptop node steps, revision 2

You are an independent adversarial reviewer (read-only), not an authority.
Your review `review/fp4-node/SOL_FP4_NODE_REVIEW.md` found FP4N-R1..R7 (FIX).
The adjudication and the repaired steps are below; revision 1 is in
`review/fp4-node/FP4_NODE_REVIEW_PROMPT.md`.

Check: (1) is each accepted repair correct and sufficient; (2) are the
dispositions that leave FP4N-R2, the R3 scan-time gate and R4 open until
step H acceptable, given that they block step H; (3) is the R1 approach
(measured sliding window, weekly checks, raise only before pruneheight
passes 972,269, resync as recovery) sound; (4) any new defect, or any
other problem you see. New findings: `FP4N2-R1`, ... with severity, place,
failure scenario, minimal repair. Verdict: ACCEPT or FIX.

## Adjudication

# Adjudication: Codex review of the FP4 laptop node steps

Review record: `SOL_FP4_NODE_REVIEW.md` (gpt-6-sol, high, read-only, web search; verdict FIX).
Adjudicated by Claude Opus 5.5 (the author of the steps), 2026-10-25.
Repaired steps: `FP4_LAPTOP_NODE_STEPS.txt` (revision 2; revision 1 is quoted in the prompt).
Owner decision behind them (Q-F1, 2026-10-25): node on the laptop ("yes go with laptop"),
after "i cant run this machine all the time so what is best opthen".

| ID | Severity | Adjudication | Repair / disposition |
|---|---|---|---|
| FP4N-R1 | BLOCKER | **Accepted.** `prune=25000` is MiB of block and undo files, a sliding window, not a fixed range. An unpruned node (~770 GB) does not fit the laptop (D: 62 GB free) and paid storage is outside the owner's budget. | Kept `prune=25000` as a measured window, not a guarantee. Recent blocks average 1.77 MB (mempool.space, last 10, 2026-10-25); at ~2 MB with undo the window is ~13,000 blocks, so F_Q1 (972,269) leaves it near height ~985,000, about mid-January 2027. Weekly checks (lines 10-12) give the real window (`blocks - pruneheight`) and the real deadline; the owner is warned weeks ahead. If the post cannot be made in time, the prune target may be raised **before** `pruneheight` passes 972,269, only if measured disk allows (raising stops further pruning; it restores nothing). If it has passed, FP4 fails for this node: a fresh resync whose window covers F_Q1 at that time is the recovery, never a photo or an explorer. Gate added to the sheet's step H/I (open, below): `pruneheight <= 972269` at each scan. |
| FP4N-R2 | BLOCKER | **Accepted**, but it belongs to the sheet's steps H (post) and I (freeze read), which are not yet written for a laptop node. Node setup alone cannot fix it. | **Open, blocks step H.** Before step H, the sheet must give: the laptop on from broadcast through 6 confirmations; a recorded node observation of acceptance (block hash, height, `getblockchaininfo` and the laptop's UTC time); the freeze read scheduled 7 days after that recorded observation with the laptop on; a missed or unproved observation or read is a stop for the owner's decision, never reconstructed from an explorer. |
| FP4N-R3 | HIGH | **Accepted.** | Weekly checks now include `getindexinfo` (filter index `synced`, height) beside `getblockchaininfo` (`chain`, `blocks`, `headers`, `initialblockdownload`, `pruneheight`). Wording corrected: `pruneheight` is the first unpruned block, so `<= 972269` is the condition (the old "below" was too strict). The scan-time gate (main chain, IBD done, headers = blocks, filter index synced, `pruneheight <= 972269`, block 972,269 readable with `getblock`, both RPCs succeed) goes into step H/I: **open, with FP4N-R2.** |
| FP4N-R4 | HIGH | **Accepted**; it belongs to step H. | **Open, blocks step H.** Step H must run `estimatesmartfee 6` on a current node just before broadcast, require a numeric `feerate` and no `errors`, else wait; convert BTC/kvB x 100,000 = sat/vB. |
| FP4N-R5 | HIGH | **Accepted and resolved by the author's verification.** | On 2026-10-25 the author verified `SHA256SUMS.asc` against `SHA256SUMS` with the 39 builder keys from GitHub `bitcoin-core/guix.sigs/builder-keys` (a different origin from bitcoincore.org), GnuPG 2.4.9: **11 good signatures, 0 bad** (Ava Chow, Michael Ford, Hennadii Stepanov, Ben Carman, Oliver Gugger, marcofleon, Matthew Zipkin, Stephan Oeste, Will Clark, Sjors Provoost, sedited). SHA256 of the verified files: `SHA256SUMS` `e63028d0bb33d22c847479d73866be8c1142246911765c005efbf611b645e706`, `SHA256SUMS.asc` `c22e1389b651dfa2f710345e23f3adc52d4e3b3dad8ed7977a7e29d55c55995f`. The signed line for the installer is `d0c6d0f3...4e193458`, the digest in step 2. Limit: trust in the keys is GitHub's repository, not a web of trust. |
| FP4N-R6 | MEDIUM | **Accepted.** | Weekly line 12 (free GB on D:) and `size_on_disk` in line 10; the prune target is not raised on estimates. |
| FP4N-R7 | LOW | **Accepted.** | `listen=0` added; the firewall instruction now says Cancel. |

Also taken from the review: `Test-Path` checks for both programs (line 4), a version check (line 5), and a note for a node window that closes by itself (line 8, with `debug.log`).

Not repaired, by design: the steps were not run on the laptop by the author or the reviewer; the first real check is the owner's photos of lines 4, 5, 10-12.

Still open, blocking step H: FP4N-R2, FP4N-R3 (scan-time gate), FP4N-R4.

## Repaired steps (verbatim)

```text
FP4 - Bitcoin verifier node on your LAPTOP (Bitcoin Core 31.1, pruned, block filters)
Run each line in PowerShell on the laptop, ONE LINE AT A TIME. No keys or wallet go on this node.
(Revision 2, after Codex review FP4N-R1..R7; see ADJUDICATION_FP4_NODE.md.)

=== ONCE: install ===

1) Download the installer (about 39 MB):
Invoke-WebRequest https://bitcoincore.org/bin/bitcoin-core-31.1/bitcoin-31.1-win64-setup.exe -OutFile $HOME\Downloads\bitcoin-31.1-win64-setup.exe

2) Check it. This must print True. (This hash is the one signed by 11 Bitcoin Core builders; checked 2026-10-25.)
(Get-FileHash $HOME\Downloads\bitcoin-31.1-win64-setup.exe).Hash -eq "D0C6D0F3CD08689472A6F53C4CE33A5F059C092758C32C42541B47DB4E193458"

   If it prints False: STOP, delete the file, tell me.

3) Install it (normal Next/Next/Finish; keep the default folder C:\Program Files\Bitcoin). Untick "Run Bitcoin Core" at the end.
Start-Process $HOME\Downloads\bitcoin-31.1-win64-setup.exe

4) Check the two programs are where these steps expect. Both lines must print True:
Test-Path "C:\Program Files\Bitcoin\daemon\bitcoind.exe"
Test-Path "C:\Program Files\Bitcoin\daemon\bitcoin-cli.exe"

   If either prints False: STOP, send me a photo of the folder C:\Program Files\Bitcoin.

5) Check the version. It must say v31.1.0:
& "C:\Program Files\Bitcoin\daemon\bitcoind.exe" -version

6) Make the node's folder on D:
New-Item -ItemType Directory -Force D:\Bitcoin

7) Write its settings (block filters on, low memory, no wallet, no incoming connections):
Set-Content -Encoding ascii D:\Bitcoin\bitcoin.conf "prune=25000","blockfilterindex=1","dbcache=300","maxmempool=100","disablewallet=1","listen=0"

=== EVERY TIME the laptop is on: start it ===

8) Start the node (a black window opens and stays open; leave it open while you work):
Start-Process "C:\Program Files\Bitcoin\daemon\bitcoind.exe" "-datadir=D:\Bitcoin"

   If Windows Firewall asks: click Cancel (the node only needs outgoing connections).
   If the black window closes by itself within a minute: the node stopped. Send me a photo of: Get-Content D:\Bitcoin\debug.log -Tail 20

=== BEFORE you shut down the laptop: stop it properly ===

9) Stop the node (wait until its window closes by itself, then shut down):
& "C:\Program Files\Bitcoin\daemon\bitcoin-cli.exe" -datadir=D:\Bitcoin stop

   Sleep / closing the lid is fine. Only a full shutdown needs line 9 first.

=== ONCE A WEEK (and whenever I ask): checks - send me a photo of each output ===

10) Sync state (I read: chain, blocks, headers, initialblockdownload, pruneheight, size_on_disk):
& "C:\Program Files\Bitcoin\daemon\bitcoin-cli.exe" -datadir=D:\Bitcoin getblockchaininfo

11) Block-filter index state (I read: synced, best_block_height):
& "C:\Program Files\Bitcoin\daemon\bitcoin-cli.exe" -datadir=D:\Bitcoin getindexinfo

12) Disk space left on D: (GB):
[math]::Round((Get-PSDrive D).Free/1GB)

Notes:
- The node keeps only about the last 13,000 blocks (about 3 months). Block 972,269 (F_Q1) must still be kept at the freeze read.
  From your weekly photos I compute the real date by which the freeze read must happen, and warn you weeks ahead.
  Never change bitcoin.conf yourself.
- Disk: expected about 50 GB on D: when synced (you have 62 GB free). Do not fill D: with other big files.
- The first sync downloads the whole chain (~770 GB, kept only partly). It continues where it stopped each time you run line 8.
- The post day (step H) and the freeze read (step I) need the laptop ON at set times; I give you those times in advance.
```
