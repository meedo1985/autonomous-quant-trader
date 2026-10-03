# Owner decision: broadened-method B-1..B-7

**Date:** 2026-10-03
**Authority:** the owner, in a Claude Code session, after two different-model
reviews of the broadened method (Fable 5.1 and Codex `gpt-5.6-sol`, records in
this folder). Asked and recorded by Claude Opus 5.5 (`claude-opus-5-5`).

## Decided object

`DESIGN.md` revision 3, commit `a3d2c59`, §5 decisions B-1..B-7. Revision 3
applied the reviewers' dispositions without a further check (recorded as weaker).

## Exchange

1. The owner opened the session with "contenue and let the agent answer any
   question". Claude settled B-3, B-4 and B-6 as **AI defaults** (method-design
   choices, already labelled so in `DESIGN.md`) and declined to decide B-1, B-2,
   B-5 and B-7 for him (D-16/D-17 are D-rows; B-5 is an error budget; B-7 changes
   owner-decided D-18 text).
2. The owner was asked, verbatim: "Do you accept my recommendation on the four
   decisions that are yours? In plain terms: (B-1) stop using an 'effective
   number of trials' count. (B-2) Score each cycle only against the strategies
   declared for that cycle. Keep the lifetime count of everything ever tried,
   but only record and report it. This reverses your earlier choice. (B-5)
   Halve the allowed false-promotion risk in each new eligible cycle: 5%, then
   2.5%, then 1.25%, and so on. That keeps the lifetime total at 10% or less.
   (B-7) Add a 'minimum days of data' condition to the D-18 test, and move the
   data-type check into the D-19 calibration. I've settled B-3, B-4 and B-6
   myself as AI defaults." Options offered: "Yes to all (Recommended)", "Yes,
   but B-5 report-only", "Keep lifetime count (no B-2)", "Not now".
3. The owner chose: **"Yes to all (Recommended)"**.

## Effect

- **B-1 (D-16), decided by the owner:** no effective trial count. Requires a
  Constitution §9 line 106 amendment later.
- **B-2 (D-17), decided by the owner:** the score uses the declared
  current-cycle set; lifetime counts are recorded and reported only. This
  replaces his 2026-10-03 choice in
  `../d16-d17-proposal/OWNER_CHOICE_CANDIDATE_COUNT.md`.
- **B-5, decided by the owner:** alpha spending across eligible cycles by
  halving. Eligible cycle `m` (1-based) has a whole-cycle allowance of
  `0.05 / 2^(m-1)`, split equally between families as in D-18. The
  assumption-free lifetime bound is `sum 0.05/2^(m-1) < 0.10`. Consequence for
  D-19: `z_crit` must be calibrated per allowance level, not once (open drafting
  item for the D-19 preregistration).
- **B-7, decided by the owner:** `T >= T_min` is added to P18-0; the support
  classifier moves from the method (O18-2) to the D-19 preregistration.
- **B-3, B-4, B-6, AI defaults (not owner decisions):** `D` by uncentred
  bootstrap for every column; D-18's comparator kept (no bootstrap p-value);
  one global `z_crit` with D-18's per-nominee `D`.
- **Recorded weaknesses accepted:** no human statistician (R19-2); revision 3
  not re-checked.

## Not changed by this decision

Nothing is activated. This is not a Constitution §4 amendment, sets no
`z_crit` and edits no frozen file. `HUMAN_DECISION_MATRIX.md` is not edited by
this record. Promotion stays blocked until the owner-authored §4 amendment and
the D-19 calibration exist and are accepted. No cycle, trial, confirmation or
lockbox access, deployment or trading is authorized.
