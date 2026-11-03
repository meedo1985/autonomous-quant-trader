# Codex review of the FP4 laptop node steps

Prompt: `review/fp4-node/FP4_NODE_REVIEW_PROMPT.md` (91f0704).
Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-sol`,
sandbox read-only, reasoning effort high, live web search on,
session id `01a171fd-1fe9-7ae1-98f6-931c1345d514`, 139,647 tokens.

Verdict: **FIX**. Findings FP4N-R1 .. FP4N-R7; dispositions in
`ADJUDICATION_FP4_NODE.md`.

## Report (verbatim)

## Verdict: **FIX**
## Verdict: **FIX**

As written, these steps do **not** establish FP4 for the whole period from block 972,269 to the freeze read. Bitcoin Core 31.1 supports the required pruned node and RPCs, but `prune=25000` does not reserve that block range. The laptop’s intermittent uptime also needs an explicit plan for recording when the node first sees acceptance and for making the freeze read seven days later.

### Findings

1. **FP4N-R1 — BLOCKER: The required blocks can be pruned.**  
   **Place:** Step 5, `prune=25000`, and step 8’s one-time `pruneheight` photo.  
   **Failure scenario:** `25000` is a target in **MiB for block and undo files**, not a promise to retain 25,000 blocks. During initial sync the node downloads and validates block 972,269, then retains it only until automatic pruning reaches it. The stated tip of 973,037 is 768 blocks after `F_Q1`; the post deadline alone is 27,731 blocks after it, with the freeze read later still. The supplied 1.8 MB-per-block estimate suggests a 25,000 MiB target could cover roughly 14,500 recent blocks, but that estimate is unverified and cannot establish a safe cutoff. Being off does not itself prune blocks; catching up after restart can. Core’s [31.1 pruning code](https://github.com/bitcoin/bitcoin/blob/v31.1/src/node/blockstorage.cpp) prunes old block files to its size target.  
   **Minimal repair:** Do not approve this fixed prune target for an unknown posting height. Use adequately sized additional storage on the **laptop** for an unpruned node, or set a bounded posting and freeze window, measure actual retention and disk use, and prove the full range remains available through the freeze read. If any required block has already been pruned, a photo or a later setting change does not restore the required continuous retention.

2. **FP4N-R2 — BLOCKER: Intermittent uptime leaves the freeze clock and read unprotected.**  
   **Place:** “Every time the laptop is on” and the planned acceptance and freeze steps.  
   **Failure scenario:** If the laptop is off when six confirmations occur, its first observation of acceptance is later, after it catches up. The seven-day clock depends on that **node observation**, which the setup steps do not timestamp. If the laptop is off at the calculated freeze time, the planned read “from your laptop” cannot happen then.  
   **Minimal repair:** Before posting, define and test a procedure that records the node’s first observed acceptance with a trustworthy UTC time and block evidence. Schedule the freeze read for exactly seven days after that recorded observation, with the laptop available and a responsible operator ready. Treat a missed or unproved observation/read as a stop condition, not a time to reconstruct from an explorer.

3. **FP4N-R3 — HIGH: The status check does not prove the verifier is ready.**  
   **Place:** Step 8 and the proposed later `scanblocks`/`getdescriptoractivity` work.  
   **Failure scenario:** `verificationprogress` near 1 and a rising `blocks` value do not prove the node is at the current tip, that the block-filter index has caught up, or that the required blocks remain present **at scan time**. Core’s [31.0 `scanblocks` documentation](https://bitcoincore.org/en/doc/31.0.0/rpc/blockchain/scanblocks/) requires the index and warns that `filter_false_positives=true` may fail on pruned nodes. Its [31.1 test](https://github.com/bitcoin/bitcoin/blob/v31.1/test/functional/feature_pruning.py) demonstrates that failure on a pruned matching block. [`getdescriptoractivity`](https://bitcoincore.org/en/doc/31.0.0/rpc/blockchain/getdescriptoractivity/) consumes the relevant block hashes and examines those blocks.  
   **Minimal repair:** Gate the post and **each** scan on `chain=main`, completed initial download, tip currency, a [synced basic block-filter index](https://bitcoincore.org/en/doc/31.0.0/rpc/util/getindexinfo/), and `pruneheight <= 972269` at that time. In 31.x, `pruneheight` is the **first unpruned block**: equality with 972,269 is sufficient, so “BELOW” is unnecessarily strict. Confirm block 972,269 is readable and record successful completion of both required RPCs. A filter index can remain available for pruned blocks; that alone does not make the specified two-step scan work.

4. **FP4N-R4 — HIGH: The fee estimate may be unavailable when needed.**  
   **Place:** FP4’s step H fee dependency; the setup provides no fee check.  
   **Failure scenario:** A node that has only just synced, or is often off, may lack enough observed transactions and blocks for `estimatesmartfee 6` to return a `feerate`. Its result can instead contain `errors`; the [31.0 RPC documentation](https://bitcoincore.org/en/doc/31.0.0/rpc/util/estimatesmartfee/) says so. An old or absent estimate cannot establish the required fee floor at broadcast.  
   **Minimal repair:** Run and record `bitcoin-cli -datadir=D:\Bitcoin estimatesmartfee 6` on a current node just before the post. Require a numeric `feerate` and no error; otherwise wait for the node to gather data. State the unit conversion for the operator: the RPC returns **BTC/kvB**, and multiplying it by **100,000** gives sat/vB.

5. **FP4N-R5 — HIGH: The hash check does not authenticate the checksum’s publisher.**  
   **Place:** Install steps 1–3.  
   **Failure scenario:** If the installer and `SHA256SUMS` are both replaced at the same download origin, comparison with a hash taken from that origin can still print `True`. Bitcoin Core’s [Windows verification instructions](https://bitcoincore.org/en/download/) call for checking `SHA256SUMS.asc` against independently trusted signer fingerprints.  
   **Minimal repair:** Have a technically capable helper verify the signed checksum file and signer fingerprints **before** handing the owner the exact approved digest. The owner can then perform the single `Get-FileHash` comparison and stop unless it prints `True`. Alternatively, guide the owner through Bitcoin Core’s full signature procedure. I could not independently retrieve the official `SHA256SUMS` bytes through the available web tool, so I do **not** attest to the stated digest.

6. **FP4N-R6 — MEDIUM: Disk capacity is an estimate, with no operating margin check.**  
   **Place:** “about 50 GB on D:” and step 5.  
   **Failure scenario:** The 25,000 MiB target covers block and undo files; chainstate, the filter index, logs and other files are additional. The supplied index and chainstate sizes are unverified. A full D: drive can stop sync or later catch-up. The current 62 GB free does not establish retention through the unknown freeze height.  
   **Minimal repair:** Measure free space and actual `D:\Bitcoin` growth during sync and before the post, reserve operating margin, and stop if it is insufficient. Do not raise the prune target on the strength of the current estimates alone. Bitcoin Core’s [pruning description](https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-0.11.0.md) explicitly separates the block-file allowance from its databases.

7. **FP4N-R7 — LOW: The firewall instruction allows unnecessary inbound connections.**  
   **Place:** Step 6, “allow on Private networks.”  
   **Failure scenario:** The verifier needs outbound peers to sync; it does not need inbound peers. Allowing inbound access on a laptop adds exposure without helping this task. Bitcoin Core’s [full-node guide](https://github.com/bitcoin-dot-org/Bitcoin.org/blob/master/en/full-node.md) distinguishes outbound sync from inbound service.  
   **Minimal repair:** Configure `listen=0` for this verifier and remove the instruction to allow inbound firewall access. Keep RPC at its default local-only binding.

### Windows command check

The listed **PowerShell 5.1 forms appear correct**: `Set-Content -Encoding ascii` with the five strings writes a valid line-oriented `bitcoin.conf`; `Start-Process` accepts the executable as its first positional argument and `-datadir=D:\Bitcoin` as its second; Windows opens a new window by default. The direct `& "…\bitcoin-cli.exe" …` calls are also valid. [Microsoft’s `Set-Content`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/set-content?view=powershell-5.1) and [PowerShell 5.1 `Start-Process`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/start-process?view=powershell-5.1) documentation support those forms. `dbcache=300`, `maxmempool=100`, and `disablewallet=1` do not appear to defeat full validation or the stated scans; `disablewallet=1` fits the no-key intent.

The default `C:\Program Files\Bitcoin\daemon\` path is documented in the [Bitcoin full-node guide](https://github.com/bitcoin-dot-org/Bitcoin.org/blob/master/en/full-node.md), but I did **not** inspect the 31.1 installer or run it on this laptop. Add `Test-Path` checks for both executables and a version check before telling the owner to start the node. `Start-Process` returns immediately, so a successful line 6 alone does not prove that `bitcoind` stayed running.

**Not verified:** the owner’s actual installer files, signature or digest; Windows 11 execution on this laptop; actual disk use, sync duration, fee-estimator readiness, and a live `scanblocks` → `getdescriptoractivity` run. This was a read-only review of a clean working tree; no tests or node commands were run. Under the repository’s review-record rule, these findings still need to be written and committed by the author before this independent check counts as a completed project review.
