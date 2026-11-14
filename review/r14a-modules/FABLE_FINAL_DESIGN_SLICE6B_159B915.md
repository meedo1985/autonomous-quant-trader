# Fable final review: slice 6b design rev 15 at 159b915 (verdict FIX)

- Reviewer: Claude Fable 5.2, model ID `claude-fable-5-2` (as reported by the session; run as
  a Claude Code subagent, read-only except for this file). Independent adversarial reviewer,
  not an authority. This record approves nothing, closes no owner item and makes no edit;
  every correction below is a proposal for the author and the owner.
- Date: 2026-11-14.
- Reviewed: `review/r14a-modules/DESIGN_SLICE6B.md` at commit `159b915` (rev 15), branch
  `confirmation-module` (checkout HEAD `f5570b9`; the only later change is the review prompt).
  `git diff --stat a116077 159b915` over `calibration`, `src`, `tests`, `docs`, `protocols`,
  `schemas`, `specs`, `FROZEN_HASHES.json` is empty: no code or frozen file changed.
- Prompt: `DESIGN_SLICE6B_REV15_PROMPT_FABLE.md`.

## Files and line ranges read

| File | Lines |
|---|---|
| `review/r14a-modules/DESIGN_SLICE6B.md` (rev 15) | 1-495 (whole); diff `a116077..159b915` (72+/27-, whole) |
| `FABLE_FINAL_DESIGN_SLICE6B_A116077.md`, `ADJUDICATION_FINAL_DESIGN_SLICE6B_A116077.md`, `ASTRA_RECHECK_DESIGN_SLICE6B_523B1DC.md`, `ADJUDICATION_RECHECK_DESIGN_SLICE6B_523B1DC.md`, `ASTRA_RECHECK_DESIGN_SLICE6B_DC9D1C7.md`, `ADJUDICATION_RECHECK_DESIGN_SLICE6B_DC9D1C7.md` | whole |
| `calibration/c2_confirmation.py` | 600-979, 1890-2119, 2560-2902; grep of every `screen.load`, `TrialError`, `except`, `code_dir`, `find_spec` |
| `calibration/c2_lockbox.py` | 480-808 (`ARTIFACT_KINDS`, `_check_items`, `_check_trial`, `_check_declared`, `pre_read_check`), 1195-1460 (`Store`, `Started`, `start`, `_install_trial_code`, `run_evaluation`) |
| `calibration/screen.py` | 381-400, 486-506, 575-614, 1930-1974 (`check_trial`, `trial_sha256`, `trial_set_sha256`, `load`, `_extend_path`, `_paths`, `run_screen` start) |
| `src/aqt/core/ledger.py` | 330-415 |
| `src/aqt/core/attempts.py` | 290-414 |
| `review/governance-statistics-amendment/o6a-channel/SPEC.md` | 40-150 (§3 end, §4, §5, §6-§7 start) |
| `docs/RESEARCH_CONSTITUTION.md` | 134-163 (§15-§18, §16 whole) |
| `review/r14a-modules/DESIGN.md` | 186-235 (§5-§5.3); grep for trial code |
| `OWNER_DECISIONS_DESIGN_SLICE6B_REV3.md` | grep B-1, B-3 |

Not read this round: `protocols/protocol_v1.yaml` (rev 13-15 cite no new line of it; lines
60-68 and 190-194 were checked in my rev 12 review), `dsr.py`, `classifier.py`, `qobj.py`,
the REV2 and REV6 owner-decision files (the B and C rows did not change except B-1). Not
run: tests, lint, types, import-boundary checks (design document only, no code changed).

## Verdict: FIX

The four rev 12 findings are applied, the Astra inventory correction is right against the
lockbox code, and I found no second look, no bar read before the look entry, no dropped
family, no lock-order cycle, no release without a closed look, and nothing that lets AI
approve or amend governance.

One input is still not defined, and it is the most sensitive one: the trials' signal and
overlay source code. Every evaluation path in the module loads it from the import path, the
design's `sources` "holds exactly" eight things and the code is not among them, and when it
is missing at the look the cycle is lost for good (F-1). It is a short text repair, the same
kind as R14D6B12-F-3. The other three findings are minor or info.

## 1. Status of R14D6B12-F-1..4 in rev 15

| ID | Status | Evidence |
|---|---|---|
| F-1 | APPLIED | §1 l.46-50: `persist` gets each status (a) family's sealed artifact bytes before the closing entry. §4 l.280-284, §10 l.411-414: closing entry binds the two records; the sealing record's `prediction_artifact_sha256` binds the artifact (`seal_family` l.2053 writes exactly `SHA256(cj(artifact))`, and the lockbox checks the same form, `c2_lockbox.py` l.780-791). §12 l.428-436: release rule covers the prediction. §12 l.438-446 says who builds `aqt.c2.artifacts.v1` (the store, not 6b). Test l.450-453. |
| F-2 | PARTIAL (minimum applied; optional entry not applied) | §3 l.209-214: one `evaluate_trial` process per `attempt_id`; crash outcome before anything else starts for the trial; residual states the extra reads and the bypassed crash and re-run accounting. Judged below. |
| F-3 | APPLIED (two details left open, see R14D6B15-F-2) | `sources` adds `screen_record` and `trial_objects`, each hash-checked (l.58-63); declaration field list (l.65-69); attempt binding names the confirmation partition and the family and is applied by `evaluate_trial` before any protected-data read (l.185-189; `family_attempts` l.757-760 filters the same three values). |
| F-4 | APPLIED | Release tests are required tests of the one store build (l.448-453); a true `capture_before_tip_window` must be cleared by the verifier (l.111-113) and the hard floor is in the B-1 row; look-lock waiter blocks, append lock keeps its timeout (l.270-272; `ledger.py` l.350-360). |

**The unapplied F-2 "read begun" entry.** Soundly justified as now qualified. The first
reason given (a deterministic result gives no choice of `d`) was not enough by itself, and
`ADJUDICATION_RECHECK_DESIGN_SLICE6B_523B1DC.md` withdrew it as the basis. The basis now is
the runner obligation plus a stated limit, and that is the same trust the design already
places in the runner for every start and outcome write. The residual text names both real
costs (extra protected-data reads, bypassed crash and re-run accounting). The owner should
see the one-launch rule as a P18-1 wording item; today the table does not show it
(R14D6B15-F-3).

## 2. Rev 13-15 changes, as a whole

| Change | Finding |
|---|---|
| Predictions persisted before the closing entry | Sound. `persist` returns only when records and predictions are durable; the closing entry is the last act. A crash between leaves `LOOK_WITHOUT_RECORD`, no release. |
| Prediction vs trial/code inventory, release rule | Sound and matches the lockbox: `_check_items` (l.565-597) wants the trial object and its code by hash and size, `_check_trial` (l.600-619) wants exactly the trial's signal and optional overlay, and the prediction is the separate `artifact_bytes`. The design does not say where the store gets the code bytes it must retain; they never pass through 6b (F-1). |
| `sources.screen_record`, `sources.trial_objects` | Sound as far as stated. The order of the trial set and two parse rules are not stated (F-2). |
| Declaration `[DESIGN layout]` | Accepted by the lockbox: `_check_declared` (l.719-756) reads with `.get`, so extra top-level keys pass; it needs one entry per nominee id with an `int` `trial_index`. |
| Attempt binding with partition and family | Sound; same filter as `family_attempts`. |
| One process per attempt | Sound as a runner rule; see F-2 status above. |
| Blocking look lock | Sound. Look lock then append lock everywhere; a waiter holds nothing. A live hung holder stalls every writer in the open, which is the safe side. The primitive is not named (F-4). |
| Shared-store handoff tests | The right four tests. They are a requirement on a build that does not exist yet, not evidence. |

Check 4 summary: look early, only the stated clock and header-time residuals and owner C-2;
look twice, none; bars before the look entry, none; drop a family, none; hide a crash, only
the stated relaunch residual; hide a procedure failure, only the stated residuals; release
or pick without a closed look, none; lockbox unable to run on a closed status (a) family,
none in the text once the store keeps the code bytes (F-1 note); AI approving or amending
governance, none.

## 3. Owner table

- B-1..B-5 and C-1..C-3 are not misstated. Rows that touch P18 or S4 wording name the
  clause in bold, and the header (l.22-24) ties them to the Constitution's process.
- Three things added in rev 13-15 are not shown to the owner as they should be:
  R14D6B15-F-3.

## 4. New findings

| ID | Severity | Where | Short |
|---|---|---|---|
| R14D6B15-F-1 | major (buildability; fails closed, but for good) | §1 l.55-63; §2.1 order l.146-166; §12 l.441-444 | The trials' signal and overlay code is not an input of either entry point; missing code at the look ends the cycle after the look entry. |
| R14D6B15-F-2 | minor (buildability) | §1 l.58-69; §3 l.185-188 | Trial-set order for the screen check, the 20-trial total, unique `(hypothesis_hash, trial_index)`, and object-vs-entry identity are not stated. |
| R14D6B15-F-3 | minor (owner table) | l.65, l.209-214, l.487, l.492 | The declaration layout has no owner row; the one-launch rule is not in the P18-1 row it cites; the verifier-clearance duty sits under "decided". |
| R14D6B15-F-4 | info | §4 l.266-272; §12 l.441-443 | Look-lock primitive not named; "trial object bytes" are objects in `sources`. |

### R14D6B15-F-1 (major): the trial code is not an input

- Where: §1 l.55-63 (`sources` "holds exactly" eight items); §2.1 order l.146-166; §12
  l.441-444 ("the store retains ... its hash-bound signal and optional overlay source
  bytes").
- Evidence. Every run in the module loads the trial's code with `screen.load(ref, sha256)`:
  the pre-look run and the sealing re-run through `baseline_d` (`c2_confirmation.py`
  l.1875-1879), and the nominee's gates and the CPCV report (l.459-462, 566, 2266-2285).
  `screen.load` finds the source with `importlib.util.find_spec` on the process's import
  path and refuses with `TrialError` when it is absent or not the declared hash
  (`screen.py` l.579-590). The screen takes a `code_dir` and places it last on the path
  (`run_screen` l.1965-1974, `_extend_path` l.1937-1947). The lockbox takes `files` and
  `code_dir` and installs the checked bytes into an empty directory (`_install_trial_code`,
  `c2_lockbox.py` l.1355-1369). The 6b design names neither a code directory nor code
  bytes, in `sources` or anywhere else, and says nothing about the import path. `TrialError`
  is not caught by `trial_result` (l.2836-2845) nor by the gate code (l.451, 476); in
  `seal_family` it is swallowed into status (d) (l.2044-2046).
- Failure scenario. (1) The look runs in a fresh process, as §1 requires. Its import path
  lacks one nominee's signal file (a different working directory, a rebuilt image, a file
  dropped after the trial runs). Steps 1-7 pass, the look entry is written, bars are read,
  and the first gate raises `TrialError`: abort after the look entry, `LOOK_WITHOUT_RECORD`,
  no pick for either family, no second look. If the gates happen to pass and only sealing
  fails, a nominee that passed every gate is sealed as status (d) `SEAL_FAILED:TrialError`.
  Either way the cycle's result is lost and cannot be redone. (2) In `evaluate_trial` the
  same error comes after the protected-data read, leaves no result entry, and the runner
  must record a crash, which spends the family's one re-run slot. (3) The builder invents
  the handle himself inside a §16 file. If the trial-code directory lands ahead of the
  engine on the path, a trial file can shadow a module that is imported later (the case
  S7R-R1 closed for the screen).
- Proposed correction. Add one item to `sources`: the trial code, as the lockbox takes it
  (`code_files{sha256: bytes}` plus an empty `code_dir`, installed as `_install_trial_code`
  does), or a `code_dir` placed by `screen._extend_path` (engine first, trial code last).
  Say that both entry points, after `start` and before any protected-data read, and
  `evaluate_look` before the look entry, load every declared trial's signal and overlay with
  `screen.load` (hash before execute, as `run_screen` l.1971-1974). Then missing or wrong
  code is a read-free `CycleError` with nothing written, never a post-look abort. Add the
  test: one declared trial's code absent or altered, no look entry, no read. In §12 say the
  code bytes the store retains for the lockbox inventory are these same hash-checked bytes.

### R14D6B15-F-2 (minor): four declaration details the builder would have to choose

1. Trial-set order. `check_screen_record` compares the record's `trial_set_sha256` with
   `screen.trial_set_sha256(trials)`, which hashes the list in the order given (`screen.py`
   l.495-502). The design does not say which trials, in which order. Say: all declared
   trials' objects, both families, in the declaration's `trials` list order (or the order
   the screen record itself fixes).
2. Total size. `trial_set_sha256` accepts 1 to `MAX_TRIALS` (20) trials and refuses repeated
   ids. `check_declaration` allows 20 per family (l.664). With one screen record for the
   whole declaration the real limit is 20 in total and ids unique across both families.
   Say so, and put it in the declaration builder's checks (Store docstring), because a
   declaration that breaks it is refused only after it is posted.
3. `(hypothesis_hash, trial_index)` must be unique across the declared trials. The attempt
   binding maps that pair to a `trial_id` (l.185-188; `trial_of`, code l.735, 761-765). With
   a repeated pair one trial's attempts are counted for the other, the second trial can
   never be run, and the two share `seed_l266`. Refuse it at parse (`CycleError`).
4. Each trial object's own `trial_id` and `family` must equal its declaration entry's (the
   hash check alone does not compare them with the entry), and `trial_index` must be an
   `int` (the lockbox requires `type(...) is int`, l.753). Today a mismatch is caught later
   by `trial_result` (l.2818) or the lockbox (l.615-616); catch it at parse.

Failure scenario for all four: nothing is read and nothing wrong is computed, but a posted
declaration is refused for a reason the builder could have checked, and a cycle is spent.

### R14D6B15-F-3 (minor): three items the owner table does not show correctly

1. The declaration layout is marked "[DESIGN layout, to be bound in the S4 text]" (l.65)
   and has no row. A-1 and A-2 cover four of its fields; `screen_record_sha256`, the trial
   entry fields and the "unknown or missing keys refuse" rule are not listed. Add a row,
   status "recommendation; **S4 wording**".
2. The one-launch-per-attempt rule and its residual say "(runner obligation, P18-1 wording
   row)" (l.213-214), but that row (l.492) speaks only of "no result entry before the first
   outcome = crash". Add the one-launch rule and the invisible-relaunch residual to it, so
   the owner sees that P18-1's crash and re-run count rests on a runner promise.
3. The B-1 row (l.487) now includes "a true `capture_before_tip_window` is a point the
   verifier must clear" under the status "decided as direction". The owner's B-1 decision
   (`OWNER_DECISIONS_DESIGN_SLICE6B_REV3.md` l.11) is the offline checks and the store and
   verifier obligation for a genuine, earliest capture. The clearance duty came from my
   review (R14D6B12-F-4), not from him. Mark that part "design proposal, **S4/SPEC
   wording**, to confirm".

Failure scenario: the S4 text is drafted from the table, and these three bindings either
go missing or go in as if already decided.

### R14D6B15-F-4 (info): two notes

1. The look lock is "an exclusive OS file lock" that blocks without a timeout. The only
   lock code in the repository is the ledger's private `_try_lock` poll loop with a deadline
   (`ledger.py` l.330-360). Say what the module uses: for example its own copy of that
   non-blocking try in a loop with no deadline, so the wait is the same on both platforms.
2. §12 l.441-443 calls `sources.trial_objects` "bytes"; §1 defines them as objects. The
   lockbox parses the trial item as JSON and re-derives the configuration hash (l.603-605),
   so any JSON serialization the store keeps will pass; say that, or make the handle bytes.

## What I could not check

- The drand chain-info layout and the CDX digest form (no network; both stay `[VERIFY]`).
- The store, the runner, the declaration builder and the signed C2 do not exist yet; the
  findings are against the design text and the code it cites.
- No code was run. The gate code's handling of a missing trial module (F-1) is read from
  the `except` clauses, not executed.
