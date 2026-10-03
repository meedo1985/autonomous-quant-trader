# Sol High review of the N-1/N-2 proposal rev1 at `f8da1b0` — SOUND WITH FIXES

Date: 2026-10-03. The OpenAI-family review for R19-2. It ran in parallel with the Fable review and without sight of it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a10256-134d-7dc2-af28-914b5b103e70`;
  tokens used 78,942; exit 0. (The reviewer's self-report names only "GPT-5 family"; the CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R1.md` (committed `f8da1b0`) with `{{PREFIX}}` = `SQ1`
  (substituted file SHA-256 `a7dfb2746a6a6b0cf01a31f440ba98ba712afe5dcc97209f1ad59eb942ddf941`).
- The reviewer's final message, verbatim:

---

Model: Codex, OpenAI GPT-5 family; exact serving model ID is not exposed  
Commit reviewed: `f8da1b04b0ed070d1f485d240e1dc4852b5ef565`  
Verdict: **SOUND WITH FIXES**

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| SQ1-1 | NON-BLOCKING | §1, N1 fallback and availability | A caller supplies nonfinite returns, invalid timestamps, or a positive but undeclared horizon such as 48 hours. | The formula, Bartlett weights, clamp, constant-series fallback, and nonpositive-`Ω` fallback match `IMPLEMENTATION_CONVENTIONS.md` and `effective_sample_size`. However, `_series` raises on malformed/nonfinite input; timestamp checks occur before this function; and `effective_sample_size` accepts any positive integer horizon. It also treats computed `γ0 == 0` from a nonconstant series as `NONFINITE_RESULT`, not fallback. | State that the governed consumer validates complete UTC days and `H ∈ {24,72,168}`, converts validation exceptions to `UNAVAILABLE`, and preserves the nonconstant-`γ0 == 0` unavailable branch. |
| SQ1-2 | BLOCKER | §1 “Consequences”; §4 owner question 1 | The owner is told that the 120 gate will “almost always” pass and could fail under strong autocorrelation in C2. | At `n=1219`, `floor(4·(n/100)^(2/9)) = 6`; all three horizons therefore give `L=6`. Since `\|γk\| ≤ γ0` and the six Bartlett weights sum to 3, positive `Ω/γ0 ≤ 7`, so every valid Newey–West result has `ESS ≥ 1219/7 = 174.142857`. The smallest fallback, for 168 hours, is also `1219/7`. Thus a complete valid C2 series cannot **FAIL** 120; it can only pass or be unavailable. | Replace the heuristic with the algebraic result. Tell the owner that the 120 gate is non-discriminating at full C2 length, while the same binding materially controls the separate CPCV switch at 250. |
| SQ1-3 | BLOCKER | §2 option table | Option (a) is presented as the correct reading and recommended, while (b) is characterized mainly as cheap. | Lines 141–145 identify a shuffled-label metric and line 289 is unqualified, so applying 0.95 to both nulls is defensible. It is not compelled: the frozen backtester specification separately calls the shuffled-label result an acceptance canary. The `N/A` exception is new amendment policy; line 249 is only an analogy concerning a different metric. The strict 475-of-500 count is internally consistent with D-14, but is an adopted empirical-percentile convention, not uniquely determined by 0.95. | Describe (a) as one amendment interpretation, not “as written.” Present (b), applicability-specific alternatives, and `REVISE/KEEP_BLOCKED` neutrally, with consequences for `U_proc`. |
| SQ1-4 | BLOCKER | §2 “Proposal N2, details” | Two implementations can follow the prose and produce different null distributions. | The proposal does not bind how draw and walk-forward-window indices derive permutations; whether each fold refits the entire label-dependent pipeline; whether preprocessing, calibration, early stopping, or feature selection are rerun; the exact eligible/aligned OOS rows; duplicate-prediction handling; or the requirement that every target realization remain inside the eligible window. Ordinary permutation also destroys the serial dependence of overlapping 72/168-hour labels, so it must not acquire an unstated permutation-test interpretation. | Specify the complete fitted pipeline, observation identity and alignment, per-draw/per-window seed derivation under D-20, and unavailable-reason precedence. Explicitly state that the simple shuffle is a diagnostic filter with no exchangeability or error-rate guarantee—or choose and justify a dependence-preserving shuffle. |
| SQ1-5 | BLOCKER | §3, D-19 problem | D-19 uses only return-level simulated state and substitutes a deterministic availability argument for actually running a gate. | The problem is real: G-3 needs ETH state, G-6/G-7 need stressed reruns, G-11 needs exposure/backtester state, and G-14 needs fitted-model/label state. But P18-7 says every mandatory pre-lockbox gate is computed for every simulated nominee and that an uncomputed gate is `UNAVAILABLE`. Its target is a joint upper bound on `P(U_proc)`, not necessarily proof that unavailability is impossible. | Require a per-gate input/availability matrix and computation in every replication. If analytic shortcuts are desired, authorize them explicitly by amendment and define how they establish the joint 1% bound; do not treat a deterministic assertion as computation under current P18-7 wording. |
| SQ1-6 | BLOCKER | §4 owner questions | The owner approves the questions as written. | Question 1 omits that N-1 also binds the CPCV threshold and makes the inaccurate “almost always” claim. Question 2 says “prediction model,” whereas option (a) applies only to a model trained to predict the vol-scaled target; a volatility-forecasting model is still a prediction model but would be `N/A`. It also omits the unbound shuffle mechanics, dependence limitation, D-20 dependency, computation cost, and an explicit revise/keep-blocked choice. | Rewrite both questions after SQ1-1 through SQ1-5. Ask separately about the ESS convention, its two consumers, shuffled-label gate status, exact applicability rule, and the completed algorithm. |

### Owner summary

1. The N-1 formula matches the inactive implementation, subject to making its validation boundary explicit.
2. With all 1,219 C2 days, the 120 threshold cannot fail mathematically; the proposal’s “almost always” wording is misleading.
3. Making shuffled labels a promotion gate is defensible, but the frozen wording does not uniquely require that choice.
4. The shuffle procedure and its applicability rule are not yet precise enough for reproducible implementation or owner approval.
5. The D-19 obstacle is real, but P18-7 requires actual per-gate computation unless an amendment expressly permits another proof.