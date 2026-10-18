# Different-model review of the screen S6 design at 5892a4a (before code)

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a1486e-5c42-7c20-bd10-6f067941303d)
- Date: 2026-10-17
- Prompt: `SCREEN_S6_DESIGN_REVIEW_PROMPT.md`; packet: the prompt, `SCREEN_S6_DESIGN.md`, owner decisions S3R-R3 and WF-4, frozen protocol l.100-275, Annex C rev 4 C-7, C-10 (1), C-12, DRAFT R-3/R-9 and gap_embargo, `calibration/gap.py`
- Limitation (the reviewer's own): local reads failed; it reviewed the packet only.
- Findings: S6D-R1..R5 (High), S6D-R6..R8 (Medium). Verdict: NOT READY.
- The reviewer's final output follows verbatim.

---

## Verdict: NOT READY

The design has the right broad pipeline, and both attached owner decisions are settled: G-14 applies to logistic sign models, and the sizing-estimator ban applies to model inputs. The blockers are the walk-forward embargo, the refit anchor and training history, unrestricted model parameters, and parts of the G-14 statistic. These need to be fixed before S6a is built from this design.

| Reading | Assessment | Material alternative or missing binding |
|---|---|---|
| **WF-1** | The daily BTC row and vol-scaled target are broadly faithful. The 23:00 bar close and 00:00 decision need one explicit timestamp convention. | A zero sign label causing whole-gate `UNAVAILABLE` is an added eligibility rule. Specify the binary class mapping and how zero is handled. For G-14, logistic IC must still use the **continuous vol-scaled target**, with a specified positive-class prediction score. |
| **WF-2** | The 30-day step and refit cadence match the protocol. The first-refit anchor is underspecified. | **24 months is not always 730 days.** Specify calendar-window boundaries, the first eligible refit, and which partition supplies its prior training data. The blanket warm-up and `INSUFFICIENT_WARMUP` rule do not follow as written. |
| **WF-3** | Purging labels that reach the refit boundary is directionally right. | Substituting the cycle-wide `g` for the validation embargo is materially different and is not supported by the supplied draft, which expressly leaves `validation.embargo` governing folds. Define the embargo cutoff’s data and its boundary inclusivity; calculate it from original labels before null shifts. |
| **WF-4** | Reading (a) is now the recorded **owner decision**. | Apply the same identity check to declared model features and `s_inputs`; update the design’s stale “OWNER” and section 5 wording. |
| **WF-5** | The six class names and fixed LightGBM settings generally track the sources. | “Every documented hyperparameter except …” is too broad. Freeze an allowlist and valid ranges, including aliases and LightGBM values that disable depth limits. Specify the logistic prediction score. |
| **WF-6** | Faithful if emissions are recomputed at their own times and G-6 changes the inputs used for inference. | Pin bar-close and emission timestamps. At a 00:00 decision, a one-hour feature delay must actually select the last input available by 23:00, while refits and labels stay undelayed. |
| **WF-7** | The per-draw, per-window shift and seed approach follows C-12 in outline. | The empty-range test is off by one. Define the OOS IC population and aggregation, the continuous target used for logistic IC, and the complete label-dependent refit pipeline. |
| **WF-8** | The selected vectors and full-grid hash match C-12’s requested shape. | Specify canonical hash bytes and the fixed `n_w` vector. C-12 also requires byte-identical outputs across the rebuilt and current images before the run definition is recorded. “Every CPython” is broader than that requirement. |

### Findings

- **S6D-R1 — High — WF-3 changes the frozen embargo.** Suppose a training window’s target ACF cutoff is 12 days while exploration-derived `g` is 7. Reading (b) admits five days of rows that `validation.embargo` would exclude. The draft explicitly says the v1 embargo still governs folds. An owner preference alone cannot replace that frozen rule; resolve its calculation under the frozen text or use the applicable amendment process.

- **S6D-R2 — High — WF-2 lacks a valid first-window boundary.** A first refit at the start of a 1,247-day eligible path requires two years of earlier training data. If those data are unavailable or include excluded gap days, the schedule cannot run as claimed. If training starts inside the path, the number of OOS refits and evaluated rows changes. Specify the data boundary and anchor before coding; use calendar 24-month windows unless the governing text is changed.

- **S6D-R3 — High — WF-5 permits models outside the intended bounds.** For example, LightGBM `max_depth=-1` satisfies a simple `<= 3` check while removing the depth limit; constructor aliases or other documented parameters can also change the fitted model. Use a finite declaration allowlist with explicit valid ranges and reject aliases that evade it.

- **S6D-R4 — High — WF-7 rejects a valid shift range.** For horizon `h=7` and `n_w=14`, C-12 permits the single offset 7: its inclusive range is `[7,7]`. `NO_SHIFT_RANGE` starts at **`n_w < 2h`**, not `n_w < 2h + 1`.

- **S6D-R5 — High — the IC estimand is not executable unambiguously.** A seven-day target near the end of a 30-day OOS interval may realize in the next interval. Including it, excluding it, averaging interval ICs, and computing one pooled IC can yield different 476-of-500 outcomes. State the exact interval endpoints and whether each draw produces one pooled IC. For logistic trials, rank the specified positive-class score against the original continuous target, not the fitted sign label.

- **S6D-R6 — Medium — WF-1 adds an unapproved zero-label refusal.** One unchanged-price target in a logistic training window would make the entire trial unavailable under `LABEL_ZERO`, although C-12 lists no such rule. Bind the binary sign objective and zero treatment before implementation; do not silently drop a row, since that changes `n_w` and its offset range.

- **S6D-R7 — Medium — purge and embargo boundaries can be implemented two ways.** A row whose label realizes exactly at refit time is retained under `end <= refit` but rejected under “ends before”; applying a horizon purge and then a full embargo after that can remove more rows than an embargo measured from the refit decision. State both comparisons and anchors in a boundary example.

- **S6D-R8 — Medium — the cost estimate is conditional, not a feasibility result.** The arithmetic is right **if** there are about 41 refits per path: `501 × 41 ≈ 20,500` fits, then about 615,000 over 30 paths. If the first refit instead follows 730 days within a 1,247-day path, there are about 18 refits and roughly 270,500 fits over 30 paths. The pilot can measure feasibility; the design cannot yet conclude that a 20-trial LightGBM set is forbidden.

**Decision boundary:** WF-4 and logistic G-14 applicability are already owner-decided. The refit anchor, timestamp convention, purge comparisons, parameter allowlist, and reference-vector encoding are drafting choices that must be fixed before review of code. A new zero-label eligibility rule or logistic score convention needs an explicit preregistered binding. Replacing the frozen validation embargo with `g` requires more than a drafting choice or an informal owner answer.

This review is based on the supplied source excerpts. Local file reads failed, so I could not verify the full DRAFT rev 9 §2.5 or C-10 (3), invoke the repository review skills, or record and commit this read-only review. No code or tests were run.