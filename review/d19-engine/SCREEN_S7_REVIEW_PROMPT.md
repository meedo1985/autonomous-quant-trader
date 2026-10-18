# Review prompt: D-19 screen slice S7 (the driver) at the head carrying this prompt

You are an independent adversarial reviewer working read-only, not an authority. This is a §16 review. Everything is attached; if your shell works you may read the repository and run `python -m pytest -q tests/unit/test_calibration_screen.py`, but do not modify files.

Check the S7 part of `calibration/screen.py` (from "S7: the screen driver": `screen_reference_vectors`, `check_object`, `check_screen_code`, `screen_job`, `_extend_path`, `run_screen`) and the thin CLI `scripts/d19_screen.py` against prereg §7.2 ("Paths", "Runs", "Outcome", "Seed"), §10 (the pilot "one screen of a 20-trial set"), §13 rev 7g item 1, Annex C rev 4 C-10 (3) and C-12 (5) (reference vectors), and the binding of `screen.py` by its bytes in the qualification object (`calibration/qobj.py` `LATER`, DRAFT R-8). Assess readings DR-1..DR-8. In particular:
- DR-1: one path per index, `max(warmup) + window + 1` hours, each trial on the path's last `warmup_t + window + 1` hours. Faithful to §7.2 "Length", or should each trial get its own path?
- DR-2/DR-3: the per-trial null-stream seed, the `PATH_UNAVAILABLE` and `TrialError` handling.
- DR-4/DR-5: the outcome rule (VALID iff every gate available or a frozen N/A) and what the record contains; whether anything §7.2 requires in the record or the declaration is missing.
- DR-6: `check_object` / `check_screen_code` reuse `mapping.py`'s MP-3/MP-4 checks with both `mapping.py` and `screen.py` taken from the object. Can a real screen run with a loaded module that is neither the engine commit's nor the object's? Is `check_runtime` enough for the screen's own float reference vectors, or must they also be recorded at the run definition and compared?
- DR-7: the pilot mode cannot be mistaken for a declaration.
- DR-8: worker processes get the engine and trial-code paths; job order in the record.
- Also: the CLI never overwrites a record, exits 2 for INVALID, and keeps all logic in `screen.py`.

Out of scope: the gates themselves (accepted slices) and the server launcher and pilot sheet (S8).

Verdict ACCEPT or FIX. Findings get stable IDs S7-Rn with severity, file:line and a concrete failure scenario.
