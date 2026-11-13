# Owner decisions on slice 6b design rev 2 (9d34615), 2026-11-13

Asked by Claude Opus 5.5 (`claude-opus-5-5`) with AskUserQuestion in the session of
2026-11-13. The owner's answers are recorded verbatim (option labels); the questions are
quoted in short. This record approves nothing beyond what the owner chose, activates no
governance, and does not amend any frozen artifact. Every item stays a proposal for the
signed C2 / S4 text and is confirmed again at signing.

| Item | Question (short) | Owner answer |
|---|---|---|
| R14D6B-S-6 | per-trial S, T, D: (a) change protected `dsr.evaluate`, or (b) recompute with `dsr`'s frozen functions plus a bit-for-bit check | (b) — "do 6b design rev 2 with option (b)" (asked before 11-10, given 11-13 as "do 4") |
| A-3 (R14S6-F-5) | cause of a recorded-unavailable trial | **"Split by reason (Recommended)"**: data/infrastructure reasons U_ops; a trial's own deterministic failure on valid data U_proc; the real reason carried into `nominate`'s message (design rev 2 §4) |
| A-1, A-2, A-4, A-5, A-6, A-7, OD-4 | accept rev 2's recommendations as the working direction | **"Accept as direction (Recommended)"**: build on them; confirmed again at signing |

Not decided here: whether `calibration/c2_confirmation.py` is a protected component
under Constitution §16 (if so, different-model and owner PR review before merge).
