# Sol re-review of the freeze/held-out sheet (8f4b4b4)

**Reviewer:** Codex CLI v0.162.1, header `model: gpt-6-sol`, `model_reasoning_effort=high`, `-s read-only`, 2026-10-24. Packet: prompt, round-1 adjudication, `git diff 6e8c646..8f4b4b4` of the sheet, the whole sheet, O-6a SPEC §4-§5, prereg §4 timing/pre-run/failure lines, DRAFT §2.0 failure rule (pasted).
**Recorded and adjudicated by:** Claude Opus 5.5 (`claude-opus-5-5`).

## Verdict: FIX. FH-2, FH-5, FH-6, FH-7 closed; FH-1, FH-3, FH-4 refined below

| ID | Severity | Finding (summary) | Adjudication |
|---|---|---|---|
| FH2-1 | BLOCKER | J fetched `id_` only for the selected row, so an earlier qualifying capture could be skipped and give a different round. | **Accepted, repaired:** every exact-URL, status-200 row of both URLs is a candidate, examined in timestamp order with its bound `id_` fetch; each earlier non-qualifying candidate keeps its evidence and reason; `T_Q1` is the first qualifying one. |
| FH2-2 | BLOCKER | Record 2 named a future event, not a start time, before the run. | **Accepted, repaired:** record 2 commits a concrete UTC start time `S`; the launch line waits until `S`; docker's recorded start must be at or after `S` and within 10 minutes, else stop for the owner. |
| FH2-3 | BLOCKER | The 7-day rule had no fixed disposition and no evidence of timely existence. | **Accepted, repaired:** FP3's formal outcome fixes the disposition before step G; the round is fetched the same day as the freeze read, so its recorded retrieval time evidences existence within 7 days; where DRAFT §2.0's rule binds, a missing output voids the attempt before evaluation. |

No finding is left unrepaired.

## Reviewer's final output (verbatim)

**Verdict: FIX.** FH-2, FH-5, FH-6 and FH-7 are closed by the pasted repairs. FH-1, FH-3 and FH-4 remain open in the following respects. I found no governance change in the sheet; FP3 still requires a formal decision before step G.

| ID | Severity | Location | Concrete failure case | Smallest fix |
|---|---|---|---|---|
| FH2-1 | BLOCKER | J, selection of `T_Q1` | Two CDX rows have exact URLs and status 200. The earlier row’s `id_` body matches the acceptance-tip hash, but only the later, selected row is fetched. The sheet can record the later `T_Q1` and a different round without establishing that it is earliest. | Examine candidate rows in timestamp order across both URLs. Retain the bound `id_` evidence and rejection reason for every earlier candidate, then fix `T_Q1` at the first verified qualifying capture. |
| FH2-2 | BLOCKER | K, Record 2 | Before launch, the committed record identifies a *future event*, not the time the run starts. Docker’s actual start time is committed only afterward. That does not meet the pasted prereg rule requiring both records, including the start-time record, **before** the run. | Resolve the pre-run time-record procedure against DF5-2 before launch. Commit a concrete UTC start time and enforce it, or obtain formal clarification if the intended rule permits an event-defined time followed by a later evidence commit. |
| FH2-3 | BLOCKER | FP3 and K, seven-day output rule | FP3 says applicability is settled before G, but K sends a missed deadline back to “the FP3 decision” and gives no binding disposition. A valid output fetched after day 7 also proves signature validity, not when verifying output first existed. The attempt could proceed, or be called void or failed, without a fixed rule and timely evidence. | Make FP3’s formal outcome an explicit prerequisite for K’s branch. Record evidence that verifying output existed by the deadline; if the rule binds and that evidence is absent, apply its specified **pre-evaluation invalidation**. If it does not bind, follow the formally settled rule. |

The remaining defects can affect the selected beacon round or whether the held-out run is valid. The sheet should stay **DRAFT, not usable** until they are resolved.
