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
