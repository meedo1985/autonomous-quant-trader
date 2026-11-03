# D-20 option C: manual release, no automatic publisher (sketch)

**Author:** Claude Opus 5.5 (`claude-opus-5-5`), in the main Claude Code session, 2026-10-30. AI drafting, not an authority. It decides, accepts or activates nothing.

**Status: INACTIVE SKETCH, UNREVIEWED.** It is written so the owner can compare it with revision 9 of the D-20 proposal. It is not a binding text. If the owner picks it, it becomes a full proposal and needs the R19-2 two-family review. It also re-opens owner-decided D-12 rows (listed in section 4), which needs a new owner decision. No human statistician has reviewed it.

**Why it exists.** Revisions 3-8 each fixed the previous round's blockers and then got new ones in the same places: the clock (D20LR8-S-1), finishes racing answers (D20L-62, D20L-69), the availability log (D20L-70) and timing hints from the shared lock (R5). All of these come from one feature: a **service that answers questions about a sealed result on a schedule, while the result may still be changing**. Option C removes that service.

## 1. The design in one paragraph

Reading, computing and sealing stay exactly as in revision 8 (pre-read check, budget, cooldown, cap C, DEFAULT FAIL, commitments, worker deadline `D*`). Nothing answers questions about a read before it is released: there is no `state` call, no publisher job, no daily release time, no signing window and no availability log. At or after `R_0`, the owner runs one command, `lockbox_release <evaluation_id>`. It prints **PASS or FAIL only** and writes one release entry. On a PASS it also signs the attestation with `cooling_off_start` equal to the time of that entry. The 72-hour cooling-off then runs from the moment the owner has the result in hand.

## 2. Rules

1. **One result, fixed by the first release.** `lockbox_release` and `mark_finished` both take the store lock for their check-and-write.
   - `mark_finished` refuses if a release entry for the evaluation exists, or if its clock reading is at or after `D*`.
   - `lockbox_release` refuses before `R_0`. Otherwise it reads the finished record (or the DEFAULT FAIL), verifies the bundle, writes the release entry and prints the result.
   - A second release prints the same entry; it never recomputes.
   - So once a result has been shown, no finish can change it, **whatever the clock does**. This removes the clock invariant D20LR8-S-1 asks for. The clock is still trusted for one thing only: not releasing before `R_0`, and for `D*`.
2. **Only PASS/FAIL leaves the store.** The command runs under a separate OS account that the owner can invoke but not log in as (exact mechanism: S4 and §16 review). The owner has no read access to the sealed directory. The output and the release entry contain PASS/FAIL, the release time and, on PASS, the attestation; nothing else.
3. **Cooling-off.** The cooling-off is 72 hours from the release entry. The printed result and attestation are copied to the owner's own record, so nothing the store does afterwards can shorten his access. This replaces P-5's "hours of reader-path availability".
4. **Cap.** No read is admitted from C on (unchanged). A pick is promoted only if it is released, cooled off for 72 hours and decided by day 255. A read released too late for that expires `U_ops`, as in P-6. Because the owner controls the release time, the command warns when `now + 72 h` is past day 255.
5. **Every read gets released.** A read that is still unreleased at day 255 is released by the same command afterwards, and its result is recorded (PASS/FAIL only). This way withholding a release cannot hide a FAIL from the cycle record.

## 3. What it deletes, and what still remains

**Deleted:** the publisher, the daily `R_j` schedule and the missed-release rule (P-7), the 6-hour signing window, `state`, `guard_state`, `insert_release`, the availability log and its tests (P-5, T-7), the §7 timing exception's delay and cap-expiry clauses (D20L-72), Q6 and Q7 in their current form, the R5 lock channel during a read, and residual R1 (signing activity before a PASS release).

**Remaining risks, disclosed:**
- **Machine-level activity.** Anyone with a shell on the lockbox machine during the read week can see CPU and disk use, and so whether the worker is still running. This is smaller than R5, which offered a callable service; it is not zero. Mitigation: no owner or research login on that machine during a read. That is an S4 procedure, not something a test can show.
- **Crash durability of sealed creates and of the release entry.** The write-temp, fsync, link, fsync rule and the platform assumptions stay `UNVERIFIED_EXTERNAL_ASSUMPTION`. The crash table shrinks to the worker's creates and one release write.
- **Owner timing.** When the owner releases cannot change a result. It only moves his own cooling-off. Choosing to release one family after seeing another is the already-accepted R4.
- **Process risk.** A forgotten release only costs the owner's own slack before day 255. Rule 5 keeps it visible.

## 4. What it would change in decided D-12 rows (needs a new owner decision)

- **Q6(i) "Separate posting job":** replaced by the owner-run release command (rule 2). THREAT_MODEL l.9 changes differently from what D-12 planned.
- **P-5:** 72 hours from the release entry; the availability measurement is not needed.
- **P-7, P-8:** the schedule is deleted. The P-8 identity checks move into the release command.
- **T-3, T-4, T-7, T-8:** replaced by tests of rules 1-5 (refuse before `R_0`; finish refused after release; one release entry; PASS/FAIL-only output; the cap warning; crash before/after the release write).
- **Unchanged:** P-1 (PASS-only attestation), P-2, P-3 (every technical FAIL counts), Q2a/Q2b, Q3, Q4, Q5, P-6 (as reworded by rule 4).

## 5. Comparison for the owner

| | Revision 9 (fix rev 8) | Option C (manual release) |
|---|---|---|
| Still-open blockers | D20LR8-S-1 clock invariant, plus whatever Astra finds in rev 8 | none known; unreviewed |
| Timing hints during a read | shared-lock waits (R5), needs signed §7 exception | machine activity only, handled by procedure |
| Daily posting, missed releases | yes | none |
| Availability log to design and test | yes (D20L-70) | not needed |
| Who posts | separate job (as decided in D-12) | you, by one command |
| D-12 re-decision needed | no | yes: Q6(i), P-5, P-7, P-8 |
| Next step | rev 9 + two re-checks, likely more rounds | full proposal + two first reviews |

**My recommendation (AI drafting choice):** option C. A non-statistician owner can check its rules, and it removes the mechanism behind six rounds of findings instead of patching it again. Its cost is re-opening four D-12 rows and running the release yourself.
