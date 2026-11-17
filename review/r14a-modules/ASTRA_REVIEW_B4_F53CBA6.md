# Astra review of 6b build B4 at f53cba6 (verbatim record)

- Reviewer: Codex CLI `codex exec -m gpt-6-astra -c model_reasoning_effort=high -s read-only`; the CLI log shows `model: gpt-6-astra`, `provider: openai`. The reviewer itself says the model ID is not exposed to it.
- Prompt: `B4_REVIEW_PROMPT_ASTRA.md` (commit e28e185). Recorded 2026-11-15 by Claude Opus 5.5 without edits below the line.

---

**Verdict: FIX.** B4 largely follows the accepted orchestration, but malformed duplicate signed rows can pass. Validation also remains incomplete.

**Model:** exact model ID is not exposed; I cannot verify the requested Astra identity. Reviewed `56790b6..f53cba6`; checkout `e28e185` adds only the permitted notes.

**Findings — proposals only**

- **B4-A-1 — major — ambiguous signed rows pass.**  
  Location: [c2_confirmation.py](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/c2_confirmation.py:3763), lines 3763–3766; inherited parser 2572–2585.  
  **Evidence:** adding either `t_min:\t"366"` or `"t_min": "366"` beside the canonical `t_min: "365"` still returns `t_min == 365`. Both reproduced. `protocol_row` counts only lines beginning with the exact `name: ` spelling.  
  **Failure:** conflicting spellings of a signed binding survive the “every row once, exact forms” check.  
  **Correction:** add B4 prevalidation rejecting noncanonical spellings and duplicate occurrences of recognized keys, while retaining the pinned parser unchanged. Add both counterexamples as refusal tests.

- **B4-A-2 — minor — oversized integers escape the promised exception contract.**  
  Location: same file, lines 3768–3771.  
  **Evidence:** `t_min="9"*4301` raises plain `ValueError` from Python’s integer-conversion limit, rather than `CycleError`. Reproduced on Python 3.14.7.  
  **Failure:** malformed signed input bypasses callers’ `CycleError` handling, although it remains read-free.  
  **Correction:** reject excessive digit length before conversion, or translate conversion errors; add the oversized-input test.

- **B4-A-3 — minor — B4-R-10 describes crash outcomes too broadly.**  
  Location: [BUILD_NOTES_SLICE6B_B4.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/review/r14a-modules/BUILD_NOTES_SLICE6B_B4.md:65), lines 65–67.  
  **Evidence:** the accepted runner rule requires eligibility checks under the look lock before writing an outcome.  
  **Failure:** a manifest refusal concurrent with a look/termination must not trigger an unconditional crash-outcome append.  
  **Correction:** qualify “then writes” with the runner’s locked eligibility check, including absence of a competing result.

**Orchestration assessment:** code inventory, per-file hash-before-write, engine-first loading, module-derived bindings, pre-read attempt checks, and locked re-check/append follow the design. No outcome is written by `evaluate_trial`. Cooperating look/trial writers cannot insert a result inside look steps 4–7; the double-launch logic permits one result.

A result **can** follow a termination inserted between the final re-check and append: termination writers need not take the look lock. This is the previously accepted conservative case, explicitly discussed in `FABLE_FINAL_DESIGN_SLICE6B_A116077.md:79`; termination prevents release. I am not reopening that decision.

**Readings**

| Reading | Assessment |
|---|---|
| B4-R-1 | **AGREE** — decimal string retained; qualification-object equality remains B5. |
| B4-R-2 | **AGREE** — stated beacon-ID grammar and integer widths. |
| B4-R-3 | **AGREE** for shared `prepare` and `evaluate_trial`; B5 must wire `evaluate_look` through it. Subject to A-1. |
| B4-R-4 | **AGREE** — eligibility is recomputed first. |
| B4-R-5 | **AGREE** — exact digest inventory, collision refusal, load exceptions translated; temporary directory retained. |
| B4-R-6 | **AGREE** — exact handles; `object_dir` unused by trial evaluation. |
| B4-R-7 | **AGREE** — capture and seeds supply result identity. |
| B4-R-8 | **AGREE** — two-tuple contract and trial-specific warm-up cut. |
| B4-R-9 | **AGREE** — derived outcome `None`; valid closing implies a look. |
| B4-R-10 | **CORRECT** — crash outcome only if the runner’s locked eligibility checks still permit it; exception propagation otherwise agrees. |
| B4-R-11 | **AGREE** — append clock supplies the timestamp. |
| B4-D-1 | **AGREE technically** — all three offline known answers pass for the stated layout, including omission of `"default"` and exclusion of scheme. Additional signed rows still require owner binding. |

**Test quality:** existing assertions address plausible regressions, but the suites do not establish every claimed guarantee. Missing tests:

- A-1/A-2 counterexamples; a spy proving each required row is requested exactly once.
- Engine-module shadowing, non-null overlays, and verification that altered bytes are never written.
- Ordered preparation checks and one real `prepare → evaluate_trial` integration with a protected-read sentinel.
- Deterministic synchronization replacing the lock test’s `sleep(0.3)` readiness assumption.

**Validation**

Commands used `rtk proxy`; bytecode writing was disabled for pytest.

| Command | Result |
|---|---|
| Requested three-file pytest command, `-q -p no:cacheprovider` | Exit 1 before collection: no writable temporary directory. |
| Same signed-file suite with `--capture=sys` | **30 passed**. |
| Prepare/trial suites with `--capture=sys -k 'sources_must or screen_record_is_checked or window_comes or malformed_signed_row or run_trial_cuts'` | **5 passed**, 20 deselected. |
| Complementary selection with `--capture=sys --tb=line -k 'not (sources_must or screen_record_is_checked or window_comes or malformed_signed_row or run_trial_cuts)'` | **4 failed, 16 setup errors**, all from unavailable temporary storage. |
| `.venv/Scripts/python.exe -B -m ruff check --no-cache` on the four changed files | Passed. |
| `.venv/Scripts/python.exe -B -m ruff format --check --no-cache` on those files | Passed. |
| `.venv/Scripts/python.exe -B -m mypy --no-incremental --no-sqlite-cache --cache-dir=NUL` on those files | Exit 1: ten errors in imported, unchanged `test_calibration_screen.py`; none reported in the four targets. Initial SQLite-cache invocations failed internally. |
| `.venv/Scripts/lint-imports.exe --no-cache` | **7 contracts kept**. |
| In-memory parser probes and frozen-integrity verification | Counterexamples reproduced; **28 baseline files, 14 sidecars, Constitution self-hash and manifest/protocol bindings passed**. |
| `git diff --exit-code`, `git diff --cached --exit-code`, status and scoped baseline comparisons | Clean; no implementation difference between `f53cba6` and HEAD. |

**Principal files/ranges read**

| File | Lines |
|---|---|
| `calibration/c2_confirmation.py` | 657–725, 1148–1170, 2572–2585, 2863–2980, 3237–3455, 3524–3615, 3710–4056 |
| Three changed test files: signed / prepare / trial | 1–123 / 1–231 / 1–309 |
| `BUILD_NOTES_SLICE6B_B4.md` / `DESIGN_SLICE6B.md` | 1–75 / 1–319, 379–394 |
| `calibration/screen.py` | 260–370, 501–745, 1930–1960 |
| `src/aqt/core/ledger.py` / `attempts.py` | 370–415 / 170–205, 280–335, 402–455 |
| Supporting evidence | Constitution §16; protocol and hash specification; CI configuration; prior FINAL-F-4 adjudication; accepted termination-race assessment |

**Local gate: BLOCKED** pending corrections/adjudication and successful mandatory validation. No drand fetch, protected-data access, file modification, or commit occurred. This report remains uncommitted under your read-only instruction; it must be preserved in the repository before counting as a completed governance review.