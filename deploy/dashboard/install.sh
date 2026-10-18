#!/bin/sh
# Install the read-only dashboard (Task 33; deploy/RUNBOOK.md section 9).
# The owner runs it as root:  sudo sh install.sh <repository URL> <commit>
# Its own checkout at /opt/aqt-dashboard/app (root's, read-only to the
# generator); the forward paper app and its checkout are not touched.
set -eu
umask 022
REPO=$1
COMMIT=$2

id aqt-dash >/dev/null 2>&1 ||
    useradd --system --no-create-home --home-dir /nonexistent \
        --shell /usr/sbin/nologin aqt-dash
install -d -o root -g root -m 755 /opt/aqt-dashboard
git clone --quiet "$REPO" /opt/aqt-dashboard/app
git -C /opt/aqt-dashboard/app checkout --quiet "$COMMIT"
chmod -R go-w /opt/aqt-dashboard
install -d -o aqt-dash -g aqt-dash -m 755 /var/lib/aqt-dashboard

for unit in aqt-dashboard@.service aqt-dashboard.timer; do
    install -o root -g root -m 644 "/opt/aqt-dashboard/app/deploy/dashboard/$unit" \
        "/etc/systemd/system/$unit"
done
systemctl daemon-reload
systemctl start aqt-dashboard@build.service  # the first page, before the timer
systemctl enable --now aqt-dashboard.timer
echo "Installed the dashboard at $COMMIT. Next: RUNBOOK.md section 9 checks."
