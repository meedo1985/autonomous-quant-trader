# Task 10 — deterministic preregistration registry

Authorization: the owner requested continuation after Task 9 passed and
delegated routine scientific choices to the reviewed best option. Claude Fable
5.1 selected this bounded registry layer on 2026-09-14.

## Scope

Implement identity and storage primitives for immutable hypothesis
preregistration and trial records. The implementation may validate the frozen
hypothesis and experiment schemas, compute canonical hypothesis hashes, derive
deterministic trial seeds, enumerate a preregistered parameter grid in a fixed
order, append records to a tamper-evident JSON Lines ledger, and answer pure
read-side accounting queries.

The ledger must preserve UTF-8 canonical JSON with LF line endings, sequence
numbers, previous-entry hashes, and entry hashes. Appends must serialize
concurrent writers on Windows, verify the current chain before writing, flush
and fsync durable bytes, and fail closed without modifying a corrupt or torn
ledger. Verification reports corruption and never truncates or repairs it.

## Bound decisions

- Remove `content_hash` while hashing hypothesis content, matching Task 9's
  accepted self-hash convention.
- Derive a seed from UTF-8 bytes of a domain-separated compact canonical JSON
  array containing protocol hash, hypothesis hash, and nonnegative trial index.
  Record the complete lowercase 64-hex SHA-256 digest; any later conversion to
  an RNG-specific seed is outside this task. Freeze the exact bytes and digest
  in a test vector.
- Trial indices are scoped to a hypothesis. Family lifetime totals are pure
  read-side counts over recorded entries.
- Registration timestamps belong to the ledger envelope and do not change the
  hypothesis content identity.
- Deterministic trial enumeration is the Cartesian product of sorted parameter
  names, each value list in its preregistered order, followed by horizons in
  their preregistered order. Values must be canonical-JSON compatible.

## Protected boundary and exclusions

This task records facts; it does not enforce research policy. Do not implement
family-budget limits, permission to start a trial, acceptance of protocol/data/
backtester hashes, cycle binding, EXPOSED state, confirmation or lockbox reads,
metrics/results, validation, promotion, governor, execution, network access,
strategy/model logic, or real-data ingestion. Do not modify frozen governance
artifacts or their sidecars. Do not start Task 11.

## Acceptance criteria

1. Hypotheses validate against the unmodified Draft 2020-12 frozen schema and
   their content hashes are deterministic across key order and text line endings.
2. Any hashed hypothesis content change changes its identity, and an incorrect
   supplied self-hash is rejected.
3. Experiment records validate against the unmodified frozen schema and bind a
   seed derived from their protocol hash, hypothesis hash, and trial index.
4. Trial enumeration is deterministic and rejects ambiguous/noncanonical grids.
5. Ledger entries use canonical JSON, monotonic sequence numbers, previous and
   own hashes, and immutable append-only APIs.
6. Concurrent processes cannot lose, duplicate, or fork append sequence numbers
   on Windows.
7. A torn trailing write or altered historical entry is detected and preserved;
   append refuses a damaged ledger.
8. Read-side counts are deterministic and do not make eligibility decisions.
9. Focused/full tests, Ruff, mypy, import contracts, Git whitespace, frozen
   verification, and Task 6 drift verification pass.
10. An independent adversarial review is adjudicated before commit and push.
