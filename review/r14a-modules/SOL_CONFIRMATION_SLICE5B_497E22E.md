# Sol review: confirmation slice 5b (verdict FIX)

- Reviewer: OpenAI Codex CLI v0.164.0, model `gpt-6-sol`, reasoning effort high, sandbox read-only, session `01a1c112-061b-7d20-b7d7-2ac8d764ab2d`, 2026-11-09.
- Reviewed commit: `497e22e`. Prompt: see the slice prompt file. Recorded verbatim below (final message only); adjudication in the matching ADJUDICATION file.

---

**What this change does:** Slice 5b builds the C-14 CPCV diagnostic report: eight groups, 28 splits, seven paths, flat-start group simulations, and paired Sharpe summaries. I reviewed commit `497e22e` against `53b6bbc` using `git show`, without accessing confirmation or lockbox data.

**Verdict: FIX.** I found one test-label leak. This is an independent review finding, not an approval.

### Findings

1. **R14S5B-S-1 — BLOCKER: held-out labels change the fit.** [c2_confirmation.py:2147](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:2147) computes one embargo length from labels in *all eight* groups, then uses it to select each split’s training rows. In a synthetic 30-day example, changing only group 0’s labels changes the embargo from 1 to 2 days; for split `(0, 7)`, training row 5 disappears. Thus held-out labels influence the fitted model. C-14(2) says each split trains on the other six groups with purge and embargo; the Constitution requires no future leakage. Compute the cutoff separately for each split without its test labels, preserving calendar gaps, and add a test that changing test labels cannot change retained training rows. I disagree with **LG5B-2**’s single window-wide embargo reading.

2. **R14S5B-S-2 — QUESTION: causal feature history crosses a test group.** [c2_confirmation.py:2158](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:2158) can retain day 5 after test group 0 while an allowed feature such as `ret_168h` still uses prices from that test group. C-14(2) says “trains on the other 6 groups,” while protocol lines 205–214 specify a label/ACF embargo, not a feature-lookback embargo. This may be an intended causal-history convention, but it prevents a claim that *no test-group features* enter a fit. Record an explicit binding before making that claim; changing the prescribed embargo would require governance review.

3. **R14S5B-S-3 — NON-BLOCKING: tests do not independently check every path label.** [test_c2_confirmation_cpcv.py:215](D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_cpcv.py:215) checks that model-path values vary, then derives expected summaries from the reported values. Swapping the reported results for paths 2 and 3 would leave those assertions, and the path-1 failure test, satisfied while violating C-14(3)’s `g XOR p` assignment. Add an independent per-path expected-result check with distinguishable synthetic split outcomes.

### Checks and limits

The group remainder, lexicographic splits, and XOR path construction match C-14. The ESS switch precedes feature, fit, and report computation; the code uses six non-test decision groups, label-horizon purge, no 24-month fit window, and the supplied estimator seed. `run_event_contract` resets exposure, pending order, and clock for each group; a fresh overlay is loaded. The whole-window benchmark, C-0 estimands, type-seven summaries, and unavailable-path reporting match the stated rules. I found no current reader of `cpcv_report`. **LG5B-1, -4, and -5** are consistent with the code and governing text. **LG5B-3**’s continuous signal state is consistent with C-14’s explicit reset list, which omits signal state; its intent remains unverified.

Ruff lint and format checks passed; the no-write engine import check returned `['numpy']`. The working tree is clean, and the commit changes no frozen-file paths. I could not run pytest: this read-only sandbox has no writable temporary directory, so pytest fails before collection. I did not independently rerun mypy, verify every frozen hash, or verify the author’s reported 306 passing tests. No review record was committed under this read-only instruction; the repository’s committed-review requirement remains outstanding.
