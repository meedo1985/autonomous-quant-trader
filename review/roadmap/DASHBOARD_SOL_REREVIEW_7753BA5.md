<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-18. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a14e57-1af6-77a2-aa0c-a88b8a0a9b46. Tokens used: 59,001. Packet built from dashboard-proposal 7753ba5 (git show only): prompt DASHBOARD_REREVIEW_PROMPT.md, DASHBOARD_SOL_REVIEW_807022F.md, DASHBOARD_PROPOSAL.md. -->

# Sol re-review of the dashboard proposal at 7753ba5

## Review (final message, verbatim)

**Verdict: FIX.** The revision resolves DB-2, DB-6, DB-8 and DB-9. DB-4 is substantially addressed. DB-1, DB-3, DB-5 and DB-7 still have gaps that affect what the page can safely serve or claim.

- **DBR-1 — Medium — DB-7 still omits raw decisions.** The `L-02` panel lists the effective count and method, but the prior correction also required raw decisions. “Out of 240 needed” can imply that a fallback count is interchangeable with the primary count, although the cited loss-bound explanation says it is not. Show `raw_decisions`, the effective value, method and unavailable reason; qualify the 240 waiting condition when the fallback method is used.

- **DBR-2 — Medium — DB-5 can still show a stale green page.** Ages and red status are computed when the 15-minute generator runs. If that timer stops, the last static page can remain green indefinitely. The banner’s “shows that the machinery runs” also exceeds what a report and bar establish. Prominently label the page’s generation time and health assessment **“as of”** that time, and describe it as recorded activity rather than proof of a running service. Add a stopped-generator acceptance case.

- **DBR-3 — Medium — DB-1/DB-3 do not yet ensure the web account serves only a finished page.** The generator is told to create its temporary file in the directory served by `http.server`. That server can serve other files there and generates a directory listing if the index is absent ([Python documentation](https://docs.python.org/3.11/library/http.server.html)). Stage the temporary file outside the served directory on the same filesystem, then rename the completed page into place. Verify that no staging file or directory listing is reachable.

- **DBR-4 — Low — “Latest approved commit” needs a verified approval record.** `deployments.jsonl` is a hash-chained ledger; a parseable final line alone does not establish an intact approval chain. Require verification of the whole ledger and its final record type before displaying a commit as approved. Apply the same integrity rule to the incident ledger, and show invalid/unknown on failure.

I reviewed the supplied proposal and adjudication. The exact `b4c5795` ref was unavailable from the connected repository, so this is a proposal review, not verification of that commit’s files or an installed server.

## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-18)

Checked locally: the `l02` mapping holds `raw_decisions`, `effective_decisions`, `method`, `reason` and `target` (`src/aqt/app/forward.py`); the deployment and incident ledgers are hash-chained and verified by `aqt.core.ledger.verify_ledger`, which the dashboard may import (`aqt.core` is not forbidden).

| ID | Severity | Decision | Change to the proposal |
|---|---|---|---|
| DBR-1 | Medium | Accept | `L-02` panel shows raw and effective counts, method and reason, and labels a fallback count as not interchangeable with the primary one. Acceptance case added. |
| DBR-2 | Medium | Accept | "As of <generation time>" at the top; ages and colours computed at that time; a page older than 30 minutes means the dashboard is not updating. Banner says "recorded activity". Stopped-generator acceptance case added. |
| DBR-3 | Medium | Accept | Staging directory outside the served one, same filesystem, atomic rename; the served directory holds only the finished page. Server check: no other path, no listing. |
| DBR-4 | Low | Accept | Both ledgers shown only after `verify_ledger` passes, the commit only when the final record is an approval; otherwise "unknown"/"invalid". Tamper acceptance case added. |

No finding is left unrepaired.
