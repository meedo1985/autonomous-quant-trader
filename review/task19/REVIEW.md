# Task 19 adversarial review

Model: GPT-6 Astra.

Checks were not rerun by me. The supplied check output was produced by implementer Claude Opus 5.5 for commit `44cc8ea`; this review examines only the supplied diff and context.

## Findings

### R-1 — BLOCKER — src/aqt/monitoring/alerts.py:129
Redaction audit events can be silently filtered out. Configure only `LedgerSink(path, Severity.CRITICAL)` and emit a CRITICAL event containing `{"api_key": "credential"}`. The sanitized event reaches the ledger, but its WARNING-level REDACTION event does not. This violates acceptance criterion 3 despite a valid router configuration. Ensure redaction auditing survives sink thresholds and cover this configuration with a test.

### R-2 — BLOCKER — src/aqt/monitoring/alerts.py:131
Credential-bearing field names reach sinks unchanged, including through the generated audit event. For example, an accepted event with fields `{"api_key=" + "K" * 64: "rejected"}` has its value redacted, but the credential-shaped key appears both in the REDACTION event's `fields` value and in the original event's field name. This violates section 28. Sanitize or safely reject credential-bearing names without reproducing them in audit records or errors; test both output records.

### R-3 — BLOCKER — review/task19/LOCAL_REPORT.md:51
T19-01 leaves the roadmap's rotating-file requirement unimplemented. A long-running caller retaining one `LedgerSink` writes every event to the same file indefinitely; each append reads and verifies that entire growing file. Choosing a dated pathname at startup does not rotate it. Implement rotation with preserved chain continuity, or obtain an explicit owner-approved scope deferral before claiming Task 19 complete.

## Deviation assessment

T19-01 is unresolved as described in R-3. T19-02 is acceptable: returning health events satisfies the stated reporting criterion, and routing can remain the caller's responsibility in Task 24.

## Verdict

FIX