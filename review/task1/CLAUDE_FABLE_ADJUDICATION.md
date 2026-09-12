# Fable 5.1 review adjudication

Model requested and observed: **claude-fable-5-1**.
Client: Claude Code 2.1.268, upgraded through its existing official winget package.
The first explicit Fable attempt was refused by old Claude Code 2.1.143; that
failed invocation is retained. The successful second invocation returned exit 0,
is_error=false and actual Fable model usage. The earlier independent review used
Sonnet 4.6 and is preserved separately; it is not labelled as a Fable review.

Fable verdict: **TASK 1 PASS**. Local blockers: **none**.

| ID | Fable severity | Disposition | Evidence / action | Validation |
|---|---|---|---|---|
| C1 | QUESTION | PARTIAL | Worker-only consistency would be inadequate. The coordinator's snapshot predates Codex implementation and its original copy matches the worker copy; eight accepted values from the earlier conversation also match. No signed historical Git baseline exists and no independent historical manifest-file hash is claimed. Owner can compare their original release before a future governance commit. | 28 exact protected hashes, 14 sidecars, canonical hash, bindings and baseline-provenance.json. No frozen file changed. |
| C2 | NON-BLOCKING | AGREE | README now says CI checks plus the additional local Git whitespace check. Machine-specific portable-runtime notes moved to review/task1/README.md. A standard CPython clean installation/remote Linux run is still unverified. | Direct inspection and non-mutating Git whitespace check of final README. No runtime change. |
| C3 | NON-BLOCKING | AGREE | review/task1/README.md explicitly documents installing PyYAML and jsonschema before the one-off audit. Absolute temporary probe paths are retained as execution provenance; they are local paths, not credentials. | Existing environment successfully ran the audit; pip check passed. A new clean environment was not claimed. |
| C4 | QUESTION | PARTIAL | Current training namespaces are models/research and indirect imports into them are blocked. Data/features/validation/benchmarks are not automatically reclassified as training by Task 1. Future work must revisit contracts before placing training/research code outside the covered namespaces. | All 20 current required direct/indirect probes reject. No blanket new boundary or frozen amendment introduced. |
| C5 | NON-BLOCKING | AGREE | GitHub workflow execution and required branch-status configuration are unverified. First authorized push/PR should establish both. No remote settings changed and no push/merge performed. | Local commands and workflow configuration passed; this is not evidence of GitHub branch protection. |

Shared-assumption follow-through:
- Ran non-mutating git diff --no-index --check against NUL for every new/changed
  source/config/evidence-script file, without touching the user's Git index.
  This caught one extra empty EOF line in run_checks.ps1, now removed. All 34
  paths are whitespace-clean; final-whitespace-results.json records raw exit
  codes. In --no-index mode exit 1 can mean files differ, so clean stdout and
  a non-error exit were distinguished from actual whitespace diagnostics.
- The six required acceptance commands passed. New changes after Fable are limited
  to documentation and one empty EOF line; no Python source, contracts, tests,
  dependencies, CI logic or frozen artifact changed.
- Remote pre-commit environments, Linux CI, lowest dependency versions, dynamic
  imports and future live namespaces were not newly tested or claimed.

Fable inspected the full original packet and did not run tools. The coordinator
executed validations and applied the accepted documentation corrections. No second
Fable review of those minor corrections was performed. Final source hashes and
the exact post-review addendum make that distinction reviewable.

Stop at Task 1. No approval to commit, merge, deploy or trade is implied.
