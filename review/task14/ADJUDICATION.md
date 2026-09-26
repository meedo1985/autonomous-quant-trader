# Task 14 review adjudication

Review: `review/task14/REVIEW.md`, saved unedited from the reviewer's reply.
Reviewer: GPT-6 Astra (`gpt-6-astra`, reasoning effort high), Codex CLI 0.154.0,
session `01a0dd7a-23f6-7523-9960-6d8ced7a986e`, read-only sandbox, no tools,
2026-09-26. Input: the full `main...HEAD` diff (including `LOCAL_REPORT.md`),
implementer-run check output and real-data build output at `18a1ff9`, and the
unchanged `build_partition_manifest` and `Bar`/`BarSeries` source. The reviewer
did not rerun the checks. Verdict: **FIX**.
Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the implementing model.

## T14-01 (outage-row rule)

The reviewer would **retain** strict exclusion, subject to R-1. Agreed.

The reviewer also notes that an outage row is a *retrospective* data-quality
classification: a 12:00 bar that turns out to end at 12:29 does not prove that
a fill at 12:00 was impossible, so a decision-at-close / fill-at-open consumer
must not use that later knowledge to cancel an otherwise executable fill or to
jump to the next retained bar. It reported this as no defect, because this
diff introduces no execution consumer. **Accepted as a carried requirement**
(T14-05) for whichever later task first consumes these gaps for execution: that
task must state how it treats a declared gap without using information from
after the decision time.

## Findings

| ID | Severity | Adjudication | Evidence |
|---|---|---|---|
| R-1 | BLOCKER | **Accepted, reproduced.** | `parse_archive` classifies a row as an outage and `continue`s (`klines.py:169-171`) before converting or validating its prices. A synthetic archive with a row closing 1 s after its open, `open="nan"` and `volume="abc"`, plus one regular row, parsed without error: 1 bar and 1 outage row. The documented rule says malformed prices stop the build. Repaired below. |

## R-1 repair (Claude Opus 5.5, 2026-09-26)

`parse_archive` now runs every row's prices and volume through the
`aqt.data.bars.Bar` checks **before** classifying it. For an outage row the
`Bar` is labelled with the row's hour only so those checks can run, and is then
discarded; the raw open and close times go to the report unchanged. A malformed
row with an irregular time now stops the build like any other malformed row.

Tests: `test_malformed_values_fail_even_on_an_outage_row` (12 cases: a short
bar and an off-hour bar, each with `nan` open, non-numeric volume, negative
volume, high below low, zero low, infinite close) and
`test_malformed_outage_row_stops_the_build` (the builder raises, so no manifest
is produced). With the parser from `5dfca9f` restored, all 13 fail; with the
repair, all pass.

### Effect on the real exploration manifests

The repair changes `klines.py`, so its code hash changes and the manifests in
`LOCAL_REPORT.md` are superseded. The earlier outputs were moved, not deleted,
to the git-ignored `data/processed/manifests-superseded-parser-91f63d51/`, and
the manifests were rebuilt:

| Symbol | Bars | Gaps | Gap hours | Manifest SHA-256 |
|---|---|---|---|---|
| BTCUSDT | 38,166 | 31 | 186 | `5f92ec5041c9560d5f31bdb99b9686d7522697e65a8e61d514a0b0dda6d0b65b` |
| ETHUSDT | 38,166 | 31 | 186 | `a587081e2171c98921568a6867b437a36f8699d25e6cbead976f933ae3b701d4` |

Parser code SHA-256: `23814f6e604a2f834e707db676a9556665f113ef70af35b5291663b4229bc55e`.

Compared field by field with the superseded manifests, only
`parser_code_sha256` and `manifest_sha256` changed. `parsed_sha256`, the gaps,
and every count are identical, so none of the 56 real outage rows per symbol
carried malformed values.

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1246 passed, 4
skipped; `ruff check .` pass; `ruff format --check .` 69 files formatted;
`mypy src scripts/download_market_data.py scripts/build_manifests.py` no
issues in 34 files; `lint-imports` 5 kept, 0 broken; `git diff --check` clean;
no change under the frozen paths.

This repair has not been re-reviewed by a different model.
