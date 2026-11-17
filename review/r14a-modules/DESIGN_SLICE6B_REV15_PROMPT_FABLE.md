# Final Fable review prompt: slice 6b design rev 15 at 159b915

You are Claude Fable, an independent adversarial reviewer for this repository (branch
`confirmation-module`, commit `159b915`). You are read-only except for ONE file you write:
`review/r14a-modules/FABLE_FINAL_DESIGN_SLICE6B_159B915.md`. Do not edit any other file, do
not commit, do not change frozen artifacts (`docs/`, `protocols/`, `schemas/`, `specs/`,
`FROZEN_HASHES.json`, SHA-256 sidecars). You are not an authority: your findings are
proposals; you approve nothing and close no owner item.

This is the final design review before building `evaluate_trial` / `evaluate_look` in
`calibration/c2_confirmation.py` (a Constitution §16 file). Since your last review (rev 12,
`FABLE_FINAL_DESIGN_SLICE6B_A116077.md`, R14D6B12-F-1..4) the design went through (all in
`review/r14a-modules/`):
- rev 13 `523b1dc`: your 4 findings (`ADJUDICATION_FINAL_DESIGN_SLICE6B_A116077.md`);
- Astra `ASTRA_RECHECK_DESIGN_SLICE6B_523B1DC.md` (FIX, R14D6B13-A-1: prediction artifact
  vs trial/code inventory) and `ADJUDICATION_RECHECK_DESIGN_SLICE6B_523B1DC.md` → rev 14
  `dc9d1c7`;
- Astra `ASTRA_RECHECK_DESIGN_SLICE6B_DC9D1C7.md` (ACCEPT WITH NOTES) and
  `ADJUDICATION_RECHECK_DESIGN_SLICE6B_DC9D1C7.md` → rev 15 `159b915` (wording only).

Read `review/r14a-modules/DESIGN_SLICE6B.md` in full and
`git diff a116077 159b915 -- review/r14a-modules/DESIGN_SLICE6B.md`. Verify claims against
the code it cites (`calibration/c2_confirmation.py`; `c2_lockbox.py` `ARTIFACT_KINDS`,
`_check_items`, `_check_trial`, `_check_declared`, `pre_read_check`, `Store`/`begin_read`;
`src/aqt/core/ledger.py`, `attempts.py`;
`review/governance-statistics-amendment/o6a-channel/SPEC.md` §4-§5;
`docs/RESEARCH_CONSTITUTION.md` §16; `protocols/protocol_v1.yaml`). Do not trust citations.
Do not reopen owner decisions B-1..B-5 or C-1..C-3; you may say if the design misstates them.

Check:
1. Each R14D6B12-F-n: APPLIED / PARTIAL / NOT APPLIED in rev 15, with evidence; whether the
   unapplied F-2 optional "read begun" entry is soundly justified as now qualified.
2. The rev 13-15 changes as a whole: predictions persisted before the closing entry; the
   prediction vs trial/code inventory split and the store's release rule; `sources`
   (`screen_record`, `trial_objects`) and the declaration `[DESIGN layout]` (accepted by
   lockbox `_check_declared` too); attempt binding with partition and family; the
   one-process-per-attempt runner rule; the blocking look lock; the required shared-store
   handoff tests.
3. Owner table: every P18/S4 wording item marked for the Constitution's formal process;
   nothing shown as decided that the owner did not decide.
4. Anything that would let a cycle look early or twice, read bars before the look entry,
   drop a family, hide a crash or procedure failure, release or pick without a closed look,
   leave the lockbox unable to run on a closed status (a) family, or let AI approve or
   amend governance.
5. Is the design buildable as written (every new function's inputs defined, every
   contract change named)?

Write the record with: title with verdict (ACCEPT / ACCEPT WITH NOTES / FIX); reviewer line
with your actual model ID as your session reports it; date; reviewed commit; files and line
ranges read; status table for R14D6B12-F-1..4; new findings with stable IDs
R14D6B15-F-1.., each with severity, location, evidence, failure scenario and proposed
correction. Plain English, concise. Reply with the verdict and one line per finding.
