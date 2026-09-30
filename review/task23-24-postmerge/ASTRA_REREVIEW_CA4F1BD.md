# PR #35 Astra re-review of `ca4f1bd` — text-only (FIX; A2324R-3 blocker)

Date: 2026-09-30. Requested by the owner ("Yes do the review now with astra").

- Invocation: `codex exec -s read-only -m gpt-6-astra -` (codex-cli 0.154.0,
  log header `model: gpt-6-astra`), prompt `review/handoff/ASTRA_PROMPT_PR35.md`
  plus attachments.
- **Text-only review.** On this machine (Android/proot) the Codex sandbox
  cannot start: bubblewrap exits 182, so every reviewer command failed in a
  first attempt, which was stopped. With the owner's choice the orchestrator
  (Claude Opus 5.5) kept `-s read-only` and attached, verbatim from
  `ca4f1bd`: the five `review/task23-24-postmerge/` records,
  `review/task24/OWNER_ANSWERS_2026-09-28.md`, `review/task22/OWNER_ANSWER_Q1.md`,
  `review/task25/ASTRA_REREVIEW_9727496.md`, the full `reconcile.py`,
  `safety.py`, `paper_loop.py`, `machine.py`, and
  `git diff 162e5ea ca4f1bd -- src tests`. Prompt bundle SHA-256: `05ae3573c5e7115c812ff1f5f37b78cc783be043712bd5700f5f0ab413662f3e`.
- The reviewer ran no command; every reproduction below is "not reproduced
  (sandbox unavailable)". The Constitution text was not attached.
- The reviewer's final message follows verbatim.

---

**Verdict: FIX**

Reviewer: OpenAI Codex, GPT-6 family. GPT-6 Astra was requested; exact serving-model suffix is not independently exposed to me.

Reviewed state: **`ca4f1bd`**, using the supplied source texts and diff against **`162e5ea`**. Commit identities and attachment completeness were not independently verified.

**This was a text-only review.** No commands, network requests, credentials, restricted data, or filesystem mutations were used. All reproduction commands below are **not reproduced (sandbox unavailable)**; no command output is claimed. Repository skill files were unavailable through the supplied attachments, so I cannot claim those skill procedures or the executable acceptance gate passed.

### Original findings

“CORRECT” below describes the repair established by code tracing, not an independently executed test result.

| Finding | Assessment | Evidence |
|---|---|---|
| **A2324-1** | **CORRECT** | `reconcile.py:151–187`: an unknown order without `AbsenceCheck` remains unresolved. With the owner’s settings, absence requires two NOT_FOUND responses separated by a verified ten-second clock advance. Known orders returning NOT_FOUND produce a difference immediately. Other query exceptions remain unresolved. The original one-query recovery cannot pass or clear `sent`. Separate clock weaknesses remain below. |
| **A2324-2** | **CORRECT** | `paper_loop.py:615`: quantity no longer gates LOSS_STOP. In the original dust/HALT scenario, the stop opens an incident and alerts while HALT remains HALT. From RUNNING, dust enters FLATTEN, then `tick` detects no sellable step and enters HALT without sending. |
| **A2324-3** | **CORRECT** | `paper_loop.py:212`: optional `max_notional` is parsed into `SymbolFilters`. The existing FLATTEN quantity bound consequently receives the configured maximum. |
| **A2324-4** | **CORRECT** | `paper_loop.py:449`: malformed JSON becomes an empty metadata mapping; `frozen_hash_problems` supplies a logged refusal. Non-object JSON and malformed constitution-hash types are also caught. Report construction no longer indexes missing hash keys. |
| **A25R-4** | **CORRECT** | `paper_loop.py:623,658`: the loop snapshots pending IDs before `tick`, then logs and counts newly retained IDs without a returned order. `safety.py:487` records quantity and cap before submission, preserving the attempted ID and sizing for lost replies. |

Tracing the original A2324-1 reproduction against this version: `r.resolved[cid]` now raises `KeyError`, because unresolved IDs are intentionally omitted. That old print statement must use membership or `.get()` before checking that `exit_freeze` refuses recovery.

For the other original scenarios, the traced outcomes are: a LOSS_STOP alert and incident despite dust; a parsed maximum of 20; and a returned REFUSED report for malformed JSON. These are **predictions from the code, not observed outputs**.

### Earlier re-review findings

| Finding | Assessment | Evidence |
|---|---|---|
| **A2324R-1** | **INCOMPLETE** | The original unchanged/backward-*sleep* scenarios are corrected. Unlike the executor, reconciliation does not enforce monotonicity across all clock readings; see A2324R-3. |
| **A2324R-2** | **INCOMPLETE** | Reports use the post-wait clock and startup decisions skip elapsed hours. Later FLATTEN reconciliation waits still do not advance the loop; see A2324R-4. |
| **F35-1** | **CORRECT** | `paper_loop.py:581`: commands at skipped startup hours are applied at `ready`, before trading. The original owner-HALT scenario therefore suppresses orders. |
| **F35-2** | **CORRECT** | Non-object JSON is normalized for reporting, and the validation path catches the relevant structural errors and refuses startup. |
| **F35-3** | **CORRECT** | `attempts` is populated before placement; FLATTEN_UNKNOWN includes that ID’s quantity and cap. |
| **F35-4** | **CORRECT** | START and controller initialization use `decision.report.at`; startup reconciliation incidents also use that timestamp. The separate REFUSE_START event still has a timestamp problem, A2324R-5. |

LOSS_STOP remains latched throughout a continuous breach. Recovery above the threshold rearms it; a subsequent fall generates another incident as intended. Owner HALT is applied before the loss check and continues to prohibit selling. An existing owner FLATTEN continues on LOSS_STOP.

FLATTEN logging does not double-count a returned order: its ID is explicitly excluded from the unknown set, including when reconciliation fails and retains it. A filter rejection leaves a new ID in `sent`, producing exactly one conservative FLATTEN_UNKNOWN attempt record and count. FREEZE prevents repetition on later ticks.

For ordinary integer counts and returning callbacks, `_query` is bounded: at most `queries` NOT_FOUND responses and `queries - 1` sleeps. Non-NOT_FOUND query exceptions terminate uncertainty checking. Exceptions from `sleep` or `clock` propagate rather than becoming reconciliation differences; I found no concrete occurrence with the loop’s supplied `_Clock`.

### New findings

IDs **A2324R-1 and A2324R-2 remain reserved** for the earlier attempt.

**A2324R-3 — BLOCKER — A backward final clock reading can produce a passed, backdated absence report**

Location: `src/aqt/execution/reconcile.py:184–187,203–205`.

Concrete scenario: one unknown order; both queries return NOT_FOUND. Clock readings are:

1. Before sleep: `T`.
2. After sleep: `T + 10 seconds`.
3. When stamping the report: `T`.

The delay check succeeds. The final reading is never compared with the previously accepted reading, and `max(at, clock())` stamps the passed report at `T`. This can make recovery eligible at a time before its confirming query occurred. The executor’s `now()` rejects this backward movement.

**Reproduced: no — not reproduced (sandbox unavailable).** Exact proposed command:

```bash
python -B - <<'PY'
from datetime import datetime, timedelta, timezone
from aqt.execution.reconcile import AbsenceCheck, LocalRecord, reconcile
from aqt.execution.simulator import ExchangeError

class Venue:
    def query_order(self, cid):
        raise ExchangeError("NOT_FOUND", cid)
    def open_orders(self):
        return ()
    def balances(self):
        return {}

at = datetime(2020, 1, 1, tzinfo=timezone.utc)
readings = iter((at, at + timedelta(seconds=10), at))
check = AbsenceCheck(
    timedelta(seconds=10), 2, lambda duration: None, lambda: next(readings)
)
report = reconcile(Venue(), LocalRecord({}, {"unknown": None}), {}, at, check)
print(report.passed, report.at.isoformat(), dict(report.resolved))
PY
```

Required correction: retain and validate the latest accepted clock reading through report construction; a backward reading must not yield a passed report.

**A2324R-4 — NON-BLOCKING — Startup-resolved orders are queried again, and later waits are discarded by the loop**

Location: `src/aqt/app/paper_loop.py:526–549,655–657,851–864`.

After successful startup reconciliation, `local` is not advanced to `decision.report.next_record()`. Unknown IDs already confirmed absent therefore remain in `local.orders`.

Concrete scenario using the owner’s unchanged ten-second/two-answer settings:

- Start with 361 unknown IDs and unchanged balances.
- Startup confirms absence in 3,610 simulated seconds.
- Owner FLATTEN at the skipped start hour applies when startup finishes.
- The first FLATTEN step occurs at `start + 2 hours`.
- Its reconciliation repeats all 361 absence checks and finishes at `start + 3 hours + 10 seconds`.
- The loop can take its next FLATTEN step at `start + 3 hours`, before that preceding reconciliation finished.

`_reconcile_flatten` discards the advanced clock/report time; its failure transition also uses the original `at`. This produces inconsistent decision and audit chronology. I classify it as non-blocking because this concrete path remains bounded, selling-only simulator behavior; no extra exposure is demonstrated.

**Reproduced: no — not reproduced (sandbox unavailable).** The shared command below probes this scenario.

Required correction: advance the local record after successful startup, and ensure callers respect completion times whenever reconciliation waits.

**A2324R-5 — NON-BLOCKING — A refusal after waiting startup reconciliation is stamped before its cause**

Location: `src/aqt/app/paper_loop.py:485–496,537–538`.

Concrete scenario: startup has one absent unknown order and a balance mismatch. Reconciliation waits ten seconds, then opens its incident at `start + 10 seconds`. Its resulting REFUSE_START events are nevertheless stamped `config.start` by `refuse()`.

F35-4 corrected START and incident timestamps, but the refusal event still predates the completed check that caused it.

**Reproduced: no — not reproduced (sandbox unavailable).** Exact proposed command for A2324R-4 and A2324R-5:

```bash
python -B - <<'PY'
import runpy
from datetime import timedelta
from decimal import Decimal as D
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import aqt.app.paper_loop as loop
from aqt.execution.reconcile import LocalRecord
from aqt.execution.safety import Trigger

t = SimpleNamespace(**runpy.run_path("tests/integration/test_paper_loop.py"))

class Incidents:
    path = Path("/__aqt_readonly_review_nonexistent__/incidents.jsonl")
    def __init__(self):
        self.entries = []
    def open(self, kind, detail, at):
        self.entries.append((kind, at))
        return str(len(self.entries))
    def open_incidents(self):
        return tuple(str(i + 1) for i in range(len(self.entries)))

config = t._config(2, starting_balances={"BTC": D(1), "USDT": D(0)})
series = t._series(24 * 12)
real_reconcile = loop.reconcile
checks = []

def traced(*args, **kwargs):
    result = real_reconcile(*args, **kwargs)
    checks.append((args[3], result.at, result.passed))
    return result

def run(record, commands):
    sink, incidents = t._ListSink(), Incidents()
    with patch.object(loop, "reconcile", traced):
        report = loop.run_paper(
            config, series, data_manifest_hash="0" * 64,
            sinks=[sink], incidents=incidents, operations_log=None,
            environ={}, repository_root=Path.cwd(),
            local_record=record, commands=commands,
        )
    return report, sink, incidents

record = LocalRecord(
    config.starting_balances,
    {f"unknown-{i:03d}": None for i in range(361)},
)
report, sink, incidents = run(record, {config.start: Trigger.OWNER_FLATTEN})
print("A2324R-4 reconciliation intervals:", checks[:2])
print("A2324R-4 ORDER events:", [
    event for event in sink.events if str(event.kind) == "ORDER"
][:2])

record = LocalRecord({"BTC": D(2), "USDT": D(0)}, {"unknown": None})
report, sink, incidents = run(record, {})
print("A2324R-5 incidents:", incidents.entries)
print("A2324R-5 STARTUP events:", [
    event for event in sink.events if str(event.kind) == "STARTUP"
])
PY
```

### Validation disposition

The attached tests directly cover the principal repairs, but they do not cover the three scenarios above. Proposed regression command:

```bash
python -B -m pytest -q -p no:cacheprovider \
  tests/unit/test_safety.py tests/integration/test_paper_loop.py
```

**Not reproduced (sandbox unavailable).** This command also requires a writable test environment because its fixtures create files.

The original four-case reproduction command remains the exact PowerShell block in the attached `ASTRA_REVIEW_1E02472.md`, with the unresolved-ID indexing adjustment noted above. **Not reproduced (sandbox unavailable).**

The author’s reported test, lint, type, import-boundary, frozen-file, and drill results were not independently rerun. This final message is the review record for owner relay; I have not committed it. **FIX** remains required for A2324R-3.