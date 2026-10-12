<!-- Recorded verbatim from codex exec (OpenAI Codex v0.160.0) on 2026-10-10. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12614-d6c3-7330-b389-0b5aaa4d5667. Tokens used: 35,642. Made from a packet (Codex's command runner fails here): review/d19-engine/ITEM1R3_REREVIEW_PROMPT.md, the previous Sol review, ADJUDICATION_ITEM1R3_6B1F72F.md, git diff 6b1f72f..c90aa7e -- calibration scripts tests, and the HEAD text of calibration/choices.py, dsr.py, classifier.py, scripts/d19_run.py. -->

# Focused re-review of I1R3 repairs at `c90aa7e2094b04b43d3ea8a4988dc89f0a246302`

## Reviewer and scope

- **Reviewer:** Independent Codex reviewer, not an authority. This interface identifies me as GPT-6 based; it does not expose an exact model ID or reasoning effort.
- **Commit reviewed:** `c90aa7e2094b04b43d3ea8a4988dc89f0a246302`, as given and not independently verified.
- **Basis:** Supplied attachments only: the prior review, adjudication, diff, and HEAD text of `choices.py`, `dsr.py`, `classifier.py`, and `d19_run.py`. I reviewed record acceptance, the new tests, and behavior introduced by the rewrite.

## Commands run

None. The command runner was unavailable. The adjudication’s reported checks were not independently verified.

## Verdict: **FIX for pilot use of the choices report**

The rewrite addresses the two reported gaps, but `consistent` still accepts concrete records that `dev_replication` cannot write. I found no record produced by the supplied driver paths that the rewrite would refuse.

## Findings

### I1R4-1 — Medium — Stored lengths, ratio, and family block can contradict one another

**Location:** `calibration/choices.py:97–105, 134–145, 176–178`

**Concrete failure scenario:** The new test helper’s nominally valid K = 2 available record has `T = 9`, column lengths `3` and `3`, and `length_ratio = 0.05` under both rules. `consistent` accepts it, but `dsr.evaluate` computes `max(lengths) / T = 3/9`; `dev_replication` would store that value. With those same columns, changing the median entry’s `block` to `4` also passes, though `family_block` returns `3` for both rules.

**Proposed repair:** Decode the stored lengths and `T`, and compare each entry’s ratio and block with the calculations in `dsr.evaluate`, using the applicable rule. Make the valid test fixtures satisfy those relationships, then add corruption cases.

### I1R4-2 — Medium — Column fields and record shape are not fully checked

**Location:** `calibration/choices.py:119–145, 149–178`

**Concrete failure scenario:** Starting with an otherwise accepted available record, set a finite column’s `column_checks` entry to `[True, None]`. The rule 1 and rule 2 comparisons still pass, but `d19_run.column_checks` writes a Boolean variance predicate for every finite column. Likewise, removing the top-level `u_g` field leaves `consistent`’s result unchanged, although `dev_replication` always writes it. Malformed inner pairs can instead raise an indexing or type error rather than return a consistency problem.

**Proposed repair:** Validate the required record keys and the exact types and two-element shapes of `column_checks` and `columns`, including `None` only where the driver writes it. Reject malformed records through the function’s stated error-result interface.

## Repair and test assessment

- **I1R3-1:** Repaired for the reported early-outcome disagreement. The new K = 2 early-reason and differing-ratio assertions would fail against the previous `consistent`, which checked neither relationship.
- **I1R3-2:** Repaired for the reported presence and absence checks. The new missing-ratio, missing-columns, and rule 1–4 column corruption assertions would fail against the previous implementation.
- The real-record assertion checks that sampled driver records are accepted, but cannot establish that every accepted record is writable. The test helper itself supplies the counterexample in I1R4-1.

No other issue introduced by the rewrite was identified from the attachments.
