# §16 different-model review of the screen slice S4c (G-8) at 612bb55

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a14865-26ad-7220-bce9-92cf0e6b1c4f)
- Date: 2026-10-17
- Prompt: `SCREEN_S4C_REVIEW_PROMPT.md`; packet: the prompt, Annex C rev 4 C-8, frozen protocol l.250-268, `OWNER_DECISION_G8_RULE_SETTINGS.md`, `calibration/screen.py` and its test at 612bb55, local validation
- Limitation (the reviewer's own): its shell failed, so it reviewed the packet only.
- Findings: S4C-R1 (Medium), S4C-R2 (Medium), S4C-R3 (Low). PL-1/PL-2 dimension selection, ordering and neighbours hold; deferring EWMA half-life neighbours is consistent. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for the S4c G-8 screen at the supplied head `612bb55`.

| ID | Severity | Location | Finding |
|---|---|---|---|
| S4C-R1 | Medium | `calibration/screen.py`, `screen_gates` early `MODEL_PENDING` and `SIGMA_UNBOUND` returns | C-8 step 1 requires **N/A when there is no ordered numeric tunable dimension**. A model trial with an empty grid, or a vol trial using `HAR_RV` with only a categorical `sigma` grid, instead gets G-8 `MODEL_PENDING` or `SIGMA_UNBOUND`. The existing test expects that result, so it would not catch the error. Classify G-8’s dimensions before those returns. |
| S4C-R2 | Medium | `calibration/screen.py`, `leg_stats` check of `paired_sharpe_improvement is None`, used by `screen_gates` | C-8 step 2 says a **nonfinite** selected or neighbour E-IMPROV makes G-8 `UNAVAILABLE`. The code checks `None` but does not check `math.isfinite`. If the statistics call returns `NaN` or infinity, G-8 reports available. A focused test returning a nonfinite statistic would expose this. |
| S4C-R3 | Low | `calibration/screen.py`, `plateau_dimensions` inclusion of every numeric grid, then `screen_gates` | A numeric singleton such as `{"k": [5]}` is treated as an available G-8 dimension, although it has no neighbour and therefore no median `m`. Whether a singleton is “tunable” needs an explicit C-8 binding: treating it as fixed gives N/A; treating it as a boundary gives FAIL at the later gate. The current tests cover neither reading. |

**PL-1/PL-2:** The supplied code correctly excludes `tau`, categorical `sigma`, categorical strings, and booleans; includes numeric rule settings and `model.<name>`; orders values by exact `Decimal`; rejects equal numeric values; and changes one dimension per neighbour while keeping model parameter declarations consistent. Deferring EWMA half-life neighbours is consistent with the protocol’s permissive “may be treated” wording and RN-2’s current refusal of other estimators.

**PL-3/PL-4:** The screen appropriately leaves C-8’s PASS/FAIL calculation to a later stage and runs the selected BTC baseline plus each present neighbour. The exceptions above affect its availability result. Tests exercise neighbour failure, but do not exercise G-8’s selected-point failure with a numeric dimension, nonfinite statistics, singleton grids, or step-1 N/A through the early returns.

The shell could not start, so I could not verify exact line numbers or rerun pytest. This review uses the attached source and reported validation; no files were changed or committed under the read-only instruction.