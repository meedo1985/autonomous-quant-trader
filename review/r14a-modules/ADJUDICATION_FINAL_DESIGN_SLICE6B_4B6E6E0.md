# Adjudication: final Fable review of slice 6b design rev 6 (R14D6B-FINAL-F-1..9)

- Record adjudicated: `FABLE_FINAL_DESIGN_SLICE6B_4B6E6E0.md` (commit `97ff99d`), verdict FIX.
  Reviewer Claude Fable 5.2 (`claude-fable-5-2`), run as a subagent of the author's session
  on the owner's machine after the owner's own run was found never to have started.
- Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the design's author. Not an authority.
- Date: 2026-11-14.

## Evidence checked

- `tests/unit/test_c2_confirmation_start.py:20-50`: the start-chain section, including
  `ACCEPTANCE_FIELDS` and `verify_code`, must equal `c2_lockbox.py` text-for-text (F-1).
- `verify_code` l.2592-2611 discards the qualification report; its manifest check can be
  repeated by a 6b function against `Started.screen_object_sha256` (F-1 route b).
- `trial_states` l.794-795 recognises a crash only by `outcome in NOT_COMPLETED` and
  `reason_code == CRASH` (F-6 item 2); `family_attempts` l.745-751 scans outcomes ledger-wide
  (F-6 item 3); `finish_attempt` l.384-400 accepts a second outcome (F-3).

## Decisions

| ID | Decision | Rev 7 |
|---|---|---|
| F-1 | Accept. Owner C-1: route (b). | Headers are a caller handle; `headers_check` and `qualification_report` are new 6b functions; pinned section untouched; §13 says so. |
| F-2 | Accept. Owner C-2. | Explicit states for a breached family; the look does not wait for it; `evaluate_trial` refuses for it. |
| F-3 | Accept. Owner C-3. | §5 precedence: a non-U_ops failing reason gives U_proc even with a breach; `failing` and `u_proc_present` fields. Marked as P18-7 wording. |
| F-4 | Accept as proposed. | `evaluate_trial` re-checks and appends under the look lock. |
| F-5 | Accept as proposed. | The module returns both records; a closing entry binds their hashes; `LOOK_WITHOUT_RECORD` = look entry without closing entry (reading to confirm, marked). |
| F-6 | Accept as proposed. | Attempt binding rule; crash rewrite sets `outcome`/`reason_code`/`end`; outcomes matched to this cycle's starts; start `protocol_hash` checked; malformed look/closing/termination payloads refused. |
| F-7 | Accept as proposed. | `aqt.c2.capture_record.v1` [DESIGN schema]; body bound to the CDX digest offline; `[VERIFY]` digest form. |
| F-8 | Accept. | Owner table names every item needing P18/S4 wording (B-1, B-2/C-1, B-3, B-4/C-2, C-3, the crash-whatever-outcome rule). |
| F-9 | Accept as proposed. | Non-nominee `d` residual stated; clock floor added. |

No finding left unrepaired. Items to confirm by the owner are marked in rev 7's table
(the "no closing entry" reading of B-3, the crash-whatever-outcome rule); neither blocks
building.
