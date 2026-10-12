<!-- Recorded verbatim from codex exec (OpenAI Codex v0.162.1) on 2026-10-12. CLI banner: model gpt-6-sol, reasoning effort high, sandbox read-only, session 01a130aa-943f-7b60-b5c6-8ecc5fa0c5e8. Tokens used: 85,604. Made from a packet built from commit bf671d0: the prompt below, the review and adjudication sections of SOL6_QOBJ_REVIEW_9DC7A40.md, git diff 2159d13 bf671d0 -- calibration scripts tests, and calibration/qobj.py. -->

> # Focused re-review: qualification-object builder after QO-1..7 (2159d13..bf671d0)
> 
> You are an independent adversarial reviewer working read-only, not an authority. Everything is attached. Review ONLY whether QO-1..QO-7 (your review, recorded below with its adjudication) are resolved, or acceptably disclosed where the adjudication says so, and whether the repairs introduce a new defect. Verdict ACCEPT or FIX; any new finding gets a stable ID QOR-n with severity, file:line and a concrete failure scenario.
> 

## Review (final message, verbatim)

## Verdict: FIX

- **QO-1 — Blocker — [qobj.py:203](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/qobj.py:203>).** The fresh choose still calls [`run_plan()`](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/scripts/d19_choose.py:46>), which [raises for every qualification manifest](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/rundef.py:262>) at `bf671d0`. A real build fails. The success tests still replace `_choose`.

- **QO-2 — High — [qobj.py:92](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/qobj.py:92>).** `git branch -r` reads local tracking refs, not the remote. After a remote branch is deleted or force-pushed, a stale local ref can still make an unpushed definition pass. The adjudication’s timestamp limitation is disclosed; this claimed push check is not.

- **QO-4 — Medium — [qobj.py:64](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/qobj.py:64>).** §4 requires a manifest of enumerated tests. `enumerated_tests()` produces only the count `m`; the object contains the cell manifest and test-counting code, but no enumeration of the tests. A successful build therefore still omits that required content.

- **QO-5 — Medium — [qobj.py:141](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/qobj.py:141>).** `_reviewed()` checks working-tree JSON, file hashes, and whether a review path exists; it never checks that the freeze-review JSON or review records are committed. Matching untracked files can pass the claimed committed-review gate. Human assessment of what a review *says* was explicitly disclosed; committedness was claimed as a repair.

- **QO-6 — Medium — [qobj.py:211](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/qobj.py:211>).** The final head check cannot detect a changed host field: [`chunks._digest()` excludes `host`](<D:/PMP-programs-for-sharawi/autonomous-quant-trader/calibration/chunks.py:59>). If host provenance changes after `host_sha256()` reads it, the head still matches and the object publishes a stale host hash.

QO-3 and QO-7 appear addressed on code inspection. I found no separate new QOR finding. I inspected the supplied snapshot and repository files at `bf671d0` read-only; the local command runner failed before starting a shell, so I could not run validation or commit a review record.
## Adjudication (Claude Opus 5.5, `claude-opus-5-5`, 2026-10-12)

| ID | Decision | Repair |
|---|---|---|
| QO-1 | AGREE, repaired | `rundef.run_plan` is split. `counts(manifest)` does all the validation: prescribed counts, the exact grid, pilot rules. `run_plan` is `counts` plus the DR2-1 refusal, for starting or recording a run (`d19_run.py`, `d19_run_definition.py`), and still refuses every qualification run. `d19_choose.py` reads finished chains with `counts`, so a fresh choose of a qualification store no longer hits the refusal. The DR2-1 refusal of *starting* is unchanged; `test_a_bad_run_plan_is_refused` passes. |
| QO-2 | AGREE, repaired | `_on_remote` lists the branches of the live remote (`git ls-remote --heads`), fetches them, and needs one of them to contain the commit (`merge-base --is-ancestor`). Local tracking refs are no longer used. A remote that cannot be read refuses. Test: after the branch is deleted on the remote, a stale local tracking ref still exists and the check refuses. |
| QO-4 | AGREE, repaired | `choices.test_manifest` lists every enumerated test as (cell, family label or `agnostic` or `joint`, bound), and its length is `enumerated_tests`, with a test. `d19_choose.py` writes it as `tests`. The builder requires `tests` and that it holds `m` tests. |
| QO-5 | AGREE, repaired | Every later file, the freeze-review record and each review record are read **as committed at HEAD** (`git show HEAD:`). The later files must also equal the working-tree bytes that are packaged. Tests: an uncommitted edit is refused, a committed change after review is refused, and a committed removal of a review record is refused. |
| QO-6 | AGREE, repaired | Host provenance is outside the chunk digest (S16-4), so the builder hashes every chain's host list twice, once around the final head check, and refuses if the two differ. |

QO-3 and QO-7 were accepted by this re-review.

Local: the qobj, grid, chunk, test-manifest and run-plan refusal tests, 50 passed; ruff check and format clean; `mypy calibration` clean.
