# Owner decision: when the screen and mapping code must be built

**Decision by:** the owner, in the Claude Code session on 2026-10-12, answering one question.
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). This file records the owner's choice; the AI made no decision.

**Context.** Preregistration §4 lists "the screen and mapping code" (§3.6, §7.2) among the contents of the qualification object, which is hashed at the freeze (freeze order step 5, after the threshold run and development). Freeze order step 2 reads: "The owner gives the go-ahead for the build and a measured pilot. The build goes through §16 review." The engine, launcher and pilot passed §16 review and are merged (PRs #48 and #50). The screen's seven gates (G-3, G-5, G-6, G-7, G-8, G-11, G-14) are not implemented anywhere in the repository.

**Question as asked:**
> "The 'screen and mapping code' must be inside the sealed qualification object at the freeze, after the 2½-month run. When must it be built?"

**Options shown:**
- "By the freeze (Recommended)": Start the full run once your Bitcoin key record is done, using the engine that's already reviewed and merged. I build the qualification object, the mapping, the screen with its 7 gates, and the held-out runner during the run, each with review and your PR review. The run's results don't depend on that code, and the plan text already fixes how it must work. I'd get an independent review of this reading before we rely on it.
- "Before the full run": The strictest reading of 'build before the threshold run'. Nothing starts until everything is built and reviewed, including the 7 gates. The full run starts weeks later, but no one can question the order.

**Owner's choice, verbatim:** "By the freeze (Recommended)".

**Recorded meaning, conditional on review.** The threshold and development runs may start on the reviewed engine once their other preconditions hold: the key record, the accepted preregistration hash, and the committed run definition (S16-2). The qualification-object builder, the §3.6 mapping, the §7.2 screen with its gates, and the held-out runner are built and reviewed before the freeze. This reading is relied on only after the independent review requested with it is recorded.
