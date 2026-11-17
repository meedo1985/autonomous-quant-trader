# Slice 6b build, B1 (read-free input checks): build notes for review

- Builder: Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15, branch `confirmation-module`.
- Design: `DESIGN_SLICE6B.md` rev 16 (`8d63b21`). Build plan (5 slices): B1 input checks;
  B2 ledger rules (attempt binding, completion/crash rewrite, order breach, result entry v2,
  `nominate` precedence); B3 look lock, look/closing/termination entries, read and manifest
  check; B4 `evaluate_trial`; B5 `evaluate_look`, records, `persist`, Store docstring.
- §16: `calibration/c2_confirmation.py` merges only with an independent different-model
  review record and the owner's PR review. B1 is not merged.

## What B1 adds (appended after the pinned 6a section; that section is unchanged)

| Function | Design | Commit |
|---|---|---|
| `headers_check` | §2 day 0 / tip row | `71b00e1` |
| `check_capture_record` | §2.1, **schema v2** (deviation B1-D-1) | `c19f458` |
| `qualification_report`, `classifier_bounds` | §2 classifier row, §8 | `5edb355` |
| `parse_declaration` | §1 layout and parse rules (deviation B1-D-2) | this commit |

Tests: `tests/unit/test_c2_confirmation_inputs.py` (known answers: Bitcoin mainnet headers
0..5; a real Internet Archive capture of `blockstream.info/api/block-height/0`).

## Deviations from rev 16 that the B1 review must accept or reject

- **B1-D-1 (capture digest).** Rev 16 §2.1 item 3 ("`body` hashes to `digest`") fails on a
  real capture: the CDX digest is the SHA-1 of the stored payload, which the origin served
  gzip-compressed. Evidence and the proposed schema v2 (adds `payload`, the exact `id_`
  bytes, and `content_encoding`) are in `VERIFY_CAPTURE_DIGEST_2026-11-15.md`. Built as v2.
  The record now carries the archive's bytes, so the store must keep them (S4/SPEC wording,
  next to B-1).
- **B1-D-2 (declaration keys).** Rev 16 §1 lists the top-level keys and refuses unknown or
  missing ones, but omits `protocol_hash`, which every declaration carries (`verify_chain`
  reads it). Applied literally, every real declaration would be refused. Built with
  `protocol_hash` in the key set. Also added, as forms the later steps need: the three
  hashes and the anchor head as 64 lower-case hex, `embargo_days` and `entry_count` as
  non-negative ints (no bool), `last_seen` as `YYYY-MM-DDTHH:MM:SSZ`, a non-empty
  `cycle_id`, at least one trial, and the trial-object map must be exactly the declared ids.

## Not in B1

No ledger, lock, read or record code; the B1 functions are not yet called by any entry
point (B4, B5). `check_declaration`, `check_screen_record` and `check_eligibility` (slice 3)
are unchanged and will be called with `parse_declaration`'s output in B5.
