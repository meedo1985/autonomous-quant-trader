# Astra re-check: slice 6b design rev 7 at e2ddcb4 (verdict FIX)

- Reviewer: Codex `gpt-6-astra`, reasoning effort high, `codex exec -s read-only` (Codex CLI v0.164.0; run log model line: `model: gpt-6-astra`; session id: 01a1da08-0015-7ff2-9faa-57bcb38c1307; 79,495 tokens), 2026-11-14. The report says the runtime model ID was not exposed to it; the run log header records it.
- Prompt: `DESIGN_SLICE6B_REV7_PROMPT_ASTRA.md` (commit `d8390c6`). Findings R14D6B7-A-1..3; minor wording points listed at the end. Report below verbatim.

---

**Verdict: FIX.** Three major design gaps remain. Findings are proposals; B-1..B-5 and C-1..C-3 remain closed.

**Model:** exact executing model ID is not exposed; I cannot verify the “Astra” designation. Reviewed Git objects at `e2ddcb4`; checkout HEAD was `d8390c6`.

All design locations below refer to [DESIGN_SLICE6B.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN_SLICE6B.md) **at `e2ddcb4`**.

**Status of R14D6B-FINAL-F-1..9**

| Finding | Status | Evidence in rev 7 |
|---|---|---|
| F-1 | APPLIED | Lines 48, 53, 348–351: separate headers and qualification reread; pinned code unchanged. Direct comparison confirms identical start-chain sections. |
| F-2 | APPLIED | Lines 154–162, 176–181: explicit breached-family states, no waiting, trial refusal. |
| F-3 | PARTIAL | Lines 229–241 add precedence and structured fields, but failure aggregation and override scope remain problematic: A-2, A-3 below. |
| F-4 | APPLIED | Lines 176–181, 201–207: final reread and append share the look lock; consistent lock order. |
| F-5 | PARTIAL | Lines 213–224, 330: closing entry and inter-record abort covered; crash before record persistence remains uncovered: A-1. |
| F-6 | APPLIED | Lines 58–59, 99–104, 133–147, 352–356: attempt binding, cycle-scoped outcomes, protocol check and explicit crash rewrite. |
| F-7 | APPLIED | Lines 75–92: exact schema and body/digest binding. Known-capture verification remains explicitly pending. |
| F-8 | APPLIED | Lines 372–377 identify the governance wording and remaining confirmations. |
| F-9 | APPLIED | Lines 50, 68–73, 105: clock floor and non-nominee residual stated. |

**R14D6B7-A-1 — MAJOR: closing precedes durable delivery of both records**

- **Location:** lines 31–35, 213–224, 319–343.
- **Evidence:** `evaluate_look` builds both records, appends the closing entry, then returns them for store persistence. `ledger.py:411–414` flushes and fsyncs the entry.
- **Failure scenario:** the process dies after the closing append succeeds but before returning—or the store crashes before persisting both records. The ledger declares a finished look, the records are unavailable, a second look is prohibited, and `LOOK_WITHOUT_RECORD` excludes this case because a closing entry exists. This hides an actual completion/delivery failure behind a successful closing marker.
- **Proposed correction:** require durable storage of both exact record byte strings before closing, through a store handle with an explicit durability contract. Alternatively, specify a distinct recovery/termination disposition for “closed, records missing.” Hashes alone cannot recover the records.

**R14D6B7-A-2 — MAJOR: procedure-failure preservation is undefined across breached attempt histories**

- **Location:** lines 139–160, 228–241, 322–324.
- **Evidence:** completion requires exactly one result; breached-family state uses the **last attempt**. Yet `failing{id: reason or state}` and `trials{id: record_sha256}` allow only one value per trial. The design never explicitly makes `u_proc_present` an aggregation over **all validated pre-look results**, regardless of derived completion. Existing `nominate` accepts results only for completed trials (`c2_confirmation.py:864–882`).
- **Failure scenario:** an attempt records `DAYS_INCOMPLETE`, then receives a duplicate result. It is no longer derived-completed and becomes `final`. A completed-only collection omits its procedure reason; a last-value collection can overwrite it. The family becomes U_ops despite the recorded U_proc failure. Retaining history in the ledger does not ensure that the classifier counts it.
- **Proposed correction:** calculate `u_proc_present` before state/result collapsing, as an OR over every identity-valid pre-look unavailable result in the family, including duplicate and superseded results. Preserve their attempt/result identities and reasons; use that flag for C-3. Add the duplicate-result and superseded-attempt cases explicitly.

**R14D6B7-A-3 — MAJOR: §5 extends C-3 beyond order-breached families**

- **Location:** lines 229–241; owner decision C-3, line 12.
- **Evidence:** C-3 selects U_proc for a family **with an order breach and a procedure-failure reason**. Rev 7 instead gives any recorded procedure failure precedence over unfinished trials and misaligned series, even without a breach. Rev 6 placed those infrastructure conditions first.
- **Failure scenario:** an unbreached family reaches day 180 with one running trial and another reporting `DAYS_INCOMPLETE`. Rev 6 classifies U_ops; rev 7 classifies U_proc. This changes ordinary mixed-failure accounting beyond C-3’s selected case.
- **Proposed correction:** apply C-3’s override specifically to order-breached families and retain the existing precedence elsewhere. Any broader precedence change needs its own explicit binding.

**Other checks and minor points**

- No lock-order inversion found: look lock → append lock; `read_entries` acquires neither.
- C-2 deliberately permits an earlier look once all **unbreached** families finish. Breached families remain failed and recorded; no additional family-dropping path found.
- Crash rewrites fit `trial_states`: completed results supply `end`; rewritten crashes supply `failed`/`CRASH_NO_ARTIFACT` and their actual outcome position.
- Clarify minor schema wording: canonical manifest hashing versus raw file hashing; exact bytes hashed by `headers_sha256`; ASCII body encoding; distinct names for capture timestamp `T` and window-length `T`; explicit state for an unstarted trial in a breached family.

**Files and ranges read**

| File | Lines |
|---|---|
| `review/r14a-modules/DESIGN_SLICE6B.md` | 1–380; requested `4b6e6e0..e2ddcb4` diff |
| `FABLE_FINAL_DESIGN_SLICE6B_4B6E6E0.md` | 1–300 |
| `ADJUDICATION_FINAL_DESIGN_SLICE6B_4B6E6E0.md` | 1–35 |
| `OWNER_DECISIONS_DESIGN_SLICE6B_REV6.md` | 1–12 |
| `calibration/c2_confirmation.py` | 600–937, 953–969, 1610–1705, 2430–2705, 2750–2902 |
| `tests/unit/test_c2_confirmation_start.py` | 1–60 |
| `src/aqt/core/ledger.py`; `attempts.py` | 90–415; 270–487 |
| Supporting governance | Constitution 99–108, 140–157; protocol 55–76; hash canonicalization 1–10; O-6a SPEC 80–140 |

**Validation:** read-only Python assertions passed for pinned-section byte equality and isolated slot/look behavior. Git comparison confirmed only five review documents changed. Tests, lint, types and import-boundary suites were N/A to this document-only re-check; proposed orchestration was not executed.

No files were modified. This report is not committed and therefore is not yet a recorded repository review under `AGENTS.md`.