# §16 different-model review of the screen slice S4a (feature columns) at ebf0c8a

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a1484b-5212-7c43-82c2-208dd122962f)
- Date: 2026-10-17
- Prompt: `SCREEN_S4A_REVIEW_PROMPT.md`; packet: the prompt, FEATURE_FACTORY_v1, `src/aqt/features/columns.py` and its test at ebf0c8a, the frozen `factory.py`, the costs EWMA series, CPython 3.14 `statistics` internals, local validation
- Limitation (the reviewer's own): its shell failed, so it reviewed the packet only.
- Findings: S4A-R1 (Major), S4A-R2 (Medium). The arithmetic (EMA, windows, first index, EWMA index, exact variance and fsum) matches; private helpers acceptable on the pinned runtime. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for S4a at the supplied head `ebf0c8a`. I could review the attached code, but the repository shell failed before running, so I could not independently verify the head or rerun pytest.

- **S4A-R1 — Major — `src/aqt/features/columns.py:151`.** The blanket finite-value check rejects a row the frozen factory returns. A valid 4,800-bar series can have every close at the smallest positive subnormal, with one bar’s high at the largest finite float. The factory computes a finite ATR and returns `atr_24 = inf` after dividing by that tiny close; `feature_columns` raises `FeatureFactoryError`. That breaks the stated equality contract. Add this edge case and match the factory’s behavior.

- **S4A-R2 — Medium — `src/aqt/features/columns.py:82`.** The factory explicitly rejects a series whose interval is not one hour; `feature_columns` has no corresponding check. A contiguous non-hourly `BarSeries` with at least 4,800 bars would therefore reach column calculation if `require_contiguous()` accepts its declared interval. Add the factory’s interval check and a refusal test.

The EMA seed and recursion, rolling-window bounds, first decision index, and EWMA series index match the attached factory code. The integer variance formula matches `statistics.stdev`’s exact rational calculation; the positive `math.fsum` inputs are represented exactly before rounding. Use of the private square-root helper and factory constants is acceptable for the stated pinned CPython 3.14 runtime, but needs reassessment if that runtime changes.

The two random-series tests exercise ordinary values and sampled rollovers. They do not cover the extreme ATR case or non-hourly refusal.