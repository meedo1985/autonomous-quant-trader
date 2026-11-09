# Local gate: confirmation slice 5b (C-14 CPCV report)

- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-09, applying `task-gate-review`,
  `scientific-reproducibility-review`, `quant-code-review`. Self-review by the author; the
  independent review is Sol (`SLICE5B_PROMPT_SOL.md`).
- Scope: DESIGN §5.4; Annex C C-14 and C-11 (5) (`origin/freeze-sheet`
  `ANNEX_C_GATE_DEFINITIONS.md`); `protocols/protocol_v1.yaml` l.197-222 (validation,
  purge, embargo, cpcv).
- Finding IDs: LG5B-n. **LOCAL GATE: PASS** (no open blocker), items in §5.

## 1. Changed files

- `calibration/c2_confirmation.py` (appended): `CPCV_*` constants, `cpcv_splits`,
  `cpcv_groups`, `cpcv_path_splits`, `cpcv_training_rows`, `cpcv_report`. No new imports.
  Reuses the frozen screen pieces: `labels`, `embargo_days`, `build_model`, `fit_target`,
  `predict`, `model_params`, `leg_targets`, `g11_targets` (shift 0, the fresh-overlay
  target builder), `benchmark_targets`, `daily_returns`, and `run_event_contract`,
  `paired_sharpe_statistics`, `type_seven_quantile`.
- `tests/unit/test_c2_confirmation_cpcv.py` (new, 11 tests).

## 2. Validation (Windows 11, repo `.venv`, Python 3.14)

| Command | Result |
|---|---|
| `pytest tests/unit/test_c2_confirmation_cpcv.py` | 11 passed |
| `pytest tests/unit/test_c2_confirmation*.py tests/unit/test_c2_lockbox*.py tests/unit/test_d19_deploy.py` | 306 passed (engine import test still `['numpy']`) |
| `ruff format --check .`, `ruff check .` | clean |
| `mypy src` | no issues (56 files) |
| `mypy --strict` module + new test | 10 errors, all in the imported `test_calibration_screen.py`, pre-existing |
| `lint-imports` | 7 kept, 0 broken |

## 3. Frozen artifacts

None touched.

## 4. Self-review

- Groups: 8 chronological, remainder days to the earliest (30 days -> 4,4,4,4,4,4,3,3).
  Splits: the 28 pairs in lexicographic order. Paths: `{g, g XOR p}`; a test shows every
  split lies on exactly one path and serves both its groups there.
- Switch: computed only if G-12's ESS >= 250 (not G-12's PASS at 120); a test proves
  nothing is computed below it. G-12 UNAVAILABLE gives an UNAVAILABLE report.
- Model trials: exactly 28 fits, all with the nominee's `estimator_seed`. A test checks each
  fit's test groups are one split's, and that no training row lies in them. A unit test
  covers purge (label span meets a test group), the embargo after each test group, and
  unrealised labels at `w1`.
- Flat restarts: a non-model trial's paths equal an independent write-out (each group run
  from flat, the window benchmark), and differ from the continuous baseline. An overlay
  counting its calls shows that each of the 8 group runs starts with a fresh overlay state.
- Unavailability: one failed fit (split (0,1)) makes path 1 unavailable with
  `MODEL_FIT_ERROR`, the other 6 available, both summaries UNAVAILABLE; no path dropped.
- Role: `diagnostic_only`. An AST test shows nothing in `calibration/` or `src/`
  references `cpcv_report` (slice 6 will write it to the record and must keep reading
  nothing from it).

## 5. Items left open (not blockers for this slice)

- **LG5B-1 [DESIGN] CP-2 training set:** window days only, no rows from the warm-up before
  `w0` (C-14 (2) says the T OOS days form the groups; l.222 removes the 24-month window).
  One fit per split, with no 30-day refits inside a split.
- **LG5B-2 [DESIGN] CP-2 embargo:** one `E` per trial, from WF-3's ACF rule applied to the
  window's original labels (`t + H <= w1`). It is applied after each test group only, not
  before. The purge drops labels whose span `[t, t + H)` meets a test group.
- **LG5B-3 [DESIGN] CP-3 signal state:** C-14 (3) lists exposure, pending order, clock and
  overlay state as reset items. The signal's own state is not listed, so it runs continuously
  over the window (like the features), and each group takes its slice of `s`. The other
  reading (reset the signal state per group too) changes stateful signals only.
- **LG5B-4 [DESIGN] CP-1:** an UNAVAILABLE G-12 gives an UNAVAILABLE report with its reason,
  not "CPCV not enabled".
- **LG5B-5 [DESIGN] report layout:** `{role, status, ess, groups, paths[{path, E-IMPROV,
  E-DIFF, reason}], summaries{E-IMPROV, E-DIFF: {median, p05} | {result: UNAVAILABLE}}}`;
  floats are raw (slice 6 decides the record encoding).
- **LG5B-6 (slice 6):** wiring. The trial, path, `estimator_seed` and G-12 gate come from
  the nominee's evaluation; the report is written to the C2 evaluation record.

Claude/Sol status: prompt `SLICE5B_PROMPT_SOL.md`, sent with this commit (held for RAM, as
5a's).
