<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12a98-330b-7a60-8244-f5418b9848d4. Tokens used: 31,100. Made from a packet built from commit fc214a3 (git show/diff only): the prompt below, prereg (fff4e5f) lines 490-493 and 556-575, the FE-7, FR2-2 and I1-8 texts, git diff ad0d46b..fc214a3 -- deploy scripts tests .github, pilot-cells.json, d19_pilot.py, d19.sh and PILOT_FE7.md at fc214a3, and the driver's WORKERS and executor code. -->

> # Review: D-19 FE-7 re-pilot kit at fc214a3
> 
> You are an independent adversarial reviewer working read-only. You are not an authority. The owner, who is not a statistician, will run this command sheet on his server with forward paper running beside it. Base the review on the attachments.
> 
> Attached:
> - the re-pilot requirements: §13 rev 7g item 6 ("Before the full run" and "Estimate"), item 3's thin categories, FE-7, FR2-2 and I1-8;
> - the diff;
> - the files at fc214a3: `pilot-cells.json`, `d19_pilot.py`, `d19.sh`, `PILOT_FE7.md`;
> - the driver's `WORKERS` constant and executor code.
> 
> Questions:
> 1. **Measurements.** Does the kit measure everything the re-pilot must? That means: speed per replication; memory with 2 workers; threshold-run cost; `U_G` and DSR-availability rates in the thin categories; a `U_G` rate across all groups (at least one cell each of Q1, Q2, Q2m, Q3, Q4, Q5 and QJ); non-finite threshold draws (FE-7); the two block rules timed apart (I1-8); and the failing-chain check (FR2-2). Name anything missing.
> 2. **Pilot size.** Is 9 cells × 2,000 threshold and 1,000 development replications at T = 1247 adequate for those purposes? State the resolution of the `U_G` and availability rate estimates honestly.
> 3. **The command sheet.** Is it correct and safe for a non-expert? Consider exact commands, expected outputs, the order of steps, the FR2-2 kill step (picking a `spawn_main` worker from `docker top`), stop and resume, and that nothing touches forward paper.
> 4. **`nonfinite`.** Does it count exactly the non-finite binary64 diagnostics, and nothing else?
> 5. **`d19_pilot.py`.** Is its seed namespace kept apart from any run's (FA-1)? Is the timing honest, for example using `nominee or 0` when DSR is unavailable?
> 6. **Defects.** Find any.
> 
> Output:
> - Put your model metadata at the top.
> - Give a verdict for giving the kit to the owner: ACCEPT or FIX.
> - Number findings FE7-n. Give each one a severity, a file:line, a failure scenario and the minimal fix.
> - Mark any finding that needs an owner decision.

## Review (verbatim)

**Model metadata:** Codex, GPT-6 family. The exact runtime model ID and effort are not exposed here.

**Verdict: FIX before giving the command sheet to the owner.** This is a read-only review of the supplied attachments.

The nine cells include at least one from each required group. The timing script uses a separate seed anchor and namespace from the threshold and development runs. The commands do not directly stop or modify forward paper; they do change host reboot configuration and use shared host resources.

### Findings

1. **FE7-1 — High — [pilot-cells.json](deploy/calibration/pilot-cells.json:4).** **Scenario:** Each thin category—QJ, Q1 unequal clusters, and Q2m—has only one pilot cell, although the requirement calls for rates *in the 2–3 cells* of each category. At 1,000 development replications, one event changes a cell’s rate by 0.001. At a true `U_G` rate of 0.00005, a cell expects 0.05 events and will usually report zero. Zero events gives a roughly 0.003 upper 95% bound per cell; even pooling all ten family tests across the nine cells gives a roughly 0.0003 bound and hides differences between groups. DSR availability has 0.001 resolution per cell; near 50% availability its approximate 95% margin is ±3.1 percentage points. **Minimal fix:** include every thin-category cell and report per-cell, per-family `U_G` and DSR-availability numerators, denominators, and intervals. **Owner decision:** set the precision and additional replication budget; this sample can serve as a smoke test, not a reliable rare-event escape-rate estimate.

2. **FE7-2 — High — [PILOT_FE7.md](deploy/calibration/PILOT_FE7.md:61).** **Scenario:** Killing a worker and resuming tests failure handling, but the sheet never compares an interrupted-and-resumed cell with a clean run. The required byte-identity test remains unshown. **Minimal fix:** run the same seeded cell clean in a separate store and compare its final chunk bytes and chain head with the resumed cell before the full run.

3. **FE7-3 — High — [PILOT_FE7.md](deploy/calibration/PILOT_FE7.md:103).** **Scenario:** Chunk modification times do not give speed per replication or total threshold cost: they omit work before the first completed chunk, discarded work, and the timing of two concurrent workers. The three synthetic timing rows also do not time the actual nine-cell threshold run. **Minimal fix:** record start, end, elapsed time, and replication counts for each stage and cell, including the interrupted attempt, then report threshold wall time and worker time.

4. **FE7-4 — Medium — [PILOT_FE7.md](deploy/calibration/PILOT_FE7.md:90).** **Scenario:** One `docker stats --no-stream` reading after 600 seconds can miss peak memory or catch a moment without two active workers. `free -m` does not establish the container’s two-worker peak. **Minimal fix:** sample container memory throughout a verified two-worker interval and report its maximum.

5. **FE7-5 — High — [d19.sh](deploy/calibration/d19.sh:139).** **Scenario:** `nonfinite` searches every quoted 16-digit hexadecimal string in every matching chunk. It cannot distinguish threshold diagnostic draws from other encoded values or reject corrupt chunks; an absent threshold directory can also yield `0` while `find` fails. Thus the number is not an exact FE-7 count. **Minimal fix:** parse validated threshold chunks and count exponent-all-ones values only in the specified diagnostic field, failing on missing or invalid input. **Owner decision:** if the corrected count is positive, the owner must decide its treatment before proceeding, as FE-7 requires.

6. **FE7-6 — Medium — [d19_pilot.py](scripts/d19_pilot.py:45).** **Scenario:** The timer replaces the classifier with `lambda *_: True` and calls `u_g` with `nominee or 0`, including when DSR supplies no nominee. It can therefore time work the run would skip and omit classifier work the run performs. Its largest timed `K` is 20, so `T = 1247` alone does not establish an upper cost bound. **Minimal fix:** time the production decision path, skip `u_g` when no nominee exists, and include the costly grid shapes. Keep the two block-rule times separate. **Owner decision:** once measured, the owner decides whether the second rule’s cost warrants a preregistration change; the current accepted rule remains the basis for the estimate.

7. **FE7-7 — High — [PILOT_FE7.md](deploy/calibration/PILOT_FE7.md:63).** **Scenario:** The manual `spawn_main` PID selection can kill the wrong process if copied incorrectly. Afterward, merely seeing `Exited` and a failing `docker top` neither requires a nonzero run exit nor checks the surviving worker’s host PID. A fixed 30-second sleep may also lead to a premature resume. **Minimal fix:** automate selection after asserting exactly two workers in `aqt-d19`, record both PIDs, require a nonzero exit and disappearance of the other PID, and resume only after that check passes.

8. **FE7-8 — Medium — [PILOT_FE7.md](deploy/calibration/PILOT_FE7.md:41).** **Scenario:** Repeating `cp -r source/raw destination/raw` when the destination already exists creates `raw/raw`, leaving the earlier data at the path used by `manifests` and `record`. The sheet also treats “every displayed line shows 4/2” as completion without requiring all nine cell lines. **Minimal fix:** make the copy step fail clearly when the destination exists or define a checked refresh procedure; require nine expected cell lines and successful exit for each namespace.

**Pilot-size conclusion:** 2,000 threshold replications per cell can measure cost if elapsed time is recorded, and can detect non-finite draws that occur. A zero count cannot establish that draws are absent. The 1,000 development replications per cell do not resolve the rare `U_G` rates used for the escape estimate.
