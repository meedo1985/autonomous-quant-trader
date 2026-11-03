# Codex Sol re-check of D-20 lockbox revision 8 (e68b947)

Prompt: `REREVIEW7_PROMPT.md`. Reviewer metadata from the Codex CLI header (2026-10-27): model `gpt-6-sol`, provider openai, sandbox read-only, reasoning effort high, Codex CLI v0.164.0, session id `01a17c92-75aa-7c12-95e5-93dd4e6f98f8`, 77,829 tokens. The report calls its IDs provisional; the CLI header confirms `gpt-6-sol`, so the IDs D20LR8-S-n stand.

Verdict: **FIX** (1 BLOCKER, 1 NON-BLOCKING, 1 QUESTION). Findings D20LR8-S-1..3. Dispositions: D20LR7-S-1 FIX (-> S-1); D20LR7-S-2 ACCEPT WITH NOTES; D20LR7-S-3 ACCEPT; D20LR7-S-4 ACCEPT; D20LR7-S-5 ACCEPT WITH NOTES (-> S-2). E7-1, E7-3 applied and E7-2 note confirmed.

No finding is left unrepaired yet; dispositions go in the next revision.

## Report (verbatim)

## Verdict: **FIX** (`REVISION_REQUIRED`)

Revision 8 removes the rev 7 first-ask race under its intended clock behavior. I found one remaining gap in the stated proof: its clock assumption is too weak to guarantee that an answer already observed cannot change. This is an inactive proposal; the review grants no authority to activate it.

I cannot see a Codex CLI model header in this interface. The `D20LR8-S-n` IDs below are **provisional Sol IDs**; the caller must verify the model metadata before recording this as a Sol review.

| Authority | Status |
|---|---|
| Frozen [Constitution](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/docs/RESEARCH_CONSTITUTION.md:72>) and [protocol](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/protocols/protocol_v1.yaml:73>) | Controlling |
| [D-12 owner decision](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d12-proposal/OWNER_DECISION_D12.md>) | Recorded; requires signed C2 binding |
| [D-20 revision 8](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV8.md>) | Inactive proposal |

### Rev 7 finding dispositions

| Own finding | Disposition | Evidence |
|---|---|---|
| **D20LR7-S-1** | **FIX** | The fixed-result entry is gone and `mark_finished` now takes `L_store`, but the proof at rev 8 line 95 needs a stronger clock invariant; see S-1. |
| **D20LR7-S-2** | **ACCEPT WITH NOTES** | Lookup precedes sealed-directory fsync, including at read-gate startup. T-S4 selects a concurrently linked startup record and RESULT bundle, crashes, and requires rev 7’s ordering to fail. This proves the modeled ordering, subject to the stated external filesystem assumption. |
| **D20LR7-S-3** | **ACCEPT** | The partial `t2` outage entry and its make-up claim are deleted. P-5 measurement and T-7 are mandatory S4/build work; the listed schedule covers crossed releases, downtime, record-write crashes and overlap. Q1 says promotion waits for that design and test. |
| **D20LR7-S-4** | **ACCEPT** | The proposed §7 row covers delayed or missed releases and resulting cap expiry, while limiting *research-visible* disclosure. Rev 8 adds neither disputed index record type. |
| **D20LR7-S-5** | **ACCEPT WITH NOTES** | §0 and Q7 now distinguish imperfect classification from a possible conservative rule. Q7 makes one unsupported implementation claim; see S-2. |

### Findings

**D20LR8-S-1 — BLOCKER; [§1.2 result proof, line 95](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV8.md:95>).** The proof says it needs only that the store clock never steps back by **21,600 seconds or more**. Take `D*=0`: `state` observes FAIL at clock `21,600`; after it releases `L_store`, two backward steps of `10,800` and `10,801` seconds occur. Neither step reaches the prohibited size, but a later finish reads `t_f=-1`, records PASS, and changes the observed outcome. **Minimal repair:** specify and validate a cross-call, restart-safe clock invariant: after any eligible answer, every later store-clock reading must remain at or above that evaluation’s `D*` (or give an equivalent enforceable rule). State the proof condition in those terms, including cumulative adjustments. The proof’s “F first” sentence should also cover a crash before F’s directory fsync: A may make a surviving link durable before using it, rather than F always having made it durable before A began.

**D20LR8-S-2 — NON-BLOCKING; [Q7, line 220](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV8.md:220>).** Q7 says the undrafted stricter policy “needs one more record per save.” The ambiguity example establishes a need for additional trustworthy completion evidence or conservative rejection; it does not establish that exact record count. An owner could take the claimed cost as a settled design. **Minimal repair:** say “needs additional durable evidence and design work,” without specifying its record shape or count.

**D20LR8-S-3 — QUESTION; [D20L-75, line 189](</D:/PMP-programs-for-sharawi/aqt-freeze-sheet/review/governance-statistics-amendment/d20-lockbox-proposal/PROPOSAL_REV8.md:189>).** A human reconciling a §26 stop could see a sealed result or a release row before `visible_from`. If that human is the owner, D-12’s working rule makes it research-visible. **Minimal repair:** make S4’s access decision an explicit gate: identify a reconciler and a view that cannot expose those facts to the owner before release. If the owner must receive them, put that disclosure to the owner as a Constitution amendment question before adopting the access design. Leaving the person unnamed is acceptable at proposal stage only with that gate.

### Other requested checks

The lock serialization works **conditional on the repaired clock premise**: an answering call and finish cannot overlap; a counted finished record is durable before an ordinary unlock; after a crash, startup or the next consumer fsyncs a surviving name before using it. Exact arithmetic gives the first-answer slack `max(21,600, t_s + 583,200 − C)` seconds, with minimum **21,600**. The rev 7 lock-free-finish alternative avoids the renewed lock channel but requires the owner to accept a result that can depend on first-ask timing. Rev 8’s simpler result rule is reasonable if its clock and R5 costs are accepted.

R5 and Q6 plainly disclose the renewed lock wait, a stalled finish delaying a release, possible whole-day slips and cap expiry; neither claims a latency bound. The 13 crash rows include survival, loss and partial index persistence around fsync, while limiting the mock to its model and retaining `UNVERIFIED_EXTERNAL_ASSUMPTION`. T-S1 accepts the lower release boundary `R_j−21,600` and refuses `R_j`. Q1 removes “briefly” and describes the day-255 scope. Q2(i), Q2(ii), and Q3–Q5 show no new conflict in this delta. E7-1 and E7-3 are applied; E7-2 is correctly left as a note about the committed citation.

**Gate status:** read-only review; no files written. `rtk git status --untracked-files=all` was clean, and working and staged diffs were empty. The arithmetic check above was run independently; implementation tests and filesystem durability tests were not run. Under the repository rule requiring a committed review record with verified model metadata, this response alone is **not a completed R19-2 review record**.