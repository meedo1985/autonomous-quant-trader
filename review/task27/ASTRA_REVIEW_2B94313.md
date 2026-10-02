# Task 27 Astra review of `2b94313` (parts a, b1, b2) — text-only (FIX; A27-1..A27-5 blockers)

Date: 2026-10-01. Requested by the owner ("Make next").

- Invocation: `codex exec -s read-only -m gpt-6-astra -` (codex-cli 0.154.0,
  log header `model: gpt-6-astra`). First different-model review of Task 27.
- **Text-only**: the Codex sandbox cannot start on this machine (Android/proot,
  bubblewrap exits 182). Attached verbatim from `2b94313`: `DESIGN.md`,
  `OWNER_ANSWERS.md`, `LOCAL_REPORT.md`, `review/task24/OWNER_ANSWERS_2026-09-28.md`,
  `state.py`, `paper_loop.py`, `safety.py`, `reconcile.py`, `live_bars.py`,
  `fetch_live_bars.py`, `test_paper_restart.py`, `test_paper_recovery.py`, the
  Constitution, and `git diff 727ec6c 2b94313 -- src scripts tests`.
  `ledger.py` and the skill files were not attached. Prompt bundle SHA-256:
  `98561c88861872eef8db52c2bc65c399fc9bf88eb9aa14439646993b53a9d2fe`.
- The reviewer ran no command. The reviewer's final message follows verbatim.

---

**Verdict: FIX.**

Reviewer: **GPT-6 Astra**, independent different-model review of implementation by Claude Opus 5.5. Reviewed supplied head **`2b94313`**, branch `task27-persistent-state`, draft PR **#37**, against supplied base **`727ec6c`**.

This was a **text-only review** of the attachments. I ran no commands and accessed no files, credentials, network, exchange APIs, or confirmation/lockbox data. Commit identities and test results were not independently verified. The orchestrator reports 1672 passed, 4 skipped; clean ruff, formatting, mypy and six import contracts; frozen verification PASS.

The local skill files and ledger implementation were not attached, so I cannot claim to have read those skills or independently checked the ledger’s locking, hash verification, and fsync implementation. This final message is the review record; I have not committed it.

All reproductions below are **not reproduced (sandbox unavailable)**. Commands are supplied for subsequent execution, use temporary directories and synthetic fixtures, and deliberately contain assertions expected to fail at this head.

**A27-1 — BLOCKER — Completion timestamps are captured before the work completes.**

Locations: `src/aqt/app/paper_loop.py:811`, `:815`, `:1031`; recovery saves in `leave_freeze` and `end_halt`; shutdown emission following the exception handler.

`done` is assigned before the hour’s executor/reconciliation work. Advancing `busy_until` does not advance `done`.

Concrete scenario: an override starts at 01:00, reconciliation completes at 03:00, and `end_halt` saves RUNNING at 03:00. The final hourly save then appends the same state at 01:00. A run ending at 02:00 also emits SHUTDOWN at 02:00 after its 03:00 transition.

Consequences:

- Journal and operations timestamps can move backwards.
- `load_saved()` returns the backdated final save, allowing a restart earlier than the completed recovery.
- That snapshot can describe a mode entered after its own save timestamp.
- The existing long-reconciliation test does not cover a recovery’s explicit completion-time save followed by `save(done)`.

The startup-refusal change for A2324R-5 is correct in the supplied code. A2324R-4 is incomplete.

Exact reproduction command, injecting a delayed completion report to isolate the loop defect:

```bash
python - <<'PY'
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import aqt.app.paper_loop as loop
from aqt.app.state import AccountDir
from aqt.core.ledger import read_entries
from aqt.execution.safety import Trigger
from tests.integration.test_paper_loop import _config, _run, _series, HOUR
from tests.integration.test_paper_restart import START, _account, _venue
from tests.integration.test_paper_recovery import _override

with TemporaryDirectory() as d:
    a = AccountDir(Path(d))
    series = _series(24 * 14)
    venue = _venue(series)
    _account(a, venue, series, START, START + HOUR,
             {START: Trigger.OWNER_HALT})
    at = START + HOUR
    real = loop.reconcile
    def delayed(*args, **kwargs):
        r = real(*args, **kwargs)
        return replace(r, at=r.at + 2 * HOUR)
    with patch.object(loop, "reconcile", delayed):
        _run(a.root, _config(1, start=at, end=at + HOUR), series,
             incidents=a.incident_log(), journal=a.journal, venue=venue,
             overrides={at: _override(a.incident_log().open_incidents(), at)})
    stamps = [e.recorded_at_utc for e in read_entries(a.journal.path)]
    assert stamps == sorted(stamps), stamps
PY
```

Fix completion-time propagation, including final saves and shutdown. If recovery waits across price bars, the Q27-1/Q27-2 reset also needs an explicit policy for valuing equity at recovery completion: currently it uses the mark captured before the wait.

**A27-2 — BLOCKER — A recovered filled buy loses its risk-increase timestamp.**

Locations: `src/aqt/app/paper_loop.py:641`, `:690`, `:962`, `:1026`.

The pre-send snapshot contains the pending client order ID but the old `last_increase`. If the process dies after the buy fills but before the successful-result bookkeeping, startup reconciliation resolves and incorporates the buy, then discards its order history through `next_record()`. The loop restores `last_increase` exclusively from the old snapshot.

Concrete scenario: the first buy fills; the process dies while emitting its ORDER event. Restart finds the fill and correct balances, but retains `last_increase=None`. Subsequent governor decisions receive a state that omits the actual risk increase, defeating the persistence requirement for governor pacing.

The supplied kill test checks balances and unsettled orders, not this field.

Exact reproduction command:

```bash
python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import aqt.app.paper_loop as loop
from aqt.app.state import AccountDir
from tests.integration.test_paper_loop import _series, HOUR
from tests.integration.test_paper_restart import START, _account, _venue, _saved

class Killed(BaseException):
    pass

real = loop.AlertRouter.emit
def kill_after_buy(self, event):
    if (str(event.kind) == "ORDER"
            and event.fields.get("side") == "BUY"
            and event.fields.get("executed_qty") not in (None, "0")):
        raise Killed()
    return real(self, event)

with TemporaryDirectory() as d:
    a = AccountDir(Path(d))
    series = _series(24 * 14)
    venue = _venue(series)
    try:
        with patch.object(loop.AlertRouter, "emit", kill_after_buy):
            _account(a, venue, series, START, START + HOUR)
    except Killed:
        pass
    else:
        raise AssertionError("fixture did not reach the injected crash")
    loop.refuse_marker_path(a.incident_log()).unlink(missing_ok=True)
    result = _account(a, venue, series, START + HOUR, START + 2 * HOUR)
    assert not result.refused, result.refused
    assert _saved(a)[0].last_increase == START, _saved(a)[0].last_increase
PY
```

Recovery must reconstruct the applicable bookkeeping from resolved fills before discarding them, or persist enough intent to restore it safely.

**A27-3 — BLOCKER — A crash before the hourly write can erase an observed peak.**

Locations: `src/aqt/app/paper_loop.py:811`, `:845`, `:1031`.

The loop raises `peak` in memory, but an hour without an order need not save it until the hourly save. Killing immediately before that write leaves the previous peak. Restart accepts a later start without replaying the missed valuation.

Concrete scenario: saved peak 100; an hour observes equity 120; the process dies before saving it; restart observes equity 90. The correct line is 96, but the restored line is 80, so the loss-stop incident is missed. This also occurs in HALT, where the owner’s HALT should remain effective but the breach should still be recorded.

The existing peak test verifies preservation of an already-saved peak, not this crash boundary.

Exact reproduction command:

```bash
python - <<'PY'
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from aqt.app.paper_loop import refuse_marker_path
from aqt.app.state import AccountDir, AccountState, StateJournal
from aqt.data.bars import BarSeries
from aqt.execution.reconcile import LocalRecord
from aqt.execution.safety import Mode, Trigger
from tests.integration.test_paper_loop import _series, HOUR
from tests.integration.test_paper_restart import START, _account, _saved

class Killed(BaseException):
    pass

class Venue:
    def balances(self):
        return {"BTC": Decimal("1"), "USDT": Decimal("0")}
    def open_orders(self):
        return ()
    def query_order(self, cid):
        raise AssertionError(cid)

bars = []
for b in _series(24 * 14).bars:
    price = 120.0 if b.open_time == START else (
        90.0 if b.open_time == START + HOUR else 100.0)
    bars.append(replace(b, open=price, high=price, low=price, close=price))
series = BarSeries(symbol="BTCUSDT", bars=tuple(bars))
real = StateJournal.save
def killed_save(self, state, at):
    if state.peak == Decimal("120"):
        raise Killed()
    return real(self, state, at)

with TemporaryDirectory() as d:
    a = AccountDir(Path(d))
    venue = Venue()
    prior = START - HOUR
    a.incident_log().open(str(Trigger.OWNER_HALT), "owner halt", prior)
    a.journal.save(AccountState(
        mode=Mode.HALT, entered_at=prior,
        record=LocalRecord(venue.balances()), sent={}, attempts={},
        peak=Decimal("100"), stop_armed=True, last_increase=None,
        incidents_seen=1), prior)
    try:
        with patch.object(StateJournal, "save", killed_save):
            _account(a, venue, series, START + HOUR, START + 2 * HOUR)
    except Killed:
        pass
    else:
        raise AssertionError("fixture did not reach the injected crash")
    refuse_marker_path(a.incident_log()).unlink(missing_ok=True)
    result = _account(a, venue, series, START + 2 * HOUR, START + 3 * HOUR)
    assert not result.refused, result.refused
    assert _saved(a)[0].peak == Decimal("120"), _saved(a)[0].peak
PY
```

The recovery contract needs to cover unsaved valuation hours; moving a write closer to the calculation alone does not eliminate a kill immediately before that write.

**A27-4 — BLOCKER — Acknowledging a later gap can skip valid bars from a rejected batch.**

Locations: `src/aqt/data/live_bars.py:244`, `:271`.

Batch append correctly refuses the whole batch on a gap. However, `acknowledge_gap()` always starts its record at the next hour already missing from the store.

Concrete scenario: the store contains hour 0. Binance supplies valid hours 1 and 3; only hour 2 is missing. Append rejects the batch. Acknowledging resumption at hour 3 records hours **1 and 2** as missing and future fetches begin at hour 3. Valid hour 1 is omitted and misclassified as part of the outage.

This is not the requested “continue after the real gap” behavior. The supplied test places the actual gap immediately after the existing store, masking the problem.

Exact reproduction command:

```bash
python - <<'PY'
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from aqt.data.bars import Bar
from aqt.data.live_bars import LiveBarStore, LiveBarError

t = datetime(2026, 9, 29, tzinfo=UTC)
h = timedelta(hours=1)
def bar(n):
    return Bar(t + n*h, 100.0, 100.0, 100.0, 100.0, 1.0)

with TemporaryDirectory() as d:
    s = LiveBarStore(Path(d) / "bars.jsonl", "BTCUSDT")
    s.append((bar(0),))
    try:
        s.append((bar(1), bar(3)))
    except LiveBarError:
        pass
    else:
        raise AssertionError("the gapped batch should be refused")
    gap = s.acknowledge_gap(t + 3*h, "owner", "Hour 2 is missing", t + 4*h)
    s.append((bar(3),))
    assert gap.first_missing == t + 2*h, gap
PY
```

Preserve batch atomicity while providing a way to establish the valid prefix before acknowledging precisely the missing interval.

**A27-5 — BLOCKER — Whole-history reads accept unsigned gap records and can reinterpret a bar as a gap.**

Locations: `src/aqt/data/live_bars.py:177`, `:203`, `:308`.

Read-time gap validation checks only the interval’s position and direction. It does not enforce the write API’s owner-name, statement, UTC/alignment requirements, or mutually exclusive row shapes.

Concrete scenario: add gap fields to an existing interior bar row, leave its OHLC fields intact, set the actor and statement to empty strings, and make the gap span that bar’s hour. `_read()` treats the row as a gap, ignores its original bar fields, and accepts the remainder of the history. A previously stored bar disappears from `bars()` behind an unsigned gap.

The append lock does not address this: subsequent appenders re-read and accept that history.

Exact reproduction command:

```bash
python - <<'PY'
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from aqt.data.bars import Bar
from aqt.data.live_bars import LiveBarStore, LiveBarError

t = datetime(2026, 9, 29, tzinfo=UTC)
h = timedelta(hours=1)
with TemporaryDirectory() as d:
    s = LiveBarStore(Path(d) / "bars.jsonl", "BTCUSDT")
    s.append(tuple(Bar(t + n*h, 100.0, 100.0, 100.0, 100.0, 1.0)
                   for n in range(3)))
    rows = [json.loads(x) for x in s.path.read_text().splitlines()]
    rows[1].update(
        gap_first_missing=(t+h).isoformat(),
        gap_resumes_at=(t+2*h).isoformat(),
        gap_actor="", gap_statement="",
        gap_recorded_at="2026-09-29T04:00:00")
    s.path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    try:
        s.bars()
    except LiveBarError:
        pass
    else:
        raise AssertionError("unsigned hybrid bar/gap row was accepted")
PY
```

Require the complete gap contract on reads and reject hybrid rows. Separately, an owner name and statement in an editable file do not establish the **signed, committed** provenance described in OWNER_ANSWERS.md. No binding to such a committed record is shown. This needs resolution before treating Q27-3 as closed; a specific cryptographic implementation is not prescribed by this finding.

**A27-6 — NON-BLOCKING — Snapshot parsing is not exact.**

Locations: `src/aqt/app/state.py:77`, `:159`, `:190`, `:233`.

Concrete scenario: `attempts={"x": "12"}` parses successfully as quantity 1 and cap 2 because the parser indexes the string. Longer sequences are silently truncated to their first two values. Unknown fields are ignored, and order identifiers are coerced with `str()`.

Additionally, `load_saved()` checks the record type and snapshot schema only for the last entry; an earlier foreign record followed by a valid snapshot is accepted.

These contradict the documented exact-parse contract. I have not established an autonomous-order bypass from these malformed fields alone.

Exact reproduction command:

```bash
python - <<'PY'
from aqt.app.state import AccountState, StateError
from tests.unit.test_account_state import _state

payload = _state().as_mapping()
payload["attempts"] = {"x": "12"}
try:
    AccountState.from_mapping(payload)
except StateError:
    pass
else:
    raise AssertionError("a string was accepted as a quantity/cap pair")
PY
```

**A27-7 — NON-BLOCKING — A second crash during recovery makes `STATE_RESUMED` unreplayable.**

Locations: `src/aqt/app/paper_loop.py:646`, `:1089`.

Concrete sequence:

1. An override closes every incident, then the process dies before saving RUNNING.
2. Restart loads HALT and opens `STATE_RESUMED`.
3. The process dies before saving the new `incidents_seen`.
4. The following restart replays `STATE_RESUMED`, which is neither a `Trigger` nor a recognized special case, and refuses the start.

This fails closed and retains the incident, so it is not a trading bypass. It nevertheless strands an otherwise valid protective restart without a normal recovery route.

Exact reproduction command:

```bash
python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from aqt.app.paper_loop import _resume
from aqt.execution.safety import IncidentLog, Mode
from tests.unit.test_account_state import _state, T0

with TemporaryDirectory() as d:
    incidents = IncidentLog(Path(d) / "incidents.jsonl")
    saved = _state(mode=Mode.HALT, incidents_seen=0)
    incidents.open("STATE_RESUMED", "resumed HALT, no incident open", T0)
    result = _resume(saved, incidents)
    assert not isinstance(result, str), result
PY
```

**Assessment of T27-07 through T27-12**

| Finding | Assessment |
|---|---|
| **T27-07** | Repair is supported by inspection: FREEZE_EXIT outside FREEZE is refused and falls through to the ordinary hour, including FLATTEN. Test not executed. |
| **T27-08** | Repair is supported: failed override reconciliation opens `RECONCILIATION_FAILED` and enters FREEZE. Completion-time handling remains defective under A27-1. |
| **T27-09** | The supplied recovery path correctly calls `settle()` with the passed report and retained authorizations. This fixes the disclosed in-process reservation leak. It does not restore crash-lost risk-increase bookkeeping, A27-2. |
| **T27-10** | Disclosure is accurate but insufficient as a blanket non-blocking disposition. A27-5 demonstrates acceptance of unsigned records and disappearance of existing bars behind a gap. Signed/committed provenance remains unresolved. |
| **T27-11** | Remains an unverified question. No network research was performed. I make no claim that Binance does or does not produce such gaps. |
| **T27-12** | Remains unverified. Reported unit/integration results do not replace the omitted drill comparison. Any mandatory drill validation must pass before the task gate can be declared complete. |

The ordinary recovery gates are substantially sound in the supplied text: startup reconciles before entering the loop; FREEZE_EXIT requires a passed reconciliation and leads to HALT; HALT override checks the five artifacts and the complete open-incident set; successful recovery releases covered reservations through `settle()`. Owner HALT continues to prohibit orders, and S-4 continues through bounded FLATTEN steps.

The supplied evidence does **not** establish the full kill-at-every-write acceptance. In particular, the crash test omits recovery transitions and does not assert recovered pacing or preservation of a newly observed peak. **FIX** is required for A27-1 through A27-5, followed by regression validation, retention of all findings in the committed review record, and the owner’s section 16 review.