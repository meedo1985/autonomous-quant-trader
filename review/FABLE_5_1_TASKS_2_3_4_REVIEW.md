# Fable 5.1 external review — Tasks 2, 3 corrected snapshot, and 4

Date: 2026-09-13

Reviewed repository HEAD: `3054805`

Requested and observed substantive reviewer: `claude-fable-5-1`

Mode: independent read-only review; no edit, commit, push, or Task 6 work

Fable inspected the current source, tests, task reports, applicable frozen
governance, and later Task 5 callers where they could expose an integration
defect. It did not execute commands. Its conclusions were subsequently checked
against the local validation results recorded at the end of this report.

## Task 2 — bar semantics

**Verdict: PASS. No blocker found.**

The implementation matches its recorded scope: UTC and interval alignment,
strictly increasing unique opens, finite and internally consistent OHLCV,
explicit gaps without filling or dropping, and decision at close(t) resolving
to open(t+1). Frozen files are not touched.

Findings:

- `T2-N1` — NON-BLOCKING: the Task 2 report did not retain its own CI run ID;
  later full-suite reports provide transitive execution evidence.
- `T2-N2` — NON-BLOCKING: Task 2 has no `authorized-spec.txt`, unlike later
  tasks, so its original scope authorization is not preserved as a file.
- `T2-N3` — NON-BLOCKING: tests do not separately cover a seconds/microseconds
  decision timestamp, a zero-offset non-UTC decision timestamp, or two holes.
  Fable's code trace found the existing logic handles them.
- `T2-Q1` — QUESTION: the bar types are interval-generic and consumers enforce
  the frozen hourly interval themselves. This is the documented design and no
  current divergence was found.

## Task 3 — corrected cost-model snapshot

**Verdict: PASS. The corrected snapshot closes A1, A2, and A4.**

Fable traced the current code and confirmed that the full prefix through the
decision must be contiguous, the public execution resolver rejects non-hourly
series, and cost arithmetic scales basis points before multiplication and
rejects non-finite results. It also confirmed the five conventions in
`review/task3/SCIENTIFIC_DECISION.md` are applied as approved.

Findings:

- `T3-N1` — NON-BLOCKING: repeated scalar `trade_cost` calls recompute the
  estimator from the beginning. Future backtester work should use a single
  series pass rather than create quadratic execution.
- `T3-N2` — NON-BLOCKING: the corrected commit's CI evidence is stored in the
  next task's report rather than the Task 3 fix report.
- `T3-N3` — NON-BLOCKING: no value-level `trade_cost` test independently checks
  a recursive-regime value, although the estimator handoff itself is tested.
- `T3-N4` — NON-BLOCKING: a direct call to `hourly_log_returns_bps` with an
  entire series also rejects a gap after a prospective decision. Current
  `trade_cost` passes only the causal prefix, so no current defect results.

## Task 4 — causal feature factory

**Verdict: PASS. Scientific sign-off completed after `T4-Q1` disposition.**

All eighteen frozen formulas are represented. Fable found no future leakage,
no volume or calendar input entering a formula, and no current disagreement
between the Task 3 volatility estimator and its Task 4 reuse.

Findings:

- `T4-Q1` — QUESTION REQUIRING SCIENTIFIC DISPOSITION: the frozen text does not
  specify the EMA seed/adjust convention or whether `ATR(..., window=24)` uses
  a trailing arithmetic mean or Wilder smoothing. Current code uses an SMA seed
  for EMA and a trailing arithmetic mean of true ranges for ATR. Preserve the
  implementation only after an explicit approve-as-is decision, or change it
  before the first registered trial. No frozen artifact should be edited.
- `T4-Q2` — QUESTION: EMA and EWMA retain dependence on the supplied series
  start. Reproducibility therefore requires the cycle data manifest to bind the
  series start and every execution to receive identical history.
- `T4-N1` — NON-BLOCKING: `require_cycle1_features` validates names, while the
  value-level no-volume guarantee comes from the factory and invariance tests.
- `T4-N2` — NON-BLOCKING: computing every historical feature row by repeatedly
  rebuilding prefixes is expensive. A future optimized implementation must be
  checked against this module as the reference oracle.
- `T4-N3` — NON-BLOCKING: hourly contiguity checks are duplicated across three
  modules, creating future drift risk but no current divergence.
- `T4-N4` — NON-BLOCKING: tests could document that rolling maximum includes
  the current close and that EMA uses the full supplied history.

### Post-review disposition

The user approved the coordinator's recommendation to preserve the current
EMA seed/recursion and trailing arithmetic-mean ATR definitions before any
registered trial. `review/task4/SCIENTIFIC_DECISION.md` records the exact
conventions, reasoning, and reviewed file hashes. This resolves `T4-Q1`.
The same decision requires the cycle data manifest to bind the supplied series
start, resolving the operational requirement in `T4-Q2`.

## Shared assumptions

- A real-data ingestion policy must decide how to handle historical outages;
  current modules deliberately reject an unresolved hole in their causal prefix.
- Spec hashes do not alone identify code-level conventions. Cycle evidence must
  bind the actual feature, cost, and benchmark code revisions where required.
- Floating functions can differ by a small number of ULPs across platforms;
  approximate unit tests do not establish byte-identical numerical artifacts.
- The approved zero-mean 168-hour estimator is reused by cost, feature, and
  benchmark code, so a later change would affect all three.
- The frozen baseline assumes a decision at close(t) can fill at open(t+1);
  the separate one-bar delay stress remains necessary.

## Independent local validation after review

| Check | Result |
|---|---|
| Full pytest suite | PASS — 725 passed, 4 skipped |
| Ruff lint | PASS |
| Ruff formatting | PASS — 26 files already formatted |
| mypy with writable temporary cache | PASS — 20 source files |
| import-linter without cache | PASS — 4 contracts kept |
| frozen baseline SHA-256 verification | PASS — 28/28 |
| `git diff --check` before adding this report | PASS |

The initial mypy and import-linter invocations attempted to write caches in a
restricted repository location and failed with access errors. Reruns using a
writable temporary cache and `--no-cache` respectively passed. Pytest emitted
only the analogous cache-write warning; all tests completed successfully.

With the recorded scientific disposition, Tasks 2, 3, and 4 pass their review
gates. This review does not authorize live trading, a frozen amendment, or
Task 6.
