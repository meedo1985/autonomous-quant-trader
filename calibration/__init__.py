"""D-19 calibration engine (inactive; the owner's go-ahead covers the build and
a measured pilot only, `OWNER_DECISION_D19_ACCEPT.md`).

Outside `aqt` because it uses NumPy, which `aqt` never imports (pyproject
`dev` note). It imports `aqt`; `aqt` never imports it. Synthetic data only;
no research, confirmation, lockbox, governor or execution access."""
