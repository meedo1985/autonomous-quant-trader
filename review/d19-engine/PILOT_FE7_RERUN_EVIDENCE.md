# D-19 re-pilot, second run on the rebuilt image: evidence from the owner's server

The owner ran the commands on his server and pasted the outputs into the Claude Code session. Claude Opus 5.5 (`claude-opus-5-5`) records them here verbatim, with any trimming stated.

**Kit:** `deploy/calibration/PILOT_FE7_RERUN.md` (PR #59), engine commit `e39b23dc23f0acd4b113479f3a05d66511d9f0ad` (main after PR #58, scikit-learn and LightGBM in the image). First run: `PILOT_FE7_EVIDENCE.md`.

## 2026-10-16: step 0 (first run's files set aside)

```
root@aqt-server:~# sudo docker ps -a --filter name=^aqt-d19$ --format '{{.Status}}'
Exited (0) 4 days ago
root@aqt-server:~# old=$(git -C /opt/aqt-d19/app rev-parse --short HEAD); echo "$old"
cbde711
root@aqt-server:~# sudo mv /opt/aqt-d19/app "/opt/aqt-d19/app-$old"
root@aqt-server:~# sudo install -d -o 990 -g 990 -m 700 /var/lib/aqt-d19/repilot1
root@aqt-server:/var/lib/aqt-d19# ... ; ls /var/lib/aqt-d19
manifests  raw  repilot1
```

## Step A (install, build, probe)

The paste began inside the build's package installation; the `rev-parse HEAD` line was not in it. The image tag carries the engine commit. Last lines verbatim:

```
Successfully installed cloudpickle-3.1.2 joblib-1.6.0 lightgbm-4.7.0 narwhals-2.27.1 numpy-2.5.3 scikit-learn-1.9.1 scipy-1.18.1 threadpoolctl-3.7.0
Successfully tagged aqt-d19:e39b23dc23f0acd4b113479f3a05d66511d9f0ad
Image aqt-d19:e39b23dc23f0acd4b113479f3a05d66511d9f0ad id sha256:54bfcf5394cbd7a40fd3351d2fda6ed61fd7564435fe2f14bcb182f996f9790c
Next: sudo sh d19.sh probe
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh probe
This CPU runs the pinned runtime.
```

The build also installed `libgomp1` (14.2.0-19), as the Dockerfile requires for LightGBM.

## Step B (automatic reboots)

The owner's first paste carried the command only. He then re-ran it:

```
Unattended-Upgrade::Automatic-Reboot "false";
```

## Step C (cell list, run definition; data reused)

`record` printed the run-definition hash:

```
6ec065f6d4c2caed6c60e68457eb2ed4626c6a9ee88a23f33f8ed44c6c5f5443
```

It differs from the first run's `926887...` as expected: the engine commit is part of the definition.

## Step D (timing, I1-8): seconds per development replication, 20 reps per cell

Verbatim (the first paste lacked the K = 2 line; the owner sent all three in a second paste):

```
{"cell": "pilot-timing-k20", "K": 20, "T": 1247, "reps": 20, "seconds_per_rep": {"generate": 0.007065982697531581, "diagnostics": 0.0023900182684883477, "dsr_largest": 1.1096730421821122, "dsr_median": 1.2327919989824294, "u_g": 1.880751720617991}, "total": 4.232672762748552}
{"cell": "pilot-timing-k5", "K": 5, "T": 1247, "reps": 20, "seconds_per_rep": {"generate": 0.003604390745749697, "diagnostics": 0.0010578308894764632, "dsr_largest": 1.0093869819014798, "dsr_median": 1.0794689675152767, "u_g": 1.8452382518909871}, "total": 3.9387564229429697}
{"cell": "pilot-timing-k2", "K": 2, "T": 1247, "reps": 20, "seconds_per_rep": {"generate": 0.0038260103843640535, "diagnostics": 0.0008465803111903369, "dsr_largest": 1.0788430298503955, "dsr_median": 1.0846072799060493, "u_g": 1.8727402676362543}, "total": 4.040863168088253}
```

Against the first run: K = 5 total 3.939 s vs 3.889 s (+1.3%), K = 2 4.041 s vs 3.991 s (+1.2%). The first run's K = 20 line was cut off, so K = 20 has no comparison.

## Step E: threshold run and the failing-chain check (FR2-2), verbatim

```
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh run threshold
0b658c45798198b8504f72329ef0936f72744018fe02cf157783be55e4a1757e
Started. Progress: sudo sh d19.sh status
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sleep 120
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh failcheck
workers 287764 and 287767; killing 287764
PASS: the run stopped (exit 1) and no worker outlived it
run stopped: BrokenProcessPool: A process in the process pool was terminated abruptly while the future was running or pending.
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh status
Exited (1) 15 seconds ago
started 2026-10-16T18:07:06.43610259Z finished 2026-10-16T18:10:01.978183533Z exit 1
slice memory peak: 466993152 bytes
4 threshold/pilot-q1-clusters-k20
4 threshold/pilot-q1-ind-k1
4 threshold/pilot-q2m-k20
4 threshold/pilot-q2-t5-rho-k20
4 threshold/pilot-q3-factor-k20
4 threshold/pilot-q4-k5
3 threshold/pilot-q5-trend-k20
4 threshold/pilot-q5-vol-k20
```

FR2-2 failing-chain check: **PASS**. The owner then resumed with `sudo sh d19.sh run threshold`.

Note on memory: `status` reads the slice's `MemoryPeak` (`d19.sh` line 146), which counts from when the systemd slice started, not from this run. 466,993,152 bytes after three minutes matches the first run's overall peak, so it is most likely carried over from that run (the server has not been rebooted). This run's own peak comes from `memwatch` in step G, which reads the run container's own `memory.peak` (`d19.sh` line 202).

## Step E (continued): threshold run finished, verbatim

```
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh status
Exited (0) About an hour ago
started 2026-10-16T18:10:57.750675118Z finished 2026-10-16T18:14:27.920942886Z exit 0
slice memory peak: 466993152 bytes
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
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh times threshold
threshold/pilot-q1-clusters-k20: 3 3 3
threshold/pilot-q1-clusters-k5: 2 2 2
threshold/pilot-q1-ind-k1: 2 2 2
threshold/pilot-q2-t5-rho-k20: 4 4 4
threshold/pilot-q2m-k2: 2 2 2
threshold/pilot-q2m-k20: 3 4 4
threshold/pilot-q2m-k5: 2 2 2
threshold/pilot-q3-factor-k20: 5 5 5
threshold/pilot-q4-k5: 6 6 5
threshold/pilot-q5-trend-k20: 24 25 141(spans a restart)
threshold/pilot-q5-vol-k20: 18 18 18
threshold/pilot-qj-k2: 7 7 7
threshold/pilot-qj-k20: 41 41 41
```

All 13 cells complete, exit 0. The resumed part ran 18:10:57-18:14:27Z. Against the first run (`PILOT_FE7_EVIDENCE.md` step E), every cell's seconds per 500 draws is within 1 s (for example qj-k20 41 vs 40, q4-k5 6/6/5 vs 5/5/5). The marked 141 s spans the failcheck stop and is excluded as designed.
