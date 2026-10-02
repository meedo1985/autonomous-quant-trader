#!/bin/sh
# First install on a fresh Ubuntu 24.04 server (roadmap 2 Task 30).
# The owner runs it as root; see deploy/RUNBOOK.md step 2.
#   sudo sh install.sh <repository URL> <commit>
# The code, its history and its interpreter belong to root: the app's
# account `aqt` can read and run them, never change them (S30-1, S30-3).
# `aqt` writes only to /var/lib/aqt.
set -eu
umask 022  # whatever the caller's: nothing here may be writable by `aqt`
REPO=$1
COMMIT=$2

apt-get update -q
apt-get install -y -q git python3-venv
id aqt >/dev/null 2>&1 ||
    useradd --system --home-dir /var/lib/aqt --shell /usr/sbin/nologin aqt
install -d -o root -g root -m 755 /etc/aqt /opt/aqt
install -d -o aqt -g aqt -m 700 /var/lib/aqt

git clone --quiet "$REPO" /opt/aqt/app
git -C /opt/aqt/app checkout --quiet "$COMMIT"
# `aqt` runs git on root's checkout for the start check, read-only.
git config --system --add safe.directory /opt/aqt/app
python3 -m venv /opt/aqt/app/.venv
/opt/aqt/app/.venv/bin/pip install --quiet --no-compile -e /opt/aqt/app
chmod -R go-w /opt/aqt

install -o root -g root -m 644 /opt/aqt/app/deploy/aqt-paper.service \
    /etc/systemd/system/aqt-paper.service
systemctl daemon-reload
echo "Installed $COMMIT. Next: approve it (RUNBOOK.md step 3)."
