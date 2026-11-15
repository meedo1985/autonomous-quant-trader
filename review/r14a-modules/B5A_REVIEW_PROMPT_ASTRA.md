# Astra review prompt: slice 6b build B5a (opening the look) at 53a4550

You are an independent adversarial code reviewer (read-only). Repository root is the
current directory, branch `confirmation-module`. Do not modify any file. Your findings are
proposals; you are not an authority. This is the Constitution §16 different-model review of
`calibration/c2_confirmation.py` changes; the builder was Claude Opus 5.5.

Scope: `git diff 3ca103a 53a4550` (`open_look`, `Look`, `_now`, and
`tests/unit/test_c2_confirmation_open.py`). Later commits on the branch may exist (B5b
work in progress); review only this range. Read first:
`review/r14a-modules/BUILD_NOTES_SLICE6B_B5A.md` (readings B5A-R-1..6) and, in
`review/r14a-modules/DESIGN_SLICE6B.md` (rev 16), §2 (order steps 4-7, the `now` row), §4,
§7, §8, §13. Earlier functions (`prepare`, `cycle_ledger`, `family_ledger`,
`look_allowed`, `look_lock`, `classifier_bounds`, `qualification_report`) are reviewed. Do
not reopen owner decisions or the rest of the design.

Check:
1. Order: nothing written before every refusal of steps 4-6; the look entry appended under
   the look lock with the step-5 clock; one look per cycle under concurrency.
2. The intervening-entry rule (§4): can an entry of this cycle land between step 4's read
   and the look entry unseen, or can a harmless entry wrongly stop the look?
3. `z_crit` and `family_block_rule` against the qualification object (§7).
4. Readings B5A-R-1..6: agree or propose a correction.
5. Test quality: would each test fail on a plausible regression? Name missing tests.

You may run: `.venv/Scripts/python.exe -m pytest tests/unit/test_c2_confirmation_open.py
-q -p no:cacheprovider` (set `TMP`/`TEMP` to a writable directory if the sandbox needs it).

Output (Markdown, concise): verdict GO / GO WITH CONDITIONS / FIX; model ID you can observe;
files and line ranges read; commands run with results; findings B5A-A-1.. with severity,
location, evidence, failure scenario, proposed correction; one line per reading.
