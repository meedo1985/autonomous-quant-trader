# Slice 6b build, B4 (signed rows, steps 2-3, evaluate_trial): build notes for review

- Builder: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15, branch `confirmation-module`.
- Design: `DESIGN_SLICE6B.md` rev 16 §1, §2 (order steps 1-4), §3 rule 4 and attempt
  binding, §4 (look lock), §7. Earlier slices: B1, B2, B3 (`ADJUDICATION_B3_E514FFC.md`).
- §16 applies as for B1-B3: not merged; different-model review and the owner's PR review
  first. The start-chain section pinned to `c2_lockbox.py` is unchanged
  (`test_c2_confirmation_start.py` passes).

## What B4 changes

| Piece | Design | Commit |
|---|---|---|
| B4a: `C2_ROWS`, `Signed`, `drand_chain_hash`, `signed_c2(protocol)`: every §7 row once through `protocol_row`, exact forms (integers `0\|[1-9][0-9]*` in range, times by `_strict_time`, hashes lower-case hex of fixed length, `z_crit` a decimal string, `family_block_rule` in `choices.RULES`, `drand_scheme == SCHEME`); the drand rows must hash to `drand_chain_hash` | §7 | `65b4279` |
| B4b: `SOURCE_KEYS`, `install_code(trials, code_files)`, `Inputs`, `prepare(started, sources)`: `headers_check`, `signed_c2`, `parse_declaration`, `check_eligibility`, `check_declaration`, `check_screen_record` (signed `qualification_object_sha256`), code install and load, `check_capture_record`, `derive_seeds`, all read-free | §1, §2 steps 1-3 | `1d3b854`, `09a6e54` |
| B4c: `trial_may_run`, `run_trial`, `evaluate_trial(started, sources, trial_id, attempt_id, read)` | §1, §3 rule 4, FINAL-F-4 | `f53cba6` |

Tests: `test_c2_confirmation_signed.py` (three drand known answers, every row form),
`test_c2_confirmation_prepare.py` (wiring with recorders for the headers, capture and
seeds checks, which have their own tests; real code install and load),
`test_c2_confirmation_trial.py` (real ledgers and threads; `prepare` and the
read-and-compute step replaced by verified inputs and a recorder; `run_trial` wiring with
recorders). Mutation check on B4c: removing the re-check under the lock, the breach check,
the running check, the look/termination check, or the lock itself each fails 2-6 tests.

## Deviation from rev 16 that the review must accept or reject

- **B4-D-1 (drand rows).** Rev 16 §7 lists `drand_public_key`, `drand_genesis_time`,
  `drand_period`, `drand_chain_hash`, `drand_scheme`. drand's chain hash also covers the
  group hash and, for a non-default chain, the beacon id (R14D6B2-F-12, which asked for
  exactly this). Pinned layout: `SHA-256(uint32 BE period || int64 BE genesis_time ||
  public_key bytes || group_hash bytes || beacon_id ASCII unless "default")`. Checked
  offline against the three chain-info files of FP3 (`origin/freeze-sheet`
  `review/fp3/drand-info-2026-10-25/`: quicknet `52db9ba7…`, default `8990e7a9…`, evmnet
  `04f1e906…`); the scheme id is not hashed (all three match without it). B4 adds two signed
  rows, `drand_group_hash` (64 hex) and `drand_beacon_id`; this is an S4/OD-4 row-list
  change for the owner.

## Readings taken (for the reviewer to confirm or correct)

- **B4-R-1** `z_crit` form is `(0|[1-9][0-9]*)(\.[0-9]+)?` (how `choices` writes it);
  its string equality with the qualification object's `z_crit`, and `family_block_rule`'s
  equality with the object's, are B5 (the look uses them). `signed_c2` checks only
  `family_block_rule ∈ choices.RULES`.
- **B4-R-2** `drand_beacon_id` form `[a-z0-9_-]+`; `drand_period` in `[1, 2^32)`,
  `drand_genesis_time` in `[0, 2^63)` (the hash's integer widths).
- **B4-R-3** Every §7 row is parsed by both entry points, so a malformed look-only row
  (`z_crit`, `canonical_benchmark_sha256`) also refuses `evaluate_trial`.
- **B4-R-4** `check_declaration(..., eligible=True)`: `check_eligibility` has passed, so
  the window is eligible.
- **B4-R-5** `code_files` must hold exactly the declared digests (an extra file is
  refused); one module name with two different sources is refused; any exception from
  `screen.load` (syntax, `check_code`, not a function) is a read-free `CycleError`. The
  directory is `tempfile.mkdtemp`, left in place (one process per entry point).
- **B4-R-6** `sources` must be exactly `SOURCE_KEYS`. `evaluate_trial` does not use
  `object_dir` (the classifier is the look's, §2 step 6).
- **B4-R-7** `prepare` runs the capture check and `derive_seeds` for `evaluate_trial` too:
  the result entry's identity needs the line-266 and estimator seeds.
- **B4-R-8** `read()` returns `(composite, served)`; anything other than a 2-tuple is a
  `CycleError`. The cut is `[w0 − warmup_hours, w1)` with the trial's own
  `warmup_hours`.
- **B4-R-9** "Running" is `family_ledger`'s derived outcome `None` (no result entry and no
  outcome). The check looks at the look and termination entries; a closing entry implies
  a look (`cycle_ledger`).
- **B4-R-10** A refusal from `run_trial` (code mismatch in `trial_result`, C-T, manifest)
  propagates; nothing is appended. The runner may then write a crash outcome only through
  its own eligibility checks under the look lock (§3 runner rule: no look, closing or
  termination entry, and the attempt still has no result entry) (corrected per Astra
  B4-A-3). A broken ledger chain raises `read_entries`' `LedgerError`, not `CycleError`.
- **B4-R-11** The result entry's `recorded_at_utc` is `append_entry`'s clock; nothing
  reads it for the trial.

## Not in B4

`evaluate_look` (look entry append, intervening-entry check, classifier bounds, records,
`persist`, closing entry), the `z_crit`/`family_block_rule` equality with the
qualification object, the `Store` docstring (B5).
