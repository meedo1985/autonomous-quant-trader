# Fable review of the D-14/D-15 proposal rev1 at `0f16e97` — UNSOUND

Date: 2026-10-03. The Anthropic-family review for R19-2. It ran in parallel with the Sol review and without sight of it.

- Invocation: Claude Code subagent `senior-statistical-governance`, model
  override `fable`, launched by Claude Opus 5.5 (`claude-opus-5-5`). Prompt:
  `REVIEW_PROMPT_R1.md` (committed `0f16e97`) with `{{PREFIX}}` = `FN1`.
- Model metadata: the reviewer reports `claude-fable-5-1` from its session metadata.
  The recorder observed the `fable` override but could not check the ID
  independently.
- The reviewer's final report, copied verbatim from its hand-back message (indentation removed):

---

claude-fable-5-1

**Reviewer:** Claude Fable 5.1, Anthropic Claude family (observed session model ID `claude-fable-5-1`); an AI reviewer, not an authority.
**Commit reviewed:** `0f16e97` (branch `docs/d19-recommendation`), target `review/governance-statistics-amendment/d14-d15-proposal/PROPOSAL.md` rev 1.
**Verdict:** **UNSOUND.** The D-14 construction is defective in substance, and fixing it needs an owner/statistician choice. D-15 alone would be SOUND WITH FIXES, but has one blocking gap. Skill verdict: `REVISION_REQUIRED`; both rows stay `KEEP_BLOCKED`.

No other review of this proposal was read; nothing was edited, committed or pushed.

## Independent calculations (exact, `fractions.Fraction`, in-memory `.venv` Python)

1. **Window:** the confirmation window 2022-01-01..2025-05-31 is 1,247 days. With g ≤ 28 (max_lag = 4×7), T ≥ 1,219 and admissible shifts ≥ 1,164. "T ≈ 1,219" is the minimum; the `T < 499+2g` unavailability rule is exact.
2. **Count rule vs type-7:** null values x(j) = (j−1)/100; x(475) = 237/50; type-7 q = 9481/2000. At c = 23701/5000 exactly 475 values are strictly below, so the count rule **PASSES**, while `c >= q` is False, so type-7 **FAILS**.
3. **Ties:** with x(475) = x(476) = c, the count is 474 (FAIL) while type-7 PASSES. The two rules are **not nested**.
4. **Level:** under ideal exchangeability, P(at least 475 of 500 strictly below) = 26/501 ≈ 0.0519; requiring at least 476 gives 25/501 ≈ 0.0499.
5. **Vol-sizing alignment:** with σ = [1,1,2,2]×2, z = [2,0]×4 and exposure 1/σ_t, the candidate's Sharpe² = 1; the shift k=2 gives Sharpe² **25/43**. General lemma: for returns σ_t z_t and sizing a_t = w_tσ_t independent of z (mean μ, variance s²), Sharpe² = μ²ρ/(μ²+s²−μ²ρ) with ρ = E[a]²/E[a²] ≤ 1, so Sharpe is strictly maximized by constant a — that is, by vol-targeting. This rests on an idealized assumption (drift independent of σ); its empirical strength for BTC is `UNVERIFIED_EXTERNAL_ASSUMPTION`.

## Findings

| ID | Sev | Location | Scenario | Evidence | Proposed disposition |
|---|---|---|---|---|---|
| FN1-1 | BLOCKER | P14-1 "Why shifts"; C-1; C-3; §5 Q1 | Candidate exposures are vol-scaled (l.111–129). Shifting x_t moves vol-scaled sizes into the wrong vol regimes, which **breaks the vol-sizing alignment the benchmark keeps**, so null draws are penalized for this, not only for losing timing. A zero-skill candidate passes: e.g. always-long at vol target 0.40 (E-IMPROV ≈ 0), or a vol-family candidate equal to the benchmark. The gate becomes inert, and C-1's "about 5%" is unsupported. | Calc 5. The proposal's claim that it destroys "exactly the timing the null tests" is false. Constitution §12 (l.115), uncited: "vol management is de-risking, not alpha". | Owner/STAT choice of what is shifted — full exposure, pre-sizing signal, or ratio to benchmark exposure; each trades off against the frozen "match mean exposure" (l.137). For the vol family, the choice decides whether better vol forecasting counts as timing skill. Keep D-14 blocked. |
| FN1-2 | BLOCKER | P14-1 | The backtester takes a timestamped target path (BACKTESTER_SPEC l.5). Targets are evaluated hourly (l.55), and intraday cuts happen when the target falls ≥ 0.10 below current (l.60). A daily x_t does not define the hourly targets of a shifted draw. Reading (A): hold the daily value flat, so the null has no intraday cuts and there is a systematic turnover/exposure mismatch. (B): shift the whole hourly target path by 24k h. (C): recompute targets. The three readings give different nulls. | "Slightly" (P14-1, Reported match) is unsupported. | State the input object. AI suggestion for the owner: (B), combined with the FN1-1 choice. |
| FN1-3 | NON-BLOCKING (fix before owner question) | P14-3 reason 3 | "Slightly stricter than type-7" is false: the count rule is more lenient for c in (x(475), q) and stricter only at ties. | Calcs 2–3; `type_seven_quantile` (statistics.py l.554–566) uses the same positions. | The count rule is a defensible reading (right answer, wrong reason). Delete the claim, state the actual relationship, and disclose the departure from the matrix's PROPOSED (a) (matrix l.56). |
| FN1-4 | NON-BLOCKING | P14-3; C-1 | Even under ideal exchangeability the level is 26/501 = 5.19%, not ≤ 5%. The same count rule is reused in N-2 option (a) (`n1-n2-proposal/PROPOSAL.md` l.67), so any change propagates to N-2. | Calc 4 | Offer "at least 476" (25/501) as an owner alternative; record the D-14→N-2 dependency. |
| FN1-5 | BLOCKER | P15-1/P15-2 | It is not stated whether the **benchmark leg** is also delayed (fills for execution delay; σ lag for feature delay). E-IMPROV differs between the two readings. Constitution §10 (l.111), **uncited**, requires benchmarks to be evaluated under "identical bar semantics, … cost model, execution baseline, and applicable band/min-hold rules". | Inherited: the same gap exists for G-5 (2x cost, l.283). D-02 decided only the estimand (OWNER_DECISION l.42–44), so the remedy for G-5 is an owner decision, not an edit. | Owner/STAT decides the benchmark-leg treatment for G-5, G-6 and G-7 together, citing §10. |
| FN1-6 | QUESTION | P15-1 feature delay; C-4 | Which items are lagged: training features/labels at retrain, or inference only? The sizing σ (l.114–119)? Hourly target evaluation (l.55)? Cost-model slippage σ (COST_MODEL l.20–25)? The benchmark σ? C-4 covers only "some features". | Lagged-feature canary, Constitution l.161 | Enumerate each item in P15-1. |
| FN1-7 | QUESTION | P15-1 execution delay | Risk increases need "24h since last risk increase" (l.57). In the baseline the 00:00 decision and its fill coincide; with a delayed fill at 01:00, the next 00:00 is 23 h later. If the clock runs from the fill, every consecutive-day increase is blocked. | l.57; COST_MODEL l.40 | State whether the clock runs from the decision or the fill. |
| FN1-8 | NON-BLOCKING | C-2 | P18-7 computes every pre-lockbox gate for every simulated nominee (d18 l.331–334). G-6, G-7 and G-11 need exposure paths, hourly prices, and feature and model re-runs (feature delay may need retraining). A return-level D-19 generator (the owner accepted a "benchmark-leg law", OWNER_DECISION l.55) cannot produce these. "2 per nominee" undercounts: each stress has BTC and ETH legs, possibly benchmark re-runs, and model re-inference. | P14-4's own reasoning implies G-11 availability reduces to the candidate's availability. The D-19 design is not fixed, so this is partly an assumption. | State the simulability consequence; offer an analytic availability argument as an owner option. |
| FN1-9 | NON-BLOCKING | C-3 | C-3's example is wrong. E-IMPROV is scale-invariant; for a constant exposure every shift is identical, so 0 of 500 values are strictly below and the candidate **FAILS** (ties). The real route to passing without skill is FN1-1 — a defect of the shift method, not "a limit of the frozen design". | Exact, from P14-3's tie rule | Rewrite C-3. |
| FN1-10 | NON-BLOCKING | P14-1 Seeds | Wrong referent. D-20 is the bootstrap influence/stream row, triggered only by D-03 or D-11, "the only two bootstrap-backed rows" (matrix l.72, l.80). `ReplicateStream` rejects every purpose except `"paired_sharpe_ci"` and indexes replicates 0..1999 (statistics.py l.448–467). A shift-draw stream is new code (later §16 scope) and a D-14→D-20 dependency the matrix does not record. | Read | Record it as a new dependency; offer deterministic evenly-spaced shifts (no RNG) as an owner alternative. |
| FN1-11 | NON-BLOCKING | P14-2 | "Follows D-02/D-03" overstates. Those decisions bound G-1, G-3, G-5 and L-4, and the owner accepted that `paired_delta_sharpe` keeps two meanings (OWNER_DECISION l.50–51). Reading l.137/l.140 as E-IMPROV is a fresh choice, consistent with matrix row 12. | Read | Reword as a new choice. |
| FN1-12 | NON-BLOCKING | §4 | Missing dependencies: P15-2 embeds the BTC drawdown constraint, which depends on owner item O-7 (DRAFT_WORDING l.206, l.350); the D-14 count rule feeds N-2 (FN1-4); the §10 question is shared with G-5 (FN1-5). | Read | Add these to §4. |
| FN1-13 | NON-BLOCKING | §5 Q1, Q2 | The questions are not neutral or complete. Q1's "keeping its … trading pattern, but breaking its timing" is inaccurate (FN1-1, FN1-2), and Q1 does not disclose the departure from matrix option (a) or the 5.19% level. Q2 omits the benchmark-leg treatment and the P15-2 alternatives. | Read | Revise after FN1-1, FN1-2 and FN1-5 are decided. |
| FN1-14 | NON-BLOCKING | P14-1 Shift set | The minimum shift g comes from the label embargo (7–28 days), not from how persistent the exposures are. For slow trend signals, near shifts nearly reproduce the candidate, which costs power (conservative for the level). | Analytic | Disclose as a power cost; optionally offer an exposure-autocorrelation floor as an owner option. |

**Verified correct:** the wrap point swaps one transition; the small-T rule is exact; an all-cash shifted draw occurs only if the candidate is all-cash; mirroring l.283 is a coherent precedent once FN1-5 is resolved; the citations l.266, l.283, P18-7, FA3-12, "§4 draft rev 4 §3" and §2.1 `gap_embargo` resolve correctly.

## Protocol items applied

1 (citations both ways): topic search found the uncited Constitution §10 l.111, §12 l.115, and protocol l.55, l.57, l.60. 2 (referents): D-20 (FN1-10), D-02/D-03 (FN1-11). 3 (bytes): N/A — no hashes recorded. 4 (discriminating reproduction): calcs 2–4. 5 (lemma sweep): the "destroys exactly timing" argument fails against itself (FN1-1, FN1-9). 6 (right answer, right reason): FN1-3, FN1-11. 7 (tooling): no verifier applies; the Python calculations ran. 8 (exact arithmetic): done. 9 (no repair beyond authority): every disposition is a proposal. 10 (self-descriptions): status and revision references true. 11 (inheritance): FN1-5 inherited from the G-5 gap; FN1-4 propagates to N-2. 12 (attributing other reviews): none read or cited. 13 (N/A vs unsatisfied): §16 does not apply to this Markdown proposal; it governs the later null, delay and stream code.

## Remaining decisions (owner/STAT)

What the null shifts, and the hourly input object (FN1-1/FN1-2); the benchmark-leg treatment under stress for G-5, G-6 and G-7 together (FN1-5); the feature-delay scope and the min-hold clock (FN1-6/FN1-7); "at least 475" vs "at least 476" (FN1-4); how D-19 handles these gates (FN1-8).

**Unauthorized:** deciding D-14/D-15; matrix or frozen-file edits; implementing the null, delay or stream code; simulation; confirmation or lockbox access; any cycle, promotion or trading. This review is not human, statistician or §16 review.

## Plain-language summary

1. The random-timing check slides the strategy's exposures in time. That also wrecks the volatility sizing the benchmark keeps, so even a strategy with no skill can beat the slid copies.
2. How the slid copies handle hour-by-hour risk cuts is not defined, so two programmers would build two different checks.
3. The "475 of 500" rule is reasonable, but its stated advantage over the earlier rule is false, and it passes a no-skill strategy slightly more than 5% of the time (about 5.2%).
4. For the delay checks it is not said whether the benchmark is delayed too, and your own rulebook (§10) points to treating both alike.
5. Keep both rows blocked until you choose these points. No statistician has checked any of this.
