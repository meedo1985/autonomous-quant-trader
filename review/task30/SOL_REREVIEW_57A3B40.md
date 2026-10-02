# Task 30 Sol High re-review of `57a3b40` — FIX

Date: 2026-10-02. Requested by the owner (re-review after the repairs of
`SOL_REVIEW_3C41F70.md`; "ok tell me when Sol finishes").

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < review/task30/SOL_PROMPT_57A3B40.md`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a0fd88-e64b-7002-8437-7a4345f3c366`;
  tokens used 100,551; exit 0.
- Checkout HEAD at run time: `29bf695`. Prompt SHA-256:
  `529f797145f17411a1c47e1a3b6c32ddfcbf5762369ab78fb1b9976067a8ad14`.
- Findings: S30-1, S30-3, S30-5 CORRECT; S30-2, S30-6 DISPOSITION HOLDS;
  S30-4 INCOMPLETE (see S30-8); new S30-7, S30-8 BLOCKER. The author's
  dispositions follow in `LOCAL_REPORT.md`.

Below is the reviewer's final message, verbatim.

---

# Task 30 independent adversarial re-review

**Reviewer model:** GPT-5.6 Sol, high effort, as session-designated. No separate runtime-model metadata endpoint was available for independent verification.  
**Implementation model:** Claude Opus 5.5.  
**Reviewed commit:** `57a3b4071e3ab9934ea76d9c71ec7a981c2d2c30`  
**Repair base:** `3c41f7092ef1757acec82905102ebf92189d0f4e`  
**Verdict:** **FIX**  
**Gate:** **BLOCKED**

The branch tip during review was `29bf695`, containing only the later local report and re-review prompt. Implementation analysis was commit-anchored to `57a3b40`.

## Previous findings

| ID | Result | Evidence |
| --- | --- | --- |
| **S30-1** | **CORRECT** | [install.sh](D:/PMP-programs-for-sharawi/autonomous-quant-trader/deploy/install.sh:9) forces `umask 022`, creates the checkout and virtualenv as root, and removes group/other write permissions from `/opt/aqt`. [aqt-paper.service](D:/PMP-programs-for-sharawi/autonomous-quant-trader/deploy/aqt-paper.service:13) gives `aqt` `/var/lib/aqt` through `StateDirectory`, uses absolute root-owned executable paths, and no longer makes `/opt/aqt` writable. Updates likewise run as root and finish with `chmod -R go-w`. Nothing found under `/var/lib/aqt` is later executed by root. S30-7 below is a separate root-only-record failure. |
| **S30-2** | **DISPOSITION HOLDS** | The root-owned service always supplies `--deployment-record`; making the general-purpose CLI option mandatory would not constrain a user already able to execute arbitrary programs as `aqt`. Imported source, `.venv`, and `.git` are root-owned. Ignored files are rejected under `src`, `scripts`, and `configs` by [deployment.py](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/core/deployment.py:89). The quoted fresh-Ubuntu CI reached `May run`, proving `--no-compile` and the editable installation do not falsely reject the intended clean checkout. Ignored executable material can still exist in `.venv`, but `aqt` cannot write there. |
| **S30-3** | **CORRECT** | `.git` and `refs/remotes/origin/main` are root-owned. `aqt` receives read-only Git access through root-controlled system `safe.directory`; only the owner’s root update commands can fetch or move the remote-tracking reference. |
| **S30-4** | **INCOMPLETE** | CI now starts the real service after modifying the runner and proves exit 2, no restart, and an operations-log `REFUSE_START`. However, the approval check is still after configuration parsing, so a malformed modified tracked config exits 1 before the check or logger and is repeatedly restarted. See S30-8. |
| **S30-5** | **CORRECT** | [telegram.py](D:/PMP-programs-for-sharawi/autonomous-quant-trader/src/aqt/monitoring/telegram.py:179) opens with `O_NOFOLLOW`, validates the same descriptor using `fstat`, requires a regular file owned by the effective account with no group/other permissions, and reads through that descriptor. Error text exposes only the path and exception type or a generic format requirement, not the credential. |
| **S30-6** | **DISPOSITION HOLDS** | The whole-tree authority remains the commit ID plus clean-checkout enforcement. `source_sha256` still covers only `src/aqt`, and dependency versions remain unlocked and unlogged. This limitation is accurately disclosed and is not represented as repaired. |

## New findings

### S30-7 — BLOCKER — The deployment record can inherit world-writable permissions

**Location:** [RUNBOOK.md](D:/PMP-programs-for-sharawi/autonomous-quant-trader/deploy/RUNBOOK.md:45), `.github/workflows/ci.yml:50-54`, `src/aqt/core/ledger.py:411`

**Concrete scenario:** The report records that the Ubuntu CI runner’s `sudo` preserved a permissive umask, which originally made the cloned tree writable by `aqt`. The repair sets `umask 022` only inside `install.sh`; that child-process setting does not affect the later step-3 approval command.

The approval command creates `/etc/aqt/deployments.jsonl` through:

```python
open(target, "ab")
```

No mode is enforced afterward. A newly created file therefore uses `0666 & ~umask`; with the already-observed permissive umask it is mode `0666`. The root-owned `/etc/aqt` directory prevents replacement of the directory entry, but a world-writable existing record can still be truncated or rewritten directly by `aqt`. The hash chain does not prevent a writable account from recomputing the chain. The `0644` lock sidecar does not help against a writer that ignores the cooperative lock.

This invalidates the runbook’s “Only root can write the record” statement and T30-01’s disposition.

The CI ownership test runs before approval and checks only whether `aqt` can create a file in `/etc/aqt`; it never checks the resulting record or lock file after approval.

**Reproduced:** **Yes, scratch-free call trace; no file created.**

```text
rtk .venv\Scripts\python.exe -B -c "<mock append_entry and inspect open call>"
exit 0
ledger_open_call=call(WindowsPath('deployments.jsonl'), 'ab')
mode_if_umask_000=0o666
```

The actual Ubuntu CI file mode could not be fetched because network access was prohibited, but the author’s quoted CI evidence establishes the permissive `sudo` umask on that runner.

**Required correction:** Create or enforce the deployment record with explicit root-controlled ownership and non-writable-by-`aqt` permissions, including existing files. CI should approve first, then prove `aqt` cannot write or truncate both the record and its lock sidecar.

---

### S30-8 — BLOCKER — A malformed modified config bypasses the deployment refusal path

**Location:** [run_paper_trading.py](D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/run_paper_trading.py:54), [aqt-paper.service](D:/PMP-programs-for-sharawi/autonomous-quant-trader/deploy/aqt-paper.service:17), `tests/unit/test_deployment.py:192-210`

**Concrete scenario:** Modify or delete the tracked `configs/paper_trading.example.toml`. The runner calls `load_config()` at line 54, while `approved_code()` is not reached until line 66.

An invalid TOML file raises before:

- the checkout integrity check;
- creation of the operations log;
- the CRITICAL `REFUSE_START`;
- the explicit return code 2.

The process exits 1. Because the unit has `Restart=on-failure` and prevents restarts only for exit 2, systemd repeatedly restarts it.

The new unit test uses the valid committed configuration, and CI modifies only `scripts/run_paper_trading.py`, so neither check covers this ordering failure.

**Reproduced:** **Yes, scratch-free monkeypatch probe.**

```text
rtk .venv\Scripts\python.exe -B -c "<load runner; make load_config raise; count approved_code calls>"
exit 1
ValueError: malformed modified config
approved_code_calls=0
```

**Required correction:** When the server deployment flag is present, verify approval before reading the tracked configuration or any data. The refusal logger must not depend on successfully parsing an unverified config; use a deterministic startup-refusal location or equivalent mechanism that still produces the required log and exit 2.

## Root-owned layout

The intended Ubuntu layout is otherwise coherent:

- `/opt/aqt/app`, `.git`, and `.venv` are root-owned, readable/executable by `aqt`, and made non-writable with both `umask 022` and `chmod -R go-w`.
- `/var/lib/aqt` is the only service state tree. `StateDirectory=aqt` makes it writable under `ProtectSystem=strict`, and the working directory makes relative raw data, reports, alert ledgers, incidents, and operations logs land there.
- `/etc/aqt/telegram` is intentionally owned and read by `aqt`; `ProtectSystem=strict` prevents service-time writes to `/etc`.
- `/etc/aqt/deployments.jsonl` is readable by `aqt`, but its write protection is not reliably established; S30-7.
- The system `safe.directory` entry permits the read-only Git checks against the root-owned checkout.
- The revised `sudo -u aqt` commands use absolute code paths and `/var/lib/aqt` as their working directory; no broken relative-path command was found.
- No `aqt`-writable code, interpreter, Git metadata, or configuration is later executed by root. The deployment record is the remaining `aqt`-writable trust input under a permissive umask.

## CI acceptance evidence

The quoted run `37036463907` proves:

- installation on fresh Ubuntu 24.04;
- root ownership of the sampled checkout, Git directory, and interpreter;
- inability of `aqt` to create files in `scripts`, `.git/refs`, `.venv/bin`, and `/etc/aqt`;
- approval and a successful clean-checkout command;
- systemd unit verification;
- an actual service start with a modified runner;
- exit status 2, `NRestarts=0`, and an operations-log `REFUSE_START`.

It does **not** prove:

- that the deployment record created after the ownership step is non-writable by `aqt`;
- that other kinds of modified tracked input, particularly an invalid configuration, reach the same logged exit-2 path;
- a successful unmodified service run, which remains honestly deferred because the exploration data is not installed in this job.

Therefore it proves its specific modified-runner scenario, but not the full ownership claim or the general modified-file refusal invariant.

## T30 dispositions

| ID | Result |
| --- | --- |
| **T30-01** | **Does not hold.** The approval record is non-cryptographic and is not reliably root-write-only because its creation mode is umask-dependent. |
| **T30-02** | **Holds after repair.** `origin/main` is inside root-owned Git metadata. |
| **T30-03** | **Holds after repair.** The service cannot modify its code during the run; checking only at start is consistent with that boundary. |
| **T30-04** | **Incomplete.** The actual-service CI scenario is materially improved, but malformed modified config bypasses logged exit-2 refusal. |
| **T30-05** | **Holds as disclosed.** CI’s synthetic `main` is explicitly dry-run-only. |
| **T30-06** | **Holds.** Forward paper and boot enablement remain explicitly gated on Task 29. |

## Commands and validation

Key commands run:

```text
rtk git status --short --untracked-files=all
rtk git branch --show-current
rtk git rev-parse HEAD
rtk git log -5 --oneline --decorate
rtk git show --no-patch --format=fuller 57a3b40
rtk git diff --stat 3c41f70 57a3b40
rtk git diff --name-status 3c41f70 57a3b40
rtk git diff --check 3c41f70 57a3b40
rtk git diff --no-ext-diff --unified=80 3c41f70 57a3b40 -- <reviewed files>
rtk git show 57a3b40:<file>
rtk git grep -n ... 57a3b40 -- <reviewed files>
rtk git diff --quiet 3c41f70 57a3b40 -- docs protocols schemas specs FROZEN_HASHES.json
rtk git diff --name-only 3c41f70 57a3b40 -- "*.sha256"
```

Targeted tests could not initialize because the managed read-only environment had no usable temporary directory:

```text
rtk .venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests/unit/test_deployment.py
FileNotFoundError: No usable temporary directory found
```

Read-only checks passed:

```text
rtk .venv\Scripts\ruff.exe check --no-cache <changed Python files>
All checks passed!

rtk .venv\Scripts\ruff.exe format --check --no-cache <changed Python files>
4 files already formatted

git diff --quiet ... frozen paths
exit 0
```

No frozen file or SHA-256 sidecar differs between `3c41f70` and `57a3b40`. The author’s quoted Linux results—1758 passed, 7 skipped, plus lint, types, imports, frozen verification, and the CI dry run—were considered as supplied and were not independently fetched.

Final Git status remained clean. No repository file was created or modified. No network, credentials, exchange APIs, confirmation data, lockbox data, or credential store was accessed.

Because repository policy requires the review record itself to be committed, this message must be preserved verbatim in the repository and committed before the section 16 review is considered recorded.