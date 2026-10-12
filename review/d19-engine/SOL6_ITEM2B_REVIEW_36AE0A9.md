<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-10. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a126ca-71ae-79f0-babf-c410410d6fcc. Tokens used: 37,024. Made from a packet (Codex's command runner fails here): review/d19-engine/ITEM2B_REVIEW_PROMPT.md, git diff 5664f0c..36ae0a9 -- calibration tests, the HEAD text of calibration/semi.py, calibration/generator.py, tests/unit/test_calibration_semi.py, ITEM2B_RULE_LIBRARY_PROPOSAL.md, the accepted preregistration §3.1-§3.6, §8 and §13, protocols/protocol_v1.yaml partitions, exposure_mapping and trial_accounting, and the klines window constants and verify_partition_manifest. -->

# Independent review: D-19 engine item 2b

**Reviewer model metadata:** OpenAI Codex, GPT-6 based, as identified in this session. The exact runtime model ID and effort setting are not exposed to me.  
**Commit reviewed:** `36ae0a9` on `d19-calibration-engine`, parent `5664f0c`.  
**Scope:** The supplied diff and HEAD excerpts of `calibration/semi.py`, `calibration/generator.py`, and `tests/unit/test_calibration_semi.py`; `ITEM2B_RULE_LIBRARY_PROPOSAL.md`; and the supplied preregistration, protocol, and manifest-verifier excerpts. **This review uses the attachments only.**  
**Commands run:** None. The command runner was unavailable. The checks reported in the proposal were not independently run or verified.

**Part A verdict: FIX before pilot use.** The bootstrap, sign process, warm-up slicing, column algebra, and benchmark refactor agree with the supplied preregistration on inspection. The claimed boundary on *reading* non-exploration bars and the reported left-out count need repair or a narrower, enforced contract.

**Part B recommendation: SOUND WITH FIXES as advice to the owner.** Defining the libraries is necessary. R-1, R-2, R-3, and R-6 have a plausible shape within the accepted 3 × 3 × 3 budgets, targets, estimator list, and trial unit. R-4 changes what a cell certifies, and R-5 leaves a material gap against the frozen exposure mapping. The owner should resolve those points before the libraries become generator code.

## Findings

### I2B-1 — High — `calibration/semi.py:64–78`: the pre-load check does not guarantee that no other partition bar is read

**Scenario:** Both manifest objects say `exploration` and declare windows within the exploration bounds, but `load(manifest)` opens an artifact containing a confirmation or lockbox bar. The loader can read that bar before `verify_partition_manifest(..., series=series)` runs. The supplied verifier excerpt establishes a post-load hash check, not a pre-read data boundary. A reversed or empty window also passes the shown bound comparisons and reaches `load`.

**Repair:** Require a trusted loader that enforces the authorized partition and time range *while reading*, and reject empty or reversed windows before calling it. Test the read boundary with an instrumented loader. Keep the parsed-hash verification after loading. The current code does precheck **both manifest labels, symbols, and outer bounds before either load**; the stronger docstring claim about every bar read is unsupported.

### I2B-2 — Medium — `calibration/semi.py:79–89`; proposal R-1: the left-out count can omit boundary days

**Scenario:** A manifest covers days 0–5, day 0 is incomplete, and days 1–5 are complete for both symbols. Day 1 has no usable predecessor, but `days` begins at day 1; `span - len(rows)` reports zero left-out days. The same problem applies at the trailing edge. The test covers an interior gap only.

**Repair:** Define the count’s denominator from the common authorized calendar window, with explicit treatment of its first return day, and count every excluded eligible date against it. Add leading, trailing, and unequal-window cases. Record excluded dates or their gap boundaries: the current compacted return array also makes rows on opposite sides of a missing day adjacent to the stationary bootstrap.

### I2B-3 — High — proposal R-4, §3.6: random subsets certify a mixture, not a fixed declared design

**Scenario:** A Q5 cell draws a fresh K-subset of 27 rules per replication and passes its error bound on average. One particular 20-rule design has a much higher error rate, but appears rarely enough for the mixture to pass. A C2 family declares that fixed design. Matching its exploration diagnostics to the mixture cell’s order statistics does not establish the cell’s error bound for that design, or the §3.6 “same law” acceptance statement.

**Repair — proposal for the owner:** State and limit the certified claim to the rule-subset mixture, or preregister fixed or stratified designs and require the applicable bound for each design class a declaration may match. Revise §3.6 mapping and its matching-law language if mixture cells remain. This changes the interpretation of the accepted preregistration and needs the owner’s recorded decision.

### I2B-4 — High — proposal R-5, R-2, R-3: exposure paths omit frozen mapping controls

**Scenario:** The proposed rules resize daily without the protocol’s absolute 0.10 rebalance band or its 24-hour minimum holding period for risk increases. A declared trial using those controls can have different zero-day shares, serial dependence, correlations, and turnover-related return behavior from the proposed Q5/QJ columns. Disclosing the omission does not make the paths representative of that declared rule.

**Repair — proposal for the owner:** Apply the frozen controls when these libraries are intended to represent declarable C2 exposures. If Q5/QJ are deliberately simplified challenge laws, define that narrower role and remove any claim that diagnostic matching alone makes them equivalent to a declared C2 design. A change to the frozen mapping itself requires its formal amendment process.

### I2B-5 — Medium — proposal R-3: HAR and GARCH rules are not yet reproducible definitions

**Scenario:** Two implementations both use HAR windows of 1, 5, and 22 days and GARCH α = 0.10, β = 0.85, yet choose different HAR weights, GARCH intercepts and initial variance, or methods for converting an H-day forecast to `σ̂ₜ,ₕ`. They produce different exposures for the same seed and path. “Frozen parameters” does not determine these values.

**Repair:** Before the owner accepts R-3 or a qualification object binds the generator, specify the complete equations, constants, initialization, horizon aggregation, timing relative to day *t*, and numerical handling. Set them without fitting on a replication or using its future returns. This is an owner decision on the proposed library, not an authorization to edit frozen text.

### I2B-6 — Medium — proposal R-2 and R-3: lock the observation and decision timing

**Scenario:** “Price above its L-day SMA” is implemented using day *t*’s close to set day *t*’s exposure, or an H-day rule is re-read using returns from within its holding interval. Either implementation follows an informal reading of the proposal but looks ahead. The 250-day warm-up and day-0 refresh do not themselves specify which close is available.

**Repair:** Define the synthetic price construction from the resampled simple returns, state that exposure on day *t* uses observations through *t−1*, and specify the refresh days and held signal for every H. Apply the same timing to each variance forecast. Once implemented, test prefix invariance: changing path rows after *t−1* must not change exposure at *t*.

### I2B-7 — Medium — proposal R-3, R-4: exact-duplicate EWMA horizons affect both coverage and accounting

**Scenario:** For each target, the three proposed EWMA horizon trials have identical exposure paths. A sampled K-subset can contain several exact duplicates, reducing its effective variety and placing correlation at 1. Treating them as one trial would conflict with the frozen `(hypothesis_id, parameter_point, horizon)` trial unit; treating them as distinct without identifying the duplication can make the random-subset mixture unlike a fixed declared family.

**Repair:** Keep all three trial identities in K and lifetime accounting if the horizons remain, explicitly record duplicate columns and their frequency in each cell, and check that correlation diagnostics and threshold construction handle correlation 1. The owner should decide whether to retain the duplicates or choose the stated alternative estimators before freezing the library.

### I2B-8 — Medium — `calibration/semi.py:92–143`; `tests/unit/test_calibration_semi.py:105–168`: the tests establish less than the comments claim

**Scenario:** The sign test counts changes, which cannot distinguish a block boundary followed by the same sign from no boundary. The replication test reconstructs results with the same bootstrap, sign, and benchmark helpers. Neither establishes independence of the `"market"` and `"sign"` streams, causal exposures, or QJ sharing: QJ assembly is not present in the attached code. There is also no direct regression test comparing the benchmark refactor with its prior loop.

**Repair:** Add independent fixed-seed reference vectors for index and sign draw order, a direct old-loop benchmark equivalence test, and integration tests when the libraries and QJ assembly exist. Verify separate stream derivation under §8 and one shared path/sign sequence across both QJ families. Describe the present tests as checks of algebra and selected distributional properties.

## Other determinations

The stationary bootstrap uses one joint row index for BTC and ETH, a uniform initial index, and geometric restarts with probability `1/mean_block`. The block-sign routine draws a fair sign then a geometric length per block, starts at day 0, and broadcasts each day’s sign across columns. With **independent** market and sign streams and exposures determined from the resampled path without sign access, `E[Xₜ,j | path, exposures] = 0`; thus `E[Xₜ,j] = 0` in distribution. A realized replication need not have sample mean zero. The callable interface alone cannot enforce those premises.

`semi_empirical` computes the benchmark on the full warm-up plus evaluation path, drops warm-up rows from reported legs, and forms `X = s(e − eᵇ)r` and `C = b + X` as specified. The extracted `benchmark_exposure` loop is textually the prior loop and uses past returns for each day’s exposure. R-6’s shared QJ path and signs fit §3.4, but its implementation cannot be assessed from these attachments.
