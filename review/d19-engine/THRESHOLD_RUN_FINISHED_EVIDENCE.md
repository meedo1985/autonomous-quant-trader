# Threshold run finished (FULL_RUN.md step D)

Owner's server output, 2026-10-24 (pasted to the AI; the AI never logs in).

- `d19.sh status`: `Exited (0) 2 days ago`; `started 2026-10-20T11:00:15.164071663Z finished 2026-10-22T06:16:43.891947039Z exit 0`.
- Slice memory peak (all D-19 runs since the slice started): 2030317568 bytes (cap 2684354560).
- 104 `threshold/` lines, every one at 600 chunks.
- Comparison with `deploy/calibration/qualification-cells.json` (the file whose hash was checked in step C): 104 listed, 104 expected, missing none, unexpected none.
- Finished rule of step D holds: `Exited (0)`, all 104 expected ids at `600 threshold/`, no other `threshold/` line.
- Duration about 43 hours with 2 workers. The go-ahead's 3,130 worker-hours is dominated by development (both block rules in every development replication, I1-8), so a short threshold run does not contradict it.
- Weekly Telegram test sent and acknowledged 2026-10-24 09:51Z.
- Forward paper `active (running) since Fri 2026-10-23 06:34:53 UTC`: it restarted on 2026-10-23, cause not yet known (journal requested).

Next: step E, development run (`sudo sh d19.sh run dev`). `run` removes the old container, so the status above is the only record of the threshold container's times and exit.
