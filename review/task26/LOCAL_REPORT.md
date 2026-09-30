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


## Fable review of `ea14844` and repairs

Record: `FABLE_REVIEW_EA14844.md` (committed `2c19fa7` before these repairs;
verdict FIX). The reviewer disclosed one real, key-free request to
`/api/v3/time` it made against instructions (F26-4 below); reported to the
owner.

| ID | Decision | Disposition | Validation |
| --- | --- | --- | --- |
| F26-1 | AGREE — BLOCKER, repaired | A bar counts as closed only when it has ended on both clocks: the cutoff is `min(local now, Binance server time)`. A local clock ahead by up to 5 s can no longer store the forming hour. | `test_a_local_clock_ahead_never_stores_the_forming_bar` (reviewer's scenario) |
| F26-2 | AGREE — repaired | A torn or edited store line raises `LiveBarError` naming file and line; the CLI exits 2. | `test_a_torn_store_line_is_a_named_refusal` |
| F26-3 | AGREE — repaired | `LIVE_START_FLOOR` = 2026-09-01T00:00Z, the first hour after the protocol's lockbox partition: a start inside confirmation or lockbox data is refused before any request. This applies the frozen partition rule; it is not a new owner choice. | `test_the_store_never_starts_in_restricted_data` (lockbox, confirmation, last lockbox hour) |
| F26-4 | AGREE — repaired | Symbol, start (UTC, floor) and the empty-store rule are checked before any request; the CLI maps network errors (`OSError`, incl. `URLError`, timeouts) to exit 2. | `test_a_bad_start_is_refused_before_any_request`, `test_the_cli_turns_network_errors_into_a_refusal` |
| F26-5 | AGREE — repaired | A committed fixture (`tests/fixtures/live/klines_btcusdt_1h.json`, synthetic, in Binance's documented row format; no real reply is recorded because the AI makes no call) replays into a store byte-identical to `expected_store.jsonl`. Fixture files are byte-exact across checkouts (`.gitattributes`). | `test_the_committed_fixture_replays_byte_identically` |
| F26-6 | AGREE — disclosed (T26-04) | See below. | — |
| F26-7 | AGREE — disclosed (T26-05) | See below. | — |

Each F26-1..F26-4 test fails on `ea14844` (7 failures) and passes after.

- **T26-04. A real Binance gap stops the store for good** (F26-6). Refusing
  is correct under §6, but there is no recovery yet. Task 27 (persistent
  state) should add an owner-acknowledged gap record; until then the owner
  would start a new store after the gap.
- **T26-05. The library does not refuse key variables itself** (F26-7); the
  CLI does, and `PublicRequest` blocks any key, signature or auth header from
  being sent. Future app code calling `fetch_new_bars` directly must call
  `refuse_credentials` first (Task 28/30).

Validation after the F26 repairs: `pytest -q` 1599 passed, 4 skipped;
ruff, format (104 files), mypy (55 files), 6 import contracts and `git diff
--check` clean; no frozen file changed. Not yet re-reviewed.

## Astra review of `3b9a006` (text-only) and repairs

Record: `ASTRA_REVIEW_3B9A006.md` (committed `b9f602f`). The Codex sandbox
cannot start on the owner's Android/proot machine, so the reviewer read
attached texts and ran nothing. F26-1, F26-2, F26-5 correct; F26-3, F26-4
incomplete (A26-3, A26-5); F26-6, F26-7 disclosures adequate. Verdict FIX.

| ID | Decision | Disposition | Validation |
| --- | --- | --- | --- |
| A26-1 | AGREE — BLOCKER, repaired | `append` takes the Task 10 ledger's cross-process lock file (`<store>.lock`, `aqt.core.ledger._exclusive_lock`, Windows and POSIX) and re-reads the store under it, so a writer with a stale view is refused as a duplicate. A lock not acquired within the ledger's timeout refuses the append. | `test_a_stale_second_writer_is_refused_under_the_lock`, `test_an_append_waits_for_the_lock_and_then_refuses` |
| A26-2 | AGREE — BLOCKER, repaired | A store is bound to one allow-listed symbol (`LiveBarStore(path, symbol)`); every row records it, reading refuses a row of another symbol, and `fetch_new_bars` refuses a different symbol before any request. `series()` takes no symbol. Stored format change: rows gain `"symbol"`; `expected_store.jsonl` regenerated accordingly. | `test_one_store_never_mixes_symbols` (reviewer's scenario) |
| A26-3 | AGREE — BLOCKER, repaired | Reading checks the whole file: the first bar not before `LIVE_START_FLOOR`, each later bar exactly one hour after the previous (no gap, duplicate or reordering), each refusal naming the line. A damaged history therefore refuses before any request, and `append` refuses a restricted first bar with or without `first`. | `test_the_whole_stored_history_is_checked` (gap, duplicate, out of order, last lockbox hour), `test_append_refuses_a_first_bar_in_restricted_data` |
| A26-4 | AGREE — repaired | A non-empty store not ending in a newline is refused ("no final newline"), so nothing is appended onto a cut-off row. | `test_a_row_without_its_newline_is_refused_before_any_append` |
| A26-5 | AGREE — repaired | `start` must be hour-aligned (`require_aligned_utc`) before any request. | `test_an_unaligned_start_is_refused_before_any_request` |

The new tests use the new store signature, so they cannot run unchanged on
`3b9a006`; each covers the reviewer's scenario as written.

Validation after the A26 repairs (Python 3.14.4, Linux aarch64 proot):
`pytest -q` 1609 passed, 4 skipped; ruff, format, mypy, 6 import contracts
and `git diff --check` clean; no frozen file changed. Not yet re-reviewed.
