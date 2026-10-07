# Claude adversarial review of the D-19 threshold driver at 8936859

Reviewer model: Claude Opus 5.5 (`claude-opus-5-5`; session `get_session`
reported `session_context.model` and `last_served_model` both
`claude-opus-5-5`, effort level medium). Session
https://claude.ai/code/session_01JyNxBd7qn8zGQu2HzD5QXm, 2026-10-07.

**Independence, disclosed.** The driver was implemented by Claude Opus 5.5.
This review is by the same model, so it is **not** a different-model review
under Constitution section 16. It does not replace the recorded Codex GPT-6
review (`SOL6_DRIVER_REREVIEW_8936859.md`, ACCEPT), and it is not the Claude
Fable 5.1 review the packet suggests. It is an extra adversarial check;
it is advisory only, and the owner decides.

Verdict: **ACCEPT for threshold pilot runs only.** Qualification remains
refused. Findings: CRD-1 to CRD-4. None of them blocks a threshold pilot.
CRD-1 must be resolved before a run definition is recorded on the server for
any namespace that uses method V or the gates (development, held-out). It
should also be resolved before the threshold *qualification* definition is
recorded, because that definition fixes the runtime values for all later
namespaces (§13 item 6, "Changes").

## Scope and inputs

- Code: `git diff 96a223e 8936859 -- calibration scripts tests`:
  `scripts/d19_run.py` (new), `calibration/rundef.py` (`seed_spec`,
  `run_plan`), `calibration/generator.py` (`cells_from_manifest`),
  `scripts/d19_run_definition.py`, and the tests in
  `tests/unit/test_calibration_rundef.py`. The accepted
  `calibration/chunks.py`, `seeds.py` and `classifier.diagnostics` were also
  read, because the driver depends on them.
- Spec: `PREREGISTRATION.md` §3.5, §8 and §13 rev 7g, items 4 and 6, at
  `origin/docs/d19-recommendation` (`fff4e5f`).
- Checklist: `CLAUDE_REVIEW_PACKET_8936859.md` and
  `DRIVER_REREVIEW_PROMPT_4.md` (worker start gating, parent-to-worker
  binding, seeds, resume identity, malformed manifest, killed worker).
- No network, credentials, server, or calibration run. Synthetic test data
  only.

## What holds (checked, no finding)

- **R3-3, FE-5 under spawn.** In a spawn child, `multiprocessing` runs the
  entry script as `__mp_main__` and aliases `sys.modules["__main__"]` to it
  before it unpickles the job. So the script's header runs first: it sets
  the OpenBLAS variables, `dont_write_bytecode` and a fresh
  `pycache_prefix`, and only then imports any engine module. `start_gate`
  sees the hashed entry script, and `bytecode_problem` would flag any engine
  module cached elsewhere. In `worker`, the order is: load the definition,
  compare its hash with the parent's `expected` (DR4-1), call
  `start_gate`, and only then build the `Chain` from `definition_sha256`
  and the gating that `start_gate` returned. That ordering is the evidence.
  The end-to-end driver tests pass here on Linux with real spawn workers.
- **Seeds (§8).** The seed is `outer_seed(prereg_sha256, cell_id,
  "d19-threshold-v1", rep)`. The worker rejects a `seed_spec` that is not
  derived from `prereg_sha256`. Streams `market` and `columns` follow §8's
  construction. Seeds are per replication, so a resumed run gives the same
  bytes as an uninterrupted one. The resume test checks that byte for byte.
- **Diagnostics.** Values are stored as binary64 bit patterns, so NaN
  payloads and signed zeros survive. `L_j/T` is absent, as §13 item 4
  requires. K = 1 has six tails, with no correlation fields, and the test
  checks this against `classifier.required(1)`.
- **Binding.** Pilot counts are bound inside the run definition. A
  501-replication definition cannot extend a finished 500-replication chain:
  the binding is refused. Qualification plans are refused, and so are
  namespaces that are not built.
- **Failure paths.** A killed worker produces `BrokenProcessPool` and exit
  code 1. A malformed manifest is refused before any store exists. A
  replaced definition is refused in the worker.
- **Tests fail when their property breaks.** Each driver test asserts the
  specific property: the binding and gating fields, the seed recomputation,
  a gate refusal that writes nothing, and resume bytes. Removing the gate
  call, the hash check, or the §8 namespace would each fail at least one of
  them. This was judged by reading the tests; no mutation run was done.

## Findings

### CRD-1 — NON-BLOCKING for threshold pilots; must be resolved before recording a V/gates run definition

- **Where:** `calibration/fast.py:29-34` (`self_check`); `calibration/rundef.py`
  `start_gate` and `gating` (no call to it); only `scripts/d19_pilot.py:71`
  calls `fast.self_check()`.
- **Claim at risk:** `fast` claims to be bit-identical to the pure-Python
  reference and to production `aqt.metrics.statistics.block_length`. That
  rests on NumPy's array-exponent `power` matching C `pow`.
- **Evidence (this session, Linux x86-64, Python 3.13.16, NumPy 2.5.3, CPU
  dispatch found `X86_V3`, `X86_V4`):**
  - `tests/unit/test_calibration_engine.py::test_block_length_is_bit_identical_to_production`
    **fails** with `RuntimeError: NumPy power no longer matches Python **
    on this runtime`.
  - On `self_check`'s own 20,000 inputs, `np.power(x, full(2.0))` differs
    from `x**2` in **546** cases.
  - With `NPY_DISABLE_CPU_FEATURES=X86_V4` (AVX-512 dispatch off) it differs
    in **0** cases.
  - So the property holds on the Windows laptop, but not on an AVX-512 Linux
    machine like the planned Ubuntu server, whose CPU is not yet known.
- **Failure scenario:** the owner records a run definition on an AVX-512
  server. `gating()` measures canaries and reference vectors with this
  divergent `fast`. Because they are compared only with themselves,
  `start_gate` passes on every resume. Method V and `u_g` then compute
  replicate variances and block lengths that differ from production in
  about 5 of 10,000 squares. The calibrated thresholds would describe a
  computation that the C2 production evaluation does not perform, and no
  gate reports it.
- **Threshold namespace:** not affected. Threshold draws use only
  `generator` and `classifier`, which do not use `fast`. That is why this
  finding does not block a threshold pilot.
- **Minimal repair (code):** call `fast.self_check()` in `rundef.gating()`
  (so a non-identical runtime cannot be recorded) and in
  `rundef.start_gate()` (before the reference vectors), raising a `U_ops`
  refusal. Add a test that monkeypatches `fast._square` to diverge and
  checks that both refuse.
- **Proposal, not an edit (runtime governance):** whether the pinned image
  sets `NPY_DISABLE_CPU_FEATURES=X86_V4` (and adds it to `V_ENVIRONMENT`),
  or the server is chosen without AVX-512, changes the A-V1 runtime
  identity. That is the owner's decision. The re-pilot should record the
  server's `__cpu_features__` and the `self_check` result.

### CRD-2 — NON-BLOCKING: a failing cell is reported late, and later cells keep running

- **Where:** `scripts/d19_run.py:114` (`list(pool.map(worker, ...))`).
- **Scenario:** `pool.map` returns results in submission order. Suppose the
  job for cell 50 fails, for example with a `ChainError` from a gap in that
  chain. The parent learns of it only when cells 0 to 49 have finished.
  Meanwhile the freed worker takes cells 51, 52 and later.
- **Evidence:** a probe with 8 jobs, 2 spawn workers, job 3 failing at once
  and job 0 sleeping. Jobs 4 to 7 still finished, and the parent reported
  the failure only after job 0 finished.
- **Impact:** no unsafe chunk is written, because every job runs its own
  gate. But the owner is told about the fault hours or days late, on a
  budget-limited run of 4 to 5 months.
- **Minimal repair:** submit the jobs and use
  `concurrent.futures.wait(..., return_when=FIRST_EXCEPTION)` (or
  `as_completed`). On the first exception, cancel the pending futures and
  report.

### CRD-3 — NON-BLOCKING: nothing prevents two driver instances on one store

- **Where:** `scripts/d19_run.py` `main`; `calibration/chunks.py` `_strays`
  and `_write` (one fixed `.tmp` name per chunk).
- **Scenario:** the owner starts the run twice by accident (a second shell,
  or a unit restarted while the old process lives). Instance B's
  `_strays(restart=True)` deletes A's in-progress `.tmp`. Alternatively, A's
  `os.replace` renames B's half-written `.tmp` into place, and then B's own
  `os.replace` fails with `FileNotFoundError`.
- **Impact:** chunk content is deterministic, so this ends in a crash or
  wasted work, not wrong results. A half-written file that a third start
  reads is deleted and recomputed. There is no integrity loss, only a
  confusing failure.
- **Minimal repair:** take an exclusive lock on the store (for example
  `fcntl.flock` on `<store>/<namespace>/.lock`, Linux only, since the run
  is on the server) before any gate or chain work, and refuse if it is
  held.

### CRD-4 — QUESTION: pilot runs reuse the qualification seeds

- **Where:** `scripts/d19_run.py:63` together with `rundef.run_plan`.
- **Observation:** a `pilot` definition uses the same §8 namespace
  (`d19-threshold-v1`) and the same anchor (the preregistration hash) as the
  later qualification threshold run. So, for the same cell ids, the pilot
  computes exactly the qualification's first N draws.
- **Threshold namespace:** harmless, because thresholds are mechanical order
  statistics and no human choice follows from them. That is why this is a
  question and not a defect.
- **Development namespace:** this matters when development is built. A
  re-pilot that measures `U_G` and DSR-availability rates (§13 item 6)
  would then see development replications before the freeze.
- **Question for the owner and statistician:** should the re-pilot use its
  own seed namespace, not in §8 today, which would need a preregistration
  amendment? Or should pilots be restricted to cell ids or replication
  ranges that the qualification run never uses?

## Validation run for this review (Linux, scratchpad venv)

Environment: Linux x86-64, Python 3.13.16, NumPy 2.5.3. The venv was
installed with `pip install -e ".[dev]"` in the session scratchpad. The
project's recorded runs were on Windows with Python 3.12.

| Command | Result |
| --- | --- |
| `python -m pytest -q -p no:cacheprovider tests/unit/test_calibration_rundef.py tests/unit/test_calibration_chunks.py tests/unit/test_calibration_engine.py` | 80 passed, **1 failed** (`test_block_length_is_bit_identical_to_production`, CRD-1) |
| `python -m pytest -q -p no:cacheprovider` (the three files above deselected) | 1788 passed, 7 skipped (Windows record: 1786 passed, 9 skipped; the difference is platform-specific skips) |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 132 files already formatted |
| `mypy src` | no issues, 53 files |
| `mypy calibration scripts/d19_run.py` | no issues, 10 files |
| `lint-imports` | 6 kept, 0 broken |
| Frozen verifier (`review/task6/verify_frozen.ps1`) | N/A: PowerShell is not installed here, and this commit adds one review file and changes no frozen artifact (`git diff --stat` shows only this file) |

## Findings deliberately left unrepaired here

This record repairs nothing: it is a review, and the code belongs to the
implementer's next commit. CRD-1's runtime choice (the CPU-feature pin) is a
governance proposal for the owner, never an automatic edit. CRD-1's
`self_check` gate, CRD-2 and CRD-3 are proposed code repairs that need the
owner's go-ahead. CRD-4 is a question for the owner and the statistician.
