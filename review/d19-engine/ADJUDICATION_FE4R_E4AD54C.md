# Adjudication of the GPT-6 Sol re-review of D-19 FE-4 at e4ad54c

**Review:** `review/d19-engine/SOL6_FE4_REREVIEW_E4AD54C.md`. The verdict was FIX. FE4-1..FE4-8 are resolved, and the FE4-3 disagreement was judged justified. The re-review raised four new findings, FE4R-1..FE4R-4.

**Adjudicated and repaired by:** Claude Opus 5.5 (`claude-opus-5-5`) on 2026-10-11. Not yet re-reviewed.

| ID | Decision | Repair and evidence |
|---|---|---|
| FE4R-1 Major | AGREE, repaired | `d19.sh probe` exits **3** only for the known crash: a segmentation fault (container exit 139) of the engine's own `rundef.gating`. Any other failure keeps its own exit status and says it is "not the known CPU crash". |
| FE4R-2 Major (owner, if a green run without validation were proposed) | AGREE, repaired so that no owner decision is needed | The skip is gone. On an incompatible runner, both calibration jobs **fail**, marked "inconclusive: rerun the job". A green run therefore always ran the engine tests and the launcher exercise. Which CPU a job gets is chance, so a rerun is the remedy. Nothing green is claimed without validation. The section of `ADJUDICATION_FE4_1C44DB8.md` that described the skip is superseded here. |
| FE4R-3 Moderate | AGREE, repaired | `probe` first runs `capped`, then starts the measurement under the run's own bounds: uid 990, no network, read-only, the systemd slice, `--memory 2560m` and `nice -n 19`. |
| FE4R-4 Minor | AGREE, repaired | The runbook separates the two cases. Exit 3 is the diagnosed CPU crash: send the printed CPU line, and the pin is the owner's D-20 decision. Any other error means stop and send the whole output and exit status, and nothing is decided until it is diagnosed. |

**Noted by the reviewer, unchanged:**

- **The test environment.** The engine-test step does not set the OpenBLAS variables itself. The engine scripts set them before NumPy loads, and the tests that need method V verify the runtime themselves. The suite passed on EPYC 7763 under Python 3.14.
- **Reboots other than unattended upgrades.** These are not covered by the runbook step. The owner's server has no other automatic reboot that the AI knows of. This is to be confirmed at the re-pilot walkthrough.

No calibration was run.

## Re-review 2 (`SOL6_FE4_REREVIEW2_BC43CC8.md`: FIX; FE4R-2/3 resolved, FE4R-4 partly)

| ID | Decision | Repair |
|---|---|---|
| FE4R2-1 Moderate (and FE4R-1) | AGREE, repaired | Exit 3 is reserved for a segmentation fault of the measurement. Any other failure that happens to exit with 3 is remapped to 1, and its original status is printed. |
| FE4R2-2 Moderate (and FE4R-4) | AGREE, repaired | A segfault is reported as "the measurement crashed (segmentation fault), not yet diagnosed". The runbook calls the AMD EPYC Zen 4/5 kernel crash the likely cause, not a proven one. It asks for the whole output, and says the D-20 pin becomes the owner's decision only once the cause is confirmed. The CI messages say the same and point to the printed CPU line. |
