# §16 different-model review of the screen slice S4b at 3fe87a4

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a14854-53e2-77b3-abbe-5bdbf574008b)
- Date: 2026-10-17
- Prompt: `SCREEN_S4B_REVIEW_PROMPT.md`; packet: the prompt, prereg §7.2, Annex C rev 4 C-0, C-3, C-5, C-7, C-10 (1)-(2), frozen protocol exposure lines, `calibration/screen.py` and its test at 3fe87a4, the accepted `event_contract.py`, the R-8 metric code, `vol_target_exposure`
- Limitation (the reviewer's own): its shell failed, so it reviewed the packet only.
- Findings: S4B-R1 (High), S4B-R2 (High), S4B-R3 (Medium), S4B-R4 (Medium). RN-2, indexing, benchmark, daily returns, E-IMPROV, drawdown and G-3 carry-over hold. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for S4b at `3fe87a4`. The attached code shows four contract gaps. Line numbers could not be verified because the local command runner failed before starting a process; the function and statement anchors below identify each location. I could not rerun pytest, so the reported 101 passing tests remain unverified here.

| ID | Severity | Location | Concrete failure scenario |
|---|---|---|---|
| S4B-R1 | High | `calibration/screen.py:screen_gates`, where `signal` and `overlay` are loaded once; `leg_targets`, where only the passed state dict is reset | Trial code can use an allowed module global to cache all BTC rows during G-5. G-6 then starts with that cache intact and can read future rows despite receiving only one row per call. RN-3’s call form is faithful to C-10 (1), but it does **not** make look-ahead impossible across runs. Load fresh trial code for each run or otherwise isolate all code state. |
| S4B-R2 | High | `calibration/screen.py:leg_targets`, after `s = float(signal(...))` | A signal returns a negative value on some hours and a positive value on others. The negative values are clipped to zero, and the run may remain available. C-10 (1) requires `s_h ≥ 0`; reject a negative `s` before clipping. |
| S4B-R3 | Medium | `calibration/screen.py:leg_targets` and `screen_gates`; `class_mismatch` is never called | A declared `constant_signal` returns alternating values. The runs proceed without `CLASS_MISMATCH`. C-10 (2) requires checking `s` every hour. The current target list also discards the `s` series that the later G-11 check needs. |
| S4B-R4 | Medium | `calibration/screen.py:leg_targets`, when building the lagged signal row and overlay market | In G-6, a declared feature value is non-finite, but the signal ignores it and returns a finite value. The run can remain available. C-7 explicitly makes a non-finite lagged input `UNAVAILABLE`; validate inputs before calling trial code. |

**Readings that hold:** RN-2 correctly refuses estimators without a bound hourly definition; inventing one would change the registered trial. The `j−1` and G-6 `j−2` indexing, unlagged benchmark, `w0` decision start, and extra final open match the attached event contract. The 00:00 equity marks, R-8 E-IMPROV call, hourly drawdown calculation, and final-equity net return also match the stated readings. An unavailable G-3 keeps G-5 through G-7 unavailable when their own runs succeed; a gate that merely **fails** is not incorrectly marked unavailable. `screen_gates` returns availability reasons only, so it does not yet expose PASS/FAIL outcomes for the later screen driver.

The supplied tests cover a signal’s row shift and several unavailable runs, but do not exercise cross-run module globals, negative `s`, `CLASS_MISMATCH`, non-finite lagged inputs, or an unavailable G-3 with otherwise available BTC runs. The review remains read-only; no record was written or committed.