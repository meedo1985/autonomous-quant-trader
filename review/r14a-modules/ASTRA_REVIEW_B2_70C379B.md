# Astra review of slice 6b build B2 at 70c379b

- Reviewer: Codex CLI 0.164.0, requested model `gpt-6-astra` (`-c model_reasoning_effort=high`, `-s read-only`); the Codex run log header shows `model: gpt-6-astra`. The reviewer reports the runtime model ID is not exposed to it.
- Prompt: `B2_REVIEW_PROMPT_ASTRA.md` (`82e80df`). Run by Claude Opus 5.5 on 2026-11-15; output recorded verbatim below.

---

**Verdict: FIX.** Four major defects reproduced using synthetic, hash-chain-validated ledgers entirely in memory. No files modified.

**Model:** exact model ID is not exposed; I cannot attest an Astra model ID. Reviewed `10eac2d..70c379b` on `confirmation-module`; HEAD `82e80df` adds only the review notes/prompt.

1. **B2-A-1 — major: wrong-cycle results disappear before identity validation.**  
   [c2_confirmation.py](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:3354), lines 3354–3356.  
   A current-cycle start followed by its result labelled `cycle_id="c0"` is silently skipped. Reproduction: `start A → wrong-cycle DAYS_INCOMPLETE result → outcome A → rerun A → valid result`. The family reports completed, without a breach, and loses the original procedure failure.  
   **Correction:** resolve the referenced start before excluding foreign-cycle results; a result referencing this cycle’s start with a mismatched/missing cycle identity must raise `CycleError`. Add this regression test.

2. **B2-A-2 — major: an outcome can precede its start and steal the re-run slot.**  
   [c2_confirmation.py](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:753), lines 753–760, 773–778.  
   `started_attempt_ids(entries)` includes future starts. Reproduced ledger positions: `0 outcome B; 1 start A; 2 outcome A; 3 start B; 4 rerun B; 5 result B`. Accepted with A `final`, B `completed`, no breach; B’s derived crash has `start=3, end=0`.  
   **Correction:** require an outcome’s start to precede it. Reject this impossible sequence rather than assigning its earlier position to P18-1. Test future-start outcomes separately from never-started outcomes.

3. **B2-A-3 — major: duplicate start IDs are silently collapsed.**  
   [c2_confirmation.py](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:3347), lines 3347–3348.  
   The dictionary retains only the last start for an ID. `start A → duplicate start A → result A` becomes one completed attempt without a breach. The uncollapsed sequence is refused by `trial_states`; `attempt_counts` does not enforce ID uniqueness. This bypasses attempt-history checks.  
   **Correction:** validate duplicate/conflicting start IDs before constructing the lookup; preserve accounting rather than silently overwriting starts. Test identical duplicates and conflicting reuse across trials/cycles.

4. **B2-A-4 — major: an unavailable reason overrides day misalignment.**  
   [c2_confirmation.py](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:926), lines 926–930.  
   A completed result with shifted, well-formed days and `reason="DAYS_INCOMPLETE"` returns **U_proc**, with `failing={"t0": "DAYS_INCOMPLETE"}`. §5 rule 2 requires **U_ops / MISALIGNED_SERIES** before reason classification.  
   **Correction:** check day alignment before the reason branch. Keep the values-length check conditional on an available result, since unavailable results decode to `[]`. Add a test combining shifted days and an unavailable reason in the **same** result.

5. **B2-A-5 — minor: post-outcome results erase the required crash rewrite.**  
   [c2_confirmation.py](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:3388), lines 3388–3394.  
   `start → outcome → result` produces `outcome="breach", end=None`. §3 requires a crash whenever no result precedes the first outcome, with `end` equal to that outcome’s position. FINAL-F-2 still correctly gives `final`; the defect is the derived attempt record.  
   **Correction:** retain the crash rewrite alongside the separate order-breach report. Assert both the state and rewritten fields.

6. **B2-A-6 — minor: the “superseded” test does not exercise supersession.**  
   [test_c2_confirmation_ledger.py](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_ledger.py:342), lines 342–355.  
   The U_proc result belongs to that trial’s **last** attempt. An implementation considering only last-attempt results could pass.  
   **Correction:** add a later successful attempt after the breach, assert the last-attempt state, and verify the older U_proc result’s exact attempt ID/hash remains recorded. Also add a post-outcome U_proc result case.

7. **B2-A-7 — minor: committed cycle tests fail the required formatter check.**  
   [test_c2_confirmation_cycle.py](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_cycle.py:297), lines 297–385.  
   Ruff requests formatting of the changed `nominate` calls. Confirmed against the actual `70c379b` blob, independently of checkout line endings.  
   **Correction:** format this test file and rerun the check.

**Readings**

- **B2-R-1 — AGREE:** pre-look slicing belongs to B3/B5; integration remains unverified.
- **B2-R-2 — AGREE:** unknown families on current-cycle results must refuse.
- **B2-R-3 — AGREE:** use the breaching entry’s position.
- **B2-R-4 — CORRECT:** where no result precedes the first outcome, retain the crash and first-outcome `end`, alongside the breach. FINAL-F-2 remains unchanged.
- **B2-R-5 — AGREE:** configuration mismatch is an identity refusal upstream; nomination’s check is defensive.
- **B2-R-6 — AGREE:** `LEDGER_ORDER:<attempt>` is the breach reason; `failing` supplies trial detail.
- **B2-R-7 — AGREE:** retain `u_proc_results` for available families too.

**Other checks and test quality:** the ordinary completion paths, following outcomes, family-local breaches, FINAL-F-2 selection, required nomination keywords, v2 field copying, governing-window check, exact decoding, and R14S6R-F-5 self-check appear consistent. Existing assertions generally target plausible regressions. Additional missing cases: valid-but-wrong `protocol_hash`, `engine_commit`, and module hash; foreign-cycle/exploration start binding; all outcome words following a result; breach ordering opposite start ordering.

**Validation**

Commands used `rtk proxy`; Python was `.venv/Scripts/python.exe`.

| Command/check | Result |
|---|---|
| Requested three-file `pytest ... -q -p no:cacheprovider` | Exit 1 before collection: no writable temporary directory |
| `python -B -X utf8 -m pytest tests/unit/test_c2_confirmation_cycle.py -q -p no:cacheprovider --capture=sys -k 'not family_attempts_come_from_the_durable_ledger'` | **22 passed, 1 deselected** |
| In-memory Python probes through `ledger._scan` and `family_ledger` | Exit 0; reproduced B2-A-1–5 |
| `python -B -m ruff check --no-cache` on all four changed Python files | Passed |
| `python -B -m ruff format --check --no-cache` on those files | Failed for cycle/run tests locally; committed-blob check confirms only cycle test failure |
| `python -B -m mypy --no-incremental --no-sqlite-cache --cache-dir NUL calibration/c2_confirmation.py` | Passed; initial SQLite-cache attempt failed before checking |
| `.venv/Scripts/lint-imports.exe --no-cache --no-logo` | **7 contracts kept** |
| `git diff --check 10eac2d 70c379b` | Passed |
| Protected-file comparison, 14 frozen sidecars, manifest hashes, Constitution canonical hash | No changes/mismatches |

**Files/ranges read:** build notes 1–end; design 190–352 and 481–503; confirmation module 733–951, 2790–3005, 3298–3412; ledger tests 1–405; run tests 1–414; cycle tests 1–385; attempts 1–487; ledger 1–120, 130–308, 365–415. Also read applicable skills, governance, repository instructions, and CI configuration.

Full three-file validation remains blocked. B3–B5 integration and owner decisions were not reopened. This read-only report is uncommitted and therefore does not yet satisfy the repository’s committed-review-record requirement.