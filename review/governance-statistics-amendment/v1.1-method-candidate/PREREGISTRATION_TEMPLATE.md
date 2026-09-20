# Preregistration template — human-completed

**Status:** `EMPTY TEMPLATE — NOT A PREREGISTRATION — NO VALUE BELOW IS SUPPLIED`
**Companion to:** `METHOD_CANDIDATE.md`, `HUMAN_DECISION_MATRIX.md`

## How to read this file

Every field is either a **reviewable field** (the reviewer records what they
decide) or an **explicit placeholder** written as
`<<UNRESOLVED: D-xx — description>>`. A placeholder is not a blank waiting for a
default; it marks a choice for which this repository contains no supporting
evidence. **Nothing in this template is pre-filled with a candidate value.**
Where `METHOD_CANDIDATE.md` offers a `PROPOSED` candidate, it is referenced by
decision ID only, so that accepting it is a deliberate recorded act rather than
a silent inheritance.

A completed copy of this template is still not a preregistration until it is
signed by a qualified human and, where the row requires it, carried through the
Constitution §4 process. Completing every field authorizes nothing by itself.

**Completeness rule.** Any remaining `<<UNRESOLVED>>` token blocks execution of
whatever depends on it. An unresolved entry is never a permission to start.
No value is implied by `dsr_minimum: 0.95`, `pbo_maximum_if_enabled: 0.30`, or
any other frozen threshold.

## 1. Registration identity

| Field | Value |
| --- | --- |
| Registration title | `<<UNRESOLVED: human-supplied>>` |
| Registering human (name, role, qualification) | `<<UNRESOLVED>>` |
| Independent reviewer (name, model or human, independence basis) | `<<UNRESOLVED>>` |
| Date/time UTC of registration | `<<UNRESOLVED>>` |
| Repository commit pinned by this registration | `<<UNRESOLVED>>` |
| SHA-256 of the method document this registration binds | `<<UNRESOLVED>>` |
| Scope: this registration covers | `<<UNRESOLVED: enumerate the row numbers of the canonical 13-row object it covers; partial coverage is permitted and must be stated>>` |
| Scope: this registration explicitly does **not** cover | `<<UNRESOLVED>>` |

## 2. Estimand registration (`D-01`)

| Field | Value |
| --- | --- |
| `E-IMPROV` registered as a distinct named estimand | `ACCEPT / REVISE / REJECT` — `<<UNRESOLVED>>` |
| `E-DIFF` registered as a distinct named estimand | `ACCEPT / REVISE / REJECT` — `<<UNRESOLVED>>` |
| Identifier assigned to each | `<<UNRESOLVED>>` |
| Observation unit, variance denominator, annualization constant, leg-compounding order | `<<UNRESOLVED: confirm the Task 12 conventions apply unchanged, or state the change>>` |
| Substitution prohibition recorded | `YES / NO` — `<<UNRESOLVED>>` |

## 3. Per-consumer bindings — rows 1–13

One row per consumer. `Decision` is one of `ACCEPT_CANDIDATE`, `REVISE`,
`REJECT`, `DEFER`. `Estimand` must be written out; it is never inferred from a
neighbouring row.

| Row | Consumer | Decision | Estimand recorded | Rationale (mandatory) | Amendment required? |
| ---: | --- | --- | --- | --- | --- |
| 1 | DSR input series | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |
| 2 | OOS/IS in-sample statistic | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |
| 3 | ETH sanity gate (`D-02`) | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |
| 4 | BTC 2x cost stress (`D-02`) | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |
| 5 | Paired CI and BTC lower bound (`D-03`) | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |
| 6 | Parameter plateau (`D-04`, `D-05`) | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |
| 7 | Three-month fold wins (`D-06`, `D-07`) | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |
| 8 | PBO ranking metric (`D-08`) | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |
| 9 | Lockbox prediction and pass rule (`D-11`) | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |
| 10 | Lockbox attestation sign (`D-12`) | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |
| 11 | CPCV diagnostic paths (`D-13`) | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |
| 12 | Random-exposure null (`D-14`) | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |
| 13 | Feature / execution delay gates (`D-15`) | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` | `<<UNRESOLVED>>` |

Additional mandatory entries:

| Field | Value |
| --- | --- |
| Plateau rule behaviour when the selected value is `<= 0` (`D-05`) | `<<UNRESOLVED>>` |
| Fold anchoring rule (`D-06`) | `<<UNRESOLVED>>` |
| Fold UTC-completeness rule (`D-06`) | `<<UNRESOLVED>>` |
| Minimum days per reporting fold (`D-06`) | `<<UNRESOLVED>>` |
| Treatment of the final partial reporting block | `<<UNRESOLVED: confirm protocol_v1.yaml:202–204 applies unchanged, or state the change>>` |

## 4. DSR

| Field | Value |
| --- | --- |
| Method identity and version | `<<UNRESOLVED>>` |
| Exact equation accepted as written in `METHOD_CANDIDATE.md` §3.1 | `ACCEPT / REVISE / REJECT` — `<<UNRESOLVED>>` |
| Input column definition | `<<UNRESOLVED: state the estimand and the annualization state explicitly>>` |
| Moment conventions (`g`, `k`, denominators) | `<<UNRESOLVED>>` |
| Trial-count event definition (`METHOD_CANDIDATE.md` §3.2) | `ACCEPT / REVISE / REJECT` — `<<UNRESOLVED>>` |
| Effective trial count construct (`D-16`) | `<<UNRESOLVED: eigenvalue / raw count / participation ratio / blocked>>` |
| Fallback trigger condition for `raw_trial_count` (`D-16`) | `<<UNRESOLVED>>` |
| Count entering `A(N)` (`D-17`) | `<<UNRESOLVED: N_cycle / N_lifetime / K>>` |
| Cross-trial dispersion `V` definition and its unavailable branch | `<<UNRESOLVED>>` |
| Primary selection rule (`D-18`) | `<<UNRESOLVED>>` |
| Primary error event and its denominator (`D-18`) | `<<UNRESOLVED>>` |
| Scientific claim attached to `score >= 0.95` (`D-19`) | `<<UNRESOLVED — owner DEFER stands, 2026-09-18>>` |
| Reason-code set and precedence | `<<UNRESOLVED: confirm the nine codes and order in DSR_CALIBRATION_RECONCILIATION.md apply unchanged, or state the change>>` |
| Single-attempt branch (`N_cycle = N_lifetime = K = 1`) | `<<UNRESOLVED>>` |
| Independent deterministic reference vectors and their author | `<<UNRESOLVED>>` |
| Calibration status | `<<UNRESOLVED — no calibration exists; do not record "not applicable">>` |

## 5. PBO

| Field | Value |
| --- | --- |
| Method identity and version | `<<UNRESOLVED>>` |
| Activation threshold | `<<UNRESOLVED: confirm 20 current-family evaluated trials, protocol_v1.yaml:235>>` |
| Observation unit (`D-09`) | `<<UNRESOLVED>>` |
| Block count and remainder placement | `<<UNRESOLVED: confirm 16 blocks, protocol_v1.yaml:236>>` |
| Minimum observations per block, and behaviour below it (`D-09`) | `<<UNRESOLVED>>` |
| Split enumeration | `<<UNRESOLVED: confirm all 12,870 oriented halves, both orientations>>` |
| Ranking metric (`D-08`) | `<<UNRESOLVED>>` |
| IS exact-tie rule (`D-10`) | `<<UNRESOLVED: uniform average / ascending trial ID>>` |
| OOS tie rule | `<<UNRESOLVED>>` |
| `omega` and logit scoring convention, including the zero-logit branch | `<<UNRESOLVED>>` |
| Missing or invalid trial, split, or observation behaviour | `<<UNRESOLVED>>` |
| Matrix alignment requirements | `<<UNRESOLVED>>` |
| `phi` aggregation and gate comparison | `<<UNRESOLVED: confirm arithmetic mean over all splits, compared against the frozen maximum 0.30>>` |

## 6. CPCV, ESS, and bootstrap

| Field | Value |
| --- | --- |
| CPCV reported statistics per path (`D-13`) | `<<UNRESOLVED>>` |
| CPCV role confirmation | `<<UNRESOLVED: confirm diagnostic_only with no promotion gate>>` |
| ESS method and fallback | `<<UNRESOLVED: confirm the Task 12 Newey-West construction applies unchanged>>` |
| Confirmation that ESS never substitutes for `T` or for the PBO matrix length | `YES / NO` — `<<UNRESOLVED>>` |
| Bootstrap influence process per bound clause (`D-20`) | `<<UNRESOLVED>>` |
| Politis-White block-length derivation per bound clause (`D-20`) | `<<UNRESOLVED>>` |
| Stream identity, purpose token, output length, attempt count (`D-20`) | `<<UNRESOLVED>>` |
| Refreshed deterministic reference vectors: author, values, tolerance (`D-20`) | `<<UNRESOLVED>>` |
| Lockbox prediction bootstrap, if any (`D-11`) | `<<UNRESOLVED — all seven sub-choices in METHOD_CANDIDATE.md §6.3>>` |

## 7. Failure behaviour and invariants

| Field | Value |
| --- | --- |
| Fail-closed contract accepted (`INDETERMINATE`/`BLOCKED`, never `PASS`) | `YES / NO` — `<<UNRESOLVED>>` |
| `NO_EDGE_FOUND` and `KEEP_BLOCKED` recorded as valid outcomes | `YES / NO` — `<<UNRESOLVED>>` |
| Invariants `I-1`–`I-9` (packet §6) preserved | `YES / NO` — `<<UNRESOLVED>>` |
| Invariants `I-10`–`I-12` (`METHOD_CANDIDATE.md` §7) accepted | `ACCEPT / REVISE / REJECT` — `<<UNRESOLVED>>` |
| Frozen thresholds untouched | `YES / NO` — `<<UNRESOLVED>>` |
| No-pooling of prior-cycle matrices confirmed | `YES / NO` — `<<UNRESOLVED>>` |

## 8. Governance and authorization state after completion

| Field | Value |
| --- | --- |
| Rows requiring the Constitution §4 process | `<<UNRESOLVED>>` |
| §4 steps completed, if any | `<<UNRESOLVED — none as of this template>>` |
| Owner-of-record signature and date | `<<UNRESOLVED>>` |
| Cycle status | `<<UNRESOLVED — C1 has never started>>` |
| DSR gate status | `<<UNRESOLVED — diagnostic-only; dsr_minimum: 0.95 unsatisfied>>` |
| Task 13 | `NOT AUTHORIZED by this document` |
| Simulation or calibration engine | `NOT AUTHORIZED by this document` |
| Confirmation or lockbox data access | `NOT AUTHORIZED by this document` |
| Governed trial, eligibility decision, promotion, deployment, trading | `NOT AUTHORIZED by this document` |

The four rows above are fixed statements of fact about *this* template, not
fields for a reviewer to change. Authorizing any of them requires the applicable
owner and Constitution process, recorded elsewhere.
