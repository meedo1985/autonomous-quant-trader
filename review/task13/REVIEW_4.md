# Task 13 fourth adversarial review

Reviewer: GPT-6 Astra.
Scope: supplied repair diff and source through `1e02d2b`; no tools used.
**Checks were not rerun by me.** The implementer reports 1205 passed, 4 skipped; Ruff, formatting, mypy, five import contracts, and diff checks passed.

## Finding status

- **R3-1 — PARTIAL.** Completed records now precede progress output, and console `OSError` cannot prevent summary creation inside `main()`. Actual process exit remains vulnerable, as described below.
- **R2-1 / R-5 — PARTIAL.** The supplied repairs address the previously identified operational failures and summary omissions; the remaining console exit issue prevents full closure.
- **R-4 — OPEN, OWNER DECISION.** No approval of roadmap PR #13 is supplied. It remains a merge blocker.

## Deliberate design choice

Continuing downloads after diagnostic console failure is reasonable. The summary remains the authoritative record, and suppressing `OSError` only around `print` does not suppress download or filesystem failures. A complete run with `"failure": null` accurately represents this policy. I withdraw the earlier requirement to stop requests solely because progress output fails.

## New finding

### R4-1 — NON-BLOCKING — `scripts/download_market_data.py:37–43,92`

**A real broken pipe can still replace the intended process exit status.** With ordinary buffered stdout connected to a pipe whose reader closes, `print(..., flush=True)` can raise `BrokenPipeError` while leaving pending bytes in the output buffer. `_say` catches that exception but leaves the failing stream installed. After `sys.exit(main())`, CPython flushes standard streams again; a cleanup flush failure changes the exit status to **120**, overriding the intended 0, 1, or 2.

The summary survives, but the repair's return-code guarantee does not. Disable or safely redirect the failed output stream so interpreter shutdown cannot retry its buffered output. Keep summary-write failures explicit.

Add an offline subprocess regression using a real buffered pipe, a deterministically closed reader, and synthetic download responses. Assert both the saved summary and the actual process exit status.

## Regression-test assessment

The console tests are substantive: they require continuation through all 53 months or preservation of the operational failure and completed records. They would catch restoration of the previous console handling.

However, `_BrokenStream.write` raises before buffering anything, and the tests call `main()` directly. They cannot detect R4-1 or validate interpreter shutdown.

The filesystem test checks the failure operation, empty records, request count, and code 2. The exact interrupted-response request sequence meaningfully checks bounded retries and stopping. The summary-failure test exercises directory creation failure; it does not directly exercise file write or close failure, though those currently remain uncaught.

## Verdict

**FIX** — finish the process-level console failure handling and regression coverage. R-4 independently blocks merging pending owner approval.

This review has not been written or committed by me; its record must be committed.