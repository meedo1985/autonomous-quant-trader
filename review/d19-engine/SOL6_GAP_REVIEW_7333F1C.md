<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-12. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12f55-7b5f-7441-9c55-076fa2622760. Tokens used: 22,356. Made from a packet built from commit 7333f1c: the prompt below, protocol_v1.yaml target and validation.embargo, the §4 draft gap_embargo block, the preregistration §1/§3.1 lines, the owner decision, ITEM_GAP_RULE.md, calibration/gap.py, scripts/d19_gap.py, the tests, the reused EWMA function and build_exploration_manifest. -->

> # Review: D-19 C2 gap rule `g` (commit 7333f1c, branch d19-gap-rule)
> 
> You are an independent adversarial reviewer working read-only, not an authority. Your shell may not start, so everything is attached. Check that `calibration/gap.py` implements the frozen protocol's embargo cutoff and the §4 draft's gap rule as quoted below; whether the proposed readings G-1..G-5 are faithful to the frozen words, or where a different reading would change `g`; leakage (any non-exploration data); determinism; and whether the tests would catch a broken implementation. The computed result is g = 7, T_C2 = 1240. Verdict ACCEPT or FIX. Give each finding a stable ID GAP-n with severity (High/Medium/Low), file:line and a concrete failure scenario. Say what you could not check.
> 

## Review (final message, verbatim)

**Verdict: FIX before adopting `g = 7`.** The implementation computes the stated per-horizon maximum, and `1247 − 7 = 1240`. The attached code does not establish that 7 is the uniquely required cutoff under the frozen wording.

| ID | Severity | Location | Finding and concrete failure scenario |
|---|---|---|---|
| GAP-1 | High | [calibration/gap.py:94](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/gap.py:94) | G-5 defines the cutoff as the **last significant lag**. That is a defensible reading of “first lag after which no remaining lag is significant,” but a reading that selects the first lag in the nonsignificant tail would make the reported 168 h cutoff 8 rather than 7. Then `g = 8` and `T_C2 = 1239`; a C2 declaration using 7 would be invalid under that reading. The owner decision fixes the horizons, not this interpretation. |
| GAP-2 | Medium | [calibration/gap.py:56](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/gap.py:56) | G-2 skips returns across missing hours, then feeds the remaining returns to an EWMA that advances once per **observed return**. After a 24-hour outage, it advances one step rather than accounting for 24 elapsed hours. This leaves the frozen “168 h half-life” treatment of outages unresolved and can change targets and their ACF. |
| GAP-3 | Medium | [calibration/gap.py:78](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/gap.py:78) | G-4 is a proposed missing-data convention, not specified by “ACF_with_Bartlett_bands.” It uses all present targets for the variance and band sample size even when far fewer pairs exist at a lag. With a long outage, a high-lag correlation can pass this band but fail a pair-count-based band, changing the cutoff. |
| GAP-4 | Medium | [calibration/gap.py:46](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/gap.py:46) | G-3 fixes the decision at the close of the 23:00 UTC bar, while the quoted frozen text specifies daily frequency without a clock time. A different daily decision close changes the target sequence and may change `g`. The claimed match to `semi.daily_closes` could not be checked from the attachments. |
| GAP-5 | Medium | [scripts/d19_gap.py:29](D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_gap.py:29) | The builder can return `missing_archives`, but the script ignores it. If an exploration month is absent, the script still prints a gap from a shortened series. Its manifest hash identifies that run but does not reject it or verify the reported pinned manifest. |
| GAP-6 | Medium | [tests/unit/test_calibration_gap.py:75](D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_calibration_gap.py:75) | The target test derives its expected value using `gap.hourly_volatility` itself; the final test checks structural relationships, not an independently expected cutoff or `g`. A change to the volatility recursion could alter every target and the reported `g` while these tests still pass. |

G-1’s CLI path is confined to exploration by the supplied `build_exploration_manifest` guard; I found **no evidence of confirmation or lockbox leakage** in that path. For fixed input bars, the sorting and calendar-day construction make the calculation deterministic. G-2 through G-4 need explicit method bindings; G-5 needs an explicit cutoff interpretation before the proposed value is frozen.

**Could not check:** the raw bars, the reported manifest hash and `g = 7` run, the complete frozen specifications, `semi.daily_closes`, or the stated test/lint results. The shell failed to start, so I also could not read the local review skills or commit the review record required by the project instructions.
## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-12)

**Sensitivity measured** (`review/d19-engine/gap_sensitivity.py`, the same exploration manifest, no missing archives). Every combination of the GAP-2, GAP-3 and GAP-4 alternatives gives `g = 7` under the last-significant-lag reading (G-5). That covers the EWMA advanced per observed return or per elapsed hour, the Bartlett band n as all present targets or as pairs per lag, and every daily decision hour from 00:00 to 23:00 UTC. Only the GAP-1 reading changes `g`. Under the first-lag-of-the-tail reading, `g = 8` at 23:00, and 7 or 8 depending on the hour.

| ID | Decision | Action |
|---|---|---|
| GAP-1 High | AGREE that it is open; **owner decision** | Both readings are defensible. The AI recommends the last significant lag (`g = 7`): with `g` days excluded, the first window decision is `g + 1` days after the last exploration decision, a lag the ACF finds not significant. The owner chooses, and the choice is recorded with the adopted value. |
| GAP-2 Medium | AGREE that it is a reading; kept | It does not change `g`, as measured above. G-2 is kept, because it reuses the cost model's frozen estimator unchanged. |
| GAP-3 Medium | AGREE that it is a reading; kept | It does not change `g`. |
| GAP-4 Medium | AGREE that it is a reading; kept | It does not change `g` at any hour under G-5. The 23:00 bar matches `calibration/semi.py` `daily_closes` ("The 23:00 UTC close of every complete UTC day"). |
| GAP-5 Medium | AGREE, repaired | `scripts/d19_gap.py` refuses (exit 1) when the build reports `missing_archives`. |
| GAP-6 Medium | AGREE, repaired | `test_volatility_follows_the_cost_model_recursion` recomputes sigma independently, in the test, from the recursion in `specs/COST_MODEL_v1.md`: the sample sd at start-up, then the EWMA with a 168 h half-life. The target test then uses that checked sigma. |

Local: the gap tests, 7 passed; ruff check and format clean; `mypy calibration` clean.
