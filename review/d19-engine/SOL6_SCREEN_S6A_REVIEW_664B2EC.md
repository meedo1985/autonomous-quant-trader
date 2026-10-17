# §16 different-model review of the screen slice S6a at 664b2ec

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a14886-f798-7931-8ae9-12ded442d9ed)
- Date: 2026-10-17
- Prompt: `SCREEN_S6A_REVIEW_PROMPT.md`; packet: the prompt, the READY design revision 4, owner decisions WF-4 and S6D-R6, frozen protocol l.100-215, `gap.py`, the diff eb3ddae..664b2ec, `calibration/screen.py` at 664b2ec, the engine import test, local validation
- Limitation (the reviewer's own): its shell failed, so it reviewed the packet only.
- Findings: S6A-R1..R3 (High), S6A-R4 (Medium). Labels, calendar clamp, refit cadence, purge and embargo boundary, class mappings and CI pins consistent. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for the supplied S6a at `664b2ec`.

- **S6A-R1 — High — [calibration/screen.py:411](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py:411).** `check_trial` accepts a model with `warmup_hours=0`. WF-2 requires enough history for 24 calendar months of training rows plus 4,801 hours of feature history, and requires refusal at declaration. Such a trial is accepted and reaches the first refit without the required rows.

- **S6A-R2 — High — [calibration/screen.py:1193](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py:1193).** `training_rows` passes a compact list of candidate labels to `embargo_days`, losing their calendar dates. `gap.py` preserves missing days when computing daily ACF lags. If candidate decisions occur every other day, correlation between consecutive candidates belongs to calendar lag 2; this code measures it at lag 1 and can choose a shorter embargo. S6a also supplies no row builder or check enforcing one 00:00 UTC BTC row per day.

- **S6A-R3 — High — [calibration/screen.py:1154](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py:1154).** `labels` does not reject an instant before sigma exists. For `j=2`, `sigma_bps[j-3]` is `sigma_bps[-1]`, so Python silently uses volatility from the end of the series to label an early row. The normal-index formula is correct, but this boundary permits lookahead; the label test does not exercise it.

- **S6A-R4 — Medium — [calibration/screen.py:1114](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/screen.py:1114).** An invalid declaration such as `model.features=[[]]` raises `TypeError` at `set(names)` instead of the interface’s `TrialError`. Validate that every feature name is a string before deduplicating, as `check_s_inputs` does.

For valid, contiguous daily inputs, I found the stated label offsets, calendar month clamp, 30-day refit cadence, purge and `<=` embargo boundary consistent with the design. The class mappings and CI pins shown also match it. The reproducibility test would not detect a deterministic but wrong model class or fixed setting.

I could not independently run pytest or verify the checkout: the shell failed before starting commands. The reported local validation is therefore unverified by this review.