# Adjudication: Astra re-check of slice 6b design rev 7 (R14D6B7-A-1..3)

- Record adjudicated: `ASTRA_RECHECK_DESIGN_SLICE6B_E2DDCB4.md` (commit `7c29af4`), verdict FIX.
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the design's author. Not an authority.
- Date: 2026-11-14.

## Evidence checked

- Rev 7 §1/§4/§10/§12: the closing entry was appended before the records reached any
  durable store; `ledger.append_entry` fsyncs the entry (A-1).
- Rev 7 §5 rule 1 applied the U_proc override to every family; owner C-3 selected it only
  for a family with an order breach. Rev 6 §5 (at `4b6e6e0`) put unfinished trials and
  `MISALIGNED_SERIES` first (A-3).
- `failing` held one value per trial (last attempt) and `nominate` reads completed trials
  only (`c2_confirmation.py` l.864-882), so a U_proc result on a duplicated or superseded
  attempt could be lost (A-2).
- `verify_code` l.2592-2594 hashes the manifest as canonical JSON (`sha(json.loads(...))`),
  files by raw bytes (minor point).
- `check_eligibility` docstring: `T` is the whole days in `[w0, c2_end + 1 s)`, so the
  capture time fixes `w0` and hence `T`; it is not `T` itself (minor point).

## Decisions

| ID | Decision | Rev 8 |
|---|---|---|
| A-1 | Accept, route 1. | `evaluate_look` takes `persist`; the closing entry is appended only after `persist` returns for both exact byte strings; Store docstring durability obligation; crash between persist and closing = `LOOK_WITHOUT_RECORD` (no pick); verifier rule for a closing entry with no matching stored record. |
| A-2 | Accept as proposed. | `u_proc_present` = OR over every identity-valid pre-look result of the family, before collapsing; `u_proc_results` kept; three named tests. |
| A-3 | Accept as proposed. | C-3 override for order-breached families only; unbreached families keep rev 6 precedence; owner-table row narrowed. |
| Minor | Accept. | Manifest canonical vs raw-file hashing; `headers_sha256` = SHA-256 of the 480 concatenated bytes; capture `body` ASCII; capture time fixes `w0`/`T` (not `T`); `unstarted` state for a breached family's trial with no attempt. |

No finding left unrepaired; no new owner item. A-3 narrows the rev 7 text back to what the
owner selected in C-3; it does not reopen C-3.
