# Astra independent review — Tasks 5 and 7

Date: 2026-09-14
Reviewed HEAD: `8f061a06ff8a20b0105a00502f0ddfab035e2c1c`
Requested reviewer: GPT-6 Astra, high reasoning
Mode: combined, independent, read-only AI review

**Task 5: PASS. Task 7: PASS. No blockers or unresolved questions.**

The reviewer used one combined session, one focused test run, one full test
run, and one combined static/integrity gate. It used no subagents, web search,
Claude call, edit, commit, push, or Task 9 work. The reviewer configuration was
GPT-6 Astra High; no separate backend `modelUsage` attestation was exposed to
the review agent. This is an AI review, not human approval or trading
authorization.

## Task 5 conclusion

The prior Sol blockers remain resolved:

- The inclusive 10 percentage-point threshold uses the accepted
  `0.10 - 4 * ulp(1.0)` representation convention and has adjacent-float,
  signed, boundary, and clearly-interior coverage.
- Exported benchmark mappings are read-only and no production path mutates the
  private backing dictionaries.
- Risk-increase timestamps require aligned UTC midnight; future timestamps are
  rejected, reductions preserve the clock, and repeated same-time increases
  are blocked.

Benchmark identities, strict trend/momentum comparisons, warmups
`1/1/169/4800/4321`, causal history slicing, full-history gap rejection, and
Task 3/4 EWMA equivalence remain intact. No Task 5 code or dependency drift was
found after fix commit `e9dd4d2d170395ff6ab083141b582ab5d5fbf2d9`.

## Task 7 conclusion

The NumPy simulation remains independent from production `aqt` code and from
the exact-oracle computation. Exact-rational error propagation for inputs,
addition, multiplication, division, clipping, and fractional drift is sound
for the documented fixture domain. Bounds are rounded upward, discrete
decisions are exact, branch margins are separately proven, and non-vacuity
tests reject `1e-9` perturbations while fixture bounds stay below `1e-10`.

Requested, clipped, held, and executed exposure remain distinct. Turnover,
cost-before-return, entry cost, no forced liquidation, scheduling, minimum
hold, and reductions match the accepted oracle. Fixed-order reductions and
byte/hex rerun checks support determinism. No Task 7 reference or dependency
drift was found after corrected gate commit
`e7538b2e90399dadcb115d6ee2cd4768692d55e5`.

## Non-blocking findings

### T7-N1 — Direct aggregate-centre regression

`tests/reference/test_numpy_reference_comparison.py` compares exact
per-segment bound centres with Task 6 but does not repeat direct equality for
all six aggregate centres. The aggregate formulas match the oracle by
inspection and their observed NumPy values satisfy the derived bounds. This is
optional future regression coverage, not an accounting defect.

Disposition: accepted as non-blocking. No duplicate test was added to the
already accepted reference snapshot.

### T7-N2 — Truncation test description is broader than its proof

The truncation regression removes the last segment and proves earlier outputs
are unchanged. It does not independently prove that a decision ignores its
own following open because that open exists in both compared runs. Direct code
order decides exposure before applying the segment return, exact-oracle action
agreement adds an independent check, and the later Task 8 causal production
tests cover price availability explicitly.

Disposition: accepted as non-blocking. The description can be narrowed if the
test is edited for another reason; no code defect was found.

## Independent validation

```text
.\.venv\Scripts\pytest.exe -q -rs -p no:cacheprovider
  tests/unit/test_canonical_benchmarks.py tests/reference
exit 0 — 556 passed, 4 skipped in 22.23s

.\.venv\Scripts\pytest.exe -q -rs -p no:cacheprovider
exit 0 — 845 passed, 4 skipped in 35.21s

.\.venv\Scripts\ruff.exe check . --no-cache
exit 0 — all checks passed

.\.venv\Scripts\ruff.exe format --check . --no-cache
exit 0 — 42 files formatted

.\.venv\Scripts\mypy.exe src --no-incremental
exit 0 — 21 source files

.\.venv\Scripts\lint-imports.exe --no-cache
exit 0 — 4 contracts kept, 0 broken

git diff --check
exit 0

& .\review\task6\verify_frozen.ps1
exit 0 — 28/28 trusted bytes, 14/14 sidecars, all bindings passed

Strict accepted Task 6 SHA-256 verification
exit 0 — 6/6 hashes; no history drift

.\.venv\Scripts\pre-commit.exe validate-config
exit 0
```

The four skips are the existing CASH/BUY_AND_HOLD warm-up branches at
`tests/unit/test_canonical_benchmarks.py:767` and `:777`, two cases each.
An initial command using the nonexistent `.venv\Scripts\python.exe` failed
before test collection; the repository console launchers then completed every
recorded check. The write-producing historical `verify_task1.py` was not run
in this read-only review; its relevant frozen and import checks were covered by
the current gates.

## Reviewed hashes

```text
d92fc9c2a9d261ccc726a4f8fd9f2369afa9f723a6e4dd9c80d19ad5ed31eea6  src/aqt/benchmarks/canonical.py
cb47d5fd42f621bee451550de5c334c0ee80fdfac65073633cbe54fb3c71a44f  tests/unit/test_canonical_benchmarks.py
0127a73db2bea2cfdefc38f0f91d42c598bfad5b3f2830110c63f02241672c42  tests/reference/_numpy_reference.py
ee578ccff74212c9707505a2d7fa8b9f56edafa1cbe08f71ea707df3aa49e873  tests/reference/_error_bounds.py
c9c47299739433178faef51a004e97d20ccd6e11fb404d1caa8607860346ec1d  tests/reference/_fixtures.py
14416d40f905eed12786ae9e01ce679de35f028d1b1a11898144a3f463faaf61  tests/reference/test_numpy_reference_comparison.py
14c307799c549635d09d54f234871fd101bc24c03c13f342fd81a40214495213  tests/reference/test_reference_band_tolerance.py
8263a407fdc5f0652c71bdc44319d1d62e856931df341d75c6d31e86c49fc59f  pyproject.toml
a754965c6779cb8c23126a75512506a9c626f2264b99758322934151cc6d2aae  review/task6/ACCEPTED_ORACLE_HASHES.sha256
```

`TASK 5 REVIEW: PASS`

`TASK 7 REVIEW: PASS`
