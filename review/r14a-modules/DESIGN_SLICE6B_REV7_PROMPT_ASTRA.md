# Astra re-check prompt: slice 6b design rev 7 at e2ddcb4

You are an independent adversarial reviewer (read-only). Repository root is the current
directory, branch `confirmation-module`, commit `e2ddcb4`. Do not modify any file. Your
findings are proposals; you are not an authority.

Narrow re-check. Read `git diff 4b6e6e0 e2ddcb4 -- review/r14a-modules/DESIGN_SLICE6B.md`,
the final Fable record `review/r14a-modules/FABLE_FINAL_DESIGN_SLICE6B_4B6E6E0.md`
(R14D6B-FINAL-F-1..9), `ADJUDICATION_FINAL_DESIGN_SLICE6B_4B6E6E0.md` and
`OWNER_DECISIONS_DESIGN_SLICE6B_REV6.md` (C-1..C-3). Verify against code only where needed
(`calibration/c2_confirmation.py` `ACCEPTANCE_FIELDS`, `verify_code`, `trial_states`,
`family_attempts`, `completed_entry`; `tests/unit/test_c2_confirmation_start.py:20-50`;
`src/aqt/core/ledger.py`, `attempts.py`). Do not re-review the rest of the design or reopen
owner decisions B-1..B-5 or C-1..C-3.

Check: (1) each R14D6B-FINAL-F-n APPLIED / PARTIAL / NOT APPLIED with evidence; (2) defects
the rev 7 changes introduce: `headers_check` and `qualification_report` (does the pinned
start-chain section really stay byte-identical?); breached-family states and the look not
waiting (can a breach drop a family, hide a crash or procedure failure, or let a cycle look
early?); `evaluate_trial` under the look lock (lock order, deadlock); closing entry and
`LOOK_WITHOUT_RECORD`; crash rewrite and attempt binding; §5 precedence with `failing` /
`u_proc_present`; clock floor; capture record schema. Report only blocking or major issues
as findings; list minor wording points briefly.

Output (Markdown, concise): verdict ACCEPT / ACCEPT WITH NOTES / FIX; model ID you can
observe (say if not exposed); files and line ranges read; status table; new findings
R14D6B7-A-1.. with severity, location, evidence, failure scenario, proposed correction.
