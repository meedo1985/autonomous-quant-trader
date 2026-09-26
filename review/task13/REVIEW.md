# Task 13 independent adversarial review

Reviewer: GPT-6 Astra.
Scope: supplied `main...HEAD` diff only; no tools used.
Checks were **not rerun by me**. Claude Opus 5.5 supplied the results at `56da0aa`, dated `2026-09-26T09:56:47Z`: 1178 tests passed, 4 skipped; Ruff, formatting, mypy, import contracts, and diff checks passed.

## Findings

### R-1 — BLOCKER — `src/aqt/data/binance_public.py:360`
**The shared temporary filename can violate raw immutability.** Two writers use the same `.part` path. After writer A links that inode to the final artifact, writer B can truncate it through `partial.write_bytes(content)` before A unlinks it. The already-published artifact then changes despite exclusive final-path creation; the bytes may also differ from the digest computed before writing. Use a uniquely and exclusively created temporary file per writer, retaining exclusive final publication. Add a deterministic interleaving test proving a second writer cannot change published bytes.

### R-2 — BLOCKER — `src/aqt/data/binance_public.py:229`
**Exploration isolation exists only in the CLI loop.** `fetch_monthly_klines("BTCUSDT", 2022, 1)` constructs a request and can store post-exploration data under the same raw root. The callable client checks neither the exploration range nor valid calendar months, and checks existing files before any partition restriction. Enforce the authorized month range before both disk lookup and transport invocation. Add synthetic tests proving out-of-window requests cannot read cached artifacts, contact transport, or write files.

### R-3 — BLOCKER — `src/aqt/data/binance_public.py:143`
**Automatic redirects bypass request validation.** `PublicRequest` validates the initial URL, but `urllib.request.urlopen` follows redirects without constructing another `PublicRequest`. A redirect can therefore reach an unlisted host or downgrade to HTTP despite the stated HTTPS allow-list guarantee. Reject redirects or validate every destination before following it, using an explicitly controlled opener. Add offline transport-level tests for disallowed-host, HTTP, and forbidden-query redirects; current fake-transport tests never exercise this behavior.

### R-4 — BLOCKER — `review/task13/LOCAL_REPORT.md:12`
**Task authorization remains outstanding.** The supplied report explicitly identifies the roadmap as unapproved and says its approval would authorize Task 13. Passing checks cannot satisfy that prerequisite. Keep this branch unmerged until the required owner approval is recorded; this review provides no authorization.

### R-5 — NON-BLOCKING — `scripts/download_market_data.py:41`
**Failed runs do not reliably produce the promised summary.** Exchange-info failure, checksum mismatch, exhausted retries, or rate limiting raises before summary creation. A run can leave downloaded artifacts without a run-level record of its completed and failed work. Persist a failure summary containing completed records and the failing operation, preserve the nonzero exit, and stop further requests. Add an offline CLI regression test covering failure after one successful archive.

## Other observations

The supplied diff changes no frozen artifacts and introduces no cost, fill, or trading logic. Visible fixtures use synthetic bytes. Existing import-contract results are reported evidence only; they do not establish research isolation for the newly callable downloader.

The current `exchangeInfo` snapshot is explicitly dated at download time. Its use as historical filters would introduce look-ahead; the supplied self-review correctly leaves that consumer restriction for Task 14.

## Verdict

**FIX** — resolve R-1 through R-3 and record the authorization required by R-4 before acceptance. This review record must also be committed under the project rules; I have not written or committed it.