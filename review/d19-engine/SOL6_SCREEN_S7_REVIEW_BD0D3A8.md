# §16 different-model review of the screen slice S7 (driver) at bd0d3a8

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a14962-c670-7870-8446-1157af3350f2)
- Date: 2026-10-17
- Prompt: `SCREEN_S7_REVIEW_PROMPT.md`
- Limitation (the reviewer's own): its shell failed; packet only.
- Findings: S7-R1..R3 (High), S7-R4..R7 (Medium), S7-R8 (Low). DR-1, DR-2, DR-4, DR-8 hold. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for S7 at the supplied head `bd0d3a8`. The following findings are based on the attached code. The shell failed before launch, so I could not verify the head, inspect additional repository text, run pytest, or obtain numeric lines for `screen.py`. I use function anchors there rather than invent line numbers.

| ID | Severity | Location | Concrete failure scenario |
|---|---|---|---|
| **S7-R1** | High | [d19_screen.py:57](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_screen.py:57); `screen.py:_extend_path` | The trial-code directory precedes installed packages on `sys.path`. A directory containing `sklearn` or `lightgbm` can supply code when `build_model` imports those libraries later. `check_object` runs before the path is added, and `mapping.loaded()` checks only `aqt` and `calibration`. A real model screen can therefore execute code from neither the engine commit nor the object nor the pinned image. |
| **S7-R2** | High | `screen.py:check_object`, `run_screen`; [d19_screen.py:60](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_screen.py:60) | The source manifest hashes, C2 window, window ID, and gap supplied to the screen are recorded but never matched to the qualification object’s declared inputs. A caller can use the posted object with different exploration bars or a different window and still obtain `VALID`. |
| **S7-R3** | High | `screen.py:run_screen`; [d19_screen.py:51](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_screen.py:51) | Object verification is enforced only by the CLI, which is absent from the shown `qobj.LATER` binding. A direct `run_screen(..., pilot=False)` call produces an ordinary `VALID` record without checking an object. The record also omits the posted object hash, so it cannot itself demonstrate which object was checked. |
| **S7-R4** | Medium | `screen.py:screen_reference_vectors`, `check_object` | The screen computes and records its `paths`, G-11, and G-14 vectors but compares none with an expected value. `mapping.check_runtime` compares the engine’s vectors only. A changed screen float result can be recorded as a new vector while the start check passes; the shown S7 test checks only that two calls agree with each other. |
| **S7-R5** | Medium | `screen.py:run_screen` pilot branch; [d19_screen.py:45](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_screen.py:45) | Pilot mode accepts a one-trial set even though §10 calls for a screen of a **20-trial set**. It also writes `outcome: "VALID"` and the CLI prints `VALID` with exit 0. The `measurement_only` field distinguishes the file if inspected, but the same outcome and digest interface can be used as a declaration result. |
| **S7-R6** | Medium | `screen.py:run_screen` job loop, `screen_job` | `trial_set_sha256` validates structure before work, but code loading can raise `TrialError` inside a job. With a stale signal hash in a later trial, earlier jobs may already run before the screen aborts without writing any record. This conflicts with DR-3’s “nothing is run” reading and §7.2’s requirement to record every screen run. |
| **S7-R7** | Medium | `screen.py:check_object` manifest loop | Unlike `mapping.load`’s MP-3 check, this loop does not verify `choices.json`. Replacing that file while leaving the posted manifest unchanged passes `check_object`, so the claimed qualification object has not been fully checked. |
| **S7-R8** | Low | [d19_screen.py:49](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_screen.py:49), [d19_screen.py:70](/D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_screen.py:70) | `exists()` followed by `write_bytes()` is not an atomic no-overwrite operation. If another process creates the output file between those calls, this CLI overwrites it. |

**Readings:** DR-1’s shared path and suffix for shorter warm-ups are a faithful reading of the stated length and keep the evaluation window aligned. DR-2’s per-trial seed matches the stated construction. DR-4’s availability rule, DR-8’s path-major result order, and the worker import path for intended modules are implemented as described. The fixes above are needed for DR-3, DR-5 through DR-7, and the CLI’s absolute no-overwrite claim.

This read-only response is **not a committed review record**; the project’s review-record gate remains open.