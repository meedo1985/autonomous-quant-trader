<!-- Recorded verbatim from codex exec (OpenAI Codex v0.160.0) on 2026-10-10. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a1268b-94ff-72b1-9d98-0cad4ce5dba4. Tokens used: 25,328. Made from a packet (Codex's command runner fails here): review/d19-engine/ITEM2A_REREVIEW_PROMPT.md, the previous Sol review, ADJUDICATION_ITEM2A_93BDC60.md, ITEM2A_SYNTHETIC_LAWS.md, git diff 93bdc60..2ec1c81 -- calibration scripts tests, the HEAD text of calibration/generator.py and tests/unit/test_calibration_generator.py, and the accepted preregistration §3.1-§3.2. -->

# Independent re-review: D-19 engine item 2a repairs

**Reviewer model metadata:** OpenAI Codex, GPT-6 family as identified by this session. The exact deployed model ID and reasoning effort are not exposed to me.

**Commit reviewed:** `2ec1c81d8d307386f6467beee36a81905910909d`, against `93bdc60`.

**Scope:** The supplied previous review, adjudication, updated item note, diff, HEAD file text, tests, and accepted preregistration §3.1–§3.2. This is an **attachment-only static review**. No repository content outside the attachments was inspected.

**Commands run:** None possible. The checks reported in the adjudication were not independently rerun.

**Verdict: ACCEPT for pilot use.** Qualification remains subject to the item 3 manifest gate. The assertion that `rundef.run_plan` currently refuses qualification runs comes from the attached adjudication; its implementation was not supplied for independent inspection.

## Disposition of prior findings

| Finding | Re-review |
|---|---|
| I2A-1 | Closed. Market AR laws now apply the recursion to `ε`, start with a unit-variance Gaussian draw, and discard 500 days. |
| I2A-2 | Closed. Each GARCH t₅ shock drives both `r_t = σ_t ε_t` and the next variance update. The emitted variance recursion matches the preregistration. |
| I2A-3 | Closed. Every market law now draws or evolves through the 500-day burn-in before emitting observations. |
| I2A-4 | Safe to carry to item 3 **given the stated qualification refusal**. Generator validation remains broader than the qualifying grid; the grid check and rejection test remain required at the qualification boundary. |
| I2A-5 | Closed for this pilot. The added controlled-draw test checks U0, U1, W order; density quadrature independently checks the frozen positive shape’s skewness; market-law and Q4 cross-column checks cover the identified gaps. The added Q4 reference case covers that path. |

`generate` uses the returned market `σ_t` for the benchmark return and for every column’s scale. Market and column draws remain on their respective supplied streams; the code shown introduces no shared random draw or nondeterministic operation.

The quadrature computes the first three moments from skew-normal and χ² densities, independently of `skew_t_moments`. Its integration ranges and resolution are adequate for the stated `2e-4` skewness tolerance. It checks distributional skewness, while the controlled-draw test checks the implementation’s draw order.

The new GARCH, AR-market, and IID burn-in tests would fail against the previous code because `market` did not exist; against an equivalent old interface, the GARCH recursion, AR correlation, and burn-in assertions target the prior defects. The Q2m/Q4 market, draw-order, and quadrature tests check properties already present before these repairs and are not expected to fail on the previous implementation. The AR test is statistical rather than an exact seeded check of its initial state or burn-in; those properties are established here by code inspection.

## Findings

No findings.

No calibration result or independently executed validation is claimed by this review.
