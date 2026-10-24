# Development run start (FULL_RUN.md step E)

Owner's server output, 2026-10-24 (pasted to the AI; the AI never logs in).

- `sudo sh d19.sh run dev`: container `45b795690734...`, "Started."; `status`: `started 2026-10-24T11:31:00.985975444Z`.
- First `memwatch` (about 11:41Z): "FAIL: no sample showed 2 workers running". Cause, from the pinned engine (`eeaa728:scripts/d19_run.py`, `main`): a development run first computes `dev_bounds` in the driver alone (it reads and verifies all 104 threshold chains and pools their thresholds), and only then starts the 2 workers. No dev chunk existed yet. Not a fault.
- About 12:29Z: `docker top ... | grep -c spawn_main` = 2; `memwatch`: "2 workers in 60 of 60 samples; this run's memory peak: 2125348864 bytes" (79% of the 2684354560 cap). Slice peak 2248105984 bytes (84%), reached before the workers started (setup), across all D-19 runs since the slice started.
- `status`: "Up 58 minutes"; first chunk `1 dev/gaussian.independent.k1.t1240`; 2 `dev/` lines.
- Step E finished rule (unchanged): `Exited (0)` and all 104 expected ids at `24 dev/`, no other `dev/` line.

## Forward paper restart on 2026-10-23 06:34:53Z: cause

- Not a crash and not a reboot (`uptime -s` 2026-10-05 06:30:22). The journal shows a clean systemd stop and start ("Deactivated successfully"), then "waiting until 2026-10-23 07:01 UTC", so no step was missed.
- `/var/log/apt/history.log`: `unattended-upgrade` upgraded `distro-info-data` (06:34:48) and `zlib1g` (06:34:51); systemd re-executed at 06:34:52 (`apt-daily-upgrade.service`) and restarted services using the upgraded library, aqt-paper among them.
- Risk for the multi-week development run: an unattended upgrade that restarts `docker` would stop the run's container (it has no restart policy). The run resumes from its last finished chunk (`run dev`), and the weekly check would see `Exited`. Docker was not restarted on 2026-10-23 (the threshold container had already exited on 10-22, and `docker0` only re-announced its link).

## Docker held for the run (2026-10-24, about 13:05Z)

- Installed: `containerd 2.2.2-0ubuntu1.1`, `docker.io 29.1.3-0ubuntu4.1`, `runc 1.4.0-0ubuntu1`.
- `sudo apt-mark hold docker.io containerd runc`: all three "set on hold"; `apt-mark showhold` lists them. Other unattended upgrades continue.
- Undo after step E finishes: `sudo apt-mark unhold docker.io containerd runc`.
