# Task 6 — backtester oracle and leakage-canary suite

Date: 2026-09-13

**TASK 6 GATE: PASS. HUMAN DECISIONS: ACCEPTED. ORACLE/CANARY SUITE: FROZEN.**

Task 6 implements only the pre-production mathematical oracles and leakage
canaries mandated before a NumPy reference or production backtester. The suite
is human-approved and frozen by the accepted-file hash manifest after final
Sol High and Astra High review. Task 7 was not started.

Claude was first invoked with the requested model `claude-opus-5-1`; Claude
rejected that name before inference with an unrecognized-model error and zero
usage. The authorized fallback `claude-opus-5` created the initial files, but
the long-running call was interrupted before it returned completion metadata.
The coordinator inspected every created file, found and corrected one false
Spearman test expectation, completed the missing report/README work, and ran
all validation independently. No claim of verified Opus 5 completion metadata
is made.

Claude Fable 5.1 then completed an independent read-only review and returned
PASS with non-blocking findings. Its timing-boundary and documentation findings
were corrected before the final local validation. The full review and verified
model metadata are recorded in `FABLE_5_1_REVIEW.md` and
`FABLE_MODEL_PROOF.json`.

## Scope and ordering

Constitution section 16 fixes this order:

`human spec review -> oracle tests -> leakage canaries -> NumPy reference -> production implementation`

This task contains the oracle and canary layers only. It deliberately contains
no NumPy reference, production adapter, production backtester, performance
engine, validation engine, strategy, model, exchange access, or trading code.
The exact authorization and acceptance criteria are in `authorized-spec.txt`.

## Frozen backtester requirement mapping

| Frozen requirement | Task 6 disposition and evidence |
|---|---|
| 1. Timestamped targets, prices, frozen costs | The private `build_ledger` accepts these primitives; malformed lengths, timestamps, prices, and costs are rejected by `test_ledger_construction_rejects_malformed_input` and the exact cost tests. |
| 2. Decision at close(t), execution at open(t+1) | Segment exposure begins at the next open; `test_buy_and_hold_enters_at_the_first_scheduled_decision`, `test_trades_occur_only_at_scheduled_decision_boundaries`, and the leakage perturbation tests cover the boundary. |
| 3. Clip exposure to `[0,1]` | `clip_exposure` runs before admissibility and ledger accounting; `test_exposure_targets_are_clipped_before_ledger_accounting` and `test_admissibility_uses_clipped_exposure_targets` fix exact lower/upper identities. |
| 4. Cost on absolute exposure change | `test_alternating_exposure_gives_exact_turnover_and_cost`, the entry-cost identity, and exhaustive cost monotonicity tests cover it. |
| 5. Increases at 00:00 UTC and 24h minimum hold | Accepted and rejected paths, exact 24h boundary, and scheduled-anchor tests cover it. |
| 6. Intraday actions only reductions crossing 10pp | Rejected intraday increases/regains and inside-band changes cover it; admissible reductions are used by the scenarios. |
| 7. No partial fills or passive limits | N/A to this pre-production mathematical suite: every target change executes completely at the frozen next-open price. No order/fill simulator or production implementation exists in Task 6. |
| 8. PnL from actual simulated exposure | `test_pnl_follows_the_executed_path_not_the_intended_one` and the clipping identities calculate PnL from the post-execution clipped path. |
| Frozen cost model | Fee, spread, slippage floor/cap/formula, stress multipliers, traded-notional charging, and monotonicity are transcribed and tested exactly. |
| NumPy/reference and production comparisons | D1/D2, deferred by the mandated order; no stub or skipped test claims coverage. |

## Acceptance mapping

| Criterion | Evidence |
|---|---|
| Zero exposure gives zero trading PnL | `test_zero_exposure_gives_exactly_zero_trading_pnl` under all frozen stress multipliers and cost extrema |
| Buy-and-hold analytic identity | exact additive sum and compounded open-price ratio tests, including one charged entry |
| Known alternating exposure gives exact turnover/cost | `test_alternating_exposure_gives_exact_turnover_and_cost` |
| Higher cost never improves identical-path net PnL | rate, stress-multiplier, and exhaustive binary-path monotonicity tests |
| Future-return leakage is absurd; causal lag is not | leak has no losing segment and is the unique exhaustive optimum; the lagged control loses and is suboptimal |
| Shuffled-label OOS null centered near zero | exhaustive permutation means are exactly zero for zero-sum PnL and tie-free Spearman, without an invented tolerance |
| Deterministic canonical metrics | exact rational records use sorted canonical JSON; independent reruns are byte-identical and SHA-256-identical |
| Exposure clipping | out-of-range targets are clipped to `[0,1]` before admissibility and ledger accounting |

The test-private kernel transcribes UTC/hourly scheduling, `[0,1]` exposure,
the 10 percentage-point band, 24-hour risk-increase rule, absolute-exposure
turnover, fallback fee, spread, slippage floor/cap, and cost-stress multipliers.
It imports no `aqt` module and cannot become an accidental production engine.

## Files

- `tests/oracles/__init__.py`
- `tests/oracles/_kernel.py`
- `tests/oracles/test_backtest_oracles.py`
- `tests/canaries/__init__.py`
- `tests/canaries/test_leakage_canaries.py`
- `tests/canaries/test_shuffled_label_null.py`
- `review/task6/authorized-spec.txt`
- `review/task6/LOCAL_REPORT.md`
- `review/task6/IMPLEMENTATION_MODEL.json`
- `review/task6/FABLE_5_1_REVIEW.md`
- `review/task6/FABLE_MODEL_PROOF.json`
- `review/task6/FABLE_DECISION_PROMPT.md`
- `review/task6/FABLE_DECISION_RETRY_PROMPT.md`
- `review/task6/FABLE_DECISION_ROUND2_PROMPT.md`
- `review/task6/FABLE_DECISION_NEGOTIATION.md`
- `review/task6/FABLE_DECISION_MODEL_PROOF.json`
- `review/task6/HUMAN_ACCEPTANCE.md`
- `review/task6/ACCEPTED_ORACLE_HASHES.sha256`
- `review/task6/SOL_DRIFT_REVIEW.md`
- `review/task6/ASTRA_DRIFT_REVIEW.md`
- `review/task6/SOL_HIGH_REVIEW.md`
- `review/task6/CLAUDE_ADVERSARIAL_REVIEW_PACKET.md`
- `review/task6/verify_frozen.ps1`
- `README.md`

## Coordinator correction

The initial test used `reversed(_PREDICTIONS)` as a perfect inverse rank. The
prediction sequence is not sorted, so reversing positions produced exact
Spearman `-31/35`, not `-1`. The corrected test negates each prediction value,
which reverses every rank and therefore has exact correlation `-1`. No
production or scientific rule changed.

Fable's follow-up findings also tightened the lagged leakage control so its
return endpoint is strictly before the current decision open, exercised the
exact 24-hour increase boundary directly, narrowed an overbroad private-kernel
docstring, and corrected a test name. These changes preserve the authorized
scope and make the claims match the fixtures.

Sol High's final review then found one blocking mismatch missed by Fable: the
private kernel rejected out-of-range exposure targets although frozen
`BACKTESTER_SPEC_v1.md` item 3 requires clipping. The kernel now clips before
both scheduling checks and ledger accounting, with exact boundary tests.

## Validation

Environment: Microsoft Windows 10.0.26200 (`Win32NT`), PowerShell 7.6.5,
pytest 8.4.2, Ruff 0.11.13, mypy 1.20.2, import-linter 2.15, UTC-aware
synthetic fixtures, exact `Fraction` arithmetic, base/HEAD
`816ee1d206a2bfb75f2233f10023dc8e3ae20cbd`.

| Exact command | Exit | Result |
|---|---:|---|
| `.\.venv\Scripts\pytest.exe -q -p no:cacheprovider tests/oracles tests/canaries` | 0 | PASS — 58 passed |
| `.\.venv\Scripts\pytest.exe -q -p no:cacheprovider` | 0 | PASS — 783 passed, 4 skipped; the four pre-existing skips are unrelated to Task 6 |
| `$env:RUFF_CACHE_DIR="$env:TEMP\aqt-ruff-task6-accepted-final2"; .\.venv\Scripts\ruff.exe check .; .\.venv\Scripts\ruff.exe format --check .` | 0 | PASS — lint clean; 32 files formatted |
| `$env:MYPY_CACHE_DIR="$env:TEMP\aqt-mypy-task6-accepted-final"; .\.venv\Scripts\mypy.exe src; .\.venv\Scripts\lint-imports.exe --no-cache` | 0 | PASS — 20 source files; 4 contracts kept |
| `& 'review/task6/verify_frozen.ps1'` | 0 | PASS — trusted inventory/bytes 28/28, sidecars 14/14, Constitution self-hash, manifest bindings 7/7, protocol bindings 7/7 and three nested bindings |
| `git diff --check` | 0 | PASS — no whitespace error |

Cache-writing was disabled or redirected to the system temporary directory
because the repository mount denies tool-cache writes. This changes no check
semantics.

## Accepted decisions and deliberate deferrals

- The owner selected multiplicatively compounded equity as production truth;
  additive fixed-notional PnL remains a diagnostic oracle.
- The owner accepted distinct target and actual held weights, exact fractional
  drift between trades, and next turnover measured from drifted actual weight.
- The owner accepted a flat start, charged initial entry, and no forced terminal
  liquidation in acceptance PnL. Hypothetical liquidation cost is a later
  reporting diagnostic.
- The owner confirmed Task 5's inclusive ULP-aware 10pp convention, applied
  against actual held weight. The exact Fraction oracle has no float tolerance.
- The NumPy comparison and production adapter are deferred by the mandated
  order. No skipped test pretends they exist.
- The protocol's 500-sample real confirmation-data null belongs to a later
  validation-engine task. This task uses exhaustive synthetic symmetry only.

## Scientific and quantitative review

The repository's `scientific-reproducibility-review` and `quant-code-review`
checklists were applied. Inputs are generated locally from fixed literals;
there is no random generator, market/confirmation/lockbox data, concurrency,
floating-point reduction, dependency fallback, I/O, or environment override.
Records use sorted compact UTF-8 JSON under the frozen canonicalization rule,
and reruns compare both bytes and SHA-256 digests. Exact rational fixtures
trace decisions through next-open execution, clipped actual exposure, exact
fractional drift, next turnover, cost, segment return, and both diagnostic and
selected production aggregation. Timing,
look-ahead, cost, scheduling, materiality, no-short/no-leverage bounds, and
scope were reviewed. Partition, schema-boundary, data-lineage, fill-quality,
and production-runtime checks are N/A because Task 6 contains synthetic
test-private oracles only and the ordered production/reference layers do not
yet exist.

Sol High independently reviewed the corrected final snapshot in read-only mode
and returned `LOCAL GATE: PASS` with no remaining technical blocker. Its first
review caught the clipping and evidence defects missed by Fable; the second
review verified their correction. See `SOL_HIGH_REVIEW.md`.

The updated current-snapshot Claude packet is
`CLAUDE_ADVERSARIAL_REVIEW_PACKET.md`. The earlier Fable review is adjudicated;
the packet is ready if a second Claude pass is desired after the human gate.

A later two-round decision negotiation with verified Claude Fable 5.1 found a
materially better fractional-exposure convention: distinguish decision targets
from actual held weights and let held weights drift with returns between trades.
The adjudication is in `FABLE_DECISION_NEGOTIATION.md`, and the owner accepted
it in `HUMAN_ACCEPTANCE.md`. The two exact drift/turnover identities are now
encoded. Final validation, different-model review, and hash pinning remain
required before the suite is declared frozen.

Human acceptance and the independent Sol High and Astra High reviews are
complete. The six accepted oracle/canary files are pinned in
`ACCEPTED_ORACLE_HASHES.sha256`; changing them now requires human rationale and
review. No live trading or Task 7 is authorized by this report.
