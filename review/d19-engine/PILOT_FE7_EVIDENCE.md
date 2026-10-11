# D-19 re-pilot (FE-7): evidence from the owner's server

The owner ran the commands on his server and pasted the outputs into the Claude Code session. Claude Opus 5.5 (`claude-opus-5-5`) records them here verbatim, with any trimming stated.

**Kit:** engine commit `cbde711d69effa3891d1683f0750205337c25902` (`deploy/calibration/PILOT_FE7.md`).

## 2026-10-11: step A (install, build, probe)

- **Server:**
  - Ubuntu 26.04.1 LTS, kernel 7.0.0-38-generic, x86_64;
  - CPU `AMD EPYC-Rome Processor` (Zen 2);
  - Docker 29.1.3 (`docker.io` from Ubuntu, installed by `d19.sh install`).
- **Image:** `aqt-d19:cbde711d69effa3891d1683f0750205337c25902`, id `sha256:6e410191e7b73e692d43e8622cec021b6169b4ceca36d48963fffd3f3e44ef16`.
  - Its base is `python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170`.
  - It installed `numpy-2.5.3-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl` with hashes required.
- **`probe`:** `This CPU runs the pinned runtime.` The `capped` slice checks ran first and passed.

## Step B (automatic reboots)

`apt-config dump | grep Automatic-Reboot` printed `Unattended-Upgrade::Automatic-Reboot "false";`.

## Step C (data, cell list, run definition)

- **First attempt failed cleanly.** `/var/lib/aqt/data/raw` did not exist: the forward-paper server had never downloaded the exploration archives, and the sheet wrongly assumed it had.
  - `copy-raw` printed `FAIL: copy failed` and left nothing behind.
  - `manifests` printed `KlineError: no BTCUSDT bars inside the exploration window`.
  - `record` stopped with `FileNotFoundError` before writing anything.
- **The download.** The owner then ran the server runbook's download (`deploy/RUNBOOK.md` step 4). It reported 106 archives `AVAILABLE` (BTCUSDT and ETHUSDT, 2017-08 to 2021-12) and `unavailable: 0`.
- **Retry.** Output verbatim:

```
Copied 106 archives
BTCUSDT: 38166 bars, 31 gaps (186 h), 0 missing archives, manifest 5f92ec5041c9560d5f31bdb99b9686d7522697e65a8e61d514a0b0dda6d0b65b
926887367368c523e05d61c13b7eed5063797420b4f7d7cb84ffc0b42c4f653a
```

The last line is the run-definition hash.

**Kit correction:** the sheet now has the download step before `copy-raw`.

## Session note: dropped connections

The owner's SSH connection dropped ("client_loop: send disconnect: Connection reset") during commands that print nothing for minutes. The `timing` call was cut off this way. The owner then reconnected with `ServerAliveInterval=30` and worked inside `tmux`. No run state was affected.

## Step D (timing, I1-8): seconds per development replication, 20 reps per cell

The first line (K = 20) was cut off at the top of the paste. The other two, verbatim from the visible part:

```
...ostics": 0.0010419080790597945, "dsr_largest": 0.998796815314563, "dsr_median": 1.0481745122931898, "u_g": 1.8370973435521591}, "total": 3.888638045499101}
{"cell": "pilot-timing-k2", "K": 2, "T": 1247, "reps": 20, "seconds_per_rep": {"generate": 0.0040810030070133506, "diagnostics": 0.0008503639954142272, "dsr_largest": 1.0417208006430883, "dsr_median": 1.083452005503932, "u_g": 1.861180728394538}, "total": 3.991284901543986}
```

The first of these two lines is the K = 5 cell; its start was cut off.

## Step E: threshold run and the failing-chain check (FR2-2), verbatim

```
4f634461417e236ad39100a0b165c7f68d05f70cc67320f62c5b6670548a03a4
Started. Progress: sudo sh d19.sh status
workers 143028 and 143031; killing 143028
PASS: the run stopped (exit 1) and no worker outlived it
run stopped: BrokenProcessPool: A process in the process pool was terminated abruptly while the future was running or pending.
Exited (1) About a minute ago
started 2026-10-11T13:40:31.514643626Z finished 2026-10-11T13:43:54.876846368Z exit 1
slice memory peak: 254787584 bytes
4 threshold/pilot-q1-clusters-k20
4 threshold/pilot-q1-clusters-k5
4 threshold/pilot-q1-ind-k1
2 threshold/pilot-q2m-k2
4 threshold/pilot-q2m-k20
4 threshold/pilot-q2-t5-rho-k20
4 threshold/pilot-q3-factor-k20
4 threshold/pilot-q4-k5
4 threshold/pilot-q5-trend-k20
4 threshold/pilot-q5-vol-k20
```

**FR2-2 on a Linux host: PASS.** Killing one worker stopped the whole run with exit code 1 and a clear `BrokenProcessPool` reason, and no worker outlived it. Ten of the 13 cells had finished their 2,000 threshold draws within 3 min 23 s, before the kill.

## Step E (continued): resumed threshold run, verbatim

```
Exited (0) 59 seconds ago
started 2026-10-11T14:37:23.399563915Z finished 2026-10-11T14:40:49.50115742Z exit 0
slice memory peak: 273391616 bytes
4 threshold/pilot-q1-clusters-k20
4 threshold/pilot-q1-clusters-k5
4 threshold/pilot-q1-ind-k1
4 threshold/pilot-q2m-k2
4 threshold/pilot-q2m-k20
4 threshold/pilot-q2m-k5
4 threshold/pilot-q2-t5-rho-k20
4 threshold/pilot-q3-factor-k20
4 threshold/pilot-q4-k5
4 threshold/pilot-q5-trend-k20
4 threshold/pilot-q5-vol-k20
4 threshold/pilot-qj-k2
4 threshold/pilot-qj-k20
threshold/pilot-q1-clusters-k20: 3 3 3
threshold/pilot-q1-clusters-k5: 2 2 2
threshold/pilot-q1-ind-k1: 2 2 2
threshold/pilot-q2-t5-rho-k20: 4 4 4
threshold/pilot-q2m-k2: 2 3262(spans a restart) 2
threshold/pilot-q2m-k20: 4 4 4
threshold/pilot-q2m-k5: 2 2 2
threshold/pilot-q3-factor-k20: 5 4 5
threshold/pilot-q4-k5: 5 5 5
threshold/pilot-q5-trend-k20: 24 24 25
threshold/pilot-q5-vol-k20: 19 18 19
threshold/pilot-qj-k2: 7 7 7
threshold/pilot-qj-k20: 40 40 40
```

Each `times` value is one worker's seconds per 500 threshold draws (FE7-3). The marked 3262 s is the gap between the failcheck kill (13:43:54) and the resume (14:37:23), so it is excluded as designed.

## Step F: resume identity (§13 item 6 "Before the full run"), verbatim

The `clean-check` output: the 13 chain heads of the clean run (`threshold/<cell>: <hash>`), then:

```
pilot-q1-clusters-k20: 4 chunks identical
pilot-q1-clusters-k5: 4 chunks identical
pilot-q1-ind-k1: 4 chunks identical
pilot-q2-t5-rho-k20: 4 chunks identical
pilot-q2m-k2: 4 chunks identical
pilot-q2m-k20: 4 chunks identical
pilot-q2m-k5: 4 chunks identical
pilot-q3-factor-k20: 4 chunks identical
pilot-q4-k5: 4 chunks identical
pilot-q5-trend-k20: 4 chunks identical
pilot-q5-vol-k20: 4 chunks identical
pilot-qj-k2: 4 chunks identical
pilot-qj-k20: 4 chunks identical
PASS: the resumed threshold run equals the clean run
```

**Result:** an interrupted and resumed run gives byte-identical chunks to a clean run, for every cell, on the owner's server. That includes the cell (`pilot-q2m-k2`) whose chain was cut by the killed worker.

## Step G: development run, start (2026-10-11)

The development run was started at `15:40:41Z`. After 12 minutes, `status` showed `Up 12 minutes`, a slice memory peak of `434622464 bytes` (about 435 MB), and no development chunk yet. The first chunk of 500 replications takes about 30–35 minutes. `docker logs` was empty, which is normal: the driver prints only at the end.

**Launcher defect found:**
- **What happened.** `memwatch` printed `FAIL: no sample showed 2 workers running` while both workers were running.
- **Cause.** It called `docker top aqt-d19 -eo args`. `docker top` refuses `ps` output without a PID column, and its error went to `/dev/null`, so every sample counted 0 workers. `failcheck` asks for `-eo pid,args` and worked.
- **Fixed** in the repository: `memwatch` now asks for `-eo pid,args`, and a test requires a PID column in every `docker top` call. That test fails on the old line.
- **On the server**, the evidence is taken by hand instead: the worker count from `docker top aqt-d19 -eo pid,args | grep -c spawn_main` and the container's `memory.peak`. The server keeps the accepted kit commit. The slice peak in `status` covers the whole night.

**Also fixed:** `times dev`, run before any development chunk existed, printed a confusing `find` error. It now prints `no dev chunks yet`.
