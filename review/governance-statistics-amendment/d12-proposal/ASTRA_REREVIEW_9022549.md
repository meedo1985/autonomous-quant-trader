# Codex Astra re-check of D-12 revision 2 (9022549)

Prompt: `REREVIEW_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-astra`, sandbox read-only, reasoning effort high, session id `01a174f1-adb9-7ba0-8857-ec5467d4e72f`, 78,073 tokens. (The report says model metadata was not exposed inside the session; the CLI header above is the verified source.)

Verdict: **FIX**. Findings D12R2-A-1 .. A-4.

**ID note:** as in `ASTRA_REVIEW_55554C6.md`, the report below calls itself the "Sol review lineage" and labels its findings `D12R2-S-1` .. `D12R2-S-4`; its table's "earlier Sol finding" rows `D12R-S-1..6` are Astra's own first-round findings as labelled in its verbatim report (that record maps them to `D12R-A-n`; its findings 7-8 are not re-checked here). The text is kept verbatim; in this record and every later reference, this report's `D12R2-S-n` is **`D12R2-A-n`** (same n). Sol's re-check is `SOL_REREVIEW_9022549.md`.

## Report (verbatim)

**Verdict: FIX.** Revision 2 resolves most earlier objections, but the audit-read option and disclosure contract need further repair.

Reviewed commit: `90225492f07927a8f98e76a5694f8a1908089aae`. I use the **Sol review lineage**, with IDs `D12R2-S-n`; exact runtime model metadata is not exposed here and must be verified before recording model identity.

| Earlier Sol finding | Re-check |
|---|---|
| D12R-S-1 — schema versus issuance | **Resolved.** P-1 is explicitly proposed wording; schema compatibility is no longer presented as enforcement. |
| D12R-S-2 — disclosure channels | **Partly resolved.** Readers, scheduled release and private diagnostics are specified; publication metadata still needs binding below. |
| D12R-S-3 — descendants | **Resolved as a proposal.** Explicit precedence replaces unconditional second-family reading. |
| D12R-S-4 — reproduction/read budget | **Partly resolved.** Determinism and independent reproduction are separated, and the budget exemption is withdrawn. R-b remains incomplete. |
| D12R-S-5 — failure paths | **Resolved as a proposal.** Pre-read rejection and post-read failure are distinguished; D12-3 is honestly identified as an amendment exception. |
| D12R-S-6 — field validation | **Resolved.** P-2 requires finite available inputs, actual JSON types and the complete L-1–L-4 PASS. |

1. **D12R2-S-1 — HIGH / BLOCKER: R-b omits material timing and publication consequences.**  
   [§6 R-b and Q4](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV2.md:111) disclose the second read’s budget cost but omit the retained **30-day cooldown**, 75-day post-nomination window and day-255 cap. With two successful nominees requiring primary and audit reads, four reads spaced 30 days apart require **at least 90 days**: a day-180 start gives days **180, 210, 240, 270**, before allowing processing or cooling-off. Staying within v1.0’s numerical read limit does not establish schedule compatibility.

   R-b also needs an explicit variant of steps 1–6: when the primary result is released, whether audit initiation is conditional on its private result, how disagreement becomes the final result, and which evaluation IDs the certificate binds. A seven-day primary release cannot await an audit requiring a 30-day cooldown.

   **Repair:** offer a complete proposed audit schedule and publication rule, identify any additional amendment needed, and disclose the delay or lost promotion opportunity in Q4. Otherwise keep R-b unavailable. R-a’s acknowledged deferred-verification risk does not itself create this scheduling defect.

2. **D12R2-S-2 — MEDIUM / BLOCKER: fixed publication time does not yet fix all published timing information.**  
   [§3](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV2.md:65) retains all twelve attestation fields, including `cooling_off_start`; [§6](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV2.md:108) signs before scheduled release. Nothing binds that timestamp to the scheduled release rather than actual signing/completion. Two PASS executions could therefore publish different completion-dependent timestamps despite identical release times. The owner is research-visible under the proposal’s own rule.

   **Repair:** specify the disclosed timestamp and cooling-off semantics, and prohibit earlier certificate access. Also require the same commitment-bearing release envelope for crashes and ordinary failures: a crash before step 4 must not produce a distinguishable missing commitment. Carry these requirements explicitly into D-20.

3. **D12R2-S-3 — MEDIUM / required D-20 condition: upside logging needs an unavailable case.**  
   [§7](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV2.md:118) defines integer `k` and a Boolean exceedance flag without conditioning them on a finite, available `T_L`. But §4 explicitly permits unavailable statistics and crashes. With ordinary unchecked NaN comparisons, the proposed expressions produce **`k = 0`, `upside_exceedance = false`**, falsely recording a numerical result.

   **Repair:** define finite-input requirements and a sealed unavailable/not-computed representation. Require the rank and upper quantile to use the same verified prediction vector. The proposed 95th percentile is clearly labelled an AI default and introduces no rejection gate; that part is sound.

4. **D12R2-S-4 — NON-BLOCKING / owner-question clarification: Q3 understates its consequence.**  
   [§5](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/PROPOSAL_REV2.md:92) makes **every post-read technical failure** bar descendants. Q3 should plainly say that a crash or signing failure in the first evaluation can prevent the second nominee from being evaluated, even without a demonstrated performance failure. Distinguish the frozen descendant prohibition from this proposed binding of technical failures to `LOCKBOX_FAIL`.

Q1 and Q5 are fair and understandable. Q2 now discloses the exception and baseline-path consequence; its question should also mention that “technical” includes data-dependent unavailability. Q3 needs the clarification above. Q4 is not yet an adequately costed choice.

The PASS lemma, numerical field bindings, descendant precedence, durable pre-access accounting, and D-11 inheritance are otherwise sound at proposal level. None supplies owner acceptance, activation or §16 review.

Validation: all 16 Boolean gate combinations checked; 28 trusted frozen files, 14 sidecars, Constitution self-hash, seven manifest bindings and seven protocol bindings verified. Frozen Git content matches `f1c17eb`; the working tree remains clean. `pwsh` was unavailable, so equivalent read-only Python checks performed the hash verification.

No implementation tests, lint, type or import checks apply to this document-only review. Nothing was written or committed; this response is therefore not yet a committed R19-2 review record.
