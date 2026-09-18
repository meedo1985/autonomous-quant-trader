# DSR reconciliation adversarial-review packet

**Status:** READY FOR HUMAN RELAY; NOT SENT TO CLAUDE
**Base/HEAD:** `3e0244bb3b11c9a1b324b3142249e6a3abb4855a`
**Task:** reconcile GitHub DSR work with the local calibration proposal
**Local gate:** PASS for committing a documentation-only NO-GO proposal
**Scientific activation:** BLOCKED

## Review attachments

Read the complete adjacent files; summaries alone are insufficient:

- `DSR_CALIBRATION_RECONCILIATION.md`
- `CALIBRATION_PREREGISTRATION_DRAFT.md`
- `ASTRA_CALIBRATION_PREREGISTRATION_REVIEW.md`
- `OWNER_ACTION_CHECKLIST.md`
- `OWNER_DSR_DEFER_DECISION.md`
- committed inputs `DSR_METHOD_PREREGISTRATION_DRAFT.md` and
  `DSR_AGENT_REVIEW_ADDENDUM.md`

Exact Windows working-tree SHA-256 values before this packet was added:

```text
4017d27d784e81db18245aae233e5cfc025ccffcc2c5bcff3184b78f0da47da8  DSR_CALIBRATION_RECONCILIATION.md
f6bdb1d50ef557da39f450ea7df8fe9d9117c83b24cceea460c66505e91f9a5d  CALIBRATION_PREREGISTRATION_DRAFT.md
2568ef63c397eb21feb4d71341a2d1bff4ab8319d612ad6f36eea943bba05ad3  ASTRA_CALIBRATION_PREREGISTRATION_REVIEW.md
5d205127511a9e8d1c4972b51a3b405dfb852d4259e74bb6654e5a14d2b9d1e2  OWNER_ACTION_CHECKLIST.md
8aee76b499f8c3b3fc851e541da7622d649437c6da7ce01071a5a84515c35531  OWNER_DSR_DEFER_DECISION.md
```

These are raw checkout-byte hashes. Historical Linux/LF hashes must not be
claimed equal to Windows/CRLF checkout hashes without explicit canonicalization.

## Outcome to challenge

The proposed decision is NO-GO for simulation. The narrow conventional DSR
candidate and the 148-cell numerical proposal are preserved as historical,
non-executable proposals because their supported domains and primary events
conflict. A small 16-cell Gaussian baseline is recorded only as a possible
future arithmetic/reference experiment; success would not establish a practical
promotion method or close B1-B5.

The owner subsequently selected `DEFER` on 2026-09-18. This closes the immediate
choice about whether to spend compute on the narrow baseline; it does not accept
a method, activate governance, or remove any scientific blocker.

## Validation evidence

- GitHub fast-forwarded to `origin/main` commit `3e0244b`; no conflict or local
  overwrite occurred.
- Frozen verifier passed: 28/28 trusted bytes and inventory, 14/14 sidecars,
  Constitution self-hash, seven manifest/protocol bindings, and nested cost,
  feature, and benchmark bindings.
- Protected-path diff is empty; Git whitespace check passed.
- `gpt-6-astra` performed read-only reconciliation and final precommit review;
  it returned PASS after correcting the score-order claim and finding mapping.
- Tests, Ruff, mypy, and import-linter are N/A: no executable code, project
  configuration, import boundary, or frozen artifact changed.
- No simulation, networked exchange activity, credentials, confirmation data,
  lockbox data, governed trial, or promotion action occurred.
- GitHub CI for commit `25bebdb` completed successfully. No open pull request or
  issue defines another authorized task; Task 13 remains explicitly blocked.

## Questions for adversarial review

Return stable `BLOCKER`, `NON-BLOCKING`, and `QUESTION` IDs with file/line,
evidence, impact, and minimal correction.

1. Does the record accurately explain why the method and 148-cell draft cannot
   be executed together?
2. Is the maximum-Sharpe versus maximum-DSR event distinction stated correctly?
3. Does the proposed joint generator actually yield independent difference
   columns despite a shared benchmark?
4. Is the primary-reason precedence deterministic without hiding a scientific
   failure needed for calibration reporting?
5. Could any wording be mistaken for human acceptance, activation, practical
   method support, or permission to simulate?
6. Is any required evidence missing before this NO-GO record is committed?

Do not propose new strategy logic, modify frozen governance, or interpret this
packet as authorization to run calibration. Claude feedback is advisory and
does not replace human/statistician acceptance.
