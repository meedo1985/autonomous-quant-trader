# Adjudication of Sol's lockbox re-check 5 (`SOL_LOCKBOX_RECHECK_850D49B.md`)

- Adjudicated by Claude Opus 5.5 (`claude-opus-5-5`), 2026-11-02, the module's author,
  against the code at `881880f` (module bytes of `850d49b`) and the cited governing text
  (freeze-sheet `8a1ec72`). Repairs are in the commit that adds this file.
- Format: `ID | Sol severity | AGREE / PARTIAL / DISAGREE | reasoning and evidence |
  disposition | validation`.

| ID | Sol | Verdict | Reasoning and evidence | Disposition | Validation |
|---|---|---|---|---|---|
| R14L5-S-1 | BLOCKER | AGREE | The `Store` docstring named only three identity fields and bound the read gate to "the cycle manifest whose hash the request carries", a caller value. Annex D §D-3.7 `begin_read` step 4 requires sealing records for every declared family, status (a) for this nominee and artifact, every check-record identity field equal to the sealing record and the request, and the check's `startup_check_id` naming a `PASS` startup record for the same module hash and image; §D-1.8 item 2 and l.98 bind reads to the cycle's data-manifest hash. | Repaired (contract text only): the `Store` docstring now states step 4 in full and that the store takes the manifest hash from its own governing cycle record, never from the request or the worker, refusing a request hash that differs. The store build itself stays an open item. | Contract text; the obligations are for the store build's tests. ruff, ruff format, mypy strict on the file clean. |
| R14L5-S-2 | BLOCKER | AGREE | DRAFT R-14a item 4 (l.159): "Where an engine-commit or later-object-file function implements a rule, the module calls it and does not re-implement it." `aqt.core.preregistration.trial_seed` implements the line-266 seed, and the R14L5-CI-1 repair re-implemented it. Calling it instead breaks item 3 on the image: the module imports `jsonschema`, which `deploy/calibration/requirements.lock` does not pin. Byte equality (pinned by test) is evidence, not compliance. | **OPEN — OWNER DECISION** (it changes governing text or the qualified image, which the author may not decide). Options in the owner question of 2026-11-02; author recommends (a): the lockbox stops deriving the line-266 seed and takes the line-266 and estimator seeds from the sealing record written after the confirmation module's item-7 verification (the same route recommended for `family_seed_f`, R14L4-S-3), checking the nominee's estimator seed against it. Until decided, the re-implementation stays, so the module imports and runs on the image. | — |

Sol's other observations are accepted: the snapshot repair (R14L4-S-1) and the startup-ID
repair (R14L4-S-2) hold, `image_digest` from `started.signed` is sound within `start()`'s
contract, and the CI globs cover all five lockbox test files on Python 3.14.

**Open before signing C2:** R14L5-S-2 (owner decision); the launch route; acceptance
provenance (owner decision); the reference vectors on the qualified image; the S4 format
bindings; the store build's §D-3.7 obligations; the source of an authenticated
`family_seed_f`.
