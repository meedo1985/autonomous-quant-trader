# §16 different-model review of the screen slice S6b at b00d59b

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a1488e-0fc9-7c90-92d1-1ff060d330b9)
- Date: 2026-10-17
- Prompt: `SCREEN_S6B_REVIEW_PROMPT.md`
- Findings: S6B-R1 (High), S6B-R2 (Medium, owner binding), S6B-R3 (Low). MR-2, MR-3 hold for the emissions produced. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for the attached `b00d59b` S6b snapshot.

Findings below use line numbers relative to the `# --- S6b` header in [calibration/screen.py](</D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py>). The repository shell failed to start, so I could not verify absolute line numbers, HEAD, or rerun pytest.

- **S6B-R1 — High — `calibration/screen.py:S6b+49–55, +80–91`.** `instants` includes only decisions with a realised label, and the same list drives emissions. WF-6 requires an emission at *every* 00:00 window decision, including those whose labels are not yet realised. In a 30-day window with `H=72h`, the last emission is at `w1−72h` and is held for one day; the final two days retain `NaN`. `leg_targets` then marks otherwise valid G-3/G-5/G-6/G-7 runs `INVALID_SERIES`. At `H=168h`, six days lack emissions. Use realised-label rows for training, but enumerate window decisions separately for inference.

- **S6B-R2 — Medium, owner binding required — `calibration/screen.py:S6b+4–8, +54–72`; `screen_gates`’s `run(s)` call.** G-3 fits a fresh model on ETH rows. “BTC and ETH evaluated jointly inside the same trial” establishes trial accounting; it does not decide whether ETH gets its own fit or receives predictions from the BTC-fitted model. WF-1 explicitly defines BTC rows, while its C-12 reference leaves the ETH application open to interpretation. This is **MR-1’s proposed reading for the owner to decide**, not a reviewer-authorized switch to BTC-fitted predictions. A logistic trial with two BTC classes but one ETH class, for example, is `MODEL_FIT_ERROR` under separate fitting and may be available under BTC-to-ETH application.

- **S6B-R3 — Low — `calibration/screen.py:S6b+24–27`.** MR-4 returns the 24-month span plus `REQUIRED_HISTORY_BARS`; WF-2 specifies that span plus **4,800 + 1** hours. At a `w0` whose preceding 24 months span 731 days, the minimum declaration can be accepted one hour below the READY threshold. Align the declaration check with the stated bound, or obtain a design correction if the extra hour is unnecessary.

**Other readings:** MR-3’s feature-column indexing, one-hour G-6 re-inference, unlagged training rows and labels, and G-5/G-7 emission reuse are consistent for the emissions it actually produces. Non-finite model features and fit failures become unavailability. MR-2’s fixed seed `0` is a defensible reading of WF-5’s fixed settings, but the same-seed reproducibility test does not prove seed independence. The configured cyclic linear solvers and `lbfgs` avoid their random selection paths, and LightGBM documents its deterministic and forced column-wise settings. [scikit-learn linear models](https://scikit-learn.org/stable/modules/linear_model.html), [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html), [LightGBM parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html).

The S6b tests cover only `H=24h` and a 30-day window, so they miss S6B-R1 and do not exercise a second refit. Their G-6 assertion checks that predictions differ, not the exact one-hour input row. The supplied “138 passed” result is reported local validation, not a result I could independently reproduce. No files were changed; this feedback has not been committed as the project’s required review record.