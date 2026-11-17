# Codex Sol re-check 2 of D-11 revision 3 (6ce228c)

Prompt: `REREVIEW2_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-sol`, sandbox read-only, reasoning effort high, live web search on, session id `01a1736f-3050-7c20-a7cb-9703ab7e1bb3`, 93,781 tokens. (The report labels its findings `D11R3-A-n` and says its interface showed only "GPT-6"; the CLI header, which set the model, says `gpt-6-sol`. They are recorded here as **Sol** findings D11R3-S-1..S-5 = its A-1..A-5.)

Verdict: **FIX**.

## Report (verbatim)

## Verdict: **FIX**

Revision 3 repairs the numerics authority wording (**S-3**), per-read accounting (**S-4**), and the unavailable-family sealing branch (**A-1**). It correctly labels both-flat starts as a new proposal (**A-3**) and qualifies D-12 disclosure (**A-4**). The execution and future-window repairs remain incomplete (**S-1/S-2, A-2**). No D-11 binding is accepted by this review.

- **D11R3-A-1 — BLOCKER: executable lookup is assumed, not specified.** [§4](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV3.md:45) says `lockbox_eval` fetches declared trial code, configuration, and model seed from the registry, but does not identify their immutable artifact records or locators. The current [experiment schema](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/schemas/experiment.schema.json) and [trial-record writer](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/src/aqt/core/preregistration.py:457) do not establish that lookup. Revision 3 itself says this was not checked. Specify the stored artifact identity and verified retrieval path; **S-1 is only partially resolved**.

- **D11R3-A-2 — BLOCKER: the timing rules are presented as alternatives without establishing that they are.** [§9](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV3.md:111) offers a fixed day-255 deadline *or* 75 days after nomination. The [S4 draft](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:228) states both a 75-day post-nomination window and a day-255 hard cap. Unless an amendment explicitly displaces one, the safe schedule must satisfy **both**: an early day-120 look ends by day 195. The 215-day route cannot be advertised for an early look on the “fixed cap” reading alone. **D11-15 identifies a real clarification need, but its either/or formulation does not resolve it.**

- **D11R3-A-3 — BLOCKER: the seven-day allowance is sequenced incorrectly.** [§9](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV3.md:102) includes the lockbox run and verification in seven days *before* `R1`, defined as the first read. Those operations require the read. Separate time before the first byte from run, verification, attestation, and cooling time afterward, then recompute the zero-slack 215-day claim. **S-2/A-2 remain partial.**

- **D11R3-A-4 — NON-BLOCKING: sealing statuses overlap.** In [§7](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV3.md:89), a nominee with an unavailable gate is both “not ELIGIBLE” (c) and `UNAVAILABLE` (d), although exactly one status is required. Give (d) precedence so the cause remains auditable.

- **D11R3-A-5 — NON-BLOCKING: Q2 states a conditional premise as fact.** [Q2](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV3.md:164) says both-flat starts match confirmation runs, while **D11-16** correctly says the confirmation baseline start is not yet bound. Present that match as conditional on the D-20 or Annex C decision. **D11-16 is sound.**

**Owner questions:** Q1 is substantially fair, although “every option needs code” should exclude **Keep blocked**. Q2 needs the executable lookup and start-state qualifications above. Q3 candidly describes the historical window; its future-window comparison needs the corrected schedule before it is decision-ready.

Read-only CPython `-B` arithmetic confirmed **457 days, 10,968 hours, 16 refits, S_pre = 2022-11-13**, and the stated values 215, 245, 155, 95, and 497 *under the proposal’s formulas*. That check does not validate the sequencing assumptions. `git status --short` was empty at `6ce228c`; code tests, lint, typing, and import checks are N/A to this document-only review. No file was written or committed.

**Metadata limit:** this interface identifies me as GPT-6, without a verified Sol/Astra variant. The `D11R3-A-n` labels are provisional tracking IDs, not a claim of verified Astra execution. This read-only response is not the committed review record required by `AGENTS.md`.
