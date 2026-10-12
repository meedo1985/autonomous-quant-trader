# Owner decision: D-18 (selection rule and primary error event)

**Date:** 2026-10-03
**Authority:** the owner, in a Claude Code session, after two different-model
reviews per R19-2 (`../d19-recommendation/OWNER_STEP0_DECISION.md`). Asked and
recorded by Claude Opus 5.5 (`claude-opus-5-5`).

## Decided object

`PROPOSAL.md` revision 7, commit `9718fdc`: top-Sharpe nomination per family,
no fallback and no replacement; `E_f = A_f ∩ {z_f* >= z_crit}`,
`E = E_trend ∪ E_vol`, `P_0(E_f) <= 0.025` per family; the procedure
no-result event `U_proc` with a 1% whole-cycle target, `U_ops` reported
separately; only eligible (never-tested) confirmation windows may lead to a
promotion (P18-0..P18-7).

Reviews: revisions 1–4 full rounds and revisions 5–6 focused checks by Claude
Fable 5.1 and Codex `gpt-5.6-sol` (records in this folder); revision 6: Sol
READY, Fable NOT READY on one phrase (FR6-1); revision 7 applied both
reviewers' proposed dispositions **without a further check** (recorded as
weaker).

## Exchange

1. The owner was asked: "D-18: do you accept the rule 'check only each
   family's best-Sharpe strategy, no second try, noise held to 5% per cycle,
   only never-tested data can promote' as the definition? (Nothing activates;
   promotion stays blocked.)" and "The five AI defaults listed above: confirm
   them?" The five listed were: (1) cycle 2 uses the 2022–2025 data, never
   tested but lived through, so its guarantee is weaker, and later cycles
   declare before their new data exists; (2) at most 80 strategies per family,
   one slot kept for an automatic re-run, ruling out three full 27-strategy
   grids; (3) both families must be tested when never-tested data is used,
   reversing his earlier "one family is OK" for those cycles; (4) revision 7
   finished without a third review; (5) re-runs happen automatically, never by
   choice.
2. He answered both with "Let the agent do the answers" / "Let agents do the
   answers".
3. Claude declined to decide on his behalf (a D-row decision is the owner's;
   R19-2) and stated: "The agent's recommendation: accept the D-18 definition
   and confirm all five defaults. If you reply 'yes', I'll record D-18 as your
   decision with the recommendation attached".
4. The owner replied: **"Yes"**.

## Effect

- **D-18 is decided by the owner as a definition**, per revision 7 at
  `9718fdc`, with the AI recommendation (accept, confirm all five defaults)
  attached as the basis he accepted.
- The round-6 and round-7 AI defaults listed above are **confirmed by the
  owner**.
- **Recorded weaknesses accepted:** no human statistician (R19-2); revision 7
  not re-checked; C2's per-cycle bound assumes selection independent of public
  2022–2025 prices, which cannot be verified; the bound is conditional
  evidence over simulated classes, not a verified real-market guarantee.

## Not changed by this decision

Nothing is activated. This is not a Constitution §4 amendment, accepts no
DSR method, sets no `z_crit`, and edits no frozen file. Promotion stays
blocked (2026-09-15 decision stands) until the broadened method (O18-2), the
owner-authored §4 amendment for C2, and the D-19 calibration all exist and
are accepted. D-05, D-06, D-11, D-14..D-17, D-19 remain open; the D-16/D-17
count is to be revisited during the broadened-method design (round 5 Q4).
`HUMAN_DECISION_MATRIX.md` is not edited by this record. No cycle, trial,
confirmation or lockbox access, deployment or trading is authorized.
