# Owner §16 review of PR #83 (R-14a lockbox module)

- Date: 2026-11-03. Reviewed head: `114863dadb23b57b0d79519539a7f7715ae8d12a`.
- CI on that head: run 41588837875, in progress when the review was given; the
  owner's merge approval is conditional on it (and on CI for the commit adding
  this record) passing. Run 41587423469 on 53be5d9 failed only in the
  calibration-launcher OpenBLAS probe (the known AMD EPYC runner segfault,
  exit 3, "inconclusive ... rerun the job"); the other three jobs passed.
- Form: behavioural yes/no walkthrough (Claude Code, AskUserQuestion); questions
  and answers verbatim below. Recorded by Claude Opus 5.5 (`claude-opus-5-5`);
  the answers are the owner's.

1. "§16 review of PR #83, Q1. The new lockbox module is the program that will one day compute the final lockbox test result for the strategy chosen in C2. It can never give itself permission to read the hidden lockbox data: a separate 'store' grants or refuses each read. If anything is refused or fails, the module stops and the sealed default result stands (counted as a failure, never a pass). Is that what you want?" — **Yes**
2. "§16 review of PR #83, Q2. Before reading any lockbox data, the module checks that the strategy, its settings, its seeds and the code are exactly the ones you sealed. The seeds come from the sealing record, as you decided (R14L5-S-2). Any difference means refusal, with no data read. After reading, it computes the whole result twice, BTC and ETH separately. If the two runs differ even slightly, the result is a technical FAIL. Is that what you want?" — **Yes**
3. "§16 review of PR #83, Q3. Merging does NOT activate anything. The module binds only once its SHA-256 hash is written into the signed C2. Before signing, these items remain open: the launch route; where the acceptance record comes from (your decision, R14L2-S-2); the reference numbers computed on the qualified image; the S4 format rows; the separate store build and its obligations; and the sealing record carrying both seeds. Is merging with these items still open OK?" — **Yes**
4. "§16 review of PR #83, Q4. The module went through 7 Sol (Codex gpt-6-sol) review rounds; the last one, re-check 7, was ACCEPT with no findings. Every finding and its repair is committed in review/r14a-modules/. Local checks: 130 lockbox tests pass, plus ruff, mypy strict and the import rules. CI on the PR head 114863d is still running. One earlier run failed only on the known AMD EPYC runner crash. Do you approve marking PR #83 ready and merging it, but only once CI on 114863d is green?" — **Yes, merge when green**
