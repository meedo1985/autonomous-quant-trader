# Codex re-review of the FP4 laptop node steps, revision 2

Prompt: `review/fp4-node/FP4_NODE_REREVIEW_PROMPT.md` (5ab63ca).
Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-sol`,
sandbox read-only, reasoning effort high, live web search on,
session id `01a17204-ab70-7f11-baa9-50bf1ffb4b7b`, 76,180 tokens.

Verdict: **FIX**. Findings FP4N2-R1 .. FP4N2-R3; dispositions in
`ADJUDICATION_FP4_NODE_REREVIEW.md`.

## Report (verbatim)

## Verdict: **FIX**

Deferring FP4N-R2, the R3 scan-time gate, and R4 to steps H/I is acceptable **only while they remain explicit blockers to step H**. The repaired setup is a plausible way to start a pruned laptop node, but two operating rules still need tightening before its measurements can be relied on.

| ID | Severity | Place and failure scenario | Minimal repair |
|---|---|---|---|
| **FP4N2-R1** | **HIGH** | [Steps 8 and 10–12, and the retention note](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt:35): a weekly photo can arrive *after* startup and catch-up have pruned block 972,269. No margin or action threshold is specified, so “warn you weeks ahead” is a forecast, not an operational safeguard. Core prunes during initial sync and as block storage grows. [Bitcoin Core pruning documentation](https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-0.11.0.md), [v31.1 pruning code](https://github.com/bitcoin/bitcoin/blob/v31.1/src/node/blockstorage.cpp). | Record an explicit **stop/raise decision point well before** `pruneheight` reaches 972,269. Before a long-offline laptop reconnects near that point, assess the catch-up risk and available disk *before* letting it sync. If retention cannot be maintained through the scheduled freeze read, keep step H blocked. Describe the three-month and January dates as projections only. |
| **FP4N2-R2** | **HIGH** | [R2 disposition](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp4-node/ADJUDICATION_FP4_NODE.md:12): a human running `getblockchaininfo` and noting the laptop’s UTC time records when the human checked, which may be later than when the node **first saw** the sixth confirmation. That difference shifts the specified seven-day freeze point. | Step I must define an event-based way to record the node’s first processing of the acceptance-tip block, tie it to the post and block hash, and verify the laptop clock. Keep the laptop awake, connected and caught up throughout the observation interval; a delayed or unproved timestamp is a stop. |
| **FP4N2-R3** | **MEDIUM** | [R6 disposition and weekly checks](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp4-node/ADJUDICATION_FP4_NODE.md:16): there is no free-space stop threshold or closer monitoring during the first sync. `getblockchaininfo.size_on_disk` covers **block and undo files**, not the whole data directory; the 50 GB total remains an estimate against 62 GB initially free. [Bitcoin Core RPC definition](https://bitcoincore.org/en/doc/31.0.0/rpc/blockchain/getblockchaininfo/). | Check free space during initial sync and before post/freeze operations, measure the whole data directory, and set a conservative minimum free-space threshold that triggers a stop and review. |

The R1 **sliding-window approach is conditionally sound**: `prune=25000` is a storage target; `pruneheight <= 972269` is the correct retention test; increasing the target before that height is pruned can preserve it, subject to measured space. Increasing it afterward restores nothing. A fresh resync is a possible recovery **only if the target and disk can retain F_Q1 through the new tip and freeze read**; otherwise this laptop cannot meet FP4. [Bitcoin Core RPC definition](https://bitcoincore.org/en/doc/31.0.0/rpc/blockchain/getblockchaininfo/), [pruning documentation](https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-0.11.0.md).

The R3 and R4 deferred gates are technically well directed. When written, the scan procedure should check `scanblocks`’s **`completed: true`**, its covered heights, and successful `getdescriptoractivity`, not merely an RPC exit without error; Core documents `completed: false` as a possible result. The `estimatesmartfee 6` numeric/no-error check and BTC/kvB × 100,000 conversion are correct. [scanblocks](https://bitcoincore.org/en/doc/31.0.0/rpc/blockchain/scanblocks/), [estimatesmartfee](https://bitcoincore.org/en/doc/31.0.0/rpc/util/estimatesmartfee/).

R5 and R7 are acceptable on the stated evidence and trust assumption. I did not independently reproduce the signature verification, install Core, or run this node on the laptop. This is a read-only review; its findings have **not** been written and committed as the repository’s review-record rule requires.
