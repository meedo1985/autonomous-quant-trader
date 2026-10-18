@echo off
rem Copy the dashboard page from the server and open it (Task 33).
rem Put your server's address in place of SERVER (once), then double-click.
scp root@SERVER:/var/lib/aqt-dashboard/page/index.html "%USERPROFILE%\Desktop\aqt-dashboard.html" && start "" "%USERPROFILE%\Desktop\aqt-dashboard.html"
