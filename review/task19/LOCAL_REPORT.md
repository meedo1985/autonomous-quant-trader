# Task 19 local implementation and gate report

Date: 2026-09-26
Base commit: `ae0862d` (`main`)
Branch: `task19-monitoring`
Author and reviewer: Claude Opus 5.5 (`claude-opus-5-5`), coding AI. This is a
**self-review**, not an independent one.

## Authority

Authorized by the owner's roadmap approval (`review/roadmap/OWNER_APPROVAL.md`).
Done before Tasks 16-17 on the owner's "go ahead" of 2026-09-26, recorded in
`review/task18/LOCAL_REPORT.md`; Task 16 is blocked by Q1. The roadmap lists
no blocking decision for Task 19.

## Scope

- `src/aqt/monitoring/events.py` (new): `Event`, `EventKind`, `Severity`;
  canonical-JSON round trip; floats refused.
- `src/aqt/monitoring/alerts.py` (new): `AlertRouter`, `StreamSink`,
  `LedgerSink`, `redact`.
- `src/aqt/monitoring/health.py` (new): stale-data, clock-skew, and loop-lag
  checks.
- `tests/unit/test_monitoring.py` (new): 30 synthetic tests.

No existing module, frozen artifact, or import contract changed. The existing
contract "Live packages cannot reach research agent code" already covers
`aqt.monitoring`. Size: 539 added lines, about 260 of them tests.

## Design

- **Tamper-evident log reuses `aqt.core.ledger`.** `LedgerSink` appends
  through `append_entry`, which verifies the whole chain under a cross-process
  lock before every write and refuses a damaged file. No new hashing code.
- **Critical events cannot be dropped.** CRITICAL is the top severity, so
  every sink receives it; a router with no sink refuses to start. A sink that
  fails raises; nothing is swallowed.
- **Redaction before any sink.** A field is replaced with `[REDACTED]` when its
  name suggests a credential (`api_key`, `secret`, `token`, `password`,
  `passphrase`, `signature`, `private_key`) or its value looks like one: a
  64-character letters-and-digits string that is not a lowercase hex SHA-256
  digest (this project logs those legitimately), a PEM private key header, or
  a `Bearer` token. A separate `REDACTION` event names the field, never the
  value.
- **Health checks take thresholds and severities as required arguments, with
  no defaults.** Choosing them is policy for the deployment protocol
  (Task 20).

### Deliberate differences from the roadmap

- **T19-01. No rotating file.** *(Superseded after review: a rotating log was
  added; see `ADJUDICATION.md` R-3.)* The roadmap says "stdout plus a rotating file".
  Rotation would break a single hash chain unless each new file linked to the
  last, which is new design. The file sink is the ledger at a path the caller
  chooses (for example one per UTC day, each its own chain). Linking files
  across rotation is left for the deployment protocol to require if wanted.
- **T19-02. Health checks return events; they do not route them.** The caller
  (the loop, Task 24) passes them to the router. This keeps the checks pure.

## Acceptance criteria (roadmap Task 19)

| # | Criterion | Evidence |
|---|---|---|
| 1 | Every event type serializes to canonical JSON and round-trips | `test_every_event_kind_round_trips_through_canonical_json` (all 9 kinds); `test_events_refuse_values_they_cannot_represent` |
| 2 | Hash-chained log; a mutated line fails verification | `test_ledger_log_is_hash_chained_and_a_mutated_line_fails`, which also shows the next append is refused |
| 3 | Credential-shaped value redacted before any sink; the redaction logged | `test_credential_shaped_values_are_redacted_and_the_redaction_logged` (5 shapes), `test_hashes_and_ordinary_values_are_not_redacted` |
| 4 | A critical event with no sink is a startup error | `test_a_router_with_no_sink_refuses_to_start`; `test_a_failing_sink_is_not_swallowed` |
| 5 | Stale-data, clock-skew, loop-lag conditions on synthetic inputs | the four health tests, including limits, both skew directions, early starts, non-positive thresholds, and naive times |

Mutation checks, each against a deliberately broken copy, then restored:

| Planted bug | Result |
|---|---|
| Redaction disabled | 5 tests fail |
| SHA-256 digests no longer excluded from the key pattern | `test_hashes_and_ordinary_values_are_not_redacted` fails |
| Router accepts zero sinks | 1 test fails |
| Stale data flagged at exactly the limit | 1 test fails |

The second mutation was first applied with a `sed` command that did not
match, so its first "all pass" result was meaningless. It was reapplied with a
checked replacement and then failed as expected.

## Validation

Environment: Windows 11, `.venv` Python 3.14.7.

| Command | Exit | Result |
|---|---|---|
| `python -m pytest -q` | 0 | 1289 passed, 4 pre-existing skips |
| `ruff check .` | 0 | all checks passed |
| `ruff format --check .` | 0 | 76 files already formatted |
| `mypy src` and the three scripts | 0 | no issues in 39 source files |
| `lint-imports` | 0 | 5 kept, 0 broken |
| `git diff --check main...HEAD` | 0 | clean (run after commit) |

Frozen verification: `git diff main` over the frozen paths is empty.

## Findings (self-review)

- T19-01 and T19-02 above.
- **T19-03 NON-BLOCKING.** Redaction is pattern-based. It cannot recognize a
  secret in a shape it does not know, which is why no credential exists in
  Milestone 0.1 at all; redaction is the second line, not the first.

## Gate

LOCAL GATE: PASS. Independent review status: `NOT SENT`.
