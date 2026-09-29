# Tasks 23-24 post-merge review: adjudication

Record: `ASTRA_REVIEW_1E02472.md` (committed `6450768` before these repairs).
Also repairs Task 25's A25R-4 (`review/task25/ASTRA_REREVIEW_9727496.md`),
which touches the same loop. Repairs by Claude Opus 5.5 on branch
`review/task23-24-astra-postmerge`.

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| A2324-1 | AGREE — BLOCKER, repaired | `reconcile` resolved an order whose outcome was unknown to "absent" on its first NOT_FOUND, with no delayed re-query (§21). New `AbsenceCheck(delay, queries, sleep)`: such an order is confirmed absent only after `queries` NOT_FOUND answers, `delay` apart. Without an `AbsenceCheck` the order stays unresolved (fail closed). `startup_check` accepts it; the paper loop passes the owner-set executor values (T22-Q1: 10 s, 2 answers) on its simulated clock at startup, after executor orders, and after FLATTEN steps. A known order (local copy) that returns NOT_FOUND is still a difference at once. | `test_one_not_found_never_resolves_an_unknown_order` (no check: unresolved, FREEZE kept); `test_a_lagging_not_found_is_queried_again_after_the_delay` (the reviewer's scenario with one lagging NOT_FOUND: the delayed query finds the expired order, one 10 s wait). Three existing tests now pass the check explicitly. |
| A2324-2 | AGREE — BLOCKER, repaired | The loop still required `held >= min_qty` before firing LOSS_STOP, so a dust account breached silently (incomplete F24R-1). The condition is removed; the latch still limits the stop to once per fall. From RUNNING a dust holding enters FLATTEN, which ends at once in HALT (no sellable step). | `test_a_breach_on_a_holding_too_small_to_sell_still_alerts` (reviewer's scenario: 0.000009 BTC, owner HALT, 30%+ fall: one CRITICAL LOSS_STOP, no order). |
| A2324-3 | AGREE — repaired | `load_config` ignored `max_notional`. It now reads it when present; absent means none. | `test_the_configuration_reads_the_maximum_notional`. |
| A2324-4 | AGREE — repaired | A malformed `FROZEN_HASHES.json` raised before the alert router existed. The parse is guarded; `frozen_hash_problems` then refuses the start through the logged REFUSE_START path and the report names the hashes "unreadable". | `test_a_malformed_frozen_manifest_is_a_logged_refusal`. |
| A25R-4 | AGREE — repaired | A FLATTEN sell whose reply was lost was not logged as an ORDER nor counted. The loop now logs every new FLATTEN id without a returned order as `ORDER` `state FLATTEN_UNKNOWN` (CRITICAL) with the holding it was sized from, and counts it. | `test_a_flatten_sell_with_a_lost_reply_is_logged_and_counted`. |

Each new test fails on `main` before these repairs (the two `test_safety.py`
tests cannot import there, since `AbsenceCheck` did not exist) and passes
after.

Validation (Windows 11, `.venv` Python 3.14): `pytest -q` 1582 passed, 4
skipped; `ruff check .` and `ruff format --check .` clean (101 files);
`mypy src scripts` no issues (53 files); `lint-imports` 6 kept; `git diff
--check` clean; no frozen file differs from `main`. The Task 25 drills rerun
into a fresh directory are byte-identical to the committed evidence, so the
repairs change no drill outcome.

These repairs touch section 16 protected code (reconciliation, safety,
loop) and need an Astra review and the owner's behavioural review before
merge.
