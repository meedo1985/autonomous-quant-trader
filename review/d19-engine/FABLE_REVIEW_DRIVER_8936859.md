# Claude Fable 5.1 adversarial review of the D-19 threshold driver at 8936859

Invocation: Claude Code subagent, model `fable` (Claude Fable 5.1), spawned
from session https://claude.ai/code/session_01JyNxBd7qn8zGQu2HzD5QXm on
2026-10-07 at the owner's request ("Go 1"). Read-only; no network, server or
credentials. It was told not to read `CLAUDE_REVIEW_DRIVER_8936859.md`, so its
findings are independent of the Opus 5.5 review. Implementer: Claude Opus 5.5.
Because both are Claude models, this is not a Constitution section 16
different-model review; the recorded Codex GPT-6 review remains that.

The reviewer's report follows verbatim. The cross-reference after it was
written by Claude Opus 5.5.

---

Reviewer model: claude-fable-5-1
Verdict: ACCEPT (scope: threshold pilot runs only; qualification refused). Conditional on FD-1 being recorded and repaired before any development or held-out run, and before the start gate is cited as proving method V's bit identity on the planned Linux x86-64 target. The threshold driver diff itself (`scripts/d19_run.py`, `rundef.seed_spec/run_plan`, `generator.cells_from_manifest`, tests) has no blocking defect; its chunk values never touch `calibration/fast.py`.

Scope reviewed: `git diff 96a223e 8936859 -- calibration scripts tests` on worktree a7ea151 (verified `git diff --quiet 8936859 -- calibration scripts tests`: code in scope equals 8936859). Spec read: PREREGISTRATION.md at origin/docs/d19-recommendation §3.1, §3.5, §8, §13 rev 7g. `review/d19-engine/CLAUDE_REVIEW_DRIVER_8936859.md` was not read. Platform: Linux 6.18 x86-64 (AVX512_SKX), glibc 2.39, CPython 3.13.16, NumPy 2.5.3 with bundled scipy-openblas 0.3.34 (DYNAMIC_ARCH, Haswell), venv at scratchpad/venv.

FINDINGS

FD-1  BLOCKER (for the method-V bit-identity claim and for development/held-out runs; does not change threshold-pilot chunk values)
File: calibration/fast.py:25-34 (`_square`, `self_check`), calibration/fast.py:37 (`mean_var`); consumed by calibration/dsr.py:138 (`fast.column_lengths` in `evaluate`, including `numerics="v"`) and dsr.py:383 (`fast.mean_var` in `_replicates_v`); gate: calibration/rundef.py:310-345 (`start_gate`) and dsr.py:315 (`v_runtime_check`) never call `fast.self_check()`.
Scenario: run the engine on a Linux x86-64 host with AVX512 (the sandbox; a common rented-server CPU class). `fast.py`'s premise, "NumPy `power` with an array exponent calls the same C `pow` as Python `**`", is false here: NumPy dispatches its own SIMD pow.
Evidence:
  `python -m pytest tests/unit/test_calibration_rundef.py tests/unit/test_calibration_chunks.py tests/unit/test_calibration_engine.py -q -p no:cacheprovider` -> `1 failed, 80 passed in 161.25s`; the failure is `test_calibration_engine.py::test_block_length_is_bit_identical_to_production` at `fast.self_check()`: `RuntimeError: NumPy power no longer matches Python ** on this runtime`.
  Quantified (python -I, OPENBLAS_NUM_THREADS=1, OPENBLAS_CORETYPE=Haswell): `np.power(x, 2.0-array) != x**2` for 546 of 20000 self-check values (example x=0.2630130439773659: 0.06917586130223981 vs 0.06917586130223982); `x*x != x**2` for 18 of 20000 (so glibc 2.39 pow(x,2) is not the rounded square either; no drop-in replacement is bit-identical). Propagation: `fast.mean_var` != reference two-pass variance in 44 of 2000 random T=365 series; `fast.column_lengths` (the Annex B block-length path used by `dsr.evaluate(numerics="v")`) != `dsr._column_lengths` in 6 of 150 generated K=5,T=365 matrices; `task12` replicate Sharpes != `reference` in 20 of 150 replicates; `fast.block_length` on raw series matched production in 480 of 480 (the rounding step before it is where they diverge).
  `grep -rn self_check calibration scripts` -> only `scripts/d19_pilot.py:71` calls it; `start_gate`, `gating()` and `v_runtime_check` do not.
Impact: on the planned target class, calibration's Annex B block lengths (and the task12 numerics) are not bit-identical to the production `aqt.metrics.statistics` routine, contrary to fast.py's stated premise and to the "no computational-equivalence rule is needed" claim. The start gate records and re-checks reference vectors measured on the same machine, so it is self-consistent and will pass while the premise is broken: it does not prove the runtime is the one the method claims. The threshold run (classifier diagnostics only) is unaffected; development/held-out and any A-V1 "same numerics as production" statement are.
Minimal correction (proposals for the owner; not automatic edits): (a) fail closed: call `fast.self_check()` inside `rundef.gating()` and `rundef.start_gate()` (or `dsr.v_runtime_check`), so a runtime where the premise fails refuses to record or start; (b) decide, with the statistician, whether to compute the reference-sensitive squares in pure Python (`[(v-mean)**2 for v in values.tolist()]`, bit-identical by construction, slower) or to bind an explicit equivalence rule; (c) run `test_block_length_is_bit_identical_to_production` on the actual server image before the re-pilot. This touches accepted components (rundef.py, dsr.py, fast.py) and the run-definition content, so it needs the owner's approval process.

FD-2  NON-BLOCKING
File: scripts/d19_run.py:121-124
Scenario: a worker raises (e.g. `ChainError` on a broken chain) while other cell-chains are queued. `pool.map` raises on the first failed result; `with ... as pool` then runs `shutdown(wait=True)` before the `except` prints. `Executor.map`'s iterator cancels only futures not yet queued; `ProcessPoolExecutor` pre-queues max_workers+1 items, which run to completion.
Evidence: harness (scratchpad/fable/raise_harness.py; 6 fake cells, cell x0 raises at t=0, others sleep 6 s, WORKERS=2): `run stopped: RuntimeError: chain x0 failed at once` / `exit=1 elapsed=12.1s done_markers=['done-x1','done-x2','done-x3','done-x4']` (prompt stop would be ~6 s with 2 markers). The killed-worker path is prompt (BrokenProcessPool cancels pending work; test passes).
Impact: exit code is 1 and completed chunks remain valid and gated, so it fails closed; but the failure message is delayed by up to three or four whole cell-chains (~18 min each at K=20, T=365 by my 3.7 ms/draw measurement, longer for QJ later). The docstring's "any worker failure stops the run" overstates it.
Minimal correction: submit futures, `concurrent.futures.wait(futures, return_when=FIRST_EXCEPTION)`, then `pool.shutdown(cancel_futures=True)` and re-raise; or amend the docstring.

FD-3  NON-BLOCKING (proposal for the owner; outside the diff, in accepted components)
File: calibration/rundef.py:86 (`reference_vectors`), calibration/dsr.py:257-259 (`runtime_identity.binaries`).
Scenario: the threshold run is the classifier; the gate's reference-vector suite exercises generator, method V and gates but never `classifier.diagnostics`, and the identity hashes only `_multiarray_umath*` and `*openblas*`.
Evidence: `grep -n classifier calibration/rundef.py calibration/gates.py` -> nothing; `/proc/self/maps` after one threshold draw lists 13 NumPy extension modules including `_pocketfft_umath` (rfft in `_gph`), `_umath_linalg` (eigh, corrcoef), `_philox`, `_generator`, `_common`, of which only `_multiarray_umath` and `libscipy_openblas64_` are hashed.
Impact: within one pinned image the digest (FE-4) covers all of it, so the pilot is sound; cross-machine reproduction of the threshold run's bit-exact order statistics rests on the digest alone, not on a direct known-answer check. Minimal correction: add `sha(_exact(classifier.diagnostics(legs.x)))` for the four REFERENCE_CASES to the suite and hash every `numpy/**/*.so`. Changes run-definition content -> owner approval.

FD-4  QUESTION
File: calibration/chunks.py:94 (`tmp = path.with_suffix(".tmp")`), :102-109 (`_strays(restart=True)` unlinks every `.tmp`); scripts/d19_run.py has no store lock.
Scenario: the owner launches the driver twice on one store. Both processes write the same `chunk-NNNNNNN.tmp`; one process's `_strays` can unlink the other's in-progress temporary, making its `os.replace` raise FileNotFoundError (a spurious run failure), or both write identical bytes.
Evidence: two concurrent `d19_run.py run` on a 3-cell x 1500-draw pilot definition: both exit 0; all 9 chunk files byte-identical to a clean single run (sha256 compare). Race not hit; no corruption is possible undetected (content hash checked on load).
Minimal correction: an `fcntl.flock` on `<store>/<namespace>` in `main`, or a documented single-launcher rule.

FD-5  QUESTION (governance observation, no code change proposed)
File: calibration/rundef.py:208-241. The definition hash binds the engine code and `seed_spec` (currently only the threshold namespace). Adding development changes `SEED_NAMESPACES` and the code hash, so every definition recorded with this driver is void for qualification; any threshold run now is a pilot whose chunks cannot be carried into the run definition that development will bind to (§13 item 6 binds both to one definition). Also `purpose: "pilot"` accepts 300,000 draws, so the pilot/qualification distinction rests only on the manifest label. The packet already states qualification is refused; the owner should know the pilot's threshold chunks are disposable.

FD-6  NON-BLOCKING (minor)
scripts/d19_run.py:37 leaks one empty `/tmp/d19-no-bytecode-*` directory per process (parent, both workers; none cleaned). scripts/d19_run.py:104 `rundef.load(args.definition)` is outside the `try`, so a missing or non-definition file exits 1 with a traceback instead of a message. Both fail closed.

CHECKED, NO FINDING
- R3-3 / R6-1 under spawn: probe (scratchpad/fable/spawn_probe.py, same preamble as the driver) in a spawn child: `main_is_mp_main: True`, `main_file` = the script, `numpy_preloaded_before_preamble: False`, `engine_preloaded_before_preamble: []`, `flags_before_preamble: (False, None)` then `dont_write_bytecode: True`, fresh `pycache_prefix`, `bytecode_problem: None`, `loaded_outside: []`, OPENBLAS env ('1','Haswell'). Every `worker()` call (one per chain, pool processes reused) runs `start_gate` before building its Chain; the integration test runs the real gate in real spawn workers.
- FE-5: Chain built from `definition_sha256(defn)` and the gate's return (mutation i caught).
- Parent-to-worker binding: worker reloads and hash-compares (mutations c caught).
- Seeds vs §8: `outer_seed` equals SHA256 of the literal string `{"anchor":...,"cell_id":"c-k2","ns":"d19-threshold-v1","rep":7}`; `stream` equals Philox(key = two big-endian uint64 from the first 16 bytes of the literal stream hash, counter 0); anchor = recorded `prereg_sha256`; namespace `d19-threshold-v1`; "sign" stream belongs to §3.4 (Q5/QJ) only, correctly absent. `_exact` preserves NaN payload (7ff8000000abcdef round-trips) and -0.0 (8000000000000000). K=1 stores six tails, K>=2 eight (§13 item 4).
- Resume identity: 501-draw test; my 3-cell x 1500 run twice -> identical bytes and heads (c-k2 edcda2ea..., c-k1 71425003..., c-k20 00dfc74f...).
- Malformed manifest refusal: `cells_from_manifest` and `run_plan` checks (exact field set, path-safe ids, duplicate ids, K set, T>=16, law/dependence, K=1/cluster fit, purpose, positive counts, qualification refused).
- Killed worker: BrokenProcessPool path exits 1 promptly (test passes; 180 s timeout).
- Would each new test fail if broken (sandbox copy, scratchpad/fable/mutate.sh): a) worker skips gate -> 2 failed; b) namespace "threshold" -> 1 failed; c) no hash check -> 2 failed; d) bytecode enabled in parent+child -> 1 failed; d') bytecode enabled in spawn child only (`"__mp_main__" not in sys.modules`) -> 1 failed with `run stopped: RuntimeError: U_ops: start gate: bytecode caching is not disabled` from the worker (parent passed); e) repr instead of bit pattern -> 1 failed; f) WORKERS=3 -> 1 failed; g) duplicate ids allowed -> 2 failed; h) store created before gate -> 1 failed; i) gating from definition -> 1 failed; j) fork instead of spawn -> 2 passed (not a property break; informational).
- Costs: `start_gate` 4.7 s per chain; threshold draw 3.7 ms (K=20,T=365), 1.4 ms (K=1).

MISSING EVIDENCE
- Not run inside the pinned container image or on the owner's server; AQT_IMAGE_DIGEST was a dummy; FE-4 launcher and FE-7 re-pilot measurement are outside this code.
- FD-1 was measured on an AVX512 host; whether the owner's server CPU (dispatch features) reproduces the mismatch is unknown — the gate would not tell (that is the finding).
- Did not reproduce the FD-4 race; only showed no corruption in one concurrent run.
- Did not read CLAUDE_REVIEW_DRIVER_8936859.md (by instruction).

VALIDATION COMMANDS (venv: scratchpad/venv; cwd /home/user/autonomous-quant-trader unless noted)
- `python -m pytest tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -x -k "driver or worker or seeds or chain_carries or interrupted or malformed or killed or replaced or run_plan or seed_spec or parent_hands"` -> 26 passed, 29 deselected in 87.81s, exit 0.
- `python -m pytest tests/unit/test_calibration_rundef.py tests/unit/test_calibration_chunks.py tests/unit/test_calibration_engine.py -q -p no:cacheprovider` -> 1 failed, 80 passed in 161.25s, exit 1 (FD-1: `test_block_length_is_bit_identical_to_production`).
- `python -m ruff check .` -> All checks passed. `python -m ruff format --check .` -> 132 files already formatted. `python -m mypy calibration src` -> Success: no issues found in 62 source files. `lint-imports` -> Contracts: 6 kept, 0 broken.
- Driver runs (fixture checkout scratchpad/fable/pt1/rundef0/engine, 3-cell 1500-draw pilot definition recorded with `scripts/d19_run_definition.py record`, printed sha 6b833554...): clean run exit 0 in 22 s; two concurrent runs exit 0/0; 9/9 files byte-identical.
- Harness/probe/mutation scripts and outputs: scratchpad/fable/{raise_harness.py, fake_worker.py, spawn_probe.py, mutate.sh, mutations.txt, baseline.txt, full.txt}. No repository file was modified; `git status` clean in scope.

---

## Cross-reference with the Opus 5.5 review (written by Claude Opus 5.5)

Scratchpad paths above are in the session's ephemeral container and are not
committed; the commands and outputs quoted are the evidence of record.

| Fable | Opus (`CLAUDE_REVIEW_DRIVER_8936859.md`) | Agreement |
| --- | --- | --- |
| FD-1 BLOCKER for dev/held-out | CRD-1 | Same defect, found independently (both: 546 of 20,000). Fable adds the propagation counts and that `x*x` differs from `x**2` in 18 cases, so a pure-Python square, not `x*x`, is the bit-identical fix. Fable's "BLOCKER for development/held-out" matches CRD-1's "resolve before recording a V/gates run definition". |
| FD-2 | CRD-2 | Same. |
| FD-3 | none | New: the start gate's reference vectors never exercise `classifier.diagnostics`, the code the threshold run uses. |
| FD-4 | CRD-3 | Same (Fable ran two concurrent drivers: identical bytes, race not hit). |
| FD-5 | CRD-4 (related) | Different angle: pilot threshold chunks can never become qualification chunks; CRD-4 is about pilots reusing qualification seeds. |
| FD-6 | none | New, minor. |

None of FD-1 to FD-6 is repaired by this commit: the record is a review. All
code repairs (FD-1(a), FD-2, FD-4 lock, FD-6) and the run-definition content
changes (FD-3) wait for the owner's go-ahead; FD-1(b) and the CPU-feature
choice are proposals for the owner and the statistician; FD-5 is information
for the owner.
