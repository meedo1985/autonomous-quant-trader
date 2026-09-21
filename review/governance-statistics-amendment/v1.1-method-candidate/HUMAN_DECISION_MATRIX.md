# Human decision matrix — `D-01` to `D-20`

**Status:** `NON-BINDING — DECISIONS REQUESTED, NONE TAKEN`
**Companion to:** `METHOD_CANDIDATE.md`, `PREREGISTRATION_TEMPLATE.md`

Every row is a choice that this candidate does **not** make. "Recommended
candidate" is an AI proposal offered for acceptance, revision, or rejection; it
carries no authority and creates no presumption. Rejecting a recommendation in
favour of retaining the present pause is always an acceptable answer and
requires no follow-up work.

**Authority codes.** `STAT` = a qualified human statistician may close it alone.
`§4` = Constitution §4 amendment process (version bump, written rationale,
owner-of-record signed and dated commit, cycle termination, pre-new-cycle
activation, preserved history, no retroactive effect) —
`docs/RESEARCH_CONSTITUTION.md` lines 47–56. `OWNER` = owner of record only.
`§16` = different-model **and** human PR review before protected code merges.
An AI satisfies none of these.

**Required reviewer response codes.** `A` = accept as written. `R` = revise,
with the substituted text. `X` = reject, with the reason. `D` = defer, keeping
the present block. Every row requires exactly one code plus a recorded rationale.

## 1. Estimand registration

| ID | Decision | Options | Evidence | Consequence if wrong | Recommended candidate | Falsifier | Authority | Response |
| --- | --- | --- | --- | --- | --- | --- | :---: | :---: |
| `D-01` | Register `E-IMPROV` and `E-DIFF` as two separately named estimands | (a) register both; (b) register one; (c) decline to name | `TECHNICAL_APPENDIX.md` §2, §2.1 — mutually non-identifiable | Silent substitution persists; sign and rank reversals stay invisible | **(a)** — a naming act only, binds no gate | A proof that one is a function of the other | `STAT` | `A/R/X/D` |

## 2. Queue I — interpretive rows (3–7)

| ID | Decision | Options | Evidence | Consequence if wrong | Recommended candidate | Falsifier | Authority | Response |
| --- | --- | --- | --- | --- | --- | --- | :---: | :---: |
| `D-02` | Estimand for the ETH sanity gate and the BTC 2x cost stress (rows 3, 4) | `E-IMPROV` / `E-DIFF` / decline | `protocol_v1.yaml:42–44, 279, 283`; sign reversal in `TECHNICAL_APPENDIX.md` §3 | A directional gate passes under one reading and fails under the other on identical returns | **`E-IMPROV`** — both legs exist at evaluation time; no frozen word changes; keeps the joint BTC/ETH trial comparable | Evidence that "directional consistency" (line 44) is better served by `E-DIFF` | `STAT` | `A/R/X/D` |
| `D-03` | Estimand for the paired 90% CI and the strictly positive BTC lower bound (row 5) | `E-IMPROV` / `E-DIFF` / decline | `protocol_v1.yaml:274–275`; inactive estimator at `src/aqt/metrics/statistics.py:208–233`; block length from the improvement influence process | Choosing `E-DIFF` discards the only existing estimator and forces a new block-length derivation (`D-20`) | **`E-IMPROV`** — the only clause with an existing inactive estimator, which already targets it | A showing the inactive estimator targets the wrong quantity here | `STAT` | `A/R/X/D` |
| `D-04` | Estimand for the parameter plateau rule (row 6) | `E-IMPROV` / `E-DIFF` / decline | `protocol_v1.yaml:263–265` | Changes both the threshold's sign and the direction of the requirement | **`E-IMPROV`**, consistent with `D-02`/`D-03` | As `D-02` | `STAT` | `A/R/X/D` |
| `D-05` | Behaviour of `median neighbour >= 0.5 * selected value` when the selected value is `<= 0` | (a) fail; (b) unavailable/`N/A`; (c) restate the rule on a sign-invariant scale; (d) leave as written | `TECHNICAL_APPENDIX.md` §3: for `v < 0`, `0.5*v > v`, inverting the rule into "neighbours must beat the selected point" | A plateau gate that silently rewards worse-than-selected neighbours | **BLOCKING — no candidate.** The defect exists under either estimand and repairing it is a change of rule meaning, not of estimand | A reading under which the inversion is intended | `STAT` then `§4` | `A/R/X/D` |
| `D-06` | Fold anchoring, UTC completeness, and minimum days for `paired_fold_win_rate` (row 7) | open specification | `protocol_v1.yaml:202–204, 280–282`; packet `README.md` §4.1 `M5` | The `>= 0.60` fraction is computed over an undefined denominator | **BLOCKING — no candidate.** Estimand is moot until the fold unit exists | — | `STAT` | `A/R/X/D` |
| `D-07` | Estimand for the per-fold statistic once `D-06` closes | `E-IMPROV` / `E-DIFF` / decline | as `D-02` | Fold wins flip with the estimand | **`E-IMPROV`**, consistent with `D-02`–`D-04`; strictly dependent on `D-06` | As `D-02` | `STAT` | `A/R/X/D` |

## 3. Queue II — amendment-required rows (8–10)

| ID | Decision | Options | Evidence | Consequence if wrong | Recommended candidate | Falsifier | Authority | Response |
| --- | --- | --- | --- | --- | --- | --- | :---: | :---: |
| `D-08` | Resolve `pbo.series_matrix` (difference matrix, `237–239`) against `pbo.ranking_metric` (`paired_delta_sharpe`, `240`) | (a) read `240` as `E-DIFF`, amend wording; (b) store both legs, rank by `E-IMPROV`, amend the stored input; (c) keep blocked | `TECHNICAL_APPENDIX.md` §2 (matrix cannot yield `E-IMPROV`), §4 (total rank reversal on two trials); Lemma `L-1` | `phi` is computed from a different IS-best trial, changing the `<= 0.30` gate outcome | **(a)** — amends one clause's wording rather than the stored input and its schema; under (b), Lemma `L-1` reduces the ranking to the candidate's own Sharpe, contradicting the frozen justification at line 239 | A showing that `E-IMPROV` ranking preserves the incremental objective, or that joint legs are required for another reason | `§4` | `A/R/X/D` |
| `D-09` | PBO observation unit and minimum observations per block | (a) complete UTC day, minimum `<<UNRESOLVED>>`; (b) another frequency | `protocol_v1.yaml:237–239` names no frequency; every project Sharpe is daily | Blocks too short to admit a Sharpe make `phi` unavailable or, worse, silently degenerate | **(a)** for the unit — narrowest consistent choice; **BLOCKING** for the minimum | A frozen or owner-accepted statement of a different matrix frequency | `STAT` then `§4` | `A/R/X/D` |
| `D-10` | PBO exact-IS-tie rule | (a) uniform average over tied trials; (b) ascending preregistered trial ID | `DRAFT_AMENDMENT_PROPOSAL.md:129` proposes (a); the DSR draft's own tie rule is (b) | Trial naming order moves `phi` under (b); (a) and (b) are internally inconsistent across DSR and PBO | **(a)**, because registration order is an arbitrary artefact — but recorded as a decision because consistency with the DSR draft argues for (b) | A demonstration that (a) and (b) cannot disagree on admissible data | `STAT` | `A/R/X/D` |
| `D-11` | Complete lockbox specification: source representation, joint-leg resampling, `m` vs `n`, prediction statistic, quantile semantics, identity boundary, pass rule | seven sub-choices, listed in `METHOD_CANDIDATE.md` §6.3 | `protocol_v1.yaml:83–91`; Astra `B4`; `TECHNICAL_APPENDIX.md` §7 | The lockbox stage is unevaluable; any partial fix changes the meaning of the rest | **BLOCKING — no candidate, not even partial** | — | `§4` + `STAT` | `A/R/X/D` |
| `D-12` | Source of `paired_delta_sharpe_sign` in the coarse attestation (row 10) | derived from `D-11` / independent | `protocol_v1.yaml:77–78` | A sign from a different statistic leaks a non-equivalent result past the `PASS_FAIL_ONLY` boundary | **BLOCKING**, strictly dependent on `D-11` | — | `§4` | `A/R/X/D` |

## 4. Queue III — undefined rows (11–13)

| ID | Decision | Options | Evidence | Consequence if wrong | Recommended candidate | Falsifier | Authority | Response |
| --- | --- | --- | --- | --- | --- | --- | :---: | :---: |
| `D-13` | What CPCV diagnostic paths report (row 11) | (a) both estimands, separately labelled; (b) one; (c) nothing | `protocol_v1.yaml:215–222`, `role: diagnostic_only` | Choosing one silently creates a precedent for a gated row | **(a)** — binds nothing and gates nothing, so it is strictly narrower than choosing | A requirement that the CPCV report feed a gate | `STAT` | `A/R/X/D` |
| `D-14` | Pass event for the random-exposure null (row 12) | (a) realized `E-IMPROV` `>=` type-7 `0.95` quantile of the 500 null values; (b) another event; (c) keep blocked | `protocol_v1.yaml:134–140, 289` supplies metric name and threshold but no event | A mandatory promotion gate with no defined pass condition | **(a)** as `PROPOSED`, but the row remains **amendment-required** because adding the event changes frozen text | A clause already stating the event | `STAT` then `§4` | `A/R/X/D` |
| `D-15` | Pass statistic for `feature_delay_hard_gate` and `execution_delay_hard_gate` (row 13) | open | `protocol_v1.yaml:267–268, 284–285` name no statistic | Two mandatory boolean gates cannot be evaluated at all | **BLOCKING — no candidate.** Naming one here would author governance | — | `STAT` then `§4` | `A/R/X/D` |

## 5. DSR

| ID | Decision | Options | Evidence | Consequence if wrong | Recommended candidate | Falsifier | Authority | Response |
| --- | --- | --- | --- | --- | --- | --- | :---: | :---: |
| `D-16` | Effective trial count: which construct, and the fallback trigger | (a) frozen eigenvalue effective number (`232`); (b) `raw_trial_count` fallback (`233`), trigger `<<UNRESOLVED>>`; (c) `N^2/sum(R_ij^2)`; (d) keep blocked | The existing candidate `aqt.dsr.iid_raw_count.proposal.v1` uses the **fallback** without the primary ever being evaluated and without a protocol-stated trigger (Constitution §9 line 106 is the only frozen trigger text, and whether it applies to the named-but-undefined line-232 method is part of this decision); Astra `B1` refutes (c) for maxima | `S0` and every score move; a selection correction that does not correct | **BLOCKING — no candidate.** The three constructs are different functions and none is validated for maxima | A validity proof for one of them under selection over maxima | `STAT` then `§4` | `A/R/X/D` |
| `D-17` | Which count enters `A(N)`: `N_cycle`, `N_lifetime`, or `K` | three options | No source read determines it; `A` is monotone in `N` | Every DSR score shifts; lifetime accounting (`190`, Constitution §5) may or may not deflate the current cycle | **BLOCKING — no value supplied.** `dsr_minimum: 0.95` implies no default | A frozen clause or owner decision fixing the count | `STAT` then `§4` | `A/R/X/D` |
| `D-18` | Primary selection rule and primary error event | one event must be named | `DEC-02` in `DSR_CALIBRATION_RECONCILIATION.md`; `TECHNICAL_APPENDIX.md` §5 (max-Sharpe trial need not be max-DSR) | Calibration designed around one event bounds nothing about the other | **BLOCKING — no candidate** | Proof of score-order equivalence between the two events | `STAT` | `A/R/X/D` |
| `D-19` | The scientific claim attached to `score >= 0.95`, and its calibration | open | Astra `B1`–`B3`; `M6`; owner **DEFER**, 2026-09-18 | A mandatory promotion gate with an uninterpreted threshold | **BLOCKING — deferred by the owner. This candidate proposes no reconsideration** | — | `OWNER` then `STAT`, `§4` | `A/R/X/D` |

## 6. Implementation and process

| ID | Decision | Options | Evidence | Consequence if wrong | Recommended candidate | Falsifier | Authority | Response |
| --- | --- | --- | --- | --- | --- | --- | :---: | :---: |
| `D-20` | Bootstrap influence process and stream identity once any bootstrap-backed clause is bound, including refreshed deterministic reference vectors | (a) migrate with refreshed vectors and review; (b) reuse the Task 12 stream; (c) keep blocked | `IMPLEMENTATION_CONVENTIONS.md` §§"Paired-Sharpe influence", "RNG, resampling, and interval"; Astra `B5` | (b) silently changes every resample while keeping stale reference vectors | **(a)** if anything is bound at all; otherwise **(c)** | A demonstration that the block length is invariant to the estimand | `§16` + `STAT` | `A/R/X/D` |

## 7. Dependency order

`D-01` is independent. `D-02`, `D-03`, `D-04` are independent of each other but
should be decided together to avoid an incoherent Queue I. `D-07` requires
`D-06`. `D-09` and `D-10` require `D-08`. `D-12` requires `D-11`. `D-17` and
`D-18` require `D-16`. `D-19` dominates all DSR work and is currently deferred.
`D-20` is triggered by the first acceptance among `D-03` or `D-11`, the only two
bootstrap-backed rows; `D-08` (PBO, `protocol_v1.yaml:234–241`) uses no bootstrap
and does not trigger it.

Closing every row in this matrix would still not authorize Task 13, a
calibration engine, a governed trial, confirmation or lockbox access, promotion,
deployment, or trading.
