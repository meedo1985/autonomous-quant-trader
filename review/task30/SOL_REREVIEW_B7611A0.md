# Task 30 Sol High second re-review of `b7611a0` — FIX

Date: 2026-10-02. Requested by the owner (re-review after the repairs of
`SOL_REREVIEW_57A3B40.md`).

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < review/task30/SOL_PROMPT_B7611A0.md`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; sandbox read-only;
  reasoning effort high; session id `01a0fda4-5297-7860-8abe-d4e119134c62`;
  tokens used 141,154; exit 0.
- Checkout HEAD at run time: `4174efc`. Prompt SHA-256:
  `6c914256f7e545d53b77c9cc2e718b946a666c5df3234a8a6dabd1d301ccbbbf`.
- Findings: S30-4 CORRECT; S30-7 INCORRECT (BLOCKER remains open); S30-8
  INCOMPLETE (see S30-9); new S30-9 BLOCKER. The author's dispositions
  follow in `LOCAL_REPORT.md`.

Below is the reviewer's final message, verbatim.

---

# Task 30 independent adversarial second re-review

**Reviewer model:** GPT-5.6 Sol, high effort, as session-designated. No separate runtime-model metadata endpoint was available for independent verification.  
**Implementation model:** Claude Opus 5.5, as supplied.  
**Reviewed commit:** `b7611a0a01492517636a375588539d492b923394`  
**Repair base:** `57a3b4071e3ab9934ea76d9c71ec7a981c2d2c30`  
**Verdict:** **FIX**  
**Gate:** **BLOCKED**

The checkout was at `4174efc`, containing only later review material. Implementation analysis was commit-anchored to `b7611a0`. The worktree remained clean.

## Previous findings

| ID | Result | Evidence |
| --- | --- | --- |
| **S30-4** | **CORRECT** | `.github/workflows/ci.yml:60-72` now damages a tracked configuration, starts the real systemd service, and requires exit 2, zero restarts, and the fixed-log refusal. The supplied CI run `37038667542` passed this scenario. This closes the original CI-evidence defect, although S30-9 exposes a separate persistent-log failure not covered by CI. |
| **S30-7** | **INCORRECT** | `approve()` appends first at `src/aqt/core/deployment.py:47-52`, through `open(target, "ab")` at `src/aqt/core/ledger.py:411`, and only afterward applies mode `0644` at `deployment.py:53`. Under a permissive umask, a new record is temporarily writable; an already-wide record remains writable throughout the append. An `aqt` process can open and retain a writable descriptor before `chmod`; changing mode does not revoke an existing descriptor. It can subsequently replace the ledger with a recomputed valid chain while the pathname reports mode `0644`, which passes `approved_code()`’s check at lines 67-69. The previous **BLOCKER remains open** and T30-01 is reopened. |
| **S30-8** | **INCOMPLETE** | The ordering defect is repaired: `approved_code()` runs at `scripts/run_paper_trading.py:59-60`, while `load_config()` is at line 77. A malformed or deleted tracked configuration is therefore detected by Git before parsing. No configuration, market data, network channel, or other application input is read before the check; only protected imports, arguments, the deployment record, and Git state are read. However, the new fixed refusal logger can raise before line 76’s `return 2`; see S30-9. |

### S30-7 scenario trace

The lock sidecar itself is created with a maximum mode of `0644` at `src/aqt/core/ledger.py:348`; a permissive umask cannot widen it. CI also proves the fresh sidecar’s final state is not writable by `aqt`.

That does not close the record race. The lock is advisory and does not stop an attacker using a retained descriptor to the record itself.

Scratch-free call-order probe:

```text
@'<probe replacing append_entry and chmod with event recorders>'@ |
  rtk .venv\Scripts\python.exe -B -

['append_completed_before_mode_fix', 'chmod_644']
```

The actual POSIX descriptor race was not executed because this review ran on Windows, but the security-relevant ordering and the underlying `open(..., "ab")` creation mode are explicit in the reviewed code.

## New findings

### S30-9 — BLOCKER — A damaged refusal ledger turns deployment refusal into a restartable crash

**Location:** `scripts/run_paper_trading.py:62-76`, `src/aqt/monitoring/alerts.py:213,233`, `src/aqt/core/ledger.py:392-396`, `deploy/aqt-paper.service:17-18`

**Concrete scenario:**

1. A previous interrupted write leaves `<out>/deployment_refusals.jsonl` with a torn or otherwise damaged final entry. This is an explicitly supported ledger failure state.
2. A later start has an unapproved or modified checkout.
3. The handler creates the output directory and emits the refusal through `LedgerSink`.
4. `append_entry()` detects the damaged ledger and raises `LedgerError`.
5. `AlertRouter` deliberately propagates sink failures. The runner does not catch this error, so line 76’s `return 2` is never reached.
6. The process exits as a crash rather than status 2. `Restart=on-failure` retries it because only status 2 is excluded.

The `StreamSink` is ordered first, so under normal systemd operation the refusal should still reach the journal before the ledger exception. It is absent from the runbook’s required fixed refusal file, and the service enters a restart loop.

**Reproduced:** **Yes, scratch-free exception-flow reproduction.**

```python
m.approved_code = lambda *a: (_ for _ in ()).throw(
    m.DeploymentError("unapproved")
)
m.Path.mkdir = lambda *a, **k: None
m.AlertRouter.emit = lambda *a, **k: (_ for _ in ()).throw(
    LedgerError("damaged refusal ledger")
)
m.main([
    "--config", "missing.toml",
    "--out", "state",
    "--deployment-record", "record",
])
```

Command and output:

```text
@'<probe above>'@ | rtk .venv\Scripts\python.exe -B -

uncaught=LedgerError: damaged refusal ledger
```

The minimal correction is to handle refusal-sink failure on this path, preserve the journal diagnostic, and still return status 2.

## Requested operational conclusions

- The fixed refusal path is under service-writable state. `StateDirectory=aqt` and `WorkingDirectory=/var/lib/aqt` make the default path `/var/lib/aqt/data/processed/paper/deployment_refusals.jsonl`.
- A fresh, writable, intact refusal ledger records the event and returns 2.
- A damaged refusal ledger crashes before returning 2; S30-9.
- A deleted or unparseable tracked configuration is checked as a Git change before configuration parsing.
- The scratch-free ordering probe returned:

```text
rc=2 events=['approved_code', 'mkdir', 'emit']
```

No `load_config` call occurred.
- `run_paper()` still performs its own deployment check at `src/aqt/app/paper_loop.py:595-599`; a successful start records the resulting commit and package-source hash at lines 664-667.
- CI proves final-state non-writability of both the record and lock for its fresh Ubuntu run. It does not test the transient record window, an existing wide record during approval, or a pre-damaged refusal ledger.

## T30 dispositions

| ID | Result |
| --- | --- |
| **T30-01** | **Does not hold.** S30-7 remains open: record permissions are only repaired after append, leaving the approval authority temporarily writable and allowing retained-descriptor access. |
| **T30-02** | **Holds.** The protected `origin/main` disposition is unchanged. |
| **T30-03** | **Holds.** The root-owned checkout remains non-writable by `aqt`; no repair reopens this boundary. |
| **T30-04** | **Holds for its original acceptance-evidence issue.** CI now starts and observes the real service on a broken tracked configuration. The broader “every refused start exits 2 without retry” claim is blocked by S30-9. |
| **T30-05** | **Holds as disclosed.** CI’s synthetic `main` remains explicitly dry-run-only. |
| **T30-06** | **Holds.** Forward paper and boot enablement remain gated on Task 29. |

S30-1, S30-3, and S30-5 remain correct. The S30-2 and S30-6 dispositions remain valid. No quant/statistical behavior changed; quant-only review areas are N/A.

## Validation and commands

Key commands run:

```text
rtk git status --untracked-files=all --short
rtk git rev-parse HEAD
rtk git branch --show-current
rtk git show --no-patch --format=fuller b7611a0
rtk git diff --stat 57a3b40 b7611a0
rtk git diff --name-status 57a3b40 b7611a0
rtk git diff --check 57a3b40 b7611a0
rtk git diff --no-ext-diff --unified=80 57a3b40 b7611a0 -- <reviewed files>
rtk git show b7611a0:<file>
rtk git grep -n <pattern> b7611a0 -- <reviewed files>
rtk git blame b7611a0 -L <range> -- <file>
rtk git diff --quiet 57a3b40 b7611a0 -- docs protocols schemas specs FROZEN_HASHES.json
rtk git diff --name-only 57a3b40 b7611a0 -- "*.sha256"
rtk .venv\Scripts\ruff.exe check --no-cache src\aqt\core\deployment.py scripts\run_paper_trading.py tests\unit\test_deployment.py
rtk .venv\Scripts\ruff.exe format --check --no-cache <same files>
rtk .venv\Scripts\lint-imports.exe --no-cache
rtk .venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider tests\unit\test_deployment.py
rtk .venv\Scripts\mypy.exe --no-incremental src scripts
rtk powershell -NoProfile -ExecutionPolicy Bypass -File review\task6\verify_frozen.ps1
```

Results:

- Ruff lint: `All checks passed!`
- Ruff format: `3 files already formatted`
- Import boundaries: `6 kept, 0 broken`
- `git diff --check`: passed.
- No frozen path or SHA-256 sidecar changed between the repair base and target.
- Pytest could not initialize: `FileNotFoundError: No usable temporary directory found`.
- Mypy could not create its metadata cache in the read-only environment; the diagnostic was environmental rather than a reported type error.
- The frozen verifier could not run under Windows PowerShell because its .NET runtime lacks `Convert.ToHexString`. The author’s quoted local and CI frozen-verification passes were considered as supplied but not independently fetched.
- Supplied CI run `37038667542`: `1760 passed, 7 skipped`; runbook dry run passed.
- Final worktree status was clean.

No repository files were created or modified. No network, credentials, exchange APIs, confirmation/lockbox data, or credential store were accessed.

This review remains incomplete as a Constitution §16 record until this final message, including the unresolved S30-7 and S30-9 findings, is preserved and committed.