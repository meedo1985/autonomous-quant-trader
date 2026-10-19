# Re-review prompt: DR2-1 unlock repairs (DR21-R1, DR21-R2)

You are an independent adversarial reviewer working read-only, not an authority. Your first review (`SOL6_DR2_1_UNLOCK_REVIEW_C536943.md`) returned FIX with DR21-R1 (the run trusted the definition's asserted preregistration hash) and DR21-R2 (the test asserted the pin is `None`). Attached: the adjudication, the gate record, and the diff `c66f8c3..e142a69`.

Check:
1. Does `rundef.prereg_problem` close DR21-R1 on every path that computes a chunk (job set-up and each worker), before any chunk, with the same replacement-free and `GIT_*`-free git the recorder uses? Can a definition still bind admission or seeds to a hash that the named commit's bytes do not have (moving names, a short ID, a missing commit, a path in a different tree)?
2. Is moving `_git` into `rundef.git` behaviour-preserving for the recorder?
3. Does the DR21-R2 test change keep the unset, other-hash and pinned cases, and allow a later one-line pin?
4. Is the gate record accurate, including the explanation of the 9 held-out failures on the uncommitted tree?

Verdict ACCEPT or FIX. New findings get stable IDs DR21R-Rn with severity, file:line and a concrete failure scenario.
