<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12a71-3157-75f1-a0db-88bb6f45829e. Tokens used: 29,283. Made from a packet built from commit e4ad54c (git show/diff only): the prompt below, SOL6_FE4_REVIEW_1C44DB8.md, ADJUDICATION_FE4_1C44DB8.md, git diff 1c44db8..e4ad54c -- deploy tests .github, d19.sh and RUNBOOK.md at e4ad54c, and the WORKERS lines of scripts/d19_run.py. -->

> # Focused re-review: D-19 FE-4 repairs (1c44db8..e4ad54c)
> 
> You are an independent adversarial reviewer working read-only. You are not an authority, and every finding will be adjudicated with evidence. Review ONLY the repairs of your findings FE4-1..FE4-8 and the later CPU-probe change, using the attached:
> - your previous review;
> - the adjudication, including its section on the CI findings;
> - the diff `1c44db8..e4ad54c`;
> - the files at e4ad54c;
> - the CI evidence below.
> 
> Base the review on these attachments, and say so where you could not verify something.
> 
> **CI evidence (draft PR #45, GitHub-hosted Ubuntu 24.04).**
> - **`calibration-launcher`.** It passed on AMD EPYC 7763 (several runs) and on Intel Xeon 8573C. It ran install, build, probe, a pilot record, threshold run, stop, resume, waited for exit 0 and checked status counts, then dev and choose.
> - **`calibration-tests`, Python 3.14 with numpy 2.5.3.** It passed on EPYC 7763: 224 calibration tests plus the deploy tests.
> - **Segfaults.** Both jobs segfaulted on AMD EPYC 9V45 and 9V74 until the probe step was added. The probe then skipped them with a warning on a 9V45.
> - **The `checks` job (Python 3.12).** It passes without the calibration tests.
> 
> **Questions.**
> 1. **Prior findings.** Is each of FE4-1, FE4-2, FE4-4, FE4-5, FE4-6, FE4-7 and FE4-8 resolved? Is the disagreement on FE4-3 justified (`WORKERS = 2` is a fixed constant in `scripts/d19_run.py`)?
> 2. **The `capped` preflight.** Is the systemd-driver check, the `MemoryMax` check and the `--cgroupns host` probe correct? Are they sufficient?
> 3. **The `probe` and the CI skip logic.**
>    - Can a real engine regression hide behind the skip? The skip is on exit 139 only, and the launcher-job skip also requires `avx512_bf16`.
>    - Is skipping acceptable when CI may then test nothing on a given run?
>    - Does the runbook tell the owner correctly what to do if the probe refuses?
> 4. **Moving the engine tests.** Is moving them from the Python 3.12 job to a Python 3.14 job justified? Is the general job's `--ignore-glob` too broad?
> 5. **New defects.** Did the repairs introduce any new defect?
> 
> **Output.**
> - Put your model metadata at the top.
> - Give a verdict for re-pilot use: ACCEPT or FIX.
> - For each prior finding, say resolved or unresolved.
> - Number new findings FE4R-n. Give each one a severity, a file:line, a failure scenario and the minimal fix.
> - Mark any finding that needs an owner decision.

## Review (verbatim)

**Model metadata:** Codex, GPT-6 family. The exact checkpoint and reasoning effort are not exposed in this session. No other model was invoked.

**Re-pilot verdict: FIX.** The supplied CI evidence supports the repaired launcher on EPYC 7763 and Xeon 8573C. The new skip logic can still produce a passing calibration workflow without running either calibration suite or launcher exercise. This is a read-only review of the supplied attachments and CI account; I could not inspect the owner’s server, independently run Docker, or verify test setup omitted from the packet.

### Prior findings

| Finding | Status | Basis |
|---|---|---|
| FE4-1 | **Resolved** | The inspected image ID is both the `docker run` image and `AQT_IMAGE_DIGEST`. |
| FE4-2 | **Resolved at code and CI level** | The driver, configured `MemoryMax`, and slice placement are checked before launcher starts. Enforcement on the owner’s server remains unverified. |
| FE4-3 | **Disagreement justified** | `WORKERS = 2` is fixed, and the shown executor uses it. The launcher needs no worker option. |
| FE4-4 | **Resolved** | `umask 022` precedes the clone; the supplied CI run successfully recorded from uid 990. |
| FE4-5 | **Resolved** | `status` prints container state and chunk counts, without logs or chunk content. |
| FE4-6 | **Resolved** | The runbook executes the script from a fresh checkout at the chosen commit. Choosing and trusting that commit remains the owner’s decision. |
| FE4-7 | **Resolved for unattended upgrades** | The runbook sets, checks, and later removes the reboot override. Other server reboot mechanisms were not verified. |
| FE4-8 | **Resolved for the launcher smoke test** | Supplied CI runs exercised record, run, stop, resume, status, dev, and choose. They do not prove that `stop` interrupted an unfinished chunk on every run; the adjudication identifies a separate resume unit test. |

### Preflight, probe, and test placement

The `capped` checks are coherent for Docker with the systemd cgroup driver. The exact `MemoryMax` value is correct for 2560 MiB, and `--cgroupns host` makes the probe’s `/proc/self/cgroup` path useful for checking slice placement. The separate `--memory 2560m` remains an additional cap. These checks establish the intended configuration and placement; the attachments do not show the owner server’s live kernel limit.

Moving the engine suite to Python 3.14 with NumPy 2.5.3 is justified by the supplied runtime and CI evidence. The general job’s `--ignore-glob` is broader than an explicit file list, but the shown calibration job selects matching top-level `test_calibration_*.py` files. I cannot establish a *current* omitted test from the attachments. Its consequence becomes serious when that job skips. Also, the calibration **test step** does not itself set `OPENBLAS_CORETYPE=Haswell` and `OPENBLAS_NUM_THREADS=1`; the probe does. I could not verify whether individual tests set those variables.

### New findings

1. **FE4R-1 — Major — `.github/workflows/ci.yml:136-139`.** On a runner advertising `avx512_bf16`, **any** nonzero launcher probe result is treated as a skip. `d19.sh probe` converts exit 139 to exit 1, so this CI branch cannot distinguish the known segfault from a Docker error or engine regression. **Minimal fix:** preserve a distinct crash exit code from `probe`, and skip only that code with the CPU condition. **Owner decision:** No.

2. **FE4R-2 — Major — `.github/workflows/ci.yml:52-55,138-144`.** A segfault in the gating/probe path can be classified as CPU incompatibility; on an affected runner both calibration jobs can then pass while executing no calibration tests or launcher flow. Exit 139 alone does not identify the cause. **Minimal fix:** require a full calibration run on at least one known compatible runner before treating CI as passing; report incompatible runners as inconclusive. **Owner decision:** **Yes**, if accepting a green CI run with no calibration validation is proposed.

3. **FE4R-3 — Moderate — `deploy/calibration/d19.sh:84-91`.** `probe` runs the engine’s gating measurement without `nice 19`, the systemd slice, or a memory limit, although the launcher and runbook say every engine process has those bounds. **Minimal fix:** run the CPU probe under the same priority and cgroup limits, using `capped` first. **Owner decision:** No.

4. **FE4R-4 — Minor — `deploy/calibration/RUNBOOK.md:50`.** For a non-segfault probe failure, the script exits without printing a CPU model, while the runbook tells the owner to send the model “it prints” and points toward a binding decision. **Minimal fix:** tell the owner to stop and report the full error, exit status, and CPU model separately; reserve the pin decision for a diagnosed CPU crash. **Owner decision:** No.
