# Sol fix-check BS5 of the D-19 preregistration §13 rev 7f at `02c14e5`: READY WITH FIXES

Date: 2026-10-04. R19-2 independent statistical fix-check, run with Codex CLI (`codex exec`, model requested `gpt-5.6-sol`, reasoning effort high), read-only. The drafter is Claude Opus 5.5. The reviewer's final report is reproduced below unchanged.

---

Model identity: OpenAI Codex, GPT-5; no finer serving-model identifier is exposed.

Commit reviewed: `02c14e5d8c44978e19f7cae359220853d3651059`

Verdict: **READY WITH FIXES**

Prior findings:

- BF4-1: RESOLVED
- BF4-2: RESOLVED
- BF4-3: RESOLVED
- BS4-1: PARTIALLY RESOLVED
- BS4-2: RESOLVED

BS5-1 — MINOR — `PREREGISTRATION.md` §13 item 6, QJ escape bullet; `ADJUDICATION_9D811E6.md` escape-cost row. The cost formula now treats QJ correctly, but its probabilities assume independence between the two QJ tests. QJ is joint, no decided record establishes independence, and BS4-1 requested dependence-robust bounds. Fix: use QJ union bounds or a directly measured joint QJ escape rate, then propagate that range/rate into the totals.

No other new error or decided-record inconsistency was found in the changed text.

Owner: The fixes are sound except that the two QJ tests must not be budgeted as independent without evidence.
