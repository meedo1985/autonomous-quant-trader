<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a126d3-8603-76f3-838d-8c7162cac71b. Tokens used: 37,492. Made from a packet (Codex's command runner fails here): the re-review prompt, the earlier review SOL6_ITEM2B_REVIEW_36AE0A9.md, ADJUDICATION_ITEM2B_36AE0A9.md, git diff 36ae0a9..a2db30c -- calibration tests, the HEAD text of calibration/semi.py and tests/unit/test_calibration_semi.py, ITEM2B_RULE_LIBRARY_PROPOSAL.md revision 2, the accepted preregistration §3.1-§3.6 and §13, protocols/protocol_v1.yaml scope, partitions, exposure_mapping and trial_accounting, src/aqt/benchmarks/canonical.py conventions and reaches_rebalance_band, and src/aqt/data/klines.py build_exploration_manifest. -->

# Independent re-review: D-19 engine item 2b, revision 2

**Reviewer model metadata:** OpenAI Codex, GPT-6 based, as identified in this session. The exact runtime model ID and effort setting are not exposed to me; I cannot verify a “Sol” designation.  
**Commit reviewed:** `a2db30c` (supplied diff from `36ae0a9`).  
**Scope:** The supplied adjudication, diff, HEAD excerpts, proposal revision 2, accepted preregistration excerpts, frozen protocol excerpts, canonical conventions, and exploration-builder excerpt. **This review uses the attachments only.**  
**Commands run:** None. The command runner was unavailable. Reported test and verification results were not independently run.

**Part A verdict: ACCEPT for pilot use of the library-independent code.** I2B-1 and I2B-2 are repaired on the supplied evidence. I2B-8 is repaired to the extent claimed in the adjudication; its integration checks remain outstanding. I found no defect introduced by the `36ae0a9..a2db30c` diff. Finding I2BR-1 is a pre-existing contract error to fix when implementing the libraries, before a Q5/QJ pilot.

**Part B recommendation: SOUND WITH FIXES, as advice to the owner.** The fixed-set choice and the R-4 index claims check out. The GARCH H-day equation is correctly indexed; the HAR forward substitution describes a causal H-day average once its initial history is defined. R-1 through R-6 are not yet fully deterministic implementation instructions. Resolve I2BR-2 through I2BR-5 in the owner’s recorded acceptance before coding the libraries. This review does not accept or amend the preregistration.

## Disposition of earlier findings

| Earlier ID | Status |
|---|---|
| **I2B-1** | **Resolved on the supplied boundary evidence.** `exploration_returns` has no caller-supplied loader and passes the exploration constant for both symbols. The supplied builder refuses another partition before opening a file, selects exploration-month archives, and filters returned bars to the window. Its sidecar-verification internals were not supplied, so that separate claim is not independently verified here. |
| **I2B-2** | **Resolved.** `joint_returns` enumerates every eligible window return date and lists leading, interior, and trailing exclusions. The tests cover each case. Compacted adjacency across a gap is expressly chosen and disclosed in R-1. |
| **I2B-3** | **Resolved as a proposal choice.** R-4 uses one fixed prefix per K, so a cell no longer averages over randomly selected designs. Acceptance still belongs to the owner. |
| **I2B-4** | **Resolved for the proposed daily stand-in, with a disclosed limit.** The band and 24-hour increase spacing are applied at daily decisions. Hourly intraday reductions in the frozen protocol remain outside this daily generator; R-5 discloses that limit. It must not be described as an exact hourly C2 exposure path. |
| **I2B-5** | **Partly resolved.** The GARCH and HAR equations and constants are supplied. HAR’s first 22 path days and the variance convention still need definitions (I2BR-3 and I2BR-5). |
| **I2B-6** | **Partly resolved.** R-2/R-3 specify observations through `t−1` and refresh timing. The day-0 exposure instructions conflict (I2BR-2), while the existing callback comment permits day-`t` information (I2BR-1). |
| **I2B-7** | **Resolved as a structural-duplicate issue.** The three EWMA choices now have distinct half-lives and trial identities. Coincident paths caused by the band can still occur and are ordinary diagnostic outcomes. |
| **I2B-8** | **Partly resolved, exactly as adjudicated.** Pinned draw vectors, scripted block boundaries, and old-loop benchmark equivalence are added. Stream derivation, library prefix invariance, and QJ path/sign sharing remain integration checks because that assembly is not supplied. |

## New findings

### I2BR-1 — High — `calibration/semi.py:46–48`; `tests/unit/test_calibration_semi.py:144–146`

**Failure scenario:** The `Exposures` comment permits row `t` to use path rows `≤ t`, although the exposure earning `r_t` must use only rows through `t−1`. The algebra test’s `cumsum(path[:, 0])` actually makes its day-`t` trend exposure depend on `r_t`. A library written to that interface comment would violate §3.4 causality while passing the current algebra test. This is pre-existing, not introduced by the reviewed diff.

**Repair:** Correct the callback contract to observations through `t−1`, use a lagged exposure in the algebra fixture, and test prefix invariance on each implemented library before a Q5/QJ pilot. The callback receives the whole array, so the contract and integration tests matter.

### I2BR-2 — Medium — proposal revision 2, “Common definitions” and R-3

**Failure scenario:** “The held exposure starts at 0 on path day 0” conflicts with applying each day’s target on day 0. EWMA and GARCH have a nonzero target on day 0 from `v̄`; one implementation gives day 0 zero exposure, another immediately rebalances to that target. Subsequent held states can differ.

**Repair:** Specify whether `e_0 = 0` is earned for the entire first path day and the first rebalance occurs for day 1, or whether 0 is merely the state immediately before the day-0 decision. Specify the first refresh for every rule accordingly.

### I2BR-3 — Medium — proposal revision 2, R-3 `HAR_RV`

**Failure scenario:** `f_t` needs `RV_{t−22} … RV_{t−1}`. At the start of the *warm-up path*, those observations do not exist. W = 250 ensures history exists by evaluation day 0, but does not define the first 22 warm-up exposures or held-state evolution.

**Repair:** Define the cold-start rule, such as a zero target until 22 returns exist, and the exact first day on which the HAR forecast can drive a rebalance. This is a proposed library definition for the owner, not a change to frozen text.

### I2BR-4 — Medium — proposal revision 2, R-3/R-4; frozen `trial_accounting`

**Failure scenario:** The vol library’s “second index” denotes three **estimator half-lives at H = 1** for EWMA, but three **forecast horizons** for HAR and GARCH. Thus R-4’s first-3 and first-9 balance is balance of index values, not of a common horizon dimension. Implementers could assign different `(hypothesis_id, parameter_point, horizon)` identities or incorrectly report a 3 × 3 × 3 horizon grid.

**Repair — proposal for the owner:** Record the exact trial tuple for all 27 vol rules, explicitly naming each EWMA half-life as an estimator parameter with horizon 1 and each HAR/GARCH H as a horizon. Describe R-4’s balance as balance of the *indexed choices*, without implying equal coverage of physical horizons. If the owner instead requires every model point to span all three horizons, that is a different library design to decide before implementation; do not silently change the frozen trial unit.

### I2BR-5 — Low — proposal revision 2, “Reference variance” and “Returns and price”

**Failure scenario:** “Variance of the source’s BTC column” leaves population versus sample variance unspecified, yielding different `v̄`, GARCH intercepts, HAR intercepts, and early exposures. The literal cumulative product `P_t` also lacks a stated response to a nonpositive factor `1+r_t` or nonfinite product after demeaning and resampling.

**Repair:** Specify `v̄` with an explicit divisor (for example, `ddof=0`) and define validation or refusal for nonpositive/nonfinite price-index factors and numerical overflow. These are reproducibility choices for the owner’s library record.

## R-4 and forecast checks

For R-4, write the second and target indices as `j = a+b (mod 3)` and `k = a+2b+c (mod 3)`. Given `(a,j,k)`, recover `b = j−a (mod 3)` and `c = k−a−2b (mod 3)`, proving a bijection over 27 rules. In the first three, `b=c=0`, so each indexed coordinate cycles once. In the first nine, `c=0`; the pairs `(a,j)`, `(a,k)`, and `(j,k)` each occur once because the corresponding two-coordinate maps are invertible modulo 3. Rule 0 has the stated canonical-like choices. The distinction about what the vol second index *means* is I2BR-4.

For GARCH, `g_t` uses observations through `t−1` and forecasts day `t`. With persistence `α+β=0.95` and unconditional variance `v̄`, the forecast for day `t+h` is `v̄+(g_t−v̄)0.95^h`; averaging `h=0,…,H−1` gives the proposed formula. For HAR, treating each forecast `f_{t+h}` as the unavailable future `RV_{t+h}` in later lag windows and averaging the H forecasts is the stated causal recursion. Its missing cold start is I2BR-3.
