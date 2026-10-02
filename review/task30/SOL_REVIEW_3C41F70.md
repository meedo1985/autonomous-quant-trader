# Task 30 Sol High review of `3c41f70` — FIX

Date: 2026-10-02. Requested by the owner ("yes start the review with Sol High").

- Invocation: `codex exec -s read-only -m gpt-5.6-sol -c model_reasoning_effort=high -o <last> - < review/task30/SOL_PROMPT_3C41F70.md`
- Log header: OpenAI Codex v0.157.1; model `gpt-5.6-sol`; provider openai;
  approval never; sandbox read-only; reasoning effort high; session id
  `01a0fd61-9245-7522-b1dc-a150ac7c128e`; tokens used 174,545; exit 0.
- Checkout HEAD at run time: `a437872` (`3c41f70` plus the prompt). Prompt
  SHA-256: `b26b27d29843bf0bbeaed6dc12575f24d0ae35ee64b15a8f2f8b20427509196a`.
- Findings: S30-1..S30-4 BLOCKER, S30-5, S30-6 NON-BLOCKING. The author's
  dispositions follow in `LOCAL_REPORT.md`.

Below is the reviewer's final message, verbatim.

---

# Task 30 independent adversarial review

**Reviewer model:** GPT-5.6 Sol, high effort, as session-designated. The interface exposed no separate runtime-model metadata endpoint for independent verification.  
**Implementation model:** Claude Opus 5.5.  
**Reviewed commit:** `3c41f7092ef1757acec82905102ebf92189d0f4e`  
**Base:** `56b3ee4`  
**Verdict:** **FIX**  
**Gate:** **BLOCKED**

## Findings

### S30-1 — BLOCKER — The `aqt` account controls the code and interpreter that root later executes

**Location:** `deploy/install.sh:15-18`, `deploy/RUNBOOK.md:42`, `deploy/RUNBOOK.md:92-94`, `deploy/aqt-paper.service:12,17`

**Concrete scenario:** Installation clones the repository and creates the editable virtualenv as `aqt`. Therefore `aqt` owns:

- `scripts/deployment.py`
- `src/aqt`
- `.venv/bin/python`
- `.git`

The runbook later executes the account-owned interpreter and script as root:

```sh
sudo /opt/aqt/app/.venv/bin/python -B \
  /opt/aqt/app/scripts/deployment.py approve ...
```

A compromised `aqt` account can replace either the interpreter or script before the owner runs this command. Its code then runs as root and can write its own approval, alter `/etc/aqt`, or compromise the server. Independently, `ReadWritePaths=/opt/aqt` lets the running service modify its own executable code and virtualenv.

`ProtectSystem=strict` does not help because `/opt/aqt` is explicitly made writable.

**Reproduced:** No exploit executed because this review is read-only on Windows. Static evidence:

```text
deploy/install.sh:15 sudo -u aqt git clone ...
deploy/install.sh:17 sudo -u aqt python3 -m venv ...
deploy/install.sh:18 sudo -u aqt .../pip install -e ...
deploy/RUNBOOK.md:42 sudo /opt/aqt/app/.venv/bin/python ... approve
deploy/aqt-paper.service:17 ReadWritePaths=/opt/aqt
```

**Required correction:** Make the checkout, `.git`, virtualenv, deployment tool, and interpreter root-owned and non-writable by `aqt`. Run updates through root or a separate deployment identity. Give `aqt` write access only to dedicated state/output directories, preferably under `/var/lib/aqt`. Never execute `aqt`-writable code through `sudo`.

---

### S30-2 — BLOCKER — Approval enforcement is optional and runs after unverified code has executed

**Location:** `scripts/run_paper_trading.py:20,46-50,78`, `src/aqt/app/paper_loop.py:595-599`, `src/aqt/core/code_identity.py:201-223`

**Concrete scenarios:**

1. `--deployment-record` is optional. Running the script without it passes `deployment=None`, so `approved_code()` is never called.
2. Python imports `aqt` modules before `main()` and before the identity check. Therefore the checker cannot establish that the code already executing is approved.
3. Ignored `__pycache__/*.pyc` files are explicitly accepted. An `aqt`-owned, unchecked-hash `.pyc` can execute during imports while the working source and Git status remain clean. The start event can then report the approved commit and committed source hash even though different bytecode executed.
4. The ignored `.venv` is itself the interpreter/runtime and is not covered by the checkout check.

**Reproduced:** Yes, scratch-free probe of the ignored-bytecode rule:

```text
rtk .venv\Scripts\python.exe -B -c "... c._require_clean(Path('.')) ..."
exit 0
ignored executable pyc accepted
```

**Required correction:** The deployed entry point must enforce approval unconditionally and before application imports or mutable runtime code. Combined with S30-1, use a protected launcher/runtime and reject executable ignored artifacts. Do not provide an unguarded server execution path merely by omitting a flag.

---

### S30-3 — BLOCKER — “On `origin/main`” is controlled by the account being checked

**Location:** `src/aqt/core/deployment.py:78-79`, `deploy/install.sh:15-16`, `deploy/RUNBOOK.md:92-94`

**Concrete scenario:** Suppose the owner accidentally approves a valid full SHA that was not merged to GitHub `main`. Because `aqt` owns `.git`, it can run:

```sh
git update-ref refs/remotes/origin/main <approved-sha>
```

`git merge-base --is-ancestor <approved-sha> origin/main` then succeeds. The checkout is accepted even though the commit was never on the authoritative remote `main`.

This directly defeats the roadmap’s “reviewed commit on `main`” requirement. Exact owner approval remains a separate control, but the second required predicate is not enforced.

**Reproduced:** No throwaway repository could be created in the read-only sandbox. Static trace confirms both the account ownership and reliance on its local ref.

**Required correction:** Protect `.git` from `aqt`. Fetch and update the remote-tracking reference only through the owner/deployment identity, then perform the offline check against that protected ref.

---

### S30-4 — BLOCKER — CI does not prove “a modified file refuses start” or dry-run the stated runbook

**Location:** `.github/workflows/ci.yml:28-52`, `deploy/RUNBOOK.md:5-7`, `tests/unit/test_deployment.py:124-143`

**Concrete scenario:** The CI job:

- runs `install.sh`;
- invokes `scripts/deployment.py check`;
- syntax-checks the unit;
- modifies a script and invokes `scripts/deployment.py check` again.

It never calls `systemctl start aqt-paper`, never observes service exit status 2, and never verifies a logged `REFUSE_START`. Consequently, a broken unit argument, optional-gate bypass, writable interpreter, or service-only path could pass CI. S30-1 and S30-2 do pass the current dry run.

The runbook also says CI repeats steps 2–4, but Telegram/data step 4 is not run.

**Reproduced:** Yes:

```text
.github/workflows/ci.yml:46 ... scripts/deployment.py check
.github/workflows/ci.yml:48 systemd-analyze verify ...
.github/workflows/ci.yml:52 ... scripts/deployment.py check
```

There is no service-start command in the job.

**Required correction:** On Ubuntu CI, assert immutable ownership first, start the actual unit with a modified tracked file, and verify exit status 2 plus the expected refusal record. Either exercise the remaining claimed runbook steps or narrow the documented dry-run claim.

---

### S30-5 — NON-BLOCKING — Credential-file symlinks are accepted

**Location:** `src/aqt/monitoring/telegram.py:178-194`

**Concrete scenario:** `Path.stat()` and `Path.read_text()` both follow symlinks. A symlink whose target is owned by the effective account and mode `0600` is accepted.

The prescribed `/etc/aqt` directory is root-owned mode `0755`, so `aqt` cannot normally replace the directory entry; this limits the deployed exploitability. Nevertheless, the credential reader itself does not enforce the requested symlink property.

**Reproduced:** Yes, scratch-free behavioral probe:

```text
is_symlink= True accepted_chat= 42 token_length= 15
```

**Required correction:** Open with `O_NOFOLLOW`, require a regular file using `fstat`, and read from that same descriptor to avoid a check/read race.

No token exposure was found in the credential error paths: failures report the path, error class, or generic format requirement, not credential contents.

---

### S30-6 — NON-BLOCKING — The logged source hash is package-only and does not identify the runtime

**Location:** `src/aqt/core/code_identity.py:49,257-297`, `src/aqt/app/paper_loop.py:664-666`, `pyproject.toml:9-13`, `deploy/install.sh:18`

**Concrete scenario:** `source_sha256` covers only `src/aqt/`. Two approved commits differing only in `scripts/run_paper_trading.py`, a configuration, the systemd unit, or installation code have different commit IDs but the same `source_sha256`.

Additionally, editable installation resolves version ranges. Reinstalling the same commit later can produce different dependency versions while logging the same commit and source hash. The existing environment fingerprint is not logged.

**Reproduced:** Yes, static definition:

```text
COVERED_PREFIX: Final[str] = "src/aqt/"
```

**Required correction:** Either rename/document this as a package-source hash and make the commit the authoritative whole-tree identity, or hash the complete executable deployment surface and record a locked environment identity.

## Requested edge-case conclusions

- Modified, staged, added, or ordinary untracked files: refused.
- `assume-unchanged` / `skip-worktree`: refused.
- Different HEAD from newest approval: refused.
- Missing, empty, damaged, or malformed approval record: fails closed.
- Invalid approval strings: rejected before append.
- `.venv`, `data/`, normal `__pycache__`, editable install, and normalized line endings do not wrongly refuse a correct checkout.
- Ignored executable bytecode/runtime: wrongly accepted; S30-2.
- Commit not really on authoritative `main`: can be accepted by rewriting the account-owned remote ref; S30-3.
- Deployment refusals inside `run_paper` are emitted as CRITICAL startup events. Systemd also captures stderr in the journal.
- With deployment enforcement active and uncompromised, the start event records full HEAD and the package-source hash. S30-2 and S30-6 limit that assurance.
- `RestartPreventExitStatus=2` correctly prevents retries of exit 2. `Restart=on-failure` still retries other failures.
- Intended output paths are writable under `ProtectSystem=strict`, but `ReadWritePaths=/opt/aqt` is dangerously broader than required.

## T30-01 through T30-06

- **T30-01:** disposition does not hold. Root-only record permissions are defeated by invoking an `aqt`-owned interpreter/script as root.
- **T30-02:** the disclosed fact is true, but the disposition is insufficient; local `origin/main` is not an authoritative second check.
- **T30-03:** does not hold. Ownership by `aqt` is the central trust-boundary failure, and `ProtectSystem` explicitly allows writes to `/opt/aqt`.
- **T30-04:** does not hold as acceptance evidence. Neither CI nor the cited loop test starts the actual service from a modified checkout.
- **T30-05:** factually accurate disclosure, but it does not test authoritative `main` membership.
- **T30-06:** holds. The unit currently replays and exits; boot enablement remains expressly gated on Task 29.

## Validation and commands

Key commands run:

```text
rtk git status --short --branch --untracked-files=all
rtk git diff --stat
rtk git diff --cached --stat
rtk git diff --name-status 56b3ee4 3c41f70
rtk git diff --check 56b3ee4 3c41f70
rtk git diff --quiet 56b3ee4 3c41f70 -- docs protocols schemas specs FROZEN_HASHES.json
rtk git diff --name-only 56b3ee4 3c41f70 -- "*.sha256"
rtk git log --oneline --decorate --graph -12 3c41f70
rtk git show --no-patch --format=fuller 3c41f70
rtk git cat-file -t 3c41f70
rtk git cat-file -t 56b3ee4
rtk git merge-base --is-ancestor 56b3ee4 3c41f70
```

I read the requested records and every changed implementation file using commit-anchored `rtk git show`, `git diff`, `git grep`, and `git blame`, including the Constitution, protocol, threat model, deployment draft, relevant skills, code-identity helper, ledger, tests, unit, installer, runbook, and CI job.

Frozen verification:

```text
PASS: 28/28 trusted bytes; 14/14 sidecars; self-hash;
7/7 bindings; nested bindings
```

Targeted pytest could not start because the managed read-only environment has no writable temporary directory:

```text
FileNotFoundError: [Errno 2] No usable temporary directory found
```

Scratch-free probes passed and reproduced the ignored-PYC and symlink findings. Final Git status was clean; no files were created or modified. No network, credentials, exchange APIs, confirmation data, lockbox data, or credential store were accessed.

Because repository policy requires the review record to be committed, this message must be copied verbatim into the repository and committed before the section 16 review is considered preserved.