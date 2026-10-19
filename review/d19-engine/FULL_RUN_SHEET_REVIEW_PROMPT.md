# Review prompt: D-19 full-run command sheet (DRAFT)

You are an independent adversarial reviewer working read-only, not an authority. Attached: the draft sheet, the re-pilot sheet it follows (PILOT_FE7.md), the launcher (d19.sh), the run driver header and job set-up (d19_run.py), rundef.run_plan/counts, grid.manifest, build_manifests write rule, and the build-order and go-ahead owner decisions. Nothing will run until P1-P3 hold.

Check: (1) Are the preconditions complete and correctly ordered against prereg §4 and the owner decisions? (2) Is every command correct for this launcher, and is any step unsafe for forward paper or for the stored re-pilot/screen records? (3) Does any step risk binding the wrong definition, prereg or engine, or starting a qualification run before the definition is committed (S16-2)? (4) Anything missing that the run needs (e.g. memory checks, a resume rule, chunk counts)? Verdict ACCEPT or FIX; IDs FS-n.
