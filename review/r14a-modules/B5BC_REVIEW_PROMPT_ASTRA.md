# Astra review prompt: slice 6b build B5b and B5c (read, nomination, gates; records, sealing, persist, closing) at 8f05d2f

You are an independent adversarial code reviewer (read-only). Repository root is the
current directory, branch `confirmation-module`, commit `8f05d2f` (or the next commit, which
only adds these notes). Do not modify any file. Your findings are proposals; you are not an
authority. This is the Constitution §16 different-model review of
`calibration/c2_confirmation.py` changes; the builder was Claude Opus 5.5.

Scope: `git diff 4dd0e92 8f05d2f` minus what the B5a review already covered: B5b
`6e4671e` (`evaluate_families` and helpers), B5c `4bb5084` (`evaluation_record`,
`seal_families`, `evaluate_look`, `Store`), and in `8f05d2f` the `of_cycle` change, the
narrowed `test_no_code_path_reads_the_report` and the `c14` rename. Read first:
`review/r14a-modules/BUILD_NOTES_SLICE6B_B5BC.md` (deviation B5B-D-1, readings B5B-R-1..4,
B5C-R-1..6), `review/r14a-modules/ADJUDICATION_B5A_53A4550.md`, and in
`review/r14a-modules/DESIGN_SLICE6B.md` (rev 16) §1, §2 step 8, §4 (closing), §5, §6, §8-§12;
`review/r14a-modules/DESIGN.md` §5.2-§5.4. Earlier functions (`nominate`, `nominee_gates`,
`family_gates`, `nominee_outcome`, `seal_family`, `sealing_record`, `cpcv_report`,
`open_look`, `check_read`, `trial_path`) are reviewed. Do not reopen owner decisions or
the rest of the design.

Check:
1. `evaluate_families`: the nomination inputs from the look's ledger (states, completed
   results, breach, every pre-look result, family seed, signed rule, classifier bounds);
   one read only when a nominee exists; each nominee's cut; every gate computed (P18-7);
   G-13 (B5B-D-1: is this reading sound, and is a missing spec correctly UNAVAILABLE?).
2. `evaluation_record` against §10 (every field, floats `hexf`, `differs`, `decision`,
   trials hashes, ledger fields); can the record misstate what the look evaluated?
3. `seal_families` and `evaluate_look`: the status (a) inputs; `persist` before the
   closing entry, exact bytes, hashes in the closing entry equal the persisted bytes'; no
   closing entry on any failure; anything written or read that should not be.
4. The `of_cycle` change: any regression in `cycle_ledger` (anchor rule) or the
   intervening check? The narrowed C-14 test: does it still enforce "no code path reads
   it"?
5. The `Store` docstring: missing or wrong obligation against §2 A-1, §2.1, §3, §4, §5.1,
   §6, §8, §12.
6. Readings and B5B-D-1: agree or propose a correction. Test quality; missing tests.

You may run: `.venv/Scripts/python.exe -m pytest tests/unit/test_c2_confirmation_families.py
tests/unit/test_c2_confirmation_look_records.py tests/unit/test_c2_confirmation_open.py
tests/unit/test_c2_confirmation_cpcv.py -q -p no:cacheprovider` (set `TMP`/`TEMP` to a
writable directory if the sandbox needs it).

Output (Markdown, concise): verdict GO / GO WITH CONDITIONS / FIX; model ID you can observe;
files and line ranges read; commands run with results; findings B5BC-A-1.. with severity,
location, evidence, failure scenario, proposed correction; one line per reading and per
B5B-D-1.
