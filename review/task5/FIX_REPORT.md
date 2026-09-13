# Task 5 — fixes for the Sol High external review

Executed by Claude Opus 5 (`claude-opus-5`) on 2026-09-13 under explicit user
authorization to fix **exactly B1, B2 and B3** from
`review/task5/SOL_HIGH_REVIEW.md` with minimal root-cause changes, and to do
nothing else.

Reviewed state: `b98d9a0`. Base of these fixes: `b98d9a0`.

**EXTERNAL REVIEW OF THE CORRECTED SNAPSHOT: PENDING.**
`review/task5/SOL_HIGH_REVIEW.md` reviewed `b98d9a0` and returned
**LOCAL GATE BLOCKED**. This report describes the implementing model's own
corrections to that state. It is **not** an independent sign-off and it does
not clear the gate: the corrected snapshot has not been re-reviewed by any
independent model, and `task-gate-review`,
`scientific-reproducibility-review`, `quant-code-review` and
`claude-adversarial-review` remain **OPEN** for Task 5.

## Scope of this change

Only the three blockers. No frozen file, no benchmark formula, window,
half-life, target, band value, annualisation constant or benchmark identity was
changed. No other task's code or tests were touched. Task 6 was not started.
No cost, PnL, turnover, fill, backtester, promotion or eligibility logic was
added. No dependency was added; `types.MappingProxyType` and `math.ulp` are
stdlib.

| File | Change |
|---|---|
| `src/aqt/benchmarks/canonical.py` | B1, B2, B3 root-cause fixes plus the conventions they settle |
| `tests/unit/test_canonical_benchmarks.py` | corrected impossible fixtures; added focused regressions |
| `review/task5/SOL_HIGH_REVIEW.md` | new — the external review, recorded verbatim as received |
| `review/task5/FIX_REPORT.md` | new — this report |
| `review/task5/LOCAL_REPORT.md` | one pointer line only; its body still describes `b98d9a0` |

`git diff --stat`: `2 files changed, 339 insertions(+), 31 deletions(-)` for the
two source/test files.

## Findings disposition

| Finding | Disposition |
|---|---|
| **B1** exact 10pp changes can be ignored | **FIXED** |
| **B2** frozen benchmark behaviour is mutable at runtime | **FIXED** |
| **B3** impossible minimum-hold states are accepted | **FIXED** |
| Positive findings | untouched; no formula, identity, causality or scope-boundary behaviour was altered |

### B1 — ULP-aware 10 percentage-point threshold semantics

Root cause: `rebalance` compared `abs(delta) < REBALANCE_BAND_ABSOLUTE`
literally, so a change the frozen documents describe as exactly 10 percentage
points was classified as inside the band whenever binary floating point
rendered it as `0.09999999999999998` — which `0.3 - 0.2`, `0.2 - 0.3`,
`0.7 - 0.6` and `1.0 - 0.9` all do.

Fix: the threshold test is centralized in one new public function,
`reaches_rebalance_band(exposure_change)`, and `rebalance` now calls it. The
comparison is `abs(change) >= REBALANCE_BAND_ABSOLUTE - REBALANCE_BAND_TOLERANCE`
with `REBALANCE_BAND_TOLERANCE = 4 * math.ulp(1.0)` (~`8.9e-16` in exposure
units, ~`1e-13` percentage points).

Why that bound: the error between the decimal difference the frozen documents
name and the float the subtraction produces is bounded by the rounding error of
the two operands plus the rounding error of the subtraction. For exposures in
`[0, 1]` each is at most `ulp(1.0)/2`, so four units in the last place of `1.0`
covers it with room to spare. The slack is many orders of magnitude below any
change the frozen documents could mean to distinguish, so no economically
meaningful behaviour is widened; the band simply stops depending on binary
representation. The frozen band value `0.10` itself is unchanged.

Semantics now recorded as convention 8 in the module docstring: the band is a
threshold on the *decimal* change, not on its binary rendering.

Non-null `reaches_rebalance_band` inputs are checked for finiteness, so a
`nan` or `inf` change raises `CanonicalBenchmarkError` instead of silently
comparing false.

### B2 — immutable exported lookup mappings

Root cause: `SIGNAL_LABELS` and `REQUIRED_HISTORY_BARS_BY_BENCHMARK` were
exported as plain `dict`s. `Final` binds the name, not the object, so a caller
could mutate either mapping and change what an identically named, hash-bound
benchmark reports or what history it refuses to run on, with no code or hash
change.

Fix: both backing `dict`s are now module-private (`_SIGNAL_LABELS`,
`_REQUIRED_HISTORY_BARS_BY_BENCHMARK`) and never written after construction;
the exported names are `types.MappingProxyType` views typed as
`Mapping[BenchmarkId, ...]`. Item assignment and deletion raise `TypeError`, and
no mutator method (`clear`, `update`, `pop`, `popitem`, `setdefault`) is
exposed. Every read path — `benchmark_signal`'s label and warm-up lookups and
`REQUIRED_HISTORY_BARS` — goes through the read-only view.

Residual, stated rather than hidden: the private backing dicts remain reachable
as `canonical._SIGNAL_LABELS` and
`canonical._REQUIRED_HISTORY_BARS_BY_BENCHMARK`. That is the "keep lookup
tables private and immutable" option the review named; deep immutability against
a caller that deliberately reaches into a module's private namespace is not
achievable in Python and is not attempted.

Recorded as convention 9 in the module docstring.

### B3 — impossible minimum-hold states rejected

Root cause: `ExposureState.__post_init__` validated
`last_risk_increase_time` only with `require_utc`, so `00:30 UTC` or
`05:00 UTC` was accepted even though the frozen rules permit a risk increase
only at the scheduled `00:00 UTC` decision. `rebalance` then ran its 24h
minimum-hold clock from that noncanonical origin.

Fix: a non-null `last_risk_increase_time` must now be UTC, aligned to the 1h
`BAR_INTERVAL`, and at `SCHEDULED_DECISION_ANCHOR_HOUR_UTC`. Naive, non-UTC and
unaligned values continue to raise `BarSemanticsError` unchanged, preserving the
documented "bare timestamp" convention; the additional canonical requirement —
the `00:00` anchor — raises `CanonicalBenchmarkError`. The value is rejected,
never normalised or rounded to an anchor.

Recorded as convention 10 in the module docstring.

**Consequence of B3 that a reviewer should see.** Once the anchor is enforced,
a valid `last_risk_increase_time` is always a midnight, and any later scheduled
decision is a whole multiple of 24h away. The only elapsed gap shorter than the
minimum hold that the rules can now reach is **zero** — a second increase
attempt at the very decision that already raised risk, which is what re-applying
`RebalanceDecision.next_state` at the same timestamp produces. The 24h
minimum-hold branch in `rebalance` is therefore defensive for every other gap.
It was left in place: it encodes a frozen rule, and removing it would be a
scope expansion, not a fix. The corresponding tests were rewritten to assert the
reachable case rather than to construct unreachable ones.

## Impossible fixtures corrected

Each of these constructed an `ExposureState` the frozen rules cannot produce.
They were fixtures, not assertions about behaviour, so correcting them changes
no expectation.

| Test | Before | After |
|---|---|---|
| `test_intraday_reduction_across_the_band_is_allowed` | `last_risk_increase_time=_ts(28)` (04:00 UTC) | `_MIDNIGHT` |
| `test_minimum_hold_blocks_an_early_increase` (parametrized 1/12/23h → 23:00/12:00/01:00 UTC) | three unreachable states | replaced by `test_minimum_hold_blocks_a_second_increase_at_the_same_decision`, zero elapsed hours, the only reachable blocking case |
| `test_minimum_hold_permits_a_later_increase` | elapsed `24, 25, 48, 1000` — `25` and `1000` are not whole days, so the origin was 23:00 and 08:00 UTC | elapsed `24, 48, 72, 1008`, all whole days from a midnight |
| `test_minimum_hold_never_blocks_a_reduction` | origin `_MIDNIGHT - 1h` (23:00 UTC) | `_MIDNIGHT`, which also makes the hold *active* (zero elapsed) so the test still proves a reduction is not blocked |
| `test_rebalance_rejects_a_future_last_risk_increase` | `_ts(100)` (04:00 UTC) | `_ts(96)` (00:00 UTC), still after the decision at `_ts(48)` |

`test_walking_a_benchmark_obeys_the_shared_rules` asserted
`drop >= REBALANCE_BAND_ABSOLUTE` on a raw float; it now asserts
`reaches_rebalance_band(drop)`, so the walk uses the same threshold semantics as
the rule it is checking.

## Regressions added

Test functions in `tests/unit/test_canonical_benchmarks.py`: **105 → 125**.

B1:
- `test_the_floating_point_band_hazard_still_exists` — asserts that at least one
  adjacent tenth-step difference really does render below `0.10`, so the
  regressions below cannot silently stop exercising the hazard.
- `test_every_adjacent_tenth_step_increase_reaches_the_band` — all ten adjacent
  tenth-step pairs `0.0/0.1 … 0.9/1.0` as increases; each must be a
  `SCHEDULED_INCREASE` to the target.
- `test_every_adjacent_tenth_step_reduction_reaches_the_band` — the same ten
  pairs as reductions, at a scheduled and at an intraday decision; each must be
  the corresponding reduction action. Both directions of every adjacent pair are
  therefore covered.
- `test_the_representable_neighbour_just_below_the_band_reaches_it` and
  `test_the_representable_neighbour_just_above_the_band_reaches_it` — the two
  `math.nextafter` neighbours of `0.10`, i.e. immediately inside and immediately
  outside, both act.
- `test_a_change_clear_of_the_band_tolerance_is_refused` — `0.10 - 1e-12`, far
  outside the tolerance, still holds; the slack is noise-sized only.
- `test_reaches_rebalance_band_accepts_changes_at_or_past_the_band`,
  `test_reaches_rebalance_band_refuses_changes_inside_the_band`,
  `test_reaches_rebalance_band_rejects_a_nonfinite_change`,
  `test_rebalance_band_tolerance_is_representation_noise_only` — direct unit
  coverage of the centralized comparison, including sign symmetry and the
  tolerance's magnitude.

B2:
- `test_exported_lookup_mappings_reject_assignment`,
  `test_exported_lookup_mappings_reject_deletion`,
  `test_exported_lookup_mappings_expose_no_mutators` — parametrized over both
  exported mappings.
- `test_a_refused_signal_label_mutation_leaves_output_unchanged` — a refused
  mutation attempt leaves two identical `benchmark_signal` calls identical,
  which is the exact drift the review demonstrated.
- `test_a_refused_warmup_mutation_leaves_validation_unchanged` — a refused
  mutation leaves the warm-up value intact and short history still rejected.

B3:
- `test_state_accepts_a_scheduled_midnight_risk_increase` — the reachable states.
- `test_state_rejects_a_risk_increase_away_from_the_scheduled_anchor` — 01:00,
  05:00, 12:00, 23:00 and 05:00-next-day, including the two timestamps the
  review named.
- `test_state_rejects_an_unaligned_risk_increase` — 1, 30 and 59 minutes past
  the anchor.
- `test_state_rejects_a_non_utc_risk_increase` — a `+02:00` offset.
- `test_every_decision_hour_leaves_a_constructible_next_state` — over all 24
  decision hours, whatever `rebalance` records is a valid state, so the tightened
  invariant cannot break the rule's own output.

## Commands executed in this session

| Exact command | Exit | Result |
|---|---:|---|
| `sha256sum -c review/task1/protected-before.sha256sums` | 0 | **PASS** — 28/28 frozen governance files and sidecars byte-identical, including `specs/CANONICAL_BENCHMARKS_v1.md`, `specs/BACKTESTER_SPEC_v1.md`, `protocols/protocol_v1.yaml`, `docs/RESEARCH_CONSTITUTION.md` and `FROZEN_HASHES.json` |
| `git diff --check` | 0 | **PASS** — no whitespace errors |
| `git status --porcelain --untracked-files=all` | 0 | only `src/aqt/benchmarks/canonical.py`, `tests/unit/test_canonical_benchmarks.py` and the `review/task5/` documents; no frozen file, workflow, or config modified |
| `od -c src/aqt/benchmarks/canonical.py \| tail -2` | 0 | ends with exactly one `\n` |
| `od -c tests/unit/test_canonical_benchmarks.py \| tail -2` | 0 | ends with exactly one `\n` |
| line-length scan `^.{89,}$` on both files | — | no matches (88-column `ruff` limit) |
| trailing-whitespace scan `[ \t]+$` on both files | — | no matches |
| CR scan `\r` on both files | — | no matches; LF endings throughout |

## Mandatory checks that could NOT be executed locally — BLOCKER

`python -m pytest`, `ruff format --check .`, `ruff check .`, `mypy src`,
`lint-imports`, `python review/task1/verify_task1.py` and
`pre-commit validate-config` were **not** run in this session.

Cause, unchanged from the Task 1–5 implementation sessions: this Claude Code
session is non-interactive and runs under a permission policy that refuses every
attempt to execute the project interpreter or its console scripts, with no
approval prompt that can be answered. Attempts made in this session, each
rejected with `This command requires approval` / `contains multiple
operations`:

- `.venv/Scripts/python.exe -V` (bash)
- `.venv\Scripts\python.exe -V` (PowerShell)
- `python -V` (PowerShell)
- `& "D:\...\.venv\Scripts\python.exe" -V` (PowerShell)
- `D:/.../.venv/Scripts/python.exe -c "print(1)"` (bash)

`sha256sum`, `git` and `od` are available, which is why the verification above
could run.

**No check was weakened, skipped by choice, or reported as passing without
evidence.** No assertion in `tests/unit/test_canonical_benchmarks.py` has been
executed locally.

Mitigation actually applied: GitHub Actions (`.github/workflows/ci.yml`) re-runs
five of the seven mandatory checks — `ruff format --check .`, `ruff check .`,
`mypy src`, `python -m pytest`, `lint-imports` — on a clean Linux Python 3.12
runner. Those CI runs are the **only** execution evidence for those five checks.

Still **not** verified anywhere for these fixes:
`python review/task1/verify_task1.py` and `pre-commit validate-config`. Both are
Task 1 evidence tooling; their frozen-hash assertions were independently
re-verified above with `sha256sum` (28/28 OK), and this change adds no import
edge at all (only stdlib `types` and the already-imported `math` are used, and
`aqt.data.bars.require_utc` is no longer imported because
`require_aligned_utc` subsumes it). The two commands themselves are recorded as
**unverified, not passing**.

### CI evidence for the corrected snapshot

| Run | Commit | Result |
|---|---|---|
| [34739517692](https://github.com/meedo1985/autonomous-quant-trader/actions/runs/34739517692) | `e9dd4d2` | **SUCCESS**, 26s, ubuntu-latest, Python 3.12 |

Per-step output of run `34739517692`:

| CI step | Exact output |
|---|---|
| `ruff format --check .` | `26 files already formatted` |
| `ruff check .` | `All checks passed!` |
| `mypy src` | `Success: no issues found in 20 source files` |
| `python -m pytest` | `725 passed, 4 skipped in 7.92s` |
| `lint-imports` | `Analyzed 20 files, 5 dependencies.` / `Contracts: 4 kept, 0 broken.` |

Against run [34738503803](https://github.com/meedo1985/autonomous-quant-trader/actions/runs/34738503803)
on the reviewed commit `b98d9a0` (`630 passed, 4 skipped`), the delta is
**+95 passing cases**, with the skip count, source-file count (20), dependency
count (5) and all four frozen import contracts unchanged. The +95 is the net of
the added regressions (all ten adjacent tenth-step pairs as increases, the same
ten as reductions at two decision hours, the neighbour and tolerance cases, the
band-helper unit cases, six mapping-immutability cases, and the risk-increase
timestamp cases) minus the three unreachable minimum-hold fixtures that were
replaced by one reachable case. No test was deleted without a replacement that
asserts the same rule on a state the frozen rules can actually produce.

The only annotation is the runner-level `Node.js 20 is deprecated` notice for
`actions/checkout@v4` and `actions/setup-python@v5`. It is infrastructure
deprecation, unrelated to this change, and the CI workflow was not modified,
because that is outside the authorized scope.

Nothing here should be read as a claim that a check passed before its run
reported success. Local execution of these five commands remains **blocked**;
CI is the evidence.

## Status

B1, B2 and B3 are fixed at the root cause. Impossible fixtures are corrected and
focused regressions are added. Mandatory local validation remains blocked by the
session permission policy; remote CI is the substitute execution evidence for
five of the seven commands.

**EXTERNAL REVIEW OF THE CORRECTED SNAPSHOT: PENDING.** The Task 5 local gate is
not cleared by this report. Task 6 was not started. No commit was amended,
force-pushed, or merged.
