# Sol re-check of R-14a design rev 3 (1d42bb7)

- Reviewer: Codex `gpt-6-sol`, reasoning effort high, `codex exec -s read-only` (run log model line: `model: gpt-6-sol`; session 01a19b3e-c4dd-7b00-b262-c5bc2b1569e7; 97,619 tokens), 2026-11-02.
- Prompt: review/r14a-modules/RECHECK_REV3_PROMPT_SOL.md.
- Finding IDs: R14D3-S-1..4 (all BLOCKER). Verdict: **FIX**.
- Adjudication: pending (to be recorded with the rev 4 repairs).

## Report (verbatim)

**Verdict: FIX.** Rev 3 repairs the inventory, lockbox start state, bundle field list, and much of the prior review feedback. Four issues remain.

| ID | Severity | Finding |
|---|---|---|
| **R14D3-S-1** | **BLOCKER** | The proposed valid start still fails the frozen verifier. The loader creates a module and sets `__file__`, but does not specify a `.py` `__spec__.origin`; `bytecode_problem()` requires that origin for every loaded `calibration` module. The valid-start test is therefore not established. [DESIGN.md:126](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:126>), [rundef.py:323](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/rundef.py:323>) |
| **R14D3-S-2** | **BLOCKER** | The permitted `__main__`-guard entry route executes the module file before its own hash-and-compile check. Keep the entry point in a separately trusted launcher, or specify a route that authenticates the bytes before executing them. This is the remaining executed-bytes issue from R14D2-S-1. [DESIGN.md:115](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:115>), [DESIGN.md:126](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:126>), [DRAFT_WORDING.md:159](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:159>) |
| **R14D3-S-3** | **BLOCKER** | The P18-0 row says the module recomputes `w0 ≥ last + embargo` for C2, then parenthetically says C2’s first embargo is dropped. Annex A expressly grants that first-cycle exception. The check must distinguish C2 from later windows or it can reject an eligible C2 window. [DESIGN.md:77](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:77>), [ANNEX_A_SELECTION_RULE.md:20](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_A_SELECTION_RULE.md:20>) |
| **R14D3-S-4** | **BLOCKER** | Annex A allocation still omits **A-U1’s fail-closed simulated-null screen of the actual trial set before declaration**. The §2 P18-7 row assigns gate computation and cause codes during evaluation, but gives no owner to this earlier declaration condition. [DESIGN.md:86](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:86>), [ANNEX_A_SELECTION_RULE.md:189](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_A_SELECTION_RULE.md:189>) |

**Earlier findings:** R14D-S-1/A-1, S-4, S-6/A-4, S-7, and R14D2-S-3’s lockbox start-state and bundle-field corrections and S-4’s C-6 correction are closed. S-2/A-3 remain open through R14D3-S-3–4; S-3/A-2 remain open through R14D3-S-1–2. S-5/A-5’s confirmation contract is explicitly tracked as a pre-signing build item in [DESIGN.md:277](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:277>). Astra’s rev 2 attempt produced no findings.

The §1 rows agree with the inspected frozen primitives and missing C2 decisions. §7.1’s revised start state and bundle fields agree with [Annex D D-3.3](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_D_LOCKBOX.md:367>) and [B4.2](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_D_LOCKBOX.md:479>). Q-P1 presents the decided baseline and optional earlier binding neutrally; its 700–1,000-line figure is a plausible **rough estimate**, not a measurement. [DESIGN.md:89](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:89>)

**Validation:** `rtk proxy git diff --check 84873ca 1d42bb7` passed; that diff changes only `DESIGN.md`, and the worktree is clean. No startup test is possible yet because the modules do not exist. This read-only review has not been written and committed as a repository review record, so the project’s review-record gate remains outstanding.
