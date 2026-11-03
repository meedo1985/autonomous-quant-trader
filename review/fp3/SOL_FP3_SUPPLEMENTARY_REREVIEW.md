# Codex re-review of the FP3 supplementary acceptance draft, revision 2 (8f56934)

Prompt: `review/fp3/FP3_SUPPLEMENTARY_REREVIEW_PROMPT.md` (d83e9bc).
Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-sol`, sandbox read-only, reasoning effort high, live web search on, session id `01a17283-92e5-7ac1-9f1b-7900c6c92633`, 51,135 tokens.

Verdict: **FIX**. Findings FP3S2-R1 .. FP3S2-R3.

## Report (verbatim)

## Verdict: FIX

Revision 2 repairs **FP3S-R2–R4 and FP3S-G2–G7** in the wording. **FP3S-G8** is now stated as a pre-G verification task, but the test and committed result remain outstanding. **FP3S-R1 / FP3S-G1 are not resolved:** Rule 5 still lets endpoint checks decide a question the owner framed as whether the output existed within seven days.

| ID | Severity | Finding and minimal repair |
|---|---|---|
| **FP3S2-R1** | **Blocker** | [Rule 5](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md:47>) tests availability at two checks *after* cutoff `C`. A round published before `C` could be unavailable at both checks and be voided. Conversely, a round first published after `C` but before finality must be used, although the [owner chose “Void after 7 days”](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp3/OWNER_PREFERENCES_2026-10-25.md:6>) when it was never published within that period. Define the governing fact as public availability by `C`, allow later evidence of that fact, and seek an explicit owner choice if late first publication is to count. |
| **FP3S2-R2** | **Blocker** | [The checks](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md:49>) leave endpoint selection and check times open. Two endpoints that are down or do not serve quicknet can return no output while another public source serves it. A party that privately saw the round and an unfavorable result could present those failures, then re-post unchanged. The false-void penalty depends on someone later proving availability *at a check*; it does not close that opportunity. Bind eligible, functioning endpoints and check timing prospectively, publish auditable evidence promptly, and make timely-publication evidence govern over failed fetches. |
| **FP3S2-R3** | **Major** | [“Obtained … at any time”](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md:47>) conflicts with a *final* void and [Rule 6’s re-post](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md:55>) if an output appears after finality. The [false-void clause](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/fp3/FP3_SUPPLEMENTARY_ACCEPTANCE_DRAFT.md:52>) also says “failed” if availability at the first check is proved before finality, while the preceding clause says to use an output found before finality. State separately what happens to evidence discovered before finality, evidence discovered after it, and an output first published after `C`. |

The two-check procedure supplies useful evidence, but as written it is neither a sound test of seven-day existence nor resistant to a selective void. This is a read-only wording review: the working tree was clean; tests, lint, type and import checks are inapplicable. This response is **not a committed review record** and cannot count toward the draft’s two-review condition until the findings and observed model metadata are recorded and committed.
