<!-- Recorded verbatim from codex exec (OpenAI Codex v0.160.0) on 2026-10-10. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12668-cd8e-71a2-9068-b3f76c166d5f. Tokens used: 28,751. Made from a packet (Codex's command runner fails here): review/d19-engine/ITEM2A_REVIEW_PROMPT.md, ITEM2A_SYNTHETIC_LAWS.md, git diff fbc75f7..93bdc60 -- calibration scripts tests, the HEAD text of calibration/generator.py, seeds.py, tests/unit/test_calibration_generator.py, rundef.py lines 30-45, and the accepted preregistration §3.1-§3.2 and §13 items 1-2. -->

# Independent review: D-19 engine item 2a

**Reviewer model metadata:** OpenAI Codex, GPT-6 family as identified by this session. The exact deployed model ID and reasoning effort are not exposed to me.

**Commit reviewed:** `93bdc60828e7651c457bee8e0ec602b0d456db16` against base `fbc75f7`.

**Scope:** The supplied item note, diff, HEAD excerpts, tests, and accepted preregistration §3.1–§3.2 and §13 items 1–2. This is an **attachment-only static review**. No repository content outside the attachments was inspected.

**Commands run:** None possible. The checks reported in the item note were not independently rerun.

**Verdict: FIX for pilot use.** The item 2a skew-t, Q2m, and Q4 column constructions appear consistent with the supplied preregistration. Two pre-existing market-generator defects conflict with §3.1 and should be repaired before using the engine as an accepted §3.1–§3.2 generator. The additional validation and test findings below also need disposition.

## Findings

### I2A-1 — High — AR market innovation is not AR(1)

**Location:** `calibration/generator.py:200`, `calibration/generator.py:217`

**Failure scenario:** In an `ar0.2` or `ar0.5` Q2 cell, `ε_t` is drawn as independent Gaussian values. The AR recursion is applied only to column innovations. Section 3.1 lists AR(1) under laws of both `ε` and column innovations. Consequently the benchmark lacks the specified serial dependence while the columns have it.

**Proposed repair:** Generate market `ε` with the stated AR recursion, stationary initialization, and discarded 500-day burn-in, using the market stream. Keep the market and column streams separate. This repairs existing reviewed code; it does **not** propose a preregistration change.

### I2A-2 — High — GARCH variance is driven by shocks different from the observed market shocks

**Location:** `calibration/generator.py:187`, `calibration/generator.py:200`

**Failure scenario:** `_sigma_path` updates variance using its own t₅ draws. `generate` then draws a new, independent t₅ sequence for `ε_t` and sets `r_t = σ_t ε_t`. Thus a large observed `r_t` does not drive the next variance update. The variance path has a GARCH marginal construction, but the generated returns do not follow the stated GARCH return recursion.

**Proposed repair:** Use the same market t₅ shock for each return and its subsequent variance update, retain the 500-day burn-in, and pass that common `σ_t` to the columns. This repairs existing reviewed code; it does **not** propose a preregistration change.

### I2A-3 — Medium — IID market series omit the specified burn-in

**Location:** `calibration/generator.py:199–200`

**Failure scenario:** Constant-σ market laws, including the new skew-t laws and the Gaussian markets used for Q2m and Q4, emit the first `T` stream draws. Section 3.1 says every series discards a 500-day burn-in. For an IID law this does not change its population distribution, but it changes the deterministic realized market, benchmark, and reference vector.

**Proposed repair:** Consume and discard 500 market innovations before emitting the IID market series. Coordinate this with I2A-1 and I2A-2 and regenerate affected reference vectors through the reviewed reference-vector process. No preregistration change is proposed.

### I2A-4 — Medium — Validation admits cells outside the accepted qualifying grid

**Location:** `calibration/generator.py:79–88`; `scripts/d19_choose.py` (`AGNOSTIC_LAWS` declaration in the supplied diff)

**Failure scenario:** A manifest cell with `law="skewt+"`, `k=2`, and `dependence="equi0.5"` is accepted, although Q2 allows only independent, `ρ=0.9`, or opposites. The new law is also listed as family-agnostic. The attachments do not show whether another qualification check rejects this combination, so actual erroneous counting cannot be established from this review.

**Proposed repair:** At the qualification boundary, enforce the accepted law, dependence, `K`, and `T` combinations separately from the generator’s ability to produce exploratory cells. Add a rejection test for an out-of-grid Q2 combination. No preregistration change is proposed.

### I2A-5 — Medium — Tests do not lock down several claimed generator properties

**Location:** `tests/unit/test_calibration_generator.py:22`, `:56`, `:67`, `:77`; `calibration/rundef.py` (`REFERENCE_CASES` in the supplied excerpt)

**Failure scenario:** The skew-t bisection test solves against `skew_t_moments` itself, so it does not independently establish the frozen shape’s numerical value. The draw test checks sample mean, variance, and the *sign* of the third moment, not skewness magnitude or draw order. Q2m and Q4 tests inspect columns but not their Gaussian, constant-σ markets; the Q4 test checks lag correlation but not cross-column independence. The supplied reference-case list includes negative skew-t and Q2m, but no Q4 or positive skew-t case. A market-law or stream-order regression could escape these tests.

**Proposed repair:** Add small deterministic tests with an independently specified expected shape or moments and controlled RNG draws for the U0, U1, W order. Assert the Q2m/Q4 market law and Q4 cross-column behavior directly. Add reference cases where the start gate is intended to protect those paths. These tests should describe **population** mean and variance as exact; finite samples are not exactly centered or unit variance.

## Assessment of item 2a and its interpretations

- **Skew-t:** The supplied construction is the Azzalini scale-mixture construction. Its draw order is U0, U1, then W. The stated product moments follow from independence: `E[X^k] = E[Z^k] E[(ν/W)^(k/2)]`; `E[Z²]=1` and `E[Z³]=sqrt(2/π)δ(3−δ²)`. Subtracting the analytic mean and dividing by the analytic standard deviation gives population mean 0 and variance 1 in exact arithmetic, subject to floating-point rounding in code. The recorded positive `α_s = 0.9224371221852867` uses positive `δ` and positive skewness; negating it reverses skewness. The supplied test reports numerical agreement with ±1, but I could not independently execute that calculation. Under nonidentity `Σ`, output column marginals need not retain skewness ±1; §3.1 explicitly discloses that mixing.

- **Q2m:** For zero-based indices, columns `j < ceil(K/2)` receive standardized t₅ draws and the remainder Gaussian draws. `c_j` is 0.5 at even `j` and 2 at odd `j`. The identity dependence matrix and separate column draws implement independence. The market is Gaussian with constant `σ` because `"unequal"` falls through `_innovations` to Gaussian and `_sigma_path` to constant `σ`, subject to I2A-3.

- **Q4:** Column 0 alone receives the `φ=0.5` AR recursion; the other columns remain IID Gaussian. The recursion starts with a unit-variance Gaussian state and discards 500 days, so its column-side initialization and burn-in are sound. Its market is Gaussian with constant `σ`, subject to I2A-3.

- **Interpretations in the note:** A Gaussian, constant-σ market for Q2m/Q4 and choosing column 0 for Q4 are defensible readings of the accepted text, which specifies their column changes but does not identify another market law or the AR column’s index. The assertion that column order has no meaning for an “exchangeable family” is not established by the supplied preregistration; column 0 is defensible because it satisfies “one AR(1) column,” not because exchangeability was shown. Freezing either choice more explicitly in the accepted text would be a **proposal for the owner**, not an AI-authorized amendment. Choosing `α_s` from analytic moments rather than unstable ν=5 sample skewness is sound.

- **Manifest and references:** The new K≥2 and independent restrictions for `unequal` and `mixed_ar` match Q2m and Q4. The `AGNOSTIC_LAWS` additions match their placement in Q1–Q4, subject to I2A-4. The two new reference cases exercise negative skew-t and Q2m paths; the attachments do not show their expected vectors or the start-gate comparison, so this review cannot verify that they act as independent numerical oracles.

No calibration result or local check is claimed by this review.
