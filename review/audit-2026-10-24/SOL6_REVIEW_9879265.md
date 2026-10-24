# Sol review of the audit repairs (9879265)

**Reviewer:** Codex CLI v0.162.1, header `model: gpt-6-sol`, `model_reasoning_effort=high`, `-s read-only`, 2026-10-24. Packet: a prompt plus `git show 9879265 -- scripts src tests`.
**Limit:** Sol's local shell failed ("Failed to create unified exec process") and it could not reach the repository, so it reviewed only the diff.
**Recorded and adjudicated by:** Claude Opus 5.5 (`claude-opus-5-5`).

## Verdict: FIX (one finding, CA-R1)

| ID | Severity | Finding (summary) | Adjudication |
|---|---|---|---|
| CA-R1 | High | In `crashed()`, `str(error)` runs before the `try`, and the fallback `print()` is unguarded. An error text that raises (even `SystemExit(2)`, which systemd would not retry) or a failing stderr replaces the original crash. | **Accepted, repaired** in the next commit: the text is built inside the `try`, which catches `BaseException`, and the fallback print is guarded the way `refuse()` guards its own. Test `test_a_crash_whose_text_or_alert_fails_is_still_raised` (an `OSError` whose `__str__` raises `SystemExit(2)`, stderr `None`) fails before the repair and passes after. |

No finding is left unrepaired. Sol's unverified points (refusal exit path, Telegram delivery, redaction, docs) go to a re-review packet that includes the connected code.

## Reviewer's final output (verbatim)

**Verdict: FIX**, based on the supplied diff. This is a limited review: the local shell failed before starting any process, and the repository connector could not access this repo. I could not read the connected code, run tests, or verify redaction and documentation.

- **CA-R1 — High — `scripts/run_forward_paper.py:150–155`.** `str(error)` runs before `crashed()` enters its `try`, and the fallback `print()` is outside its protection. If an exception’s `__str__` raises, no SHUTDOWN alert is sent and that new exception replaces the original. If it raises `SystemExit(2)`, systemd treats the crash as a non-retryable exit. A failed stderr write can also mask the original error. **Smallest fix:** make the notification call best effort at the `main()` catch site, guarding it against `BaseException` before the bare `raise`; test a failing formatter and failing fallback output. Direct `KeyboardInterrupt` and `SystemExit` from `step()` remain outside the `except Exception` handler.

The PA-2 change checks nonzero results from all three git calls. Its new tests cover the two `ls-files` failures, while the new crash test proves only successful ledger delivery. I cannot confirm the refusal exit path, Telegram delivery, secret redaction, or whether the runbook and module docstring remain accurate without the connected files.
