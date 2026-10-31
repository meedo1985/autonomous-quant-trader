# Codex re-review 2 of the FP3 supplementary acceptance draft, revision 3 (631541e)

Prompt: `review/fp3/FP3_SUPPLEMENTARY_REREVIEW2_PROMPT.md` (3d2c4c5).
Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-sol`, sandbox read-only, reasoning effort high, live web search on, session id `01a17295-a286-7ee2-af17-2453e59d4485`, 57,423 tokens.

Verdict: **FIX**. Findings FP3S3-R1 .. FP3S3-R3.

## Report (verbatim)

## Verdict: FIX

Revision 3 resolves **FP3S2-R3**: it defines what happens to evidence found before and after attempt 2’s post, consistent with the owner’s item 6. **FP3S2-R1 and R2 remain only partly resolved.** Rule 5 still permits outcomes that conflict with the owner’s seven-day publication choice and can treat a relay’s stale view as proof about the whole chain.

| ID | Severity | Finding and repair |
|---|---|---|
| **FP3S3-R1** | **Blocker** | [Rule 5, lines 51–64](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md:51): a matching `/info` identifies the chain; it does not establish that `public/latest` is current. Two functioning relays can report `< r` after `C` while another source served `r` by `C`. Their reports prove only what those relays had seen. This leaves the selective-void route in FP3S2-R2 open, especially because evidence discovered after attempt 2’s post cannot cancel the void. Require evidence that supports the *public publication* decision; do not infer global nonpublication from two relay heads. Drand describes relays and CDN caching separately from the nodes that generate rounds. [Drand operator guidance](https://docs.drand.love/operator/), [HTTP API](https://docs.drand.love/developer/http-api/). |
| **FP3S3-R2** | **Blocker** | [Rule 5, lines 55–69](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md:55): suppose `r` is first published at `C + 1 hour`. A decisive check at `C + 2 hours` reports `≥ r`, so there is **no void** and the output is used. A check before publication could instead void the attempt. The note at line 90 says late output gives a void, and [owner preference item 3](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp3/OWNER_PREFERENCES_2026-10-25.md:7) says to void when the number was never published within seven days. Fix the rule so publication time relative to `C`, rather than the chosen check time, determines this case; retain item 6’s attempt-2-post deadline for later evidence. |
| **FP3S3-R3** | **Major** | [Rule 5, line 66](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md:66): `latest ≥ r` after `C` does not establish that `r` was published **by `C`**. It may reflect later catch-up. The sentence “the output is taken to exist” also relies on an endpoint report without requiring its signature to verify. Treat a later head report as a reason to investigate, not proof of timely publication or of a verifying output for `r`. Drand distinguishes scheduled rounds from when beacons are generated during catch-up. [Drand protocol specification](https://docs.drand.love/docs/specification/). |

The fixed endpoints, daily records, and attempt-2-post deadline improve auditability, but they do not make the present void test sound or remove the check-time choice. This was a read-only wording review; tests, lint, type, and import checks are inapplicable. No review record was written or committed, so this response does not satisfy the draft’s committed-review condition.
