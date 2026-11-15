# Slice 6b build, B5a (opening the look): build notes for review

- Builder: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15, branch `confirmation-module`.
- Design: `DESIGN_SLICE6B.md` rev 16 §2 (order steps 4-7), §4 (look entry, look lock,
  intervening entries), §7 (`z_crit`, `family_block_rule`), §8, §13 (`look_allowed`).
  Earlier slices B1-B4 (`ADJUDICATION_B4_F53CBA6.md`; owner accepted B4-D-1).
- §16 applies: not merged; different-model review and the owner's PR review first. The
  pinned start-chain section is unchanged.
- B5 is split: B5a opening the look (this note, `53a4550`); B5b read, nomination, gates;
  B5c sealing, records, `persist`, closing entry, `Store` docstring.

## What B5a adds

`_now()` (the one clock read), `Look`, `open_look(inputs, sources)`: after `prepare`, the
qualification report from `sources["object_dir"]` (`qualification_report`), whose `z_crit`
and `family_block_rule` must equal the signed rows as strings; then under the look lock:
`read_entries`, `cycle_ledger`, `family_ledger` for every declared family on the pre-look
ledger, one clock read truncated to whole seconds, `look_allowed`, `classifier_bounds` for
each family's `(T, K_f)`, and the look entry appended with `recorded_at_utc` = that clock.
After release the ledger is read again; the appended entry must be the cycle's one look; an
entry of this cycle between the step-4 length and the look entry stops the look
(`CycleError`; the look entry stays, no closing entry: the store's `LOOK_WITHOUT_RECORD`).

Tests: `tests/unit/test_c2_confirmation_open.py` (real ledgers, threads; `prepare`'s inputs
and the qualification report given directly). Mutation check: removing the intervening
check, the `z_crit` check, the truncation, the lock, or `look_allowed` each fails 1-2 tests.

## Readings taken

- **B5A-R-1** `K_f` for the classifier bounds is the number of declared trials of the
  family (§8 "(K_f, T)").
- **B5A-R-2** The qualification report is read before the lock (read-free, no ledger
  dependency); the bounds are computed under the lock after `look_allowed` and before the
  append, so a missing `T=<T>` refuses with nothing written.
- **B5A-R-3** "Intervening" is judged on the entries after the step-4 ledger length and
  before the look entry; an entry of this cycle after the look entry is not intervening
  (a late result is ignored by the look, §3 rule 3).
- **B5A-R-4** A family ledger whose `family_ledger` raises (identity breach, extra start in
  an unbreached family) refuses the whole look before the entry (§3 rule 2).
- **B5A-R-5** `look_entry`'s `families` is the declared families (sorted); it is written
  only here.
- **B5A-R-6** The step-4 `Look.ledger` is the pre-look ledger B5b evaluates; the re-read is
  used only for the intervening check.
