# Astra review prompt: slice 6b build B3 (cycle ledger, look lock, read check) at e514ffc

You are an independent adversarial code reviewer (read-only). Repository root is the
current directory, branch `confirmation-module`, commit `e514ffc` (or the next commit, which
only adds these notes). Do not modify any file. Your findings are proposals; you are not an
authority. This is the Constitution §16 different-model review of
`calibration/c2_confirmation.py` changes; the builder was Claude Opus 5.5.

Scope: `git diff 054812b e514ffc` (B3a `725663f`, B3b `36df555`, B3c `e514ffc`). Read first:
`review/r14a-modules/BUILD_NOTES_SLICE6B_B3.md` (readings B3-R-1..9) and, in
`review/r14a-modules/DESIGN_SLICE6B.md` (rev 16), §2 (table rows for the ledger and `now`,
A-1), §3 (tests list), §4, §5.1, §6, §13. Use `src/aqt/core/ledger.py`,
`src/aqt/core/attempts.py` and `src/aqt/data/manifest.py` as needed. Do not reopen owner
decisions B-1..B-5, C-1..C-3, or the rest of the design.

Check:
1. `cycle_ledger`: anchor extension (count and head; empty ledger; count 0), every entry of
   the cycle after the anchor (outcomes through their starts), every start's protocol hash,
   look/closing/termination forms, one look, closing only after the look. Can a dishonest
   ledger hide a look or termination entry, or place a cycle entry before the anchor
   unseen?
2. `look_allowed`: looked/terminated from the ledger, clock floor (day 0, last entry,
   whole seconds), breached families not waited for, day 180.
3. `look_lock`: matches §4 (own copy of `_try_lock`, own sidecar, blocking wait, release in
   `finally`, order look lock then append lock possible); platform correctness.
4. `check_read` against §6: composite verified, hash, cycle, protocol; partition entries
   only from the composite; whole partitions; the module's own cut; no lockbox read path;
   whether served bars or manifests can pass that are not the declared data.
5. Readings B3-R-1..9: agree or propose a correction.
6. Test quality: would each test fail on a plausible regression? Name missing tests.

You may run: `.venv/Scripts/python.exe -m pytest tests/unit/test_c2_confirmation_look.py
tests/unit/test_c2_confirmation_read.py tests/unit/test_c2_confirmation_cycle.py -q -p
no:cacheprovider` (set `TMP`/`TEMP` to a writable directory if the sandbox needs it).

Output (Markdown, concise): verdict GO / GO WITH CONDITIONS / FIX; model ID you can observe
(say if not exposed); files and line ranges read; commands run with results; findings
B3-A-1.. with severity (blocker/major/minor/info), location, evidence, failure scenario,
proposed correction; one line per reading B3-R-1..9: AGREE / CORRECT (with the correction).
