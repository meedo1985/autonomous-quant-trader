# GPT-6 Sol review of the D-19 run driver at 1789d0b

- Prompt: `review/d19-engine/DRIVER_REVIEW_PROMPT.md`.
- CLI metadata: codex exec, model: gpt-6-sol, reasoning effort: high, sandbox: read-only, session 01a10c49-77fc-74a0-be33-9b175e20abc4, 68,522 tokens.
- Verdict FIX (DR-1..DR-5). Final answer verbatim:

---

Reviewer model: GPT-6 (exact variant not exposed)  
FIX

- **DR-1 — BLOCKER — `scripts/d19_run.py:54,67`.** §8 specifies the seed namespace `d19-threshold-v1` and the preregistration hash as the threshold anchor. The driver uses `"threshold"` and accepts any `seed_spec.anchor`; the test fixture uses `"x"`. A recorded run can therefore produce draws from the wrong seed stream. Use the §8 namespace and validate the anchor against `prereg_sha256`.

- **DR-2 — BLOCKER — `scripts/d19_run.py:66,99–101`.** Duplicate cell IDs are silently collapsed in the worker’s dictionary, while both jobs can write the same chain concurrently. Unknown laws or dependence values can also fall through to generator defaults. Validate manifest shape, unique and path-safe IDs, and supported cell parameters before starting the pool.

- **DR-3 — BLOCKER — `scripts/d19_run.py:87,99–105`.** `--replications 0` reports successful genesis heads with no draws. A completed run ending on a 500-draw boundary can also be resumed with a larger count and silently extended. Enforce the prescribed threshold count and bind the planned count to resume state.

- **DR-4 — NON-BLOCKING — `scripts/d19_run.py:48–49`.** `float.hex()` preserves finite values but collapses distinct NaN bit patterns to `"nan"`. If “bit-exact” includes non-finite draws, encode IEEE-754 bits or state and test an explicit NaN canonicalization rule.

- **DR-5 — BLOCKER — `tests/unit/test_calibration_rundef.py:498–523,545–565`.** The new tests would still pass if `Chain.gating` came from the definition instead of the worker gate’s return value, or if seeds used the wrong namespace. The “resume” test reruns an already complete chain; it does not test interruption. Add focused checks for those properties and for malformed manifests and changed replication counts.

Static inspection indicates the **spawn path meets R3-3, FE-5, and R6-1 as written**: the child re-executes the driver as `__mp_main__`, sets bytecode controls before calibration imports, and calls `start_gate` before `chunks.run`. Worker exceptions propagate through `starmap`, so a partial pool does not report success. Focused pytest could not start because this read-only environment has no usable temporary directory.
