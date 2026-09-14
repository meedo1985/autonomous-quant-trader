# Fable 5.1 Decision Review

Observed model metadata: `claude-fable-5-1`.

Initial verdict: **REVISE**.

The reviewer agreed that the data-manifest layer is the correct next dependency
but identified three blockers:

1. A generic manifest builder could leak raw lockbox identity. The accepted
   design refuses lockbox build/verification and admits only a sealed reference.
2. A working-tree code hash would drift with CRLF conversion and could miss new
   modules. The accepted design hashes every committed Git blob under `src/aqt`
   and refuses dirty/untracked covered paths, while recording commit and
   environment details.
3. Parsed-data identity was underspecified. The accepted design uses a versioned
   little-endian binary encoding with explicit type and shape and rejects floats
   from manifest JSON.

The review also required half-open UTC gap intervals, explicit point-in-time
availability records, composite hash recomputation, and no edits to frozen
schemas. All findings are incorporated into the authorized specification.
