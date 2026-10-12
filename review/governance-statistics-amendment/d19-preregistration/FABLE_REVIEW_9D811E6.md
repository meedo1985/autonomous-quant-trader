# Fable fix-check BF4 of the D-19 preregistration §13 rev 7e at `9d811e6`: READY WITH FIXES

Date: 2026-10-04. R19-2 independent statistical fix-check, run as a Claude Code subagent with the `fable` model. The drafter is Claude Opus 5.5. The subagent's final report is reproduced below unchanged.

---

**Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`). This is the BF4 fix-check, done read-only.
**Commit reviewed:** `9d811e6` (branch docs/d19-recommendation). Scope: `git diff 9762781 9d811e6 -- review/governance-statistics-amendment/d19-preregistration/` (PREREGISTRATION.md §13 and its history; ADJUDICATION_9762781.md).
**Verdict:** READY WITH FIXES (minor only)

## 1. Are the earlier findings fixed?

| Finding | Status |
|---|---|
| BF3-1 | RESOLVED. The canary expected values and the reference-vector outputs are recorded on the server before the threshold run. They are part of the run definition and its hash. They are carried unchanged into the qualification object, which satisfies A-V1's "recorded at the D-19 freeze". Any later change voids every bound chunk. Start and resume now check against the run-definition values. |
| BF3-2, BS3-1 | RESOLVED. The gating identity is the decided A-V1 identity (V_BINDING §3: interpreter, NumPy and OpenBLAS binaries, platform, dispatch features, environment), plus the image digest and the canary and vector results. The CPU model and microcode are now host provenance, recorded and never compared. The chunk-acceptance rule and the host-change rule now agree. The adjudication is correct that the CPU model was never in the decided A-V1 identity, so no owner-decided change to the runtime contract is needed. |
| BS3-2 | RESOLVED. The table is now labelled per `U_G` test. The QJ range of 1–2 times the per-test value (0.023–0.046 at p = 5·10⁻⁵) matches Sol's bounds. The DSR-availability route is disclosed as separate and not included. |
| BF3-3, BS3-3 | MOSTLY RESOLVED. The estimate is now parametric: about 25 hours per ordinary escape and 50 per QJ escape. The escape counts are correct: P(1 or 2 events) is 0.21, 0.43 and 0.58, which gives about 22, 45 and 60 cells, and about 550, 1,100 and 1,500 hours. The month conversion is correct: 5,400/2 h ≈ 3.7 months and 7,200/2 h ≈ 4.9 months. The remaining gaps are BF4-1 and BF4-2. |

## 2. Findings

**BF4-1 (MINOR). §13 item 6, "Estimate", Conversion bullet.** The lower end of "5,400–7,200 server-core-hours, about 3½–5 months" assumes no escapes at all. The lowest scenario the text gives (p = 2·10⁻⁵) works out to (4,200 + 300 + 550) × 1.2 ≈ 6,060 server-core-hours, about 4.1 months. The other two scenarios check out: about 6,720 and 7,200.
- **Fix:** Either say "about 6,000–7,200 (5,400 if there are no escapes), about 4–5 months", or list the three scenario totals.

**BF4-2 (MINOR). §13 item 6, the re-pilot list under "Before the full run," against item 3 and the Estimate.** The list still measures only "the `U_G` rates in the thin categories (item 3)".
- Item 3 now also says the re-pilot measures DSR-availability rates there (BS3-2). The two places disagree.
- The Estimate says "the re-pilot's measured rates replace these assumptions". But the escape count depends on the all-cells `U_G` rate, which BF3-3 asked for. Rates from only the thin categories (2–3 cells each) cannot supply it.
- **Fix:** Make the list say "`U_G` and DSR-availability rates in the thin categories, and an all-cells `U_G` rate for the escape estimate". Also state that the go-ahead estimate uses that all-cells rate.

**BF4-3 (MINOR, advisory). §13 item 6, gating identity "platform", against "The host may install security updates".** In a container, a Python `platform`-style string usually includes the host kernel release. A host kernel update would then change the gating identity and stop the run. Worse, it could make C2's later evaluation unreproducible, and under A-V1 that makes it void. `runtime_identity()` is not implemented yet: the only platform-related code found was `python_version()` and `python_implementation()` in `src/aqt/core/code_identity.py`. So this is a definition gap, not a defect in existing code.
- **Fix:** Define "platform" in the gating identity as the OS/architecture triple and libc inside the image, without the host kernel release. Record the kernel release as host provenance.

No other new errors were found. The two-hash ordering, the binding of chunks to the run definition before the freeze and to the qualification-object hash for held-out data, and the access definition are all consistent. They agree with A-V1, V_BINDING §3 and P18-6. The history row and the adjudication match the text.

**For the owner, in plain words:** The earlier problems are fixed, and the plan's statistics and safety rules now fit together. Three small wording fixes remain: the low end of the run-time estimate is a bit optimistic (about 4–5 months is more realistic), the trial-run list needs to match the rest of the text, and "platform" should be defined so that a routine server update cannot void the results.
