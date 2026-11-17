# Fable final review: slice 6b build (B1-B5) at 24f0c95 (verdict GO WITH CONDITIONS)

- Reviewer: Claude Fable 5.2, model ID `claude-fable-5-2` (as reported by the session; run as
  a Claude Code subagent, read-only except for this file). Independent adversarial reviewer,
  not an authority. This record approves nothing, closes no owner item, merges nothing and
  edits nothing; every correction below is a proposal for the builder and the owner.
- Date: 2026-11-16.
- Reviewed: `calibration/c2_confirmation.py` and `tests/unit/test_c2_confirmation_*.py` at
  `24f0c95`, branch `confirmation-module` (checkout HEAD `7b24fd7`, which only adds the
  prompt). `git diff --name-only 8d63b21 24f0c95` outside `review/r14a-modules/` and the
  confirmation tests lists only `calibration/c2_confirmation.py`; the diff over `docs`,
  `protocols`, `schemas`, `specs`, `FROZEN_HASHES.json` is empty.
- Prompt: `BUILD_SLICE6B_FINAL_PROMPT_FABLE.md`.

## Verdict

**GO WITH CONDITIONS** to the owner's §16 PR review. I found no path that reads protected
data before its checks, looks early, looks twice, lands a result inside a look, drops a
family, or writes a closing entry before `persist` returns. I found no blocker. The
conditions are F-1 (a joined test, before merge) and a decision on F-2, F-3 and F-7; the
rest are minor or informational. "GO" here means "ready for the owner to review", not
"approved to merge".

## Files and line ranges read

| File | Lines |
|---|---|
| `review/r14a-modules/DESIGN_SLICE6B.md` (rev 16) | 1-523 (whole) |
| `calibration/c2_confirmation.py` | 340-470, 630-1040, 1044-1075, 1570-1622, 1660-1790, 1922-2186, 2249-2425, 2575-2592, 2720-4543 (all of 6b); list of all top-level definitions; hunk list of `git diff 8d63b21 24f0c95` |
| `src/aqt/core/ledger.py` | 60-90, 108-126, 222-236, 296-312, 366-415 |
| `src/aqt/core/attempts.py` | 150-160, 226-300, 365-487 |
| `src/aqt/data/manifest.py` | 74-80, 641-672; `verify_composite_manifest` raise sites |
| `calibration/screen.py` | 344-358, 530-601, 926-990, 1616-1632, 1937-1957; `walk_forward` raise sites |
| `calibration/dsr.py` | 46-55 (`FamilyResult`); `qobj.py`, `choices.py`, `reduce.py`, `classifier.py`: grep for `z_crit`, `family_block_rule`, `for_k`, `within` only |
| `docs/RESEARCH_CONSTITUTION.md` | 136-160 (§15-§17) |
| `ADJUDICATION_B1..B5BC` (six) | whole |
| `BUILD_NOTES_SLICE6B_B1`, `_B4`, `_B5A`, `_B5BC`, `VERIFY_CAPTURE_DIGEST_2026-11-15.md` | whole (B1 and VERIFY: first 600 columns of each line) |
| `ASTRA_REVIEW_B1..B5BC` (six) | finding IDs and model lines only (grep); bodies **not** read |
| `tests/unit/test_c2_confirmation_trial.py` | 1-124; `..._cpcv.py` diff `8d63b21..24f0c95` (whole); test names of `_families`, `_look_records`, `_open`, `_trial`, `_prepare`, `_read` |

Not read: `BUILD_NOTES_SLICE6B_B2`, `_B3`; the Astra record bodies; `calibration/c2_lockbox.py`
(the pinned-section identity is taken from `test_c2_confirmation_start.py` passing);
`protocols/protocol_v1.yaml`; the BLS code (l.1173-1568); the bodies of most tests. Test-only
repairs (B1-A-3, B2-A-6, B2-A-7, B3-A-3, B5A-A-2 and the "extra tests" lists) were checked by
the suite passing and by test names, not by reading each test.

## Commands run

| Command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest tests/unit -k c2_confirmation -q -p no:cacheprovider` (`TMP`/`TEMP` set to a scratch directory) | 593 passed, 2205 deselected, 199.6 s |
| `.venv/Scripts/ruff.exe check calibration tests/unit/` | All checks passed |
| `.venv/Scripts/mypy.exe calibration/c2_confirmation.py` | Success: no issues found in 1 source file |
| `.venv/Scripts/lint-imports.exe` | 7 kept, 0 broken |
| inline `python -c` (no file written): `cycle_ledger` with a result entry whose `attempt_id` is a list; with a start payload lacking `cycle`; `completed_entry` with a 7-character `engine_commit`; `benchmark_spec_sha256()` | `TypeError` (not `CycleError`); `KeyError` (not `CycleError`); `CycleError: the pre-look identity fields are not canonical`; `None` |
| `git status --short` after the run | clean before this file was written |

## Check 1: whole-flow safety (what I traced, by reading)

| Question | Result |
|---|---|
| Trial: read before rule 4 | No. `evaluate_trial` l.4063-4066: `prepare`, `trial_may_run`, then `run_trial` (the only `read()`, l.4028) |
| Look: read before the look entry | No. `evaluate_look` l.4477-4479: `open_look` appends at l.4142; the only `read()` is l.4247 |
| Early look (day 180, clock floor, breached families) | `look_allowed` l.856-880 under the look lock; refusal precedes the append. Breached families are skipped as owner C-2 says; if every family is breached the look is allowed at once (follows from C-2) |
| Second look | `look_allowed` l.868 and `cycle_ledger` l.3562, both inside the lock; the re-read l.4148 checks the appended entry is the one look |
| Result inside steps 4-7 | `evaluate_trial` l.4067-4069 re-checks and appends under the look lock |
| Family, crash, breach or procedure failure dropped | `evaluation_record` iterates the declared families; `sealing_record` requires exactly the declared set; `attempts`, `breaches`, `u_proc_results` are recorded. Not covered: F-10 |
| Closing entry without `persist` | No. l.4485 precedes l.4493; an exception in `persist` propagates |
| Caller value standing unverified | Each `sources` handle is hash- or signature-checked before use. Exceptions: `started` itself (F-8); the benchmark spec file (owner decision B5B-D-1, fails closed) |

## Findings

### R14B6F-F-1 (major): no test joins the real producers to the real consumers; the stated obstacle does not hold

- Location: `tests/unit/test_c2_confirmation_trial.py` l.33-62, `..._families.py`,
  `..._open.py`, `..._look_records.py`, `..._prepare.py`.
- Evidence: every step test hand-builds its neighbour's output. `Inputs` is constructed with
  `signed=None, headers=None, capture=None` and a hand-written `seeds` dict (trial test
  l.50-54); result payloads are built from `inputs().expected(...)`, not from `trial_result`;
  `prepare` is replaced by a lambda; `run_trial`, `nominee_gates`, `cpcv_report`, the headers,
  capture and seed checks are recorders. `grep "trial_result("` over `tests/unit` hits only
  `test_c2_confirmation_run.py`, which never passes its output to `family_ledger`. So no test
  shows that a payload written by `trial_result` with `derive_seeds`' real record is accepted
  by `family_ledger` through `Inputs.expected`, or that the `d` the trial stage hashes is the
  `d` `seal_family` recomputes from the look's path (the `d_sha256` check in
  `prediction_artifact`). I traced both seams by reading and found them consistent (19 keys
  both sides; `seeds["families"][f]["trials"][id]` carries every field read; `trial_path`
  gives `warmup + hours + 1` rows, which `nominee_gates`, `baseline_d`, `cpcv_report` and
  `seal_family` all require). Reading is not a test.
- The builder's reason ("synthetic beacon not possible: BLS needs a real round") is not an
  obstacle. `headers_check` checks no proof of work, so six linked 80-byte headers are
  synthetic; the capture record is checked offline for self-consistency, so it is synthetic;
  its timestamp can be chosen so that `beacon_round` (l.1570-1594) gives round 1,000,000,
  whose real quicknet signature is already a known answer in `test_c2_confirmation_bls.py`
  l.163; `Started` is a dataclass the test can build, with `load_line266` loaded as the seed
  tests do.
- Failure scenario: a later edit changes one side of a seam (a key in `derive_seeds`' record,
  the identity field set, the cut in `run_trial` vs `evaluate_families`). Every step test
  still passes; the first real cycle reads all its confirmation data and then refuses at the
  look, or seals status (d) for every nominee. The cycle is spent.
- Proposed correction: one joined test before merge. Real `prepare` (real `signed_c2`,
  `headers_check`, `check_capture_record`, `install_code`, `derive_seeds` with the known
  round); real `evaluate_trial` for every declared trial on synthetic bars and a synthetic
  composite; real `evaluate_look` with real `open_look`, `nominate`, `seal_family` and a
  `persist` recorder. If the frozen gate code is too slow on the fixed window (about 1,200
  days), `nominee_gates` and `cpcv_report` may stay recorders, stated as such. Assert: each
  result entry is accepted at the look; `trials{id: record_sha256}`; a status (a) artifact
  whose `source.d_sha256` equals the pre-look value; the closing entry's two hashes.
  My answer to prompt question 5: the gap is not acceptable before merge in its present
  width; it is acceptable once narrowed to the frozen gate code only.

### R14B6F-F-2 (minor): three look-only checks are decidable before any trial reads

- Location: `open_look` l.4108-4114, l.4136-4139; `prepare` l.3927-3976; `BUILD_NOTES_SLICE6B_B4.md` B4-R-6.
- Evidence: the qualification re-read, the `z_crit` and `family_block_rule` equality with the
  object, and `classifier_bounds(T, K_f)` depend only on the signed C2, the object directory
  and the declaration. `evaluate_trial` receives `object_dir` (it must, `SOURCE_KEYS` is
  exact) and never opens it. The `Store` docstring asks the declaration builder to check
  only the thresholds.
- Failure scenario: a signed `z_crit` that differs from the object's by one character. Every
  `evaluate_trial` reads the confirmation data and writes its result; `evaluate_look` then
  refuses, every time. No look is possible; the data has been read for nothing.
- Proposed correction (design change, owner): run the three checks in `prepare`, so both
  entry points refuse read-free; or, at least, add the two equalities to the declaration
  builder's obligations. Related fact, not a reopening of B5B-D-1: at `24f0c95`
  `specs/CANONICAL_BENCHMARKS_v1.1.md` does not exist (`benchmark_spec_sha256()` returned
  `None`), so at this checkout every nominee would be `NO_RESULT` (G-13
  `BENCHMARK_SPEC_MISSING`, U_ops). That too is knowable before any read.

### R14B6F-F-3 (minor): the identity fields' form is first checked after the protected read

- Location: `trial_result` l.2959 (`completed_entry`, form check l.2985-2994), reached from `run_trial` l.4035 after `read()` l.4028.
- Evidence: `completed_entry` requires `engine_commit` to be 40 lower-case hex and
  `image_digest` non-empty. `start` (pinned) does not fix those forms: `line266_sources`
  passes `engine_commit` to `git show <commit>:<path>`, which accepts an abbreviated hash, and
  the only other check is equality with the object's definition. Confirmed inline:
  `completed_entry` with a 7-character `engine_commit` raises `CycleError`.
- Failure scenario: a C2 signed with a short `engine_commit`. `start` passes; each
  `evaluate_trial` reads, computes, then raises with nothing appended; the runner records a
  crash; the re-run crashes the same way. Every family ends U_ops after all its data was read.
- Proposed correction: in `prepare`, check the form of every value `result_identity` will
  write (a few lines, reusing `_hex`), with one test. Same class of defect as F-2.

### R14B6F-F-4 (minor): malformed ledger content raises `TypeError`/`KeyError`, not `CycleError`

- Location: `cycle_ledger` l.3546-3547 (`p["cycle"]`, `p["protocol_hash"]` on
  `recorded_attempts`' payloads, which `attempts.py` l.277 returns unvalidated); `of_cycle`
  l.3498, l.3501 (`... in ours` with an unhashable value; l.3501 is the B5A-A-1 line of
  `8f05d2f`); `family_ledger` l.3392; `open_look` l.4150-4152.
- Evidence: both reproduced inline (table above).
- Failure scenario: fails closed, so no safety loss. But the B1-A-1 rule ("a malformed input
  is a `CycleError`") is not met for ledger entries, and a caller that treats `CycleError` as
  the refusal type sees a crash instead. In `open_look`'s scan after the append it is an
  abort after the look entry (the same end as the `CycleError` there).
- Proposed correction: validate starts before use in `cycle_ledger` (as `family_attempts`
  does through `attempt_counts`), require `attempt_id` to be a `str` in `of_cycle`, and wrap
  `AttemptError`; three tests. This is the only thing I found in the `of_cycle` change of
  `8f05d2f`; the change itself is right.

### R14B6F-F-5 (minor): the statement-level C-14 guard has stated-nowhere limits

- Location: `tests/unit/test_c2_confirmation_cpcv.py` `c14_violations` (repair `9e0487d`).
- Evidence: the guard is by name. It accepts `ev.cpcv is None` and `_plain(ev.cpcv)` anywhere
  in `evaluation_record`, so `"outcome": None if ev.cpcv is None else ev.outcome` passes. It
  does not see a read of the serialised record by string key
  (`evaluation["families"][f]["cpcv"]` in `evaluate_look` or `seal_families`),
  `getattr(ev, "cpcv")`, `dataclasses.asdict(ev)`, or a function handed the whole
  `FamilyEvaluation`. The repair introduced no defect that I found.
- Proposed correction: add one behavioural test: run `evaluate_families`,
  `evaluation_record` and `seal_families` twice with two different `cpcv_report` recorders
  and assert that everything except the `cpcv` field (and the hashes that cover it) is
  equal. State the static guard's limits in its docstring.

### R14B6F-F-6 (minor): an unexpected exception in the diagnostic ends the cycle

- Location: `evaluate_families` l.4274; `cpcv_report` l.2249-2402.
- Evidence: `cpcv_report` converts `RunUnavailable`, `StatisticsError` and the fit's
  exceptions into report fields, but anything else it raises (for example
  `g12_gate.values["ess"]` absent, a `TrialError`, an error in `screen.labels` or
  `g11_targets` outside the wrapped calls) leaves `evaluate_families` after the look entry.
- Failure scenario: a report nothing may read (§9) aborts the look; both families end
  `LOOK_WITHOUT_RECORD`, no pick.
- Proposed correction (design choice, owner): in `evaluate_families`, record a failed C-14 as
  `{"role": "diagnostic_only", "status": UNAVAILABLE, "reason": "C14_ERROR:<type>"}` instead
  of aborting. I rate this minor because I did not find a concrete input that triggers it.

### R14B6F-F-7 (minor): capture record v2 has open [VERIFY] points that can refuse a cycle for good

- Location: `check_capture_record` l.3106-3162; `VERIFY_CAPTURE_DIGEST_2026-11-15.md`.
- Evidence: the known answer is one `blockstream.info` capture. `mempool.space`, the other
  qualifying host, was not checked (archive offline that day). Only `identity` and `gzip` are
  accepted; a capture stored with another encoding (`br`, `zstd`) or with a trailing newline
  is refused. Rev 16 §2 says of the capture floor that a refusal of the genuine earliest
  capture "would be permanent (the SPEC fixes the earliest capture)"; the same holds here.
  `gzip.decompress` runs on caller bytes with no size bound.
- Proposed correction: before signing, a `mempool.space` known answer; an owner/SPEC rule for
  an earliest capture the module cannot decode; a small cap on `payload` length before
  decompressing (the body is 64 characters).

### R14B6F-F-8 (minor): `started` is a caller value whose origin the module does not check

- Location: `prepare` l.3927-3940; `evaluate_trial`, `evaluate_look` signatures.
- Evidence: every check hangs on `started.protocol`, `started.declaration` and
  `started.chain_log`. The entry points accept any `Started` instance. The only tie to a real
  `start` in the process is that `derive_seeds` needs line 266 loaded. A `Started` built by
  hand, or kept from an earlier `start` on other bytes in the same process, is used as
  verified. This is the R14D6B-S-1 rule at the outer boundary.
- Failure scenario: a runner that calls `start` once and then builds or reuses `Started`
  objects for several evaluations (against §1's "fresh process").
- Proposed correction: `start` is in the pinned section and cannot record its return value.
  Either a 6b wrapper that calls `start`, remembers the object and is the only accepted
  source (identity check in `prepare`), or the rule written into the `Store` docstring as a
  launch-route obligation (it is not there now).

### R14B6F-F-9 (info): DSR nominees in the record are column numbers with no column order

- Location: `evaluation_record` l.4346-4355; `dsr.FamilyResult.nominee` (`dsr.py` l.50).
- Evidence: `families.<f>.nominee` is a trial id; `dsr.V.nominee`, `dsr.task12.nominee` and
  `dsr.decision.nominee` are integers, columns in ascending trial-id order (`nominate`
  l.942). The record does not carry that order. `decision` is Task 12's as §9 says, while V
  governs; a reader may take "decision" for the governing one.
- Proposed correction: add the column order (the sorted trial ids) to the `dsr` block, with
  the other §10 field additions; or bind it in the S4 text.

### R14B6F-F-10 (info): a sealing failure has no P18-7 cause in either record

- Location: `seal_family` l.2126-2128; `evaluation_record` l.4341.
- Evidence: status (d) `SEAL_FAILED:<reason>` exists only in the sealing record, which has
  no cause field; the evaluation record is hashed before sealing and cannot carry it.
- Proposed correction: owner wording item (how such a family is counted, U_ops or U_proc).

### R14B6F-F-11 (info): the deviations are spread over six notes; the design text is still rev 16

- Evidence: §2.1 still says `capture_record.v1` and "`body` hashes to `digest`"; §1 lists no
  `protocol_hash`; §7 lists no `drand_group_hash`, `drand_beacon_id`; §10 lists no
  `breaches`, `attempts` or per-gate `cause`; `U_OPS_REASONS` gained an entry. Each is
  recorded in a note or adjudication, none in the design. The B4-A-1 consequence (a comment
  that names a row anywhere in the signed C2 makes `signed_c2` refuse every run) is recorded
  only as an "S4 drafting note" in the adjudication.
- Proposed correction: one list of every deviation from rev 16 (or a rev 17) for the owner's
  PR review; a pre-signing step that runs `signed_c2` on the candidate C2 bytes.

## Check 2: design conformance

§1-§13 are implemented as written apart from the recorded deviations (B1-D-1, B1-D-2,
B4-D-1, B5B-D-1) and the B5BC-A-2 field additions. Readings that narrow the text and are
recorded in the notes: `read` is called only when a family has a nominee (B5B-R-1), so with
no nominee the look makes no manifest check; the closing entry is appended even after a
termination entry (B5C-R-5). I found no silent deviation and no rev 16 requirement without
code. The §12 release tests are not in 6b, as §12 says.

## Check 3: repairs

All 21 Astra finding IDs in the six records appear in the adjudications (compared by grep).
Code repairs checked against the code: B1-A-1 (l.3124, 3174-3187, 3202-3208, 3278-3284),
B1-A-2 (`_strict_time`), B2-A-1 (l.3391-3394), B2-A-2 and A-3 (l.766-778), B2-A-4 (l.958),
B2-A-5 (l.3427), B3-A-1 and A-2 (`_control_ok`, l.3553), B3-R-7 (l.3706), B4-A-1 (l.3776-3779),
B4-A-2 (l.3783), B5A-A-1 (l.3499-3501), B5BC-A-1 (l.4304-4311, 4341, 4360), B5BC-A-2
(l.4337-4338), B5BC-A-3 (the test). Each is as its adjudication says. None was left
unrepaired except B5BC-O-1, which went to the owner. New defects from repairs: none beyond
F-4 (exception type) and F-5 (guard limits). The last two commits (`9e0487d`, `24f0c95`)
have had no different-model review other than this one.

## Check 6: §16 and governance

Nothing in the build, notes or records has an AI approve, merge, amend or activate
governance. The code comments mark the list, the row additions and the G-13 source as
design readings or owner decisions with S4 wording to follow. `ADJUDICATION_B1` says B1-D-1
and B1-D-2 "are accepted by this review" and, in the next sentence, that they remain design
changes for the owner; that is correct but easy to misread. The three owner decisions are
chat quotes written down by the builder; the owner should confirm them in his own words in
the PR review.

## Owner decisions and open deviations

| Item | Result |
|---|---|
| B4-D-1 | Applied as recorded: `C2_ROWS` l.3723-3728, `drand_chain_hash` l.3750-3761, checked l.3815-3818. Not presented as amended governance |
| B5B-D-1 | Applied as recorded: `BENCHMARK_SPEC` l.4163, `benchmark_spec_sha256` l.4166-4173, UNAVAILABLE override l.4271-4272. The file is absent at this checkout (see F-2) |
| B5BC-O-1 | Applied as recorded: `U_OPS_REASONS` l.651-653, with its test |
| B1-D-1 (my view) | Accept the v2 schema: the evidence is sound, the CDX digest covers the stored bytes and v1's rule cannot pass for a gzip capture. Conditions before signing in F-7 |
| B1-D-2 (my view) | Accept: without `protocol_hash` in the key set every real declaration is refused, and `verify_chain` already compares its value. The added form rules are read-free and fail closed. The S4 layout must take the code's key set, not rev 16's |

## Before the owner's PR review

1. Add the joined test of F-1 and run the four checks again.
2. Decide F-2 and F-3 (move the read-free checks into `prepare`, or state the obligations).
3. Repair F-4 and add F-5's behavioural test; decide F-6 and F-8.
4. Record F-7's open points as pre-signing items.
5. Write the single deviation list of F-11, with F-9 and F-10 as wording items.
6. Commit this record and the builder's adjudication of it before any repair commit cites it.
7. Then the owner's own §16 PR review; no AI review stands in for it.
