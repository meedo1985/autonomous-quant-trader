# Tasks 23-24 post-merge Astra review (FIX)

Date: 2026-09-29. Requested by the owner ("make astra review for all we
need"). Tasks 23 and 24 were merged after Claude Fable 5.1 reviews, an
owner-chosen substitute from the implementer's provider family; this is the
different-family section 16 review.

- Invocation: `codex exec -s read-only -m gpt-6-astra -` (CLI header
  `model: gpt-6-astra`); the model reports only the GPT-6 family.
- Scope: `git diff edc3b39 main` over `src`, `tests`, `pyproject.toml`,
  `configs`, `scripts`; reviewed `main` at `1e02472`.
- The reviewer's final message follows verbatim.

---

**Verdict: FIX**

Reviewer: OpenAI Codex, GPT-6. Exact **Astra** runtime metadata is not exposed in this session; I cannot attest the suffix.

Reviewed `main`: **`1e02472b6dad5dea39df894764c9b684da1aa106`**, against `edc3b39`. Worktree remained clean. No files, credentials, network, exchange APIs, or restricted data were used or changed.

**A2324-1 — BLOCKER — Reconciliation prematurely clears an uncertain FLATTEN order**

Location: [reconcile.py:148](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/reconcile.py:148), [safety.py:337](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/execution/safety.py:337).

A FLATTEN order expires unfilled because the next open exceeds its price cap, then placement times out. With the simulator’s existing `not_found_queries=2` fault, reconciliation receives its **first** `NOT_FOUND`, records the order as resolved to `None`, and passes because balances are unchanged. One second after the timeout, `exit_freeze()` accepts this report, enters HALT, and clears `sent`.

This bypasses §21’s delayed re-query. The coverage repair checks membership in `resolved`, but membership does not establish confirmed absence.

**Reproduced: yes**, using the command below:

```text
A2324-1: True None 1 HALT 0
```

Meaning: reconciliation passed; reported absent; only one query; FREEZE exited; pending order forgotten. No unintended fill was demonstrated—the defect is premature resolution and recovery.

The existing recovery regression uses a placement that never reaches the venue. The hidden-fill regression relies on changed balances exposing uncertainty. Neither covers a hidden zero-fill order.

Correction: retain uncertainty until the required delayed absence confirmation or a terminal order response.

**A2324-2 — BLOCKER — Minimum quantity suppresses a required loss-stop alert and incident**

Location: [paper_loop.py:585](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/app/paper_loop.py:585).

Start with `0.000009 BTC`, zero USDT, and the existing `min_qty=0.00001`. Apply owner HALT, then move the price from 10,000 to 7,000. Equity falls 30%, but `held >= min_qty` suppresses both the CRITICAL loss-stop alert and its incident.

**Reproduced: yes**:

```text
A2324-2: HALT 0 0 ['OWNER_HALT']
```

Meaning: HALT preserved, no orders, **no LOSS_STOP alert**, only the owner-HALT incident.

This demonstrates an incomplete F24R-1 repair. It also contradicts the later review’s dismissal of dust holdings: an account can begin entirely in dust, rather than almost entirely in USDT. Existing loss-stop regressions use holdings above the minimum.

Correction: separate breach reporting from whether a bounded sell is possible.

**A2324-3 — NON-BLOCKING — Configuration silently discards maximum notional**

Location: [paper_loop.py:205](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/app/paper_loop.py:205).

Add `max_notional = "20"` to the example’s `[filters]`. `load_config()` accepts the configuration but constructs `SymbolFilters(max_notional=None)`. Using those filters, FLATTEN sells 0.5 BTC at 7,000—3,500 USDT despite the supplied 20 USDT cap.

**Reproduced: yes**:

```text
A2324-3: None 0.50000 3500.000000
```

The maximum-notional controller regression constructs `SymbolFilters` directly, bypassing the loader. The controller repair works; configuration never supplies its bound.

Correction: parse the optional maximum, or reject the unsupported field explicitly.

**A2324-4 — NON-BLOCKING — Malformed manifest bypasses logged startup refusal**

Location: [paper_loop.py:436](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/app/paper_loop.py:436).

If `FROZEN_HASHES.json` contains malformed JSON, the initial unguarded parse raises before alert-router initialization and before `frozen_hash_problems()` handles unreadable metadata. No `REFUSE_START` report or alert is produced.

**Reproduced: yes**, injecting malformed contents in memory:

```text
A2324-4: JSONDecodeError 0 0
```

Trading does not start, so this remains non-blocking. Existing hash tests alter valid artifacts; they do not exercise malformed manifest parsing.

Correction: initialize refusal reporting before parsing untrusted startup metadata.

The following **single reproduction command** produces all four outputs above. It uses synthetic bars, in-memory incident sinks, and an audit hook blocking filesystem writes and sockets:

```powershell
rtk proxy .venv/Scripts/python.exe -B -c @'
__file__='<stdin>'
import hashlib, runpy, sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from datetime import timedelta
from decimal import Decimal as D

def readonly(event,args):
    if event=='open' and ((isinstance(args[1],str) and any(c in args[1] for c in 'wax+')) or (isinstance(args[2],int) and args[2] & (1|2|64|512|1024))): raise RuntimeError('write forbidden')
    if event.startswith('socket.') or event in ('os.mkdir','os.remove','os.rename','os.rmdir'): raise RuntimeError(event+' forbidden')
sys.addaudithook(readonly)
t=SimpleNamespace(**runpy.run_path('tests/integration/test_paper_loop.py'))
from aqt.execution.safety import SafetyController, Mode, Trigger
from aqt.execution.reconcile import LocalRecord, reconcile
class Incidents:
    path=Path('review/task24/__nonexistent_readonly_probe__.jsonl')
    def __init__(self): self.entries=[]
    def open(self,kind,detail,at): self.entries.append(kind); return str(len(self.entries))
    def open_incidents(self): return tuple(map(str,range(len(self.entries))))
def controller(at):
    return SafetyController(t.AlertRouter([t._ListSink()]),Incidents(),at,mode=Mode.RUNNING)
start=t.T0+192*t.HOUR
series=t.BarSeries('BTCUSDT',tuple(t.Bar(t.T0+i*t.HOUR,p,p,p,p,5.) for i in range(195) for p in [10000. if i<192 else 7000.]))
config=t._config(1,end=start+2*t.HOUR,starting_balances={'BTC':D('0.000009'),'USDT':D(0)})
def run(sink,incidents):
    return t.run_paper(config,series,data_manifest_hash='0'*64,sinks=[sink],incidents=incidents,operations_log=None,environ={},repository_root=Path.cwd(),commands={start:Trigger.OWNER_HALT})

# A2324-1
cid='aqt-flat-'+hashlib.sha256(f'BTCUSDT|{start.isoformat()}|1'.encode()).hexdigest()[:27]
v=t.SimulatedExchange({'BTCUSDT':series},{'BTCUSDT':t.FILTERS},{'BTC':D(1),'USDT':D(0)},scenario=t.Scenario({cid:t.Fault(timeout=True,not_found_queries=2)}))
c=controller(start); c.trigger(Trigger.OWNER_FLATTEN,start)
c.tick(v,'BTCUSDT',t.FILTERS,config.flatten,D(10000),start,start)
at=start+timedelta(seconds=1)
r=reconcile(v,LocalRecord({'BTC':D(1),'USDT':D(0)},c.sent),{},at)
print('A2324-1:',r.passed,r.resolved[cid],sum(e['event']=='query_not_found' for e in v.events),c.exit_freeze(r,at),len(c.sent))

# A2324-2
sink=t._ListSink(); incidents=Incidents(); report=run(sink,incidents)
print('A2324-2:',report.final_mode,report.orders_sent,sum(e.fields.get('trigger')=='LOSS_STOP' for e in sink.events),incidents.entries)

# A2324-3
text=Path('configs/paper_trading.example.toml').read_text().replace('[filters]','[filters]\nmax_notional = '+chr(34)+'20'+chr(34))
with patch.object(Path,'read_text',return_value=text): loaded=t.load_config(Path('in_memory.toml'))
at=start+t.HOUR
v=t.SimulatedExchange({'BTCUSDT':series},{'BTCUSDT':loaded.filters},{'BTC':D(1),'USDT':D(0)})
c=controller(at); c.trigger(Trigger.OWNER_FLATTEN,at)
o=c.tick(v,'BTCUSDT',loaded.filters,loaded.flatten,D(7000),at,at)
print('A2324-3:',loaded.filters.max_notional,o.executed_qty,o.quote_amount)

# A2324-4
original=Path.read_text
sink=t._ListSink(); incidents=Incidents()
def read_text(p,*a,**kw): return '{' if p.name=='FROZEN_HASHES.json' else original(p,*a,**kw)
with patch.object(Path,'read_text',read_text):
    try: run(sink,incidents)
    except Exception as error: print('A2324-4:',type(error).__name__,len(sink.events),len(incidents.entries))
'@
```

Validation on Python 3.14.7:

- **12 tests passed; 81 deselected** from the three scoped test modules. Tests requiring file-writing fixtures were excluded to respect read-only authorization. No complete-suite pass is claimed.
- `rtk proxy .venv/Scripts/python.exe -B -m ruff check --no-cache .` — passed.
- `rtk proxy .venv/Scripts/python.exe -B -m ruff format --check --no-cache .` — 99 files formatted.
- `rtk proxy .venv/Scripts/python.exe -B -m mypy --no-incremental --no-sqlite-cache --cache-dir=NUL src scripts` — 52 source files passed.
- `rtk proxy .venv/Scripts/python.exe -B -c "from importlinter.cli import lint_imports; raise SystemExit(lint_imports(no_cache=True))"` — six contracts kept.
- `rtk proxy git diff --check edc3b39 main` — passed.
- Read-only frozen verification — 28/28 baseline files and inventory, 14/14 sidecars, Constitution self-hash, manifest/protocol bindings, and nested bindings passed.

All four findings remain unrepaired under the requested read-only scope. Task 25’s FLATTEN ORDER logging change was excluded.
