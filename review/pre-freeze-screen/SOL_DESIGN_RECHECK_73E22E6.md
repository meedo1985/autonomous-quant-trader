# Codex Sol re-check of the pre-freeze screen change design rev 2 (73e22e6)

Prompt: reproduced in section "Prompt" below. Reviewer metadata from the Codex CLI header (2026-10-31): model `gpt-6-sol`, provider openai, sandbox read-only, approval never, reasoning effort high, Codex CLI v0.164.0, session id `01a191d0-8c16-7352-9e65-dea0829a404e`, 105,840 tokens. Reviewed `review/pre-freeze-screen/DESIGN.md` rev 2 at `73e22e6`.

Verdict: **FIX**: 1 BLOCKER (PFS2-S-1), 1 NON-BLOCKING (PFS2-S-2). No gaps in numbering.

Disposition: both to be applied in design rev 3 (test changes only); none left unrepaired.

## Report (verbatim)

**Verdict: FIX.** Rev 2 resolves the scope and governance issues in the rev 1 review, subject to the proposed R-14a exception being adopted and signed. Its exact reference-vector guard still lacks a required test.

| ID | Severity | Place | Failure scenario and minimal repair |
|---|---|---|---|
| **PFS2-S-1** | **BLOCKER** | [DESIGN.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/pre-freeze-screen/DESIGN.md:47), T1 | “All reference-vector tests pass” does not establish the claimed bit-identical S8 paths vector. The existing [unit test](D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_calibration_screen.py:1812) compares G-11 and G-14 exactly but only checks the *stored constant* for paths; the earlier float-path test uses a tolerance. Pin the pre-edit baseline commit and add an exact `screen_reference_vectors()["paths"]` comparison on the pinned image. |
| **PFS2-S-2** | **NON-BLOCKING** | [DESIGN.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/pre-freeze-screen/DESIGN.md:50), T4 | A counterfactual run on the true `w1` bar need not finish even when the derived-path run does. [Feature generation](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/features/columns.py:107) and [cost volatility](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/backtest/costs.py:245) eagerly compute terminal values. A valid true terminal bar with a modest open but extreme close can overflow its close-to-close ratio and make that run fail, although the terminal values are not consumed by in-window decisions. Limit T4’s equality assertion to consumed values on a successful synthetic pair; do not claim whole-run equivalence for every valid true bar. |

**Rev 1 dispositions:** PFS-S-1 is conditionally resolved by routing the coordinator to R-14a; rev 2 accurately says that proposal is inactive and that the coordinator must be frozen before step G if it is not adopted. PFS-S-2’s guard excludes timing and changed identities, but T1 needs the exact check above. PFS-S-3 matches [Bar’s](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/data/bars.py:133) positive-price, non-negative-volume and OHLC-order rules. PFS-S-4’s object hash, review, G0 and freeze-command consequences are covered. PFS-S-5’s caller-value checks are assigned to R-14a item 5.

C1’s nominee and G-14 seed routing matches the current [fit path](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py:1547). C2’s derived open supplies the [runner’s final exit price](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/backtest/event_contract.py:206). T2, T3 and T5 are sound as designed. I found no further §4 omission or rev 2 regression.

This was a read-only design review: no code, tests or restricted data were run, and no review record was written or committed.
## Prompt

# Re-check: pre-freeze `screen.py` change design, rev 2

You are an independent adversarial reviewer, read-only, not an authority. Write nothing. Follow `.agents/skills/quant-code-review/SKILL.md` and `.agents/skills/scientific-reproducibility-review/SKILL.md` where they apply to a design. Branch `pre-freeze-screen-q2-q5`. Re-check `review/pre-freeze-screen/DESIGN.md` rev 2 (Claude Opus 5.5, commit 73e22e6), which answers your rev 1 review `review/pre-freeze-screen/SOL_DESIGN_REVIEW_CEB12C3.md` (PFS-S-1..5). PFS-S-1 was routed to the owner, who chose a narrow exception; its draft is `git show origin/freeze-sheet:review/governance-statistics-amendment/r14-exception/PROPOSAL.md` (reviewed separately; check here only that the design is consistent with it). Ground truth: `calibration/screen.py`, `calibration/qobj.py`, `src/aqt/backtest/event_contract.py`, `src/aqt/backtest/costs.py`, `src/aqt/data/` (Bar validation), the reference-vector tests, and on `origin/freeze-sheet`: `deploy/calibration/FREEZE_HELDOUT.md`, `review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV3.md` A1b/A6, `PROPOSAL_REV4.md` A1b.

Check: 1. each disposition in §0 (ACCEPT / ACCEPT WITH NOTES / FIX, with evidence); 2. the narrowed guard and T1-T5 (sound, sufficient, testable?); 3. C2 validation vs `Bar`'s own rules; 4. §4 completeness; 5. anything rev 2 broke. Do not re-open accepted points unless rev 2 broke them.

IDs: `PFS2-S-n`, each with severity (BLOCKER / NON-BLOCKING / QUESTION), place, failure scenario, minimal repair. Verdict: ACCEPT, ACCEPT WITH NOTES, or FIX.
