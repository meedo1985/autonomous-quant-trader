# Astra re-check: slice 6b design rev 13 at 523b1dc (verdict FIX)

- Reviewer: Codex `gpt-6-astra`, reasoning effort high, `codex exec -s read-only` (Codex CLI v0.164.0; run log model line: `model: gpt-6-astra`; session id: 01a1da9f-db9b-7241-be1b-6809d2670734; 57,324 tokens), 2026-11-14. The report says the runtime model ID was not exposed to it; the run log header records it.
- Prompt: `DESIGN_SLICE6B_REV13_PROMPT_ASTRA.md` (commit `eab44f5`). Finding R14D6B13-A-1; minor wording points (called N-1 §4 durable predictions, N-2 look-lock acquisition timeout, N-3 F-2 residual wording, by the adjudicator). Report below verbatim.

---

**Verdict: FIX** — one major artifact-contract defect remains. Findings are proposals, not approval.

**Model ID:** exact runtime model ID is not exposed; I cannot verify the Astra designation.

Reviewed `523b1dc` directly. Actual HEAD is `eab44f5`; its only subsequent change is the review prompt. No files modified.

| R14D6B12 finding | Status | Evidence at rev 13 |
|---|---|---|
| F-1 | **PARTIAL** | Lines 44–48, 409–412, 426–438 correctly persist and bind every status-(a) prediction artifact and prohibit release without closure. The new `aqt.c2.artifacts.v1` construction instruction conflates different artifacts; see A-1. |
| F-2 | **PARTIAL — minimum applied** | Lines 201–212 require one process per attempt, crash accounting before another start, and disclose invisible relaunches. Optional “read begun” entry omitted explicitly. |
| F-3 | **APPLIED** | Lines 53–67 supply screen bytes, hash-checked trial objects and declaration fields. Lines 183–187 bind attempts to cycle, confirmation partition and family before reading. |
| F-4 | **APPLIED, with wording notes** | Lines 109–112, 268–272, 435–438 and 472 cover verifier follow-up, blocking waits, shared-store tests and the owner-table note. |

The F-2 omission is **sound within the explicitly trusted runner contract**. Determinism alone does not justify it: hidden relaunches still bypass crash/re-run accounting and permit extra reads. The one-launch and crash-accounting obligations, plus the disclosed enforcement limitation, justify accepting the minimum without adding another entry type.

**R14D6B13-A-1 — MAJOR: prediction artifacts cannot supply the lockbox’s trial/code inventory**

- **Location:** [DESIGN_SLICE6B.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/DESIGN_SLICE6B.md:426), lines 426–438.
- **Evidence:** `persist` receives prediction bytes per family, and the text says the store constructs `aqt.c2.artifacts.v1` “from the stored artifacts.” However, `c2_lockbox.py:489,565–619` requires one **trial object**, its **signal source**, and any **overlay source**, with hashes and sizes. Prediction bytes are a separate `artifact_bytes` input (`759–792`). `seal_family` does not return those trial/code bytes.
- **Failure scenario:** A store follows this paragraph and retains only the newly specified outputs. A closed status-(a) look exists, but constructing the inventory from predictions yields `IDENTITY_MISMATCH`; listing the required trial without retaining its bytes yields `ARTIFACT_NOT_FOUND`. Both prevent lockbox evaluation. Applying the paragraph’s prediction-hash release condition literally to trial/code artifacts also prevents their release.
- **Proposed correction:** Distinguish **prediction artifacts** from the **preregistered trial/code inventory**. Require the store to retain the declared trial and hash-bound signal/optional-overlay bytes, construct the nominee’s inventory from those bytes, and serve them alongside the separately persisted prediction. Scope `prediction_artifact_sha256` matching specifically to predictions. Add a shared-store handoff test exercising `_check_items`, `_check_trial` and prediction checks after closure, plus refusal before closure.

Other requested checks:

- **Prediction persistence/release:** Correct hash chain: closing entry → sealing record → prediction bytes. No compliant release before closure or after recorded termination.
- **Declaration:** Compatible. `_check_declared` permits additional top-level fields; a synthetic check using the exact committed function accepted the rev 13 layout.
- **Screen/trial checks:** Consistent with `check_declaration` and `check_screen_record`: trial validity/family, declared configuration hash, screen trial-set hash and qualification-object hash.
- **Locking:** No lock-order cycle found. Look → append ordering remains consistent; a blocked waiter does not hold the look lock. Finite compliant runner activity reveals no new starvation mechanism. FIFO fairness and recovery from a **live hung holder** are not guaranteed.

Minor wording points: §4 lines 280–281 should mention durable predictions as well as both records. Lines 268–270 should say “look-lock acquisition timeout”: the existing append lock still times out. The F-2 residual should explicitly retain “extra reads and bypassed crash accounting.”

Files and ranges read at `523b1dc`:

| File | Lines |
|---|---|
| `review/r14a-modules/DESIGN_SLICE6B.md` | 1–480; full requested diff |
| `…/FABLE_FINAL_DESIGN_SLICE6B_A116077.md` | 1–220 |
| `…/ADJUDICATION_FINAL_DESIGN_SLICE6B_A116077.md` | 1–29 |
| `calibration/c2_confirmation.py` | 600–795, 1895–2110, 2660–2690, 2795–2830 |
| `calibration/c2_lockbox.py` | 475–493, 520–645, 700–800, 1200–1305, 1360–1445 |
| `src/aqt/core/ledger.py` | 270–415 |
| Supporting governance/context | `AGENTS.md` 1–48; Constitution 130–165; protocol 60–68, 188–196; parent `DESIGN.md` 185–235 |

Validation: read-only `python -B -` checks passed for declaration acceptance and both artifact refusal scenarios. Git comparisons found no code/test/frozen-path changes in the reviewed interval. Tests/lint/types/import-boundary suites were N/A for this document-only re-check; full frozen-hash verification and runtime concurrency testing were not performed.

The review record remains uncommitted under your read-only instruction; repository review-record acceptance remains outstanding.