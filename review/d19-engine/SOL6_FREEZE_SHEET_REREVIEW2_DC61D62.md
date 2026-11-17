# Sol re-review 2 of the freeze/held-out sheet (dc61d62)

**Reviewer:** Codex CLI v0.162.1, header `model: gpt-6-sol`, `model_reasoning_effort=high`, `-s read-only`, 2026-10-24. Packet: prompt with timing facts, `git diff 8f4b4b4..dc61d62` of the sheet, sections J-M, prereg §4 pre-run/failure lines (pasted).
**Recorded and adjudicated by:** Claude Opus 5.5 (`claude-opus-5-5`).

## Verdict: FIX. FH2-1 closed; two findings

| ID | Severity | Finding (summary) | Adjudication |
|---|---|---|---|
| FH3-1 | MAJOR | A late first qualifying capture puts the round after the freeze read, so a same-day drand fetch would find no output. | **Accepted, repaired:** the fetch is made after the freeze read and after the round's scheduled time, whichever is later, and within 7 days of the scheduled time. |
| FH3-2 | MAJOR | Record 2 names minute `S` but accepted a start up to 10 minutes later. | **Accepted, repaired:** docker's recorded start must fall within the UTC minute `S`; otherwise the attempt stops before any held-out result is read, for the owner's decision. |

No finding is left unrepaired.

## Reviewer's final output (verbatim)

**Verdict: FIX.** FH2-1 is closed: the sheet requires checking candidates in timestamp order and retaining evidence for every earlier rejection. FH2-2 and FH2-3 still have failure cases.

| Finding | Severity and location | Concrete failure case | Smallest fix |
|---|---|---|---|
| **FH3-1** | Major — §K, drand output | The node sees acceptance on day 0, the freeze read occurs on day 7, and the first qualifying capture is from day 6.5. Its selected round is scheduled around day 7.5. The required same-day drand fetch cannot obtain an output that has not been published. This is not grounds to void the attempt. | Keep the one-time CDX freeze read, but fetch drand after the selected round is published. Complete record 1 before the run; apply the already fixed FP3 disposition only if the seven-day deadline passes without a verifying output. |
| **FH3-2** | Major — §K record 2 and §L | Record 2 says the run starts at `S`, yet a Docker start nine minutes after `S` is expressly accepted. The committed pre-run record then names a time at which the run did not start. | Require Docker’s recorded start to fall within the stated UTC minute `S`, and state the outcome if it does not. |

FH2-3’s seven-day evidence works when the round has already been published at the freeze read, but FH3-1 prevents its unconditional same-day rule from closing the issue.
