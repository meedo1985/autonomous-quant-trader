# Sol re-check: confirmation slice 6a repairs (verdict FIX)

- Reviewer: OpenAI Codex CLI v0.164.0, model `gpt-6-sol`, reasoning effort high, sandbox read-only, session `01a1c145-71a0-7c42-a025-e613de40aa11`, 2026-11-09.
- Reviewed commit: `4fa758f`. Recorded verbatim below (final message only).

---

What this repair does: at commit `4fa758f`, `start()` loads line 266 before the code inventory and clears `_TRIAL_SEED` when a later check fails. The new tests cover that order, the loader swap, and several refusal paths. I reviewed the committed bytes with `git show` because this checkout uses `core.autocrlf=true`.

### Earlier findings

- **R14S6A-S-1 — PARTLY CLOSED.** The fresh-process test and [start()](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:2632) put `aqt.core.preregistration` in the inventory before `verify_code()`. The import now executes before that check, however, and a failed check leaves the imported module cached. Findings 1 and 2 below prevent full closure.
- **R14S6A-S-2 — CLOSED for the requested test gap.** The swap test changes the file during `compile`, checks that the executed value remains A, and checks that the disk contains B. A second read through `exec_module` would fail it. The bytecode tests exercise the frozen refusal function; the extra-module test exercises `cf.verify_code()` through the real screen check. These are synthetic, component-level checks, not a full start with a real qualification object.
- **R14S6A-S-3 — PARTLY CLOSED.** [LG6A-4](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/LOCAL_GATE_CONFIRMATION_SLICE6A.md:72) accurately carries the existing R14L2-S-2 owner decision. Leaving it there is acceptable for this build slice. It remains a **pre-signing blocker** for establishing that the asserted post was accepted on chain; this review does not close R-14a item 2.

### New findings

1. **R14S6AR-S-1 — BLOCKER — unverified import can act before refusal.** [c2_confirmation.py:2632](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:2632) imports engine code before `verify_code()`. The checked-in preregistration import path shows no protected partition read. But if that source is substituted with an import-time confirmation read, it executes under the experiment-engine identity before the later hash mismatch refuses the start. [R-14a item 2](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN.md:155) requires refusal without a protected read; Constitution §7a restricts confirmation access. **Minimal correction:** authenticate the exact bytes to be executed before granting that import confirmation access, then retain the loaded-module check.

2. **R14S6AR-S-2 — BLOCKER — a refused start can poison a retry.** [load_line266()](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:1023) leaves a successfully imported `aqt.core.preregistration` in `sys.modules`; [start()](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:2646) clears only `_TRIAL_SEED`. A changed source can import, fail `verify_code()`, then be restored on disk. A second `start()` reuses the changed module from memory while the code check hashes the restored file and can pass. That defeats R-14’s loaded-byte binding and R-14a’s refusal rule. **Minimal correction:** make a failed start terminal for that worker and require a fresh process for retry, or prove that every newly loaded module is removed before retry.

3. **R14S6AR-S-3 — NON-BLOCKING — seed clearing misses failures before the load.** [start()](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:2615) does not clear `_TRIAL_SEED` on entry. After one successful start, a second call with an invalid acceptance record fails in `verify_chain()` while the prior seed callable remains usable by `derive_seeds()`. R-14a item 7 says an invalid evaluation runs no gates. **Minimal correction:** clear `_TRIAL_SEED` at the start of each start attempt and add a success-then-chain-failure test. The current slice has no gate orchestration, so I did not establish a protected read from this path.

**Verdict: FIX.** This is an independent review, not approval. The acceptance provenance and launch route also remain open before signing.

`git diff --check`, focused Ruff check and format, and import-linter (7 contracts kept) passed. Focused pytest could not initialize because this read-only sandbox has no usable temporary directory; mypy returned an internal error with a no-cache invocation. I could not independently verify the author’s reported 366 passing tests, a real qualified-image start, or protected-data behavior. No confirmation or lockbox data or network was accessed. This response is not a committed review record.
