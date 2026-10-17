# §16 different-model re-review of the screen slice S8 at 85022c3

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a1498c-5130-7781-ac42-7f50853599b8)
- Date: 2026-10-17
- Prompt: `SCREEN_S8_REREVIEW_PROMPT.md`
- Findings: S8-R1, S8-R3 resolved; S8R-R1, S8R-R2, S8R-R3 (Medium; S8-R2 and S8-R4 incomplete). Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX.** The sheet points to [`e4e7339`](https://github.com/meedo1985/autonomous-quant-trader/commit/e4e733935f15c4fdca7c75d9af9d74a59682d449), which contains the repaired launcher and summary. The later sheet commit does not change either file.

The original screen-only case in **S8-R1** now stops correctly. **S8-R3** is resolved: the summary says “MEASUREMENT ONLY” and labels available gates as `available`. The shared-peak label and trial-mix cost qualification are also present. **S8-R2 and S8-R4 remain incomplete**, with these findings:

- **S8R-R1 — Medium — stop can report false success.** [`running()` and `stop`](https://github.com/meedo1985/autonomous-quant-trader/blob/e4e733935f15c4fdca7c75d9af9d74a59682d449/deploy/calibration/d19.sh#L54-L56) treat a failed `docker inspect` like an absent container. If Docker cannot be inspected, `stop` can exit successfully saying “no D-19 run was going” without stopping or verifying either run. Distinguish inspection errors from absence and report stop failures.

- **S8R-R2 — Medium — the concurrency guard misses a calibration run.** [`alone()`](https://github.com/meedo1985/autonomous-quant-trader/blob/e4e733935f15c4fdca7c75d9af9d74a59682d449/deploy/calibration/d19.sh#L58-L64) checks only two named containers. [`clean-check`](https://github.com/meedo1985/autonomous-quant-trader/blob/e4e733935f15c4fdca7c75d9af9d74a59682d449/deploy/calibration/d19.sh#L207-L211) starts an unnamed `engine --rm` calibration run, so `screen-pilot` can start alongside it in the shared slice. The claim that the runs never compete is therefore unproven.

- **S8R-R3 — Medium — step 0 gives contradictory checks.** In the [command sheet](https://github.com/meedo1985/autonomous-quant-trader/blob/85022c31a2e76f2683639579c6ea94931042bc25/deploy/calibration/PILOT_SCREEN.md#L13-L27), the desired absent `app-$old` makes `ls -d` fail, while the sheet says to stop on *any* failed command. It also says the line after `status` must be `e39b23d`, although `status` prints its start/exit and slice-peak lines before the separate `old` command prints that hash. The destination guard exists, but an operator following the instructions literally cannot pass step 0.

This was a read-only code review. The local shell failed to start, so I could not independently rerun the supplied tests or validation checks. No review record was committed; the project’s review-record rule still applies.