# Adjudication: Sol review of the DR2-1 unlock at c536943

Record: `SOL6_DR2_1_UNLOCK_REVIEW_C536943.md` (FIX). Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-19.

| ID | Verdict | Repair |
|---|---|---|
| DR21-R1 (High) | Accepted, reproduced. The driver and the workers trusted the definition's `prereg_sha256` without reading the commit it names. With a pinned hash, a hand-edited definition could assert it (with seeds anchored to it) while naming other preregistration bytes. | `rundef.prereg_problem(defn, root)` reads `PREREG_PATH` at `prereg_commit` with the same replacement-free, `GIT_*`-free git the recorder uses (moved from `d19_run_definition.py` into `rundef.git`; the recorder now calls it), and compares the SHA-256. `d19_run.py` runs it in the job set-up and in every worker, before any chunk. The new test `test_the_driver_refuses_a_preregistration_hash_its_commit_does_not_have` fails on the old driver (checked) and passes now. |
| DR21-R2 (Medium) | Accepted. The test asserted the constant is `None`, so the later one-line pin would fail the suite. | The test sets the constant to `None` with `monkeypatch` for the unset case. |

No finding left unrepaired. The repair changes engine code (`calibration/rundef.py`), so `generator_sha256` changes; no qualification definition or chunk exists yet.
