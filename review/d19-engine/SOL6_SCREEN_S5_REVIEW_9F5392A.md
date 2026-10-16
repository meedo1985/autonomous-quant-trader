# §16 different-model review of the screen slice S5 (G-11 shifts) at 9f5392a

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a14650-1a92-7a72-aab5-22bef095b7f5)
- Date: 2026-10-16
- Prompt: `SCREEN_S5_REVIEW_PROMPT.md`; packet: the prompt, Annex C C-0 excerpt and C-10, the bound `aqt.metrics.statistics` constants and draw, `seeds.py`, `calibration/screen.py` and its test at 9f5392a
- Limitation (the reviewer's own): its shell failed, so it reviewed the packet only.
- Findings: S5-R1 (Medium, test coverage). The implementation matches the annex. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for test coverage. The supplied S5 implementation matches Annex C’s seed material, inclusive shift pool, `T − 2m ≥ 499` rule, and `bootstrap_indices` rejection draw. The screen trial seed also uses a distinct object from the S1 path seed.

- **S5-R1 — Medium — `tests/unit/test_calibration_screen.py`, `test_g11_is_unavailable_below_the_shift_range`:** The availability boundary is tested only at `g = 30`. A regression that hard-codes the `T ≥ 559` threshold would pass the current tests but accept `g = 45, T = 588`, where the pool has only 499 shifts; its final `_draw(0)` would loop forever. Add the `g = 45` boundary: `T = 589` available and `T = 588` unavailable.

I could not rerun pytest or verify a numeric line number: shell creation repeatedly failed before commands started. This was read-only; no review record was committed, so it does not meet the repository’s recorded-review completion rule.