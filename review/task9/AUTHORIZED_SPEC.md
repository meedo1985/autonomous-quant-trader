# Task 9 Authorized Specification

## Goal

Implement the deterministic data-manifest and code-identity layer required by
the frozen v1.0 protocol before the first research trial can be bound. Task 9
does not bind a real experiment cycle because no approved real dataset exists.

## Authorization and review basis

The user authorized continuing Task 9 and has delegated routine scientific
choices to the reviewed best option. Claude Opus selected the manifest layer as
the next protocol dependency. Claude Fable 5.1 reviewed that proposal and
required the trust-boundary and reproducibility corrections recorded below.

## Bound decisions

- Use partition manifests and a composite cycle manifest.
- The general builder and verifier refuse lockbox data. A future `lockbox_eval`
  process may supply only a sealed partition-manifest reference to the composite.
- Raw artifacts are identified by SHA-256 of their exact source bytes.
- Parsed hourly bars use a versioned binary encoding containing explicit type,
  shape, interval, timestamps, and little-endian binary64 OHLCV values.
- Manifest JSON follows the frozen JSON canonicalization rules and rejects all
  floating-point values, including NaN and infinity. The manifest self-hash is
  excluded while computing the hash.
- Gaps are sorted, non-overlapping half-open UTC intervals. Observed bars may not
  fall inside a declared gap.
- Fees, exchange filters, and symbol status are each recorded as either
  `AVAILABLE` with source hash and `as_of_utc`, or `UNAVAILABLE` with a reason.
- The source bundle includes every committed Git blob under `src/aqt`, sorted by
  repository path. It records the commit and refuses a dirty or untracked
  covered path. The bundle hash is based on Git blob content, not checkout line
  endings.
- The environment fingerprint records the committed `pyproject.toml` hash and
  Python, NumPy, and installed project-package versions beside the source hash.
  It is not folded into the source hash.
- Task 9 records identities only. It does not claim that a hash is accepted or
  write the protected trial-binding decision.

## Implementation

- `src/aqt/data/manifest.py`: canonical bar encoding, partition manifests,
  sealed references, composite manifests, and strict verification.
- `src/aqt/core/code_identity.py`: clean-tree Git blob identity plus environment
  fingerprint.
- Focused unit and integration tests proving determinism, sensitivity,
  provenance, coverage, lockbox refusal, and Git working-tree safeguards.

## Explicit exclusions

- No Binance/network access, credentials, or real market data.
- No raw lockbox read, parse, hash, or verification outside `lockbox_eval`.
- No metrics engine, trial execution, promotion, or Task 10 work.
- No edit to any frozen v1.0 governance artifact or its sidecar.
- No protected cycle-binding or protocol-enforcement component.

## Acceptance criteria

1. Canonical manifest bytes are repeatable and reject floats.
2. Bar hashes change when any value, timestamp, interval, parser hash, raw hash,
   or gap declaration changes.
3. Partition lineage links exact raw hashes, parser code hash, and parsed hash.
4. General APIs fail closed on lockbox data.
5. Gap and point-in-time provenance constraints are enforced.
6. Composite verification recomputes hashes and requires exactly the three
   protocol partitions without exposing raw lockbox identity.
7. Code identity uses committed Git blobs, covers all tracked `src/aqt` files,
   records environment details, and refuses covered dirty/untracked files.
8. A synthetic experiment record accepts the produced manifest and code hashes
   under the frozen experiment schema.
9. Focused and full repository validation pass, including frozen-artifact and
   Task 6 inventory drift gates.
10. Stop after Task 9; do not start Task 10.
