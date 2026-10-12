# Fable fix-check BF5 of the D-19 preregistration §13 rev 7f at `02c14e5`: READY WITH FIXES (one minor advisory)

Date: 2026-10-04. R19-2 independent statistical fix-check, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`). This is the BF5 fix-check, done read-only.
**Commit reviewed:** `02c14e5` (branch docs/d19-recommendation). Scope: `git diff 9d811e6 02c14e5 -- review/governance-statistics-amendment/d19-preregistration/`
**Verdict:** READY WITH FIXES (one minor advisory finding)

## 1. Are the earlier findings fixed?

| Finding | Status |
|---|---|
| BS4-1 (QJ cost) | RESOLVED. The cost is now 25·E[ord] + 50·E[QJ]. I recomputed it with Poisson rates at 12,000 development replications (λ = 0.24, 0.6, 1.2). Per test, P(1–2 events) is 0.211, 0.428 and 0.578. A QJ cell escapes with probability (1−P(≥3))² − P(0)², which is 0.377, 0.653 and 0.682. There are 102 ordinary cells and 2 QJ cells: QJ runs at `K` ∈ {2, 20}, at one `T`, as item 1 says. The added cost is about 577, 1,157 and 1,542, which matches the stated 570, 1,160 and 1,550. |
| BS4-1 (re-pilot) | RESOLVED. The re-pilot now measures an all-groups `U_G` rate, from at least one cell of each of Q1, Q2, Q2m, Q3, Q4, Q5 and QJ. These are the full group list in §2. The scenarios are labelled conditional, and the go-ahead uses the measured rate. |
| BF4-1 | RESOLVED. (4,500 + escapes) × 1.2 gives about 6,090, 6,790 and 7,250. That matches the stated 6,100, 6,800 and 7,300. At about 1,460 server-core-hours a month (2 vCPU), this is about 4.2, 4.7 and 5.0 months, which matches "about 4, 4½ or 5". The case with no escapes is 5,400, about 3.7 months, which matches "3½–4". |
| BF4-2 | RESOLVED. The re-pilot list now names `U_G` and DSR-availability rates in the thin categories, which matches item 3, plus the all-groups rate. |
| BF4-3 | RESOLVED in substance. "Platform" is now the OS and architecture inside the image, plus libc. The host kernel release is host provenance. I checked the engine branch: `runtime_identity()` records `platform.system()` and `platform.machine()` only, with no kernel release. A host kernel update therefore does not change the gating identity. See BF5-1 for a small leftover. |
| BS4-2 | RESOLVED. Rev 7e's history row cites the committed BF4 (`23ce5f4`) and BS4 (`026a23a`) records and their actual verdicts. Rev 7f's row says "awaiting fix-check". The title and the §13 heading say rev 7f. |

## 2. Findings

**BF5-1 (MINOR, advisory). §13 item 6, the "Platform" bullet, and `ADJUDICATION_9D811E6.md`, BF4-3 row.**
- **Problem:** The text puts "the image's libc" in the gating identity. The adjudication says "no code change is needed". But `runtime_identity()` (engine branch, `calibration/dsr.py`) does not record libc: its platform field is `system machine`, and `_interpreter_files` hashes only the Python executable and libpython. In effect libc is still gated, because the image digest pins it, and the image digest is in the gating identity. So this is not a safety gap. It is an inaccurate statement about where libc is recorded.
- **Fix:** Pick one.
  - Say in §13 that libc is covered by the image digest, and is not a separate field.
  - Or record libc in `runtime_identity` (for example `platform.libc_ver()`) when the engine is extended, and correct the adjudication's "no code change" wording.

No other new errors or inconsistencies were found. The diff agrees with item 1 (the QJ `K` values), item 3 (the per-test demotion values, 0.21, 0.43 and 0.58 without demotion), and A-V1 / V_BINDING §3 ("the platform").

**For the owner, in plain words:** All five earlier problems are fixed and the run-time numbers check out (about 4 to 5 months). One small wording point remains about where a system library's version is recorded, and it does not affect the results.
