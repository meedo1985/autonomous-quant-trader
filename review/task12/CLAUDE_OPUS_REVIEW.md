# Task 12 Claude adversarial review

Date: 2026-09-18  
Reviewed commit: `c59447a5d9b4db0c4aaa3c0188a698e88b031300`  
Reviewer model observed in Claude Code runtime metadata: `claude-opus-5`  
Mode: independent read-only review; no network, data, credential, or file writes

The requested `opus` alias resolved to `claude-opus-5`. It did not report an
Opus 5.1 identifier, so this record does not claim that model.

## Decision

**PASS.** Claude found no blocker and agreed that Task 12 is numerically
correct, deterministic, fail-closed, and within its inactive-primitives scope.
It did not authorize governed use, Task 13, DSR/PBO, confirmation/lockbox
access, promotion, or trading.

## Eight-question result

1. Daily aggregation preserves the accepted hourly equity and cost chain and
   rejects partial, irregular, non-UTC, noncontiguous, or misaligned paths.
2. Paired Sharpe improvement and difference-series Sharpe remain distinct;
   sample variance, zero risk-free return, and `sqrt(365)` scaling match the
   approved convention.
3. Newey-West ESS uses denominator `n`, the approved lag and Bartlett weights,
   complete diagnostics, clamping on the ordinary path, and only the authorized
   fallback cases.
4. No PPW cutoff/window off-by-one error was found. The influence transform,
   weights, corrected constant, degeneracy, clipping, and invalid-spectrum
   behavior match the approved convention.
5. Seed material is compact and convention-bound; private MT19937 streams,
   unbiased index draws, paired indices, and draw order are deterministic.
6. The interval executes exactly 2,000 indexed attempts, records invalid
   attempts without replacement, uses unrecentered type-7 quantiles, and fails
   closed.
7. No protected I/O, global RNG, input mutation, policy verdict, DSR/PBO,
   protected-data access, or governance activation was found.
8. Tests are mostly independent and meaningful. The review identified one
   missing non-degenerate end-to-end regression and two untested window-identity
   rejection branches.

## Findings as returned

| ID | Claude severity | Finding |
|---|---|---|
| T12C-01 | NON-BLOCKING | `LOCAL_REPORT.md` describes the original uncommitted snapshot rather than current HEAD; refresh validation evidence if current-HEAD evidence is needed. |
| T12C-02 | NON-BLOCKING | No real-RNG, non-degenerate test joined block selection, index generation, and the 2,000-replicate interval into one numeric regression. |
| T12C-03 | NON-BLOCKING | The test asserted that the recorded runtime contained `3.12` although project metadata permits Python versions after 3.12. |
| T12C-04 | NON-BLOCKING | Plain return sequences are not intrinsically cross-checked against the asset, cost, and window labels in `ReplicateStream`. |
| T12C-05 | NON-BLOCKING | The approved PPW window formula differs from one external reference formula, although it is identical for practical Task 12 sample sizes. |
| T12C-06 | NON-BLOCKING | Non-midnight and parseable-but-noncanonical evaluation-window identities lacked direct rejection tests. |
| T12C-07 | NON-BLOCKING | The inner `_sharpe` zero-variance conditional contains a redundant equality arm after constant inputs have already returned. |
| T12C-08 | QUESTION | The approved horizon fallback `n / h` is intentionally not clamped and can be below one. |
| T12C-09 | QUESTION | A plain percentile interval has known coverage limitations if it is later used by a promotion gate. |
| T12C-10 | QUESTION | Frozen `paired_delta_sharpe` language is not yet bound to one of Task 12's deliberately distinct estimands. |
| T12C-11 | NON-BLOCKING | A representability failure producing a daily return of exactly `-1` uses the umbrella `NONFINITE_RESULT` code. |
| T12C-12 | QUESTION | Non-UTC, off-midnight input reaches `PARTIAL_DAY` before `INVALID_TIMESTAMP`; both paths fail closed, but reason precedence is unspecified. |

The complete feedback was adjudicated in `CLAUDE_OPUS_ADJUDICATION.md`. This
review is advisory and does not replace an owner decision or any Constitution
section 16 human review.
