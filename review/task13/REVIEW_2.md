# Task 13 repair re-review

Reviewer: GPT-6 Astra.
Scope: supplied repairs through `f27e908` and current source; no tools used.
**Checks were not rerun by me.** Implementer reports 1191 passed, 4 skipped; Ruff, formatting, mypy, import contracts, and diff checks passed.

## Original findings

- **R-1 — RESOLVED.** Each writer receives an exclusively created temporary file. The file handle closes before linking and unlinking, avoiding the usual Windows open-file deletion problem. Exclusive final publication remains intact. **Regression test: effective** against the original shared-inode corruption; it actually interleaves publication with a competing write and checks final bytes and cleanup.

- **R-2 — RESOLVED.** The exploration/calendar guard precedes URL construction, cache lookup, and transport. **Regression test: effective** against removal or relocation behind `_existing`: the planted artifact would otherwise raise a different error. It also checks no requests or additional files. It does not directly instrument reads, so it cannot prove absence of every possible premature disk access.

- **R-3 — RESOLVED.** Supplying the redirect-handler subclass to `build_opener` replaces the default redirect handler; its refusal prevents following destinations. No handler-order bypass is apparent. **Regression tests: effective** for the supplied 302 destinations, with a separate production-opener wiring assertion. They exercise urllib processing, not merely a fake client response. Additional 303/307/308 cases would strengthen coverage but are not necessary to establish this repair.

- **R-4 — OPEN, OWNER DECISION.** Roadmap PR #13 approval remains outstanding in the supplied evidence. Keep the branch unmerged; this review provides no authorization.

- **R-5 — PARTIAL.** Fetch-time `DownloadError` now preserves completed records and the failing operation, stops requests, and returns 2. Other expected operational failures still bypass summary creation. **Regression test: effective but narrow**: the wrong checksum filename triggers a real `DownloadError`, and the assertions catch removal of the summary handling or continued requests. It does not exercise a digest mismatch, startup failure, filesystem error, or interrupted response read.

## New findings

### R2-1 — NON-BLOCKING — `scripts/download_market_data.py:54`
**The failure-summary boundary remains incomplete.** This is a residual R-5 gap, not evidence that the repairs introduced a new corruption path.
- At `src/aqt/data/binance_public.py:156`, a truncated HTTP response can raise `http.client.IncompleteRead`. It is not an `OSError`, so `_get` does not retry or convert it to `DownloadError`; the CLI exits without recording earlier completed downloads.
- Cached sidecar decoding/validation and filesystem operations can raise other uncaught exceptions, including `JSONDecodeError`, `ValueError`, and `PermissionError`.
- Client construction at `scripts/download_market_data.py:41` is outside the handler, so even its credential-refusal `DownloadError` bypasses the promised summary.
Normalize expected operational failures or handle them at the run boundary, including initialization. Preserve fail-closed behavior and nonzero exit. Add offline tests for an interrupted response and malformed cached metadata after a successful archive, plus initialization refusal. Summary-write failure itself must remain an explicit error.

## Cross-cutting assessment

No new look-ahead, silent byte transformation, trading action, or credential-bearing request is introduced by the supplied repairs. Current `exchangeInfo` remains unsuitable as historical filter evidence; August 2017 still requires downstream boundary trimming. Import-contract success is implementer-reported, not independently verified. No additional repair-induced Windows temporary-file or handler-order defect was established.

## Verdict

**FIX** — R-1 through R-3 are resolved; finish R-5's operational failure handling. R-4 independently remains a merge blocker pending owner approval. This review content has not been written or committed by me; the required review record must be committed.