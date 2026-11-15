# Adjudication of the Astra review of 6b build B4 (record `ASTRA_REVIEW_B4_F53CBA6.md`)

- Adjudicated and repaired by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-15.
- Astra verdict: FIX (B4-A-1 major, B4-A-2 and B4-A-3 minor); readings B4-R-1..9, 11
  AGREE, B4-R-10 CORRECT; B4-D-1 AGREE technically (the two added rows still need the
  owner's binding).

| ID | Decision | Repair |
|---|---|---|
| B4-A-1 major | Accepted | `signed_c2` refuses a protocol in which any §7 row name occurs, as a whole token, on more than one line (a tab, quoted-key, unquoted, commented or value-side spelling beside the canonical row). The pinned `protocol_row` is unchanged. A row name inside a longer identifier (`old_t_min_note`) is not a match. Fails closed: a comment naming a row in the signed C2 text is refused (S4 drafting note) |
| B4-A-2 minor | Accepted | integer rows longer than 19 characters are refused before `int()`, so Python's conversion limit is never reached; the error is a `CycleError` |
| B4-A-3 minor | Accepted | B4-R-10 reworded: the runner writes a crash outcome only through its locked eligibility checks (no look, closing or termination entry; no result entry of the attempt) |
| B4-R-10 | Correction accepted | as B4-A-3 |
| B4-D-1 | Agreed technically | stays an owner item (S4/OD-4 row list: `drand_group_hash`, `drand_beacon_id`) |
| Termination race (Astra note) | No change | a termination appended between the final re-check and the append is the accepted conservative case (`FABLE_FINAL_DESIGN_SLICE6B_A116077.md` l.79): the termination blocks release |

Missing tests Astra named, added: both A-1 counterexamples and three more spellings; the
oversized integer (4301 and 20 digits); a spy proving every row is requested exactly once;
engine-module shadowing (`numpy:s` resolves to the installed package and is refused); a
non-null overlay installed and required; refused code bytes never written; a failed header
check stops before the signed rows, the code install, the capture and the seeds; the real
`prepare` in front of `evaluate_trial` refusing wrong code with a read sentinel that raises
and the ledger never opened; the look-lock test now waits on an event set by the read
instead of a fixed sleep.

Not added: a full `prepare → evaluate_trial` run through the real BLS beacon, headers and
capture to a result entry. Those three checks have known-answer tests of their own
(`test_c2_confirmation_bls.py`, `test_c2_confirmation_inputs.py`); a joint fixture needs a
real beacon round matching a real capture for real headers. It is planned for B5's
end-to-end look test, where the same inputs are required anyway.

Not repaired: none.

Astra's sandbox could not run the ledger and temp-directory tests (no writable temporary
directory); they were run here.

## Checks after repair

- New tests against the pre-repair module: 6 failed (B4-A-1 x5, B4-A-2 x1), 62 passed.
- `pytest tests/unit -k c2_confirmation`: 542 passed.
- `ruff check calibration tests/unit/`: clean; `ruff format --check` on the module and the
  confirmation test files: clean.
- `mypy` on the module and the three B4 test files: clean apart from the 10 pre-existing
  errors in the imported `test_calibration_screen.py`.
- `lint-imports`: 7 kept, 0 broken.

## Owner decision (2026-11-15)

The owner, in chat on 2026-11-15, accepted B4-D-1: "yes accept B4-D-1". The signed C2 row
list gains `drand_group_hash` and `drand_beacon_id` (OD-4/S4 wording to follow). Recorded by
Claude Opus 5.5; this is the owner's decision, not an AI approval.
