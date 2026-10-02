# Task 30 Sol High third re-review of `ca68eee` — FIX

Date: 2026-10-02. Requested by the owner ("yes go ahead").

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < review/task30/SOL_PROMPT_CA68EEE.md`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a0fdba-8e54-7bf2-b490-c3eaa7b33080`;
  tokens used 113,746; exit 0.
- Checkout HEAD at run time: `b3f8e76`. Prompt SHA-256:
  `a607fe039121f8a061b0c24b0a92a36a1af761a52b91c2baf329fe7004e3a041`.
- Findings: S30-7 CORRECT; S30-8 INCOMPLETE; S30-9 INCOMPLETE (BLOCKER
  remains open); new S30-10 NON-BLOCKING. The author's dispositions follow in
  `LOCAL_REPORT.md`.

Below is the reviewer's final message, verbatim.

---

# Task 30 independent adversarial third re-review

**Date:** 2026-10-02  
**Reviewer model:** GPT-5.6 Sol, high effort, as session-designated. No independent runtime-model metadata endpoint was exposed.  
**Implementation model:** Claude Opus 5.5, as supplied.  
**Reviewed commit:** `ca68eee23dd82a6091978c038bb499584b03ca1e`  
**Repair base:** `b7611a0a01492517636a375588539d492b923394`  
**Verdict:** **FIX**

The checkout was at `b3f8e76155837184116f24c8d811d00368e7efca`, containing only later review/report material. `git diff --exit-code ca68eee HEAD` passed for all implementation, deployment, and CI paths, so the review remained commit-anchored to `ca68eee`.

## Previous findings

| ID | Result | Evidence |
| --- | --- | --- |
| **S30-7** | **CORRECT** | `approve()` checks existing permissions before append at `src/aqt/core/deployment.py:47-51`. A fresh record is created at lines 52-55 with `O_CREAT\|O_EXCL\|O_WRONLY` and requested mode `0644` before `append_entry()` runs. A permissive umask cannot widen that mode. An existing group/world-writable record is neither opened nor appended to, and `approved_code()` also rejects it at lines 82-83. The lock sidecar is created with maximum mode `0644` at `src/aqt/core/ledger.py:348`. Therefore a new `aqt` writable descriptor cannot be acquired; a retained descriptor to an existing wide record does not help because that pathname remains refused. The prescribed recovery—move the inode aside and create a new record—also leaves any legacy descriptor referring only to the discarded inode. No server or legacy production record exists for this task. |
| **S30-8** | **INCOMPLETE** | The ordering repair is correct: `approved_code()` runs at `scripts/run_paper_trading.py:59-60`; `load_config()` is not reached until line 84. The probe returned `ordering_rc=2 events=['approved_code', 'mkdir', 'emit']`, with no configuration read. However, the guarantee that the refusal is logged and exits 2 remains incomplete because S30-9 still has an escaping fallback exception. |
| **S30-9** | **INCOMPLETE — BLOCKER remains open** | The new handler correctly catches failures creating or appending the fixed refusal log and, with working stderr, returns 2. But its fallback `print()` at `scripts/run_paper_trading.py:79-82` is outside another guard. If the refusal ledger is damaged/unwritable and stderr also raises—e.g. the journal stream is unavailable—the exception escapes before line 83. `deploy/aqt-paper.service:17-18` then treats it as a restartable failure rather than excluded status 2. The new test at `tests/unit/test_deployment.py:244-264` covers a damaged ledger only while stderr works. |

### S30-9 reproduction

Scratch-free probe:

```text
@'<patch approved_code to refuse; make output mkdir and stderr raise>'@ |
  rtk .venv\Scripts\python.exe -B -
```

Output:

```text
fallback_rc=2
broken_stderr_uncaught=OSError: stderr unavailable
```

Thus the common damaged/unwritable-log case is repaired, but not “any exception on the refusal path before `return 2`.”

## New finding

### S30-10 — NON-BLOCKING — Restrictive umask makes the record unreadable by `aqt`

**Location:** `src/aqt/core/deployment.py:52-55`; `deploy/RUNBOOK.md:45-49`

**Concrete scenario:** Root runs the approval command with umask `077`, a normal hardened setting. POSIX applies the umask to the requested `0644` mode, creating the record as `0600`. Because the previous after-append `chmod(0644)` was removed, the mode remains `0600`. The root approval succeeds, but the immediately prescribed `sudo -u aqt ... check` and the service cannot read the record, so a correct approved checkout is refused.

This does not permit unauthorized execution and does not reopen S30-7’s write-protection defect; it is an availability/runbook regression introduced by the repair.

**Reproduced:** **No actual POSIX execution**; the host is Windows and WSL is unavailable. Scratch-free call/mode evidence:

```text
fresh_flags_create=True excl=True write=True mode=0o644
posix_result_mode_if_umask_077=0o600
```

A safe correction is to retain the exclusive descriptor, apply `fchmod(fd, 0o644)`, then close it before appending. That adds only read permissions and creates no writable window.

No other new finding was identified.

## Earlier findings and T30 dispositions

- **S30-1:** remains correct. Code, Git metadata, and interpreter remain root-owned.
- **S30-2:** disposition remains valid; the root-owned service always supplies the deployment record.
- **S30-3:** remains correct; protected Git metadata still controls `origin/main`.
- **S30-4:** remains correct for its narrow CI acceptance-evidence defect: the quoted CI scenario starts the actual service against a damaged tracked configuration. It is not proof that every refusal avoids restart; S30-9 remains open.
- **S30-5:** remains correct.
- **S30-6:** disclosed limitation remains unchanged.

T30 dispositions:

| ID | Result |
| --- | --- |
| **T30-01** | **Holds.** S30-7’s security defect is closed. A restrictive umask makes the record less accessible, not writable by `aqt`. |
| **T30-02** | **Holds.** Protected `origin/main` handling is unchanged. |
| **T30-03** | **Holds.** The checkout remains non-writable by `aqt`. |
| **T30-04** | **Holds for the original dry-run evidence issue.** The broader refusal/no-retry claim remains blocked by S30-9. |
| **T30-05** | **Holds as disclosed.** CI’s synthetic `main` remains dry-run-only. |
| **T30-06** | **Holds.** Forward paper and boot enablement remain gated on Task 29. |

The author’s categorical disposition that S30-9 and, through it, S30-8 are closed does not hold.

## Validation

Passed:

```text
git diff --check b7611a0 ca68eee -- . ':(exclude)review/**'
git diff --exit-code ca68eee HEAD -- <implementation/deploy/CI paths>
git diff --exit-code b7611a0 ca68eee -- docs protocols schemas specs FROZEN_HASHES.json
git diff --name-only b7611a0 ca68eee -- '*.sha256'
ruff check --no-cache .
ruff format --check --no-cache .
lint-imports --no-cache
```

Results:

```text
Ruff: All checks passed
Format: 114 files already formatted
Import contracts: 6 kept, 0 broken
Frozen-path repair diff: empty
Final worktree: clean
```

Unavailable in the read-only environment:

```text
pytest -q -p no:cacheprovider tests/unit/test_deployment.py
```

failed before collection with:

```text
FileNotFoundError: No usable temporary directory found
```

`mypy --no-incremental --cache-dir=NUL src scripts` returned a mypy internal error. The frozen PowerShell verifier also could not run because this PowerShell/.NET runtime lacks `Convert.ToHexString`. The author’s quoted local and CI results—including CI run `37041961014`—were treated as supplied and were not independently fetched.

Principal inspection commands also included commit-anchored `rtk git show`, `git diff`, `git grep`, and `git log` over the three repair files, ledger implementation, runbook, unit, CI, prior review records, local dispositions, roadmap acceptance criteria, Constitution, protocol, threat model, cost model, and backtester specification.

No repository file was created or modified. No network, credentials, exchange APIs, confirmation/lockbox data, or credential store was accessed.

**Final verdict: FIX.** S30-9 remains a blocker; S30-8 consequently remains incomplete.