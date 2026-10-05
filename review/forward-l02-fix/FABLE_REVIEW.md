# Different-model review of PR #44 (fix/forward-l02-unknown-order)

- Prompt: `review/forward-l02-fix/SOL_PROMPT.md` (finding IDs FF44-n instead of SF44-n).
- Sol High (`gpt-5.6-sol`, `codex exec -s read-only`) was tried twice on 2026-10-05;
  both runs ended with `ERROR: Selected model is at capacity` before any review
  output. No findings exist from those attempts.
- Reviewer actually used: Fable 5.1, as a Claude subagent, read-only.
- Reviewed diff: `git diff main 30a8bed -- src tests` (commit "Forward paper: L-02 count skips snapshots with an order in flight").

The hand-back is reproduced verbatim below.

---

Reviewer model: claude-fable-5-1

Verdict: FIX. It is a small fix, and the crash repair itself is correct.

The fix does stop the crash. Skipping an in-flight snapshot is the right choice in the ordinary case. One rarer path still produces a silently wrong L-02 line, and the new docstring makes a claim that is false on that path. Details follow.

Evidence (read-only; test artifacts went to a scratchpad --basetemp, `git status` is clean afterwards):
- With the fix, `pytest tests/integration/test_forward_paper.py`: 21 passed.
- I extracted main's `src` (`git archive main src`) to the scratchpad and ran the new test against it with PYTHONPATH (I checked that `aqt.__file__` resolved to the old copy). Result: 1 failed with `reconcile.py:139: ValueError: an order with an unknown outcome has no expected balance`, the same error the server hit. So the test fails on the old code for the right reason.

Answers to the prompt's questions:
1. Ordinary case: skipping is sound. The pre-send save (`paper_loop.py` ~1166, `save(decision_time, LocalRecord(..., {cid: None}))`) differs from the snapshot before it only by the unknown order. Falling back to the earlier snapshot therefore values the known part of the same state. The first journal entry is always `save(ready)`, made before any order (`paper_loop.py` ~1015), so `first` in `daily_equity_returns` cannot move. Closes still bound the loop, so no close gap gets bridged. A midnight decision (the baseline trades at hour 0) saves the in-flight snapshot at exactly 00:00. Skipping it values that midnight before the trade. That matches what happens when execution waits (post-trade save after 00:00). Whether a midnight trade is valued before or after the trade depends on `busy_until`, but that was true before this change.
2. Persistence: an unknown outcome can last past the step (see FF44-1). It does not stall L-02 silently across many hours, because the next `run_step` refuses loudly at `resumed_venue` (`forward.py:203-208`, ForwardError, already alerted, exit 2, no report line). The problem is limited to the report line of the step in which the unknown arose.
3. Other callers: `expected_balances` is called only at `forward.py:213` (already guarded at 203-208) and `forward.py:229` (fixed). `reconcile()` handles `None` itself (`reconcile.py:238-269`). No other caller has the same failure.
4. The test is adequate as a regression test. Its final assertion is weak (FF44-3).

Findings:

FF44-1. Medium. `src/aqt/app/forward.py:218-230` (`snapshots`), together with `daily_equity_returns` at 233-266.
- **Failure scenario:** The docstring says "the snapshot that records the outcome follows it within the same step". That is false on two paths:
  - Executor FREEZE with `result.order is None`: `paper_loop.py` ~1210-1220 keeps `{cid: None}` in `local.orders` and triggers AMBIGUOUS_ORDER.
  - FLATTEN: `safety.py:490` sets `sent[cid]=None` and leaves it there on the generic-exception FLATTEN_FAULT (`safety.py:508-510`); this is the FLATTEN_UNKNOWN path in `paper_loop.py` ~1100.

  On both paths every later save in that step carries the `None`, so every trailing snapshot is skipped. `run_step` still returns a report. `scripts/run_forward_paper.py:108` then calls `l02_count`, which values every midnight after the send that has a close with the pre-send balances. A catch-up step spanning days after downtime can cover several midnights this way. Those daily returns are invented, because the real holdings are unknown, and they go into the L-02 count and the persisted report line. Before the fix this case crashed loudly; now it misvalues silently.
- **Suggested repair:** Keep skipping in-flight snapshots, but stop valuation at the time of the first trailing unresolved snapshot when no resolved snapshot follows it. Example: `snapshots` also returns that cutoff, and `daily_equity_returns` values only midnights at or before it. That matches "a gap is never bridged". Alternatively, report it in the L-02 mapping (e.g. `reason: "unknown order outcome"`). Correct the docstring either way. Do not stop on any in-flight snapshot that is the last one at or before a midnight: that would wrongly truncate the ordinary midnight-decision case from point 1.

FF44-2. Low. Same location (the docstring/semantics is shared with FF44-1).
- **Failure scenario:** An unknown that a FREEZE_EXIT inside the same step later resolves (`leave_freeze`, `paper_loop.py` ~900) leaves the midnights between the send and the resolution valued pre-send. This is rare, and bounded by the in-step resolution.
- **Suggested repair:** Fold it into the FF44-1 repair, or document it as a known approximation.

FF44-3. Low. `tests/integration/test_forward_paper.py:126`, `assert count.as_mapping()`.
- **Failure scenario:** `as_mapping()` returns a non-empty dict, so the assertion is always true. A wrong count (e.g. valuation truncated, or zero returns) would pass. The test only proves "no exception".
- **Suggested repair:** Assert a value. For example, compare against `effective_decisions(daily_equity_returns([s for s in snapshots(...)], ...))` computed from the journal with the in-flight entries removed, or assert `count.raw_decisions > 0` and equality with a replay of the same series. Add a case for FF44-1: an unresolved trailing snapshot must not produce returns after its time.

No other issues found. The diff is minimal, it reuses `_local`, and it mirrors the existing guard in `resumed_venue`.
