# Codex Sol check of laptop-node sync tuning (2026-10-26)

Owner asked for faster sync and for the change to be checked with Sol. Prompt (verbatim below) proposed `dbcache=1000` and `blocksonly=1`. Reviewer metadata from the Codex CLI header: model `gpt-6-sol`, sandbox read-only, reasoning effort high, session id `01a178ac-7f5b-7962-9a77-43935cdfa697`.

**Outcome (applied by Claude Opus 5.5):** `blocksonly=1` NOT applied (FP4 needs `estimatesmartfee 6`, FREEZE_HELDOUT.md l.92; verified). `blockfilterindex=1` and `prune=25000` kept (o6a-channel/SPEC.md l.53; verified). `dbcache` raised 300 -> 500 only, Sol's cautious value, effective at next node start; watch free RAM and revert to 300 if the laptop pages. No finding left unapplied other than the declined 1000 value and blocksonly, per the verdict.

## Prompt

Read-only advisory check. Write nothing.

A Bitcoin Core v31.1.0 pruned node on a Windows 11 laptop is doing initial block download (block ~600,000 of ~973,250, 32.7%). Machine: 7.8 GB RAM total (~0.8 GB free while bitcoind ~2.1 GB working set and a Claude Code session run), NVMe SSD, on mains power, CPU ~22% busy, 10 outbound peers. Current D:\Bitcoin\bitcoin.conf:
prune=25000
blockfilterindex=1
dbcache=300
maxmempool=100
disablewallet=1
listen=0

Proposed change, applied at next restart: dbcache=1000 and add blocksonly=1.

Questions:
1. Is this change safe and likely to speed up IBD on this machine? Any better value for dbcache given 7.8 GB RAM? Any risk with prune=25000 or with blocksonly=1 for a node that will later be used only to read the chain (no wallet, no relay)?
2. This repository uses the node for the FP4 freeze precondition (search the repo, e.g. review/fp4-node/, deploy/calibration/FREEZE_HELDOUT.md, for "blockfilterindex", "prune", "blocksonly", "dbcache", "mempool", and how the node is used: e.g. reading a block hash/header at a height, rechecking block 972,269). Does anything in the repository require blockfilterindex=1, require mempool/transaction relay, or forbid these config changes? Could blocksonly=1 break any required step (for example if a step needs to see or broadcast an unconfirmed transaction)?
3. Would temporarily disabling blockfilterindex during IBD materially help, and is it allowed by the repository's FP4 procedure?

Answer briefly with a verdict (SAFE / SAFE WITH NOTES / DO NOT CHANGE) per proposed setting, and cite file:line for repository facts. State your model name.

## Report (verbatim)

**Verdict:** Keep `blockfilterindex=1` and `prune=25000`; do not make the proposed `dbcache=1000` or `blocksonly=1` changes for this FP4 node.

| Setting | Verdict | Reason |
|---|---|---|
| `dbcache=1000` | **DO NOT CHANGE now** | Raising it from 300 MiB may help IBD, but the extra 700 MiB is too close to the reported 0.8 GB free while Claude Code is running. Paging could make IBD slower. A cautious trial around **450–500 MiB**, with Windows memory and paging monitored, is more reasonable; speedup is not guaranteed. [Bitcoin Core memory guidance](https://github.com/bitcoin/bitcoin/blob/v31.1/doc/reduce-memory.md). |
| `blocksonly=1` | **DO NOT CHANGE** | The FP4 post requires this node’s `estimatesmartfee 6` to return a numeric rate immediately before broadcast. Bitcoin Core says block-only mode disables fee estimation. `testmempoolaccept` remains an RPC check, and Electrum handles broadcast, so those are not the obstacle. `deploy/calibration/FREEZE_HELDOUT.md:92–114`; [Bitcoin Core traffic guidance](https://github.com/bitcoin/bitcoin/blob/v31.1/doc/reduce-traffic.md). |
| Keep `prune=25000` | **SAFE WITH NOTES** | FP4 permits pruning only while block 972,269 remains readable. The 25,000 MiB target is a moving window, and the procedure requires a retention check before the post and again at later scans. `deploy/calibration/FREEZE_HELDOUT.md:19,61–76,129`; `review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt:67–82`. |
| Temporarily disable `blockfilterindex` | **DO NOT CHANGE** | FP4 explicitly requires the index, a synced `getindexinfo` result, and `scanblocks`. Disabling it may save some indexing work, but there is no established material IBD gain here. If pruning overtakes the index’s last processed block, restoring it can require a full resync. `review/governance-statistics-amendment/o6a-channel/SPEC.md:53–55`; `deploy/calibration/FREEZE_HELDOUT.md:75–77`; [Bitcoin Core index/pruning report](https://github.com/bitcoin/bitcoin/issues/21229). |

Reading confirmed blocks or headers does not require transaction relay. The repository deliberately excludes unconfirmed activity from its scan (`include_mempool=false`), but **its fee-estimate gate does require the node to receive transactions**.

**Model:** GPT-6 (Codex; backend variant not exposed to me).