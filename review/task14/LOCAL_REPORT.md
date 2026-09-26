# Task 14 local implementation and gate report

Date: 2026-09-26
Base commit: `64aee5f` (`main`)
Branch: `task14-klines-manifests`
Author and reviewer: Claude Opus 5.5 (`claude-opus-5-5`), coding AI. This is a
**self-review**, not an independent one.

## Authority

Task 14 is authorized by the owner's approval of the roadmap
(`review/roadmap/OWNER_APPROVAL.md`, merged as `1f852df`). Task 13 is merged
(`8035d59`), and the owner's Q3/Q4 answers are recorded
(`review/roadmap/OWNER_ANSWERS_Q3_Q4.md`). The produced manifest hashes are
**not** bound into any cycle record; that is a `cycle_start_bindings` act,
which `KEEP_BLOCKED` forbids and this task does not touch.

## Scope

- `src/aqt/data/klines.py` (new): strict parser from Task 13's raw archives to
  `aqt.data.bars.Bar`, sidecar verification, and `build_exploration_manifest`.
- `scripts/build_manifests.py` (new): CLI; writes the canonical manifest and a
  build report per symbol, write-once.
- `tests/unit/test_klines.py`, `tests/integration/test_exploration_manifest.py`
  (new): 27 synthetic tests.

No existing module, frozen artifact, or import contract changed. Size: 717
added lines, of which about 330 are tests, against the roadmap's ~400 target.

## Decision for review: outage rows (T14-01)

Real Binance archives are not a clean hourly grid. Both symbols contain **56
irregular rows out of 38,222**, at the same moments in both: bars cut short by a
maintenance stop (for example 2017-12-18 12:00 closing at 12:29:13), about 43
bars on a `:28:14` offset after the 8-11 February 2018 maintenance, one bar
1 ms past the hour (2017-09-06 15:00), and one closing before it opens
(2020-12-21 14:00, zero volume).

**Rule implemented.** A row is regular only if it opens exactly on the hour and
closes exactly 1 ms before the next hour. Any other well-formed row is an
**outage row**: it becomes no bar, it is listed in the build report with file,
line, raw times, and reason, and the hours it would have covered fall into the
declared gaps. Nothing is shifted onto the hour grid or stretched to a full
hour. Malformed rows (field count, non-millisecond times, unparsable or
impossible prices) still stop the build.

**Why.** Constitution section 6 says outages are untradeable and forbids silent
correction. Shifting the offset bars or stretching short bars would be
correction, and would also change what `close(t)` means for the decision rule
in `specs/BACKTESTER_SPEC_v1.md` item 2. The rule is strict with no tolerance:
it also excludes 2021-08-13 01:00 (closes 999 ms early) and 2021-12-24 04:00
(about 5 s early). A tolerance would be a new judgment; it is not introduced
here. This rule is a data-semantics choice made by the coding AI and should be
reviewed as such.

## Result on the real exploration data

Run by the coding AI under the owner's Q4 reading, on the archives it
downloaded (106 of 106 available, exit 0):

| Symbol | Bars | Outage rows | Gaps | Gap hours | Manifest SHA-256 |
|---|---|---|---|---|---|
| BTCUSDT | 38,166 | 56 | 31 | 186 | `8106b1a6cd3a67bcd27164d8a7bddafa0d854fbac529d0a8db58db2b1e76133a` |
| ETHUSDT | 38,166 | 56 | 31 | 186 | `1cae2699ab1fe90dc765c3d2a4514ef7e4cb1deb549206fa133c4de0f893db4f` |

Parser code SHA-256 (LF-normalized source): `91f63d51eb6589fe4641812e74f5a8639cac0a3e0a9b4d9426c19548781f7703`.

Checks: bars + gap hours = 38,352 = every hour of `[2017-08-17, 2022-01-01)`;
rows − outage rows = bars; the 31 gaps are identical for both symbols; no bar
lies outside the window; a rebuild is byte-identical (write-once no-op). The
largest gap is 2018-02-08 00:00 to 2018-02-11 04:00 (76 h); the leading gap is
the 4 h before trading began on 2017-08-17. Fees, exchange filters, and symbol
status are recorded `UNAVAILABLE` (T13-01: the only `exchangeInfo` snapshot
postdates the window, and the manifest builder rejects it anyway). Outputs are
under the git-ignored `data/processed/manifests/`.

## Acceptance criteria (roadmap Task 14)

| # | Criterion | Evidence |
|---|---|---|
| 1 | Synthetic archive round-trips to the exact `BarSeries` | `test_archive_round_trips_to_exact_bars` |
| 2 | Malformed row raises; no partial series | `test_malformed_row_raises_and_returns_nothing` (8 cases), `test_empty_wrongly_named_or_corrupt_archives_raise`, `test_outage_rows_are_still_checked_for_shape` |
| 3 | Rebuild gives byte-identical canonical JSON and hash | `test_build_is_deterministic_and_verifies`; real-data rebuild |
| 4 | Lockbox refused before any file is read | `test_other_partitions_are_refused_before_any_file_is_read` (patches `Path.read_bytes` and `Path.exists` to fail) |
| 5 | Confirmation refused by the CLI | `test_cli_refuses_confirmation_and_writes_nothing`; the library refuses it too |
| 6 | Holed archive gives `Gap` records covering exactly the missing intervals | `test_gaps_cover_exactly_the_absent_hours` (leading, internal, trailing) |
| 7 | `verify_partition_manifest` accepts, and rejects a flipped byte | `test_a_flipped_hash_byte_is_rejected` |

Also: outage-row shapes seen in the real data (`test_outage_rows_become_no_bar_and_are_reported`), tampered archive refused, write-once CLI output, window constants checked against `protocols/protocol_v1.yaml`, and parser identity independent of checkout line endings.

## Validation

Environment: Windows 11, `.venv` Python 3.14.7.

| Command | Exit | Result |
|---|---|---|
| `python -m pytest -q` | 0 | 1233 passed, 4 pre-existing skips |
| `ruff check .` | 0 | all checks passed |
| `ruff format --check .` | 0 | 69 files already formatted |
| `mypy src scripts/download_market_data.py scripts/build_manifests.py` | 0 | no issues in 34 source files |
| `lint-imports` | 0 | 5 kept, 0 broken |
| `git diff --check` | 0 | clean |

Frozen verification: `git diff main` over `docs/`, `protocols/`, `schemas/`,
`specs/`, `FROZEN_HASHES.json` and its sidecar is empty.

## Findings (self-review)

- **T14-01 QUESTION (owner / reviewer).** The outage-row rule above. It is the
  conservative reading of section 6, but it is a data-semantics choice.
- **T14-02 NON-BLOCKING.** `parser_code_sha256` hashes `klines.py` alone,
  LF-normalized. A change to `aqt.data.bars` that altered parsing would not
  change it. The manifest's `parsed_sha256` still changes if any bar changes,
  so no silent drift reaches the manifest identity.
- **T14-03 NON-BLOCKING.** Size exceeds the ~400-line target (see Scope).
- **T14-04 NON-BLOCKING (carried to Task 15).** The build report lists outage
  rows and gaps, but Task 15's data quality report is where they become
  human-readable evidence.

## Gate

LOCAL GATE: PASS. Independent review status: `NOT SENT`.
