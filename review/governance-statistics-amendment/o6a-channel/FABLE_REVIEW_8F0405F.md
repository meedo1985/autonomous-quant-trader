# Fable review OF1 of the O-6a channel specification at `8f0405f`: READY WITH FIXES

Date: 2026-10-04. This is an R19-2 independent review, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

Reviewer: Claude Fable 5.1 (claude-fable-5-1), Anthropic Claude family. R19-2 independent review. Read-only. No confirmation or lockbox data was read.
Commit checked: 8f0405f (branch docs/d19-recommendation), object review/governance-statistics-amendment/o6a-channel/SPEC.md rev 1.
Verdict: READY WITH FIXES

| ID | Sev | Location | Problem | Evidence | Fix |
|---|---|---|---|---|---|
| OF1-1 | MAJOR | §5 depth/reorg, §9 `round` | It is not clear when T and the round become final. "Re-apply §3 to the new main chain" lets a post that was reorganized and then mined again count with a new T. A new T means a new round, so a second beacon draw could be possible after the first beacon is public. That line also conflicts with "reorganized away → invalidated". | §5 bullets 2–3 | Freeze T, the block hash and the round when the post first reaches the required depth, and record them under §27. Any later reorganization that changes the post's block invalidates the cycle. Never recompute T. |
| OF1-2 | MINOR | §5 vs §9 | "6 blocks built on its block" means 7 confirmations under Bitcoin Core's convention, where the containing block counts as 1. §9 says "6 confirmations". | §5 bullet 1; §9 `first_post_rule` | Use one wording, e.g. "6 confirmations (the containing block plus 5)". |
| OF1-3 | MINOR | §3 first-post rule | The time scope of "first post" is undefined. A test or accidental spend from A before C2, or before signing, would become the "first post". "During C2" has no start or end. | §3; DRAFT §2.0 `first_post_rule` | Require, and check at signing, that A has no spends at signing. Posts count from signing to the end of C2. |
| OF1-4 | MINOR | §7 custody | Custody covers only theft before the post. Anyone holding K at any time during C2 can spend a later output at A, including payments by others, which counts as a second post and invalidates the cycle (a griefing route). | §7 Custody; §3 "any later post" | State that K stays secured until C2 ends. Or state that the owner may destroy K once the post is final. |
| OF1-5 | MINOR | §3 well-formed post | The exact script bytes are not fixed. A push using OP_PUSHDATA1 still carries 37 bytes of data but gives a 40-byte script. "Other outputs carry no data" cannot be verified (a change program can be any 20 or 32 bytes). | §3, §6 | Define the scriptPubKey as `6a 25 4151544332 <32-byte hash>` (39 bytes). Replace "carry no data" with "no other OP_RETURN output". Matching uses only that script. |
| OF1-6 | MINOR | §4 listing | `-txindex` is not an address index. Bitcoin Core has no address index. | Bitcoin Core `-txindex` indexes by txid only | Use a watch-only descriptor wallet (`addr(A)` or `wpkh(pubkey)`) with a rescan from the key-creation height, or Electrum-protocol scripthash history. Keep the two explorers. |
| OF1-7 | MINOR | §4 | The spec does not say what happens if the two explorers disagree with each other or with the verifier's own node, or if one is unavailable. | §4 bullet 1 | The verifier's own validated node governs. A disagreement is recorded and blocks verification until it is resolved. Name a substitute explorer. |
| OF1-8 | MINOR | §3 | The old message is 90 bytes, not 89 ("AQT C2 DECLARATION SHA256 " is 26 characters, plus 64 hex). Its script would be 93 bytes. The conclusion, that it exceeded the old 83-byte default, is unchanged. | byte count | Change to "90 bytes (93-byte script)". |
| OF1-9 | MINOR | §6 quote | The quoted sentence is cut short. The full release-note text ends "..., not including the scriptPubKey size itself" (the length prefix is not counted). This does not affect the 39-byte result. | Release notes 30.0 | Quote the full sentence. |
| OF1-10 | MINOR | §5 T bound | The argument for the bound is only implied. The lower bound on T is MTP+1s, and MTP usually runs about 1 hour behind wall time, so T can be earlier than the time of inclusion. | consensus MTP rule | Add: "T > MTP ≥ roughly wall time − a few hours, so the round's scheduled time is ≥ about 20 h after the post exists. Gaming T needs majority hashpower." |
| OF1-11 | MINOR | §8 owner question | (A) leaves out operational risks that a non-specialist needs: he must run a Bitcoin wallet himself; one wrong format, an accidental second spend, or a stolen or lost key invalidates the cycle (m increments) or blocks C2; the post is public and permanent. "O-6 is re-asked" and "network fee" are jargon. The "recommended" tag is acceptable because it is disclosed as the AI default. | §8 | Add one sentence on these risks to (A). Explain "O-6 re-asked" as "the earlier seed-disclosure decision must be revisited". |

**Q1 (coverage).** All seven SR3-2 items and the four §2.0 properties are addressed:
- key and post: §3;
- listing: §4;
- depth: §5, subject to OF1-1 and OF1-2;
- T: §5;
- archive: §2 and §4. Archival nodes, two explorers and the verifier's own record are adequate, subject to OF1-7;
- funding and fees: §7. A 1-input, 1-output OP_RETURN transaction has 99 non-witness bytes, which is at or above the 65-byte standardness minimum;
- privacy: §7.

**Q2 (facts).** These are correct:
- P2WPKH spends are signed by K;
- the script is 39 bytes (0x6a, 0x25, 37 data bytes);
- the pre-v30 83-byte limit counted the scriptPubKey;
- the v30 default is 100,000, with multiple OP_RETURN outputs allowed;
- the timestamp must be greater than the median of the last 11 blocks;
- nodes reject a block more than 2 hours in the future;
- the OP_RETURN sits in the outputs, which the txid and the Merkle path cover.

The errors are OF1-6 and OF1-8.

**Q3 (gaming).** These routes give no advantage:
- other keys, address types or signed messages (only spends of A count, and A is fixed at signing, before any declaration);
- RBF or double-spends, and unconfirmed transactions (all are settled before T, so before the beacon is known);
- extra hashes in change outputs or witness data (matching uses only the OP_RETURN);
- payments to A by others (they are not posts).

These routes remain:
- the reorganization re-draw (OF1-1);
- the pre-signing first-post ambiguity (OF1-3);
- griefing with K after the post (OF1-4);
- a deliberate later spend to abort the cycle. This is the known FA5-3 residual and costs an increment of m.

**Q4 (§8).** The question is accurate and mostly neutral but incomplete for a layperson (OF1-11).

**Sources checked:**
- https://bitcoincore.org/en/releases/30.0/ (released 2025-10-10);
- github.com/bitcoin/bitcoin doc/release-notes/release-notes-30.0.md (full datacarriersize sentence);
- the repository files SPEC.md, PROPOSAL.md §4 and DRAFT_WORDING.md §2.0.

These were not re-fetched and come from reviewer knowledge: the Bitcoin consensus rules for MTP and future block time, Bitcoin Core `-txindex` semantics, and the minimum-standard-transaction-size policy.

**For the owner:**
1. The Bitcoin design works: one post from one dedicated address, readable by anyone, and you cannot quietly post twice.
2. Several rules need tightening before the question is put to you. The main one is to lock the post's time permanently once it is confirmed.
3. Choosing (A) means you handle one Bitcoin key and one small payment yourself, and a mistake with that key can cancel the cycle.
