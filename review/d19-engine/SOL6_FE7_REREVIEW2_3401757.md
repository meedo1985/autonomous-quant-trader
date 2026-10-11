<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-11. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a12ac2-ac7c-7d32-a033-9b096d870706. Tokens used: 49,497. Made from a packet built from commit 3401757 (git show/diff only): the prompt below, SOL6_FE7_REREVIEW_A939AD0.md, the 'Re-review' section of ADJUDICATION_FE7_FC214A3.md, git diff a939ad0..3401757 -- deploy scripts tests .github, d19.sh, PILOT_FE7.md and d19_pilot_checks.py at 3401757, and the dev_replication excerpt of scripts/d19_run.py. -->

> # Focused re-review 2: D-19 FE-7 kit (a939ad0..3401757)
> 
> You are an independent adversarial reviewer working read-only. You are not an authority. Review ONLY the repairs of the open points of your re-review, using:
> - your re-review;
> - the adjudication section "Re-review";
> - the diff;
> - the files at 3401757: `d19.sh`, `PILOT_FE7.md`, `d19_pilot_checks.py`;
> - the `dev_replication` excerpt of `scripts/d19_run.py`.
> 
> The open points are: FE7-2/FE7R-1, FE7R-2, FE7-3, FE7-4, FE7-6 (disagreed with evidence) and FE7-8.
> 
> **CI at 3401757.** `calibration-launcher` passed on AMD EPYC 7763. It ran `clean-check` (PASS), checked that a second `clean-check` is refused, and ran `times` and `nonfinite`.
> 
> **Questions.**
> 1. Is each open point resolved? Is the FE7-6 disagreement justified?
> 2. Is the command sheet now correct and safe for a non-expert owner?
> 3. Did the repairs introduce any new defect? Consider `times`, `memwatch`, `copy-raw` and the byte comparison.
> 
> **Output.**
> - Put your model metadata at the top.
> - Give a verdict for giving the kit to the owner: ACCEPT or FIX.
> - Number new findings FE7R2-n. Give each one a severity, a file:line, a failure scenario and the minimal fix.

## Review (verbatim)

**Model metadata:** Codex, GPT-6 family. The exact runtime model ID and reasoning effort are not exposed to me; I did not switch models.

**Verdict: FIX before giving the kit to the owner.** The byte comparison and clean-store refusal are repaired, but the sheet still presents timing and memory samples as measurements they do not establish.

| Open point | Assessment |
|---|---|
| FE7-2 / FE7R-1 | **Resolved.** `compare` requires the same cells, chunk names, and byte-identical chunk contents. Equal chunk bytes imply equal stored chain heads. |
| FE7R-2 | **Resolved.** `clean-check` refuses an existing `store-clean`; CI exercised that refusal. |
| FE7-3 | **Unresolved.** Chunk completion timestamps do not measure worker time. |
| FE7-4 | **Unresolved.** A maximum of 10-second memory samples is not the development run’s peak. |
| FE7-6 | **Disagreement justified.** The development path computes the classifier decision before `dsr.evaluate`; the diagnostics stage times that work. The timer’s accepting path exercises the longer DSR branch. This is a path comparison, not a guaranteed upper bound for every possible input’s elapsed time. |
| FE7-8 | **Original issue resolved.** An existing raw directory now causes a clear refusal. The copy has a separate failure-recovery defect below. |

### New findings

1. **FE7R2-1 — High — `deploy/calibration/d19.sh:167`.** `times` subtracts chunk file modification times. If a chunk finishes before `failcheck` and the next finishes after the owner resumes, the reported “500 replications” includes the entire stopped interval. Normal scheduling gaps can also enter the figure. **Fix:** measure each chunk’s elapsed worker time inside the worker, save it outside the deterministic chunk files, and report those durations. Change the sheet’s claim until that measurement exists.

2. **FE7R2-2 — Medium — `deploy/calibration/d19.sh:176`.** `memwatch` can miss a short memory spike between samples; if it sees no two-worker sample, it successfully prints a maximum of **0 bytes**. The sheet calls this a peak with two workers. **Fix:** refuse a zero-sample result and use an interval-scoped memory high-water mark for the development run, while recording evidence that two workers ran.

3. **FE7R2-3 — Medium — `deploy/calibration/d19.sh:118`.** If `cp -r` fails partway through, it leaves a partial `raw` directory. The next `copy-raw` refuses it, while the sheet tells the owner to stop only on `refused` or `FAIL`; an interactive shell can continue to `manifests` after the copy error. **Fix:** copy to a temporary directory, remove it on failure, and rename it to `raw` only after success. Tell the owner to stop on **any failed command**.

The reported CI confirms normal `clean-check`, its repeat refusal, `times` output presence, and `nonfinite`. It does not establish the accuracy of `times` or exercise `memwatch` and `copy-raw`.
