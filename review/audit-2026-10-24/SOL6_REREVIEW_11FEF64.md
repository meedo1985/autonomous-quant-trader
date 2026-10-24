# Sol re-review of the audit repairs (11fef64)

**Reviewer:** Codex CLI v0.162.1, header `model: gpt-6-sol`, `model_reasoning_effort=high`, `-s read-only`, 2026-10-24. Packet: prompt, `git diff origin/main..11fef64 -- scripts src tests`, and pasted whole `scripts/run_forward_paper.py`, `deploy/aqt-paper.service`, `src/aqt/monitoring/alerts.py`, `src/aqt/core/deployment.py`, `telegram.py` lines 215-285, `deploy/RUNBOOK.md` exit/restart lines (its shell cannot run here).
**Recorded and adjudicated by:** Claude Opus 5.5 (`claude-opus-5-5`).

## Verdict: FIX. CA-R1 confirmed closed; four new findings

| ID | Severity | Finding (summary) | Adjudication |
|---|---|---|---|
| CA2-R1 | High | The crash event's `reason` is `str(error)`; a secret in an error text (e.g. `password=hunter2`) is not matched by the redaction's value patterns and reaches every sink. | **Accepted, repaired:** the event carries the type only, plus `strerror` for an `OSError` (the operating system's fixed text, no paths or user data), following `telegram.py`'s rule of never logging exception messages. Tests `test_a_crash_alert_never_carries_the_error_text`; `test_a_crash_is_alerted_then_raised` now uses an `OSError` with a path and expects only `strerror`. |
| CA2-R2 | Medium | `TelegramSink.report()` can raise when a local sink fails while recording a failed send. | **Rejected.** A failing local sink propagates by design (`AlertRouter.emit`: "A sink failure propagates; nothing is swallowed"), and the ledger sink sits before Telegram in the same router, so it fails first anyway. In the new crash path `crashed()` catches it. Not in this change's scope. |
| CA2-R3 | Medium | `subprocess.run` can raise `OSError` (no git) inside `deployment._git`; it escapes `approved_code` as a restartable crash before the loop, not a refusal. | **Accepted, repaired:** `_git` turns `OSError` into `DeploymentError`, so it is a logged exit-2 refusal. Test `test_git_that_cannot_run_refuses`. |
| CA2-R4 | Low | The usage doc said exit 1 means a failed fetch only; `crashed()` promised crashes are "never silent". | **Accepted, repaired:** both texts now say exit 1 is a failed fetch or a crash, and the alert is best effort. |

Left unrepaired: CA2-R2, for the reason above.

## Reviewer's final output (verbatim)

**Verdict: FIX.** Static review of the pasted code only; I did not run commands.

CA-R1 closes the earlier finding. Both `str(error)` and the fallback `print` are inside `BaseException` guards, so neither can replace the original exception from `step()`. An ordinary unhandled exception exits 1 and is restarted by the service. A returned refusal exits 2 and is excluded from restart. `KeyboardInterrupt` and `SystemExit` from `step()` still bypass the new `except Exception` handler.

| ID | Severity | Location | Concrete failure and smallest fix |
|---|---|---|---|
| CA2-R1 | High | `scripts/run_forward_paper.py:149` | `OSError("password=hunter2")` puts that text in the `reason` field. `AlertRouter.emit` runs redaction, but its value patterns do not match this secret, so sinks receive it. Omit exception text from the crash event; retain the exception type. |
| CA2-R2 | Medium | `src/aqt/monitoring/telegram.py:report` | If a Telegram send fails and a local sink raises while recording `ALERT_CHANNEL` (for example, a full ledger disk), `TelegramSink.write()` raises through `report()`. Catch ordinary exceptions from each local reporting sink if the sink must never raise. |
| CA2-R3 | Medium | `src/aqt/core/deployment.py:_git` | PA-2 correctly refuses nonzero `git` results, but `subprocess.run` can raise `OSError` before returning a result. If that happens during a checkout listing, it escapes `approved_code`; the service treats it as a restartable crash instead of a refusal. Convert `_git` invocation errors to `DeploymentError`. |
| CA2-R4 | Low | `scripts/run_forward_paper.py:27,145` | The usage doc says exit 1 means a failed fetch, though an unhandled crash also exits 1. The `crashed()` docstring promises crashes are “never silent,” while failed alerting and failed stderr can leave one silent. State the exit meanings and best-effort alert behavior accurately. |

The supplied runbook and service settings agree on exit 2 versus restartable failure.
