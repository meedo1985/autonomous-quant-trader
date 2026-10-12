# CI finding: engine tests fail on an Intel Xeon 8573C runner with AMX (2026-10-12)

**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`), from the CI logs. No code was changed for this finding.

**What happened.** PR #48, run `38216236898` (head `b85f4ef`, whose engine code is identical to `cdab6d0`), job `calibration-tests`, ran on an `INTEL(R) XEON(R) PLATINUM 8573C` with flags `fma avx2 avx512f avx512_bf16 amx_tile`. Result: `2 failed, 229 passed`.

- `test_calibration_engine.py::test_block_length_is_bit_identical_to_production`: `RuntimeError: NumPy power no longer matches Python ** on this runtime`. This is `calibration/fast.py` `self_check` refusing, as designed.
- `test_calibration_rundef.py::test_a_q5_pilot_runs_on_recorded_exploration_data_only`: one diagnostic differs in its last bit, `max_gph_d` `bfe7167d5bfb35b9` against the expected `bfe7167d5bfb35bb`.

**Same code, other CPU.** At `cdab6d0` the same job passed `231 passed` on an `AMD EPYC 7763` (job `114697650549`). The earlier record (`ADJUDICATION_FE4_1C44DB8.md`) lists one passing Xeon 8573C run; why this one differs (runner image, hosted Python patch release, or CPU features) is not diagnosed.

**Reading.** The CI job runs on the hosted Python 3.14 with the image's NumPy 2.5.3, not inside the pinned image. Its bit-exact expected values hold only on a runtime with the same CPU dispatch behaviour. §13 rev 7g item 6 makes this a gating condition for real runs: the runtime may be rebuilt only on a machine with the same CPU dispatch features, and the start gate re-checks canaries and reference vectors before any chunk. On a mismatch the engine refuses, as it did here.

**Owner's server: not affected.** It is an AMD EPYC-Rome (Zen 2, no AVX-512), the engine runs inside the pinned image, and its start gate passed for the FE-7 threshold and development runs (`PILOT_FE7_EVIDENCE.md`).

**Follow-up, not done here:** CI could treat a `self_check` refusal on the runner like the AMD Zen 4/5 segfault, as inconclusive. That needs its own small review. Until then, a red `calibration-tests` job needs its CPU line read before anything is concluded.

**Seen again, 2026-10-12 (PR #51, run `38271163886`):** the same two tests failed in the same way on an `Intel(R) Xeon(R) Platinum 8370C` (Ice Lake, AVX-512, no AMX), with `2 failed, 260 passed`. So the dependence is on Intel AVX-512 runners generally, not on AMX. The owner's server (AMD EPYC-Rome, no AVX-512) is still unaffected.
