#!/bin/sh
# D-19 calibration launcher (prereg §13 rev 7g item 6; FE-4).
# The owner runs it as root on the server; the AI never logs in. See
# deploy/calibration/RUNBOOK.md.
#
#   sudo sh d19.sh install <repository URL> <engine commit>
#   sudo sh d19.sh build
#   sudo sh d19.sh manifests
#   sudo sh d19.sh record <d19_run_definition.py record arguments>
#   sudo sh d19.sh run <threshold|dev>
#   sudo sh d19.sh status
#   sudo sh d19.sh stop
#   sudo sh d19.sh choose
#
# Every engine process runs in the pinned image, as uid 990, without network,
# at `nice 19`, inside aqt-d19.slice (MemoryMax 2560M), with the engine's own
# read-only checkout at /app (never the forward-paper one). AQT_IMAGE_DIGEST
# is read from `docker image inspect` here, never typed (FE-4).
set -eu
APP=/opt/aqt-d19/app
WORK=/var/lib/aqt-d19
NAME=aqt-d19

image() { echo "aqt-d19:$(git -C "$APP" rev-parse --verify HEAD)"; }

engine() {  # engine [docker run options...] -- <script> [arguments...]
    digest=$(docker image inspect --format '{{.Id}}' "$(image)")
    opts=""
    while [ "$1" != "--" ]; do opts="$opts $1"; shift; done
    shift
    script=$1
    shift
    # shellcheck disable=SC2086  # $opts is a list of plain flags
    # --init: python is not PID 1, so `stop` (SIGTERM) ends it at once.
    docker run $opts --init --user 990:990 --network none --read-only \
        --tmpfs /tmp --cgroup-parent aqt-d19.slice --memory 2560m \
        -e AQT_IMAGE_DIGEST="$digest" -e HOME=/tmp \
        -v "$APP:/app:ro" -v "$WORK:/work" -w /work \
        "$(image)" nice -n 19 python "/app/scripts/$script" "$@"
}

case "${1:-}" in
install)
    REPO=$2
    COMMIT=$3
    apt-get update -q
    apt-get install -y -q docker.io git
    install -d -o root -g root -m 755 /opt/aqt-d19
    git clone --quiet "$REPO" "$APP"
    git -C "$APP" checkout --quiet "$COMMIT"
    chmod -R go-w "$APP"
    install -d -o 990 -g 990 -m 700 "$WORK"
    install -o root -g root -m 644 "$APP/deploy/calibration/aqt-d19.slice" \
        /etc/systemd/system/aqt-d19.slice
    systemctl daemon-reload
    echo "Installed engine $COMMIT. Next: sudo sh d19.sh build"
    ;;
build)
    docker build --pull -t "$(image)" "$APP/deploy/calibration"
    echo "Image $(image) id $(docker image inspect --format '{{.Id}}' "$(image)")"
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
status)
    docker ps -a --filter "name=^$NAME\$" --format '{{.Status}}'
    docker logs --tail 5 "$NAME" 2>&1 || true
    # Progress counts only (chunks per chain); never chunk content (P18-6).
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
    sed -n '2,13p' "$0"
    exit 1
    ;;
esac
