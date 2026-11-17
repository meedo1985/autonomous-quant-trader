# Adjudication of the Astra review of 6b build B1 (record `ASTRA_REVIEW_B1_637A7B0.md`)

- Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15.
- Astra verdict: FIX (B1-A-1 major, B1-A-2 minor, B1-A-3 minor); B1-D-1 ACCEPT; B1-D-2
  ACCEPT WITH CHANGES (the change is B1-A-2's exact `last_seen` form).

| ID | Decision | Repair |
|---|---|---|
| B1-A-1 major | Accepted | `check_capture_record`: a non-string `url` is refused as a `CycleError`. `parse_declaration`: `trial_id` (non-empty str), `family` (str), `hypothesis_hash` and `configuration_hash` (64 hex) are checked before any set or map use. `qualification_report`: the signed row is read first; a missing or malformed manifest or file, or a `qobj.read` refusal, becomes a `CycleError`. `classifier_bounds`: any malformed threshold set (missing side or `T`, non-numeric value, wrong shape, `for_k` error) becomes a `CycleError` |
| B1-A-2 minor | Accepted | new `_strict_time`: ASCII only and an exact `strftime` round trip, used for the CDX timestamp and `last_seen` (refuses unpadded fields, Unicode digits, lower-case `z`) |
| B1-A-3 minor | Accepted | tests: object map in reverse order; 11 + 10 trials across both families (refused) and 20 (passes); own-`trial_id` mismatch with a matching hash; gzip variants (recompressed, empty member appended, zero padding) fail against the archived digest; extra decoded content refused; non-canonical base64 pad bits refused; `classifier_bounds` with `K=1` equals `reduce.for_k` |

Not repaired: none. Astra's note that SPEC §5 obligations (exact `id_` fetch binding,
redirect exclusion, freeze timing, earliest capture, later invalidation) stay external is
agreed; it is already the §2.1 residual, and v2 does not claim them.

The deviations: B1-D-1 (capture schema v2) and B1-D-2 (`protocol_hash` in the declaration
key set) are accepted by this review. They remain **design changes to rev 16** that the
final review and the owner's §16 PR review see; they amend no governance text (the
declaration layout and capture schema are still [DESIGN] items for the S4/SPEC wording).

## Checks after repair

- `.venv/Scripts/python.exe -m pytest tests/unit/test_c2_confirmation_inputs.py -q`:
  72 passed. Against the pre-repair module (stashed): 15 failed, 57 passed, so the new
  A-1/A-2 tests fail on the old code.
- `pytest tests/unit/test_c2_confirmation_start.py -q`: 51 passed (pinned 6a section
  unchanged).
- `ruff check calibration tests/unit/test_c2_confirmation_inputs.py`: clean.
- `mypy calibration/c2_confirmation.py`: clean. `mypy` on the test file reports 10 errors,
  all in the imported `tests/unit/test_calibration_screen.py`, identical at `8d63b21`
  (pre-existing, not touched).
- `lint-imports`: 7 kept, 0 broken (unchanged imports: standard library only).

Astra's own test run failed on a read-only sandbox temp directory (27 setup errors), not on
the code; the suite above was run here.
