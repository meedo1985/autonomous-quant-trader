# Adjudication: Astra review of slice 6b design rev 4 (R14D6B4-A-1..6)

- Record adjudicated: `ASTRA_DESIGN_SLICE6B_9F45303.md` (commit `1c49aa5`), verdict FIX.
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the design's author. Not an authority.
- Date: 2026-11-14.

## Evidence checked by the adjudicator

- `c2_confirmation.py` l.2451-2454: `ACCEPTANCE_FIELDS` has the inclusion `block_hash` and no
  acceptance-tip hash; O-6a SPEC §5 l.82-95: the capture body must equal the tip at `h+5` (A-1).
- `family_attempts` l.745-751 raises on a second outcome; l.764-767 leaves `end=None` without
  an outcome; `trial_states` l.797-803 treats a first attempt with `end=None` that started
  before the slot crash as making the slot undetermined (A-2, A-3).
- `attempts.finish_attempt` l.384-400 does not refuse an existing outcome (A-3).
- `ledger.append_entry` serialises single appends only (A-5).

## Decisions

| ID | Decision | Rev 5 |
|---|---|---|
| A-1 | Accept. | The acceptance record carries `headers`: the six 80-byte headers `h..h+5` instead of rev 4's single `block_header`. `start` checks `hash(headers[0]) == block_hash`, each header's previous-hash field equals the hash of the one before, and takes `tip_block_hash = hash(headers[5])`. The capture check compares with that. Chain provenance (main chain, valid work) stays the verifier obligation. Within B-1/B-2 direction; no new owner item. |
| A-2 | Accept. | The rewrite sets both `outcome="completed"` **and** `end` = the result entry's ledger position for a derived-completed attempt; crash attempts keep their real outcome position. Regression test: A writes its result and dies before any outcome, B crashes without artefact → A completed, B gets the slot, B's re-run allowed. |
| A-3 | Accept. | Rev 4's "`evaluate_trial` writes the `completed` outcome" is **withdrawn**: completion is derived from the result entry, so no module outcome is needed and the double-outcome race disappears. The runner writes outcomes only for attempts with no result entry. `family_attempts` reports duplicate outcomes as an order breach of that family (owner B-4: family U_ops `LEDGER_ORDER`), not a cycle `CycleError`; contract change named. |
| A-4 | Accept. | `days` leaves the identity list. Identity fields (including `window_id`) mismatched or malformed → `CycleError`; well-formed `days` not equal to the window's days → that family U_ops `MISALIGNED_SERIES` (as `nominate` does today). §3, §5 and tests agree. |
| A-5 | Accept. | `evaluate_look` holds an exclusive per-ledger look lock (OS file lock next to the ledger) from step 4 through the step-7 append; a second caller waits, then sees the look entry at step 4 and refuses without appending. Store obligation: all looks of a cycle use the same ledger path on one host. |
| A-6 | Accept. | Residual reworded: header time must exceed the median of the previous 11 blocks and may be at most 2 hours ahead of validating nodes' clocks; there is no guaranteed bound on how far it lags real time. Stated, not corrected. |

No finding is left unrepaired. No new owner item. B-3 (`LOOK_WITHOUT_RECORD`, decided
2026-11-14, `e0f0848`) is marked decided in rev 5.
