# Task 26 Astra review of `3b9a006` — text-only (FIX; A26-1..A26-3 blockers)

Date: 2026-09-30. Requested by the owner ("Yes do the review now with astra").

- Invocation: `codex exec -s read-only -m gpt-6-astra -` (codex-cli 0.154.0,
  log header `model: gpt-6-astra`), prompt `review/handoff/ASTRA_PROMPT_PR36.md`
  plus an output section and attachments.
- **Text-only review.** On this machine (Android/proot) the Codex sandbox
  cannot start (bubblewrap exits 182). With the owner's choice the
  orchestrator (Claude Opus 5.5) kept `-s read-only` and attached, verbatim
  from `3b9a006`: `AGENTS.md`, `review/roadmap/ROADMAP_2_OWNER_ANSWERS.md`,
  the three `review/task26/` records, `src/aqt/data/live_bars.py`,
  `scripts/fetch_live_bars.py`, `tests/unit/test_live_bars.py`, both
  `tests/fixtures/live/` files, `.gitattributes`, `src/aqt/data/binance_public.py`,
  `src/aqt/data/bars.py`, the Constitution, and `protocols/protocol_v1.yaml`
  lines 55-80. Prompt bundle SHA-256: `803461345d4f582b9768fde220f15cbbcd5d045062779f2a196d549fdb771bb2`.
- The reviewer ran no command; every reproduction below is "not reproduced
  (sandbox unavailable)".
- The reviewer's final message follows verbatim.

---

**Verdict: FIX**

Reviewer: **GPT-6 Astra**, independent different-model reviewer; implementer recorded as Claude Opus 5.5.

Reviewed state: supplied texts identified as **3b9a006**, branch `task26-live-public-bars`, draft PR #36, intended comparison base `162e5ea`. **Text-only review:** no commands, network calls, file changes, or data access occurred. Commit identity, actual diff, and reported test results were not independently verified. Required skill texts were unavailable; their procedures were not executed.

Locations below identify lines in the supplied `live_bars.py` text.

### Previous findings

| Finding | Assessment | Reason |
|---|---|---|
| F26-1 | **CORRECT** | `min(now, server_now)` prevents storing the reported forming bar. Integer-millisecond comparison excludes the final millisecond until the hour ends. |
| F26-2 | **CORRECT** | Malformed JSON and the listed field/`Bar` validation failures become `LiveBarError` with path and line. This repairs the reported torn-JSON scenario; a separate append-boundary defect remains in A26-4. |
| F26-3 | **INCOMPLETE** | Fresh fetches enforce the floor before requesting data. Existing history is not checked, and public `append` accepts restricted-period bars. See A26-3. |
| F26-4 | **INCOMPLETE** | Naive/non-UTC starts and the empty-store condition are checked first; `OSError` transport failures are handled. Hour alignment is not checked before requests. See A26-5. |
| F26-5 | **CORRECT** | The committed synthetic fixture is compared against expected bytes across two stores; `.gitattributes` preserves fixture bytes. This establishes synthetic replay, not a recorded real-response replay, which the report explicitly discloses. |
| F26-6 | **Disclosure adequate** | A missing hour prevents subsequent appends. Starting another store preserves the discontinuity only if consumers retain and respect that boundary; gap recovery remains deferred. |
| F26-7 | **Disclosure accurate** | The library omits the environment credential refusal. The CLI checks it, and these generated requests contain no credentials. This review found no concrete secret-value leakage in the attached live-fetch path. |

### New findings

**A26-1 — BLOCKER — concurrent appenders can write duplicate bars**
`src/aqt/data/live_bars.py:152` and `:187`, `LiveBarStore.append`.

The last-bar read, continuity validation, and write have no shared lock or atomic conflict check. Two callers can both observe an empty store, validate the same batch, and append it twice. Both calls succeed. `fsync` does not prevent this race.

The prior review’s statement that concurrent runs are refused is therefore incorrect. The attached tests exercise sequential duplicate appends only.

Reproduction: case A26-1 in the command below. **Not reproduced (sandbox unavailable)**; confirmed by tracing the interleaving.

**A26-2 — BLOCKER — one store can silently combine BTCUSDT and ETHUSDT**
`src/aqt/data/live_bars.py:170`, serialized fields; `:223`, symbol validation.

The symbol is allow-listed but never bound to the store. Fetch BTC into a file, then invoke the CLI with the same file and `--symbol ETHUSDT`. ETH bars starting at the next hour pass continuity checks and are appended to BTC history. `series("BTCUSDT")` then labels the entire mixed history BTCUSDT without detecting the change.

Reproduction: case A26-2 below. **Not reproduced (sandbox unavailable)**; traced through both fetches.

**A26-3 — BLOCKER — existing store history bypasses sequence and restricted-period checks**
`src/aqt/data/live_bars.py:116`, `LiveBarStore.bars`; `:225–240`, resume/floor checks.

Reading validates individual bars only. It does not validate historical uniqueness, ordering, continuity, or the floor. Fetching uses only the last row.

Concrete scenarios:

- A file containing hours `00:00, 02:00` accepts `03:00` and reports success, retaining its gap.
- A file containing duplicate `00:00` rows accepts `01:00`.
- A store ending at `2026-08-31T23:00Z` resumes at the permitted floor, retaining its restricted-period bar. A file produced before F26-3’s repair can therefore bypass the intended restriction.

Public `append` also permits that restricted initial bar. Checking only the next requested hour does not establish that restricted data never enter the live store.

Reproduction: case A26-3 below. **Not reproduced (sandbox unavailable)**; traced through read and resume.

**A26-4 — NON-BLOCKING — missing final newline corrupts the next successful append**
`src/aqt/data/live_bars.py:120` and `:188`.

A partial write that ends immediately after the last JSON `}` leaves a valid JSON object without its terminating newline. `splitlines()` accepts it. The next append concatenates another object onto that same line, returns successfully, and leaves a store that subsequently fails JSON parsing.

This fails closed on the subsequent read, but the writer should refuse the incomplete record boundary before adding bytes.

Reproduction: case A26-4 below. **Not reproduced (sandbox unavailable)**; traced through `splitlines()` and append mode.

**A26-5 — NON-BLOCKING — unaligned start performs requests before inevitable refusal**
`src/aqt/data/live_bars.py:232`, start validation.

`--start 2026-09-29T00:30:00Z` passes UTC and floor checks. The code requests server time and klines. A normal reply starting at `01:00` then raises a gap error because `first` remains `00:30`.

This contradicts “Every input is checked before any request.” Validate alignment with the existing bar-semantics helper before calling the transport.

Reproduction: case A26-5 below. **Not reproduced (sandbox unavailable)**; traced through validation and fetch.

### Exact proposed reproduction command

**Not reproduced (sandbox unavailable). No command output is claimed.** This command uses synthetic values, blocks socket creation before importing project code, and removes its temporary files through `TemporaryDirectory`. Assertions describe the predicted defective behavior.

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
import socket

def forbidden(*args, **kwargs):
    raise AssertionError("network access attempted")

socket.socket = forbidden
socket.create_connection = forbidden

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier
from urllib.parse import parse_qs, urlsplit

from aqt.data.bars import Bar
from aqt.data.binance_public import FetchResponse
from aqt.data.live_bars import (
    LIVE_START_FLOOR, TIME_URL, LiveBarError, LiveBarStore, fetch_new_bars,
)

T = datetime(2026, 9, 29, tzinfo=UTC)
H = timedelta(hours=1)
S = timedelta(seconds=5)

def bar(t, price=100.0):
    return Bar(t, price, price, price, price, 1.0)

def ms(t):
    return int(t.timestamp() * 1000)

def exchange(times, now, price=100.0):
    calls = []
    def reply(request):
        calls.append(request.url)
        if request.url == TIME_URL:
            body = {"serverTime": ms(now)}
        else:
            start = int(parse_qs(urlsplit(request.url).query)["startTime"][0])
            body = [
                [ms(t), str(price), str(price), str(price), str(price),
                 "1.0", ms(t) + 3_599_999]
                for t in times if ms(t) >= start
            ][:1000]
        return FetchResponse(200, json.dumps(body).encode())
    return reply, calls

def record(t):
    return json.dumps({
        "open_time": t.isoformat(),
        "open": 100.0, "high": 100.0, "low": 100.0,
        "close": 100.0, "volume": 1.0,
    }) + "\n"

with TemporaryDirectory() as directory:
    root = Path(directory)

    # A26-1: force two writers to finish reading before either writes.
    barrier = Barrier(2)
    class RacingStore(LiveBarStore):
        def last_open_time(self):
            last = super().last_open_time()
            barrier.wait(timeout=10)
            return last

    path = root / "race.jsonl"
    writers = [RacingStore(path), RacingStore(path)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(w.append, (bar(T),)) for w in writers]
        for job in jobs:
            job.result()
    assert [b.open_time for b in LiveBarStore(path).bars()] == [T, T]

    # A26-2: change the requested symbol while retaining the same store.
    store = LiveBarStore(root / "mixed.jsonl")
    btc, _ = exchange([T], T + H, 65000.0)
    fetch_new_bars(btc, store, "BTCUSDT", T + H, S, start=T)
    eth, _ = exchange([T + H], T + 2 * H, 3000.0)
    fetch_new_bars(eth, store, "ETHUSDT", T + 2 * H, S)
    assert [b.close for b in store.series("BTCUSDT").bars] == [
        65000.0, 3000.0,
    ]

    # A26-3: existing gaps and duplicates survive successful fetching.
    for name, history, next_time in [
        ("gap", [T, T + 2 * H], T + 3 * H),
        ("duplicate", [T, T], T + H),
    ]:
        path = root / (name + ".jsonl")
        path.write_text("".join(record(t) for t in history), encoding="utf-8")
        store = LiveBarStore(path)
        fake, _ = exchange([next_time], next_time + H)
        result = fetch_new_bars(
            fake, store, "BTCUSDT", next_time + H, S,
        )
        assert result.appended == 1
        assert [b.open_time for b in store.bars()] == history + [next_time]

    store = LiveBarStore(root / "restricted.jsonl")
    store.append((bar(LIVE_START_FLOOR - H),))
    fake, _ = exchange([LIVE_START_FLOOR], LIVE_START_FLOOR + H)
    result = fetch_new_bars(
        fake, store, "BTCUSDT", LIVE_START_FLOOR + H, S,
    )
    assert result.appended == 1
    assert store.bars()[0].open_time < LIVE_START_FLOOR

    # A26-4: emulate a write interrupted just before its newline.
    store = LiveBarStore(root / "boundary.jsonl")
    store.append((bar(T),))
    content = store.path.read_bytes()
    assert content.endswith(b"\n")
    store.path.write_bytes(content[:-1])
    assert len(store.bars()) == 1
    store.append((bar(T + H),))
    try:
        store.bars()
    except LiveBarError:
        pass
    else:
        raise AssertionError("expected concatenated JSON to be unreadable")

    # A26-5: invalid alignment reaches both fake endpoints.
    store = LiveBarStore(root / "unaligned.jsonl")
    fake, calls = exchange([T + H], T + 2 * H)
    try:
        fetch_new_bars(
            fake, store, "BTCUSDT", T + 2 * H, S,
            start=T + timedelta(minutes=30),
        )
    except LiveBarError as error:
        assert "gap" in str(error)
    else:
        raise AssertionError("expected an alignment-induced gap refusal")
    assert len(calls) == 2
    assert calls[0] == TIME_URL
PY
```

The attached tests support ordinary sequential fetching and the specific F26 repairs. They do not exercise concurrent writers, symbol changes, invalid historical sequences, or a missing record terminator. Normal pagination preserves contiguous page boundaries; appends are page-by-page, so a later refusal can leave earlier valid pages stored.

**FIX:** resolve A26-1 through A26-3 before acceptance. This message is the review record; it has not been committed.