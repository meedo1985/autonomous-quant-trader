# Codex Sol re-check of D-11 revision 2 (845a516)

Prompt: `REREVIEW_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-sol`, sandbox read-only, reasoning effort high, live web search on, session id `01a17362-86fc-7482-987a-051487458508`, 101,117 tokens. (The report says its API exposed only "GPT-6" and calls its IDs provisional; the CLI header, which set the model, says `gpt-6-sol`.) R19-2 re-check 1 of 2.

Verdict: **FIX**. Findings D11R2-S-1 .. S-4.

## Report (verbatim)

## Verdict: **FIX**

Revision 2 repairs the numerical examples, the E-DIFF availability rule, and the block-length choice. Its data-flow and future-window choices still need correction before Q1–Q3 are decision-ready. This is a read-only review of a proposal, not acceptance of D-11.

| Earlier finding | Re-check |
|---|---|
| Sol S-1 | **Resolved.** Both float64 boundary examples now give the operative result. |
| Sol S-2 | **Resolved as a proposed binding.** Sharpe influence \(\psi\) is explicitly chosen for block length. Its predictive coverage remains unestablished; the proposal says so. Politis–White’s basic target is inference for a sample mean. [Politis–White paper](https://public.econ.duke.edu/~ap172/Politis_White_2004.pdf). |
| Sol S-3 | **Partial.** The history, refit schedule and access amendment are identified, but the runnable handover and benchmark start need work below. |
| Sol S-4 | **Resolved.** BTC checks the difference-series result; ETH checks both leg Sharpes; incomplete paths fail closed. |
| Sol S-5 | **Substantially resolved.** Two predeclared evaluations of the exposed window are specified; per-read accounting should be explicit. |
| Sol S-6, S-7 | **Resolved.** Q1 describes an average difference, withdraws the “small cost” claim, and names the outstanding seed and identity decisions. |
| Astra A-1 | **Partial**, for the same data-flow reasons as S-3. |
| Astra A-2, A-3, A-4 | **Resolved**, subject to the stated lack of predictive calibration. |
| Astra A-5 | **Partial.** The historical-window limitation is candid, but the Constitutional wording and shorter-window schedule remain unsettled. |
| Astra A-6, A-7 | **Resolved.** Route D blocks signing as drafted; the probabilities are labelled illustrative and L-2-only where applicable. |

### New findings

- **D11R2-S-1 — BLOCKER, execution contract.** [§4](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV2.md:94>) correctly calculates **S_pre = 2022-11-13** and the **16** refits, and correctly identifies the need to amend Constitution §7a and the threat-model permission. But “prediction artifact plus nominee identity” does not say how `lockbox_eval` obtains and verifies the registered executable strategy, training rule, model artifacts and their hashes. Also, the cited [CPCV precedent](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-d13-proposal/PROPOSAL.md:589>) starts the *candidate* flat while slicing a continuing benchmark series; it does not establish a flat start for both lockbox legs. Specify the immutable artifact lookup and verification path, and justify the proposed benchmark reset against the confirmation source used for prediction. Both-flat may be a reasonable lockbox choice, but it is a new choice.

- **D11R2-S-2 — BLOCKER, Q3’s shorter future-window cost.** [§9 and Q3](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV2.md:208>) offer **180–225 days** inside a 255-day cycle. If both families qualify, the draft requires a **30-day interval between reads** and a **72-hour attestation cooling-off**. Even with zero processing time, the first read must occur by about **day 222** for the second to finish by day 255. A 225-day future window therefore cannot support that advertised two-family route within the current cap. Give the owner a feasible schedule, including processing time, or say which timing rules also require amendment. The quoted standard-error range itself is arithmetically correct.

- **D11R2-S-3 — NON-BLOCKING, authority wording.** [D11-12](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV2.md:227>) says the positive float residue is “accepted under C-0 Numerics.” [C-0](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_C_GATE_DEFINITIONS.md:77>) labels its extension beyond named gates an **AI default**; the L gates remain open. The example is useful, but call float64 sign handling a *proposed* D-11 choice for the owner, not an accepted one.

- **D11R2-S-4 — NON-BLOCKING, exposure record.** [§7](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL_REV2.md:153>) reasonably permits the second fixed nominee to use an already-EXPOSED segment. State that **each** read still consumes its family budget, is logged and gets its own evaluation ID, as [Constitution §7](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/docs/RESEARCH_CONSTITUTION.md:72>) requires.

**Owner questions.** Q1 is understandable and honest about Route A’s unknown power cost. Q2 is answerable in principle, but “yes” should refer to the completed executable and benchmark contract in S-1. Q3 states the historical weakness plainly. Its R2 interpretation must be made effective at the **Constitution §0 level** through the §4 process; protocol wording alone cannot override “future data.” Its future-window option needs the corrected schedule in S-2. D11-13 correctly identifies the threat-model amendment; D11-14 correctly keeps the meaning of “future” open.

**Checks:** Read-only Python confirmed 457 days, S_pre, 16 refit dates and the day-222 timing bound. Git status and staged/unstaged diffs were empty; frozen paths showed no diff against `f1c17eb`; all 13 SHA-256 sidecars matched their local files. Tests, lint, typing and import checks are N/A to this document-only re-check. **LOCAL GATE: BLOCKED** by S-1 and S-2. No file was written or committed, so this response is not the committed review record required by `AGENTS.md`.

**Reviewer metadata limit:** This API identifies the current model only as **GPT-6**, without a verified Sol or Astra variant. The `D11R2-S-n` IDs are provisional tracking IDs, not a claim that verified Codex Sol performed this re-check. That metadata gap, and the uncommitted record, mean this response alone cannot satisfy the repository’s R19-2 recording requirement.
