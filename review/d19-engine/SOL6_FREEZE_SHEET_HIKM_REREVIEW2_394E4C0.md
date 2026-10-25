# Codex re-review 2 of freeze sheet after HK2-R1, HK2-R2 (394e4c0)

Prompt: `review/d19-engine/FREEZE_SHEET_HIKM_REREVIEW2_PROMPT.md` (a229954).
Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-sol`, sandbox read-only, reasoning effort high, live web search on, session id `01a172e5-d4c8-7280-9818-fe681628ce3c`, 69,681 tokens.

Verdict: **FIX**. HK2-R1 resolved; HK2-R2 resolved with new HK3-R1.

## Report (verbatim)

What this change does: The repair makes every CDX page subject to the one-hour window and checks the signed transaction’s actual fee rate before broadcast.

**HK2-R1: Resolved.** [Step J](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/deploy/calibration/FREEZE_HELDOUT.md:132) requires every index request for both URLs to finish within the hour, with a stop if timing cannot be proved.

**HK2-R2: Fee-check defect resolved, but the repair introduces one defect.**

- **HK3-R1 — Must fix:** [Step H.4(b)](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/deploy/calibration/FREEZE_HELDOUT.md:104) tells the owner to send the signed hex before approving broadcast and calls it public data. Anyone receiving that hex can submit the transaction without the owner pressing Broadcast; [Bitcoin Core’s `sendrawtransaction`](https://bitcoincore.org/en/doc/30.0.0/rpc/rawtransactions/sendrawtransaction/) accepts signed hex directly. Keep the hex on the laptop. Run the signed checks there and send a report containing the txid, checked inputs and outputs, fee, `vsize`, fresh estimate, and mempool acceptance result.

**Verdict: FIX.** This was a read-only review; no review record was committed.

## Adjudication (Claude Opus 5.5, the author, 2026-10-25)

| ID | Disposition and repair |
|---|---|
| HK3-R1 | **Accepted.** H.4(b): the signed transaction is saved to a file on the laptop and never sent, pasted or committed before broadcast. The AI reads it only on the laptop, with `decoderawtransaction` and `testmempoolaccept` (test-only), never `sendrawtransaction`, and records a report (txid, inputs/outputs, fee, vsize, fresh estimate, acceptance result). The owner alone presses Broadcast; the file is deleted after broadcast. |
