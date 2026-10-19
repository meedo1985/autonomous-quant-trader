# Sol re-review: DR2-1 unlock repairs at 3799bc5

Reviewer: OpenAI Codex v0.162.1, model `gpt-6-sol`, reasoning effort high, sandbox read-only, session `01a152e8-8026-7c91-87d2-442d3da8d158`, 2026-10-19. Prompt `DR2_1_UNLOCK_REREVIEW_PROMPT.md` (3799bc5). Its shell failed; it could not rerun checks.

Final answer, verbatim:

**Verdict: FIX.**

- **DR21R-R1 — High — [calibration/rundef.py:309](D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/rundef.py:309).** `prereg_problem` hashes the bytes returned by `git show`, but does not require `prereg_commit` to be a full, immutable commit ID. A hand-edited definition can name `HEAD` or an abbreviated ID while asserting the hash those names resolve to today. A ref can later move after a worker’s check, leaving chunks bound to a hash the definition’s named ref no longer has. Git also accepts tree expressions here, although the field claims to name a commit. Require the field to equal the resolved full commit ID, verify it is a commit, and read the path using that ID.

For the four requested checks: job setup and every worker call `prereg_problem` before chunk execution; a missing commit or wrong file hash fails there. The extracted `rundef.git` preserves the recorder’s replacement-free command and `GIT_*` filtering. The DR21-R2 test change removes its dependency on the production pin being `None` while retaining the unchanged other-hash and pinned cases.

The gate record’s explanation of the nine uncommitted-tree failures is consistent with the held-out tests: those cases compare the loaded `d19_run.py` with the committed version. I could not independently rerun the checks or verify the reported command results because local shell creation failed before execution. This is read-only feedback; no review record was committed.
