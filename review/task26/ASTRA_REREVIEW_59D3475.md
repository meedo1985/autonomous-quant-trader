# Task 26 Astra re-review of the A26 repairs at `59d3475` — text-only (ACCEPT)

Date: 2026-09-30. Requested by the owner ("Ok contenue with 1 and 2").

- Invocation: `codex exec -s read-only -m gpt-6-astra -` (codex-cli 0.154.0).
- **Text-only**, as for `ASTRA_REVIEW_3B9A006.md`: the sandbox cannot start
  on this machine. Attached verbatim from `59d3475`: that record,
  `LOCAL_REPORT.md`, `live_bars.py`, `fetch_live_bars.py`,
  `test_live_bars.py`, `expected_store.jsonl`, `ledger.py`, `bars.py`,
  `pyproject.toml`, and `git diff 3b9a006 59d3475 -- src tests scripts`.
  Prompt bundle SHA-256: `72c982cd71d401edae57bdec25fee9480596c93c95cb0c06e47fbaa19bd67feb`.
- Orchestrator's run of the reviewer's proposed command below at `59d3475`
  (Python 3.14.4, Linux aarch64): exit 0, `10 passed in 0.67s`. Not run on Windows; no
  cross-process race or crash test was executed (as the reviewer notes).
- The reviewer's final message follows verbatim.

---

**Verdict: ACCEPT — text-only repair review.**

Reviewer: **GPT-6 Astra**, independent different-model reviewer; implementer: Claude Opus 5.5.

Reviewed state: attached texts identified as **59d3475**, branch `task26-live-public-bars`, draft PR **#36**, including the supplied diff from `3b9a006`. Commit identity and repository contents were not independently verified.

No commands, network calls, edits, commits, credentials, or confirmation/lockbox data access occurred. The sandbox is reported unavailable because bubblewrap exits 182. Required skill texts were not attached; their procedures were not executed. This message is the review record; I have not committed it.

The orchestrator reports **1609 passed, 4 skipped**, with ruff, format, mypy and six import contracts clean. **These results were not verified by me.**

| Finding | Assessment | Evidence and independent scenario |
|---|---|---|
| **A26-1** | **CORRECT** | `live_bars.py:181–187` acquires the sidecar lock before rereading history and holds it through validation, write, flush and fsync. If two fetchers observe the same last hour and fetch overlapping batches, the second appender rereads the first writer’s committed history and rejects its overlapping first bar before writing. This also covers concurrent initialization of a missing store. |
| **A26-2** | **CORRECT** | Constructor validation, the required per-row symbol, read-time equality checks, and the fetch-time symbol check close both entry paths. Independently constructing `LiveBarStore(existing_btc_path, "ETHUSDT")` cannot bypass the binding: its first read rejects the BTC row, including when that read occurs inside `append`. `series()` no longer accepts a replacement label. |
| **A26-3** | **CORRECT** | `bars()` checks every row through `Bar` and `_require_next`; `_append_locked` checks the first incoming bar against the floor even when `first` is supplied. A history `00:00, 02:00, 03:00` now fails at row 2 despite its valid final pair. Duplicates and reversals fail similarly. A restricted first row fails before resume can reach the transport. |
| **A26-4** | **CORRECT** | `live_bars.py:134–138` rejects a nonempty decoded store without a terminating newline. A complete final JSON object missing only its LF is refused during the locked reread, before opening the store for append. Existing bytes remain untouched. An empty file remains a valid empty store. |
| **A26-5** | **CORRECT** | `live_bars.py:275` calls `require_aligned_utc` before `_get`. This rejects seconds and microseconds as well as the reported half-hour offset. On a populated store, `start` remains unused; the effective resume timestamp comes from validated hourly history. |

The lock implementation supports the repair as written:

- **POSIX:** separately opened descriptors contend through exclusive nonblocking `flock` on the same sidecar. The data file need not exist when locking begins.
- **Windows:** each attempt seeks to offset zero and requests a one-byte `msvcrt.LK_NBLCK` lock. A byte-range lock can extend beyond EOF, so an empty sidecar does not require a sentinel byte. Unlocking seeks back to zero.
- **Timeout:** unsuccessful acquisition retries against a monotonic deadline, ordinarily 120 seconds. Expiry raises `LedgerError` before entering `_append_locked`; `append` converts it to `LiveBarError`. The descriptor closes on this path.
- **Crash:** the OS releases the held lock when the process’s handle closes. The surviving `.lock` file is reusable; its mere existence does not indicate ownership. The implementation correctly leaves it in place.
- **Scope:** this protects cooperating writers using the same sidecar. It does not make an entire multi-page fetch transactional. Readers outside `append` remain unlocked and can transiently refuse an incomplete in-progress write; the locked reread prevents that observation from authorizing a corrupt append.

The supplied stale-writer test is sequential, and the timeout test holds a competing descriptor in the same process. They support the intended behavior but **do not constitute an executed cross-process race or crash-recovery test**, nor does the reported Linux run verify the Windows branch.

The format change is acceptable for this first, unmerged store implementation. Every **nonempty legacy store containing rows without `symbol`** now fails with a named missing-field refusal. Missing and empty files remain usable. Refusing legacy rows avoids guessing their symbol. The supplied fixture diff adds the sorted `"symbol"` field without changing its OHLCV values or timestamps. I cannot independently establish byte-identical replay from these attachments because the input kline fixture is not included here.

Whole-history validation establishes the requested floor, gap, duplicate and ordering properties. Blank or malformed rows also refuse; nothing is silently skipped or repaired. Its cost is **O(n) time and memory per read**. A successful single-page append through `fetch_new_bars` ordinarily scans history three times: initial resume, locked validation, and final result. Repeated hourly appends therefore incur quadratic cumulative scanning as history grows. This is a disclosed scaling consideration, not a demonstrated Task 26 blocker; the supplied material provides no measured performance failure.

The private import at `live_bars.py:27` creates this dependency:

`aqt.data.live_bars → aqt.core.ledger → aqt.data.manifest`

None of the supplied import contracts categorically prohibits `aqt.data` importing `aqt.core`. That path alone does not demonstrate a module import cycle. Reusing `_exclusive_lock` introduces coupling to a private helper, but no concrete import failure is established by the attachments. I would not require a shared-lock-module refactor solely to approve these repairs.

**New findings A26-6 onward: none.** No new blocker is demonstrated by the supplied repair text.

The following exact command targets the attached repair tests. **Not reproduced (sandbox unavailable).** It is a proposed command only; these tests use synthetic values and their socket-blocking fixture.

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/unit/test_live_bars.py::test_a_stale_second_writer_is_refused_under_the_lock \
  tests/unit/test_live_bars.py::test_an_append_waits_for_the_lock_and_then_refuses \
  tests/unit/test_live_bars.py::test_one_store_never_mixes_symbols \
  tests/unit/test_live_bars.py::test_the_whole_stored_history_is_checked \
  tests/unit/test_live_bars.py::test_append_refuses_a_first_bar_in_restricted_data \
  tests/unit/test_live_bars.py::test_a_row_without_its_newline_is_refused_before_any_append \
  tests/unit/test_live_bars.py::test_an_unaligned_start_is_refused_before_any_request
```

**ACCEPT** applies to the five repairs by source inspection. It does not certify executed platform validation, complete the repository’s mandatory task gate, or authorize merge.