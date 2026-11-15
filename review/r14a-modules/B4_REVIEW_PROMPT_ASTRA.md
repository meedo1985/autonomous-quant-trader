# Astra review prompt: slice 6b build B4 (signed rows, steps 2-3, evaluate_trial) at f53cba6

You are an independent adversarial code reviewer (read-only). Repository root is the
current directory, branch `confirmation-module`, commit `f53cba6` (or the next commit, which
only adds these notes). Do not modify any file. Your findings are proposals; you are not an
authority. This is the Constitution §16 different-model review of
`calibration/c2_confirmation.py` changes; the builder was Claude Opus 5.5.

Scope: `git diff 56790b6 f53cba6` (B4a `65b4279`, B4b `1d3b854` + `09a6e54`, B4c
`f53cba6`). Read first: `review/r14a-modules/BUILD_NOTES_SLICE6B_B4.md` (deviation B4-D-1,
readings B4-R-1..11) and, in `review/r14a-modules/DESIGN_SLICE6B.md` (rev 16), §1, §2
(order steps 1-4), §3 (attempt binding, runner rule, rule 4), §4 (look lock), §7. Use the
earlier B3 functions (`cycle_ledger`, `family_ledger`, `look_lock`, `check_read`) as
reviewed. Do not reopen owner decisions B-1..B-5, C-1..C-3, or the rest of the design.

Check:
1. `signed_c2`: every row once, exact forms, no default; can a malformed or ambiguous row
   pass (Unicode digits, signs, leading zeros, case, range)? Is the drand chain-hash
   layout right (B4-D-1)? You cannot fetch drand; reason from the three known answers in
   `tests/unit/test_c2_confirmation_signed.py`.
2. `prepare` and `install_code`: §2 order, every step read-free, the code checked before
   it is written and loaded with the engine first on the path; can missing, extra,
   shadowing or wrong code reach a read? Any input taken from the caller that the module
   should verify itself (R14D6B-S-1)?
3. `evaluate_trial`, `trial_may_run`, `run_trial` against §3 rule 4 and FINAL-F-4: every
   refusal before the read; the re-read, re-check and append under the look lock; binding
   (cycle, confirmation partition, family, trial); one entry on a double launch; no
   outcome written. Can a result land inside a look's steps 4-7, or after a termination?
4. Readings B4-R-1..11 and B4-D-1: agree or propose a correction.
5. Test quality: would each test fail on a plausible regression? Name missing tests.

You may run: `.venv/Scripts/python.exe -m pytest tests/unit/test_c2_confirmation_signed.py
tests/unit/test_c2_confirmation_prepare.py tests/unit/test_c2_confirmation_trial.py -q -p
no:cacheprovider` (set `TMP`/`TEMP` to a writable directory if the sandbox needs it).

Output (Markdown, concise): verdict GO / GO WITH CONDITIONS / FIX; model ID you can observe
(say if not exposed); files and line ranges read; commands run with results; findings
B4-A-1.. with severity (blocker/major/minor/info), location, evidence, failure scenario,
proposed correction; one line per reading B4-R-1..11 and B4-D-1: AGREE / CORRECT (with the
correction).
