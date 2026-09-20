# Independent review — `v1.1-method-candidate/`

**Reviewer:** Claude, exact observed model ID `claude-opus-5`. AI reviewer,
read-only analysis plus in-place correction of the reviewed draft's two defects.
**Date:** 2026-09-20
**Repository HEAD at review:** `a7f6a5cfdc1d2a3f77b6757201889fe4b49f06f2`
**Skills applied:** `.agents/skills/statistical-binding-review/SKILL.md`,
`.agents/skills/scientific-reproducibility-review/SKILL.md`,
`.agents/skills/task-gate-review/SKILL.md` (as directed by root `AGENTS.md`).
**Bytes reviewed:** the first revision of the five files in
`v1.1-method-candidate/`, whose `MANIFEST.sha256` verified 4/4 before review:
`README.md` `32b49c45…`, `METHOD_CANDIDATE.md` `53fea11c…`,
`HUMAN_DECISION_MATRIX.md` `e02d70fb…`, `PREREGISTRATION_TEMPLATE.md` `85e08f4e…`.

## Verdicts

| Question | Verdict |
| --- | --- |
| The **statistical binding** question (rows 1–13) | `KEEP_BLOCKED` — **unchanged**. This review disturbs no prior recommendation and closes no row. |
| The **reviewed packet**, as an artifact fit to put in front of a human | `REVISION_REQUIRED` → corrections `R-1` and `R-2` applied; the packet is now internally consistent. |

This review is not scientific or governance authority. It is not human, owner, or
statistician acceptance; it does not satisfy Constitution §4 or §16; and it
authorizes no code, simulation, data access, trial, promotion, or trading. No
simulation was run, no data was accessed, no network or exchange call was made,
and no credential was used.

## 1. Authority and status of what was reviewed

| Item | Status | Authority |
| --- | --- | --- |
| `protocols/protocol_v1.yaml`, `docs/RESEARCH_CONSTITUTION.md` | `FROZEN` v1.0, cycle `C1`, byte-unchanged | Frozen governance |
| DSR active method and the `dsr_minimum: 0.95` gate | Diagnostic-only; gate unsatisfied; promotion blocked | Owner **DEFER**, 2026-09-18 |
| `src/aqt/metrics/statistics.py` paired statistics | Implemented, **inactive** | Accepted implementation fact, not a binding |
| `aqt.dsr.iid_raw_count.proposal.v1` | Unaccepted AI proposal | None |
| Everything in `v1.1-method-candidate/` | Unaccepted AI candidate | None |
| Astra `B1`–`B5`, `DEC-01`–`DEC-03` | Open | — |

Nothing in the reviewed directory was promoted in status by being reviewed.

## 2. Estimands as reviewed

| Symbol | Formula | Required input | Units |
| --- | --- | --- | --- |
| `E-IMPROV` | `A*S(c) - A*S(b)`, `A = sqrt(365)` | both daily legs | annualized-Sharpe |
| `E-DIFF` | `A*S(c - b)` | difference series only | annualized-Sharpe |

`S(x) = mean(x)/sd(x)`, `sd` denominator `n - 1`. The two are mutually
non-identifiable and reverse rankings; §5 below reproduces that exactly. The
separation is preserved throughout the reviewed packet, and the packet nowhere
asserts a universal binding. Confirmed compliant with the
`statistical-binding-review` project invariants.

## 3. Frozen-citation audit — `PASS`

Every `protocol_v1.yaml` and `RESEARCH_CONSTITUTION.md` line number cited
anywhere in the four Markdown files was re-read at HEAD. All resolve to the
asserted clause. Load-bearing cases:

| Cited | Actual content at that line | Verdict |
| --- | --- | --- |
| `42–44`, `279` | `eth_gate` … `paired_delta_sharpe_point_estimate_gt_0_…`; justification "directional consistency"; `eth_sanity_rule` | `PASS` |
| `150` | `stress_multipliers: [1.0,1.5,2.0,3.0]` | `PASS` |
| `232` / `233` | `effective_trial_count_method: eigenvalue_effective_number_…` / `fallback: raw_trial_count` | `PASS` — the primary/fallback split is exactly as `F-1` describes, and no trigger condition exists in frozen text |
| `237–239` / `240` | `series_matrix` (difference matrix vs `VOL_TARGET_BUY_AND_HOLD`, justification "Keeps PBO on the same incremental objective as DSR") / `ranking_metric: paired_delta_sharpe` | `PASS` — the row-8 conflict is real |
| `263–265` | `median available-neighbor … >= 0.5 * selected-point value` | `PASS` — the negative-`v` inversion is real |
| `83–86`, `87–89`, `90–91` | prediction-interval construction with lockbox **decision-count**, `one_sided_lower_5_percentile`, pass rule including `AND BTC delta-Sharpe > 0` | `PASS` — the lockbox incompatibility and the "seven things" scoping are both supported |
| `134–140`, `289` | `samples: 500`, `gate_metric`, `null_minimum_percentile: 0.95`, with **no pass event stated anywhere** | `PASS` |
| Constitution §4 `47–56`, §5 line 67 | amendment rule; "Prior-cycle results are not pooled … lifetime trial counts persist" | `PASS` |

Implementation citations also hold: `statistics.py:208–233` is exactly
`PairedSharpeStatistics` plus `paired_sharpe_statistics`, and its
`paired_sharpe_improvement = a.scaled - b.scaled` is `E-IMPROV`;
`IMPLEMENTATION_CONVENTIONS.md` confirms `psi = u - (S/2)*(u^2 - 1)`,
`z = psi_candidate - psi_benchmark`, `n >= 16`, purpose token
`"paired_sharpe_ci"`, 2,000 attempts, and type-7 quantiles. The `I-10`
estimand/bootstrap coupling argument is therefore correct as stated.

## 4. Reproducibility review

`MANIFEST.sha256` verified 4/4 before and after correction. No tracked file was
modified, renamed, deleted, or regenerated; `git diff --check` is silent; the
working tree contains only this directory plus this review file.

`review/task6/verify_frozen.ps1` **cannot run in this environment** (`N-3`).
Its full logic was therefore independently reimplemented against
`review/task1/protected-before.json` and
`schemas/HASH_CANONICALIZATION_v1.md` rules 1, 5, 6, and every assertion passed:
28/28 baseline hashes, exact protected-inventory match, 14/14 sidecars,
Constitution canonical self-hash reproduced as
`4cb6c7d35e238bdd778e8dd74b25d1b978e57fedffdbfae83b2867b5ec4fb8d7`,
`release`/`status` metadata, the `constitution_content_hash` binding, and 7/7
embedded spec hash bindings. This closes the gap the reviewed draft recorded as
"canonical self-hash step not re-executed": it is now verified, not inferred.

## 5. Independent exact-arithmetic checks — all `PASS`

Recomputed from exact rationals, independently of the packet's own arithmetic:

| Claim | Published | Reproduced |
| --- | --- | --- |
| `S(c_1)` | `4.5*sqrt(3)` | `7.794228634059947` — identical |
| `S(c_2)` | `(13/62)*sqrt(3)` | `0.36317194352250654` — identical |
| `E-IMPROV_1` / `E-IMPROV_2` | `(13/3)*sqrt(1095)` / `(4/93)*sqrt(1095)` | `143.39339826737722` / `1.423259536152627` — identical |
| `E-DIFF_1` / `E-DIFF_2` | `-sqrt(1095/3604)` / `1.5*sqrt(1095)` | `-0.5512069292029372` / `49.63617632332288` — identical |
| Shared benchmark across both trials | asserted | confirmed: `b = (1/5, -1/10, 1/5, -1/10)` in both |
| Total ranking reversal | asserted | confirmed: `E-IMPROV` orders 1 > 2, `E-DIFF` orders 2 > 1 |
| **Lemma `L-1`** | `E-IMPROV` ranking `=` own-Sharpe ranking under a shared `b` | confirmed on this instance, and exact in general since the two differ by the constant `A*S(b)` |
| PBO split count | `C(16,8) = 12,870 = 2 × 6,435` | confirmed; `6,435` unordered half-partitions |
| `N = 2` PBO branches | `omega ∈ {1/3, 2/3}`, `logit = ∓ln 2`, scores `1`/`0`; exact tie gives `omega = 0.5`, `logit = 0`, score `0.5` | confirmed, `ln 2 = 0.6931471805599453`; the `0.5` branch is reachable |
| Plateau inversion | for `v < 0`, `0.5*v > v` | confirmed (`v = -2` → `-1 > -2`); not triggered for `v > 0` |

Lemma `L-1` is sound and its use in `D-08` is legitimate: under option (b) the
PBO ranking would collapse to the candidate's own Sharpe, which does contradict
the frozen justification at line 239. This is the strongest argument in the
packet and it survives independent check.

## 6. Findings

### Corrected in place (were blocking the packet)

- **`R-1` — wrong decision referent.** `HUMAN_DECISION_MATRIX.md` row `D-03`
  cited `D-19` for the consequence "forces a new block-length derivation".
  `D-19` is the deferred `score >= 0.95` calibration question; the
  bootstrap-migration decision is `D-20`, as `METHOD_CANDIDATE.md` §5 and the
  matrix's own dependency note ("`D-20` is triggered by the first acceptance
  among `D-03`, `D-08`, or `D-11`") both state. A reviewer answering `D-03` would
  have been sent to a deferred DSR question instead of to the migration decision
  their answer actually triggers. **Corrected to `D-20`.** The draft's own
  "Decision-ID consistency `PASS`" check could not catch this, because it tested
  only that each cited ID resolved to *some* row. The check table now separates
  ID resolution from referent correctness.
- **`R-2` — undeclared label scheme.** `METHOD_CANDIDATE.md` §7 cited
  `I-1`–`I-9` as carried forward from
  `external-review-packet/STATISTICAL_BINDING_CANDIDATE.md` §6, and cited `I-7`
  and `I-9` inline. That source presents its nine invariants as an **unlabelled
  numbered list**; no `I-n` token appears anywhere in the external packet. The
  positional mapping is correct — `I-7` does match §6 item 7 — but a reviewer
  searching the cited source for `I-7` would find nothing. **§7 now declares the
  mapping explicitly.**

### `NON-BLOCKING`, left for the human reviewer to weigh

- **`N-1` — overstated exclusivity.** Row 5 and `D-03` say "the only existing
  estimator … already targets `E-IMPROV`". `paired_sharpe_statistics` returns
  `difference_series_sharpe` (`E-DIFF`) in the same frozen dataclass, so both
  quantities are computed today. What is genuinely `E-IMPROV`-specific is the
  `paired_sharpe_improvement` field and the Politis–White block length derived
  from `z = psi_c - psi_b`. The substantive argument is unaffected; the wording
  overstates it. Not edited, because the claim a reviewer must judge is the
  bootstrap coupling, and rewording it mid-review would move the target.
- **`N-2` — incomplete citation.** Row 7 and `D-06` cite `202–204`
  (`final_partial_reporting_block`) for the three-month fold, omitting line 201
  `reporting_fold_months: 3`, which is the clause that actually defines the fold
  length. Both cited lines are relevant; the definition itself is missing.
- **`N-3` — the frozen verifier cannot run here.**
  `review/task6/verify_frozen.ps1:57` calls `[Convert]::ToHexString`, which
  requires .NET 5+ / PowerShell 7. This machine has only Windows PowerShell
  5.1.26100.9444; PowerShell 7 is absent. The script carries no
  `#Requires -Version 7`, so it fails mid-run at line 57 *after* its inventory,
  baseline-hash, and sidecar assertions have already passed, rather than refusing
  to start. Every mandatory frozen check was covered by independent
  reimplementation (§4), so nothing is left unverified — but the repository's own
  verifier is environment-fragile, and a future session could mistake its failure
  for a frozen-artifact breach. Not repaired here: `review/task6/` is another
  task's accepted artifact and editing it is outside this task's scope.
  Recommended scoped follow-up: add `#Requires -Version 7` plus a 5.1-compatible
  hex conversion.
- **`N-4` — `eol=lf` packaging, now actionable.** The directory's own §6.2 records
  that it has no `.gitattributes` pinning `eol=lf`, unlike
  `external-review-packet/`. On a Windows checkout with `core.autocrlf=true`,
  committing as-is can later rewrite these files with CRLF and invalidate all
  four manifest entries with no content change. The remedy is the one §6.2
  already prescribes. Left for the owner, as §6.2 intends. **Closed:** the owner
  instructed the remedy be applied at commit time; `.gitattributes` was added and
  the manifest regenerated and re-verified. See packet README §6.2, and `F-N4` in
  `V1_1_FABLE_ADVERSARIAL_REVIEW.md` for the root-rule redundancy.
- **`N-5` — unproven bias claim.** `METHOD_CANDIDATE.md` §4.1 step 3 asserts that
  using `6,435` splits instead of `12,870` "would halve the sample and bias
  `phi`". Halving alone reduces precision; it does not by itself bias. The claim
  holds only under a **non-random** orientation rule — for instance, always
  taking the chronologically earlier half as in-sample, which would make the
  split sample systematically asymmetric. Using `6,435` with a randomized
  orientation would be approximately unbiased and merely less precise. Retaining
  all `12,870` oriented selections remains the right choice and matches standard
  CSCV for `S = 16`; only the stated reason is stronger than the evidence
  supports.

### `QUESTION`

- **`Q-1`.** `partitions: 16` (line 236) is read throughout as *16 chronological
  blocks*, from which `C(16,8)` splits follow. The reading is consistent across
  the packet and with standard CSCV, but it is an interpretation of a frozen
  token that no `D-nn` row currently owns. Should it be an explicit decision row
  rather than an assumed reading?

## 7. Local gate

`LOCAL GATE: PASS` for the reviewed scope, after `R-1` and `R-2`.

| Check | Result |
| --- | --- |
| Frozen artifacts | `PASS` — independently verified in full (§4); no protected path changed |
| `MANIFEST.sha256` | `PASS` — 4/4, regenerated after correction |
| Frozen citations | `PASS` — all resolve as asserted |
| Exact arithmetic | `PASS` — every published value reproduced |
| Decision/invariant IDs | `PASS` after `R-1`, `R-2`; `D-01`–`D-20` bidirectionally complete across all three documents |
| Tests, Ruff, mypy, import-linter | `N/A` — review Markdown only; no executable code, configuration, dependency, or import boundary is added or changed. Not "unavailable": the repository's suites exist and are simply not applicable to this change |
| Secrets, data access, network | `PASS` — none |

## 8. Remaining human decisions, and what is still prohibited

Unchanged by this review: every one of `D-01`–`D-20` is open. `D-05`, `D-06`,
`D-09`, `D-11`, `D-12`, `D-15`, `D-16`, `D-17`, `D-18` remain blocking
placeholders with no candidate value, and `D-19` remains under the owner's
**DEFER**. `D-08`, `D-12`, and `D-14` are `§4` amendment questions that no
statistician can close alone. Astra `B1`–`B5` and `DEC-01`–`DEC-03` are open.

Still prohibited, and not authorized by anything here: authoring, merging,
activating, or self-approving an amendment; Task 13; a calibration engine; any
simulation or Monte Carlo run; confirmation-partition or lockbox access; a
governed trial; an eligibility decision; promotion; deployment; trading. The
`dsr_minimum: 0.95` gate remains unsatisfied and promotion remains blocked.

Constitution §16 requires different-model **and** human PR review before any
later validation-engine, promotion-gate, governor, executor, lockbox-ACL, or
protocol-enforcement code merges. This review satisfies neither requirement.

**Claude adversarial-review status:** `N/A` — this document *is* the independent
AI review; it is not a packet awaiting one.
**Human/statistician review status:** `NOT SENT`.

## 9. Later events, recorded after this review was written

- An independent adversarial review by Claude, self-reported model ID
  `claude-fable-5-1`, is recorded at `V1_1_FABLE_ADVERSARIAL_REVIEW.md`. It
  confirmed this review's arithmetic and verifier reproduction, and corrected it
  in three places: the `D-20` trigger note carried the same wrong-referent defect
  class as `R-1` (`A-1`); README §6's working-tree row was stale when
  `LOCAL GATE: PASS` was declared (`A-2`); and this review's citation audit tested
  only that cited lines *resolve*, never whether a governing clause had been
  *omitted* — `docs/RESEARCH_CONSTITUTION.md` §9 line 106 ("If no frozen
  effective-count method exists, raw count is used") bears directly on `F-1` and
  was cited by nobody (`A-3`). The §3 audit verdict in this document should be
  read as `PASS for resolution, incomplete as an audit`.
- Its finding `F-Q1` — that Lemma `L-1` collapses row 12, so that under
  `E-IMPROV` the shared benchmark cancels from the null pass event and
  "versus `VOL_TARGET_BUY_AND_HOLD`" is inert — was verified independently and is
  material. The owner elected to leave row 12's proposal `PROPOSED` with the
  question standing, so the statistician rules on it. No AI demoted it.
- Owner instruction, same date: commit the packet with the §6.2 `eol=lf` remedy
  applied. Committing changes no verdict here; every `D-nn` remains open.
