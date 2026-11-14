# Adjudication: Astra re-check of slice 6b design rev 13 (R14D6B13-A-1)

- Record adjudicated: `ASTRA_RECHECK_DESIGN_SLICE6B_523B1DC.md` (commit `5299e65`), verdict FIX.
  R14D6B12-F-3/F-4 APPLIED; F-1 PARTIAL (A-1); F-2 minimum applied, omission of the
  optional entry judged sound within the trusted runner contract.
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the design's author. Not an authority.
- Date: 2026-11-14.

## Evidence checked

- `c2_lockbox.py` l.489 `ARTIFACT_KINDS = ("trial", "signal", "overlay")`; `_check_items`
  l.565-619 checks those items by hash and size and returns the trial object; prediction
  bytes are the separate `artifact_bytes` input of `pre_read_check` (l.759-792). Rev 13 said
  the inventory is built "from the stored artifacts" (predictions): wrong (A-1, confirmed).
- Astra: determinism alone does not justify omitting the F-2 entry; a hidden relaunch still
  makes extra reads and bypasses crash accounting (N-3, accepted; the F-2 reason in
  `ADJUDICATION_FINAL_DESIGN_SLICE6B_A116077.md` is qualified here: the omission rests on
  the runner obligation and the disclosed limit, not on determinism).

## Decisions

| ID | Decision | Rev 14 |
|---|---|---|
| A-1 | Accept as proposed. | §12 separates the prediction artifact from the preregistered trial/code inventory; the store retains trial objects and signal/overlay bytes, builds the inventory from them, serves both only after closure; prediction-hash match scoped to predictions; shared-store handoff test through `_check_items`, `_check_trial` and prediction checks. |
| N-1 | Accept. | §4 closing entry follows durable records **and** predictions. |
| N-2 | Accept. | "look-lock acquisition timeout"; append lock keeps its timeout. |
| N-3 | Accept. | F-2 residual names extra reads and bypassed crash/re-run accounting. |

Nothing left unrepaired; no new owner item.
