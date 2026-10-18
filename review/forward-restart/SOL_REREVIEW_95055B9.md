<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-18. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a14faf-d106-79c1-8af0-88206bc7ae5e. Tokens used: 17,286. Packet built from restart-wait-proposal 95055b9 (git show only): prompt SOL_REREVIEW_PROMPT.md, SOL_REVIEW_56DFCF0.md, PROPOSAL.md, scripts/run_forward_paper.py. -->

# Sol re-review of the F-RESTART proposal at 95055b9

## Review (final message, verbatim)

**Verdict: FIX.** FR-2 through FR-4 are addressed in the revised proposal. FR-1 is clear in the examples, but the scheduling instruction still conflicts with them.

**FRR-1 — The proposed first-wait calculation is ambiguous at :00.** The proposal says a 14:00:30 start waits 30 seconds, yet describes the target as “the next hour plus `STEP_OFFSET`.” The existing loop calculates exactly that and would wait until **15:01**, skipping the 14:01 slot. That would delay the first check and potentially add another pending hour.

Specify **the next occurrence of HH:01 UTC**: use the current hour’s :01 if startup setup finishes before it, otherwise the following hour’s :01. Require boundary tests for both 14:00:30 → 14:01 and 14:01:10 → 15:01, with `--once` still immediate.

This is a proposal review based on the supplied attachments; I did not run code.

## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-18)

| ID | Decision | Change to the proposal |
|---|---|---|
| FRR-1 | Agree | The target is the next occurrence of HH:01 UTC (this hour's :01 if set-up finishes before it); boundary tests 14:00:30 -> 14:01, 14:01:10 -> 15:01, and `--once` immediate are required. |

No finding is left unrepaired.
