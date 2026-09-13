# Task 4 scientific disposition — approved by user

Date: 2026-09-13

Status: **APPROVED BEFORE ANY REGISTERED TRIAL**

The user approved the coordinator's recommendation to preserve the current
Task 4 conventions as the best available choice at this stage. This resolves
`T4-Q1` from the Claude Fable 5.1 external review without changing any frozen
artifact or implementation code.

## Approved Cycle-1 conventions

1. `EMA(close, span=N)` uses `alpha = 2 / (N + 1)`, starts from the simple
   arithmetic mean of the first `N` causal closes, and applies the recursive
   update over every later close through the decision timestamp.
2. `ATR(high, low, close, window=24)` is the simple arithmetic mean of the
   trailing 24 causal true ranges, divided by the current close for `atr_24`.
   Wilder smoothing is not used in Cycle 1.
3. EMA and EWMA depend on the supplied history start. The cycle data manifest
   must bind that start, and reproductions must use the identical ordered bar
   history. This resolves the operational requirement identified as `T4-Q2`.

## Reason for the decision

The frozen feature specification fixes the names and windows but leaves these
calculation details open. The current definitions are causal, deterministic,
documented, independently reviewed, and covered by synthetic tests. Selecting
them before any registered market-data trial avoids post-result tuning and is
the smallest defensible choice. A later formula change would create a new
feature-factory hash and end the active cycle under the frozen specification.

## Bound snapshot

- Approval base commit: `7ebc7f932446075fdedad49339a412cf5b843a6d`
- `src/aqt/features/factory.py` SHA-256:
  `862924a7dbf92f26160b5e7587cca97cc17b2db927c5c96acf5999931658e1d5`
- `tests/unit/test_feature_factory.py` SHA-256:
  `ceebdb108a35f1e091d3c7817987e1fc8fe5dc3f86c98b24d26ec5744dc28e82`
- Fable review SHA-256:
  `a96d114686f5e3ad3bdb033fa0823364ed7a38b3ba48e3dee772b37aee347d33`

This decision approves the current Task 4 scientific convention only. It does
not authorize live trading, access to restricted data, a frozen amendment, or
Task 6.
