# Astra delta review: FP2 changes after ACCEPT (05321c5 -> ff1af4c, sheet 9afbb80)

Prompt: `review/d19-engine/FP2_BUILD_DELTA_REVIEW_PROMPT.md` (6365208).
Reviewer metadata from the Codex CLI header (2026-10-25): Codex v0.164.0,
model `gpt-6-astra`, provider openai, sandbox read-only, reasoning effort high,
session id `01a171e2-e0a2-7f43-a064-f45aacf4d3ee`, 78,124 tokens.
(The reviewer itself reports its runtime metadata as unavailable; the values
above are the CLI's header for the run.)

Verdict: **ACCEPT**. Findings: none (no `FP2D-R*` IDs issued), so none left
unrepaired. Recorded by Claude Opus 5.5 (the implementer); no adjudication
needed. The reviewer's limits stand: a bounded code review, not the full task
gate or the owner's §16 approval; `--no-optional-locks` is sufficient for the
stated deployment (ordinary checkout, no external filters or hooks), not a
general write prohibition.

## Report (verbatim)

**Verdict: ACCEPT** for `05321c5 → ff1af4c`, including launcher compatibility with sheet `9afbb80`. No new `FP2D-R*` findings.

1. **The earlier repairs remain intact.** Freeze and certify still acquire the lock before checking output existence. Freeze still verifies the named commit, cleanliness and root-only permissions before replacing the scratch clone. Failed `status` or `find` explicitly refuses. The CI assignment now also preserves `find` failure instead of treating empty output as success.

2. **`--no-optional-locks` fixes the identified index-write problem.** Git documents that it suppresses status’s optional index refresh. For the intended ordinary checkout, the remaining source operations—`rev-parse`, `remote get-url`, inspection and local cloning—do not rewrite the build checkout. Checkout, remote modification, ownership changes and the builder’s fetch target `freeze-root`; `--no-hardlinks` prevents shared object ownership changes. [Git status documentation](https://git-scm.com/docs/git-status#_background_refresh), [clone documentation](https://git-scm.com/docs/git-clone).

   This is sufficient for the stated deployment, **not a general filesystem write prohibition**: configured external filters/hooks or other nonstandard Git arrangements would require separate assessment. The option suppresses optional locking operations, rather than sandboxing Git. [Git option semantics](https://git-scm.com/docs/git#Documentation/git.txt---no-optional-locks).

3. **The merged argument checks are exactly equivalent.** Previously acceptance required `$2 ∈ {1,2}` **and** `$# = N`. The new literal patterns accept precisely `N:1` or `N:2`, where `N` is 5 or 3. Missing arguments safely expand through `${2:-}`; extra arguments, whitespace, colons and wildcard characters cannot create another match. Both versions emit the same usage message and exit 1 otherwise.

4. **The `ls` output is best-effort diagnostics; refusal remains unconditional.** `ls` can fail if the path disappears, and unusual filenames can make its presentation misleading—especially trailing newlines stripped by command substitution or backslashes interpreted by some `echo` implementations. Neither permits execution to continue: the branch still exits 1. Quoting prevents word splitting, and substitution output is not executed as shell code. I confirmed both successful and failing `ls` cases refuse. This does not reopen FP2R-R1.

5. **Sheet `9afbb80` matches the launcher.** G0 uses the same status options after `chmod -R go-w`, followed by the same ownership/write-permission predicate. FP2-R2(b)’s broader procedural acceptance remains outside this verdict.

Independent validation on Windows/Python 3.14.7/Git for Windows:

- Targeted pytest, with `-B --capture=sys -p no:cacheprovider` and `-k 'launcher or freeze_refuses'`: **7 passed**.
- Ruff `check --no-cache .`: **passed**; `format --check --no-cache .`: **177 formatted**.
- `lint-imports --no-cache --no-logo`: **7 kept, 0 broken**.
- Exact committed launcher: **`sh -n` passed**.
- In-memory shell probes: **242 old/new argument comparisons passed**, plus failed-`ls` and CI failed-`find` checks.
- Frozen verification: **28 baseline files unchanged** across both reviewed commits, the sheet commit and working files; **14 sidecars**, Constitution self-hash and manifest/protocol bindings verified.

Full pytest, mypy and Docker/systemd integration were not independently rerun; the supplied CI results remain author-reported. This ACCEPT is a bounded code-review verdict, not certification of the complete task gate or §16 owner approval.

Reviewer: Codex; exact runtime model/effort metadata unavailable. No files were edited or committed. Preserve this report in a committed review record before treating the review as complete under `AGENTS.md`.
tokens used
