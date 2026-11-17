# Final Fable review prompt: slice 6b build (B1-B5) at 24f0c95

You are Claude Fable, an independent adversarial reviewer for this repository (branch
`confirmation-module`, commit `24f0c95`, or the next commit, which only adds this prompt).
You are read-only except for ONE file you write:
`review/r14a-modules/FABLE_FINAL_BUILD_SLICE6B_24F0C95.md`. Do not edit any other file, do
not commit, do not change frozen artifacts (`docs/`, `protocols/`, `schemas/`, `specs/`,
`FROZEN_HASHES.json`, sidecars). You are not an authority: your findings are proposals; you
approve nothing, close no owner item and merge nothing.

This is the **final** different-model review of the slice 6b build of
`calibration/c2_confirmation.py`, a Constitution §16 protected component, before the
owner's PR review. The builder was Claude Opus 5.5; each slice had a Codex Astra review
(`gpt-6-astra`) and a repair.

## What to read

- Design: `review/r14a-modules/DESIGN_SLICE6B.md` rev 16 (your final design review was
  `FABLE_FINAL_DESIGN_SLICE6B_A116077.md`; adjudication `8d63b21`).
- Code: `git diff 8d63b21 24f0c95 -- calibration/ tests/` (everything after the
  pinned start-chain section of `c2_confirmation.py` that 6b adds or changes; the
  section pinned to `c2_lockbox.py` must be byte-identical, checked by
  `tests/unit/test_c2_confirmation_start.py`).
- Per slice, in `review/r14a-modules/` (build notes → Astra record → adjudication):

| Slice | Content | Notes | Astra record | Adjudication |
|---|---|---|---|---|
| B1 | headers, capture record v2, qualification re-read, declaration parse | `BUILD_NOTES_SLICE6B_B1.md` | `ASTRA_REVIEW_B1_*` | `ADJUDICATION_B1_637A7B0.md` |
| B2 | result entries, attempt binding, completion/crash, order breach, `nominate` §5 | `BUILD_NOTES_SLICE6B_B2.md` | `ASTRA_REVIEW_B2_*` | `ADJUDICATION_B2_70C379B.md` |
| B3 | cycle ledger, look/closing/termination entries, `look_allowed`, look lock, `check_read` | `BUILD_NOTES_SLICE6B_B3.md` | `ASTRA_REVIEW_B3_E514FFC.md` | `ADJUDICATION_B3_E514FFC.md` |
| B4 | signed rows §7 + drand chain hash, `prepare` + code install, `evaluate_trial` | `BUILD_NOTES_SLICE6B_B4.md` | `ASTRA_REVIEW_B4_F53CBA6.md` | `ADJUDICATION_B4_F53CBA6.md` |
| B5a | `open_look` | `BUILD_NOTES_SLICE6B_B5A.md` | `ASTRA_REVIEW_B5A_53A4550.md` | `ADJUDICATION_B5A_53A4550.md` |
| B5b/c | `evaluate_families`, records, sealing, `persist`, closing, `Store` | `BUILD_NOTES_SLICE6B_B5BC.md` | `ASTRA_REVIEW_B5BC_8F05D2F.md` | `ADJUDICATION_B5BC_8F05D2F.md` |

Verify against the code the documents cite (`src/aqt/core/ledger.py`, `attempts.py`,
`src/aqt/data/manifest.py`, `calibration/screen.py`, `dsr.py`, `classifier.py`, `qobj.py`,
`c2_lockbox.py`, `docs/RESEARCH_CONSTITUTION.md` §16, `protocols/protocol_v1.yaml`). Do not
trust citations or test names; read the code.

## Owner decisions taken during the build (recorded, do not reopen; check they are applied as recorded)

- **B4-D-1** two added signed rows `drand_group_hash`, `drand_beacon_id`; drand chain hash
  layout pinned by three known answers (`ADJUDICATION_B4_F53CBA6.md`, owner section).
- **B5B-D-1** G-13 compares SHA-256 of `specs/CANONICAL_BENCHMARKS_v1.1.md` in the module's
  checkout with the signed `canonical_benchmark_sha256`; absent file → UNAVAILABLE
  (`BUILD_NOTES_SLICE6B_B5BC.md`, owner section).
- **B5BC-O-1** `BENCHMARK_SPEC_MISSING` ∈ `U_OPS_REASONS` (`ADJUDICATION_B5BC_8F05D2F.md`).
These need S4/OD-4 wording through the formal process; check nothing presents them as
already amended governance.

**Not owner-decided yet** (accepted by the Astra B1 review only; the owner decides at the
§16 PR review): **B1-D-1** capture record schema v2 (archive payload and encoding,
`VERIFY_CAPTURE_DIGEST_2026-11-15.md`) and **B1-D-2** `protocol_hash` in the declaration's
key set (`ADJUDICATION_B1_637A7B0.md`). Give your view on each.

## Check

1. **Whole-flow safety.** Following `evaluate_trial` and `evaluate_look` end to end: can any
   path read protected data before its checks (trial: rule 4 before the read; look: the
   look entry before the read); look early (day 180, clock floor, breached families);
   produce a second look; land a result inside a look's steps 4-7; drop or hide a family,
   a crash, a breach or a procedure failure; write a closing entry without `persist`
   returning; or let a caller-supplied value stand where the module should verify it
   (R14D6B-S-1)?
2. **Design conformance.** Each rev 16 section (§1-§13) implemented as written, or the
   deviation recorded (B1-D-1, B1-D-2, B4-D-1, B5B-D-1). Name any silent
   deviation or any rev 16 requirement with no code.
3. **Repairs.** Every Astra finding in the six records: repaired as the adjudication says,
   or deliberately left (with reason). Any repair that introduced a new defect (for example
   the `of_cycle` change in `8f05d2f`, the statement-level C-14 guard in `9e0487d`).
4. **Cross-slice seams** that no per-slice review saw whole: `prepare` → `trial_may_run` →
   `run_trial`; `open_look` → `evaluate_families` → `evaluation_record` →
   `seal_families` → `persist` → closing; the identity fields written by `trial_result` and
   compared by `family_ledger` via `Inputs.expected`; the cut in `check_read` vs
   `trial_path` vs `nominee_gates`/`seal_family` path lengths.
5. **Tests.** Known gap stated by the builder: no end-to-end run of `evaluate_trial` or
   `evaluate_look` through the real BLS beacon, headers, capture and frozen gate code; the
   step tests replace those with recorders. Is that gap acceptable before merge, or must an
   end-to-end test (synthetic beacon not possible: BLS needs a real round) be added? Name
   any other missing test that would catch a plausible regression.
6. **§16 and governance.** Nothing in the build, notes or records lets AI approve, merge,
   amend or activate governance; owner items are marked as owner items.

You may run (set `TMP`/`TEMP` to a writable directory if needed):
`.venv/Scripts/python.exe -m pytest tests/unit -k c2_confirmation -q -p no:cacheprovider`
(593 passed at `24f0c95`, about 4-5 minutes), `.venv/Scripts/ruff.exe check calibration
tests/unit/`, `.venv/Scripts/mypy.exe calibration/c2_confirmation.py` (10 pre-existing
errors in the imported `tests/unit/test_calibration_screen.py` when test files are
included), `.venv/Scripts/lint-imports.exe` (7 contracts kept).

## Output (write to the one file named above; Markdown, concise)

Verdict GO / GO WITH CONDITIONS / FIX; the model ID you can observe (say if not exposed);
files and line ranges read; commands run with results; findings `R14B6F-F-1..` each with
severity (blocker/major/minor/info), location, evidence, failure scenario, proposed
correction; one line per owner decision above (applied as recorded / not) and per B1-D-1,
B1-D-2 (your view); and a short
list of what must happen before the owner's PR review.
