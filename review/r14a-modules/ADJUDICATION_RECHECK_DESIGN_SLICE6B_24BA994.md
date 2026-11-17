# Adjudication: Astra re-check of slice 6b design rev 5 (R14D6B5-A-1..4)

- Record adjudicated: `ASTRA_RECHECK_DESIGN_SLICE6B_24BA994.md` (commit `659fda4`), verdict FIX.
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the design's author. Not an authority.
- Date: 2026-11-14.

## Evidence checked

- Bitcoin header layout: the previous-block field (bytes 4-35) holds SHA256d of the previous
  header in internal byte order; the displayed block hash is that digest reversed (A-1).
- `c2_confirmation.py` l.2876-2881: `completed_entry` requires `window_id` to equal the days'
  own window, so shifted days with the governing `window_id` raise (A-2).
- `trial_states` l.805-809 raises "attempt 2 is not permitted" when a trial with two
  attempts does not own the slot (A-3).
- `ledger.append_entry` takes its own sidecar lock (A-4).

## Decisions

| ID | Decision | Rev 6 |
|---|---|---|
| A-1 | Accept. | Link check on decoded bytes `headers[i][4:36] == SHA256d(headers[i-1])`; display form `SHA256d(h)[::-1].hex()` for `block_hash`, tip and capture body. |
| A-2 | Accept. | `completed_entry` contract change: `window_id` vs governing window; days form-only; days-own-window check removed; `d` integrity kept. |
| A-3 | Accept. | A breached family skips `trial_states`' admissibility checks; history kept and recorded; no cycle-level error from it; regression test for duplicate crash outcome after a legitimate re-run. |
| A-4 | Accept. | Distinct `<ledger>.look.lock` sidecar, released in `finally`, order look lock → append lock. |

No finding left unrepaired; no new owner item.
