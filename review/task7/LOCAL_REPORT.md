# Task 7 local report

Date: 2026-09-13
Base commit: `a1838742f1ed6e204278881efab3dcbd9f875acf` (accepted Task 6)
Initial Task 7 commit: `465e80d`
Implementation model: Claude Opus 5 (`claude-opus-5`, high effort)

Reviewed snapshot: committed Task 7 state at `465e80d` plus the following
working-tree corrections, all included in the final validation run:

- `tests/reference/test_numpy_reference_comparison.py`: formatting correction
  and a direct cost-before-return regression
- `review/task7/LOCAL_REPORT.md`: complete gate evidence
- `review/task7/CLAUDE_ADVERSARIAL_REVIEW_PACKET.md`: refreshed hashes/evidence

## Scope

Task 7 adds only a research/test-side NumPy `float64` reference and synthetic
comparisons against the accepted exact Task 6 oracle. It covers clipped target
exposure, fractional drift of actual held weight, next-open execution, absolute
turnover, cost-before-return, the inclusive 10 percentage point band, UTC
midnight scheduling, the 24-hour minimum hold, intraday reductions, and the
accepted additive/compounded diagnostics. No production backtester or strategy
code was added. No frozen governance file or accepted Task 6 file changed.

NumPy is a development-only dependency because the repository specification
requires a NumPy reference while runtime packages remain unchanged.

## Environment

- Windows / PowerShell, repository-local `.venv`
- OS: Microsoft Windows NT 10.0.26200.0, AMD64
- Python 3.12.10 (64-bit CPython, MSC v.1943)
- NumPy 2.5.3
- pytest 8.4.2
- Ruff 0.11.13
- mypy 1.20.2
- import-linter 2.15

No network, market data, exchange, credential, environment-variable, clock, or
random input is used by the reference or its fixtures. The fixtures are fixed
synthetic values and all reductions execute in deterministic array order.

## Validation evidence

| Check | Result |
|---|---|
| Focused reference tests | `37 passed` |
| Full suite | `820 passed, 4 skipped` |
| Ruff (`tests/reference`) | passed |
| Mypy (`src`, no incremental cache) | passed, 20 source files |
| Import contracts | passed, 4 kept, 0 broken |
| `git diff --check` | passed |
| Frozen v1 audit and Task 6 accepted hashes | unchanged and verified |

Exact final-snapshot commands and exit codes:

```text
.\.venv\Scripts\pytest.exe -q -p no:cacheprovider tests/reference
exit 0 — 37 passed

.\.venv\Scripts\pytest.exe -q -rs -p no:cacheprovider
exit 0 — 820 passed, 4 skipped

.\.venv\Scripts\ruff.exe check .
exit 0 — All checks passed

.\.venv\Scripts\ruff.exe format --check .
exit 0 — 38 files already formatted

.\.venv\Scripts\mypy.exe src --no-incremental
exit 0 — Success, 20 source files
(with `MYPY_CACHE_DIR` set to a task-specific temporary directory)

.\.venv\Scripts\lint-imports.exe --no-cache
exit 0 — 4 contracts kept, 0 broken

git diff --check
exit 0

& review/task6/verify_frozen.ps1
exit 0 — 28/28 trusted bytes and exact inventory; 14/14 sidecars;
Constitution self-hash and all manifest/protocol/nested bindings passed

PowerShell:
$bad=@(); $count=0
Get-Content -LiteralPath 'review/task6/ACCEPTED_ORACLE_HASHES.sha256' |
  ForEach-Object {
    if($_ -match '^([0-9a-f]{64}) \*(.+)$') {
      $count++
      $expected=$Matches[1]
      $path=$Matches[2]
      $actual=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLower()
      if($actual -ne $expected) { $bad += $path }
    }
  }
if($bad.Count) { Write-Error ("FAIL: " + ($bad -join ', ')); exit 1 }
Write-Output "PASS: $count/$count accepted Task 6 oracle/canary hashes"
exit 0 — 6/6 accepted Task 6 oracle/canary hashes
```

The four skips are the two parameterized constant-benchmark cases at
`tests/unit/test_canonical_benchmarks.py:767` and `:777` (two cases each): a
constant benchmark needs only the decision bar. They predate Task 7 and are
intentional test branches, not missing Task 7 coverage.

The first review of commit `465e80d` found a Ruff formatting failure and two
trailing-space failures in this report. Both were corrected before the final
commands above were run. Sol High also requested a direct assertion of the
observable intra-segment cost ordering; that regression was added before the
final 37/820-test runs. No scientific convention changed.

The reference comparison bounds are derived from binary64 unit roundoff
(`2**-53`) and the operation graph in `_error_bounds.py`; they are not trading
or performance thresholds. Discrete trade/HOLD decisions are asserted exactly.

## Changed files

- `pyproject.toml` (NumPy in the development extra only)
- `README.md` (Task 7 status only)
- `tests/reference/__init__.py`
- `tests/reference/_numpy_reference.py`
- `tests/reference/_error_bounds.py`
- `tests/reference/_fixtures.py`
- `tests/reference/test_numpy_reference_comparison.py`
- `tests/reference/test_reference_band_tolerance.py`
- `review/task7/AUTHORIZED_SPEC.md`
- `review/task7/OPUS_PROMPT.md`
- `review/task7/LOCAL_REPORT.md`
- `review/task7/CLAUDE_ADVERSARIAL_REVIEW_PACKET.md`
- `review/task7/SOL_HIGH_REVIEW.md`

## Reviewed implementation hashes

```text
8263a407fdc5f0652c71bdc44319d1d62e856931df341d75c6d31e86c49fc59f  pyproject.toml
d48e6f5b53b687a2401767ebb9232fee539d34f9e7f552d3ff3718e441b902ed  README.md
68a65e8f80eb34381cad798f69d970007a78db48d1fc4b5f9123d8a853fee3f1  tests/reference/__init__.py
ee578ccff74212c9707505a2d7fa8b9f56edafa1cbe08f71ea707df3aa49e873  tests/reference/_error_bounds.py
c9c47299739433178faef51a004e97d20ccd6e11fb404d1caa8607860346ec1d  tests/reference/_fixtures.py
0127a73db2bea2cfdefc38f0f91d42c598bfad5b3f2830110c63f02241672c42  tests/reference/_numpy_reference.py
14416d40f905eed12786ae9e01ce679de35f028d1b1a11898144a3f463faaf61  tests/reference/test_numpy_reference_comparison.py
14c307799c549635d09d54f234871fd101bc24c03c13f342fd81a40214495213  tests/reference/test_reference_band_tolerance.py
41b139b234571eeead61371fc23ab82eb16a694ca9cc251c0e1257e42dc4c018  review/task7/AUTHORIZED_SPEC.md
91d150538e336bde0e16221c418d24634d2384afdedf03da50833afe6fa8c7c9  review/task7/OPUS_PROMPT.md
```

`LOCAL_REPORT.md`, the adversarial packet, and `SOL_HIGH_REVIEW.md` are excluded
from this list because they describe the reviewed snapshot and therefore cannot
contain stable self-hashes.

No commit or push was performed by the Claude implementation run. The
coordinator committed and pushed the initial Task 7 snapshot, then corrected
the two review-only formatting findings described above. Task 8 was not
started. Claude packet status: `READY FOR REVIEW`; no separate Claude review
result is claimed because Claude Opus 5 authored the implementation. Sol High's
different-model independent review is recorded in `SOL_HIGH_REVIEW.md` and
returned `PASS`. The owner authorized continuation after Task 7 review.

`LOCAL GATE: PASS`
