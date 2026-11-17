# Sol second re-check: confirmation slice 6a (verdict FIX)

- Reviewer: OpenAI Codex CLI v0.164.0, model `gpt-6-sol`, reasoning effort high, sandbox read-only, session `01a1c150-f4f5-7cf3-a057-3da5f0fb0683`, 2026-11-09.
- Reviewed commit: `eb00731`. Recorded verbatim below (final message only).

---

What this change does: `start()` now derives hashes for line-266 modules from the signed engine commit, loads missing modules through `load_verified()`, and makes a refused start terminal for the process. I reviewed commit `eb00731` using `git show` for committed bytes.

### Earlier findings

| Finding | Status | Evidence |
|---|---|---|
| R14S6AR-S-1 | **PARTLY CLOSED** | [line266_sources](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:2619) obtains engine-commit blob hashes, and [load_verified](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:2531) hashes bytes before executing the two listed modules. Imports those modules trigger are checked only *after* execution; see finding 1. |
| R14S6AR-S-2 | **CLOSED** | [start](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:2668) rejects retries after `_START_FAILED`, and its `except BaseException` sets that flag on refusals inside the check, including `SeedError`. |
| R14S6AR-S-3 | **CLOSED** | [start](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:2669) clears `_TRIAL_SEED` on entry and again on refusal. |

The recorded boundary for modules loaded **before** `start()` is fair for this slice: their executed bytes must be established by the still-open launch route, LG6A-2. [DESIGN §10](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md) also leaves confirmation access mechanics open. That boundary does not cover a module newly imported *during* `load_verified()`.

### New findings

1. **R14S6AR2-S-1 — BLOCKER — an unexpected import can execute before refusal.** At [c2_confirmation.py:1031](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:1031), `load_verified()` executes a signed module; its imports can load another `aqt` or `calibration` file from disk. The [check at line 1037](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:1037) then refuses it, after its top-level code has run. For example, if the signed engine version of preregistration imports a further module and that module’s disk bytes are substituted with an import-time confirmation read, the read precedes refusal. DESIGN §4 requires the chain before a protected read, and §10 requires every executed line to be bound. **Minimal correction:** authenticate the complete import closure before allowing its execution, or use an import loader that hashes each newly requested engine module before executing it. Make a synthetic import-time marker test assert that the marker was never reached.

2. **R14S6AR2-S-2 — NON-BLOCKING — the start tests miss incorrect source wiring.** The [autouse fixture](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_start.py:77) replaces `line266_sources` with hashes of current disk files, while the main start tests replace the loader or code check. An implementation that passes disk-derived hashes instead of hashes from the signed `engine_commit` could leave those tests green; the separate [blob test](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/tests/unit/test_c2_confirmation_start.py:424) does not test `start()`’s wiring. DESIGN §4 requires the signed bytes to bind execution. **Minimal correction:** in a start test, spy on the signed commit passed to `line266_sources` and assert that its returned mapping reaches `load_line266` unchanged.

The raw SHA-256 and canonical comparison are compatible on the specified Linux checkout: Git stores these blobs with LF, so raw hashing and [canonical_sha256’s CRLF-to-LF hashing](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/rundef.py:161) agree there. A CRLF checkout fails the raw check first, as DESIGN §4 specifies. The temporary `jsonschema` placeholders contain code constructed by the signed confirmation module; I found no path through that window that executes unauthenticated `jsonschema` bytes.

**Verdict: FIX.** This is a read-only review, not approval. `git diff --check` and focused Ruff check and format passed. Focused pytest could not initialize because the sandbox has no usable temporary directory, so I could not verify the author’s 371-test result, a qualified Linux launch, or protected-read behavior. I did not run a full frozen-hash audit. No confirmation or lockbox data or network was accessed. This response is not a committed review record.
