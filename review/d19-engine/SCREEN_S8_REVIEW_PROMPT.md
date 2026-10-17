# Review prompt: D-19 screen slice S8 (cost pilot kit) at the head carrying this prompt

You are an independent adversarial reviewer working read-only, not an authority. This is a §16 review of launcher code and a pilot kit the owner will run as root on his server. Everything is attached.

Check:
1. **Launcher (`deploy/calibration/d19.sh`):** the new `screen-pilot`, `screen-status`, `screen-summary` commands and the `stop` change. They must keep every engine guarantee of the existing commands (pinned image by inspected id, uid 990, no network, read-only root, the capped slice, `nice 19`), refuse an existing record, run detached under a separate container name so the calibration `status`/`times` are unaffected, and never touch forward paper.
2. **Pilot set (`deploy/calibration/screen-pilot/`):** 20 valid declarations (they pass `check_trial`), trial code that obeys TI-2 (only `math`/`numpy`, no forbidden names), a mix that measures each cost class (rule trials with and without overlay, both families, every model class, LightGBM at its largest allowed size), and warm-ups that fit the screen's rules. Is the set a fair §10 measurement, and does anything in it bias the cost estimate low?
3. **Summary (`scripts/d19_screen.py summary`):** reports what the sheet asks for (seconds per trial, slowest path, gate results, total worker-hours, the reference vectors) and nothing that could be mistaken for a declaration outcome.
4. **Owner sheet (`deploy/calibration/PILOT_SCREEN.md`):** correct commands and order, safe step 0, the right checks, and an honest time estimate.

Out of scope: the screen's gates and driver (their own reviews).

Verdict ACCEPT or FIX. Findings get stable IDs S8-Rn with severity, file:line and a concrete failure scenario.
