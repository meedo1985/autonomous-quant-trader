# Astra fidelity re-check of the S4 fold-in rev 2 (22252ce)

- **Reviewer:** Codex CLI, model `gpt-6-astra`, reasoning effort high (from the run log); session `01a192c1-3487-75f0-8e4f-462c91950ac9`; tokens used 109,828.
- **Date:** 2026-10-31. Read-only, on branch `freeze-sheet` at `22252ce` (S4 fold-in rev 2).
- **Prompt:** a focused re-check of its own earlier findings (`ASTRA_FIDELITY_REVIEW_C5CB1FF.md`) against rev 2, plus any new contradiction of the four owner choices.
- **Finding IDs:** S4F2-A-1..S4F2-A-13.
- **Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). The report below is verbatim; only this header is added. Dispositions: `FIDELITY_DISPOSITIONS_C5CB1FF.md`, section "Re-check of rev 2".

---

**VERDICT: FIX.** Twelve earlier findings are resolved. The record-contract repair remains incomplete under **S4F2-A-5**. No additional owner decision or new mechanism is needed.

Reviewed clean checkout `freeze-sheet` at `22252ce`. The owner’s four choices are treated as decided, subject to the existing amendment process.

References below: **Annex** = [ANNEX_D_LOCKBOX.md](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/ANNEX_D_LOCKBOX.md); **DRAFT** = [DRAFT_WORDING.md](/D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/s4-amendment-draft/DRAFT_WORDING.md). **R2/R3/etc.** and **C2/C3/etc.** mean the corresponding D-20 proposal and option-C revisions. Numbering maps directly to the earlier findings.

1. **S4F2-A-1 — ACCEPT — NON-BLOCKING (closed).**  
   **Place:** Annex 241–251; DRAFT `processing_cap` and §4.  
   **Evidence:** Owner choice 1 adopts `C = min(T + 255 days, look + 75 days)`. Annex restores the archive-time anchor, single configured cap, and P-6 interpretation, matching R3 208–211 and C2 312. A day-120 look now ends processing at day 195.  
   **Conflicting source:** None remaining. **Minimal repair:** None.

2. **S4F2-A-2 — ACCEPT — NON-BLOCKING (closed).**  
   **Place:** DRAFT R-14d, line 162.  
   **Evidence:** Flat starts now apply specifically to the confirmation source baseline and lockbox runs. The universal final-hour rule remains; C-14 is explicitly preserved. This matches R2 138–145, R3 147–148 and R4 216–219.  
   **Conflicting source:** None remaining. **Minimal repair:** None.

3. **S4F2-A-3 — ACCEPT — NON-BLOCKING (closed).**  
   **Place:** Annex 443–455; DRAFT §4 and §6 signing values.  
   **Evidence:** Custody, no backup, protocol-bound public key, pinned publisher verification, no replacement, and loss/compromise dispositions are restored. The compromise test correctly uses ATTESTATION delivery and RESULT `delivered_at`, as C2 311 replaces R3 198.  
   **Conflicting source:** None remaining against R2 241–245 and R3 193–200. **Minimal repair:** None.

4. **S4F2-A-4 — ACCEPT — NON-BLOCKING (closed).**  
   **Place:** Annex 112.  
   **Evidence:** Restores the worker’s two reads/computations, determinism-only interpretation and captured inputs, matching D-12 rev 7 line 82. It expressly distinguishes later R-a replay.  
   **Conflicting source:** None remaining. **Minimal repair:** None.

5. **S4F2-A-5 — FIX — BLOCKER.**  
   **Place:** Annex 148–150 and 479–485.  
   **Evidence:** Encodings, typed block fields, strict-less-than counting, unavailable upside, reason enums, DEFAULT values, pre-read payload, evaluation ID and nonce are restored. However, the effective record contract remains abbreviated:
   - **R3 line 272** specifies the computed upside record as `{status:"COMPUTED", k:int, exceeds_p95:bool, reason:null}`. The annex never fixes the computed branch’s `reason` to null.
   - **R3 line 274** requires all `operational` fields to be supplied by the store; `read_start` is the store second when the first lockbox byte was served, and `sealed_at` is the store second of the bundle write. Annex names these fields and supplies DEFAULT exceptions, but omits their general ownership and definitions.

   These are residual omissions within the earlier effective-schema finding. Merely retaining the field names leaves implementations able to choose different timestamps or producers.

   **Minimal repair:** Carry those two source rows into §D-3.7, retaining `read_start = null` and `sealed_at = t_s` for DEFAULT. No new fields or mechanism.

6. **S4F2-A-6 — ACCEPT — NON-BLOCKING (closed).**  
   **Place:** Annex 463.  
   **Evidence:** Restores internal `visible_from = t1`, including a barred descendant’s own insert, while withholding it from readers. Matches R8 99, C2 314 and C5 44.  
   **Conflicting source:** None remaining. **Minimal repair:** None.

7. **S4F2-A-7 — ACCEPT — NON-BLOCKING (closed).**  
   **Place:** Annex 404–405.  
   **Evidence:** Once-per-process-start reproduction replaces every-computation reproduction. Separate pre-read P-4 checks remain, matching R3 102, 115 and 134.  
   **Conflicting source:** None remaining. **Minimal repair:** None.

8. **S4F2-A-8 — ACCEPT — NON-BLOCKING (closed).**  
   **Place:** Annex 554–604.  
   **Evidence:** Restores the previously identified artifact, seed, metric, interval, signing, role, compromise and replay tests. T-S1 now preserves admission boundaries and injected-error cases; signer tests use C3’s `sign_permit` replacement. C5’s concurrency assertions are retained. The D-12 test reference is expressly qualified by option C, whose crosswalk deletes T-4/T-7 and replaces the other affected tests.  
   **Conflicting source:** None remaining against R2 121–123, 198–200, 252–256, 320–325; R3 201–205, 319–322; C2 336–343; C3 160; C5 33–38. **Minimal repair:** None.

9. **S4F2-A-9 — ACCEPT — NON-BLOCKING (closed).**  
   **Place:** Annex 320–323.  
   **Evidence:** All three conditions from `OWNER_DECISION_D20_LOCKBOX.md:25` are restored. Commit `f715dfe` is an ancestor of the reviewed commit; the text preserves the separate requirement that the eventual freeze contain it.  
   **Conflicting source:** None remaining. **Minimal repair:** None.

10. **S4F2-A-10 — ACCEPT — NON-BLOCKING (closed).**  
    **Place:** Annex 328–333; DRAFT R-14a.  
    **Evidence:** Restores the later-freeze, unqualified-composition, public-price, implementation-error and earlier-access limitations from R-14a rev 2 lines 58–69 and rev 3 line 34.  
    **Conflicting source:** None remaining. **Minimal repair:** None.

11. **S4F2-A-11 — ACCEPT — NON-BLOCKING (closed).**  
    **Place:** Annex 98; DRAFT history-access rows.  
    **Evidence:** Owner choice 2 explicitly includes 31 May, resolving the earlier endpoint discrepancy. `[S_pre, L1)` now has clear owner authority.  
    **Conflicting source:** None remaining. **Minimal repair:** None.

12. **S4F2-A-12 — ACCEPT — NON-BLOCKING (closed).**  
    **Place:** Annex 327, 530–531; DRAFT R-14a item 5.  
    **Evidence:** Owner choices 3–4 decide lineage before budget and the four-field `code` object. Module contracts must identify A7 field producers, preserving R-14a rev 3 line 30.  
    **Conflicting source:** None remaining. **Minimal repair:** None.

13. **S4F2-A-13 — ACCEPT — NON-BLOCKING (closed).**  
    **Place:** Annex 29, 246, 303; DRAFT R-14a, `added_purposes`, §6.  
    **Evidence:** Visibility follows C4 41; R1 is changed rather than erased, matching C2 332; the adapter matches R2 363–364. R-14a is inlined now, and purpose/checklist entries are synchronized.  
    **Conflicting source:** None remaining. **Minimal repair:** None.

Beyond the residual above, the repairs introduce no identified reversal or invention of a decided rule. The newly inlined R-14a preserves its adopted verification chain, execution boundaries, seed checks and contract allocation.

Read-only arithmetic confirmed the cap examples, 457-day window, strict tie exclusion and quantile equality behavior. Target-file `git diff --check` passed. Protected inventory and bytes match `c5cb1ff`; all 13 frozen sidecars, seven manifest file hashes and the Constitution canonical hash verified. The broader directory whitespace check flags Markdown hard breaks in the archived review.

No files were written or committed. Implementation tests, lint, typing and import checks were N/A for this documentary re-check; implementation correctness was not assessed.