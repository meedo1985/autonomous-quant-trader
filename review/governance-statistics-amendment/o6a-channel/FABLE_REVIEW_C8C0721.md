# Fable narrow re-check OF4 of the O-6a specification rev 4 at `c8c0721`: READY WITH FIXES

Date: 2026-10-04. This is an R19-2 independent narrow re-check, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

Reviewer: Claude Fable 5.1 (`claude-fable-5-1`), Anthropic Claude family. R19-2 independent narrow re-check; the drafter is Claude Opus 5.5. Read-only; I read no confirmation or lockbox data and used no network.
Commit: c8c0721 (branch docs/d19-recommendation). Object: review/governance-statistics-amendment/o6a-channel/SPEC.md rev 4. Scope: `git diff 89ecead c8c0721 -- .../SPEC.md`.
Verdict: READY WITH FIXES. Both fixes are MINOR and need only wording.

**Status of the last round's findings**

| ID | Status | Note |
|---|---|---|
| OF3-1 (BLOCKER) | Resolved, with one residual (OF4-1) | Under the inverted rule, a declarer who reports a later capture as `T` can only invalidate the cycle. Any surviving earlier capture can be shown by anyone. The retained raw CDX bytes expose omitted rows, and so does a fresh CDX query. The result is the disclosed abort (one `m`), not a choice of round. The window for showing a capture runs until the evaluation is final. That is the same class as the FA5-3 abort. |
| OF3-2 | Resolved | The deadline is now the public height `D`. The fee floor is labeled procedural. See OF4-2 for bounds on `D`. |
| OF3-3 | Resolved | `T` is the 14-digit UTC CDX timestamp. `x-archive-src` and `x-archive-orig-date` are recorded. Not taking the later-of-two option is reasonable, given the OF3-1 rule. |
| OS3-1 | Resolved | §4 keeps the full CDX evidence: the query URI (exact match, no collapsing, every page), the raw bytes, headers and status, the retrieval time and the SHA-256. §5 binds the `id_` fetch to the row by original URL, timestamp and digest, and rejects redirects. |
| OS3-2 | Resolved | The wording is now "cannot predate the frozen 6-confirmation chain state", and §4 records when the node first saw acceptance. |

**Q1, the remaining route to choosing a round.** One route remains, and it is not abort-only. A capture that has disappeared cannot be shown. The declarer could save the URLs repeatedly, then watch each capture's beacon (`T + 24h`) become public. Before the freeze read (day 7), he could have the archive remove his own unwanted earlier captures. The remaining earliest capture then sets `T`, and nobody can show the removed ones. §5 line 113 says only that he "cannot remove other parties' earlier captures". The route depends on the Internet Archive acting on a removal request from someone who does not own the site within 7 days. That is unlikely, but rev 4 does not state it as an assumption (OF4-1).

**Q2, `D`.** Sound. It is public, fixed at signing and checkable by anyone. Inclusion by height `D` is a public fact, and the fallback self-spend closes the record. The only gap is that `D` has no stated bounds (OF4-2).

**Q3.** No other new defect. §9 `round` and the four `failure` conditions match §5 and §7.

**New findings**

| ID | Sev | Location | Problem | Fix |
|---|---|---|---|---|
| OF4-1 | MINOR | §5 "An earlier capture invalidates"; line 113 | The invalidation rule relies on earlier captures staying visible. If the declarer can get his own earlier captures removed between their beacons and the freeze read, he chooses among about 7 days of candidate rounds, and nothing can be shown afterwards. Rev 4 states only that he cannot remove other parties' captures. | Treat it as a trust assumption. State in §5 and §8(A): "assumes the archive does not remove captures at the declarer's request before the freeze read". Add a procedural rule: the owner requests no removal and makes exactly one Save Page Now request per URL. Removing the risk entirely would need a freeze read within 24h of the first capture, which gives up the 7-day outage tolerance. Not recommended. |
| OF4-2 | MINOR | §3 "Post deadline height `D`" | `D` has no stated bounds. A `D` at or below the signing height makes every cycle invalid. A `D` after C2's end or evaluation conflicts with "before C2 ends". | Add: "`D` > the signing height, and the block at `D` is expected before C2's evaluation starts; this is checked and recorded at signing." |

**For the owner**
1. The fix for last round's blocker works: if anyone finds an earlier archive copy later, the cycle is cancelled, so cherry-picking a copy can no longer pick the random draw.
2. One small gap remains: the rule assumes the archive will not delete your own earlier copies on request, and the spec should say so.
3. The new posting deadline (block height `D`) is a good public fix. It only needs a line saying that `D` must fall after signing and before C2 ends.
