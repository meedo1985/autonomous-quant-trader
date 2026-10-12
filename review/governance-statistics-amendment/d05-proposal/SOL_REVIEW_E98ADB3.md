# Sol High review of the D-05 proposal rev1 at `e98adb3` — SOUND WITH FIXES

Date: 2026-10-03. The OpenAI-family review for R19-2. It ran in parallel with the Fable review and without sight of it.

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < <prompt>`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a1021f-ac79-7ed0-99b4-4921ce04e5ea`;
  tokens used 56,809; exit 0. (The reviewer's self-report names only "GPT-5 family"; the CLI
  header is the observed model metadata.)
- Prompt: `REVIEW_PROMPT_R1.md` (committed `e98adb3`) with `{{PREFIX}}` = `SP1`
  (substituted file SHA-256 `8b110d2c3aa9750bcf3d6895c4d4418360d6f4ca2d3b6387f7bf794d8f5d0def`).
- The reviewer's final message, verbatim:

---

**Model:** OpenAI Codex, GPT-5 family; exact serving-model identifier is not exposed.  
**Commit reviewed:** `e98adb35e62d9927114e36691b5e0cf0db737ed6`  
**Verdict:** **SOUND WITH FIXES**

The central recommendation—treating an available `v <= 0` as substantive `FAIL`—is defensible. The proposal is not ready for the owner because its availability rules, `U_proc` claims, and supporting probability claims need correction.

| ID | Severity | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| SP1-1 | BLOCKER | §2 option (b); §3.3; §5 | Option (b) is described as “UNAVAILABLE (or N/A)” and then treated uniformly as contributing to `U_proc`. | P18-7 expressly counts `UNAVAILABLE` and technically invalid gates but excepts frozen `N/A`. Therefore `UNAVAILABLE` affects `U_proc`; `N/A` waives the gate and does not. The claim that non-positive `E-IMPROV` is “close to half” under the global null is also unsupported: that null constrains `E-DIFF`, not `E-IMPROV`. | Split option (b) into `(b1) UNAVAILABLE` and `(b2) N/A`. Explain that `(b2)` changes gate applicability. Remove the “close to half” and “unreachable” claims unless D-19 later establishes them for every qualifying cell. |
| SP1-2 | BLOCKER | §3 proposed wording; §4 C-4 | The wording says every case not satisfying the pass conjunction is `FAIL`, including an unavailable selected value or unavailable median. | [`statistics.py:218–233`](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/metrics/statistics.py:218) permits `E-IMPROV` to be unavailable. P18-7 classifies technically invalid or uncomputed mandatory gates as `UNAVAILABLE`. The wording also contradicts C-4, which says no available neighbour produces `UNAVAILABLE`. | Bind precedence explicitly: no ordered numeric dimension → frozen `N/A`; otherwise unavailable `v` or required neighbour statistic → the chosen availability outcome; otherwise `v <= 0` → `FAIL`; otherwise evaluate threshold and boundary. Do not let an earlier substantive failure hide technical unavailability. |
| SP1-3 | BLOCKER | §3.2 and §3.4; §4 | “G-8 almost always fails exactly where G-1 already fails” is unverified, while point 4 strengthens it to “the gate cannot pass G-1 anyway.” | The implementation stores the observed point separately at line 617 and computes the lower endpoint solely from bootstrap replicates at lines 646–650. For 2,000 valid replicates, the type-7 5% endpoint interpolates at position `99.95`; no code invariant requires it to be ≤ the observed point. Selection on `E-DIFF` further weakens ordinary centring intuition. The proposal itself concedes a positive lower endpoint with `v <= 0` is possible. | Replace “almost always” with an explicitly unverified hypothesis and delete “cannot pass.” State the real consequence: when G-1 does pass despite `v <= 0`, option (a) newly blocks promotion and P18-5 permits no fallback. |
| SP1-4 | BLOCKER | §4 C-4 | A neighbour with unavailable/nonfinite `E-IMPROV` is silently omitted, while the remaining neighbours determine the median. | Frozen lines 260–264 say “available ±1-step neighbors” but do not clearly establish that a geometrically present neighbour with an invalid statistic may be discarded. P18-7 instead says a technically invalid mandatory gate is `UNAVAILABLE`. These readings produce different medians and different `U_proc` rates. | Define “available neighbour” operationally: geometric presence, successful evaluation, finite `E-IMPROV`, or some combination. Specify whether one invalid neighbour invalidates G-8, whether valid neighbours may remain, and whether a minimum count is required. Treat this as a proposed binding, not an already frozen fact. |
| SP1-5 | BLOCKER | §4 C-2 | Exact `v = 0` is dismissed as having near-zero probability for continuous returns. | Structural equality can create exact zero regardless of continuous returns. The earlier proposal itself gives the positive scaling case `candidate = 1.5 × benchmark`, for which Sharpe is scale-invariant and `E-IMPROV = 0` (`d02-d04-proposal/PROPOSAL.md:77–80`). Duplicate/equivalent strategies can do likewise. | Remove the probability claim. Treat `v = 0` as a live boundary requiring an intentional rule. |
| SP1-6 | NON-BLOCKING | §1; §5 | The text says “neighbours must be better” and says the check “turns upside down” for zero or negative values. | For `v < 0`, only the **median** must exceed `v`; not every neighbour must. At `v = 0`, the rule is `m >= 0`, so there is no strict algebraic inversion, although the relative-retention interpretation degenerates. | Say: for `v=0`, the median must be nonnegative; for `v<0`, the median must be strictly better than the selected point by at least `0.5|v|`. |
| SP1-7 | NON-BLOCKING | §2(a); §5 owner question | “No isolated peak exists,” “invent a new rule,” and “very hard to meet” are not neutral descriptions. | A negative selected value can still be a local peak relative to more-negative neighbours. The effect on the 1% target depends on the qualifying-cell distribution and whether the outcome is `UNAVAILABLE` or `N/A`. | Use “no positive improvement exists,” “adopt a separately justified sign-aware rule,” and describe `U_proc` effects conditionally. Add the selected/neighbor availability decision to the owner question or resolve it first. |

The frozen formula works as intended for positive values, degenerates at zero, and reverses its direction below zero.  
Failing an available non-positive selected value is a defensible policy, but the proposal is not ready for decision.  
`UNAVAILABLE` and `N/A` are different outcomes and must not remain one option.  
Neither the “almost always fails G-1” claim nor the “half under the null” claim is established.  
Define availability precedence and neighbour handling, remove the zero-probability claim, and present the owner with neutral tradeoffs.