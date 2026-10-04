# Fable focused re-check OF3 of the O-6a specification rev 3 at `89ecead`: NOT READY

Date: 2026-10-04. This is an R19-2 independent re-check, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

Reviewer: Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family. R19-2 independent focused re-check; the drafter is Claude Opus 5.5. Read-only; no confirmation or lockbox data read.
Commit: 89ecead2cfbee56a689c854290237a062789c36e (branch docs/d19-recommendation). Object: review/governance-statistics-amendment/o6a-channel/SPEC.md rev 3. Diff checked: 9ffcb4a..89ecead.
Verdict: NOT READY. One BLOCKER (OF3-1), and its fix is one rule change. The rest of rev 3 is sound.

**Earlier findings**

| ID | Status | Note |
|---|---|---|
| OF2-1 | Resolved | `T` now comes only from the `id_` body of a block-height API capture. Rendered pages are excluded. |
| OF2-2 | Partly resolved | `T` and the round are frozen at a single read. But the rule that "a capture appearing later never changes `T`" creates OF3-1. |
| OF2-3 | Resolved | The risk is disclosed in §5 and §8(A). Not adding a second archive is a reasoned [AI default]. |
| OF2-4 | Resolved | `-blockfilterindex=1`, no pruning, `filter_false_positives=true`, `include_mempool=false`, and the no-false-negatives note are all present. |
| OF2-5 | Resolved | §8(A) lists the steps and the archive risk. §9 `round` cites §5. |
| OS2-1 | Resolved | A qualifying body equals the hash of block `h+5`. That block does not exist before the 6th confirmation, so no qualifying capture can predate acceptance. |
| OS2-2 | Resolved | The raw bytes, headers, status, URI, timestamp and SHA-256 are retained. If the archive later cannot serve a capture, the retained record governs. |
| OS2-3 | Resolved | There is a 30-day deadline, an invalidation outcome, a fee floor and an RBF rule. See OF3-2 for a verifiability gap. |
| OS2-4 | Resolved | Same as OF2-4. |
| OS2-5 | Resolved | The wording is changed as asked, and (B) now needs its own procedure. |

**Question 2: the `T` rule**
- **Can a qualifying capture predate acceptance?** No. I checked the endpoints live. `GET https://mempool.space/api/block-height/1000` and the same path on blockstream.info both return `200 text/plain` with the 64-hex block hash. A height that does not exist returns `404 "Block not found"`. Before block `h+5` is mined, no body can equal its hash.
- **Do the archive mechanics work as assumed?** Yes. The CDX index lists exact URLs with 14-digit timestamps. `.../web/<ts>id_/<url>` returns the original body, with `x-archive-orig-*` headers and a `memento-datetime` header.
- **Can capture timing alone give a choice of beacon outcome?** No, if the CDX read is honest. Every capture is made in real time, and its round is published only afterwards.
- **The flaw: the freeze read happens after the beacon is public.** The CDX index is read at acceptance + 7 days. By then the beacon for every candidate `T` (each candidate's `T + 24h`) is public. The read itself cannot be verified, which gives the declarer a choice (OF3-1).

**New findings**

| ID | Sev | Location | Problem | Evidence | Fix |
|---|---|---|---|---|---|
| OF3-1 | BLOCKER | §5 `T` ("A capture that appears in, or disappears from, the index later is recorded, but it never changes `T`"); §4 record | The freeze read happens 6 days after the candidate beacons are public. Neither the read nor its time can be verified. CDX responses are unsigned, and a CDX row carries no "indexed-at" time. So a dishonest declarer can save the URL repeatedly, for example every hour for 7 days. After seeing the beacons, he reports as the "earliest listed at the freeze point" whichever capture gives the round he prefers. He then calls every earlier capture "appeared later", and under rev 3 those never change `T`. That is up to ~168 choices of round, which reopens choice of beacon outcome. Honest late indexing also really happens: the Internet Archive adds partner collections afterwards. | §5 text. A live `id_` fetch showed `x-archive-src: portuguese-web-archive-AWP36-2020-1231/...arquivo.pt.warc.gz`, a capture written by a partner archive. CDX has no field for when a row was indexed. | Invert the rule. `T` = the earliest qualifying capture. If anyone, at any time before the evaluation is final, shows a qualifying capture earlier than the recorded `T` that gives a different round, the cycle is invalidated, with the same cost as the FA5-3 abort (one `m`). A removed capture still cannot change `T`, because the retained bytes govern. In §4, also retain the raw CDX responses for both URLs at the freeze point. Hiding a capture then gains nothing. |
| OF3-2 | MINOR | §7 "Fees and deadline" | "30 days after first broadcast" and "fee ≥ `estimatesmartfee`" are self-reported. Broadcast time and the node's estimate leave no public trace, so a verifier cannot check either one. There is no beacon gain, because everything resolves before acceptance. | §7 bullets | Anchor the deadline to a public event, e.g. a block height recorded in the protocol at signing plus 4,320 blocks. Or label both items "procedural; not publicly verifiable", as §7 already does for destroying `K`. |
| OF3-3 | MINOR | §5 `T`; §4 record | The Wayback timestamp is written by whichever crawler made the WARC record, which may be a partner archive, not the Internet Archive itself. It can also differ from the explorer's own `Date` header: in the sample, the memento time was 21:47:42 and the original date 21:45:17. The spec does not define the timestamp format, or say which value governs if they differ. | Live `id_` fetch: `memento-datetime` vs `x-archive-orig-date`, plus `x-archive-src`. | Define `T` as the 14-digit UTC CDX timestamp. Record `x-archive-src` and `x-archive-orig-date`. Optionally set `T` = the later of the two. That can only move the round later, which is safe. |

**Sources**
- Live checks (2026-10-04): `https://mempool.space/api/block-height/{1000,99999999}` and `https://blockstream.info/api/block-height/{1000,99999999}` (200 with the hash; 404 "Block not found").
- `https://web.archive.org/cdx/search/cdx?url=mempool.space/api/blocks/tip/height` (CDX row format).
- `https://web.archive.org/web/20210325214742id_/https://mempool.space/api/blocks/tip/height` (original body; `x-archive-orig-*`, `memento-datetime` and `x-archive-src` headers).
- Repository: SPEC.md rev 3, ADJUDICATION_9FFCB4A.md, FABLE_REVIEW_9FFCB4A.md, SOL_REVIEW_9FFCB4A.md.
- drand timing: reviewer knowledge, not fetched.

**For the owner**
1. The new time rule is the right idea: no archive copy that counts can exist before the post has 6 confirmations.
2. One hole remains. The copy that sets the time is picked a week later, after the random draws are public, and nobody can check that pick. A dishonest declarer could therefore pick the draw he likes. The fix is a one-line rule change: any earlier copy found later cancels the cycle.
3. Two small items: the 30-day deadline relies on the owner's own word about when he sent the post, and the exact archive timestamp should be defined.
