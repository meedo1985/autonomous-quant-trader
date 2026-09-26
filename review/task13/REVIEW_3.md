# Task 13 third adversarial review

Reviewer: GPT-6 Astra.
Scope: supplied diff and source through `faf5013`; no tools used.
**Checks were not rerun by me.** The implementer reports 1201 passed, 4 skipped; Ruff, formatting, mypy, five import contracts, and diff checks passed.

## Finding status

- **R2-1 / R-5 — PARTIAL.** The specifically identified interrupted-response, malformed-sidecar, and constructor-refusal paths are repaired. Expected filesystem errors now enter the CLI handler. However, output errors can still omit a completed artifact or prevent summary creation, as detailed below.
- **R-4 — OPEN, OWNER DECISION.** No roadmap PR #13 approval is supplied. It remains a merge blocker; this review grants no approval.
- R-1 through R-3 remain resolved on the supplied evidence.

## New findings

### R3-1 — NON-BLOCKING — `scripts/download_market_data.py:54`

**Progress output can make the failure summary incomplete, and error output can bypass it altogether.** After a successful fetch, `print(..., flush=True)` precedes `records.append(record)`. If stdout raises `BrokenPipeError` or another `OSError`, the new handler records a failure but omits the artifact that was successfully stored. If the handler's stderr write at line 60 also raises `OSError`, execution never reaches summary creation. The final print at line 74 can likewise override the intended return code after writing the summary.

This is a residual failure-boundary defect exposed by the expanded `OSError` handling; the print ordering itself predates this repair. Append completed records before progress output, and ensure diagnostic-output failures cannot prevent summary writing or the intended error return. Keep summary-write failures explicit.

Add offline fault-injection tests for a progress-write failure after successful storage and a diagnostic-write failure while handling an operational error. Assert the saved records, failure operation, nonzero result, and absence of subsequent requests.

## Regression-test assessment

The new tests are substantive: transient interruption must recover exact bytes; persistent interruption must raise `DownloadError` after three requests and leave no files; malformed metadata must fail without requests or artifact changes; startup refusal must produce an empty summary without requests.

The interrupted-run CLI test checks preservation of the earlier archive and the failing operation. Its assertions would catch loss of the new exception normalization or run-summary handling. The startup test's self-referential error-field comparison is weak by itself, but its separate message, operation, records, and request assertions prevent a vacuous pass.

Coverage remains incomplete: there is no malformed-cache CLI case after an earlier success, no injected filesystem `OSError`, and no assertion that summary-write errors propagate. Removing `OSError` from the CLI handler would leave the supplied new tests passing. The interrupted-run test also lacks an exact request-sequence assertion.

## Cross-cutting assessment

No new look-ahead, silent byte transformation, credential-bearing request, trading path, or import-boundary violation is apparent. Exploration gating and redirect refusal remain intact. Current `exchangeInfo` is not historical filter evidence; August 2017 still needs downstream trimming.

The added exception catches are localized and retain bounded retries and nonzero failure behavior; no new unsafe retry or artifact-corruption path is established. Artifact and sidecar publication remain separate, so a sidecar-write failure can leave an orphan artifact that subsequent runs refuse. That behavior predates this repair.

## Verdict

**FIX** — finish the output-error boundary and its regression coverage. R-4 independently blocks merging pending owner approval. This review has not been written or committed by me; its record must be committed.