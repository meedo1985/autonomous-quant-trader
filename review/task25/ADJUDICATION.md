# Task 25 review adjudication

## GPT-6 Astra review of `01f10ad`

Record: `ASTRA_REVIEW_01F10AD.md` (committed `a22dfac` before these repairs).
Repairs by Claude Opus 5.5.

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| A25-1 | AGREE — BLOCKER, repaired | Reproduced by reasoning from the committed logs: the clean run's next order after 2020-07-16 is on 2020-11-26, outside the 30-day window. The HALT drill now runs the full window and uses the clean run as its control: it requires the control to have an order after the HALT time and the HALT run to have none. | The reviewer's mutation (`may_trade` true in HALT) now fails the drill: "clean-run orders after that time 1 (2020-11-26T09:00); orders after HALT 1". |
| A25-2 | AGREE — BLOCKER, repaired | The loop now logs each FLATTEN sell as an ORDER event with `held_before`, `orig_qty`, `executed_qty` (also repairs T25-01). The drill checks every step from the log: at most the configured fraction of the holding before it, strictly hourly, chained (each step starts from what the last left), the remainder equals the final balance and is non-negative, at least two steps. The trace is committed as `drills/flatten/steps.json`. | The reviewer's mutation (`max_step_fraction` 1) now fails: "1 steps, largest share 1.0000". `test_an_owner_flatten_sells_everything_then_halts` asserts the logged steps. |
| A25-3 | AGREE — BLOCKER, repaired | The runner creates each drill directory with `exist_ok=False` and never unlinks a log; `main` refuses a non-empty `--out` (exit 2). The first committed outputs were removed with `git rm` and regenerated into a fresh directory; they stay in git history at `01f10ad`. | `test_drills_never_overwrite_earlier_evidence`: an existing drill directory raises and its file is untouched; `main` returns 2 on a non-empty output. |

The repairs touch `src/aqt/app/paper_loop.py` (one logged event), so they
are within section 16 scope and need re-review.

## Found by the implementer after the repairs

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| T25-03 | Repaired | Git warned that the committed ledgers would be checked out with CRLF under `core.autocrlf`. A CRLF copy of `drills/flatten/operations.jsonl` fails `verify_ledger` (LF intact: True; CRLF intact: False). `.gitattributes` now marks `/review/task25/drills/** -text`, as the frozen files already are. | `git check-attr text` reports `unset` for the drill ledgers. |

Follow-up: the drill script wrote JSON with the platform's line endings, so
its output differed by OS. It now writes LF line endings everywhere, and the committed
JSON files were converted to LF. A full rerun into a fresh scratch directory
matched every committed drill file byte for byte (`diff -r`: identical).
`tests/integration/test_drills.py`: 3 passed.

## Astra re-review attempts

- Attempt 1 (`ASTRA_REREVIEW_ATTEMPT_1.md`): stopped for low memory, no
  findings.
- Attempt 2 (`ASTRA_REREVIEW_ATTEMPT_2.md`, committed `7e49b08` before these
  repairs): cut off by the Codex usage limit before its final report, so no
  verdict. Before the cut-off it confirmed: both original mutations now fail;
  all 11 ledgers intact; all 31 drill files survive checkout byte for byte
  with `core.autocrlf=true` (T25-03); the replay reproduced all 20 evidence
  files; the packet matches the logs; a failed reconciliation freezes before
  another FLATTEN step; the zero-fill alert still fires; the no-overwrite
  rule preserved earlier incidents and `summary.json`.

| ID | Decision | Evidence and disposition | Validation |
| --- | --- | --- | --- |
| A25R-1 | AGREE — BLOCKER, repaired | My A25-2 repair replaced the remainder check instead of adding to it, so a FLATTEN that stopped after two valid half-steps (0.27477 BTC left) passed. The drill now requires both: every step bounded, hourly and chained, and the final remainder below twice the notional minimum at the window's lowest price. | Mutation "stop after 2 steps" now fails the drill (see validation below). |
| A25R-2 | AGREE — repaired | `held_before` came from the loop's reconciled record, which can differ from the venue balance `tick` sizes from when the tolerance is not zero. The loop now reads the venue balance immediately before `tick` and logs that. With the owner's zero tolerance the logged values are unchanged. | Drill rerun byte-identical (see below). |
| A25R-3 | NOT RECOVERABLE | Mentioned as a second "logging limitation" but never described before the cut-off. A completed re-review must restate it if it still holds. | — |

Validation of the A25R repairs: mutations HALT gate bypass, 100% FLATTEN
step and FLATTEN stopped after 2 steps each now fail their drill; a full
drill rerun into a fresh directory is byte-identical to the committed
evidence; `pytest -q` 1576 passed, 4 skipped; ruff, format, mypy (53 files),
6 import contracts, `git diff --check` clean; no frozen file changed. A
complete Astra re-review is still required.
