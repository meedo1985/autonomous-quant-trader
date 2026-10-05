# Adjudication of the Codex review of the D-19 engine at 2e77f45

Review: `review/d19-engine/CODEX_REVIEW_2E77F45.md` (Codex, GPT-6, run by the
owner outside this session; committed verbatim at `0f4807c`). Adjudicated and
repaired by Claude (Opus 5.5) on 2026-10-05.

| ID | Decision | Evidence | Repair |
|---|---|---|---|
| D19CR-1 BLOCKER | AGREE | The review's snippet reproduced exactly: `within(d, {}, {})` True, `within({}, u, l)` True, NaN draw gives a NaN bound that passes `1e300`. | `classifier.required(k)` is the exact field set (eight tails, six at K = 1, plus K and T). `fit_thresholds` refuses empty draws, missing/extra fields, mixed K or T, and any non-finite draw value (stops; not dropped, not replaced, as the review asks: its treatment is not settled by the accepted method). `within` refuses (ValueError) an incomplete or non-finite threshold set and incomplete diagnostics; a non-finite diagnostic or another K/T is a refusal (False); ties accepted; ranks unchanged. Snippet now: error, False, error. Tests: rewritten `test_classifier_ranks_tails_and_exact_checks` (complete sets) and new `test_classifier_refuses_incomplete_or_non_finite_threshold_sets`. |
| D19CR-2 BLOCKER | AGREE | Reproduced: extra `chunk-0000009.json` ignored by `verify`, `reduce` yields `[0, 1]`. | `_strays(chain, restart=)`: `verify` (and so `reduce`) now refuses any file the chain does not name, read-only; an unfinished `.tmp` is deleted unread only on a restart (`run`) and refused by verification. Tests: duplicated and out-of-range file refused by both `verify` and `reduce` and left in place; `.tmp` refused by `verify` and left in place. |
| D19CR-3 BLOCKER (pre-existing) | AGREE | `mypy calibration` exited 1 (two import-untyped); `mypy calibration src` exited 1 (attr-defined at `gates.py:13`). | `[tool.mypy] mypy_path = "src"` so `calibration` is checked against the `aqt` source (no suppression); `gates.py` imports `aqt.metrics.statistics` as a module. Now `mypy calibration`, `mypy src` and `mypy calibration src` all pass. |
| D19CR-4 BLOCKER to full-engine acceptance | AGREE (unfinished scope) | The run definition and start gate are not built. | Not repaired here: it is the next build item (`CODEX_BRIEF_RUNDEF.md`); the engine is not claimed ready. |

Left unrepaired: D19CR-4 only, for the reason above.

## Checks after repair (2026-10-05, Windows 11, Python 3.14.7, NumPy 2.5.3)

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest tests/unit/test_calibration_engine.py tests/unit/test_calibration_chunks.py -q -p no:cacheprovider` | 26 passed |
| `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider` | 1812 passed, 9 skipped in 527.26s (0:08:47) |
| `.venv/Scripts/python.exe -m ruff check .` | all checks passed |
| `.venv/Scripts/python.exe -m ruff format --check .` | 128 files already formatted |
| `.venv/Scripts/python.exe -m mypy calibration` / `mypy src` / `mypy calibration src` | no issues (8 / 53 / 61 files) |
| `.venv/Scripts/lint-imports.exe` | 6 kept, 0 broken |
| `pwsh -NoProfile -File review/task6/verify_frozen.ps1` (pwsh from the Codex runtime path) | PASS: 28/28 trusted bytes, 14/14 sidecars, Constitution self-hash, 7/7 bindings, nested bindings |

These repairs have not been re-reviewed by a different model.

## D19CR-4 build (2026-10-05, Claude Opus 5.5; Codex attempts at capacity)

Built per `CODEX_BRIEF_RUNDEF.md`: `calibration/rundef.py` (reference-vector
suite of four fixed cases K = 1, 2, 5, 20 that reach method V's nominee and
the U_G gates, about 3.4 s; host provenance; gating identity measured after
method V's environment check; run definition build/write/load and hash;
generator-code hash; `start_gate` re-checking runtime identity, both canaries,
image digest and every reference vector), `scripts/d19_run_definition.py`
(`record`, `check`), `tests/unit/test_calibration_rundef.py` (record in one
fresh pinned process, check passes in another; wrong digest, changed canary,
changed reference vector each stop with U_ops; wrong record type refused;
generator hash covers every file).

Not yet done: wiring `start_gate` into a run driver that hands its gating to
`chunks.Chain` (the driver is a later item).

Checks: `pytest -q` 1818 passed, 9 skipped; `ruff format --check .` 131 files
formatted, `ruff check` clean; `mypy calibration src` 62 files clean;
`lint-imports` 6 kept; frozen verification PASS.
