# Claude Fable 5.1 Final Review

Observed model metadata: `claude-fable-5-1` (Claude Fable 5.1).

Verdict: **PASS**.

Fable executed adversarial probes in throwaway repositories and confirmed that
semantic rehashing, non-hourly bars, non-lockbox sealed entries, invalid
composite headers, caller-asserted raw metadata, Git index masking, ignored
source files, and clean-filter masking are rejected. CRLF checkout content kept
the same committed-blob identity. It also confirmed the lockbox mapping contains
only sealed keys and the integration test uses a real Draft 2020-12 validator.

Five non-blocking follow-ups remain explicitly outside Task 9: a static upper
bound for bar count when no series is available, interval-overlap semantics for
partial gaps, defining the future lockbox evaluator's sealed hash, the runtime
policy for ignored bytecode caches, and refusing an uncommitted `pyproject.toml`
when recording an environment fingerprint. None prevents this identity-only
task from passing its authorized acceptance criteria.
