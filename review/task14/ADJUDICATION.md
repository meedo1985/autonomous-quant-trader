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
| R-1 | BLOCKER | **Accepted, reproduced.** | `parse_archive` classifies a row as an outage and `continue`s (`klines.py:169-171`) before converting or validating its prices. A synthetic archive with a row closing 1 s after its open, `open="nan"` and `volume="abc"`, plus one regular row, parsed without error: 1 bar and 1 outage row. The documented rule says malformed prices stop the build. Not yet repaired. |
