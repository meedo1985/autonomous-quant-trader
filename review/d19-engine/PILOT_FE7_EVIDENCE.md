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
