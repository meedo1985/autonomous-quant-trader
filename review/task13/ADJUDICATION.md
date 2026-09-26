# Task 13 review adjudication

Review: `review/task13/REVIEW.md`, saved unedited from the reviewer's reply.
Reviewer: GPT-6 Astra (`gpt-6-astra`, reasoning effort high), Codex CLI 0.154.0,
session `01a0dd26-7dd0-7723-b6b8-b346e366d00c`, read-only sandbox, 2026-09-26.
Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the implementing model.

## How the review was run

Two earlier attempts in a workspace-write sandbox (sessions
`01a0dd1f-7ba9-7f93-9294-a4c97a1b684f`, `01a0dd20-4113-7fc1-8f20-030328f37a16`)
produced no review: the Codex Windows sandbox failed to start
(`helper_unknown_error: setup refresh had errors`), so the reviewer could not
read files or run commands, and it said so rather than issuing a verdict.
The third run received the full `main...HEAD` diff and check output generated
by the implementer at `56da0aa` in its prompt, and used no tools. **The reviewer
did not rerun the checks itself**, and the review says so.

## Findings

| ID | Severity | Adjudication | Evidence |
|---|---|---|---|
| R-1 | BLOCKER | **Accepted.** | `_write_once` uses a fixed `<name>.part` path and `os.link` shares the inode, so a second concurrent writer's `write_bytes` truncates the just-published artifact before the first unlinks. Narrow (needs two runs on one root) but real, and it breaks section 6 immutability. |
| R-2 | BLOCKER | **Accepted.** | `fetch_monthly_klines` accepts any year and month; only the CLI loop limits months to `EXPLORATION_MONTHS`. A caller can fetch confirmation or lockbox months (2022 onward) into the same root. The guard belongs in the client. |
| R-3 | BLOCKER | **Accepted.** | `urllib_transport` uses `urlopen`, which follows redirects without re-validating the target, so the HTTPS host allow-list in `PublicRequest` covers only the first hop. |
| R-4 | BLOCKER | **Accepted; already recorded.** | Same as the merge blocker in `LOCAL_REPORT.md`: roadmap PR #13 is unapproved. It needs the owner's approval, not a code fix. |
| R-5 | NON-BLOCKING | **Accepted.** | `main()` writes the run summary only after every fetch returns; any raised `DownloadError` exits without one. |

No finding is rejected. R-1, R-2, R-3 and R-5 are to be repaired in a later
commit on this branch; R-4 stays open until the owner approves the roadmap.
