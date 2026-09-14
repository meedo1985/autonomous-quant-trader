# Claude Opus Implementation Brief

Implement only `review/task9/AUTHORIZED_SPEC.md`.

Read the frozen constitution, protocol, hash canonicalization specification,
experiment schema, existing bar model, package conventions, and test setup
before editing. Do not modify frozen artifacts or their sidecars.

Prefer the standard library and existing dependencies. Keep the API small.
General manifest code must refuse lockbox data before inspecting it. Code
identity must use committed Git blob bytes for every tracked path under
`src/aqt`, record commit/environment metadata, and refuse dirty or untracked
covered paths.

Add focused tests and run only those focused tests. Do not run the full suite,
commit, push, bind a real trial, or start Task 10. Report changed files, focused
test results, and any remaining assumption.
