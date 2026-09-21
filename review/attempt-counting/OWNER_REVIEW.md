# Owner review — evaluation-attempt counting (PR #6)

**Status:** `HUMAN PR REVIEW RECORD — COMPLETE AND SIGNED`
**Subject:** PR #6, merged as `94f44d8` on 2026-09-21
**Constitution §16 prong recorded here:** the **human** prong
**Different-model prong:** `FABLE_5_1_SECTION_16_REVIEW.md`, observed model ID
`claude-fable-5-1`, verdict `REVISION_REQUIRED`, committed as `79ea60a` before
any repair cited it

The factual sections below were prepared by Claude (observed model ID
`claude-opus-5`) from the session record. **§4 and §5 are the owner's own
determinations**, given on 2026-09-21 in answer to questions put to the owner
directly, and are recorded as given. No AI composed them: an AI writing the human
prong of §16 on the human's behalf would make the §16 record a formality rather
than a control — the same failure as an AI completing a statistician's decision
form.

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
The owner has since stated the basis on which that constitutes the §16 human
review, in §4: process trust, not an independent code audit.

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

## 4. Owner's determinations

Recorded as given by the owner on 2026-09-21.

**What did you review before merging?**

> **Trusted the process.** The owner merged on the strength of the
> different-model review having run, its repairs having been applied, and the
> validation having passed — without independently reviewing the code or the
> individual findings in detail.

**The four open items in §3 — do any block?**

> **Accepted as open.** None blocks the module being in the repository, since
> nothing consumes these counts yet. They are to be resolved before anything
> binds `N` into a gate.

**`F-11` — when does §16 cover this module?**

> **Covered from now.** `attempts.py` is treated as a §16-enumerated component
> immediately, not only once a consumer binds to its counts. This adopts the
> reviewer's recommendation and is the more conservative of the two readings:
> every future change to this module requires different-model and human PR
> review.

### What a later reader should weigh

Recorded because the record is worth less if it overstates itself. "Trusted the
process" means **no human independently examined this code or its findings.**
The human prong of §16 exists so that a person catches what a model missed, and
on this change that did not happen in the strong sense: the owner's contribution
was the decision to merge, the three determinations above, and the choice to
treat the module as §16-covered from now on.

Against that, what the process did contain: an adversarial different-model review
that found two undercount blockers the author missed, all of which were repaired
and tested; a verdict of `REVISION_REQUIRED` that was acted on rather than
argued with; and the fact that nothing in the repository consumes these counts,
so no gate currently depends on them.

A later reader deciding how much weight this review carries should read the two
paragraphs above together, and should not treat this file as evidence that a
human audited the arithmetic.

## 5. Signature

```text
Owner of record (name):    meedo1985
Reviewed on (UTC):         2026-09-21
Merge commit reviewed:     94f44d8
Different-model review:    FABLE_5_1_SECTION_16_REVIEW.md (79ea60a)
Constitution §16 human prong:   satisfied by the owner of record, on the basis
                                stated in §4 — a process-trust review, not an
                                independent code audit
Signature:                 meedo1985, recorded 2026-09-21
```

## 6. What this record does not do

It does not accept, calibrate, or activate any statistical method. It does not
close `D-16`, `D-17`, or any other row of the decision matrix. It authorizes no
consumer of these counts, no calibration engine, no simulation, no confirmation
or lockbox access, no promotion, no deployment, and no trading. The statistical
verdict remains `KEEP_BLOCKED`.
