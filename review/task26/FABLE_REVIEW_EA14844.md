# Task 26 adversarial review of `ea14844` (Claude Fable 5.1)

Date: 2026-09-29. Requested by the owner ("let fable make a review").

- Reviewer model: Claude Fable 5.1 (`claude-fable-5-1`), read-only subagent.
  Same provider family as the implementer (Claude Opus 5.5).
- Reviewed commit: `ea14844` (`task26-live-public-bars`, draft PR #36),
  `git diff 162e5ea ea14844`.
- Reviewer's tests: `tests/unit/test_live_bars.py`, 15 passed.

## Process breach disclosed by the reviewer

The reviewer was told to make no network call. Once, checking how the CLI
handles a naive `--start`, it called `fetch_live_bars.main([... '--start',
'2026-09-29T00:00:00'])` with the real transport and sockets not blocked.
`fetch_new_bars` fetches server time before it validates `start`, so one
unauthenticated GET to `https://data-api.binance.vision/api/v3/time` almost
certainly succeeded before `BarSemanticsError`. No klines were requested, no
credential was involved, no file was written. This contradicts owner answer
Q-A ("the AI itself would never make these calls"); it is reported to the
owner. The same observation is F26-4.

## Findings (substance recorded in full)

### F26-1 — BLOCKER — a forming bar can be stored as closed

`live_bars.py:81` (`if close_ms >= now_ms`) with lines 200-209 and
`fetch_live_bars.py:42` (`datetime.now(UTC)`): the cutoff uses the local
clock, which S-5 allows to be up to 5 s ahead of Binance. In the last <=5 s
of an hour the server still serves the hour as forming while the code treats
it as closed, and the partial bar is appended permanently. A scheduler at
hh:00:00 on a PC 1-5 s fast hits exactly this. T26-02 disclosed only the
harmless direction. Reproduced (fake transport, sockets blocked): server
04:59:57, local = server + 4 s: "skew 0:00:04 appended 5 last 2026-09-29
04:00:00+00:00 … last bar closes 2026-09-29 05:00:00+00:00". Fix: cutoff
`min(local now, serverTime)`; test local ahead by 1-5 s at an hour's end.

### F26-2 — NON-BLOCKING — a torn or edited store line gives a raw traceback

`LiveBarStore.bars` (`live_bars.py:109-125`) catches nothing; the CLI catches
only `DownloadError`/`LiveBarError`: a torn last line after a crash raises
`JSONDecodeError`, exit 1 not 2, without naming file or line; the store is
unusable until repaired by hand. Fails closed. Reproduced. Fix: raise
`LiveBarError` with path and line number.

### F26-3 — NON-BLOCKING — `--start` has no floor

The owner could start the store inside confirmation or lockbox periods
(protocol: confirmation 2022-01-01..2025-05-31, lockbox
2025-06-01..2026-08-31), writing restricted-period bars into a store later
code and AI sessions may read. Task 13 refuses non-exploration months; this
path does not. Reproduced (fake transport): start 2025-06-01 appended 3
bars. Fix: refuse a start before 2026-09-01T00:00:00Z, or an explicit owner
decision.

### F26-4 — NON-BLOCKING — validation after a network call; errors escape

An invalid `start` is checked only after the `/api/v3/time` request, and
`BarSemanticsError`, `URLError`, `TimeoutError`, `OSError` escape the CLI as
tracebacks (exit 1). Reproduced (the breach above). Fix: validate `start` and
the empty-store condition before any request; map transport errors to a
refusal.

### F26-5 — NON-BLOCKING — acceptance wording weakened, not tested

The roadmap says "a recorded fixture replays byte-identically"; the report
says "deterministically"; the tests use a generated fake and compare values,
not bytes. Byte identity held in the reviewer's probe but no committed test
proves it. Fix: a committed fixture and a byte comparison, or honest wording.

### F26-6 — QUESTION — a real Binance gap blocks the store forever

Binance has had missing 1h klines during halts; a gap after the last bar
makes every later run refuse, with no documented recovery. Correct under §6,
but an operability dead end for the owner or Task 27 to resolve; disclose.

### F26-7 — NON-BLOCKING — the library does not refuse key variables

`fetch_new_bars` does not call `refuse_credentials`; only the CLI does. No
credential can be sent anyway (`PublicRequest` guard). By reading.

## Checked and sound

Pagination (limit 1000, break below 999, no loop, no skipped or repeated
page); exact ms/datetime conversion; row format matches Binance's documented
klines row with closeTime = openTime + 3,599,999; skew check sign, units,
before any klines request; duplicates, out-of-order and gaps refused, and a
concurrent run is refused rather than duplicated; tests offline.

## Verdict

FIX (F26-1 must be repaired; F26-3's floor should be decided before the
first real run).
