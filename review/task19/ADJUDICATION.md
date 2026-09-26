# Task 19 review adjudication

Review: `review/task19/REVIEW.md`, saved unedited from the reviewer's reply.
Reviewer: GPT-6 Astra (`gpt-6-astra`, reasoning effort high), Codex CLI 0.154.0,
session `01a0de2d-9e42-72c1-a27f-d723f0b13c4f`, read-only sandbox, no tools,
2026-09-26. Input: the full `main...HEAD` diff (including `LOCAL_REPORT.md`),
implementer-run check output at `44cc8ea`, and the unchanged `aqt.core.ledger`
source. The reviewer did not rerun the checks. Verdict: **FIX**.
Adjudicator: Claude Opus 5.5 (`claude-opus-5-5`), the implementing model.

| ID | Severity | Adjudication | Evidence |
|---|---|---|---|
| R-1 | BLOCKER | **Accepted, reproduced.** | A router with only `LedgerSink(path, Severity.CRITICAL)` emitting a CRITICAL event with `{"api_key": "credential"}` wrote one entry, kind `ORDER`: the WARNING-level `REDACTION` audit event was filtered out by the sink threshold. |
| R-2 | BLOCKER | **Accepted, reproduced.** | A field named `api_key=` followed by 64 `K`s had its value redacted, but the credential-shaped name reached a stream sink twice: as the field name and inside the `REDACTION` event. |
| R-3 | BLOCKER | **Accepted.** | T19-01 replaced the roadmap's rotating file with a single caller-chosen path, on the implementer's own judgment and without the owner's agreement. That is a scope change the implementer should not have made alone. |

Deviation T19-02 (health checks return events rather than routing them): the
reviewer accepts it. Agreed.

All three are repaired below.

## Repairs (Claude Opus 5.5, 2026-09-26)

| ID | Change | Regression test |
|---|---|---|
| R-1 | The `REDACTION` record takes the higher of WARNING and the original event's severity, so every sink that receives the event also receives the record. | `test_the_redaction_record_reaches_a_critical_only_log` |
| R-2 | A field whose **name** looks like a credential is renamed `redacted_field_<index>` with a `[REDACTED]` value; the audit record lists only the safe names. | `test_a_credential_shaped_field_name_never_reaches_a_sink` |
| R-3 | `RotatingLedgerSink` writes one hash-chained ledger file per UTC day. Every file after the first opens with a rotation record naming the previous file, its entry count and its verified head hash; a late timestamp never reopens an older file. `verify_rotated_log` checks every file and every link. | `test_the_log_rotates_daily_and_the_chain_continues`, `test_a_late_timestamp_never_reopens_an_older_file`, `test_damage_to_a_rotated_log_is_detected` (edited first file; deleted middle file) |

`LEDGER_RECORD_TYPE` and the single-file `LedgerSink` remain for callers that
want one file. T19-01 in `LOCAL_REPORT.md` is marked superseded.

Mutation check: with `alerts.py` from `016d136` restored (and a single-file
stand-in for the rotation API so the tests can import), the R-1, R-2 and three
of the four rotation tests fail. The edited-file case passes there too,
because the underlying ledger detects edits by itself.

Validation after repair, `.venv` Python 3.14.7: `pytest -q` 1295 passed, 4 skipped in 63.02s (0:01:03);
ruff, format, mypy and `lint-imports` pass; `git diff --check main...HEAD`
clean (after commit); no change under the frozen paths.

These repairs have not been re-reviewed by a different model.
