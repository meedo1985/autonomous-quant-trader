# Task 26 local report: live public market data (no keys)

Date: 2026-09-29. Coding AI: Claude Opus 5.5 (`claude-opus-5-5`).
Branch `task26-live-public-bars` from `main` `162e5ea`. Authorized by the
owner's roadmap 2 answers (`review/roadmap/ROADMAP_2_OWNER_ANSWERS.md`):
Q-A (the app may read Binance's public live prices; the AI never makes these
calls) and Q-D (Tasks 26, 27, 28, 30 in order).

## What changed

| File | Change |
| --- | --- |
| `src/aqt/data/live_bars.py` (new) | `parse_klines`, `LiveBarStore`, `fetch_new_bars` |
| `scripts/fetch_live_bars.py` (new) | Owner/app-run CLI: refuses with a Binance key variable set; S-5 5 s skew limit |
| `tests/unit/test_live_bars.py` (new) | 15 tests, fake transport, sockets blocked |

## Behaviour

- Requests go only through the Task 13 `PublicRequest` guard: HTTPS to
  `data-api.binance.vision`, no key, signature or auth header; redirects
  refused. Endpoints: `/api/v3/time` and `/api/v3/klines` (1h, BTCUSDT or
  ETHUSDT only).
- The clock is checked against Binance's server time first; more than 5 s
  either way (owner setting S-5) fetches nothing.
- Each row must be an integer-timed bar spanning exactly its hour and pass the
  `aqt.data.bars` checks. The last row may be the hour still forming, which is
  dropped; an unclosed bar anywhere else, or any irregular closed bar, is
  refused, never skipped.
- The store is an append-only JSON-lines file, fsynced. Each batch must start
  exactly where the store ends (or at `--start` on an empty store) and run
  hour after hour; a gap, duplicate or out-of-order bar refuses the whole
  batch, and nothing is filled or corrected (Constitution §6). Pages of 1000
  are fetched until the latest closed bar.

## Acceptance (roadmap 2 Task 26)

| Criterion | Evidence |
| --- | --- |
| A recorded reply replays deterministically | `test_a_fresh_store_gets_every_closed_bar_and_not_the_forming_one`, `test_a_second_fetch_resumes_after_the_last_bar`, `test_more_than_one_page_is_fetched_in_order` |
| A gap, a duplicate and an out-of-order bar are each refused | `test_a_gap_in_the_reply_appends_nothing`, `test_a_gap_at_the_start_is_refused`, `test_duplicates_and_out_of_order_bars_are_refused` |
| Irregular or unclosed bars refused | `test_an_irregular_closed_bar_is_refused_not_skipped` (4 cases), `test_an_unclosed_bar_before_the_last_row_is_refused` |
| Clock skew refused | `test_a_skewed_clock_fetches_nothing` (+6 s, −6 s) |
| No credential is read | Requests carry no key or header (first test); `test_the_cli_refuses_while_a_key_variable_is_set` |

Mutation checks: removing the gap check fails 3 tests; removing the skew
check fails 2; keeping the forming bar fails 3.

## Disclosed limits

- **T26-01.** The store is plain JSON lines, not hash-chained; it is
  append-only by code, not tamper-evident. Raw replies are not archived.
  Proposed for Task 27 (persistent state), if the owner wants it.
- **T26-02.** A bar's `close_time` is Binance's `openTime + 1h − 1 ms`; a
  reply whose server time is ahead of the local clock by less than 5 s could
  still include a bar that closed on the server a moment before it closed
  locally. It is a closed bar either way.
- **T26-03.** Nothing runs on a schedule yet; the CLI appends on demand. The
  loop does not read the store yet (Task 29, not authorized).
- No live call was made during this task, by the AI or anyone. The first real
  run is the owner's.

## Validation

Windows 11, `.venv` Python 3.14:

| Command | Result |
| --- | --- |
| `pytest -q` | 1591 passed, 4 skipped in 262.01s |
| `ruff check .` / `ruff format --check .` | clean / 104 files formatted |
| `mypy src scripts` | no issues in 55 source files |
| `lint-imports` | 6 kept, 0 broken |
| `git diff --check` | clean; no frozen file differs from `main` |
