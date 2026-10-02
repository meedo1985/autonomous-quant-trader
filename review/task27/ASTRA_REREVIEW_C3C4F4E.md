# Task 27 Astra re-review of `c3c4f4e` (FIX; A27-24 non-blocking)

Date: 2026-10-02. Requested by the owner ("go ahead with Astra and the drills").

- Invocation: `codex exec -s read-only -m gpt-6-astra -o <last> - < ASTRA_PROMPT_C3C4F4E.md`
  (codex-cli 0.157.1; log header: model `gpt-6-astra`, provider openai,
  sandbox read-only, reasoning effort high, session
  `01a0fbfc-807a-7880-bcf6-3c7bc4ff53dc`).
- Prompt: `ASTRA_PROMPT_C3C4F4E.md` in this folder, SHA-256
  `7d35b2dc72682effc7fcd540a035e0292895712164980b8bb609c06610c34e54`.
- First Task 27 review run on a PC inside the repository: the reviewer read
  files and ran read-only commands. pytest was blocked by the sandbox (no
  usable temporary directory); the reviewer used in-memory reproductions
  instead, as it states below.
- The reviewer's final message follows verbatim.

---

**Verdict: FIX.**

Reviewer: **GPT-6 Astra**, independent reviewer; implementation attributed to **Claude Opus 5.5**. Reviewed branch `task27-persistent-state`, commit **`c3c4f4e347cf2b9e0008006f48828ee191c59556`**, repair diff `ad24b7d..c3c4f4e`, for draft PR #37. Commit and branch verified locally; PR metadata was not checked online.

No repository files were changed. No network, credentials, exchange APIs, or restricted data were accessed. This message is the review record; it is not committed.

| Finding | Assessment | Evidence |
|---|---|---|
| **A27-17** | **INCOMPLETE** | The original repairs work, but startup can still permanently omit an available historical breach through the new count-based deduplication: A27-24. |
| **A27-20** | **CORRECT for the original scenario** | Invalid override at mark 70, peak 100: uninterrupted and killed/restarted paths each record one LOSS_STOP. Tested using the actual loop with in-memory persistence substitutes. |
| **A27-21** | **CORRECT** | Recovery now receives `history`; trading retains its contiguous window. The original gap scenario recovers peak **120** and records **one** LOSS_STOP. |
| **A27-22** | **INCOMPLETE** | The original full-history scenario now records **two versus two** incidents, including after two successive kills during replay appends. However, count-based deduplication can suppress a different, unlogged firing when supplied history is shorter: A27-24. |

**A27-24 — NON-BLOCKING — A logged firing can suppress a different, never-logged firing**

Location: [paper_loop.py:726](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/app/paper_loop.py:726), especially `for hour in missed[logged:]` at line 732.

Concrete scenario, HALT throughout, one BTC, peak 100, armed:

1. Snapshot watermark is H−1.
2. H has mark 70. The loop appends its LOSS_STOP incident, then dies before saving the updated watermark/latch.
3. Restart supplies a shorter history beginning at bar-open H. The bar that supported H’s already-logged firing—open H−1—is absent.
4. Available decision marks are H+1 = 100, H+2 = 70, H+3 = 100.
5. Restart at H+3 passes the contiguous-window check.
6. Replay finds **one** firing, at **H+2**.
7. `logged == 1` because H’s incident follows the snapshot. `missed[1:]` discards H+2’s firing.
8. Startup saves past H+2, permanently consuming its unlogged breach.

**Reproduced: yes, in memory.** The actual `run_paper` implementation was exercised with in-memory journal, incident-log, marker, and sink substitutes; valuation, reconciliation, override, controller, and replay logic remained real.

Output:

```text
A27-24 memory: expected 2 LOSS_STOP, actual 1 latch True
loss details: ['equity 70.00 below 0.80 x peak 100.00']
```

A shorter history is accepted by this API; it does not enforce complete recovery coverage. This finding does not require modifying historical prices or fabricating an unrelated incident.

Severity follows A27-22: the demonstrated defect loses an incident, while HALT, peak, and final latch remain correct. **No trading bypass was reproduced.**

Correction: identify which firing an incident represents rather than subtracting an undifferentiated count, or explicitly refuse recovery when the required correspondence cannot be established. A timestamp alone needs care because waited/replayed incidents are stamped at reconciliation completion.

This compact, filesystem-read-only reproduction also confirms the mismatched slicing:

```powershell
@'
from decimal import Decimal as D
from aqt.app.paper_loop import _replay
from aqt.data.bars import BarSeries
from tests.integration.test_paper_recovery import START as H, HOUR, ONE_BTC, _priced

s = _priced({H-HOUR:70., H:100., H+HOUR:70., H+2*HOUR:100.})
s = BarSeries(s.symbol, tuple(b for b in s.bars if b.open_time >= H))
peak, armed, valued, missed = _replay(
    s, ONE_BTC, 'BTC', (H-HOUR, H, H+3*HOUR),
    (D(100), True), D('.2'), fires=True)
logged = 1
print('replayed firing offsets:', [int((t-H)/HOUR) for t in missed])
print('new incidents after count slicing:', len(missed[logged:]))
print('expected new incidents: 1')
assert missed == [H+2*HOUR] and missed[logged:] == []
'@ | rtk proxy .venv/Scripts/python.exe -B -X utf8 -
```

Exit 0:

```text
replayed firing offsets: [2]
new incidents after count slicing: 0
expected new incidents: 1
```

**Other requested crash and replay checks**

- **Two consecutive kills:** with complete history, killing immediately after each successive replay LOSS_STOP append produced counts 1, then 2; the eventual restart retained 2. No duplicate reproduced.
- **Different incident kinds:** the counter excludes OWNER_HALT, reconciliation failures, and other non-LOSS_STOP incidents. I found no second legitimate LOSS_STOP-producing cause in the loop that independently establishes another defect.
- **Refused override:** before/after both save calls, the transient-breach scenario ultimately recorded exactly one incident.
- **Failed reconciliation:** enters FREEZE; `fire()` suppresses LOSS_STOP there. The report’s statement that failed overrides “fire” therefore needs this existing FREEZE qualification. No new code finding: FREEZE suppression was already explicitly accepted.
- **Accepted override:** after the reset snapshot is saved, restart preserves peak 70 and produces no old-line firing. A kill immediately before that snapshot restores HALT with peak 100 and subsequently records the old-line breach. This is the conservative rollback disclosed in the previous review, **not proof of exactly-once override completion at every instruction boundary**.
- **Watermark/reset boundary:** direct replay checks excluded pre-watermark prices, including an earlier price of 1000; a saved reset at H retained peak 90 instead of replaying H’s old 120 mark.
- **Gap/FREEZE replay:** historical 120 was retained across the gap; `fires=False` preserved the peak without firing. No new ordering or double-valuation defect was reproduced.
- **A27-23:** respected the owner’s “Fire as usual” decision; it is not reopened.

**Commands and validation**

All Python commands used `-B` to prevent bytecode writes.

- Git: `status --short --untracked-files=all`, `rev-parse HEAD`, `branch --show-current`, unstaged/staged diffs, repair diff/stat, `diff --check ad24b7d c3c4f4e`, and frozen-path comparison against local `main`.
- Read the prior review, dispositions, owner answers, design, governing documents, relevant skills, implementation, tests, and CI configuration.
- Attempted:

```powershell
rtk proxy .venv/Scripts/python.exe -B -m pytest -p no:cacheprovider -q tests/integration/test_paper_recovery.py tests/integration/test_paper_restart.py tests/integration/test_paper_loop.py tests/unit/test_account_state.py tests/unit/test_live_bars.py tests/unit/test_safety.py
```

  **Blocked before collection**, exit 1: `FileNotFoundError: No usable temporary directory found`. This is a sandbox limitation, not a test failure.

- Extracted and executed the original reproduction from `ASTRA_REREVIEW_AD24B7D.md`. **Blocked at `TemporaryDirectory()`**, same error.
- Ran inline, no-write Python reproductions using in-memory persistence substitutes. Original-scenario output:

```text
A27-20 memory: 1 1
A27-21 memory: 120.0 1
replay append kill 1 losses 1
replay append kill 2 losses 2
A27-22 memory: 2 2 after two kills 2
```

- Ran the override save-boundary matrix and watermark/reset/gap checks described above. These verify loop behavior, **not filesystem durability**.
- Independently ran a read-only Python port of the frozen verifier: **PASS—28 trusted files and exact inventory, 14 sidecars, Constitution self-hash, manifest/protocol bindings**.
- `git diff --check`: clean. Frozen-path diff against local `main`: empty. Final worktree status: clean, with Git warning that the global ignore file was inaccessible.
- Environment: **Python 3.14.7, Windows AMD64**. Lint, mypy, import-boundary checks, and the full suite were not independently rerun; the committed local report records their prior passing results.

**FIX remains the verdict because the requested incident-equivalence repair is incomplete.** A27-24 is the sole new finding; no additional safety blocker was reproduced. The original A27-20 and A27-21 scenarios are repaired.