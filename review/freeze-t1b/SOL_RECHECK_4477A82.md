# Sol re-check of 4477a82 (repair of T1BF-S-1)

- Reviewer: Codex `gpt-6-sol`, reasoning effort high, `codex exec -s read-only` (run log: `model: gpt-6-sol`), 2026-11-01.
- Prompt: diff 3ba1bef..4477a82 (IDs T1BFR-S-n).
- Verdict: **ACCEPT WITH NOTES** (T1BFR-S-1, note).

## Report (verbatim)

What this change does: `CODE=""` now runs before command dispatch. An inherited `CODE` is cleared before `engine()` chooses the `/app` mount. I checked that behavior with an inherited `/wrong` value; the mount resolved to `/opt/aqt-d19/app:/app:ro`.

**T1BFR-S-1 (note):** The added test checks the launcher’s source text but does not execute the inherited-variable case. The repair closes T1BF-S-1, and I found no new defect in the changed lines.

**Verdict: ACCEPT WITH NOTES.** This read-only re-check has not been written and committed as a review record, as the repository requires.

## Adjudication

- T1BFR-S-1 (note): accepted and repaired in the commit that records this: `tests/unit/test_d19_deploy.py` now runs the launcher preamble under `sh` with `CODE=/wrong` in the environment and asserts the mount source is `/opt/aqt-d19/app`. Not re-reviewed (test-only).
- No finding left unrepaired.
