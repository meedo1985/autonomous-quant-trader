# PR #35 Astra re-review of the A2324R-3 repair at `e5837d4` — text-only (ACCEPT)

Date: 2026-09-30. Requested by the owner ("Ok contenue with 1 and 2").

- Invocation: `codex exec -s read-only -m gpt-6-astra -` (codex-cli 0.154.0).
- **Text-only**, as for `ASTRA_REREVIEW_CA4F1BD.md`: the sandbox cannot start
  on this machine. Attached verbatim from `e5837d4`: that record,
  `ADJUDICATION.md`, `reconcile.py`, `machine.py`, `paper_loop.py`, and
  `git diff ca4f1bd e5837d4 -- src tests`. Prompt bundle SHA-256: `79ea8cb453513661e7007a55f4aea4cccdbc68bfb7dac76a8adc59cd2bb9951e`.
- Orchestrator's run of the reviewer's reproduction below at `e5837d4`
  (`.venv/bin/python -B -`, Python 3.14.4): exit 0, printed
  `False 2020-01-01T00:00:10+00:00 {'unknown': None}`; all three asserts held.
- The reviewer's final message follows verbatim.

---

**Verdict: ACCEPT — scoped to the A2324R-3 repair.** A2324R-4 and A2324R-5 remain open.

Reviewer: OpenAI Codex, GPT-6 family; assigned reviewer identity GPT-6 Astra. Exact serving-model suffix is not independently exposed to me.

Reviewed commit: **`e5837d4`**, from the attached source and diff against `ca4f1bd`. Commit identity and attachment completeness were not independently verified.

**Text-only review.** No commands, network access, credentials, restricted data, edits, or commits were used. Constitution, skill texts, and `safety.py` were not attached; I cannot claim independent verification of their requirements or implementation. This final message is the review record for owner relay.

**A2324R-3: CORRECT**

Evidence: `src/aqt/execution/reconcile.py:151–222`.

- `latest` starts at `at` and is carried between orders.
- Each before-sleep reading must be at least `latest`. Otherwise the order remains unresolved, is omitted from `resolved`, and creates a persistent reconciliation difference.
- Each after-sleep reading must exceed its before reading by the positive protocol delay. Consequently, every successful wait preserves monotonicity. A backward or insufficient advance leaves the order unresolved; `max(latest, before, after)` retains the highest observed timestamp for subsequent checks and stamping.
- The final reading is compared with `latest`. A backward final reading adds a difference; `max(latest, now)` prevents backdating. Later successful checks cannot erase earlier differences.

For the exact original sequence **`T`, `T + 10 seconds`, `T`**, the second NOT_FOUND resolves the order as absent, but the final clock check makes **`passed=False`**, with **`report.at=T + 10 seconds`**. Retaining that absence entry in `resolved` does not make the whole report successful: `next_record()` and `settle()` explicitly reject failed reports.

For finite integer query counts and returning callbacks, the repair introduces no infinite loop: each NOT_FOUND increments `answers`, with at most `queries` queries and `queries - 1` sleeps per unknown order. Clock or sleep exceptions propagate rather than producing a passed report.

The final reading occurs after all order queries. With monotonic observed readings, a passed report cannot be stamped before the confirming query. This guarantee concerns the supplied clock observations; it cannot detect unobserved clock movement.

**Paper clock and recovery interaction**

The paper loop’s `_Clock` returns its current value and advances by the supplied sleep duration. Starting a reconciliation clock at `at` satisfies the new inclusive comparison; equal readings are valid outside the required sleep advance. Post-executor reconciliation reuses the executor’s advanced clock and supplies its current value as `at`.

The repair enforces monotonicity within each reconciliation call. It does not enforce chronology across fresh `_Clock` instances; that remaining caller issue is accurately retained as A2324R-4.

The attached prior review states that `exit_freeze` and `override_halt` reject future-dated reports. The corrected timestamp preserves that protection, and the failed report must remain ineligible for recovery. **Those methods’ actual guards cannot be independently rechecked here because `safety.py` is absent.**

**Tests and reproduction**

The new `test_a_clock_that_moves_back_fails_instead_of_backdating` supplies the exact three-reading sequence and asserts failure, the retained `T + 10 seconds` stamp, and the backward-clock difference. The second new test covers a clock initially behind `at`, including omission of the unresolved ID.

The attached test additions do not directly exercise cross-order backward readings or recovery-method rejection; those conclusions rely on source tracing and, for recovery, the prior record.

**Not reproduced (sandbox unavailable).** Exact standalone reproduction:

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
assert not report.passed
assert report.at == at + timedelta(seconds=10)
assert "clock moved backwards during reconciliation" in report.differences
print(report.passed, report.at.isoformat(), dict(report.resolved))
PY
```

**Open dispositions and new findings**

- **A2324R-4:** Accurately marked open. Startup still does not advance `local` to `decision.report.next_record()`. `_reconcile_flatten` still discards completion time and stamps failure transitions at its original `at`. The prior bounded, selling-only scenario remains applicable.
- **A2324R-5:** Accurately marked open. `refuse()` still stamps REFUSE_START at `config.start`, including refusals following waiting reconciliation.
- **New findings:** None established from the supplied texts.

The orchestrator reports `pytest -q`: **1593 passed, 4 skipped**, clean ruff/format/mypy and six import contracts, and both new tests failing on `ca4f1bd` and passing on `e5837d4`. These results were **not independently verified**. Acceptance of this repair does not constitute completion of the executable acceptance gate or owner approval to merge.