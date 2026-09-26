# Task 13 review adjudication

Review: `review/task13/REVIEW.md`, saved unedited from the reviewer's reply.
Reviewer: GPT-6 Astra (`gpt-6-astra`, reasoning effort high), Codex CLI 0.154.0,
session `01a0dd26-7dd0-7723-b6b8-b346e366d00c`, read-only sandbox, 2026-09-26.
Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the implementing model.

## How the review was run

Two earlier attempts in a workspace-write sandbox (sessions
`01a0dd1f-7ba9-7f93-9294-a4c97a1b684f`, `01a0dd20-4113-7fc1-8f20-030328f37a16`)
produced no review: the Codex Windows sandbox failed to start
(`helper_unknown_error: setup refresh had errors`), so the reviewer could not
read files or run commands, and it said so rather than issuing a verdict.
The third run received the full `main...HEAD` diff and check output generated
by the implementer at `56da0aa` in its prompt, and used no tools. **The reviewer
did not rerun the checks itself**, and the review says so.

## Findings

| ID | Severity | Adjudication | Evidence |
|---|---|---|---|
| R-1 | BLOCKER | **Accepted.** | `_write_once` uses a fixed `<name>.part` path and `os.link` shares the inode, so a second concurrent writer's `write_bytes` truncates the just-published artifact before the first unlinks. Narrow (needs two runs on one root) but real, and it breaks section 6 immutability. |
| R-2 | BLOCKER | **Accepted.** | `fetch_monthly_klines` accepts any year and month; only the CLI loop limits months to `EXPLORATION_MONTHS`. A caller can fetch confirmation or lockbox months (2022 onward) into the same root. The guard belongs in the client. |
| R-3 | BLOCKER | **Accepted.** | `urllib_transport` uses `urlopen`, which follows redirects without re-validating the target, so the HTTPS host allow-list in `PublicRequest` covers only the first hop. |
| R-4 | BLOCKER | **Accepted; already recorded.** | Same as the merge blocker in `LOCAL_REPORT.md`: roadmap PR #13 is unapproved. It needs the owner's approval, not a code fix. |
| R-5 | NON-BLOCKING | **Accepted.** | `main()` writes the run summary only after every fetch returns; any raised `DownloadError` exits without one. |

No finding is rejected. R-1, R-2, R-3 and R-5 are to be repaired in a later
commit on this branch; R-4 stays open until the owner approves the roadmap.

## Repairs (Claude Opus 5.5, 2026-09-26)

| ID | Status | Change | Regression test |
|---|---|---|---|
| R-1 | Fixed | `_write_once` writes through a unique `tempfile.mkstemp` file per writer, then `os.link`s it; the temp file is always removed. | `test_concurrent_writer_cannot_change_published_bytes` runs a second writer between link and cleanup: it is refused and the bytes are unchanged. |
| R-2 | Fixed | `fetch_monthly_klines` calls `_require_exploration_month` first, before any disk lookup or request; invalid calendar months are refused too. | `test_months_outside_exploration_are_refused_before_disk_or_network` (2017-07, 2022-01, 2025-06, month 0, month 13), with a planted cached file. |
| R-3 | Fixed | `urllib_transport` uses a module opener with `_RefuseRedirects`, so a 3xx comes back as its status and `_get` stops without retrying. | `test_real_transport_refuses_redirects` (HTTP downgrade, foreign host, `apiKey` query) and `test_module_opener_uses_the_redirect_refusing_handler`; 301/302 added to the stop-without-retry test. |
| R-4 | Open | Needs the owner's approval of roadmap PR #13. | — |
| R-5 | Fixed | The CLI catches `DownloadError`, writes the summary with the records so far and a `failure` entry naming the operation, and exits 2. | `test_cli_writes_a_summary_when_a_run_stops`. |

Mutation check: with the pre-repair `binance_public.py` restored, the R-1, R-2
and R-3 tests fail (10 failures); the R-3 tests partly because the handler does
not exist there. The R-5 test covers the script, which that check left repaired.

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1191 passed, 4
skipped; `ruff check .` pass; `ruff format --check .` 65 files formatted; `mypy
src scripts/download_market_data.py` no issues in 32 files; `lint-imports` 5
kept, 0 broken; `git diff --check` clean; no change under the frozen paths.

Behavior note: if `data.binance.vision` itself answers with a redirect, the
download now stops with `HTTP 30x ... stopping` instead of following it. That
is the fail-closed choice; allowing a redirect would require validating the
target through `PublicRequest` first.

These repairs have not been re-reviewed by a different model.

## Second review: repairs (`REVIEW_2.md`)

Reviewer: GPT-6 Astra (`gpt-6-astra`, reasoning effort high), Codex CLI 0.154.0,
session `01a0dd30-75bf-7680-bc5c-56d4008555e9`, read-only sandbox, no tools.
Input: the first review, this file, implementer-run check output at `f27e908`,
the code diff `5c0d6bc..f27e908`, and the full current module and CLI. The new
tests reached the reviewer only through that diff. The reviewer did not rerun
the checks. Verdict: **FIX**. Saved unedited.

| ID | Reviewer status | Adjudication |
|---|---|---|
| R-1 | RESOLVED | Agreed. |
| R-2 | RESOLVED | Agreed. |
| R-3 | RESOLVED | Agreed. 303/307/308 cases were suggested as optional; not required. |
| R-4 | OPEN | Agreed; owner decision. |
| R-5 | PARTIAL | **Accepted**; the remainder is tracked as R2-1. |
| R2-1 | NON-BLOCKING | **Accepted.** Verified: `http.client.IncompleteRead` subclasses `HTTPException`, not `OSError`, so `_get` neither retries nor converts it (`binance_public.py:156`, `:306`); a malformed sidecar raises `JSONDecodeError`/`KeyError`/`ValueError` from `_existing` (`:354`, `:361`); client construction sits outside the CLI's handler (`download_market_data.py:41`). Repaired below. |

### R2-1 repair (Claude Opus 5.5, 2026-09-26)

- `_get` treats `http.client.HTTPException` (including `IncompleteRead`) as a
  transport fault: retried within the same bound, then a `DownloadError`.
- `_existing` turns an undecodable, non-object, or incomplete sidecar, or one
  with an invalid `as_of_utc` or hash, into `DownloadError("unreadable
  sidecar")`. It never rewrites the sidecar or the artifact.
- The CLI builds the client inside its handler and catches `DownloadError` and
  `OSError`, recording `operation: "start"` for a refusal to start. Other
  exceptions, and a failure to write the summary itself, stay uncaught.

Tests: `test_interrupted_response_is_retried`,
`test_persistent_interrupted_response_is_a_download_error`,
`test_malformed_sidecar_is_a_download_error` (6 cases),
`test_cli_records_a_refusal_to_start`,
`test_cli_records_an_interrupted_response_after_a_success`. With the module and
CLI from `f27e908` restored, all 10 fail; with the repair, all pass.

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1201 passed, 4
skipped; `ruff check .` pass; `ruff format --check .` 65 files formatted; `mypy
src scripts/download_market_data.py` no issues in 32 files; `lint-imports` 5
kept, 0 broken; `git diff --check` clean; no change under the frozen paths.

This repair has not been re-reviewed by a different model.

## Third review: R2-1 repair (`REVIEW_3.md`)

Reviewer: GPT-6 Astra (`gpt-6-astra`, reasoning effort high), Codex CLI 0.154.0,
session `01a0dd3e-a1d8-7700-b61e-78c560d14b87`, read-only sandbox, no tools.
Input: the second review, this file, implementer-run check output at `faf5013`,
the code diff `28ba68c..faf5013`, and the full current module, CLI and test
file. The reviewer did not rerun the checks. Verdict: **FIX**. Saved unedited.

| ID | Reviewer status | Adjudication |
|---|---|---|
| R-1..R-3 | RESOLVED | Agreed. |
| R-4 | OPEN | Agreed; owner decision. |
| R2-1 / R-5 | PARTIAL | Agreed: the three named paths are repaired; the remainder is R3-1. |
| R3-1 | NON-BLOCKING | **Accepted.** Verified in `download_market_data.py`: the progress `print` (`:54`) runs before `records.append` (`:55`), so a stdout `OSError` drops a stored artifact from the summary; the stderr `print` in the handler (`:60`) runs before the summary is written; the final `print` (`:74`) can replace the intended return code. Coverage gaps also confirmed: no test injects a filesystem `OSError`, and none asserts that a summary-write failure propagates. Practical trigger is a failing console stream (for example a closed pipe). Repaired below. |

The reviewer's note that a sidecar-write failure leaves an orphan artifact
that later runs refuse predates these repairs and is the fail-closed behavior
already recorded as T13-02.

### R3-1 repair (Claude Opus 5.5, 2026-09-26)

- Each completed record is appended before its progress line is printed.
- All console output goes through `_say`, which ignores `OSError`: console
  output is diagnostic, and the run summary is the record. The stop message
  and the final line are printed only after the summary is written, so neither
  can prevent the summary or change the return code.
- A failure to write the summary itself still raises.

**Deliberate difference from the reviewer's suggestion.** The review proposed
tests asserting a nonzero result and no further requests after a
progress-write failure. This repair instead treats a broken console as not a
failure: the run continues and the summary lists every record. Stopping a data
download because a terminal closed would lose no data but would add nothing,
and the summary would still be the only record either way.

Tests: `test_cli_broken_console_does_not_change_the_run`,
`test_cli_broken_console_during_failure_still_writes_summary`,
`test_cli_records_a_filesystem_error` (injected `PermissionError` from the
artifact write), `test_cli_summary_write_failure_propagates`, and an exact
request-sequence assertion added to
`test_cli_records_an_interrupted_response_after_a_success`.

Mutation checks: with the CLI from `27b6f0f` restored, the two console tests
fail; the filesystem and summary-write tests pass there, because they cover
behavior that was already correct but untested. With `OSError` removed from
the CLI handler, `test_cli_records_a_filesystem_error` fails, which closes the
coverage gap the reviewer named.

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1205 passed, 4
skipped; `ruff check .` pass; `ruff format --check .` 65 files formatted; `mypy
src scripts/download_market_data.py` no issues in 32 files; `lint-imports` 5
kept, 0 broken; `git diff --check` clean; no change under the frozen paths.

This repair has not been re-reviewed by a different model.

## Fourth review: R3-1 repair (`REVIEW_4.md`)

Reviewer: GPT-6 Astra (`gpt-6-astra`, reasoning effort high), Codex CLI 0.154.0,
session `01a0dd4f-f69f-7df2-a925-7df80f8dad14`, read-only sandbox, no tools.
Input: the third review, this file, implementer-run check output at `1e02d2b`,
the code diff `27b6f0f..1e02d2b`, and the full current CLI and test file. The
reviewer did not rerun the checks. Verdict: **FIX**. Saved unedited.

The reviewer accepted the deliberate design choice (a broken console does not
stop the run) and withdrew its earlier suggestion to stop requests.

| ID | Reviewer status | Adjudication |
|---|---|---|
| R3-1, R2-1 / R-5 | PARTIAL | Agreed; the remainder is R4-1. |
| R-4 | OPEN | Agreed; owner decision. |
| R4-1 | NON-BLOCKING | **Accepted, reproduced.** A child Python 3.14.7 process on Windows that prints through a `_say`-style `try/except OSError` into a closed pipe and calls `sys.exit(2)` exits with **120**, logging `Exception ignored while flushing sys.stdout: OSError: [Errno 22] Invalid argument`. The summary survives; the exit code does not. The in-process tests replace `sys.stdout` with a stream that fails before buffering, so they cannot see this. Repaired below. |

### R4-1 repair (Claude Opus 5.5, 2026-09-26)

When a console write fails, `_say` now calls `_silence`, which points the dead
stream's file descriptor at the null device with `os.dup2`, as the Python
documentation advises for broken pipes. The interpreter's final flush then
succeeds and the intended exit code stands. A stream without a real file
descriptor is left alone, since it has nothing to flush at exit.

Test: `test_cli_exit_code_survives_a_closed_stdout_pipe` runs the real CLI in a
child process whose stdout is a pipe with its read end closed before the child
starts, so the first write fails deterministically. The child uses a fake
transport and opens no socket. It asserts exit code 1 (every month
unavailable in the fake) and a complete summary. With the CLI from `12cbd56`
restored, it fails with exit code 120 and `Exception ignored while flushing
sys.stdout: OSError: [Errno 22] Invalid argument`, the reported defect.

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1206 passed, 4
skipped; `ruff check .` pass; `ruff format --check .` 65 files formatted; `mypy
src scripts/download_market_data.py` no issues in 32 files; `lint-imports` 5
kept, 0 broken; `git diff --check` clean; no change under the frozen paths.

This repair has not been re-reviewed by a different model.
