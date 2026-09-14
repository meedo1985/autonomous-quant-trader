# Task 9 Sol High Review

Observed model: `gpt-5.6-sol`, reasoning effort `high`.

Initial verdict: **REVISE**.

The reviewer demonstrated five blockers against the initial implementation:

1. A caller could directly construct a partition manifest, change semantic
   fields, recompute the self-hash, and pass verification.
2. The builder admitted a genuine two-hour series although Cycle 1 is fixed to
   one-hour bars.
3. Direct sealed references and composite headers were insufficiently
   validated, and non-lockbox partitions could be sealed.
4. Raw SHA-256 and byte count were caller assertions rather than values computed
   from one byte snapshot.
5. Git `assume-unchanged`, `skip-worktree`, and ignored source files could hide
   working code from the clean-tree check.

The adversarial probes reproduced all five findings. Frozen verification and
the unaffected tests passed during the review. The findings were accepted and
fixed; their disposition is recorded in `SOL_FINDING_DISPOSITION.md`.
