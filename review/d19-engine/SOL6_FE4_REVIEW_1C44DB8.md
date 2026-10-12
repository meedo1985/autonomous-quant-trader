<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12a06-5b93-7d60-b9bb-d45f82fbffec. Tokens used: 57,081. Made from a packet built from commit 1c44db8 (git show only): the prompt below, prereg §13 rev 7g item 6 (fff4e5f lines 520-560), the FE-4 origin row, the new deploy files, test and CI diff at 1c44db8 (requirements.lock shortened to 12 lines), the rundef/dsr gate code, the recorder's git use, and the forward-paper service and install.sh. -->

> # Review: D-19 FE-4 at 1c44db8 (calibration container image and launcher)
> 
> You are an independent adversarial reviewer working read-only. You are not an authority, and every finding will be adjudicated with evidence. Base the review on the attachments, and say so wherever you could not verify something. Docker was not available to the drafter. The image has not been built yet; a new CI job builds it.
> 
> Attached:
> - the preregistration §13 rev 7g item 6 (running on the server);
> - the earlier FE-4 requirement;
> - the new files in full: `Dockerfile`, `requirements.lock` (hash lines shortened), `aqt-d19.slice`, `d19.sh`, `RUNBOOK.md`, `tests/unit/test_d19_deploy.py`, and the CI job;
> - the relevant engine code:
>   - `rundef.start_gate`, `bytecode_problem` and `loaded_outside`;
>   - `dsr.runtime_identity` and `V_ENVIRONMENT`;
>   - the recorder's git use;
> - the existing forward-paper service and `install.sh`, for contrast.
> 
> Questions:
> 1. **Item 6.** Does the setup implement item 6? Check each of these:
>    - one image pinned by digest, holding the whole userland;
>    - nothing updated during a run;
>    - `nice 19`;
>    - systemd `MemoryMax` 2.5 GB;
>    - 2 workers;
>    - the owner starts and stops the run;
>    - the AI never logs in;
>    - the digest comes from host `docker inspect` and is never typed (FE-4).
> 2. **Gating.** Is the "image digest" the right one to gate on? Is `.Id` (the local config digest) or a RepoDigest the correct choice? Can anything vary inside a run while the gating identity stays the same?
> 3. **Start gate inside the container.** Will `start_gate` pass inside the container? Consider the read-only `/app`, the `/tmp` tmpfs and `pycache_prefix`, uid 990 with git `safe.directory`, `HOME`, `sys.prefix` versus `site-packages`, and the OpenBLAS environment. Will the recorder's git commands work? Find any step in the runbook that would fail.
> 4. **Security and isolation.** Consider:
>    - root on the host;
>    - the engine's network access, its user and its write paths;
>    - separation from forward paper (its files, checkout and service);
>    - the `curl | sh`-style install;
>    - supply chain: the base image digest, the hash-locked wheel, and the unpinned apt `git`.
> 5. **Operations.** Do stop and resume work, given `--init`, SIGTERM and the chunk resume? Does `status` respect P18-6 (counts only)? Is the memory cap actually enforced with `--cgroup-parent` plus `--memory`?
> 6. **Tests and CI.** Are the tests and the CI job adequate, or are any vacuous?
> 
> Output:
> - Put your model metadata at the top.
> - Give a verdict for re-pilot use: ACCEPT or FIX.
> - Number findings FE4-n. Give each one a severity, a file:line, a failure scenario and the minimal fix.
> - Mark any finding that needs an owner decision.

## Review (verbatim)

**Model metadata:** Codex, GPT-6 family per this session’s runtime instructions. The exact checkpoint and reasoning effort are not exposed to me; no Claude model was invoked.

**Verdict for re-pilot use: FIX.** This is a read-only review of the attachments. I could not build the image, run the tests, inspect the server, verify the shortened lockfile hashes, or inspect the omitted worker and chunk-resume code.

Item 6 is **partly implemented**. The Dockerfile pins the base image, and the launcher obtains the built image’s `.Id` from host `docker image inspect` without asking the owner to type it. The image contains the specified userland and runs read-only; the engine checkout is a separate read-only mount. `nice 19`, uid 990, and owner-operated commands are explicit. AI non-login is a procedure stated in the runbook, not something these files can prove. The launcher does not establish two workers, and the server’s **systemd** `MemoryMax` is not yet verified. Automatic reboots are checked, but not switched off.

For a **locally built** image, `.Id` is a sound gating digest: Docker says the image ID covers its configuration and layers. A RepoDigest identifies a registry manifest and need not exist for this local build. The launcher must also *run that inspected ID*. [Docker image IDs](https://docs.docker.com/reference/cli/docker/image/pull/), [registry manifests](https://docs.docker.com/reference/cli/docker/manifest/).

### Findings

1. **FE4-1 — MAJOR — `deploy/calibration/d19.sh:27,39`.** **Scenario:** `engine()` inspects the tag, then runs the tag. If it is rebuilt or retagged between those operations, `AQT_IMAGE_DIGEST` names one image while Docker starts another. This defeats the claimed digest pin for that start. **Minimal fix:** pass `"$digest"` as the `docker run` image argument, and verify the created container’s image ID in an integration test. **Owner decision:** No.

2. **FE4-2 — MAJOR — `deploy/calibration/d19.sh:35-36`; `deploy/calibration/aqt-d19.slice:6`.** **Scenario:** The unit is installed and syntax-checked, but the procedure never checks Docker’s cgroup driver, the container’s actual slice membership, or the active slice’s `MemoryMax`. With a different cgroup layout, `--memory 2560m` can still cap container RAM, while the preregistered **systemd `MemoryMax`** is absent. **Minimal fix:** make launch fail unless Docker uses the intended systemd slice, then verify the live container’s cgroup and `MemoryMax=2560M` on the server. Docker documents driver-dependent `--cgroup-parent` behavior; `--memory` is a separate container limit. [Docker cgroup parent](https://docs.docker.com/reference/cli/dockerd/), [memory limits](https://docs.docker.com/engine/containers/resource_constraints). **Owner decision:** No.

3. **FE4-3 — MAJOR, unverified requirement — `deploy/calibration/d19.sh:72-73`.** **Scenario:** `run` supplies no worker count. If `d19_run.py` defaults to anything other than two, the re-pilot violates item 6. That CLI/default was not attached, so I cannot say it actually does. **Minimal fix:** pass an explicit two-worker option supported by the engine and assert the live worker count in the launch smoke test. **Owner decision:** No.

4. **FE4-4 — MAJOR — `deploy/calibration/d19.sh:49-51`.** **Scenario:** Under a restrictive root umask such as `077`, `git clone` can create `/opt/aqt-d19/app` without traverse permission for uid 990. `chmod -R go-w` does not add read or execute permission. The runbook’s `record` step then cannot read the checkout or run Git. **Minimal fix:** set `umask 022` before cloning, as the forward-paper installer does, and verify uid 990 can read `/app` and run the recorder’s Git commands. **Owner decision:** No.

5. **FE4-5 — MODERATE — `deploy/calibration/d19.sh:78`.** **Scenario:** `status` prints the last five arbitrary log lines. Thus its output is not guaranteed to be counts only under P18-6; a future error or progress log could expose more. **Minimal fix:** remove `docker logs` from `status`; retain container state and per-chain counts. **Owner decision:** No.

6. **FE4-6 — MODERATE — `deploy/calibration/RUNBOOK.md:24-25`.** **Scenario:** The owner executes a separately downloaded script as root before verifying its bytes against the chosen engine commit. A compromised download or mistaken ref can therefore run host-root code. The base digest and wheel hashes constrain the image build, but do not protect this bootstrap step; the image’s apt-installed `git` is also unpinned, so rebuilds can differ, though a changed final image ID would be detected by the gate. **Minimal fix:** verify the downloaded script against `deploy/calibration/d19.sh` in a locally verified commit before `sudo sh`, and record or pin the apt package source/version if reproducible rebuilding is required. **Owner decision:** **Yes**—the owner must accept or change this host-root bootstrap trust procedure.

7. **FE4-7 — MODERATE — `deploy/calibration/RUNBOOK.md:29-33`.** **Scenario:** `grep` may show automatic reboot enabled; it does not switch it off as item 6 requires. **Minimal fix:** give the owner an explicit disable-and-verify step for the server’s reboot mechanism before starting, and a restore step afterward. **Owner decision:** **Yes**—this changes server update policy for the run.

8. **FE4-8 — MAJOR — `.github/workflows/ci.yml:83`; `tests/unit/test_d19_deploy.py:46`.** **Scenario:** CI builds the image, but its smoke command bypasses `d19.sh`, supplies no digest, uses `/tmp` instead of the `/work` bind mount, and only *prints* identity and canaries. The unit test checks launcher text. Both can pass while `record`, `start_gate`, the actual launcher, or stop/resume fail. **Minimal fix:** in CI, invoke the real launcher with a temporary writable work directory and a small fixture definition, assert a successful `record`/`check`, then exercise start, stop, and resume. Keep a server check for live slice enforcement. **Owner decision:** No.

The supplied `start_gate` logic has no evident inherent conflict with read-only `/app`: its code reads are allowed, `/tmp` supplies a writable empty `pycache_prefix`, and image `site-packages` lie under `sys.prefix`. The system Git `safe.directory /app` and `HOME=/tmp` should allow the recorder’s read-only Git commands, subject to FE4-4. The script preamble sets both required OpenBLAS variables before engine imports. Those are code-level conclusions, **not a successful container start**.

`--init` should forward SIGTERM to the Python child, but Tini normally signals only its immediate child; the attached material does not establish worker shutdown or corrupt-chunk cleanup. The claimed atomic chunk resume needs the FE4-8 exercise before relying on it. [Tini signal behavior](https://github.com/krallin/tini). The running image filesystem stays fixed, while mounted `/work` data, host kernel or microcode, and a host tag can change without changing the recorded gate; host provenance is deliberately disclosed rather than compared.
