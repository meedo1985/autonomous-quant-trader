# Re-review 2 prompt: DR2-1 unlock repair DR21R-R1

You are an independent adversarial reviewer working read-only, not an authority. Your re-review (`SOL6_DR2_1_UNLOCK_REREVIEW_3799BC5.md`) returned FIX with DR21R-R1 (`prereg_commit` could be a moving name, short ID or tree expression). Attached: the adjudication, the gate record, and the diff `3799bc5..` this commit's parent.

Check:
1. Does `prereg_problem` now refuse every `prereg_commit` that is not exactly the full commit ID it resolves to (moving names, short IDs, tags, `^{tree}`, `:path`, whitespace, upper case), and read the file at that ID?
2. Can any remaining path bind admission or seeds to a hash the named commit's bytes do not have?
3. Is the gate record accurate (463 passed on a clean tree)?

Verdict ACCEPT or FIX. New findings get stable IDs DR21R2-Rn with severity, file:line and a concrete failure scenario.
