# §16 different-model re-review 2 of the screen slice S7 at 8f40348

- Reviewer: Codex CLI v0.162.1, model gpt-6-sol, reasoning effort high, sandbox read-only (session 01a14972-aa15-7511-a857-e0774b9d5b1b)
- Date: 2026-10-17
- Prompt: `SCREEN_S7_REREVIEW2_PROMPT.md`
- Findings: S7R-R1 still open (path aliases), new S7R2-R1 (Medium, cleanup by name). S7R-R2..R4 resolved. Verdict: FIX.
- The reviewer's final output follows verbatim.

---

**Verdict: FIX** for the committed S7 repair at `8f40348`. S7R-R2, R3, and R4 are addressed in the reviewed code. S7R-R1 remains open.

| ID | Severity | Finding |
|---|---|---|
| **S7R-R1 remains open** | High | [`_extend_path`](https://github.com/meedo1985/autonomous-quant-trader/blob/8f403485bcded648782b3d4bbb476d96e4fb7864/calibration/screen.py#L1879-L1893) removes entries by exact string comparison. If `sys.path` contains a symlink or another spelling of `code_dir` before site-packages, that entry stays there. A trial-supplied `sklearn` or `lightgbm` can still be selected during a model screen. The new test covers only identical strings. Compare resolved directory identities and test an alias placed first. |
| **S7R2-R1** | Medium | The CLI’s [failure cleanup](https://github.com/meedo1985/autonomous-quant-trader/blob/8f403485bcded648782b3d4bbb476d96e4fb7864/scripts/d19_screen.py#L54-L84) unlinks `args.out` by name, without establishing that it still names this run’s reserved file. On a filesystem that permits replacement of an open file, another process can replace the path while the screen runs; if this run then fails, cleanup deletes the replacement. Avoid path-based cleanup that can remove another file. |

The raw-root declaration now rebuilds bars through the sidecar-checked loader, closing the caller-supplied-array route in S7R-R2. `run_screen` sets the parent import path before preloading, closing S7R-R3’s missing-module case. Exclusive output creation now precedes screen work, closing S7R-R4’s wasted-jobs case.

I verified commit `8f40348` and its diff through the read-only GitHub view. The local command runner failed before launch, so I could not run tests or inspect uncommitted files. This response is **not a committed review record**; the project’s review-record requirement remains outstanding.