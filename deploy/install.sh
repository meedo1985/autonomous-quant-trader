#!/bin/sh
# First install on a fresh Ubuntu 24.04 server (roadmap 2 Task 30).
# The owner runs it as root; see deploy/RUNBOOK.md step 2.
#   sudo sh install.sh <repository URL> <commit>
set -eu
REPO=$1
COMMIT=$2

apt-get update -q
apt-get install -y -q git python3-venv
id aqt >/dev/null 2>&1 ||
    useradd --system --create-home --home-dir /opt/aqt --shell /usr/sbin/nologin aqt
install -d -o root -g root -m 755 /etc/aqt

sudo -u aqt git clone --quiet "$REPO" /opt/aqt/app
sudo -u aqt git -C /opt/aqt/app checkout --quiet "$COMMIT"
sudo -u aqt python3 -m venv /opt/aqt/app/.venv
sudo -u aqt /opt/aqt/app/.venv/bin/pip install --quiet -e /opt/aqt/app

install -o root -g root -m 644 /opt/aqt/app/deploy/aqt-paper.service \
    /etc/systemd/system/aqt-paper.service
systemctl daemon-reload
echo "Installed $COMMIT. Next: approve it (RUNBOOK.md step 3)."
