# §16 different-model review of the model-library image change (PR #58) at 7d8ef54

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a134bd-c54b-7ff1-b56a-221bee60280b)
- Date: 2026-10-13
- Reviewed: owner decision D-20 §3a (a) excerpt, `dsr.runtime_identity`, `rundef.gating`/`reference_vectors`, `d19.sh probe`, the diff main...7d8ef54 and the full new lock (packet)
- Limitation (the reviewer's own): its local shell failed; it read the packet and the public PR/CI state.
- Findings: IM-R1, IM-R2 (blocking). Verdict: CHANGES REQUESTED.
- The reviewer's final output follows verbatim.

---

## Verdict: CHANGES REQUESTED

**IM-R1 — Blocking — The CI comparison does not use the current image.** [ci.yml](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/.github/workflows/ci.yml:164>) copies the *new* Dockerfile into the “numpy-only” build. That image therefore contains the newly added `libgomp1`; only its Python lock is reduced. The comparison can pass while the system-library change affects the engine’s outputs, so it does not establish the D-20 claim about the current image versus the rebuilt image. **Minimal repair:** build the baseline from the base commit’s Dockerfile *and* lock, or use the existing old image by digest, then compare it with the new image on the same runner.

**IM-R2 — Blocking — The equality check can pass with an empty suite.** [ci.yml](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/.github/workflows/ci.yml:173>) checks for two JSON lines and equality, but does not require the `blas` and `libm` canaries or all eight reference-vector keys. `gating()` measures canaries and checks them against that same measurement, so it supplies no independent key-count check. If both measured dictionaries regressed to empty, this step would pass. At this commit, the functions define two canaries and eight vectors; I found no evidence that they are empty. **Minimal repair:** assert the exact expected key sets for each image before comparing their values.

### Other checks

The lock has eight exact pins, a SHA-256 hash in every stanza, and an unchanged NumPy 2.5.3 stanza with all 66 prior hashes. The [Dockerfile](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/deploy/calibration/Dockerfile:14>) retains the base digest, adds `libgomp1`, and installs with `--require-hashes --only-binary :all:`. The CI image-build step succeeded, which is evidence that its selected wheels resolve with pinned, hashed transitive dependencies on that runner: pip requires hashes for dependencies and rejects source distributions under these flags. [pip documentation](https://pip.pypa.io/en/stable/topics/secure-installs/)

The comparison does select the newly built `aqt-d19:$COMMIT` tag, and both measurements run in one CI job on one runner. The [deploy test](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_d19_deploy.py:40>) still asserts that importing the engine modules loads only NumPy among third-party packages. Its guard covers imports made during module loading, not imports made later inside functions; this PR changes no engine code.

The PR correctly identifies the changed image digest and the expected A-V1 identity change from SciPy’s OpenBLAS files. It also states the required server re-pilot, CPU probe, interrupt-and-resume check, and reopening of FE-4 before go-ahead. I could not inspect a built image or server run to confirm the observed identity change or re-pilot results. When checked, CI’s comparison and image build had passed, while the overall calibration-launcher and calibration-tests jobs were still running. The local command runner failed before checkout access, so I ran no local tests and could not inspect local untracked changes. No files were edited. Per the repository’s review-record rule, this report still needs to be committed with its finding IDs and reviewer model metadata before the §16 review is treated as recorded.
