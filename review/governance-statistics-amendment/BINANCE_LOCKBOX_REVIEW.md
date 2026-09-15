# Binance specialist review — future lockbox proposal

**Model:** `gpt-5.6-sol` at high reasoning effort
**Mode:** independent read-only specialist review
**Date:** 2026-09-15
**Verdict:** **PASS WITH CONDITIONS** for retaining a blocked proposal

## Findings

- **BQR-B01 — BLOCKER for activation.** The final specification must reconcile
  frozen “decision-count” language with complete daily Sharpe observations and
  gap handling, and jointly resample candidate and benchmark 1.0x-cost legs.
- **BQR-B02 — BLOCKER for activation.** Diagnostic-only DSR cannot satisfy the
  mandatory 0.95 gate; Binance behavior provides no remedy.
- **BQR-B03 — BLOCKER for activation.** The final specification, implementation
  hash, deterministic streams, and independent references remain unbound.
- **BQR-B04 — RESOLVED IN PROPOSAL.** The experiment engine computes and seals
  the confirmation-derived prediction artifact before target access;
  `lockbox_eval` verifies it and computes the target comparison without receiving
  raw confirmation pairs or replicate diagnostics.
- **BQR-NB01 — Later ingestion requirement.** Use immutable final 1h klines,
  explicit UTC open/close semantics, rejected gaps/duplicates, point-in-time
  symbol status, and sealed provenance. `lockbox_eval` must not fetch from
  Binance or hold exchange credentials.
- **BQR-NB02 — Later cost requirement.** Apply cost multipliers only to total
  modeled fee, spread, and slippage per traded notional and side, independently
  to both legs. Preserve BTC 2.0x eligibility stress, ETH 1.0x sanity, lockbox
  1.0x, exposure `[0,1]`, and separate execution-delay stress. Do not infer fee
  tiers or BNB discounts.
- **BQR-NB03 — Later execution requirement.** Filters, precision, rounding,
  minimum notional, client-order identity, partial fills, commissions, timeout
  recovery, balances, reconciliation, rate limits, time drift, and stream recovery
  are N/A now and mandatory only in their scheduled executor/shadow/canary work.

The proposal selects a preregistered calendar-day target length bound before
target access and fail-closed gaps. The reviewer recommended synthetic or
authorized non-lockbox calibration and fresh official Binance documentation
checks only when exchange integration is implemented. It accessed no network,
credentials, confirmation, or lockbox data and changed no files.
