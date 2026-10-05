# Sol High re-review of the D-19 engine at c8942db

- Prompt: `review/d19-engine/REREVIEW_PROMPT_C8942DB.md`.
- CLI metadata: codex exec v0.160.0, model: gpt-5.6-sol, reasoning effort: high, sandbox: read-only, session 01a10bc7-5e2b-7c80-827f-243f118c5985, 121,447 tokens. The answer's own first line says "gpt-5"; the CLI header is the observed metadata.
- An earlier attempt the same day hit the Codex usage limit (reset 2:15 PM local) before any output.
- Verdict FIX (RR-1..RR-5). Final answer verbatim:

---

Reviewer model: gpt-5  
FIX

RR-1 — BLOCKER — `calibration/gates.py:122`  
Failure scenario: `or` short-circuits, unlike `aa3457b`, which evaluated every gate eagerly. An early G-2/G-4 refusal now suppresses a later G-10/G-12 exception or trace, potentially counting a replication as ordinary `U_G` instead of stopping on an engine fault. Trace instrumentation itself does not change availability comparisons.  
Minimal repair: evaluate all five gates into a tuple with tracing, then return the first non-`None` reason. Add a test proving later gates execute after an earlier refusal.

RR-2 — BLOCKER — `calibration/rundef.py:134`, `scripts/d19_run_definition.py:29`  
Failure scenario: the hash covers checkout files, not necessarily executed code. `aqt` can resolve from another installation because `ROOT/src` is not forced or verified; executable scripts and the future driver are excluded. A modified driver/check script or stale installed `aqt` can therefore run while the hashed tree still matches.  
Minimal repair: verify every loaded engine module resolves under the hashed root, force `ROOT/src` precedence, and include all executable entrypoints/driver code in the hash. FE-5 is acceptable only if the driver enforces this before workers/chunks start.

RR-3 — MAJOR — `scripts/d19_run_definition.py:34`, `calibration/rundef.py:134`  
Failure scenario: `git status --porcelain` can miss files marked assume-unchanged/skip-worktree and configuration-suppressed or ignored files. `record` can consequently claim a clean HEAD while hashing modified source that cannot be reconstructed from that commit. The preregistration commit is likewise not checked against `--prereg-file`.  
Minimal repair: compare a complete canonical source inventory directly with HEAD blobs, reject index flags and extra executable files, force untracked-file reporting, and verify the preregistration bytes against its commit/path.

RR-4 — MAJOR — `calibration/rundef.py:134`  
Failure scenario: the code hash is process-stable and uses POSIX path separators, but is not OS-stable because it hashes working-tree bytes. This checkout has 33/62 hashed files with CRLF; its raw hash is `b3af03…`, versus `7fb4cd…` after LF normalization. The same clean commit therefore receives different identities across Windows and Linux.  
Minimal repair: hash Git blob bytes or an explicitly UTF-8/LF canonical source manifest; optionally record raw checkout bytes separately as provenance.

RR-5 — MINOR — `tests/unit/test_calibration_rundef.py:91,154`, `tests/unit/test_calibration_engine.py:274`  
Failure scenario: not every new test fails when its claimed repair component is reverted. The U_G test covers only G-1 arithmetic; reverting G-10/G-12 tracing still passes. The extra-vector test checks only count, not `INVALID_SERIES`; benchmark inclusion is untested. Identity refusal and the lower-bound tie already worked at `aa3457b`.  
Minimal repair: add focused mutation-sensitive tests for every trace branch, benchmark-only changes, the unavailable cause, eager gate evaluation, canonical hashing, and loaded-module provenance.

FE-6 is repaired. FE-7’s re-pilot/owner disposition is acceptable. FE-4 and FE-5 are acceptable only as explicit pre-driver operational requirements, not as completed full-run guarantees.
