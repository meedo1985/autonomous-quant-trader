# Astra review prompt: slice 6b build B2 (ledger rules) at 70c379b

You are an independent adversarial code reviewer (read-only). Repository root is the
current directory, branch `confirmation-module`, commit `70c379b` (or the next commit, which
only adds these notes). Do not modify any file. Your findings are proposals; you are not an
authority. This is the Constitution §16 different-model review of
`calibration/c2_confirmation.py` changes; the builder was Claude Opus 5.5.

Scope: `git diff 10eac2d 70c379b` (B2a `1782fc3`, B2b `aec0987`, B2c `70c379b`). Read first:
`review/r14a-modules/BUILD_NOTES_SLICE6B_B2.md` (readings B2-R-1..7) and, in
`review/r14a-modules/DESIGN_SLICE6B.md` (rev 16), §3 (result entry, attempt binding,
completion, runner rule, entry rules 1-4), §5 (precedence, `u_proc_present`) and §13. Use
`src/aqt/core/attempts.py` and `src/aqt/core/ledger.py` as needed. Do not reopen owner
decisions B-1..B-5, C-1..C-3, or the rest of the design.

Check:
1. Each §3 and §5 rule against the code: binding (this cycle, confirmation partition, the
   entry's family, before the entry, trial mapping), every identity field compared,
   completion (exactly one result, after the start, before any outcome; any outcome may
   follow), crash rewrite (no result before the first outcome, whatever the outcome says;
   `end` = first outcome position), order breaches (second result, second outcome, result
   after outcome) for that family only, FINAL-F-2 states, outcomes matched to this cycle's
   starts only, outcome with no start a `CycleError`.
2. Whether an honest sequence (the §3 test list) can produce a `CycleError` or a wrong
   state, and whether a dishonest ledger can make a family look completed or move the
   P18-1 re-run slot.
3. `nominate` §5: precedence order, `u_proc_present` computed before any collapsing over
   every identity-valid pre-look result (duplicates, superseded and post-outcome ones
   included), `failing` from the last attempt, the record fields; the required keywords.
4. `trial_result` v2 and `completed_entry`: identity fields, `window_id` against the
   governing window, days form-only, the R14S6R-F-5 self-check still meaningful.
5. Readings B2-R-1..7: agree or propose a correction.
6. Test quality: would each test fail on a plausible regression? Name missing tests.

You may run: `.venv/Scripts/python.exe -m pytest tests/unit/test_c2_confirmation_ledger.py
tests/unit/test_c2_confirmation_run.py tests/unit/test_c2_confirmation_cycle.py -q -p
no:cacheprovider` (set `TMP`/`TEMP` to a writable directory if the sandbox needs it).

Output (Markdown, concise): verdict GO / GO WITH CONDITIONS / FIX; model ID you can observe
(say if not exposed); files and line ranges read; commands run with results; findings
B2-A-1.. with severity (blocker/major/minor/info), location, evidence, failure scenario,
proposed correction; one line per reading B2-R-1..7: AGREE / CORRECT (with the correction).
