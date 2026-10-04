# Adjudication of OF1 (Fable) and OS1 (Sol) on the O-6a specification at `8f0405f`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter
**Records:** `FABLE_REVIEW_8F0405F.md` (`cc136ba`, READY WITH FIXES) and `SOL_REVIEW_8F0405F.md` (`a7dcd6b`, NOT READY)
**Result:** `SPEC.md` revision 2

Every finding is accepted. None is rejected. The stricter reviewer is followed wherever the two differ.

| Finding | Disposition | Where in rev 2 |
|---|---|---|
| OS1-1 (BLOCKER) | Accepted. Bitcoin timestamps have no wall-clock lower bound against a miner, so the block time cannot secure the 24-hour gap. `T` is now the time of the first **independent archive capture** of the accepted post (§5). That is a wall-clock time from a third party, and the post demonstrably existed then. Delaying the capture only moves the round further into the unknown future, so it gives no advantage. Block times are recorded but do not set the round. | §5 |
| OF1-10 | Superseded by OS1-1: `T` no longer depends on block time. | §5 |
| OS1-2 (BLOCKER) | Accepted. The spec now says honestly what the rule does. It selects the **one admissible commitment**: the payload of the first confirmed spend of the bound outpoint. It cannot detect commitments made elsewhere, under other keys or in private, but those can never be presented, because the declaration must match the admissible post. All competing unconfirmed variants (RBF, double-spends) are resolved before `T`, so before the beacon is known; choosing among them gives no information. A **single funding outpoint** is bound at signing. Fee bumps must carry the identical payload. This is the owner's procedure, and it is disclosed as unverifiable for transactions that never confirm. | §3, §7 |
| OS1-3 (BLOCKER), OF1-1 (MAJOR), OF1-2 | Accepted. Confirmations are counted as `tip_height − inclusion_height + 1 ≥ 6`. Before acceptance, the post is re-evaluated on the current chain. At acceptance, the inclusion block hash, the post, the acceptance tip and then `T` and the round are **frozen and recorded under §27**. Any later change to the inclusion block or the order of posts invalidates the cycle, and `T` is never recomputed. | §5 |
| OF1-3 | Accepted. At signing, `A` holds only the funding output and has no spends; this is checked and recorded. Posts count from signing to the end of C2. | §3 |
| OF1-4 | Accepted. `K` stays secured until the post is accepted. After acceptance the owner **destroys `K`** [AI default], so no later spend can be made, by him or by a thief. Payments others make to `A` can then never be spent. | §7 |
| OF1-5 | Accepted. The scriptPubKey is fixed byte for byte: `6a 25 41 51 54 43 32 <32-byte hash>`, 39 bytes. A post has exactly one OP_RETURN output. Matching uses only that script. | §3 |
| OF1-6, OS1-5 (MAJOR) | Accepted. `-txindex` is withdrawn. The scan uses Bitcoin Core 30 `scanblocks` with descriptor `addr(A)` from the funding block's height to the acceptance tip, cross-checked with `getdescriptoractivity`. The record keeps each spent previous output's transaction, script and value, and the inclusion proof. | §4 |
| OF1-7 | Accepted. The verifier's own validated node governs. Any disagreement with the two named explorers is recorded and blocks verification until it is resolved. A substitute explorer is named. | §4 |
| OS1-4 (MAJOR) | Accepted. The independent archive is named: Internet Archive Save Page Now captures of the transaction page on both named explorers, taken once the post is accepted. The record keeps the capture URLs and times, and the hashes of the raw responses. | §4, §5 |
| OS1-6 (MAJOR) | Accepted. The spec now binds the funding outpoint (`txid:vout` and amount, confirmed before signing). The post has a zero-value OP_RETURN output. Fee bumps use RBF with an identical payload. If the post has not confirmed 14 days after first broadcast, the owner may re-broadcast the same payload [AI default]. The disclosed costs now cover two on-chain transactions plus any withdrawal fee. The privacy section now covers the revealed public key, the amounts, the fee and the change linkage. | §7 |
| OF1-8 | Accepted. The old message is 90 bytes, with a 93-byte script. | §3 |
| OF1-9 | Accepted. The full release-note sentence is quoted. | §6 |
| OS1-7 (MAJOR), OF1-11 | Accepted. The options are now parallel and equally specified. Both only fix which commitment is admissible. The difference between them is who can verify it: anyone, or one named person. The costs and practical risks are stated plainly, and the jargon is removed. The AI recommendation is kept but labelled, as the owner asked on 2026-10-04 to be given recommendations. | §8 |
