# D-20 lockbox: your decisions (draft, plain language)

**Prepared by:** Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-30. AI drafting, not advice that binds anything.

**Status: DRAFT. Not to be answered yet.**
- Codex Sol re-checked option C revision C4: ACCEPT WITH NOTES (`SOL_OPTION_C4_REVIEW_5599056.md`).
- Codex Astra's re-check is still pending: its first attempt hit the usage limit (`ASTRA_OPTION_C4_REVIEW_ATTEMPT_1.md`).
- R19-2 needs both reviews before you decide. If Astra finds something, this sheet changes.
- No human statistician has reviewed any of it.

**What these answers do:** they record your choices. Nothing binds until you sign the C2 amendment, after a person reviews it. Every question has **"Keep blocked"**, which is always a valid answer.

**Sources:** option C is `OPTION_C_PROPOSAL_REV2.md` + `_REV3.md` + `_REV4.md` (on top of `PROPOSAL_REV8.md`'s reading side). Q2-Q5 are from `PROPOSAL_REV4.md` §3, as amended by `PROPOSAL_REV5.md` §3.

---

## Part A: how results reach you (new with option C)

### QC1. Switch the lockbox to "release on request"?

**What happens:**
- No result is released before seven days after its test started. If you ask earlier, you get "not yet".
- From then on you ask, and the separate posting job releases the result and copies it to your own records: PASS or FAIL, nothing else.
- If you don't ask, the service tries to release it by itself after another seven days, so release never depends on you. A broken service can hold it up; the cycle report then stays marked incomplete.
- On a PASS, your 72 hours of cooling-off start when your copy arrives, and the signed certificate carries that time.

**What it changes in your D-12 decisions:**
- **kept:** the separate posting job; PASS/FAIL only; every technical fail counts; the day-255 rule;
- **replaced:** the daily posting timetable, and counting the 72 hours by service uptime;
- **reworded:** the signer's checks.

**Why it is recommended:** it removed the mechanism behind six rounds of review findings in the timetable design. With it, a released result can never change, even if the clock jumps.

**Options:**
- **"Switch to release on request (Recommended)."** Cost: you run one command per test, and the D-12 rule changes above go into C2.
- **"Keep the daily timetable (revision 8)."** A revision 9 would be needed, and revision 8 still has an open blocker.
- **"Keep blocked."**

### QC2. Adopt the detail rules?

**What it means:** this adopts the AI-drafted rule book for running, sealing, releasing and certifying lockbox tests. With it, the builds can start, each needing your §16 review. Without it, the lockbox cannot run.

**Points that affect you directly:**
- **From day 255, no new test is admitted and none can count as finished.** One admitted shortly before day 255 may end as a technical fail.
- **You get one fixed command, and no login on the lockbox computer while a test runs.**
- **Your copies of results live on your own machine.** Keeping them backed up is up to you.
- **If the service stops for an incident, a person must sort it out.** Who that person is, and what they may see, is still to be decided (S4). If it has to be you, that is a separate Constitution question first.
- **A certificate counts only if it becomes valid before day 255 and before any revision.**

Adopting this does **not** settle D11-15.

**Options:**
- **"Adopt (Recommended)."** Cost: several builds, each needing §16 review. A lost signing key can cost a good PASS, because its certificate can never be signed.
- **"Keep blocked."**

### QC3. May the service's speed and delays give hints?

**What it means:** the hidden test and the parts that answer you share one computer.
- How long any answer takes, even "not yet", can depend on hidden work, for this test or another. Someone timing it closely might guess that a test is still running or has just finished.
- Nobody has shown that it cannot hint at pass versus fail.
- A busy or broken computer can delay a result, its copy to you or its certificate by any length of time. Near day 255, that can make a PASS expire unpromoted.
- Before a result is released, a busy or broken computer can make a test miss its deadline. It then counts as a technical fail, although it might have passed.
- You see only six fixed answers: "not yet"; "FAIL"; "PASS, certificate pending"; "PASS, certified"; "PASS, not certifiable"; or "stopped", which never says why.
- You and research also see the bookkeeping:
  - which tests ran, and when each may be released;
  - the reason a test was refused before it started;
  - when results were released and copied to you;
  - whether a certificate could not be issued, and why (day 255 or a revision).

Once a result is released, these delays cannot change it. The Constitution says research receives PASS/FAIL only, so allowing these hints needs a **written exception**, which you would sign in C2 after a person reviews it. Its words are in C4 item 4.

**Options:**
- **"Accept the exception (Recommended)."** Cost: the hints above, allowed in writing.
- **"Keep blocked."** Stronger separation would be needed, for example separate machines. No draft proposes it.

### Q7. When does a save count as made in time?

**What it means:** saving to disk takes a moment nobody can bound, so a rule must say at which instant a save "happened". Three saves have deadlines:
- starting a test (before day 255);
- finishing a test (before the worker deadline);
- a certificate becoming valid (before day 255 and before any revision).

Your answer also fixes how your D-12 rules "finished before the deadline" and "attested by day 255" are read; C2 would write that meaning in.

**Draft rule:** a save counts at the moment the service checks its clock, while it holds its lock, if that is before the deadline. The service shows "done" only after the save is safely on disk. If a crash loses the save, it never happened: no test, a technical fail, or a certificate attempt retried (and refused after day 255).
- *Cost:* a save may reach the disk just after the deadline and still count. For example, a certificate checked a moment before day 255 counts even if it is saved a moment after.

**Stricter rule (possible; not drafted):** a save counts only if the service confirmed, after the disk finished, that the deadline had not passed.
- *Cost:* some saves made in time are thrown away: a technical fail, or a certificate refused. It needs additional durable evidence and design work.

No rule can both keep every on-time save and refuse every late one, because after a crash the records can look the same either way.

**Options:**
- **"Accept the draft rule (Recommended)."**
- **"Ask for the stricter rule."** A new draft would be needed.
- **"Keep blocked."**

---

## Part B: how the lockbox test itself runs (unchanged from earlier drafts)

**Time-sensitive:** Q2(ii) and Q5 must be settled **before the freeze (step G)**. Otherwise their recommended options are lost.

### Q2. How do the runs that feed and make up the lockbox test start and end?

**(i) Start:**
- **"Strategy and benchmark start with no position; each pays its entry cost at its first permitted entry (Recommended)."** This matches the lockbox start you decided in D-11. Cost: the entry costs fall inside the measured period.
- **"Carry positions over from the warm-up."** Cost: the forecast and the lockbox start differently, and D-11's stated reason no longer holds.

**(ii) End:**
- **"Use the last hour's own closing price (Recommended)."** No run ever needs data from after its period. Cost: the confirmation-run part must be in the reviewed `screen.py`, or another file the R-14 rule allows in the frozen object, **before the freeze**, in the same change as Q5. If the freeze comes first, C2 stays blocked until a formal amendment.
- **"Read one more price, just after the period."** Cost: it changes your D-11 data permission, and the confirmation runs still cannot use it.

**Or:** **"Keep blocked."**

### Q3. Which seed drives the lockbox forecast's random draws?

- **"The post-protected seed, as for G-1 (Recommended)."** Cosmetic edits made before the public post cannot pick it. Cost: one more C2 row.
- **"The old protocol seed."** No wording change. Cost: the seed is known before the post, so cosmetic edits can be tried offline, and this must be disclosed.
- **"Keep blocked."**

### Q4. Where does the lockbox code live?

The frozen rules say evaluation code must be inside the frozen engine. The lockbox checker comes later, so either it gets a narrow written exception, or part of it goes into the engine before the freeze. Both routes need the exception for the lockbox service.
- **"One separate reviewed lockbox module, its fingerprint in the signed C2, with a narrow R-14 exception (Recommended)."** Cost: one amendment row, and the build and review must be done before you sign C2.
- **"The forecast code inside `screen.py` before the freeze."** Cost: the freeze waits for it, and the exception is still needed.
- **"Keep blocked."**

### Q5. Which number seeds the chosen strategy's own model fit?

- **"The protocol's seed, turned into an ordinary number in a fixed way (Recommended)."** It follows your R-13 decision. Cost: a small reviewed `screen.py` change, and the freeze must be built from the commit that contains it.
- **"Seed 0 everywhere."** No estimator-seed change; the Q2(ii) adapter is still required. Cost: a C2 row overrides part of R-13. The results are unaffected only if the fits truly ignore the seed, which the screen assumes but has not proven.
- **"Keep blocked."**

---

## After you answer

- Your answers are recorded word for word as `OWNER_DECISION_D20_LOCKBOX.md`, with the reviews they relied on.
- They bind only through your signed C2 amendment, after the required human review.
- Then the consolidated S4 text and the builds follow, each build under §16 review.
