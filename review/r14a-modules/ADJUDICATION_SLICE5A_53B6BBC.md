# Adjudication: Sol review of confirmation slice 5a at 53b6bbc

- Review record: `SOL_CONFIRMATION_SLICE5A_53B6BBC.md` (gpt-6-sol, high, verdict FIX).
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-09. The adjudication is the
  author's and approves nothing. The repairs are in the commit that adds this file.

| ID | Sol | Decision | Repair |
|---|---|---|---|
| R14S5-S-1 | BLOCKER | **Accepted.** Status (a) trusted the caller's seeds. A wrong `estimator_seed` gave (a), and then the lockbox refused the artifact. | `seal_family` now recomputes `seed_l266` through the loaded line 266 from the trial record's hypothesis hash and index. It requires the seed record's index, `seed_l266`, policy and `estimator_seed` (an int equal to `screen.estimator_seed(seed_l266)`) to match. Any mismatch, or line 266 not loaded, gives `SealError`, which yields status (d). Tests cover a wrong index, `seed_l266`, policy, seed+1, a bool seed, and line 266 not loaded. |
| R14S5-S-2 | BLOCKER | **Accepted, in a narrower form.** `check_declaration` lets a non-eligible window declare one family, so the binding is "exactly the declared families", not "both". | `sealing_record(..., declared)` refuses unless the entries' families equal the declared set (non-empty, known families). Tests cover a missing family, an extra family, an unknown family, and an empty record. |
| R14S5-S-3 | BLOCKER (lockbox contract) | **Accepted.** | `c2_lockbox._check_shape` now checks values as well as keys, before any read: `source.window_id` must be a str; `source.n` a non-bool int ≥ 2; `d_sha256`, `evaluation_record_sha256` and `psi_sha256` 64 lowercase hex characters; `block.value` a hexf, finite and ≥ 1; `block.raw` None or a finite hexf; `clipping` one of None, LOWER, UPPER. Eleven negative tests run through the lockbox's own checks. |
| R14S5-S-4 | BLOCKER (test gap) | **Accepted.** | New test: a model nominee with an overlay at estimator seed 12345. Every fit gets seed 12345, d equals an independent write-out (walk-forward at that seed, model column held daily, fresh overlay), and removing the overlay changes d. |
| R14S5-S-5 | NON-BLOCKING | **Accepted.** | A seed record without the family (or without `family_seed`) now raises `CycleError`: a seed-derivation failure, which invalidates the evaluation, not status (d). Failures after that point while sealing stay (d). LG5-5 is narrowed accordingly. Tested. |

LG5-1 now reads: the sealing record covers exactly the declared families (S-2). LG5-5 now
reads: "any failure while sealing an ELIGIBLE nominee, after the family's seed entry is
read, gives (d)" (S-5).

Validation after the repairs (5a and 5b together): 327 passed
(`pytest tests/unit/test_c2_confirmation*.py tests/unit/test_c2_lockbox*.py
tests/unit/test_d19_deploy.py`); ruff format and check are clean; `mypy src` is clean;
strict mypy shows only the 10 pre-existing errors in `test_calibration_screen.py`;
lint-imports reports 7 contracts kept. Sol re-check: one round, with 5b's.

## Re-check (SOL_CONFIRMATION_SLICE5_RECHECK_775A3E4.md, verdict FIX)

Sol closed R14S5-S-1, -2, -4 and -5, and R14S5B-S-1 and -3. It found R14S5-S-3 partly closed, and accepted R14S5B-S-2 as an open owner/S4 item (LG5B-7).

| ID | Sol | Decision | Repair |
|---|---|---|---|
| R14S5R-S-1 | BLOCKER | **Accepted.** The pre-read check had no upper bound on `block.value`, while A4 requires `1 <= b <= n`. | `_check_shape` now requires `1 <= value <= source.n`. New negative test: `value = 121` with `n = 120`. The degenerate `raw = 0.0` stays accepted, as Sol confirmed. |

Validation: 328 passed (same suites); ruff is clean; strict mypy is clean on `c2_lockbox.py`. Not re-sent to Sol: the change adds one bound, at the exact line Sol named. A further round is available on request.
