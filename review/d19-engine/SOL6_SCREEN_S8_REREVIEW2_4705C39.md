# §16 different-model re-review 2 of the screen slice S8 at 4705c39

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a14990-1282-73d2-bcb5-ae0ebf3ba22b)
- Date: 2026-10-17
- Prompt: `SCREEN_S8_REREVIEW2_PROMPT.md`
- Findings: S8R-R1, S8R-R3 resolved; S8R2-R1..R3 (Medium). Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX.** The sheet pins `336e3221a1a5c7d60cf39638900e8baa19d68651`, and [the sheet commit](https://github.com/meedo1985/autonomous-quant-trader/commit/4705c392518d7a28f232303774d10de9599dac24) contains the same `d19.sh` blob as that engine commit. S8R-R1’s Docker query failure handling and S8R-R3’s step 0 instructions are resolved. S8R-R2 remains incomplete.

- **S8R2-R1 — Medium — the exclusion guard still permits competing runs.** `timing`, `record`, `choose`, and other [engine entry points](https://github.com/meedo1985/autonomous-quant-trader/blob/4705c392518d7a28f232303774d10de9599dac24/deploy/calibration/d19.sh#L153-L225) bypass `alone()`. Starting `timing` after `screen-pilot` therefore puts both in the shared slice. Two guarded launches can also both pass the query before either starts. Apply one atomic exclusion mechanism to every run that must be alone.

- **S8R2-R2 — Medium — step 0 can miss a running legacy clean check.** The [sheet checks only `status`](https://github.com/meedo1985/autonomous-quant-trader/blob/4705c392518d7a28f232303774d10de9599dac24/deploy/calibration/PILOT_SCREEN.md#L18-L31), which reports the named calibration container. At the expected old commit, [`clean-check` runs unnamed and unlabelled](https://github.com/meedo1985/autonomous-quant-trader/blob/e39b23d/deploy/calibration/d19.sh#L166-L171). Step 0 can pass while it runs, and the new label query will not see it. Check for legacy runs before moving and installing the app.

- **S8R2-R3 — Medium — `stop` abandons remaining containers after one failure.** Its [loop exits on the first failed `docker stop`](https://github.com/meedo1985/autonomous-quant-trader/blob/4705c392518d7a28f232303774d10de9599dac24/deploy/calibration/d19.sh#L179-L186). If two labelled containers are up, a failure stopping the first leaves the second unattempted. Attempt each stop, then return failure if any failed.

This is a static, read-only review. The local shell failed to start, so I could not rerun validation. No review record was committed; the project’s review-record requirement remains outstanding.