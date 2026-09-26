# Task 16 research harness: independent adversarial review

Reviewer: Claude Fable (`claude-fable-5-1`), requested through the Claude Code Agent tool. This is a different model from the implementer, Claude Opus 5.5. The review was read-only against commit `b9e7580` (base `5fda787`). I ran `pytest tests/integration/test_research_harness.py` in a detached scratch worktree with `PYTHONPATH` pointing at its `src`: 7 passed. I also ran one synthetic reproduction script, shown under R-1. I did not run the full suite, ruff, mypy or lint-imports, and I did not run the harness on the real data in `data/`. The worktree has been removed.

## Findings

**R-1 (BLOCKER): the partition boundary is enforced by a name label only.** Location: `src/aqt/research/harness.py:180-187`.

- `run_exploration` checks only `manifest.partition == "exploration"`.
- `verify_partition_manifest` (`src/aqt/data/manifest.py:560-638`) checks that the bars fit the manifest's own declared window. It never compares that window with the protocol bounds, and neither does `build_partition_manifest`.
- So a self-consistent manifest labelled `exploration` but covering confirmation data passes the check, and the harness runs on confirmation bars.
- Observed with 50 synthetic bars starting at 2023-03-01 (inside the protocol confirmation window), built through `build_partition_manifest(partition="exploration", ...)` with `BUY_AND_HOLD`:
  `NOT_A_REGISTERED_TRIAL 2023-03-01 03:00:00+00:00 2023-03-03 00:00:00+00:00 46`
- The same run would accept a window that extends past 2022-01-01. It would also accept lockbox-dated bars, as long as the label says `exploration`.
- This makes the module docstring's claim at lines 15-17 ("no confirmation or lockbox bar is ever read") false, and Constitution section 7a ("Sandbox mounts exploration only") is not enforced on data content.
- A mislabelled or hand-built manifest is enough to trigger this. No hostile caller is needed.
- Repair: before `load` is called, refuse any manifest where `window_start_utc < aqt.data.klines.WINDOW_START` or `window_end_exclusive_utc > aqt.data.klines.WINDOW_END_EXCLUSIVE`. Those constants already mirror `partitions.exploration`. Because `verify_partition_manifest` already confines the bars to the manifest window, this one check also closes the "load() returns out-of-window bars" case.
- Add a test using the manifest above.

No other defect with a concrete reachable failure was found. Checks that held:

- **Decision indexing is correct.**
  - Decision bar `i` reads `bars[:i+1]` (`canonical.py:787-812`), so `i >= required-1`.
  - Execution happens at bar `i+1`, and the engine requires `i+1 >= 3`, so `i >= 2`.
  - The holding return needs bar `i+2`, so `i <= len-3`, which equals `last_index`.
  - No bar after the decision close is read.
  - Each contiguous run gets a fresh `run_backtest` call, which starts flat (`ExposureState(MIN_EXPOSURE)`, equity 1.0).
  - Short runs go to `skipped_runs` with their bar counts.
- **The tests are not vacuous.**
  - Determinism: the subprocess gets a fresh `PYTHONHASHSEED`, so it would catch set-order nondeterminism.
  - Refusal: the empty loader call list would catch removal of the name check.
  - No ledger: the monkeypatch catches module-attribute calls, and the AST import scan catches `from`-imports.
  - The key scan plus the exact `HarnessResult` field set would catch a promotion key added to `as_mapping`.
  - None of these tests covers R-1.

## Deviations and question

- **T16-01 (agree):** no permitted configuration consumes features, and before the model tasks a feature pass would be dead computation.
- **T16-02 (agree):** splitting at gaps and restarting flat is the only reading consistent with section 6 (no filling) and the contiguity checks in the engine and the benchmarks. Skipped runs are reported, not dropped.
- **T16-03 (agree, non-blocking):** vol-target history is the whole prefix of the run, so cost grows roughly quadratically with run length. That code belongs to other modules, and this is a performance issue, not a correctness one.
- **T16-04 (agree):** the protocol's "all jobs logged" requirement (`sandbox_exploration_policy`) is Task 17's scope.
- **T16-Q1:** I support the cautious reading. The partition refusal is the only code-level enforcement of section 7a in this path, so it is protocol-enforcement logic under section 16. Merging should need this different-model review plus the owner's own review. That decision belongs to the owner, not the AI.

## Roadmap acceptance

Criteria 1, 2, 3 and 5 have tests. Criterion 4 (lint-imports) is reported in LOCAL_REPORT but I did not re-run it. Criterion 2 is met only in its literal "partition name" form; R-1 is the gap in substance.

## Verdict

FIX: repair R-1 with the protocol-window check and a regression test, then re-verify.
