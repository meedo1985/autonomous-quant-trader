# Owner decision: canonical qualification cell ids (FA-1, governance part)

**Decision by:** the owner, in the Claude Code session on 2026-10-11, answering one question.
**Recorded by:** Claude Opus 5.5 (`claude-opus-5-5`). This file records the owner's choice; the AI made no decision.

**Question as asked:**
> "FA-1: each calibration cell's name (id) feeds its random seeds. How should qualification cell ids be fixed, so nobody can pick names that give lucky draws?"

**Options shown:**
- "Derived from the cell (Recommended)": the id is computed from the cell's settings (law, dependence, K, T), for example 'gaussian.equi0.9.k5.t1200'. No free choice exists, and any other name is refused. It is simple, and anyone can check it.
- "Freeze a manifest file first": ids stay free text, but the full cell list is committed and frozen before any threshold draw. This needs a commit-order check and leaves a choice on record.

**Owner's choice, verbatim:** "Derived from the cell (Recommended)".

**Effect:**
- A qualification manifest must use, for every cell, the id computed from that cell's settings.
- The manifest must hold exactly the qualifying grid of §3.2 with the §13 rev 7g overrides.
- This closes the governance part of FA-1 (`FABLE_ADVERSARIAL_REVIEW_8936859.md`). Its code part was closed in `ADJUDICATION_FABLE_8936859.md`.
- The other governance point in FA-1 is still open: the qualification path must check the accepted preregistration hash. That hash is pinned only after the owner's key record completes the preregistration.
