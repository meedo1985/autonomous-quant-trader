# Sol re-review 2 of the audit repairs (de3c9ff)

**Reviewer:** Codex CLI v0.162.1, header `model: gpt-6-sol`, `model_reasoning_effort=high`, `-s read-only`, 2026-10-24. Packet: prompt with the adjudication of round 2, `git diff 11fef64..de3c9ff -- scripts src tests`, `run_forward_paper.py` lines 1-30 and 140-215, `deployment.py` lines 75-145 (pasted; its shell cannot run here).
**Recorded and adjudicated by:** Claude Opus 5.5 (`claude-opus-5-5`).

## Verdict: FIX. CA2-R3 closed, CA2-R2 rejection judged sound; two findings

| ID | Severity | Finding (summary) | Adjudication |
|---|---|---|---|
| CA3-R1 | High | `OSError.strerror` is chosen by whoever raises the error, so `OSError(errno.EIO, "password=hunter2")` still puts a secret in the alert. | **Accepted, repaired another way:** the reason is `os.strerror(error.errno)`, the operating system's own words for the number, never text the raiser chose; `None` when there is no number. This keeps the useful "No space left on device" that Sol's smallest fix (type only) would drop. Test `test_a_crash_alert_never_carries_the_error_text` now raises exactly Sol's example and checks the secret is absent and the reason is `os.strerror(errno.EIO)`. |
| CA3-R2 | Medium | The usage doc says any other error is alerted, but the handler covers only `step()`; e.g. an error in `load_config()` is not alerted. | **Accepted, repaired:** the doc says "any other error during a step". |

No finding is left unrepaired.

## Reviewer's final output (verbatim)

**Verdict: FIX.** CA2-R3 is closed: `_git()` now turns an `OSError` into `DeploymentError`, which `main()` handles as a refusal. CA2-R2’s rejection is sound under the stated `AlertRouter` contract and sink order: a local sink failure propagates, and `crashed()` catches an alert failure while the caller re-raises the original exception.

- **CA3-R1 — High — `scripts/run_forward_paper.py:153`.** CA2-R1 is still open. `OSError.strerror` is supplied by the exception creator; it is not necessarily fixed operating-system text. For example, `OSError(errno.EIO, "password=hunter2")` puts the secret in the crash alert. Smallest fix: record only the exception type and set `reason` to `None` for `OSError` too; update the disk-error test accordingly.
- **CA3-R2 — Medium — `scripts/run_forward_paper.py:26`.** The new documentation says any other error is alerted, but the crash handler surrounds only `step()`. For example, an unexpected exception from `load_config()` exits without a `SHUTDOWN` alert. Smallest fix for the documentation repair: say that unexpected errors **during a step** are alerted.

This is a review of the pasted material; I did not run checks.
