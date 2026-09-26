# Task 14 adversarial review

Reviewer: GPT-6 Astra  
Scope: supplied diff and context for `task14-klines-manifests` against `main`.

Checks were **not rerun by me**. The supplied passing checks and real-data builds were produced by the implementer, Claude Opus 5.5, at `18a1ff9` on 2026-09-26.

## T14-01 verdict

Retain strict exclusion of irregular rows from the complete-hour `BarSeries`, subject to R-1. Shifting timestamps or stretching partial bars would misrepresent the observations; explicit exclusions backed by immutable raw archives are appropriate here.

This is a retrospective data-quality classification, not proof that an outage was knowable at the hour's open. For example, a 12:00 bar ending unexpectedly at 12:29 does not establish that execution at 12:00 was impossible. Decision-at-close(t)/fill-at-open(t+1) consumers must not use that later-discovered irregularity to cancel an otherwise executable opening fill or jump to the next retained bar. No execution consumer is introduced in this diff, so I do not report such leakage as an implemented defect.

## Findings

### R-1 — BLOCKER — `src/aqt/data/klines.py:171`

**Irregular timestamps bypass OHLCV validation.** The early `continue` excludes the row before numeric conversion and `Bar` validation. A shortened row containing `open="nan"`, `volume="abc"`, negative volume, or an impossible high/low therefore becomes an outage record instead of failing the build. With another valid row present, the builder can successfully publish a manifest.

This contradicts the stated T14-01 rule that malformed prices stop the build and disguises malformed input as an accepted outage exclusion. The outage-shape test checks only field count and misses this path.

Validate OHLCV for every row before accepting its exclusion, reusing validation owned by `aqt.data.bars` without changing raw timestamps. Add synthetic cases combining irregular timestamps with invalid numeric values and impossible OHLC relationships; both parsing and manifest construction must fail.

## Verdict

**FIX** — repair R-1 and rerun the required checks. This review is supplied as Markdown only; I have not written or committed its record.