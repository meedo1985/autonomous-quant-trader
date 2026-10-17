#!/bin/sh
# D-19 calibration launcher (prereg §13 rev 7g item 6; FE-4).
# The owner runs it as root on the server; the AI never logs in. See
# deploy/calibration/RUNBOOK.md.
#
#   sudo sh d19.sh install <repository URL> <engine commit>
#   sudo sh d19.sh build
#   sudo sh d19.sh probe
#   sudo sh d19.sh manifests
#   sudo sh d19.sh record <d19_run_definition.py record arguments>
#   sudo sh d19.sh run <threshold|dev>
#   sudo sh d19.sh status
#   sudo sh d19.sh stop
#   sudo sh d19.sh choose
#   sudo sh d19.sh timing
#   sudo sh d19.sh nonfinite
#   sudo sh d19.sh clean-check
#   sudo sh d19.sh failcheck
#   sudo sh d19.sh copy-raw
#   sudo sh d19.sh times <threshold|dev>
#   sudo sh d19.sh memwatch
#   sudo sh d19.sh screen-pilot
#   sudo sh d19.sh screen-status
#   sudo sh d19.sh screen-summary
#
# Every engine process runs in the pinned image, as uid 990, without network,
# at `nice 19`, inside aqt-d19.slice (systemd MemoryMax 2560M, checked before
# every start), with the engine's own read-only checkout at /app (never the
# forward-paper one). The image is started by the id that `docker image
# inspect` reports here, and the same id is AQT_IMAGE_DIGEST: never typed
# (FE-4, FE4-1). The driver runs exactly 2 workers (scripts/d19_run.py,
# WORKERS).
set -eu
umask 022  # FE4-4: uid 990 must be able to read the checkout
APP=/opt/aqt-d19/app
WORK=/var/lib/aqt-d19
NAME=aqt-d19
SLICE=aqt-d19.slice
MEMORY_MAX=2684354560  # 2560M in bytes, as systemd reports it

tag() { echo "aqt-d19:$(git -C "$APP" rev-parse --verify HEAD)"; }

capped() {  # FE4-2: refuse unless containers really land in the capped slice
    driver=$(docker info --format '{{.CgroupDriver}}')
    [ "$driver" = systemd ] || { echo "refused: docker cgroup driver is $driver, not systemd" >&2; exit 1; }
    max=$(systemctl show "$SLICE" -p MemoryMax --value)
    [ "$max" = "$MEMORY_MAX" ] || { echo "refused: $SLICE MemoryMax is $max" >&2; exit 1; }
    # --cgroupns host: a private cgroup namespace would show only "0::/".
    docker run --rm --network none --cgroupns host --cgroup-parent "$SLICE" "$1" \
        cat /proc/self/cgroup |
        grep -q "/$SLICE/" || { echo "refused: containers are not placed in $SLICE" >&2; exit 1; }
}

running() {  # running <container>: true if that container is up
    [ "$(docker inspect -f '{{.State.Running}}' "$1" 2>/dev/null)" = true ]
}

alone() {  # S8-R2: calibration and screen runs share the slice; never both
    if running "$NAME" || running "$NAME-screen"; then
        echo "refused: a D-19 run is going (sudo sh d19.sh status / screen-status)" >&2
        exit 1
    fi
}

engine() {  # engine [docker run options...] -- <script> [arguments...]
    id=$(docker image inspect --format '{{.Id}}' "$(tag)")
    capped "$id"
    opts=""
    while [ "$1" != "--" ]; do opts="$opts $1"; shift; done
    shift
    script=$1
    shift
    # --init: python is not PID 1, so `stop` (SIGTERM) ends it at once.
    # shellcheck disable=SC2086  # $opts is a list of plain flags
    docker run $opts --init --user 990:990 --network none --read-only \
        --tmpfs /tmp --cgroup-parent "$SLICE" --memory 2560m \
        -e AQT_IMAGE_DIGEST="$id" -e HOME=/tmp \
        -v "$APP:/app:ro" -v "$WORK:/work" -w /work \
        "$id" nice -n 19 python "/app/scripts/$script" "$@"
}

case "${1:-}" in
install)
    REPO=$2
    COMMIT=$3
    apt-get update -q
    apt-get install -y -q git
    command -v docker >/dev/null || apt-get install -y -q docker.io
    install -d -o root -g root -m 755 "$(dirname "$APP")"
    git clone --quiet "$REPO" "$APP"
    git -C "$APP" checkout --quiet "$COMMIT"
    chmod -R go-w "$APP"
    install -d -o 990 -g 990 -m 700 "$WORK"
    install -o root -g root -m 644 "$APP/deploy/calibration/$SLICE" \
        "/etc/systemd/system/$SLICE"
    systemctl daemon-reload
    echo "Installed engine $COMMIT. Next: sudo sh d19.sh build"
    ;;
build)
    docker build --pull -t "$(tag)" "$APP/deploy/calibration"
    echo "Image $(tag) id $(docker image inspect --format '{{.Id}}' "$(tag)")"
    echo "Next: sudo sh d19.sh probe"
    ;;
probe)  # can this CPU run the pinned runtime? (V_BINDING: OPENBLAS_CORETYPE=Haswell)
    # The engine's own measurement (canaries and reference vectors), once,
    # under the run's own bounds (FE4R-3). On AMD EPYC Zen 4/5 runners it
    # crashed in OpenBLAS dgemm (PR #45). Exit 3 means a segmentation fault
    # in the measurement, and only that (FE4R-1, FE4R2-1). It is reported
    # as unclassified until diagnosed (FE4R2-2): the AMD crash is the likely
    # cause, not a proven one.
    id=$(docker image inspect --format '{{.Id}}' "$(tag)")
    capped "$id"
    rc=0
    docker run --rm --init --user 990:990 --network none --read-only \
        --tmpfs /tmp --cgroup-parent "$SLICE" --memory 2560m \
        -e HOME=/tmp -e OPENBLAS_NUM_THREADS=1 -e OPENBLAS_CORETYPE=Haswell \
        -v "$APP:/app:ro" "$id" nice -n 19 python -B -c \
        "import sys; sys.path[:0] = ['/app', '/app/src']
from calibration import rundef; rundef.gating('probe')" || rc=$?
    case $rc in
    0) echo "This CPU runs the pinned runtime." ;;
    139) echo "refused: the measurement crashed (segmentation fault)," \
            "not yet diagnosed; on newer AMD EPYC this has been the pinned" \
            "OpenBLAS kernel. $(grep -m1 'model name' /proc/cpuinfo)" >&2
        exit 3 ;;
    *) echo "probe failed with exit status $rc" >&2
        [ "$rc" = 3 ] && exit 1  # exit 3 is reserved for a crash
        exit "$rc" ;;
    esac
    ;;
copy-raw)  # FE7-8: forward paper's exploration archives, once; never overwrites
    [ ! -e "$WORK/raw" ] || { echo "refused: $WORK/raw already exists" >&2; exit 1; }
    # FE7R2-3: a failed copy leaves nothing behind; raw appears only complete
    rm -rf "$WORK/raw.partial"
    cp -r /var/lib/aqt/data/raw "$WORK/raw.partial" ||
        { rm -rf "$WORK/raw.partial"; echo "FAIL: copy failed" >&2; exit 1; }
    chown -R 990:990 "$WORK/raw.partial"
    mv "$WORK/raw.partial" "$WORK/raw"
    echo "Copied $(find "$WORK/raw" -name '*.zip' | wc -l) archives"
    ;;
manifests)  # the BTC exploration manifest that `record` needs (Task 14)
    engine --rm -e PYTHONPATH=/app/src -- build_manifests.py --raw raw \
        --out manifests --symbol BTCUSDT
    ;;
record)
    shift
    engine --rm -- d19_run_definition.py record "$@"
    ;;
run)
    alone
    docker rm "$NAME" >/dev/null 2>&1 || true
    engine -d --name "$NAME" -- d19_run.py run --definition definition.json \
        --store store --namespace "$2" --raw-root raw
    echo "Started. Progress: sudo sh d19.sh status"
    ;;
status)  # FE4-5, P18-6: state, times, memory, chunks per chain; nothing else
    docker ps -a --filter "name=^$NAME\$" --format '{{.Status}}'
    # FE7-3: the run's own start, finish and exit (kept until the next run)
    docker inspect -f 'started {{.State.StartedAt}} finished {{.State.FinishedAt}} exit {{.State.ExitCode}}'         "$NAME" 2>/dev/null || true
    # FE7-4: the capped slice's exact peak memory since it started, shared by
    # calibration and screen runs (S8-R2; `memwatch` gives a run's own peak)
    echo "slice memory peak (all D-19 runs since the slice started): $(systemctl show "$SLICE" -p MemoryPeak --value) bytes"
    find "$WORK/store" -name 'chunk-*.json' 2>/dev/null |
        awk -F/ '{ n[$(NF-2) "/" $(NF-1)]++ } END { for (c in n) print n[c], c }' |
        sort -k2
    ;;
stop)  # S8-R1: each D-19 container that is up, independently
    stopped=0
    for c in "$NAME" "$NAME-screen"; do
        if running "$c"; then docker stop -t 60 "$c" >/dev/null && echo "stopped $c" && stopped=1; fi
    done
    [ "$stopped" = 1 ] || echo "no D-19 run was going"
    ;;
screen-pilot)  # S8, prereg §10: one screen of the 20-trial pilot set, measurement only
    [ ! -e "$WORK/screen-pilot.json" ] || { echo "refused: $WORK/screen-pilot.json exists" >&2; exit 1; }
    alone
    docker rm "$NAME-screen" >/dev/null 2>&1 || true
    engine -d --name "$NAME-screen" -- d19_screen.py pilot \
        --trials /app/deploy/calibration/screen-pilot/trials.json \
        --trial-code /app/deploy/calibration/screen-pilot \
        --raw-root raw --out screen-pilot.json
    echo "Started. Progress: sudo sh d19.sh screen-status"
    ;;
screen-status)  # S8: state, times and this run's memory high-water mark
    docker ps -a --filter "name=^$NAME-screen\$" --format '{{.Status}}'
    docker inspect -f 'started {{.State.StartedAt}} finished {{.State.FinishedAt}} exit {{.State.ExitCode}}' \
        "$NAME-screen" 2>/dev/null || true
    if running "$NAME-screen"; then
        pid=$(docker inspect -f '{{.State.Pid}}' "$NAME-screen")
        echo "memory peak so far: $(cat "/sys/fs/cgroup$(cut -d: -f3 "/proc/$pid/cgroup")/memory.peak") bytes"
    fi
    docker logs --tail 3 "$NAME-screen" 2>&1 || true
    ;;
screen-summary)  # S8: seconds per trial and gate availability from the record
    engine --rm -- d19_screen.py summary --record screen-pilot.json
    ;;
choose)
    engine --rm -- d19_choose.py choose --definition definition.json \
        --store store --out choices.json
    ;;
timing)  # re-pilot (FE-7, I1-8): seconds per stage, both block rules apart
    engine --rm -- d19_pilot.py --reps 20
    ;;
nonfinite)  # FE-7, FE7-5: non-finite threshold diagnostics, per cell
    engine --rm -- d19_pilot_checks.py nonfinite store
    ;;
clean-check)  # FE7-2: a clean threshold run equals the interrupted+resumed one
    [ ! -e "$WORK/store-clean" ] ||
        { echo "refused: $WORK/store-clean exists; a clean run needs an empty store" >&2; exit 1; }
    engine --rm -- d19_run.py run --definition definition.json         --store store-clean --namespace threshold --raw-root raw
    engine --rm -- d19_pilot_checks.py compare store store-clean
    ;;
times)  # FE7-3: per chain, seconds between finished chunks = one worker's
    # time for 500 replications (a chain's chunks run back to back on one
    # worker). FE7R2-1: an interval across the current run's start spans a
    # stop and a resume, so it is marked and is no worker time. FE7R3-1: one
    # namespace, read while its own (last) run is the current container;
    # FE7R3-2: the start time keeps its fraction of a second.
    case "${2:-}" in threshold | dev) ;; *) echo "usage: d19.sh times <threshold|dev>" >&2; exit 1 ;; esac
    # FE7F-1: a chain directory exists before its first chunk is written
    [ -n "$(find "$WORK/store/$2" -name 'chunk-*.json' -print -quit 2>/dev/null)" ] ||
        { echo "no $2 chunks yet"; exit 0; }
    started=$(date -d "$(docker inspect -f '{{.State.StartedAt}}' "$NAME")" +%s.%N)
    for d in "$WORK/store/$2"/*/; do
        find "$d" -name 'chunk-*.json' -printf '%T@\n' | sort -n |
            awk -v c="$(basename "$(dirname "$d")")/$(basename "$d")" -v t0="$started" \
                'NR > 1 { s = s sprintf(" %.0f", $1 - p) (p < t0 && $1 >= t0 ? "(spans a restart)" : "") }
                 { p = $1 }
                 END { print c ":" (NR == 0 ? " (no chunk yet)" : s == "" ? " (one chunk)" : s) }'
    done
    ;;
memwatch)  # FE7-4, FE7R2-2: the run's exact memory high-water mark, with
    # evidence over 10 minutes that both workers were running
    n=0
    for _ in $(seq 60); do
        if [ "$(docker top "$NAME" -eo pid,args 2>/dev/null | grep -c spawn_main)" = 2 ]; then
            n=$((n + 1))
        fi
        sleep 10
    done
    [ "$n" -gt 0 ] || { echo "FAIL: no sample showed 2 workers running" >&2; exit 1; }
    # the container's own cgroup, as the kernel reports it (systemd nests
    # aqt-d19.slice inside aqt.slice: the dash means a parent slice)
    pid=$(docker inspect -f '{{.State.Pid}}' "$NAME")
    peak=$(cat "/sys/fs/cgroup$(cut -d: -f3 "/proc/$pid/cgroup")/memory.peak")
    echo "2 workers in $n of 60 samples; this run's memory peak: $peak bytes"
    ;;
failcheck)  # FR2-2, FE7-7: kill one worker; the run must stop, none survive
    [ "$(docker inspect -f '{{.State.Running}}' "$NAME" 2>/dev/null)" = true ] ||
        { echo "refused: no run is going (start one with: run threshold)" >&2; exit 1; }
    # shellcheck disable=SC2046  # the PIDs are words
    set -- $(docker top "$NAME" -eo pid,args | awk '/spawn_main/ { print $1 }')
    [ $# = 2 ] || { echo "refused: expected 2 workers, found $#" >&2; exit 1; }
    echo "workers $1 and $2; killing $1"
    kill -9 "$1"
    for _ in $(seq 120); do
        [ "$(docker inspect -f '{{.State.Running}}' "$NAME")" = false ] && break
        sleep 1
    done
    code=$(docker inspect -f '{{.State.ExitCode}}' "$NAME")
    [ "$(docker inspect -f '{{.State.Running}}' "$NAME")" = false ] ||
        { echo "FAIL: the run did not stop within 120 s" >&2; exit 1; }
    [ "$code" != 0 ] || { echo "FAIL: the run exited 0 after a killed worker" >&2; exit 1; }
    ! kill -0 "$2" 2>/dev/null || { echo "FAIL: worker $2 outlived the run" >&2; exit 1; }
    echo "PASS: the run stopped (exit $code) and no worker outlived it"
    docker logs --tail 3 "$NAME" 2>&1
    ;;
*)
    sed -n '2,21p' "$0"
    exit 1
    ;;
esac
