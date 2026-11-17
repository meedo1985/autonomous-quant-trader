# Astra re-check prompt: slice 6b design rev 13 at 523b1dc

You are an independent adversarial reviewer (read-only). Repository root is the current
directory, branch `confirmation-module`, commit `523b1dc`. Do not modify any file. Your
findings are proposals; you are not an authority.

Narrow re-check. Read `git diff a116077 523b1dc -- review/r14a-modules/DESIGN_SLICE6B.md`,
the final Fable record `review/r14a-modules/FABLE_FINAL_DESIGN_SLICE6B_A116077.md`
(R14D6B12-F-1..4) and `ADJUDICATION_FINAL_DESIGN_SLICE6B_A116077.md`. Verify against code
only where needed (`calibration/c2_confirmation.py` `seal_family`, `sealing_record`,
`check_screen_record`, `check_declaration`, `family_attempts`; `calibration/c2_lockbox.py`
artifact checks, `_check_declared`, `Store` docstring; `src/aqt/core/ledger.py` lock). Do
not re-review the rest of the design or reopen owner decisions B-1..B-5 or C-1..C-3.

Check: (1) each R14D6B12-F-n APPLIED / PARTIAL / NOT APPLIED with evidence, and whether the
unapplied F-2 optional "read begun" entry is soundly justified; (2) defects the rev 13
changes introduce: artifacts passed to `persist` and the extended release rule (does every
artifact the lockbox needs get stored and bound; can one be released without a closed look;
does the lockbox's `aqt.c2.artifacts.v1` expectation match "written by the store build"?);
the declaration layout (consistent with lockbox `_check_declared`, which must also accept
it?); `screen_record` / `trial_objects` checks; attempt binding with partition and family;
the one-process-per-attempt runner rule; the blocking look lock (can a blocked waiter
deadlock or starve a look?). Report only blocking or major issues as findings; list minor
wording points briefly.

Output (Markdown, concise): verdict ACCEPT / ACCEPT WITH NOTES / FIX; model ID you can
observe (say if not exposed); files and line ranges read; status table; new findings
R14D6B13-A-1.. with severity, location, evidence, failure scenario, proposed correction.
