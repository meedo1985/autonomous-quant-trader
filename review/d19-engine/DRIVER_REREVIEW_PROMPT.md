You are an independent, adversarial code reviewer (different model from the implementer, Claude Opus 5.5). Read-only: do not edit or commit; no network.

Repository in your working directory, branch d19-calibration-engine. New file: `scripts/d19_run.py` (the D-19 run driver, threshold namespace only), plus new tests at the end of `tests/unit/test_calibration_rundef.py` (`_driver`, `test_the_driver_*`, `test_a_worker_runs_the_start_gate_before_any_chunk`) and a manifest change in that file's fixture. Review the driver repairs: `git diff 1789d0b HEAD -- calibration scripts tests` (HEAD = the repair commit). Previous review: review/d19-engine/SOL6_DRIVER_REVIEW_1789D0B.md; adjudication: review/d19-engine/ADJUDICATION_DRIVER_1789D0B.md.

Spec: `git show origin/docs/d19-recommendation:review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md` section 13 (rev 7g), items 4 and 6 (and §8 seeds).
Accepted components it builds on: `calibration/rundef.py` (start_gate, run definition; accepted in review/d19-engine/SOL6_REREVIEW_5734FB7.md) and `calibration/chunks.py`.

Requirements carried to this driver (review/d19-engine/ADJUDICATION_5734FB7.md):
- R3-3: every process that computes chunks runs `start_gate` itself before any chunk.
- FE-5: every `Chain` is built only from `definition_sha256(defn)` and the gating `start_gate` returned.
- FE-4: AQT_IMAGE_DIGEST taken from host `docker inspect` (launcher; documented here).
- FE-7: re-pilot measures non-finite threshold draws (not this code).
- R6-1: every worker entry point disables bytecode caching before importing engine code.

Check:
0. Are DR-1..DR-5 repaired as the adjudication claims (including the reading of "the preregistration hash" as prereg_sha256)?
1. Are R3-3, FE-5 and R6-1 still met with multiprocessing "spawn" workers (what is `sys.modules["__main__"]` in a spawn child; do the bytecode settings run before any engine import in the child; can a worker compute a chunk without having passed the gate)?
2. Threshold replications: seed namespace and derivation per §8 (`outer_seed(anchor, cell_id, "threshold", rep)` with the definition's seed anchor), diagnostics stored bit-exactly, K=1 tail set, chunk binding/gating fields. Anything that makes a resumed run differ from an uninterrupted one?
3. Failure behaviour: a worker exception, a partial pool failure, a wrong `--replications` on resume, a cell manifest that is malformed — fail closed?
4. Would each new test fail if its property were broken?

You may run read-only Python with `.venv/Scripts/python.exe` writing only to a temp dir.

Output: first line "Reviewer model: <model id>", then verdict ACCEPT or FIX, then findings DR2-1, DR2-2, ... with severity, file:line, failure scenario, minimal repair. Concise.
