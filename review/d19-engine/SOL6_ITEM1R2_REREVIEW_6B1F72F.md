<!-- Recorded verbatim from codex exec (OpenAI Codex v0.160.0) on 2026-10-10. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12603-3e6f-7e13-b1fd-02cce9b9c9b9. Tokens used: 30,029. Made from a packet (Codex's command runner fails here): review/d19-engine/ITEM1R2_REREVIEW_PROMPT.md, the previous Sol review, ADJUDICATION_ITEM1R2_A6EC3C5.md, git diff a6ec3c5..6b1f72f -- calibration scripts tests, and the HEAD text of calibration/choices.py, dsr.py, classifier.py, scripts/d19_run.py. -->

# Focused re-review of I1R2 repairs at `6b1f72fac4633161690538e606323b2c1d2e5d84`

## Reviewer and scope

- **Reviewer:** Independent Codex reviewer, not an authority. This interface identifies the assistant as GPT-6 based; it does not expose an exact model ID or reasoning effort.
- **Commit reviewed:** `6b1f72fac4633161690538e606323b2c1d2e5d84`, as given; not independently verified.
- **Basis:** Attachments only: the prior review, adjudication, diff, and supplied HEAD file text. I checked I1R2-1, I1R2-2, the new tests, and behavior introduced by the repairs.

## Commands run

None. The command runner was unavailable. The adjudication’s reported test results were not independently verified.

## Verdict: **FIX for pilot use of the choices report**

I1R2-2 is repaired by inspection. I1R2-1 is improved, but `consistent` still accepts records that `dev_replication` cannot write.

## Findings

### I1R3-1 — Medium — Rule outcomes can disagree before block-rule selection

**Location:** `calibration/choices.py:92–120`

**Concrete failure scenario:** In a K = 2 record, give `largest` the reason `INVALID_SERIES` and `median` the reason `ZERO_VARIANCE_COLUMN`, with the null fields required for each refusal. `consistent` can accept both entries. Both evaluations receive the same matrix, and `dsr.evaluate` applies rules 1–4 before the family block rule can affect the result; it cannot return those two different reasons for one replication. The same concern applies to other rule-independent early outcomes and the fixed classifier decision.

**Proposed repair:** Enforce agreement between the two entries whenever evaluation stops before block-rule-dependent work. Add a K = 2 corruption test that changes only one rule’s early reason.

### I1R3-2 — Medium — Stored DSR fields remain outside the consistency check

**Location:** `calibration/choices.py:102–117`; `scripts/d19_run.py:134–143`

**Concrete failure scenario:** Start with an otherwise valid `UNSUPPORTED_LAW` record and replace its `length_ratio` and top-level `columns` with `None`. `consistent` still accepts it. That return of `dsr.evaluate` supplies both a ratio and column results, which `dev_replication` encodes and stores. Conversely, the rule 1–2 returns have neither. The new checks cover `z`, `s0`, `block`, and `nominee`, but therefore do not establish the stated “exactly the records” claim.

**Proposed repair:** Check `length_ratio` and the shared `columns` field against the presence and encoding implied by each return path, including their agreement across the two rules. Add corruption tests for a refusal with computed lengths and for an early refusal.

## Repair and test assessment

- **I1R2-1: partially repaired.** The added checks reject the listed invalid nominee and null or populated `z`, `s0`, and `block` cases. The new corruption test would fail against the previous implementation: it previously accepted, among other cases, a matching but invalid nominee and a rule 5–6 refusal without `block`. It does not exercise either finding above.
- **I1R2-2: closed by inspection.** `column_checks` now records `[False, None]` for a non-finite column and describes the entries as per-column predicates. Its test checks finite, constant, NaN, and infinity columns. The previous implementation would report a non-finite column’s variance entry as `True`, so this test would fail without the repair.

No other issue introduced by these repairs was identified from the attachments.
