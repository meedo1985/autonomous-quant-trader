# Adjudication of OF2 (Fable) and OS2 (Sol) on the O-6a specification rev 2 at `9ffcb4a`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter
**Records:**
- Fable re-check: `FABLE_REVIEW_9FFCB4A.md` (`0cc0f8e`), READY WITH FIXES.
- Sol re-check: `SOL_REVIEW_9FFCB4A.md` (`bb10c3a`), NOT READY.

**Result:** `SPEC.md` revision 3.

Every finding is accepted. The earlier findings the reviewers rated "partial" (OF1-1, OF1-6, OS1-1, OS1-2, OS1-4, OS1-5, OS1-6) are closed by the rows below.

| Finding | Disposition | Where in rev 3 |
|---|---|---|
| OS2-1 (BLOCKER), OF2-1 (MAJOR), OF2-2 (MAJOR) | Accepted. `T` is now set by a capture that **cannot exist before acceptance**, and only by the raw bytes the archive stored.<br>**What counts.** A *qualifying capture* is an Internet Archive capture of the explorer API URL `https://mempool.space/api/block-height/<h+5>` or `https://blockstream.info/api/block-height/<h+5>`. Here `h` is the inclusion height. Its original body, fetched with the Wayback `id_` modifier, must equal the frozen acceptance-tip block hash: the block that gave the 6th confirmation. That block did not exist before acceptance, so no qualifying capture can predate acceptance, whoever made it and whenever it was requested. Rendered or replayed pages never count.<br>**Which one sets `T`.** `T` is the earliest qualifying capture listed by the archive's CDX index, read once at the freeze point (§5). Later index changes are recorded but never change `T`.<br>**Choosing among captures.** The declarer cannot pick among captures: the earliest is fixed by others' captures and his own alike, and any capture is made in real time before the round that follows it. | §5 |
| OS2-2 (MAJOR) | Accepted. The record retains the raw body bytes, the response headers and status, the capture URI and timestamp, and the SHA-256 of the body. If no qualifying capture exists within 7 days of acceptance, the cycle is invalidated. If the archive later cannot serve a recorded capture, the retained record governs. Its later unavailability is recorded and changes neither `T` nor validity: the verifier then relies on the retained bytes and the block hash, which anyone can check against the chain. | §4, §5 |
| OF2-3 (MINOR) | Accepted as a disclosure. An archive outage of 7 days or more invalidates the cycle (one increment of `m`) with no fault by anyone. A second archive is not added: there is no comparable index API for it, so it would add rules without a reliable "earliest" [AI default]. | §5, §7, §8 |
| OS2-3 (MAJOR) | Accepted. There is now a final deadline. If the post has not confirmed 30 days after its first broadcast, the cycle is invalidated. The owner then spends `F` back to himself with a higher fee. That spend is itself a post, so it closes the record [AI default]. The fee rate at broadcast is at least the node's `estimatesmartfee` for 6 blocks. Bumps until the deadline are RBF with the identical script. | §7 |
| OF2-4, OS2-4 (MINOR) | Accepted. The node runs with `-blockfilterindex=1` and is not pruned below `F`'s height. `getdescriptoractivity` is called with `include_mempool=false`, and `scanblocks` with `filter_false_positives=true`. The cross-check is described as removing false positives, because BIP158 filters have no false negatives. | §4 |
| OF2-5, OS2-5 (MINOR) | Accepted. Option (A) in §8 now lists the steps: the archive capture and the key destruction. It also gives the 7-day archive risk. "Reveals nothing" becomes "does not disclose the declaration's contents by itself". "Anyone, permanently" becomes "anyone with access to public Bitcoin data". Option (B) now says that a receipt and record procedure would need its own specification and review before signing. §9 `round` now cites §5. | §8, §9 |
