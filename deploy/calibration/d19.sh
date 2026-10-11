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
    # crashed in OpenBLAS dgemm (PR #45). Exit 3 means exactly that crash
    # (FE4R-1); any other failure keeps its own exit status.
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
    139) echo "refused: this CPU crashes the pinned OpenBLAS kernel" \
            "(segmentation fault). $(grep -m1 'model name' /proc/cpuinfo)" >&2
        exit 3 ;;
    *) echo "probe failed with exit status $rc (not the known CPU crash)" >&2
        exit "$rc" ;;
    esac
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
    docker rm "$NAME" >/dev/null 2>&1 || true
    engine -d --name "$NAME" -- d19_run.py run --definition definition.json \
        --store store --namespace "$2" --raw-root raw
    echo "Started. Progress: sudo sh d19.sh status"
    ;;
status)  # FE4-5, P18-6: container state and chunks per chain, nothing else
    docker ps -a --filter "name=^$NAME\$" --format '{{.Status}}'
    find "$WORK/store" -name 'chunk-*.json' 2>/dev/null |
        awk -F/ '{ n[$(NF-2) "/" $(NF-1)]++ } END { for (c in n) print n[c], c }' |
        sort -k2
    ;;
stop)
    docker stop -t 60 "$NAME"
    ;;
choose)
    engine --rm -- d19_choose.py choose --definition definition.json \
        --store store --out choices.json
    ;;
*)
    sed -n '2,14p' "$0"
    exit 1
    ;;
esac
