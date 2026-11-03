# Astra re-check of R-14a design rev 4 (c2c5131)

- Reviewer: Codex `gpt-6-astra`, reasoning effort high, `codex exec -s read-only` (run log model line: `model: gpt-6-astra`; session 01a19b77-463c-7b71-84a6-b732922a86d1; 134,846 tokens), 2026-11-02. (The report says the runtime model ID was not exposed to it; the run log header records it.)
- Prompt: review/r14a-modules/RECHECK_REV4_PROMPT_ASTRA.md.
- Finding IDs: R14D4-A-1, A-2 (BLOCKER), A-3 (NON-BLOCKING, mandatory before signing). Verdict: **FIX**.
- Adjudication: pending (to be recorded with the rev 5 repairs).

## Report (verbatim)

**Verdict: FIX — two BLOCKER findings and one NON-BLOCKING finding.**

Reviewed rev 4 **`c2c5131`**, governing draft **`8a1ec72`**, engine **`eeaa728`**, and later object files **`eba1c21`**, using Git blobs. No statistical rule changes are proposed.

1. **R14D4-A-1 — BLOCKER — P18-0’s embargo-source check omits the governing R-9 restriction.**

   [DESIGN.md:89](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:89) requires the embargo’s source to be “outside the window.” But [DRAFT_WORDING.md:153](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:153) explicitly **replaces** that condition: the source must have been mounted in the sandbox or evaluated **before declaration**. The prescribed computation repeats this restriction at [line 204](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:204).

   Unexposed lockbox data is outside the confirmation window, so it satisfies the design’s stated source condition while violating R-9. Verifying the arithmetic gap alone does not resolve this.

   **Correction:** assign verification of the R-9 source restriction and prescribed `gap_embargo.rule` to the governance consumer, with the confirmation module checking the resulting evidence and bound value. This restates an existing rule.

2. **R14D4-A-2 — BLOCKER — §7.1’s “complete” adapter contract omits asset and shared-series checks.**

   [DESIGN.md:290](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:290) pairs legs by day index; [line 294](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:294) lists timestamp, interval, start and equity refusals. Neither states the A6 checks for the **asset** and **same series and start for both legs**, required by [Annex D:371–377](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_D_LOCKBOX.md:371).

   Two results from different underlying series can have identical timestamps, lengths, starts and positive equities. They satisfy the listed structural checks but must fail A6. The frozen `daily_returns` helper receives only an `EventResult`; it cannot establish source identity itself ([screen.py:1038](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py:1038)).

   **Correction:** include the missing A6 identity checks explicitly and test wrong-asset and different-series pairs. §6.4’s reference to A6 establishes the intended rule, but §7.1 is not yet its complete consumer contract.

3. **R14D4-A-3 — NON-BLOCKING for this design review; mandatory before signing — launcher binding remains unresolved.**

   [DESIGN.md:340](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:340) correctly tracks the launcher question. However, placing a third launcher’s text in signed protocol bytes does not, by itself, admit that additional file. R-14a permits exactly two further files and preserves the existing loading restrictions ([DRAFT_WORDING.md:157–159](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:157)).

   Keep R14D3-S-2 explicitly **open as a pre-signing build item** until a concrete launch route fits the permitted code locations. Independent review can verify compliance; it cannot create another exception. Removing direct execution fixes the identified unsafe route, but does not yet establish the replacement’s authority.

**The embargo adjudication is correct.** R14D3-S-3’s waiver interpretation should not be adopted. The decisive source is stronger than the Annex A sentence cited in §0.1: **R-3 explicitly defines “first embargo dropped” as excluding those days**, and the partition binding fixes the resulting start ([DRAFT_WORDING.md:147](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:147), [line 196](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md:196)). Cite these directly; the current governing draft leaves no waiver interpretation open.

The remaining requested checks resolve as follows:

| Check | Result |
|---|---|
| **§1 inventory, every row** | C-0, C-6, G-1 through G-14, C-14 and L-1..L-4 correctly distinguish existing primitives from missing C2 decisions. In particular, `screen_gates`, `g11_check` and `g14_check` discard statistics; `gates.g4/g10/g12` are calibration availability checks. |
| **§2 allocation and A-U1** | Owners are now assigned for the previously missing operations. A-U1 names the correct `screen.declare` function and actual output fields: set hash, qualification-object hash and `SCREEN_AVAILABLE`/`INVALID` ([screen.py:2012](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py:2012)). R14D4-A-1 remains. |
| **§4 executed bytes** | Hashing the retained byte buffer and compiling that buffer fixes the substitution problem. Spec-backed module creation fixes the missing-origin refusal. The reviewed mapping admits the two signed modules without admitting a third extra module. Launcher authority remains open. |
| **§7.1 Annex D fidelity** | Revised start state, window lengths, final-hour treatment, transformations and bundle field list agree. R14D4-A-2 prevents calling the contract complete. |
| **§3 Q-P1** | Neutral: (b) is the decided baseline; (a) is optional earlier binding. The review/build/G0 route agrees with `qobj.LATER`, `REVIEWED` and `_reviewed`. **700–1,000 lines plus tests is a plausible rough estimate**, not a measured schedule commitment. |

**Earlier-review accounting:** Rev 1’s inventory, pre-read ordering and Q-P1/Q-D1 findings are addressed. Rev 2’s executed-byte and C-6 findings are addressed; its confirmation-contract work remains explicitly tracked at [DESIGN.md:300](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:300). Rev 3’s spec-origin and A-U1 findings are addressed; its launcher finding remains tracked, and its embargo-waiver interpretation is contradicted by R-3. Astra’s rev 2 attempt produced no findings. The two new blockers above prevent blanket closure of allocation/contract completeness.

Validation:

- `rtk proxy git diff --check 1d42bb7 c2c5131`: **passed**.
- Read-only Python 3.14.7 probes using the frozen verifier functions: spec-backed modules passed; missing spec, stale-cache indication, substituted source and a third extra module were refused. The mapping probe used controlled file snapshots, not a production launch.
- Git-blob verification: **29 protected files unchanged from `eeaa728`; 14 sidecars, manifest entries, Constitution self-hash and protocol bindings passed**.
- Both worktrees remained clean. Implementation tests, lint, types and import-boundary suites were N/A for this document-only review.

Reviewer: this Codex session; exact runtime model ID was not exposed. No files were written or committed, so the repository’s committed-review-record requirement remains outstanding. Actual modules and a qualified-image end-to-end startup were not tested because they do not yet exist.
