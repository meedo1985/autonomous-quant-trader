# Owner review — evaluation-attempt counting (PR #6)

**Status:** `HUMAN PR REVIEW RECORD — PARTIALLY COMPLETE, AWAITING OWNER TEXT`
**Subject:** PR #6, merged as `94f44d8` on 2026-09-21
**Constitution §16 prong recorded here:** the **human** prong
**Different-model prong:** `FABLE_5_1_SECTION_16_REVIEW.md`, observed model ID
`claude-fable-5-1`, verdict `REVISION_REQUIRED`, committed as `79ea60a` before
any repair cited it

The factual sections below were prepared by Claude (observed model ID
`claude-opus-5`) from the session record. **The owner's assessment in §4 and the
signature in §5 are deliberately blank.** An AI filling them in would be writing
the human prong of §16 on the human's behalf, which would make the §16 record a
formality rather than a control — the same failure as an AI completing a
statistician's decision form. Only the owner of record can complete them.

## 1. What was merged

| | |
| --- | --- |
| Branch | `feat/evaluation-attempt-counting` |
| Commits | `c7b116c` (module and tests), `79ea60a` (review record), `cc17a3d` (repairs) |
| Merge commit | `94f44d8` |
| Files added | `src/aqt/core/attempts.py`, `tests/unit/test_attempts.py`, `review/attempt-counting/FABLE_5_1_SECTION_16_REVIEW.md` |
| Frozen artifacts touched | None. 28 protected paths, 28 baseline hashes, 14 sidecars re-verified unchanged |

The module implements Constitution §9 counting — "Count when evaluation begins;
aborted evaluated runs count. All failures count." — by writing a durable
`EVALUATION_STARTED` record before evaluation reads data, and taking every count
from those records alone.

## 2. What the owner was shown before merging

Stated plainly so that the depth of this review is not later overstated. Before
instructing the merge, the owner was given, in the session:

- the two blockers `F-1` and `F-2`, described as undercount channels, with the
  mechanism of each;
- `F-5`, that the author had invented a `training` partition with no frozen
  referent, and that this had concealed a second-order bug affecting `lockbox`;
- `F-10`, that the author's own crash-safety test did not test crash safety, and
  that the reviewer had supplied a real one;
- `F-7`, the misattributed citation, verified independently;
- the list of repairs applied, and the four items left open;
- the validation results: `pytest` 1153 passed / 4 skipped, `ruff` clean,
  `mypy src` clean, `import-linter` exit 0;
- the §16 ruling in `F-11`, including its recommendation that the owner treat the
  module as covered by §16 now rather than later.

The owner's instruction was to merge. **The owner did not comment on any
individual finding**, and no line-by-line code review by the owner is recorded.
Whether the merge instruction constitutes the §16 human review, and on what
basis, is for the owner to state in §4 — it is not asserted here.

## 3. Items the review left open, unresolved at merge

These were open when the merge happened and remain open. None is a defect in the
merged code; each is a decision the code deliberately does not make.

| ID | Open question | Whose |
| --- | --- | --- |
| `F-5` (part) | The partition is a caller-supplied label, but §9's criterion is a fact about which data was mounted. A caller that mislabels a confirmation run as `exploration` lowers `N`, and no code in this module can detect it. The engine that mounts the partition should set the label | Owner / design |
| `F-6` | `preregistration.FamilyTrialCounts` and this module both now claim to be the §9 count, with no cross-link between the record types. `D-17` does not choose between them | Owner / statistician |
| `F-8` | No ledger location is fixed anywhere, so "lifetime family accounting persists" holds only within a single file. Nothing forces a caller to invoke `start_attempt` at all: counting when evaluation begins remains a calling convention, not a guarantee | Owner / design |
| `F-11` | §16 scope. The reviewer ruled the module outside the enumeration as it stands, and inside it the moment a DSR or promotion-gate consumer binds to these counts | Owner |

**Nothing consumes these counts yet.** No DSR computation, promotion gate, or
eligibility decision reads them. Under `F-11`'s ruling, a future change that
binds `N` from this module into the promotion gate requires its own §16 review.

## 4. Owner's assessment

*To be completed by the owner of record. Suggested prompts, none of them
binding — delete what does not apply and write what does.*

**Did you review the code itself, the summary of findings, or both?**

> `<<UNRESOLVED>>`

**Do you accept the four open items in §3 as open, or does any of them block use
of this module?**

> `<<UNRESOLVED>>`

**`F-11`: do you treat this module as covered by §16 from now, or only once a
consumer binds to its counts?**

> `<<UNRESOLVED>>`

**Anything you want a later reader to know about why you merged this:**

> `<<UNRESOLVED>>`

## 5. Signature

*An unsigned record is not a §16 human review. Until this block is completed,
this file records that a merge occurred and what preceded it — nothing more.*

```text
Owner of record (name):
Reviewed on (UTC):
Merge commit reviewed:     94f44d8
Different-model review:    FABLE_5_1_SECTION_16_REVIEW.md (79ea60a)
Constitution §16 human prong:   satisfied / not satisfied
Signature:
```

## 6. What this record does not do

It does not accept, calibrate, or activate any statistical method. It does not
close `D-16`, `D-17`, or any other row of the decision matrix. It authorizes no
consumer of these counts, no calibration engine, no simulation, no confirmation
or lockbox access, no promotion, no deployment, and no trading. The statistical
verdict remains `KEEP_BLOCKED`.
