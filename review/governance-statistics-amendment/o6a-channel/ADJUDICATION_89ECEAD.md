# Adjudication of OF3 (Fable) and OS3 (Sol) on the O-6a specification rev 3 at `89ecead`

**Date:** 2026-10-04
**By:** Claude Opus 5.5 (`claude-opus-5-5`), the drafter
**Records:**
- `FABLE_REVIEW_89ECEAD.md` (`f7d32ff`): NOT READY
- `SOL_REVIEW_89ECEAD.md` (`784516d`): READY WITH FIXES

**Result:** `SPEC.md` revision 4

Every finding is accepted.

| Finding | Disposition | Where in rev 4 |
|---|---|---|
| OF3-1 (BLOCKER) | Accepted, with the reviewer's fix. `T` is still frozen at the freeze point. But if anyone shows a qualifying capture earlier than the recorded `T` that gives a different round, at any time before C2's evaluation is final, the cycle is invalidated. That costs one increment of `m`, the same as the FA5-3 abort. A declarer who reports a later capture as the earliest, after the beacons are public, can therefore only invalidate the cycle, never choose a round. The rule also covers honest late indexing. A capture that disappears never changes `T`. | §5 |
| OS3-1 (MAJOR) | Accepted. At the freeze point the record keeps, for both URLs: the exact CDX query (exact match, no collapsing, every page), the complete raw response bytes, the headers and status, the retrieval time and the SHA-256. It also keeps the time the verifier first saw the post accepted. A qualifying row must match the URL exactly and have archived status `200`. Its `id_` fetch must match the row's URL, timestamp and digest. A replay redirect, or any other timestamp, does not count. | §4, §5 |
| OF3-3 (MINOR) | Accepted. `T` is the 14-digit UTC CDX timestamp. `x-archive-src` and `x-archive-orig-date` are recorded but do not set `T`. The CDX timestamp is the archive's own fetch start time, per the reviewer's source. The later-of-two option is not taken, because the invalidation rule (OF3-1) already closes the choice [AI default]. | §4, §5 |
| OF3-2 (MINOR) | Accepted. The deadline is now public: block height `D`, fixed at signing at about the planned posting date plus 4,320 blocks (about 30 days). If no post is included by `D`, the cycle is invalidated. The fee-rate floor is labelled procedural and not publicly verifiable. | §3, §7, §9 |
| OS3-2 (MINOR) | Accepted. A qualifying capture cannot predate the frozen 6-confirmation chain state. It may predate the verifier's own observation of that state, and this weakens nothing. The observation time is recorded because it starts the 7-day window. | §4, §5 |

The two new invalidation conditions and the deadline are also added to the owner's risks in §8 (A).
