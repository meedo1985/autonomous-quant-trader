# Re-review prompt: D-19 screen slice S1 at f47ce17

You are an independent adversarial reviewer working read-only, not an authority. You reviewed S1 at 8bf7188 (verdict FIX, S1-R1..R3; record attached). Attached: the adjudication, the repair diff 8bf7188..f47ce17, and the complete `calibration/screen.py` and its test at f47ce17. Check that each repair resolves its finding without new defects: the gap/end restart in `hourly_indices` (draw order, off-by-one at the last row, a source with gaps everywhere), the `PathUnavailable` check (prices only, volume excluded), and the SP-6 wording. Out of scope: later slices.

Verdict ACCEPT or FIX. New findings get stable IDs S1R-Rn with severity, file:line and a concrete failure scenario.
