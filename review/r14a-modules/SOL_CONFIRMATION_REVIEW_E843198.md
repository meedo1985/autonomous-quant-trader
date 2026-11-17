# Sol independent review of the R-14a confirmation module, slices 1-3 (prompt at e843198)

- Reviewer: Codex `gpt-6-sol`, reasoning effort high, `codex exec -s read-only` (run log model line: `model: gpt-6-sol`; session 01a1b59e-1680-7982-b50e-69b4786df98d; 136,738 tokens), 2026-11-07. The report says the interface did not expose exact model metadata; the run log header records it.
- Role: the different-model review R-14a item 1 requires. Author of the module: Claude Opus 5.5.
- Prompt: review/r14a-modules/CONFIRMATION_REVIEW_PROMPT_SOL.md. Code: 87b7cf7 (slices 1-3) at e843198.
- Finding IDs: R14C-S-1..4 (BLOCKER), R14C-S-5 (QUESTION), R14C-S-6 (BLOCKER). Verdict: **FIX**.
- Adjudication and repairs: review/r14a-modules/CONFIRMATION_ADJUDICATION_E843198.md (to be written).

## Report (verbatim)

What this change does: Slices 1–3 add the C2 gate decisions, nominee runs, and Annex A selection helpers. The individual gate thresholds I checked match Annex C, including the G-4 rate, the 20-trial PBO switch and 0.30 limit, and the 476-of-500 null rule. The orchestration still has blocking paths.

### Findings

- **R14C-S-1 — BLOCKER:** [c2_confirmation.py:803](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:803>) lets an incomplete gate map proceed. `nominee_outcome({})` returns `PROCEEDS_TO_LOCKBOX`; even `{"G-2": N/A}` does. Annex A P18-7 counts an uncomputed mandatory gate as `UNAVAILABLE`, and Annex C restricts `N/A`. Require all 14 gate results and validate which gates may be `N/A` before permitting a lockbox request.

- **R14C-S-2 — BLOCKER:** [c2_confirmation.py:691](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:691>) does not enforce P18-1’s single family rerun slot against durable attempts. Two first crashes each return `rerun` when passed `slot_used_by=None`; `[PARTIAL_OUTPUT, completed]` is accepted as completed; a crash whose slot is reserved for that same trial is called `final`. Derive and reserve the slot from [attempts.py](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/core/attempts.py:277>) records, and validate the permitted attempt sequence before the look.

- **R14C-S-3 — BLOCKER:** [c2_confirmation.py:659](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:659>) checks caller supplied `w0` and `t_days` without establishing either from the bound C2 partition and manifest. A window starting on 2022-01-01 with `g=30` passes the test fixture, although DRAFT R-3 excludes the first 30 days. A claimed `t_days=365` also passes without 365 complete days. Bind `w0` to the partition start plus `g`, and compute the day count from the validated manifest.

- **R14C-S-4 — BLOCKER:** [c2_confirmation.py:739](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:739>) cannot establish P18-3’s “started and exactly one completed evaluation.” A dictionary of return lists can hide an unstarted trial or two completions under one ID; equal lengths also cannot establish the identical ordered day index required by Annex B §2.1. Accept validated attempt and dated-series evidence before constructing `X`. Hash mismatch must retain its P18-7 `U_ops` cause; the current [cause_code](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:795>) would classify that reason as `U_proc`.

- **R14C-S-5 — QUESTION:** [c2_confirmation.py:648](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:648>) accepts 21–80 trials per family, but its A-U1 check calls [screen.trial_set_sha256](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py:495>), which refuses more than 20. Thus a set accepted by `check_declaration` cannot obtain a valid screen record. The owner needs to settle the C2 count against the frozen screen’s qualified scope; enforce the same bound at both checks.

- **R14C-S-6 — BLOCKER:** The required tests do not catch several wrong outcomes. [test_c2_confirmation_cycle.py:220](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_cycle.py:220>) expects the incomplete gate map in S-1 to proceed. [test_c2_confirmation_runs.py:94](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_runs.py:94>) accepts any G-1 outcome, while its G-14 integration test covers only `PASS`. DESIGN §8 requires per-gate `PASS`, `FAIL`, and `UNAVAILABLE` cases. Add falsifying end-to-end cases for those outcomes and for the attempt and eligibility examples above.

### Validation and limits

The 49 targeted tests passed on Python 3.14.7. Ruff check and format passed; `lint-imports --no-cache` kept all seven contracts. The committed frozen paths have no diff from `809cd45`; all 14 frozen sidecars and the manifest bindings checked matched. Mypy could not open its cache database in this read-only sandbox, so type validation remains unavailable.

