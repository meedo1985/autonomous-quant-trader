# Task 19 review adjudication

Review: `review/task19/REVIEW.md`, saved unedited from the reviewer's reply.
Reviewer: GPT-6 Astra (`gpt-6-astra`, reasoning effort high), Codex CLI 0.154.0,
session `01a0de2d-9e42-72c1-a27f-d723f0b13c4f`, read-only sandbox, no tools,
2026-09-26. Input: the full `main...HEAD` diff (including `LOCAL_REPORT.md`),
implementer-run check output at `44cc8ea`, and the unchanged `aqt.core.ledger`
source. The reviewer did not rerun the checks. Verdict: **FIX**.
Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the implementing model.

| ID | Severity | Adjudication | Evidence |
|---|---|---|---|
| R-1 | BLOCKER | **Accepted, reproduced.** | A router with only `LedgerSink(path, Severity.CRITICAL)` emitting a CRITICAL event with `{"api_key": "credential"}` wrote one entry, kind `ORDER`: the WARNING-level `REDACTION` audit event was filtered out by the sink threshold. |
| R-2 | BLOCKER | **Accepted, reproduced.** | A field named `api_key=` followed by 64 `K`s had its value redacted, but the credential-shaped name reached a stream sink twice: as the field name and inside the `REDACTION` event. |
| R-3 | BLOCKER | **Accepted.** | T19-01 replaced the roadmap's rotating file with a single caller-chosen path, on the implementer's own judgment and without the owner's agreement. That is a scope change the implementer should not have made alone. |

Deviation T19-02 (health checks return events rather than routing them): the
reviewer accepts it. Agreed.

All three are to be repaired in a later commit on this branch.
