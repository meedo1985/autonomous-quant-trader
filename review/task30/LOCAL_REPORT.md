# Task 30 local report: server runbook and code identity

Author: Claude Opus 5.5 (`claude-opus-5-5`), 2026-10-02, Ponytail full
(owner's request). Branch `task30-runbook-design` (design `fcd9f4d`, then
`main` `56b3ee4` merged in). Design `DESIGN.md`; owner answers Q30-1 Ubuntu,
Q30-2 only the approved commit, Q30-3 manual updates, Q30-4 GitHub test
machine, in `OWNER_ANSWERS.md`. Closes T24-03 and T28-06.

## Changes

| File | What |
| --- | --- |
| `src/aqt/core/deployment.py` (new) | `approve` appends the owner's approval (full commit id, name, statement) to a hash-chained record; `approved_code` refuses unless the checkout is exactly the newest approved commit: on `origin/main`, nothing modified, untracked or masked anywhere in the checkout, and `src/aqt` equal to its committed bytes (reuses `aqt.core.code_identity.git_source_bundle`). |
| `src/aqt/app/paper_loop.py` | Optional `deployment` record: a failed check is a logged REFUSE_START; the start event records the commit and the source hash. |
| `src/aqt/monitoring/telegram.py` | `read_file_credential` for the server (`/etc/aqt/telegram`, chat id and token, refused unless readable by its owner only); `owner_channel` reads the store of the system it runs on. |
| `scripts/deployment.py` (new) | Owner commands `approve <commit> --by --statement` and `check`. |
| `scripts/run_paper_trading.py` | `--deployment-record`. |
| `deploy/RUNBOOK.md`, `deploy/install.sh`, `deploy/aqt-paper.service` (new) | The runbook (rent, install, approve, Telegram and data, start, logs, update, stop), the first-install script, the `systemd` unit (account `aqt`, never root, refused start not retried). |
| `.github/workflows/ci.yml` | Job `runbook-dry-run`. |
| `tests/unit/test_deployment.py` (new) | 16 tests on throwaway repositories. |

## Acceptance (roadmap 2, Task 30)

| Criterion | Evidence |
| --- | --- |
| A dry run of the runbook on a clean machine | CI job `runbook-dry-run` on a fresh `ubuntu-24.04` runner: `install.sh` (step 2), approve and check (step 3), `systemd-analyze verify` of the unit. Passed on GitHub (see below). |
| A modified file refuses start | `test_a_modified_checkout_refuses` (changed script, added file, changed `src/aqt` file, masked `skip-worktree` change); `test_the_loop_refuses_an_unapproved_checkout` (logged REFUSE_START, no order); the CI job's last step on the installed server copy. |
| Only a reviewed commit on `main` | `test_a_commit_not_on_main_refuses`, `test_only_the_newest_approval_counts`, `test_a_missing_or_damaged_record_refuses`, `test_an_approval_needs_a_full_commit_and_a_name`. |
| Logs say which code ran | `test_the_start_event_names_the_approved_code`. |
| Server credential store (T28-06) | `test_the_server_credential_file` (runs on Linux only: owner-only file accepted; group-readable and malformed refused, the token never in the error). |

## Findings

| ID | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| T30-01 | NON-BLOCKING | The approval is the owner's name and statement in a hash-chained record, not a cryptographic signature; it is protected by being writable by root only. | As the gap record (Q27-3). Whoever is root on the server can run anything anyway; a signed record can be added before real money. |
| T30-02 | NON-BLOCKING | "On `main`" is checked against `origin/main` as last fetched, which the `aqt` account could alter. | The binding check is the root-only approval of an exact commit; `main` is a second check. |
| T30-03 | NON-BLOCKING | The checkout is checked at start only; a file changed while the loop runs is found at the next start. | The service's files are owned by `aqt`, which runs no other program; ProtectSystem keeps the rest read-only. |
| T30-04 | NON-BLOCKING | The dry run does not start the service: the paper run needs the exploration data download, which is network work the owner runs. | The refusal path of the loop itself is tested (`test_the_loop_refuses_an_unapproved_checkout`); the CI job checks the installed copy and the unit. |
| T30-05 | NON-BLOCKING | In the dry run the PR's own commit stands in for `main` (a local branch in a bundle). | Dry run only; on the server `main` comes from GitHub. |
| T30-06 | QUESTION (Task 29) | Today the service replays the exploration data and stops; `systemctl enable` (start on boot) is marked for once Task 29 is authorized. | Forward paper is not authorized; nothing here authorizes it. |

## Validation (2026-10-02, Python 3.14.7, Windows 11, exit 0 each)

- `python -m pytest -q -p no:cacheprovider`: 1755 passed, 7 skipped (the
  three server credential-file cases are skipped on Windows; they run in
  CI on Linux).
- `ruff check .`: all passed, after wrapping one long test line.
  `ruff format --check .`: 114 files formatted (after formatting the new
  test file; its 16 tests rerun: 13 passed, 3 skipped).
- `mypy src scripts`: no issues, 60 source files.
- `lint-imports`: 6 kept, 0 broken.
- `git diff --check`: clean.
- Frozen verification (Python port of `review/task6/verify_frozen.ps1`):
  28/28 trusted bytes and exact inventory, 14/14 sidecars, Constitution
  self-hash, 7/7 manifest and protocol bindings, nested bindings.
- Task 25 drills rerun, identical to `review/task25/drills`.

CI on PR #40 at `021f51a` (run 37031449002): `checks` pass, and
`runbook-dry-run` pass on a fresh `ubuntu-24.04` runner. Its log:
"Installed 17fdaea...", "Approved 17fdaea...", "May run: 17fdaea...,
source 0a051a96...", `systemd-analyze verify` without error, then after one
appended line "Refused: checkout differs from its commit: ['M
scripts/run_paper_trading.py']". (`17fdaea` is GitHub's merge of the PR
into `main`.) The first run at `9b6f05f` failed before installing: the
runner's checkout had one commit only, so the bundle lacked history;
`021f51a` fetches the full history. Harmless warnings in the log: the
bundle names no HEAD branch (the script checks out the commit), and
`sudo -u aqt` cannot read the runner's own git config.

LOCAL GATE: PASS. Required before merge (section 16: the start check is
protocol-enforcement logic): independent different-model review, then the
owner's walkthrough.
