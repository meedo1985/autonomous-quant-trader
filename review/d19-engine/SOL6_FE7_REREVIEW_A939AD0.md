<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12ab7-bbe3-7081-878e-8c02bf538d81. Tokens used: 30,290. Made from a packet built from commit a939ad0 (git show/diff only): the prompt below, SOL6_FE7_REVIEW_FC214A3.md, ADJUDICATION_FE7_FC214A3.md, OWNER_DECISION_FE7_PILOT_SIZE.md, git diff fc214a3..a939ad0 -- deploy scripts tests .github, and d19.sh, PILOT_FE7.md, pilot-cells.json, d19_pilot_checks.py, d19_pilot.py at a939ad0. -->

> # Focused re-review: D-19 FE-7 re-pilot kit repairs (fc214a3..a939ad0)
> 
> You are an independent adversarial reviewer working read-only. You are not an authority. Review ONLY the repairs of your findings FE7-1..FE7-8, using:
> - your review;
> - the adjudication;
> - the owner's pilot-size decision;
> - the diff;
> - the files at a939ad0: `d19.sh`, `PILOT_FE7.md`, `pilot-cells.json`, `d19_pilot_checks.py`, `d19_pilot.py`.
> 
> **CI at a939ad0.** All four jobs passed. `calibration-launcher` ran on AMD EPYC 7763 and printed:
> - `status`, with "started ... finished ... exit 0" and "slice memory peak: 227713024 bytes";
> - `nonfinite`: "pilot-k1: 0 non-finite of 24", "pilot-k2: 0 non-finite of 30", "all cells: 0 non-finite of 54";
> - `clean-check`: "pilot-k1: 1 chunks identical", "pilot-k2: 1 chunks identical", "PASS: the resumed threshold run equals the clean run".
> 
> The first CI run of this repair failed because `.locks` (the chain lock directory) was treated as a cell. That is fixed in a939ad0 and covered by the test. `failcheck` is not exercised in CI: the tiny CI pilot ends in about 13 s. The engine's unit tests cover the killed-worker path.
> 
> **Questions.**
> 1. Is each of FE7-1..FE7-8 resolved?
> 2. Is the command sheet now correct and safe for a non-expert owner?
> 3. Is `failcheck` correct? Look at the worker selection, the stop wait, the exit-code check and the survivor check.
> 4. Did the repairs introduce any new defect?
> 
> **Output.**
> - Put your model metadata at the top.
> - Give a verdict for giving the kit to the owner: ACCEPT or FIX.
> - For each prior finding, say resolved or unresolved.
> - Number new findings FE7R-n. Give each one a severity, a file:line, a failure scenario and the minimal fix.

## Review (verbatim)

**Model metadata:** Codex, GPT-6 family. The exact runtime model ID and reasoning effort are not exposed in this session. Claude Opus 5.1 was not available here; no Claude model performed this re-review.

**Verdict: FIX before giving the kit to the owner.** The reported CI results support the normal run, non-finite count, and clean comparison paths. They do not exercise `failcheck`, and several measurement and command-sheet gaps remain.

| Prior finding | Status | Reason |
|---|---|---|
| FE7-1 | **Resolved** | The 13 cells cover the thin categories. The owner explicitly chose 1,000 development replications per cell with the rare-event limit disclosed. |
| FE7-2 | **Unresolved** | `compare` checks two fields per chunk, not chunk bytes or the chain head. The purported clean store can also be reused. |
| FE7-3 | **Unresolved** | `status` supplies namespace start and finish times, but no per-cell elapsed time or measured worker time per replication. Multiplying wall time by two does not measure worker time. |
| FE7-4 | **Unresolved** | `MemoryPeak` is the slice peak across its lifetime. The sheet does not verify two workers during the reported measurement or isolate the development interval. |
| FE7-5 | **Resolved** | The checker decodes threshold result values as binary64 and counts NaN and infinity; it fails on missing chains. The sheet runs it after chain verification by `choose`. |
| FE7-6 | **Unresolved** | Skipping `U_G` without a nominee is fixed, but the timer still substitutes an always-true classifier. Its reported DSR time is not an established upper bound for the production path, which must execute the classifier. |
| FE7-7 | **Resolved in code; untested end to end** | `failcheck` selects two `spawn_main` host PIDs from the named container, kills one, waits up to 120 seconds, requires a nonzero container exit, and checks the other PID is gone before printing `PASS`. CI did not run this path. |
| FE7-8 | **Unresolved** | When `raw` already exists, `test ! -e ... && cp ...` silently skips the copy. An interactive shell continues with manifests and recording against the existing data. |

### New findings in the repairs

1. **FE7R-1 — High — `scripts/d19_pilot_checks.py:67`.** A clean chunk can have the same `content_sha256` and `results` fields but different remaining bytes or chain metadata; `compare` prints `PASS`. Compare the complete chunk bytes and the verified final chain head for every expected cell.

2. **FE7R-2 — Medium — `deploy/calibration/d19.sh:151`.** A second `clean-check` resumes an existing `store-clean`, so an interrupted clean attempt can become another resumed run while the sheet calls it “from scratch.” Refuse to start when `store-clean` exists, or create a new empty store for each check.

For the owner sheet, fix the silent raw-data skip and state what timing and memory figures actually measure before asking the owner to rely on them.
