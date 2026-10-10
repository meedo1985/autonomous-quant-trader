# D-19 threshold-run driver — independent adversarial review (Claude Fable 5.1) at 8936859

Recorded verbatim from the reviewer's final report (2026-10-10). Run as a
read-only background agent requested with model `fable`; the reviewer
self-reported model id `claude-fable-5-1`. Adjudication pending.

## Reviewer metadata
- Reviewer: Claude Fable 5.1 (session-reported model id `claude-fable-5-1`; reasoning-effort setting not exposed as metadata).
- Role: independent adversarial reviewer, not an authority; every finding is a proposal for adjudication. Nothing here supplies owner or §16 human approval.
- Implementer (per packet): Claude Opus 5.5.
- Commit reviewed: `8936859`; repository HEAD during review `6cba606` (packet commit), branch `d19-calibration-engine`.
- Read-only: no repo file changed, nothing committed, no server access, no calibration run. `git status --short` empty after the review.

## Scope
`scripts/d19_run.py`; `calibration/rundef.py`, `calibration/chunks.py`, `calibration/seeds.py`, `calibration/generator.py` (incl. `cells_from_manifest`), `calibration/classifier.py` and `calibration/dsr.py` identity as used by the driver; `scripts/d19_run_definition.py` (anchor source); `tests/unit/test_calibration_rundef.py` (driver tests) and `tests/unit/test_calibration_chunks.py`. Checked against preregistration §8 and §13 rev 7g item 6 (read via `git show docs/d19-recommendation:review/governance-statistics-amendment/d19-preregistration/PREREGISTRATION.md`). Prior reviews/adjudications read to avoid re-raising settled items (`SOL6_DRIVER_*`, `ADJUDICATION_DRIVER_*`, `FABLE_REVIEW_AA3457B.md`). FE-4 and FE-7 remain carried items, not re-raised.

## Commands run
| Command | Result |
|---|---|
| `.venv/Scripts/python -m pytest tests/unit/test_calibration_chunks.py tests/unit/test_calibration_rundef.py -q -p no:cacheprovider -k "chunk or driver or worker or seed or plan or manifest or killed or parent or resum"` | 38 passed, 28 deselected, 118.4 s |
| `.venv/Scripts/python -I -c "<enumerate runtime_identity's hashed numpy binaries and the pocketfft files>"` | hashed: `_multiarray_umath.cp314-win_amd64.pyd`, `libscipy_openblas64_-….dll` only; `_pocketfft_umath.cp314-win_amd64.pyd` exists and is not hashed (numpy 2.5.3) |
| `git status --short`; `git rev-parse HEAD` | clean; `6cba606…` |

## Verdict
**ACCEPT for threshold pilot runs**, with non-blocking findings below. No finding lets a pilot chunk escape its run-definition hash or gating identity, or lets a refused namespace or qualification plan run. Qualification, development and held-out runs remain refused. FA-1 must be resolved before any qualification threshold run (and is better resolved before the pilot, since the cheap code repair changes which draws the pilot makes).

### What held up under attack (no finding)
- Parent→worker binding: each worker reloads the definition, checks its hash against the parent's (DR4-1), runs `start_gate` before building the `Chain`, and binds the chain to `definition_sha256(defn)` and the worker gate's own return value. The spawn child re-runs the entry script as `__mp_main__`, setting the bytecode controls before engine imports. The real end-to-end driver test passes the real gate inside workers, so worker bytecode/entry-point/code-hash checks hold.
- Seeds: `outer_seed` matches §8 exactly (keys anchor, cell_id, ns, rep; canonical JSON; 0-based rep), streams "market"/"columns" keyed Philox, anchor = `prereg_sha256`; worker re-derives and compares the recorded seed spec.
- Chain integrity: cell/namespace/range/prev/gating/binding checked per chunk; gap before a later chunk stops; corrupt chunk deleted unread and recomputed; stray `.tmp` deleted on restart and refused by `verify`; another definition's store fails on binding.
- Refusals: unbuilt namespaces, qualification plans, malformed manifests and changed seed spec refused before any chunk is written; not bypassable via the definition, because purpose and replication counts are inside the hashed definition and `run_plan` is re-checked in every worker.
- Determinism: each replication is a pure function of seed + pinned BLAS threads + cell; chains independent; `pool.map` preserves output order.
- Tests prove the claimed properties (gate ordering via refusal leaving no store; gating from worker gate return; stored draws equal an independent §8 recomputation; interrupted resume byte-identical; definition replaced after parent gate refused; pool size 2; killed worker → `BrokenProcessPool`).

## Findings

### FA-1 — QUESTION (NON-BLOCKING for pilot; BLOCKER before any qualification threshold run) — pilot runs draw the real threshold-namespace seeds, and `cell_id` is a free seed input
- **Where:** `scripts/d19_run.py:49,59-63`; `calibration/rundef.py:207-240` (`run_plan` accepts any positive `pilot` count); `calibration/generator.py` `cells_from_manifest` (any path-safe `cell_id`); `scripts/d19_run_definition.py:104-123` (any `--prereg-commit`).
- **Problem:** a `purpose: "pilot"` run uses namespace `d19-threshold-v1` and anchor `prereg_sha256` — the same seeds the qualification threshold run will use. (a) The "pilot" label is the only guard: a pilot with 300,000 reps over the candidate cells is the threshold run in substance (same bytes), made before the run definition the prereg requires. (b) A pilot whose cell ids equal the eventual manifest ids gives early sight of that cell's threshold draws before freeze. (c) `cell_id` is free text entering the outer seed, and `prereg_commit` can be any commit containing the prereg path, so cheap pilots can be repeated over id spellings / prereg commits and observed before the ids that shape the threshold acceptance region are fixed. No registry records pilot runs.
- **Impact:** §13 item 6 says the threshold run uses "its own namespace" under a definition committed before the run; pilot and threshold share seeds, and cell_id/anchor freedom is an unrecorded selection channel. Not a numerical error; a reproducibility/selection gap.
- **Proposed repair (code-only, no §8 change):** require pilot cell ids to carry a reserved prefix (e.g. `pilot-`) and refuse that prefix in any non-pilot manifest, so pilot draws never coincide with qualification draws; cap pilot reps below `PRESCRIBED["threshold"]`. Governance-level (needs decision): before qualification, derive `cell_id` canonically from (k, t, law, dependence) or freeze the manifest before any threshold-namespace draw; the qualification path should verify `prereg_commit`/`prereg_sha256` equal the accepted rev 7g ones. A separate pilot namespace would be a §8 change — proposal only.

### FA-2 — NON-BLOCKING (resolve before the threshold run) — the threshold run's own numerics are outside the reference-vector suite and the identity's binary hashes
- **Where:** `calibration/rundef.py:53-92` (reference cases exercise generator, DSR and U_G, never `classifier.diagnostics`); `calibration/dsr.py:259` (identity hashes only `_multiarray_umath*` and `*openblas*`); `scripts/d19_run.py:59-63`.
- **Problem:** every threshold replication is `classifier.diagnostics`, which uses `np.fft.rfft` (pocketfft), `np.log`, `np.corrcoef` and fractional powers; none is in a reference vector, and the pocketfft extension (`numpy/fft/_pocketfft_umath*`) is not among hashed binaries (confirmed in local venv). Only the image digest guards it, and per FE-4 that digest is a launcher-trusted environment value.
- **Scenario:** a resume runs in an image whose numpy FFT build differs (rebuilt image, wrong digest passed, different SIMD path inside pocketfft); identity, canaries and reference vectors all still match; new chunks compute different diagnostics under the same binding; the chain breaks only if a recomputed chunk happens to overlap an existing one.
- **Proposed repair:** add `classifier.diagnostics(legs.x)` (hex) to each `_reference_outputs` case, with a test that a changed diagnostic changes `reference_vectors()`. Hashing `_pocketfft_umath*`/`_umath_linalg*` in `runtime_identity` would change the decided A-V1 identity — proposal only.

### FA-3 — NON-BLOCKING — no single-writer lock on a chain; orphaned/doubled writers possible
- **Where:** `calibration/chunks.py:93-111,114-146`; `scripts/d19_run.py:119-122`.
- **Scenario:** the owner stops only the parent (e.g. `kill <pid>` outside systemd's cgroup kill) or launches twice. `ProcessPoolExecutor` workers keep computing their current chain to its end (days for a 300k chain). A relaunch runs a second writer on the same chain: its `_strays(restart=True)` can delete the live writer's `.tmp` (which then fails on `os.replace` with `FileNotFoundError`), and both open the same `.tmp` with truncation, so an interleaved truncate/rewrite can briefly publish a torn file at the final chunk name, never re-read by the writer that published it.
- **Impact:** determinism + content hashes make a silent wrong result unlikely; the cost is spurious stops, duplicated compute, and torn chunks found only at the next resume/`verify`.
- **Proposed repair:** take an exclusive non-blocking `fcntl.flock` on the chain directory fd (or a sibling `<cell_id>.lock`; a file inside the chain dir would trip `_strays`) at the start of `chunks.run`, refusing if held; document in the run procedure that the whole service cgroup is stopped, never the parent alone.

### FA-4 — NON-BLOCKING — the reported chain head is never read back from disk, and the rename is not made durable
- **Where:** `calibration/chunks.py:93-99,143-146`; `scripts/d19_run.py:90,126-127`.
- **Problem:** `run` returns a head computed from in-memory records; on-disk bytes are never re-verified, so the printed "final chain head" can differ from what `verify` would return (FA-3 torn write, media error). `_write` fsyncs the file but not the directory after `os.replace`; after a power loss a later chunk's rename can survive while an earlier one is lost, and the chain then stops permanently with "missing before a later chunk" with no recovery procedure.
- **Proposed repair:** in `worker`, return `chunks.verify(chain)` after `chunks.run` (hash-chain verification is explicitly not access under P18-6); fsync the chain directory after `os.replace` (and after `mkdir`); add a test where `_write` corrupts on-disk bytes and the driver exits 1 instead of printing a head.

### FA-5 — NON-BLOCKING (operations) — a failing chain is reported only after all earlier chains finish
- **Where:** `scripts/d19_run.py:121-125`.
- **Problem:** `pool.map` raises in submission order, so a `ChainError`/gate refusal/seed-spec refusal in cell *n* is hidden until cells 0..*n*-1 finish — days to weeks in a full run — while remaining chains keep consuming the server. A killed worker surfaces at once (BrokenProcessPool), an ordinary exception does not.
- **Proposed repair:** submit, then `concurrent.futures.wait(..., return_when=FIRST_EXCEPTION)` and `shutdown(cancel_futures=True)` on the first failure; print heads in manifest order as now.

## Findings deliberately not raised
- FE-4 (host `docker inspect` digest) and FE-7 (non-finite threshold-draw rate): carried; the driver does not make them impossible (non-finite diagnostics are stored bit-exactly, so the re-pilot can measure them).
- A missing/malformed definition key (e.g. `gating`) raises an uncaught `KeyError` in `main` and exits 1 with a traceback — fail-closed, not a finding.
- Host provenance excluded from the content hash can be edited undetected — matches §13 "recorded, never compared" design; content hashes are not MACs anywhere in this store.
- No reducer decodes the driver's hex results yet — remaining engine item, out of driver scope.
