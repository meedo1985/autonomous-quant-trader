# Adjudication: Codex review of freeze sheet steps H/I/K/M (d5e7843)

Record: `SOL6_FREEZE_SHEET_HIKM_REVIEW_D5E7843.md` (gpt-6-sol, FIX, HK-R1..R6). Adjudicated by Claude Opus 5.5 (the author), 2026-10-25. All findings accepted.

| ID | Repair |
|---|---|
| HK-R1 | J: the read starts within the hour after the freeze-read time, with retrieval times as proof; otherwise the attempt stops for the owner's decision; a later CDX query is never the freeze read. |
| HK-R2 | K: the first commit of the drand record is the anchor and is never reset. Record 1 is made within 24 h of it; `S` is at least 1 h after record 1 and at most 48 h after the anchor. A miss stops the attempt for the owner's decision. A fresh record 1 does not restart the clock. |
| HK-R3 | H: a retention plan before H. The prune target is computed from the measured window, the projected step-M date + 30 days; the owner frees the space; the target is raised with his OK while `pruneheight` ≤ 972,269; the calculation is committed. Without the space, the post waits. |
| HK-R4 | H.3: `estimatesmartfee 6` runs immediately before each broadcast, including replacements. The transaction's actual sat/vB must be at least that rate. |
| HK-R5 | H0: exact Git Bash commands. `getblockhash` comes first, then `getblock <hash>`. `scanblocks` takes the options object in the 6th argument, with `-rpcclienttimeout=0`. `getdescriptoractivity` takes the block array and the descriptor array. **Smoke-tested on the laptop node on 2026-10-25** at heights 361,990–362,010: `completed: true` with the covered heights, and the activity returned. The `UpdateTip` log format was confirmed: `<UTC> UpdateTip: new best=<hash> height=<h> … date='…'`. |
| HK-R6 | K: chain-specific URL templates (v2 `/v2/chains/$Q/rounds/<r>`, v1 `/$Q/public/<r>`) for api.drand.sh and drand.cloudflare.com; any relay for the same bound round allowed; the forbidden thing is "another chain, round or randomness source". |

The reviewer reran the verifier fixtures and found the verifier and its test adequate.
