# §16 different-model review of the screen slice S8 (cost pilot kit) at 042c8da

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a14985-6840-7bc1-be9b-a837486a77fd)
- Date: 2026-10-17
- Prompt: `SCREEN_S8_REVIEW_PROMPT.md`
- Findings: S8-R1 (High), S8-R2..R4 (Medium); the pilot set is a valid 20-trial measurement; the launcher keeps every engine guarantee; the 15-hour estimate fits this mix only. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for `042c8da`. The pilot is a valid 20-trial §10 measurement set based on the supplied `check_trial` result and code inspection. It covers both rule families, rules with and without overlays, all six model classes, and LightGBM’s maximum declared estimator count, depth, and leaves. The launcher’s pilot command inherits the inspected image ID, uid 990, network isolation, read-only root, memory cap, and `nice 19`; it uses a separate container name and does not access the forward-paper checkout.

- **S8-R1 — High — [d19.sh](D:/PMP-programs-for-sharawi/autonomous-quant-trader/deploy/calibration/d19.sh:155).** With `set -e`, `stop` exits when `aqt-d19` does not exist, before it reaches `aqt-d19-screen`. A screen-only run therefore cannot be stopped by this command. Handle the two containers independently, including the case where either is absent.

- **S8-R2 — Medium — [d19.sh](D:/PMP-programs-for-sharawi/autonomous-quant-trader/deploy/calibration/d19.sh:149).** Both containers use `aqt-d19.slice`, while calibration `status` prints that slice’s `MemoryPeak`. After the screen peaks above a calibration run, calibration `status` reports the screen’s peak. Concurrent runs also compete under the same slice cap. Separate their accounting or explicitly exclude concurrent operation and identify the peak as shared.

- **S8-R3 — Medium — [d19_screen.py](D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_screen.py:62).** The summary prints `G-*:ok` for a gate whose value is `None`, although the pilot checks *availability*, not a passing declaration result. It also lacks a visible “measurement only” heading. A forwarded summary can be read as gate passes. Label these as “available” and identify the output as a measurement.

- **S8-R4 — Medium — [PILOT_SCREEN.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/deploy/calibration/PILOT_SCREEN.md:19).** Step 0 does not check whether `app-$old` already exists. If it is a directory from an earlier attempt, `mv` nests the current checkout inside it and the sheet continues with the wrong archive layout. Guard the destination and verify the expected old commit before moving.

The **15-hour estimate is reasonable for this particular mix**: the sheet’s figures imply roughly 13–15.4 hours on two workers. It is optimistic for a model-heavy declaration: the pilot has 14 rule trials and only one LightGBM trial, each model uses five features and the minimum allowed warm-up. At the sheet’s own 20 minutes per LightGBM path, 20 such trials would take about 100 hours on two workers. Report feasibility by proposed trial mix, not by set size alone.

I confirmed that the sheet’s `e01e745` checkout has the same reviewed launcher, pilot manifest, screen script, and screen engine bytes as `042c8da`. I could not rerun tests or commit the required review record because the local shell failed to start and this review session is read-only. The supplied 188-test and `sh -n` results remain supplied evidence, not independently reproduced validation.