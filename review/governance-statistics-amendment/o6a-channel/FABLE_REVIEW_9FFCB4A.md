# Fable focused re-check OF2 of the O-6a specification rev 2 at `9ffcb4a`: READY WITH FIXES

Date: 2026-10-04. This is an R19-2 independent re-check, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

Reviewer: Claude Fable 5.1 (claude-fable-5-1), Anthropic Claude family. This is the R19-2 independent re-check. It was read-only, and no confirmation or lockbox data was read.
Commit: 9ffcb4aa032eabbf80fd00766c55bcc23d82a196 (branch docs/d19-recommendation). Object: review/governance-statistics-amendment/o6a-channel/SPEC.md rev 2. Diff checked: 8f0405f..9ffcb4a.
Verdict: READY WITH FIXES

**Earlier findings**

| ID | Status | Note |
|---|---|---|
| OF1-1 | Partly resolved | §5 freezes the block hash, the order of posts and the acceptance tip. It does not freeze `T` or the round, although ADJUDICATION says it does. See OF2-2. |
| OF1-2 | Resolved | The count is `tip − inclusion + 1 ≥ 6`, and it is used consistently. |
| OF1-3 | Resolved | `A` is checked at signing, and posts count from signing to the end of C2. |
| OF1-4 | Resolved | `K` is destroyed after acceptance. |
| OF1-5 | Resolved | The 39-byte script is exact: `6a 25` + "AQTC2" (`41 51 54 43 32`) + 32 bytes. There is exactly one OP_RETURN. |
| OF1-6 | Resolved | `scanblocks` with `getdescriptoractivity` replaces `-txindex`. The required node settings are missing; see OF2-4. |
| OF1-7 | Resolved | The node governs, a disagreement blocks verification, and blockchair is the substitute. |
| OF1-8 | Resolved | 90 bytes, with a 93-byte script. |
| OF1-9 | Resolved | The full release-note sentence is quoted. |
| OF1-10 | Superseded | Block time no longer sets `T`. |
| OF1-11 | Resolved | One small gap remains; see OF2-5. |
| OS1-1 | Partly resolved | The archive-time design is the right direction. Its capture time is ambiguous, though (OF2-1), and `T` is not stable (OF2-2). |
| OS1-2 | Resolved | §1 limits the claim to "the one admissible commitment". |
| OS1-3 | Resolved | |
| OS1-4 | Resolved | The archive is now named. It is a single point of failure; see OF2-3. |
| OS1-5 | Resolved | The scan range and the previous-output records are now specified. |
| OS1-6 | Resolved | |
| OS1-7 | Resolved | The options are parallel, and the recommendation is labelled as the AI's. |

**Question 2: the `T` design**

The design is sound in principle. When `T` is fixed at a capture time `t`, the round at `t + 24h` has not been published, and the post's txid already commits to the hash. So delaying the capture, or never capturing, gives the declarer no information to choose with. "Earliest capture, by anyone" also stops the declarer from picking among captures, provided the record is stable.

If the archive is unavailable for 7 days, the cycle is invalidated. That works like the disclosed FA5-3 abort: the declarer gains nothing from it, but an outage costs one increment of `m` (OF2-3).

`T` can be earlier than the post's confirmation, or earlier than its broadcast, in two cases:
- Wayback replay of a JavaScript-rendered page (OF2-1).
- An earlier capture that appears in the archive's index late (OF2-2).

**New findings**

| ID | Sev | Location | Problem | Evidence | Fix |
|---|---|---|---|---|---|
| OF2-1 | MAJOR | §5 `T`; §4 archive | "Capture time of a page that shows the accepted post in its block" is ambiguous for pages built in the browser by JavaScript. mempool.space is one; check blockstream.info. A tx page's saved HTML is a generic page with no transaction data in it. When Wayback replays it, the data is fetched from captures of the explorer's API made at other times, so the replayed page can show the confirmed post under a timestamp from before the block existed. An attack follows. The declarer signs N transactions that spend `F`, each with a different hash. He saves each `/tx/<txid>` URL at `t0`. After the beacon for `t0 + 24h` is published, he broadcasts the transaction whose declaration he prefers. A verifier who reads the replayed page dates its capture to `t0`. This reopens choosing the declaration after the beacon is known. | Wayback replays embedded resources from the nearest capture in time, which can be a different time (reviewer knowledge; not fetched). The txid is fixed before broadcast, so its URL can be saved in advance. | Define `T` as the Wayback timestamp of a capture whose raw response bytes contain both the txid and the frozen inclusion block hash. Use the explorer's JSON API URL for this, for example `mempool.space/api/tx/<txid>` and `blockstream.info/api/tx/<txid>`, read from the CDX index for that exact URL. A replayed or rendered page never counts. Keep the hash of the raw response as §4 already requires. |
| OF2-2 | MAJOR | §5 freeze list; §9 `round` | `T` and the round are missing from the "frozen at acceptance" list. `T` cannot always be frozen at acceptance, because the capture may come up to 7 days later. "Earliest capture" is also not stable over time. Collections the archive adds later can carry earlier timestamps, and a capture can be removed or hidden after a request to the archive. In both cases `T`, and with it the round, changes after the beacon is public. A selective removal would give a choice among rounds. | §5 bullets "At acceptance…" and "`T`"; ADJUDICATION row OS1-3 says `T` and the round are frozen. | Fix a single observation point, for example acceptance plus 7 days, or the first capture once it is seen. At that point, take the earliest qualifying capture listed by the archive's index (CDX), record that response and its hash under §27, and freeze `T` and the round. A capture that appears or disappears later is recorded but never changes `T`. |
| OF2-3 | MINOR | §5 7-day failure | The Internet Archive is a single third party, and it has been offline for days before (October 2024). Any outage of 7 days or more invalidates the cycle and costs one increment of `m`, even though nobody did anything wrong. | §5 last bullet | Disclose this risk in §7 and §8. Optionally add a second archive, such as archive.today, under the same "earliest" rule, or extend the window. |
| OF2-4 | MINOR | §4 own node | The node configuration is incomplete. `scanblocks` "requires blockfilterindex". `getdescriptoractivity` includes the mempool by default (`include_mempool=true`), and unconfirmed transactions are not posts. The node must also keep the blocks from `F`'s height onward. The cross-check uses only the block set that `scanblocks` returns, so it checks for false positives, not missed blocks. That is acceptable because BIP158 filters have no false negatives. | scanblocks and getdescriptoractivity docs, Bitcoin Core 30.0 | Require `-blockfilterindex=1`, no pruning below `F`'s height, `include_mempool=false`, and `filter_false_positives=true`. Describe the cross-check as removing false positives. |
| OF2-5 | MINOR | §8 (A); §9 | Under "what you do", (A) leaves out three things: saving the archive captures, the 7-day archive risk, and destroying the key after acceptance. §9 `round` does not repeat §5's "in its frozen inclusion block". | §8 (A); §9 `round` | Add one line on the steps and the archive risk to (A). Make §9 `round` cite §5's exact definition, with the OF2-1 and OF2-2 wording. |

Otherwise, §8 is neutral and plain enough for a non-specialist owner.

**Sources**
- Bitcoin Core 30.0 `scanblocks` documentation: https://bitcoincore.org/en/doc/30.0.0/rpc/blockchain/scanblocks/ ("requires blockfilterindex"; false positives at a rate of 1/M; `filter_false_positives` option).
- Bitcoin Core 30.0 `getdescriptoractivity` documentation: https://bitcoincore.org/en/doc/30.0.0/rpc/blockchain/getdescriptoractivity/ (`include_mempool` defaults to true; "pairs well with" `scanblocks`).
- Repository: SPEC.md rev 2, ADJUDICATION_8F0405F.md, FABLE_REVIEW_8F0405F.md, SOL_REVIEW_8F0405F.md.
- Reviewer knowledge, not fetched: Wayback replay timing and the CDX index, the Internet Archive outage of October 2024, BIP158 filter contents, mempool.space being rendered in the browser, and the AQTC2 byte values.

**For the owner**
1. The revised Bitcoin design works: the post's time now comes from an independent archive, so the random draw cannot be chosen after the fact.
2. Two wording fixes are needed first. The time must come from the archive's raw saved data, not from a replayed web page. It must also be recorded once and never change afterwards.
3. Choosing (A) also means the cycle depends on the Internet Archive being reachable within a week of the post.
