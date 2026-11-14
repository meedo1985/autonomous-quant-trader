# Owner decisions on the final Fable review of slice 6b design rev 6 (C-1..C-3)

- Date: 2026-11-14. Asked by Claude Opus 5.5 in Claude Code (multiple-choice question); the
  owner's selections are recorded below. Direction for design rev 7, not activation of any
  governance change; rows touching P18 or S4 wording follow the Constitution's process.
- Source: `FABLE_FINAL_DESIGN_SLICE6B_4B6E6E0.md` (R14D6B-FINAL-F-1..9).

| Item | Finding | Owner selection |
|---|---|---|
| C-1 | FINAL-F-1 headers vs pinned lockbox copy | "Separate input (Recommended)": the six headers are a separate caller handle checked against the acceptance record's `block_hash`; acceptance record and lockbox untouched. Also confirms six headers instead of the one-header B-2 selection. |
| C-2 | FINAL-F-2 breached family at the look | "Don't wait (Recommended)": the look does not wait for a family with an order breach; `evaluate_trial` refuses for it. |
| C-3 | FINAL-F-3 breach recoding U_proc | "Count as U_proc (Recommended)": a family with an order breach and a procedure-failure reason counts as U_proc; a yes/no `u_proc_present` field is also recorded. |
