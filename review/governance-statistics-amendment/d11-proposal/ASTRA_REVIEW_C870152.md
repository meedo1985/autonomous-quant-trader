# Codex Astra review of the D-11 proposal (c870152)

Prompt: `REVIEW_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-25): model `gpt-6-astra`, sandbox read-only, reasoning effort high, live web search on, session id `01a17352-2e9c-7892-b6ac-c49637612cef`, 119,410 tokens. R19-2 review 2 of 2.

Verdict: **FIX**. Findings D11R-A-1 .. D11R-A-7.

## Report (verbatim)

**VERDICT: FIX.** Route A is a defensible reading of the frozen construction, but the proposal is not yet a complete, decision-ready binding.

Reviewer: **`gpt-6-astra`, high effort**, verified from session metadata. Reviewed HEAD: `c870152aa134a2d0eda1d7377153aa1c1fd9738f`. All findings below concern the proposal; no repairs were made.

| Authority | What it establishes |
|---|---|
| Frozen protocol and Constitution | Difference-series construction, lower 5th percentile, mandatory lockbox conditions, access boundaries |
| Owner decisions D-01/D-02, D-18, D-20/D-13 | Separate estimands; ETH E-IMPROV; E-DIFF nomination; existing bindings explicitly exclude lockbox |
| R19-2 | Two different-model reviews plus owner decision; no statistician review |
| D-11 proposal and C2 draft | Proposed wording; neither activates a binding |

**The central estimand argument is correct.** A difference series cannot identify E-IMPROV. I independently reproduced the appendix’s counterexample: identical differences give E-DIFF ≈ `33.09078421555`, but E-IMPROV ≈ `33.09078421555` or `14.79864858695`. Route B therefore requires an explicit change to the frozen input contract. Joint-leg resampling and difference-series resampling are equivalent **for E-DIFF**, when they use identical indices.

That establishes Route A’s textual compatibility, not its predictive calibration or scientific superiority.

1. **D11R-A-1 — HIGH / BLOCKER: Q2 does not resolve the identity boundary.**  
   **Place:** [proposal lines 48, 151, 167–170](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL.md:167).  
   **Failure scenario:** A “sealed” package contains confirmation history needed for rolling training. Delivering it to another identity still transfers confirmation data; hashing does not satisfy Constitution §7a or the earlier proposal’s no-raw-confirmation boundary. Conversely, transferring only the initial fitted state may not support subsequent 24-month rolling refits. “Start flat” also leaves benchmark initialization, pending orders, last-risk-increase state, and drawdown initialization unspecified.  
   **Minimal repair:** Provide a reviewed execution/data-flow contract, including causal label cutoffs and subsequent refits, that preserves the boundaries—or identify the required amendment. Define initialization for both legs. Present Q2 only after those options are technically coherent.

2. **D11R-A-2 — HIGH / BLOCKER: raw-return block selection is not dictated by line 85.**  
   **Place:** [proposal line 40](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL.md:40), §§7–8.  
   **Failure scenario:** Returns have little serial correlation but persistent volatility. Selecting blocks from `d` can miss dependence in the squared-return component of the Sharpe influence process. The resampled series and the series used to select block length are different decisions. Calling raw `d` the “literal” reading obscures this choice; allowing D-20 to choose differently leaves the proposed distribution unsettled.  
   **Minimal repair:** Remove the claim that line 85 determines this input. Explicitly settle and review raw `d` versus its Sharpe influence process before calling the binding complete. State that PPW does not itself establish coverage for this selected, shorter-horizon predictive statistic. The original method’s basic target is sampling variance of a mean. [Politis–White, §2](https://public.econ.duke.edu/~ap172/Politis_White_2004.pdf).

3. **D11R-A-3 — MEDIUM / BLOCKER: availability and window validation need an executable contract.**  
   **Place:** [proposal definitions, lines 37–48](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL.md:37).  
   **Failure scenario:** A caller checks `paired_sharpe_statistics.reason`, which reports **leg** failures. Identical nonconstant legs have aggregate `reason=None` but unavailable E-DIFF. Conversely, a constant candidate can have available E-DIFF while aggregate `reason="ZERO_VARIANCE"`. Also, `daily_net_returns` validates the supplied contiguous path; it does not establish that the path covers the entire declared window.  
   **Minimal repair:** Bind BTC to `sharpe(d).scaled`, or explicitly to `.difference_series_sharpe.scaled` and that field’s availability. Define ETH availability separately. Require exact expected timestamps and lengths, aligned identities/costs, `n≥16`, successful block selection, finite statistics/quantile, and all 2,000 valid attempts. A shorter complete path must not pass.

4. **D11R-A-4 — MEDIUM / BLOCKER: the recommendation understates Route A’s cost.**  
   **Place:** [D11-10 and Q1](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL.md:157).  
   **Failure scenario:** The owner accepts “the practical cost is small” because confirmation E-DIFF cleared DSR. Neither selection nor DSR clearance establishes that future incremental mean returns remain positive, or quantifies rejection of useful de-riskers. “Beats the benchmark day by day” can also suggest daily wins rather than a positive **average** difference.  
   **Minimal repair:** Delete the unsupported small-cost claim. Recommend A for input compatibility and consistent BTC estimand, while describing its unquantified power cost. Explain that B is a different, uncalibrated additional filter; with fixed nomination and no leakage/retries, choosing that filter does not itself enlarge the upstream false-promotion event.

5. **D11R-A-5 — MEDIUM / BLOCKER: Q3 needs a governance consequence, not only acknowledgment.**  
   **Place:** [Q3](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL.md:172).  
   **Failure scenario:** “Keep it and record the weakness” is treated as sufficient authorization for a historical lockbox, although Constitution §0 defines lockbox as future data and the C2 draft expressly leaves that definition unchanged. D-18’s historical-confirmation exception does not decide this lockbox question. Later paper trading also does not retroactively restore independence.  
   **Minimal repair:** Resolve that textual conflict explicitly before recommending retention. Describe retention as a historical, potentially selection-contaminated check with no demonstrated predictive coverage. Forward paper evidence is fresh only under a separately fixed prospective procedure.

6. **D11R-A-6 — MEDIUM / NON-BLOCKING: Route D misstates signing eligibility.**  
   **Place:** [route table, line 121](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL.md:121).  
   **Failure scenario:** The owner believes C2 can be signed with unresolved markers provided promotion remains impossible. DRAFT_WORDING explicitly prohibits that.  
   **Minimal repair:** Say: “Keeping D-11 blocked prevents signing C2 as currently drafted.” A separately revised research-only route would require its own wording and review.

7. **D11R-A-7 — LOW / NON-BLOCKING: distinguish illustrative mathematics from operational probabilities.**  
   **Place:** [§6](D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d11-proposal/PROPOSAL.md:105).  
   **Failure scenario:** The owner reads 8% as the selected nominee’s failure rate, or 71% as whole-lockbox power. Neither follows. IID and equal source/target asymptotic variances also do not alone fix Sharpe’s standard deviation at 0.894.  
   **Minimal repair:** State the approximation’s normal-limit/moment assumptions, omit selection conditioning, and label 71% as **L-2-only** power. Specify a Gaussian or near-zero-Sharpe approximation for the quoted Sharpe standard error; general variance depends on higher moments. [Lo, equations A32–A33](https://traders.berkeley.edu/papers/The-Statistics-of-Sharpe-Ratios.pdf).

**Independent numerical checks**

| Claim | Result |
|---|---|
| Target/source calendar lengths | **457 / 1247 days**, before source embargo |
| Type-7 position | `99.95`; weights `0.05`, `0.95` on zero-based entries 99, 100 |
| Positive boundary | Exact `0.319`; reference `0.31900000000000006`; float64 `T=0.319` fails |
| Negative boundary | Exact `−0.401`; reference `−0.40099999999999997`; float64 `T=−0.401` also fails L-1 |
| Disagreement example | E-IMPROV `24.818088161661457`; E-DIFF `−2.0681740134717863`; rational squared Sharpes correct |
| Illustrative L-1 false-fail | `Φ(z₀.₀₅√(n/(n+m)))`: **0.07969852**, or **0.08340220** for `n=1100` |
| Gaussian L-2 approximation | SD ≈ `0.8937`; pass probabilities ≈ **0.50 / 0.712** at true E-DIFF **0 / 0.5** |

The negative boundary statement is correct as **exact arithmetic**, but needs the same operational qualification already given for the positive case.

**Consumer contract and inheritance**

| Consumer | Required binding |
|---|---|
| Construction | Confirmation BTC daily differences; target length 457; finalized block/stream contract |
| L-1 | Annualized E-DIFF `T≥q`, reference float64 comparison |
| L-2 | Same `T>0`; zero fails |
| L-3 | Lockbox hourly-path `MDD(candidate)−MDD(benchmark)≤0.05` |
| L-4 | Lockbox ETH E-IMPROV `>0` and ETH drawdown condition, at 1x |
| D-12 | Sign follows L-2; decay follows L-1; BTC drawdown follows L-3; resolve L-4 disclosure and PASS_FAIL_ONLY |
| D-20 | Exact statistic/availability, block input, initialization, seed provenance, source/target identities, runtime, streams and reference vectors |

D11-1/2/4/5/8/11 are substantially right, subject to the repairs above. D11-3 is a valid illustrative calculation. D11-6 supports the proposed 457-day interpretation, but N-1 explicitly decided G-12/CPCV; it did not independently close D-11. D11-7 is conditional, not evidence of an actual lockbox outage. D11-9 correctly identifies shared-window dependence; D-20 must specify exposure accounting for the already-decided fixed-order family reads, without replacement or adaptive changes. D11-10’s sign identity is correct; its small-cost conclusion is unsupported.

Validation used CPython **3.14.7**, `-B`, importing this checkout’s `src`; deterministic checks passed. The 27 frozen files/sidecars/manifest matched baseline `421737f`; canonical Constitution and protocol bindings passed. Six oracle-manifest raw-byte checks differed solely because of existing CRLF checkout conversion; their committed blobs matched. No files changed.

Tests, lint, typing and import-boundary suites were N/A to this document-only review. No simulation or restricted-data access occurred. This response is **uncommitted review evidence**; recording it for R19-2 remains outstanding under the explicit read-only instruction.
