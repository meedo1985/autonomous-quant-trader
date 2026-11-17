# Astra short check: repairs of the final Fable 6b review, the joined test, the deviation list

You are an independent adversarial code reviewer (read-only). Repository root is the
current directory, branch `confirmation-module`, at the commit that adds this prompt. Do not
modify any file. Your findings are proposals; you are not an authority. This is the
Constitution §16 different-model check of changes to `calibration/c2_confirmation.py` and
its tests; the builder was Claude Opus 5.5. Keep it short: this is a check of three
commits, not a new review of the build.

Scope:
1. `f1974a7` (`git diff 95e5574 f1974a7`): repairs of R14B6F-F-2, F-3, F-4, F-6, F-7 (cap),
   F-8 (docstring), F-5 (guard limits).
2. `867fcc6`: `tests/unit/test_c2_confirmation_joined.py`, the joined test for F-1 and the
   behavioural test for F-5.
3. `89c1f83`: `review/r14a-modules/DEVIATIONS_SLICE6B_REV16.md` (F-11).

Read first: `review/r14a-modules/FABLE_FINAL_BUILD_SLICE6B_24F0C95.md` (the findings),
`review/r14a-modules/ADJUDICATION_FABLE_FINAL_6B_24F0C95.md` (the decisions). Do not reopen
owner decisions (B4-D-1, B5B-D-1, B5BC-O-1) or the design.

Check:
1. Does each repair do what the adjudication says, without a regression? In particular:
   F-2 (`qualification_checks` in `prepare` before the code install and seeds; `open_look`
   still re-checks); F-3 (`_code_identity_ok` in `prepare`); F-4 (`_starts`,
   `family_attempts`, `of_cycle` on malformed entries: refuse, never crash or count as
   ours); F-6 (the C-14 fallback: can it hide anything other than the diagnostic?); F-7 cap
   (before any decompression).
2. The joined test against Fable's F-1 request: are the producers and consumers it calls
   really the module's, wired as the entry points wire them? Are the stand-ins
   (`nominee_gates`, `cpcv_report`, `qobj.read`, `benchmark_spec_sha256`, hand-built
   `Started`, `persist`, `dsr._V_VERIFIED`) stated and no wider than needed? Would it catch
   a change on one side of the seams Fable named (a key in `derive_seeds`' record, the
   identity field set, the cut in `run_trial` vs `evaluate_families`, the `d` hashed before
   the look vs the `d` sealed)? Is the F-5 test sound (fixed clock, copied ledger, which
   keys it drops)?
3. The deviation list: is any deviation, field addition or reading from the build notes,
   the adjudications or the Fable record missing or misstated? Is any status wrong (an
   owner acceptance claimed without a recording commit)?

You may run: `.venv/Scripts/python.exe -m pytest tests/unit/test_c2_confirmation_joined.py
tests/unit/test_c2_confirmation_prepare.py tests/unit/test_c2_confirmation_look.py
tests/unit/test_c2_confirmation_families.py tests/unit/test_c2_confirmation_inputs.py -q
-p no:cacheprovider` (set `TMP`/`TEMP` to a writable directory if the sandbox needs it).

Output (Markdown, concise): verdict GO / GO WITH CONDITIONS / FIX; model ID you can
observe; files and line ranges read; commands run with results; findings B6FR-A-1.. with
severity, location, evidence, failure scenario, proposed correction.
