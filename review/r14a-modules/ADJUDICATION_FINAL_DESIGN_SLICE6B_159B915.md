# Adjudication: final Fable review of slice 6b design rev 15 (R14D6B15-F-1..4)

- Record adjudicated: `FABLE_FINAL_DESIGN_SLICE6B_159B915.md` (commit `8ed4480`), verdict FIX.
  Reviewer Claude Fable 5.2 (`claude-fable-5-2`), run as a subagent of the author's session
  on the owner's machine at the owner's request. R14D6B12-F-1/3/4 APPLIED; F-2 PARTIAL,
  omission of the optional entry judged sound as qualified.
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the design's author. Not an authority.
- Date: 2026-11-14.

## Evidence checked

- `screen.load` (`screen.py` l.579-590) resolves code with `importlib.util.find_spec` on the
  import path; every run in `c2_confirmation.py` calls it (l.459-462, 566, 1875-1879,
  2266-2285); `sources` named no code input (F-1, confirmed).
- `c2_lockbox.py` `_install_trial_code` l.1355; `screen._extend_path` l.1937 with S7R-R1
  (engine first, trial code last).
- `screen.trial_set_sha256` l.495 hashes the list in the order given (F-2.1).
- `ledger.py` `_try_lock` l.314/328 and a deadline loop l.350-355 (F-4.1).

## Decisions

| ID | Decision | Rev 16 |
|---|---|---|
| F-1 | Accept as proposed. | `sources.code_files{sha256: bytes}` installed like `_install_trial_code`, placed last on the path via `_extend_path`; every declared trial's code loaded before the look entry (and before `evaluate_trial`'s read); failure read-free `CycleError`; test; §12 store retains the same bytes. |
| F-2 | Accept. | Parse rules: `int` trial_index, ≤20 trials total and ids unique across families, unique `(hypothesis_hash, trial_index)`, trial object `trial_id`/`family` match; screen trial set in declaration order; builder checks the same before posting. |
| F-3 | Accept. | Owner table: declaration-layout row; P18-1 row names the one-launch runner promise; verifier-clearance duty split from B-1 as a design proposal to confirm. |
| F-4 | Accept. | Look lock = own copy of `_try_lock` in a loop with no deadline; trial objects kept as JSON (any serialization passes the lockbox). |

Nothing left unrepaired; no new owner decision (the verifier-clearance row is now shown as
a proposal to confirm rather than as decided).
