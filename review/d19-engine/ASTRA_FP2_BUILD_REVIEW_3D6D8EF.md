<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-24. CLI banner: model gpt-6-astra, reasoning effort high, sandbox read-only, session 01a16e61-011c-7ef0-9ce5-67a0725ec32e. Tokens used: 129,839. Prompt: review/d19-engine/FP2_BUILD_REVIEW_PROMPT.md (commit 621f9e2), reviewing 3d6d8ef. The reviewer's closing remark "Exact reviewer model/effort metadata was unavailable" refers to its own view; the banner above is the CLI's record. Below: the reviewer's two final messages, unedited. -->

# Astra review of FP2 (freeze and held-out launcher commands) at 3d6d8ef

- Findings: FP2-R1 (MAJOR), FP2-R2 (MAJOR). Verdict: FIX.
- Adjudication: `ADJUDICATION_FP2_BUILD_3D6D8EF.md`.

---

codex
The verdict is FIX. Certification checks for an existing report before acquiring the lock, which leaves an overwrite race. FP2 also lacks the promised procedure for installing and verifying the merged build checkout. I found no event-content disclosure in the new status path. The protected-file diff is empty, and the frozen hashes I checked match.
codex
Reviewed `6cd20c8..3d6d8ef` directly from Git, including the connected builder, runner, governing text and draft sheet. No files changed.

**FP2-R1 — MAJOR — Certification can overwrite an existing report.**

**Place:** `deploy/calibration/d19.sh:365–369`; the eventual write is `scripts/d19_heldout.py:458`.

**Failure scenario:** Invocation A passes the output-existence check and is suspended before `engine()` acquires the lock. Invocation B completes certification, writes `certify-v1.json`, and releases the lock. A resumes, acquires the lock, and runs certification without rechecking the output. The runner’s `write_text()` truncates the existing report. The lock prevents simultaneous engine execution but does not make the earlier existence check safe.

**Repair:** Call `lock` before checking the output path, retaining it through execution and printing. Add a regression check for this interleaving. Exclusive output creation in the runner would provide additional protection, but moving the launcher check inside the lock is the smallest scoped repair.

**FP2-R2 — MAJOR — The promised build-installation and commit-verification procedure is missing.**

**Place:** `deploy/calibration/d19.sh:47,327–332`; `freeze-sheet:deploy/calibration/FREEZE_HELDOUT.md`, §0 FP2(d).

**Failure scenario:** On the existing server, the documented installation creates `/opt/aqt-d19/app`, not `/opt/aqt-d19/build`; step G therefore cannot run without an undocumented setup step. If someone creates `build` at an unintended commit, `freeze` simply selects its `HEAD`. QO-2 checks the **definition commit’s** remote ancestry, not whether the build checkout is the reviewed, merged build commit.

**Repair:** Supply the promised owner-run installation procedure: create the root-owned build checkout, select and verify the approved full merge SHA, verify `/app` remains at the run’s full SHA, check permissions and origin, and record that evidence before step G. The launcher currently depends on this procedural binding.

The remaining answers:

1. **Object integrity and filesystem scope.** With the intended checkouts installed, I found no new path that publishes an object rejected by `qobj.read`. Fresh `choose`, review hashes, definition timing, chain checks and staged publication remain intact. Fetch does not check out fetched code. `--no-hardlinks` correctly prevents the clone’s object files sharing ownership with the build checkout. [Git documentation](https://git-scm.com/docs/git-clone)  
   The reviewed tree contains no symlinks. Under the stated ordinary-directory layout, cleanup and ownership changes stay within `freeze-root`; this is not a general containment guarantee against externally replaced paths.

2. **Network.** `NET=none` overwrites an inherited `NET`; only the freeze branch changes it. Other engine commands retain explicit network isolation. I accept BUILD-1 under the trusted-code deployment assumption, but its scope is the **whole freeze container and its children for their entire lifetime**. Bridge mode provides external access and communication with other containers on that bridge; it is not restricted to the Git remote. [Docker documentation](https://docs.docker.com/engine/network/drivers/bridge/) Installation and image building already require network separately.

3. **Visibility, concurrency and evidence.** The new held-out start/status paths do not display event content. Status reads names and counts, not chunk bodies. `certify` reaches `engine()`’s lock despite lacking a direct call. The shared lock and slice checks prevent concurrent engine runs; FP2-R1 remains the report-overwrite exception.

4. **Shell behavior.** Dash syntax and malformed heldout/certify argument checks passed. Quoted argument forwarding is sound. An in-memory shell harness confirmed report printing with exit statuses **0 and 2 preserved**. Freeze/status ignore extra arguments, but I found no consequential failure from that.

5. **Sheet and BO-4.** Besides FP2-R2 and the acknowledged posted-hash syntax update, replace “read-only checkout … as `root`” with the actual arrangement: protected source checkout plus writable disposable clone. All three recorded SHA-256 values match committed blobs. The screen record is sufficient **as the final closure of the cumulative review chain**, not as a standalone review of the entire screen: the earlier record confirms the `f3e3313` code repair; subsequent findings concern gate-record wording.

Validation: changed Python blobs passed Ruff lint/format checks; protected files and sidecars are unchanged from the base; checked frozen hashes and the Constitution canonical hash match. Docker/systemd integration, pytest, mypy and import-boundary checks were not independently rerun. The GitHub lookup returned no PR-triggered workflow run for this exact SHA. The pilot refusal occurs before the remote fetch, so it does not validate that operation.

**Verdict: FIX. LOCAL GATE: BLOCKED.** This is not merge approval. Exact reviewer model/effort metadata was unavailable. Per the read-only instruction, no review record was committed; the full findings still need preservation before repairs under the repository rule.
