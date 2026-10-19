# Adjudication: Sol re-review of the DR2-1 unlock repairs at 3799bc5

Record: `SOL6_DR2_1_UNLOCK_REREVIEW_3799BC5.md` (FIX). Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-19.

| ID | Verdict | Repair |
|---|---|---|
| DR21R-R1 (High) | Accepted, reproduced. `prereg_problem` read whatever `prereg_commit` named: `HEAD`, a short ID or a tree expression with the honest hash passed. A moving name could later resolve to other bytes than the ones the chunks were bound to. | `prereg_problem` resolves `<prereg_commit>^{commit}` with the same safe git and refuses unless the result equals the field exactly (a full 40-hex commit ID), then reads the file at that ID (`e38df13`). The DR21-R1 test now also refuses `HEAD`, a 12-character ID and `<id>^{tree}` with the honest hash; it fails on the previous `rundef.py` (checked: `AssertionError: HEAD`). |

Sol's other conclusions (both paths check before any chunk; `rundef.git` keeps the recorder's behaviour; the R2 test change; the gate record) need no action. No finding left unrepaired.
