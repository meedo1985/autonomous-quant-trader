# Slice 6b build, B3 (cycle ledger, look lock, read check): build notes for review

- Builder: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15, branch `confirmation-module`.
- Design: `DESIGN_SLICE6B.md` rev 16 §2 (A-1), §4, §5.1, §6, §13. Earlier slices: B1
  (`ADJUDICATION_B1_637A7B0.md`), B2 (`ADJUDICATION_B2_70C379B.md`).
- §16 applies as for B1 and B2: not merged; different-model review and the owner's PR
  review first. The start-chain section pinned to `c2_lockbox.py` is unchanged
  (`test_c2_confirmation_start.py` passes).

## What B3 changes

| Piece | Design | Commit |
|---|---|---|
| B3a: `LOOK_ENTRY`, `CLOSING_ENTRY`, `TERMINATION_ENTRY` and their exact keys; `CycleLedger` (`entries`, `look`, `closing`, `terminations`, `pre_look`, `head_hash`); `of_cycle`; `cycle_ledger(entries, decl, protocol_hash)` (anchor extension, every entry of the cycle after the anchor, every start's `protocol_hash`, look/closing/termination forms, one look, one closing only after the look); `look_entry`, `closing_entry` payload builders; `look_allowed(families, ledger, cycle_start, now)` (looked and terminated from the ledger, clock floor, breached families not waited for) | §2 A-1, §3, §4, §5.1, §13 | `725663f` |
| B3b: `look_lock(ledger_path)`: own copy of the ledger's non-blocking lock, sidecar `<ledger>.look.lock`, blocking wait with no deadline, released in `finally` | §4 | `36df555` |
| B3c: `check_read(composite, served, *, decl, protocol_hash, start, end)`: `verify_composite_manifest`, hash = declaration's `data_manifest_sha256`, cycle and protocol, each served whole partition checked by `verify_partition_manifest(entry, series=)` with the entry from the composite, the module's own cut `[start, end)`, then `check_confirmation_read` | §6 | `e514ffc` |

Tests: `tests/unit/test_c2_confirmation_look.py` (new, real ledgers and threads),
`tests/unit/test_c2_confirmation_read.py` (new, real manifests over the screen fixture's
bars); `test_c2_confirmation_cycle.py` updated to the new `look_allowed` shape.

## Readings taken (for the reviewer to confirm or correct)

- **B3-R-1** "A start with another `protocol_hash` refuses" (§3 tests) applies to every
  start naming this cycle, whatever its partition or family.
- **B3-R-2** The look entry's `families` is the sorted list of declared family names.
- **B3-R-3** Termination `kind` is not enumerated in rev 16; any termination entry of the
  cycle with the exact keys and non-empty string values blocks both entry points.
- **B3-R-4** `cycle_ledger` checks the form of look, closing and termination entries only;
  result entries are decoded and bound by `family_ledger` (B2). An entry of the cycle at a
  position before `anchor.entry_count` is refused whatever its type (start, outcome of a
  start of the cycle, result, look, closing, termination).
- **B3-R-5** If every declared family is order-breached, `look_allowed` returns true at
  once (nothing to wait for, owner C-2).
- **B3-R-6** The clock floor compares `now` with the last ledger entry of the whole ledger
  (any cycle), parsed from its `recorded_at_utc`; equal is allowed. `now` must be
  timezone-aware UTC with no microseconds (the caller truncates; the same value is the look
  entry's `now`).
- **B3-R-7** `check_read` accepts served keys only in {exploration, confirmation} x
  {BTCUSDT, ETHUSDT} that name a full manifest in the composite; partitions are joined in
  window-start order and an overlap is refused by `BarSeries`. A missing exploration
  partition is caught as a short cut (C-T). `start` and `end` (`w0 - W`, `w1`) are the
  caller's, from the governing window and the trial's warm-up (B4).
- **B3-R-8** The look-lock tests use two threads in one process: both `msvcrt.locking`
  and `flock` lock per open handle, so two handles in one process conflict as two
  processes do.
- **B3-R-9** Not in B3, left for B4/B5 using `of_cycle` and `CycleLedger`: the look
  entry append and the intervening-entry check (§4), `evaluate_trial` rule 4 refusals,
  the closing entry append.

## Not in B3

`evaluate_trial` (B4); `evaluate_look`, the records, `persist`, the Store docstring,
`code_files` install (B5).
