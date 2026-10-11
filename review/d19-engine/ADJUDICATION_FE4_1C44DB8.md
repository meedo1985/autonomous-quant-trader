# Adjudication of the GPT-6 Sol review of D-19 FE-4 at 1c44db8

**Review:** `review/d19-engine/SOL6_FE4_REVIEW_1C44DB8.md` (FIX for
re-pilot use; FE4-1..FE4-8).

**Adjudicated and repaired by:** Claude Opus 5.5 (`claude-opus-5-5`) on
2026-10-11. Not yet re-reviewed.

The reviewer confirmed that the image's `.Id` is the right digest to gate on for a locally built image. A RepoDigest need not exist for a local build.

| ID | Decision | Repair and evidence |
|---|---|---|
| FE4-1 Major | AGREE, repaired | The launcher calls `docker image inspect` once. It starts the container by that id, `"$id"`, and passes the same id as `AQT_IMAGE_DIGEST`. A retag between the inspection and the start can no longer change which image runs. The test requires exactly one `id=` taken from the inspection, the `"$id"` image argument, and a single `AQT_IMAGE_DIGEST=`. The CI job runs it. |
| FE4-2 Major | AGREE, repaired | `capped` runs before every engine start and refuses unless three things hold. Docker's cgroup driver must be `systemd`. `systemctl show aqt-d19.slice -p MemoryMax` must report 2684354560 (2560M). A probe container started with `--cgroup-parent aqt-d19.slice --cgroupns host` must list `/aqt-d19.slice/` in its `/proc/self/cgroup`; a private cgroup namespace would show only `0::/`. `--memory 2560m` stays as a second, container-level cap. **Limit:** the live check on the owner's server happens when the owner first starts the re-pilot. CI exercises it on GitHub's Ubuntu 24.04 runner. |
| FE4-3 Major | DISAGREE, with evidence | The worker count is not a launcher input. `scripts/d19_run.py` fixes `WORKERS = 2` ("§13 rev 7g item 6: two workers, not a run-time choice", DR5-1), and no option can change it. The launcher's header now says so. The reviewer did not have the driver, as it noted. |
| FE4-4 Major | AGREE, repaired | The launcher sets `umask 022` before anything it creates, as `deploy/install.sh` does. The CI job installs as root and then runs `record` as uid 990 inside the container. That run reads the checkout and runs the recorder's git commands. |
| FE4-5 Moderate | AGREE, repaired | `status` prints only the container state and the chunk count per chain. The runbook gives `docker logs` as a separate owner command, for threshold and development runs only, to see why a run stopped. The held-out run, not yet built, will have its own rule. The test refuses `docker logs` or `cat` inside `status`. |
| FE4-6 Moderate (owner) | AGREE, repaired by a stricter procedure | The runbook no longer downloads a loose script. The owner clones the repository, checks out the chosen commit and confirms `rev-parse HEAD`, then runs `d19.sh` from that checkout. A commit id is a hash over every file, so the root-run script is exactly that commit's. This is strictly stronger than the forward-paper runbook's download, which the owner already accepted. It is reported to the owner, not decided for him. He can keep or change it at the re-pilot walkthrough. **Left unrepaired:** the image's apt `git` package is not version-pinned. A rebuild can therefore differ, but it gets a different image id, and the start gate refuses it against a recorded definition. A rebuild that is reproducible byte for byte is not required by §13 item 6. |
| FE4-7 Moderate (owner) | AGREE, repaired | §13 item 6, which the owner accepted, already says "Automatic reboots are switched off for the run", so no new decision is needed. The runbook now has an explicit step: write `Unattended-Upgrade::Automatic-Reboot "false"` to `/etc/apt/apt.conf.d/99aqt-d19-no-reboot` and verify it with `apt-config dump`. Another step removes the file after the calibration. |
| FE4-8 Major | AGREE, repaired | The CI image job is replaced by `calibration-launcher`. It runs the real launcher on a fresh Ubuntu 24.04 machine:<br>- `install` from a bundle of this commit and the preregistration branch, then `build`;<br>- `record` of a two-cell pilot definition;<br>- `run threshold`, then `stop`, then `run threshold` again, waiting for exit code 0;<br>- `status`, which must show one chunk per chain;<br>- `run dev`, then `choose`, which must write `choices.json`.<br>Every start passes `capped` and the engine's own start gate. **Limit:** the test of a byte-identical resume stays in the unit suite (`test_the_driver_runs_one_bound_chain_per_cell_and_resumes`). CI shows that a stopped and resumed run completes under the launcher. |

The reviewer also noted that `--init` forwards SIGTERM only to its direct
child. The driver terminates its own workers on the first failure (FA-5), and
a resume deletes an incomplete chunk unread. The CI stop-and-resume step
exercises that path.

No calibration was run.
