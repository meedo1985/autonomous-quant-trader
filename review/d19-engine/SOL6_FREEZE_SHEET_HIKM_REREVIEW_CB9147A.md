# Codex re-review of freeze sheet steps H/I/J/K/M after HK-R1..R6 (cb9147a)

Prompt: `review/d19-engine/FREEZE_SHEET_HIKM_REREVIEW_PROMPT.md` (36f2de0).
Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-sol`, sandbox read-only, reasoning effort high, live web search on, session id `01a172e1-f89c-77a2-84e7-4f06a15f17a0`, 101,280 tokens.

Verdict: **FIX**. HK-R2, R3, R5, R6 resolved; HK2-R1, HK2-R2.

## Report (verbatim)

**Verdict: FIX.** HK-R2, HK-R3, HK-R5 and HK-R6 are resolved by the repair. HK-R1 and HK-R4 remain incomplete:

- **HK2-R1 — HIGH — freeze-read timing** ([FREEZE_HELDOUT.md](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/deploy/calibration/FREEZE_HELDOUT.md:120)). The stop rule requires the *read to start* within an hour, but the read spans both URLs and potentially multiple CDX pages. A first request can meet the deadline while a later page or second URL is fetched much later, after the index changes. Bound **every CDX request** to the read window, or stop for the owner’s decision if the complete read cannot be obtained in time.

- **HK2-R2 — HIGH — fee check uses the pre-signing transaction** ([FREEZE_HELDOUT.md](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/deploy/calibration/FREEZE_HELDOUT.md:92)). Step H sends the export for decoding *before* signing, then asks for the final transaction’s actual fee divided by virtual size immediately before broadcast. Signing adds witness data, so that earlier decode cannot establish the signed transaction’s actual virtual size. The sheet needs a check of the **signed transaction that will be broadcast**, repeated for replacements, against the fresh node estimate. [Bitcoin Core’s decoder](https://bitcoincore.org/en/doc/31.0.0/rpc/rawtransactions/decoderawtransaction/) reports the serialized transaction’s virtual size; [Electrum’s workflow](https://github.com/spesmilo/electrum-docs/blob/master/coldstorage.rst) separates unsigned preview, signing and broadcast.

This was a read-only document review; I did not test the laptop workflow or commit a review record. The existing frozen-file verifier could not complete under this machine’s PowerShell 5.1 because `Convert.ToHexString` is unavailable.

## Adjudication (Claude Opus 5.5, the author, 2026-10-25)

| ID | Disposition and repair |
|---|---|
| HK2-R1 | **Accepted.** J: every CDX index request (every page of both URLs) within the hour; any miss or unprovable timing stops for the owner's decision. The `id_` fetches of individual captures are not index requests. |
| HK2-R2 | **Accepted.** H.4 split into (a) unsigned check before signing and (b) the signed hex checked with the node before broadcast: `decoderawtransaction` (same inputs/outputs; fee / `vsize` at least a fresh `estimatesmartfee 6`) and `testmempoolaccept`; replacements repeat (a) and (b). |

Reviewer note (frozen-file verifier needs PowerShell 7; it fails under 5.1): known, recorded in `review/skill-handoff/REVIEW.md`; this change touches no frozen file.
