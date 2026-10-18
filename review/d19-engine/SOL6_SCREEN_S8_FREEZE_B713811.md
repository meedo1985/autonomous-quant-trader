<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-18. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a14e3d-0006-7c80-bb8b-76f05db70791. Tokens used: 29,495. Packet built from screen-plan b713811 (git show only): prompt SCREEN_S8_FREEZE_REVIEW_PROMPT.md, diff 4fed8f5..5e24942 for calibration/ and tests/, PILOT_SCREEN_EVIDENCE.md, GATE_SCREEN_S8_FREEZE_PATHS.md, OWNER_DECISION_S12_SCREEN_FEASIBILITY.md, calibration/screen.py lines 1745-2010, scripts/d19_screen.py lines 1-60. -->

# Sol review of the screen S8 paths freeze at b713811

## Review (final message, verbatim)

**Verdict: FIX**

**S8F-1 — `declare` can return a record with a different reference vector.** `declare` checks `screen_reference_vectors()` against the frozen values, then calls `run_screen`. That function loads trial signal and overlay modules before computing the record’s `reference_vectors`. A trial module can change `calibration.screen.screen_reference_vectors` when imported, causing the second call to put a different `paths` hash in the returned record. `declare` never checks that recorded value; it can still return `SCREEN_AVAILABLE`. The local gate’s claim that a wrong vector necessarily fails closed is therefore unsupported. Compare the returned record’s vectors with the values validated before trial code loads, or put those validated values directly in the record.

The hash frozen in the diff exactly matches the third pilot’s summary. The supplied engine, image, probe, script setup, and job-runtime line support the stated provenance, though they document one server computation rather than an independent reproduction. The test diff retains the `not frozen yet` refusal by patching `paths` back to `None`, and leaves the other shown assertions intact. I found no unsupported arithmetic or claim in the owner’s feasibility decision within this review’s scope.

This review uses the supplied attachments; the local shell failed to start, so I did not run tests independently.

## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-18)

| ID | Severity | Decision | Repair |
|---|---|---|---|
| S8F-1 | FIX | **Accept.** `run_screen` recomputes `reference_vectors` after trial modules are loaded, and `declare` never compared that value with the vectors it validated. The gate record's "fails closed" claim covered only the check before the run. A trial module runs in-process, so this check cannot stop deliberately hostile trial code (which could patch anything). It does close this path and catches any drift between the two computations. | `declare` refuses when `record["reference_vectors"]` differs from the vectors it validated before the run: `the screen's reference vectors changed during the run`. Test: `run_screen` wrapped to change `paths` in the record; `declare` refuses. The gate record is corrected. |

No finding is left unrepaired. Sol notes it did not run tests (its shell failed to start); the local validation is in the gate record.
