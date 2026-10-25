# Codex re-review 3 of the FP4 laptop node steps, revision 4

Prompt: `review/fp4-node/FP4_NODE_REREVIEW3_PROMPT.md` (0a5423a).
Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-sol`,
sandbox read-only, reasoning effort high, live web search on,
session id `01a1720a-4b02-7d61-b6ef-e0c473bd7775`, 43,424 tokens.

Verdict: **FIX**. Findings FP4N4-R1, FP4N4-R2.

## Report (verbatim)

## Verdict: **FIX**

- **FP4N4-R1 — HIGH:** FP4N3-R1 is still unresolved. [S2](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt:67) turns one measured window, `W`, into a fixed future date. Bitcoin Core prunes to a **byte target** by deleting block files, so `W` can shrink as later blocks are stored. After the date is filled, S2 no longer requires a check before restarting from a stale photo. A laptop could restart *before* the forecast date, catch up, and prune block 972,269 during that catch-up. Keep the date as a forecast, but require a retention decision before such a restart and act on the measured `pruneheight` while the node runs. [Bitcoin Core 31.1 pruning code](https://github.com/bitcoin/bitcoin/blob/v31.1/src/node/blockstorage.cpp).

- **FP4N4-R2 — MEDIUM:** FP4N3-R2 is still unresolved. [Line 12](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt:56) rounds 7.96 GB to `8.0` (PowerShell displayed `8` in the check), so [S1](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp4-node/FP4_LAPTOP_NODE_STEPS.txt:66) does not stop below its stated 8 GB threshold. Compare the unrounded free space directly with `8GB`.

I checked the committed repair diff and the rounding case; the worktree is clean. Tests, lint, type, and import checks are N/A for this read-only text review. No review record was written or committed, so the repository’s review-record gate remains open.

## Adjudication (Claude Opus 5.5, the author, 2026-10-25)

| ID | Severity | Adjudication | Repair (revision 5) |
|---|---|---|---|
| FP4N4-R1 | HIGH | **Accepted.** W is a byte target in blocks, so it can shrink; a fixed date cannot authorise a restart. | S2 (a): each photo's measured `pruneheight` margin below 3,000 blocks is a STOP for a running node. (b): the date is a forecast only, never a permission, moved only earlier. (c): SAFE START: once the date is filled, and whenever the last photo is older than 7 days, the node is first started with `-connect=0` (no peers, so no new blocks and no pruning), line 10 is photographed, the node stopped, and a normal start waits for the author's GO. |
| FP4N4-R2 | MEDIUM | **Accepted.** | Line 12 is now `(Get-PSDrive D).Free -lt 8GB`, printing True below 8 GB; S1 acts on True. Checked in Windows PowerShell 5.1: `(7.96GB) -lt 8GB` prints True. |
