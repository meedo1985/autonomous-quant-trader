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

## Step F: resume identity, verbatim

```
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh clean-check
threshold/pilot-q1-ind-k1: 0fdcd239a02a67b0200ca40a4a69960cf7aa0218ec79c65aecf971d821172e2a
threshold/pilot-q1-clusters-k20: 272f529dc8efe9ed253444d06a3d957d67e08933afa2e9343a4c82f967058c21
threshold/pilot-q2-t5-rho-k20: 1f67ab8d90140b95a1b72975bc24beb29521be9fe41aa075808f43bc8fa431d4
threshold/pilot-q2m-k20: 7fbf241e3ffb4501649736800a07a365dd26e961f27d4d3c7865d3ea2ddaf835
threshold/pilot-q3-factor-k20: 3bdcbc1e006a2b9af809e3b6db25bbe10914749d0c313d8af9bcdf4c64f50eca
threshold/pilot-q4-k5: 2f7ce6d6fbe76a53aa19228cbf3484540dc9a914bd33bceb666255feeacb0c3c
threshold/pilot-q5-trend-k20: a93ab8b18a7decc11161e69be9585fd609828ac94ca7660e5b6a9e76c2b28283
threshold/pilot-q5-vol-k20: a5a7fbdca26d51f414287f4bac27b41e4866303effd4746d2b74222e6ad169e5
threshold/pilot-qj-k20: 0778f20711dddf2b8df088f0e81e81b45cf2acb41475a7a3bc94f1d863d2e20c
threshold/pilot-q1-clusters-k5: 5b44cc8cdc6a24e73c0f9684868e9be15e646e251776313b85c01fb90d8f8adb
threshold/pilot-q2m-k2: 5bf35ac62301d38e2a21777375b8d09045b1a26a553d3c0fbd8e05eef36df178
threshold/pilot-q2m-k5: a37f63275073822bf25629d7f43c8d84eca0fc3e36917b91260d22d79a8253dc
threshold/pilot-qj-k2: a6757f3c0681d8f698a2fd1d4bb4011e030553bcf512723b8ccd6a14d3d387e6
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

**Result:** PASS on the rebuilt image, as on the first run; that includes `pilot-q5-trend-k20`, whose chain was cut by the killed worker this time. The first run's clean-run chain heads were not recorded, so they cannot be compared with these.

## Step G: development run started, memory, forward paper (verbatim)

The owner's first `memwatch` ran before any development run had been started (his paste shows no `run dev` line before it), so it correctly printed `FAIL: no sample showed 2 workers running`; `status` then still showed the finished threshold run. He then started the run:

```
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh run dev
6c4cb48f8b23bbae0c00a56bcbf86ba7f7554e2560988eb57f5fe98d39060d9a
Started. Progress: sudo sh d19.sh status
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# sudo sh d19.sh memwatch
2 workers in 60 of 60 samples; this run's memory peak: 413155328 bytes
root@aqt-server:/opt/aqt-d19/app/deploy/calibration# systemctl status aqt-paper --no-pager | head -3
● aqt-paper.service - aqt forward paper trading
     Loaded: loaded (/etc/systemd/system/aqt-paper.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-10-05 06:30:33 UTC; 1 week 4 days ago
```

(The `systemctl` lines were sent before the run started; forward paper had been running unchanged since 2026-10-05.) Both workers ran in every sample. This run's own peak, 413,155,328 bytes (about 413 MB), read from the run container's `memory.peak`, is in line with the first run (slice peak about 435 MB twelve minutes into its development run, about 467 MB overall). The first run's `memwatch` itself was broken then and fixed later (`ec5349f`), so there is no exact first-run `memwatch` number to compare.

## Step H: results, verbatim (2026-10-17)

`status` (sent before step H):

```
Exited (0) 3 minutes ago
started 2026-10-16T20:27:30.33631332Z finished 2026-10-17T05:23:56.587136212Z exit 0
slice memory peak: 506847232 bytes
```

with all 13 `dev/...` lines at `2` and all 13 `threshold/...` lines at `4`. The development run took 8 h 56 min 26 s (first run: 9 h 01 min 33 s). The slice peak (about 507 MB) counts since the slice started, so it includes the threshold, clean-check and development runs; this run's own peak is `memwatch`'s 413 MB (step G).

`times dev` (one worker's seconds per 500 development replications):

```
dev/pilot-q1-clusters-k20: 2238
dev/pilot-q1-clusters-k5: 1983
dev/pilot-q1-ind-k1: 1450
dev/pilot-q2-t5-rho-k20: 2213
dev/pilot-q2m-k2: 1967
dev/pilot-q2m-k20: 2154
dev/pilot-q2m-k5: 1909
dev/pilot-q3-factor-k20: 2098
dev/pilot-q4-k5: 1818
dev/pilot-q5-trend-k20: 2067
dev/pilot-q5-vol-k20: 2052
dev/pilot-qj-k2: 3881
dev/pilot-qj-k20: 4254
```

`choose`:

```
z_crit None, family_block_rule largest
```

`nonfinite`: 0 non-finite in every cell; `all cells: 0 non-finite of 296000`.

`choices.json`: recorded whole, verbatim, in `pilot_fe7_rerun_choices.json` next to this file.

## Comparison with the first run (`PILOT_FE7_EVIDENCE.md`, `pilot_fe7_choices.json`)

- **Results bit-identical.** Every key both `choices.json` files share is equal, except `chain_heads`, `definition_sha256` and `measurement_only`: `cells` (every event count, status and margin), `coverage`, `dev_thresholds_sha256`, `family_block_rule`, `final_thresholds`, `joint`, `m`, `margin_ok`, `qualifies`, `smallest_margin`, `status`, `targets`, `worst_cell_rate_at_1.96`, `z_crit`. The run definition's hash differs because its engine commit differs, and the chain heads carry it. `dev_thresholds_sha256` equal means the threshold numbers themselves are the same bits. The rerun's file also has `alpha_s`, `cell_bounds` and `tests`, which the engine at the first run did not write yet.
- **Development events unchanged:** `pilot-q3-factor-k20` 1 DSR event (capped 1), `pilot-qj-k20/vol` 4 DSR events, `pilot-qj-k20` 4 joint U_proc events, every other count 0, no U_G events, no non-finite values.
- **Speed unchanged:** the 13 development times sum to 30,084 s against 30,462 s (-1.2%); cells range from -5.9% to +5.9%. Threshold times were within 1 s per cell (step E), timing lines within about 1% (step D).
- **Memory:** 413 MB peak with 2 workers.

**Conclusion:** adding scikit-learn and LightGBM to the image changed neither the calibration's numbers nor its cost. The first run's planning estimates (`PILOT_FE7_FINDINGS.md`: about 3,130 worker-hours, about 65-70 days with 2 workers; about 8 days for the I1-8 second block rule; full threshold run under 2 days) stand as measured on the rebuilt image. This closes the re-run condition of D-20 §3a (a) (Annex C C-12 (5)): "the FE-7 re-pilot is re-run on the rebuilt image, with the CPU probe and the interrupt-and-resume test, before the go-ahead". Probe: step A; interrupt-and-resume: steps E and F.
