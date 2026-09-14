# Task 9 Scientific Decision

Status: **APPROVED FOR IMPLEMENTATION** under the user's standing delegation.

The next protocol dependency is a deterministic data-manifest and code-identity
layer. Partitioned manifests preserve provenance without crossing the lockbox
trust boundary. Exact raw-byte hashes and a versioned binary representation of
parsed bars avoid locale, JSON-float, and platform ambiguity. A composite
contains sealed partition references and coverage only.

The code identity is the canonical hash of all committed Git blobs under
`src/aqt`, with the commit and environment fingerprint recorded separately.
This makes the content hash stable across checkout line endings while refusing
dirty or untracked source files.

This task deliberately does not bind a real cycle. Acceptance of manifest and
backtester hashes belongs to the protected pre-trial workflow and requires an
approved real data manifest plus the governance review required by the frozen
constitution.
