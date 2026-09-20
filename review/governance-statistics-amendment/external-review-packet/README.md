# External statistical review packet — paired Sharpe estimand bindings

**Status:** `UNSIGNED REVIEW REQUEST — NOT AN AMENDMENT — NOT ACCEPTED — NOT ACTIVE`
**Prepared:** 2026-09-20
**Prepared by:** Claude, exact observed model ID `claude-opus-5`, read-only
documentation task, AI author. (Claude Opus 5.1 was the preferred author model;
the model metadata actually observed in the preparing and revising sessions is
`claude-opus-5`, and is recorded here as observed rather than as preferred.)
**Independent reviews received:** `claude-fable-5-1`, verdict
`REVISION_REQUIRED` (`CLAUDE_FABLE_5_1_REVIEW.md`), then, after the corrections,
`claude-fable-5-1` closure review, verdict `PASS_WITH_ADVISORIES` with one LOW
advisory (`CLAUDE_FABLE_5_1_CLOSURE_REVIEW.md`) — both adjudicated in
`REVIEW_ADJUDICATION.md`. Neither is human or statistician acceptance, and
neither authorizes any governance or trading action.
**Repository HEAD at preparation:** `fad5564044f6d368029bcf153fd879ec04f97fe4`
**Recommended verdict carried into review:** `KEEP_BLOCKED` (see §4)

## 1. What this packet is

`autonomous-quant-trader` operates under a frozen v1.0 Research Constitution and a
frozen cycle protocol (`protocols/protocol_v1.yaml`, `status: "FROZEN"`, cycle
`C1`). The protocol requests a paired Sharpe-like statistic in **thirteen**
distinct clause groups — enumerated once, as rows 1–13 of the canonical decision
object in `STATISTICAL_BINDING_CANDIDATE.md` §5 — and defines an estimator for
none of them. Two of the thirteen (rows 1–2) name the paired *difference series*
explicitly and are settled; the other **eleven** (rows 3–13) request the quantity
the protocol calls **paired delta-Sharpe**, eight of them using that literal
token and three referring to it without it (`STATISTICAL_BINDING_CANDIDATE.md`
§4 gives the line numbers). Every
count in this packet resolves to those row numbers. Two mathematically distinct
estimands already exist in the project's inactive Task 12 implementation, and the
frozen clauses are not all satisfiable by the same one. No governed research,
trial, promotion, or trading has occurred; cycle C1 never started.

This packet is a request for one bounded scientific judgement from a qualified
external statistician. It assembles, in reviewable form:

| File | Contents |
| --- | --- |
| `README.md` | Cover, exact review request, scope boundary, source inventory and hashes |
| `STATISTICAL_BINDING_CANDIDATE.md` | Symbols, units, estimands, inputs/outputs, the canonical thirteen-row consumer decision object, invariants, and comparison of four admissible routes |
| `TECHNICAL_APPENDIX.md` | Five deterministic worked examples establishing non-identifiability, sign disagreement, rank reversal, and selection-event non-equivalence; explicit separation of DSR, PBO, paired difference-series Sharpe, and paired Sharpe improvement |
| `REVIEWER_DECISION_FORM.md` | Accept / revise / reject questions, required rationale, packet byte verification, conflict disclosure, signature and date |
| `CLAUDE_FABLE_5_1_REVIEW.md` | Verbatim record of the independent `claude-fable-5-1` review: reviewer metadata, verdict `REVISION_REQUIRED`, its independent checks, and findings F-01 to F-06 |
| `CLAUDE_FABLE_5_1_CLOSURE_REVIEW.md` | Record of the independent `claude-fable-5-1` closure review after those corrections: verdict `PASS_WITH_ADVISORIES`, F-01 to F-06 closed, one LOW advisory F-07 |
| `REVIEW_ADJUDICATION.md` | Author response to each finding — AGREE / PARTIAL / DISAGREE, the exact correction applied, and the evidence |
| `MANIFEST.sha256` | SHA-256 of the seven Markdown files above, generated after they were final; it does not hash itself |
| `.gitattributes` | Packaging integrity only: pins LF line endings for this directory so `MANIFEST.sha256` stays verifiable after a checkout on Windows (`core.autocrlf=true`). It is not hashed, because the manifest contract covers every Markdown file and nothing else |

Read `STATISTICAL_BINDING_CANDIDATE.md` first, then `TECHNICAL_APPENDIX.md`, then
`CLAUDE_FABLE_5_1_REVIEW.md` and `CLAUDE_FABLE_5_1_CLOSURE_REVIEW.md` with
`REVIEW_ADJUDICATION.md`, then complete
`REVIEWER_DECISION_FORM.md`. The packet is self-contained for the binding
question but deliberately does not restate the source documents; §5 lists them.

## 2. The exact question

> **Q.** Given the frozen v1.0 protocol wording, can the eleven remaining paired
> delta-Sharpe consumers — rows 3–13 of the canonical decision object in
> `STATISTICAL_BINDING_CANDIDATE.md` §5 — be bound
> to estimators by scientific reasoning alone — that is, without changing any
> frozen input, threshold, or clause meaning — and if so, to which estimator is
> each consumer bound?
>
> If they cannot, state which consumers are blocked, whether each is blocked by
> *missing information* (a definition a statistician may supply) or by
> *incompatible frozen text* (requiring the Constitution §4 amendment process),
> and the minimum set of facts or governance choices that would unblock each one.

Subsidiary questions, each answerable independently, are enumerated in
`REVIEWER_DECISION_FORM.md` §2.

## 3. What this packet is not, and does not request

This document is a review request written by an AI. It is explicitly **not**:

- a formal amendment, or any part of the Constitution §4 amendment process
  (version bump, written rationale, owner-of-record signed and dated commit,
  cycle termination, pre-new-cycle activation, preserved history, no retroactive
  effect) — `docs/RESEARCH_CONSTITUTION.md` §4;
- human, owner, or statistician acceptance of any statistical method, and it does
  not create, imply, or substitute for such acceptance;
- authorization for Task 13, a calibration engine, any simulation or Monte Carlo
  run, or any code change;
- authorization for confirmation-partition or lockbox data access, a governed
  trial, an eligibility decision, promotion, deployment, or trading;
- a claim that any DSR method is calibrated. Under
  `OWNER_DSR_DEFER_DECISION.md` (2026-09-18, owner decision **DEFER**) DSR remains
  diagnostic-only, the mandatory `dsr_minimum: 0.95` promotion gate remains
  unsatisfied, and promotion remains blocked regardless of the answer here;
- a resolution of Astra findings B1–B5 (`ASTRA_REVIEW.md`) or of DEC-01 to DEC-03
  (`DSR_CALIBRATION_RECONCILIATION.md`). Answering the binding question closes
  none of them.

A reviewer who answers only "the evidence does not support a single binding" has
given a complete and useful answer. `KEEP_BLOCKED` and `NO_EDGE_FOUND` are valid
scientific outcomes in this project.

No frozen artifact, sidecar, `FROZEN_HASHES.json` entry, source file, test, or
pre-existing review record was modified in preparing this packet, or in revising
it after the `claude-fable-5-1` reviews; only the nine files in this directory
were added or edited, and nothing outside this directory was touched.

## 4. Recommendation carried into review

**`KEEP_BLOCKED` for any single universal binding of "paired delta-Sharpe".**

The two candidate estimands are not merely different parameterizations: neither is
a function of the other's stored inputs (`TECHNICAL_APPENDIX.md` Examples A and
A2), they disagree in **sign** on admissible daily data (Example B), and they
produce **opposite** trial rankings on the same data (Example C). Because
`validation.dsr.series` and `validation.oos_is_ratio.in_sample_definition` name a
difference series explicitly while `lockbox_policy.prediction_interval` names a
difference series *and* asks for a delta of Sharpes, no single estimand satisfies
the frozen text everywhere. That is an internal incompatibility in v1.0, not an
open modelling choice.

**The narrowest scientifically defensible next decision** — the only one this
packet recommends — is a single bounded, minuted decision by a qualified
human statistician that does no more than:

1. **Register two distinct named quantities** (`E-IMPROV`, `E-DIFF`) as separate
   estimands with the definitions in `STATISTICAL_BINDING_CANDIDATE.md` §3. This
   is a naming and disambiguation act, not a binding of any gate.
2. **Confirm the two already-explicit frozen inputs** — rows 1–2 of the canonical
   decision object: DSR consumes the candidate-minus-comparison difference
   series; the OOS/IS in-sample statistic is the training-window Sharpe of the
   difference series — and record that substituting `E-IMPROV` into either is out
   of scope without a formal amendment. These two rows are *settled*, not queued.
3. **Partition the eleven remaining consumers — rows 3–13 — into three disjoint
   queues**, without binding any of them. The queue membership is normatively
   defined in `STATISTICAL_BINDING_CANDIDATE.md` §5 and is only summarised here:
   - *Queue I — interpretive (rows 3–7, five rows):* the frozen text is silent on
     the estimator, so a statistician could later supply one without
     contradicting v1.0 (`eth_gate`/`eth_sanity_rule`, `survive_2x_cost_rule`,
     `paired_confidence_interval` with `btc_min_sharpe_delta_ci_lower_bound`,
     `plateau.pass_rule`, `paired_fold_win_rate`).
   - *Queue II — amendment-required (rows 8–10, three rows):* a statistic **is**
     named, but it cannot be computed from the frozen stored input, so any
     binding changes frozen text (`pbo.ranking_metric` against
     `pbo.series_matrix`; `lockbox_policy.prediction_interval` construction and
     `pass_rule`; `attestation_coarse_fields`).
   - *Queue III — undefined (rows 11–13, three rows):* the clause names **no**
     pass statistic at all, so there is nothing to bind and choosing an estimand
     would not make the row evaluable (`cpcv.role`;
     `null_models.random_exposure`; `feature_delay_hard_gate` and
     `execution_delay_hard_gate`). These are *information first, then
     governance* (M4 below): a statistician must first name a pass statistic, and
     only the resulting change to frozen text is a Constitution §4 question.
     Queue III is kept distinct from Queue II precisely because merging them
     would assert that rows 11–13 already name a statistic, which they do not.

   Counts, for audit: `2 settled + 5 + 3 + 3 = 13`; eleven remaining.
4. **Record that nothing else changes.** Queue I remains unbound, Queue II remains
   an amendment question, Queue III remains without a pass statistic, DSR stays
   diagnostic-only, and the pause holds.

Even this decision is not proposed for adoption here; it is the option this packet
asks the reviewer to accept, revise, or reject. Rejecting it in favour of simply
retaining the current pause is an acceptable outcome and requires no follow-up
work.

### 4.1 Minimum information or governance choices required to go further

Listed once, and not repeated elsewhere in the packet:

| # | Requirement | Type | Who can supply it |
| --- | --- | --- | --- |
| M1 | An authoritative reading of "paired delta-Sharpe" for each Queue I clause, with the estimand named and the reason recorded | Information | Qualified human statistician |
| M2 | A decision on whether `pbo.series_matrix` (difference matrix) or `pbo.ranking_metric` (`paired_delta_sharpe`) governs when they conflict; ranking by `E-IMPROV` requires storing both legs, which the frozen matrix does not | Governance (amendment) | Constitution §4 process |
| M3 | A lockbox specification fixing source representation, joint-leg resampling, target length `m` versus source length `n`, the prediction statistic, quantile semantics, the identity boundary, and the pass rule — Astra B4 | Governance (amendment) + information | §4 process after statistician review |
| M4 | Pass statistics for `cpcv.role` paths, `null_models.random_exposure`, `feature_delay_hard_gate` and `execution_delay_hard_gate` — the whole of Queue III (rows 11–13), none of which the frozen text binds to a Sharpe estimand | Information, then governance | Statistician, then §4 process |
| M5 | Fold anchoring, UTC-completeness, and minimum-days rules for `paired_fold_win_rate` before its estimand matters | Information | Statistician |
| M6 | A complete, independently calibrated DSR procedure — selection event, effective trial count, finite-sample branches, and the claim attached to 0.95 — Astra B1–B3, DEC-02 | Information (calibration) | Deferred by owner decision 2026-09-18 |
| M7 | A human-authored final statistical specification bound to a reviewed implementation and hash, with refreshed deterministic bootstrap reference vectors — Astra B5 | Governance + engineering | Human author; §16 different-model and human PR review for protected code |
| M8 | Owner-of-record signed and dated activation commit, cycle termination, and version bump | Governance | Owner of record only |

M1 and M5 are the only items a statistician can close alone. M2–M4 and M7–M8 are
governance acts that no reviewer, and no AI, can perform.

## 5. Source inventory

Every source read in preparing this packet is listed below with the SHA-256 of its
working-tree bytes at HEAD `fad5564044f6d368029bcf153fd879ec04f97fe4`. Hashes are
over raw file bytes as checked out on Windows with LF line endings; they are not
canonicalized and must not be compared to hashes computed after a line-ending
conversion. Paths are repository-relative.

### 5.1 Frozen governance (read-only; unchanged by this packet)

| SHA-256 | Path |
| --- | --- |
| `776396a25012276f22c4d7478166614e2f4f58e1a866e274ff8437e60cc09516` | `docs/RESEARCH_CONSTITUTION.md` |
| `d22efb8989cb31a1d673000bba1e69baf5e0965bb400a8798aa966a3035d8b26` | `protocols/protocol_v1.yaml` |
| `962bdb5096ae191556933cdde940d34f1548261f2ee9a7be65b523208b26912d` | `FROZEN_HASHES.json` |

### 5.2 Project instructions, skill, verifier, and implementation

| SHA-256 | Path |
| --- | --- |
| `ab4cb23eefec99207165c35e19727a12ca439e42741c01130b7db24d4dc0474b` | `AGENTS.md` |
| `627e27aaf531327c8e072bf361d72d6f287cbb6e3ec0fb4f8baab659450d97f6` | `.agents/skills/statistical-binding-review/SKILL.md` |
| `796ea6b60745fe4af6a2e76445d6f238f6b9236eb860b0371e13cd2feb0803e3` | `review/task6/verify_frozen.ps1` |
| `e8cd22385b978c49b2d0ba5b15f8760b179226b86fea70fdb027d9c382044bad` | `src/aqt/metrics/statistics.py` |

### 5.3 Task 11 and Task 12 records

| SHA-256 | Path |
| --- | --- |
| `20d1b17306b6f676eea8c1d260a42e62ec1cd9efafec88ec290d5fb4b589b645` | `review/task11/SCIENTIFIC_DECISION.md` |
| `f3ba9362c5f1512fd24600775df2aa048a7e701c8f40c8cb00e97c2c644f515c` | `review/task12/IMPLEMENTATION_CONVENTIONS.md` |
| `1c686bcf61b4851f336b270c4e437d01e6a81459cbe3e6b86325c692e058d600` | `review/task12/OWNER_DECISION.md` |

### 5.4 Paired-Sharpe usage and adjudication records

| SHA-256 | Path |
| --- | --- |
| `05f771973a23c159c615a9e9dd5cc0e71e1cc1e196f740f79436f7df572b7621` | `review/estimand-disambiguation/PAIRED_SHARPE_USAGE_RECORD.md` |
| `d1426e3c667df8a887ef60fa6b7a6e00c47486daa25c2d198250217d425b10a3` | `review/estimand-disambiguation/REVIEW_ADJUDICATION.md` |

### 5.5 `review/governance-statistics-amendment/` (complete directory as of HEAD)

| SHA-256 | Path (prefix `review/governance-statistics-amendment/`) |
| --- | --- |
| `2568ef63c397eb21feb4d71341a2d1bff4ab8319d612ad6f36eea943bba05ad3` | `ASTRA_CALIBRATION_PREREGISTRATION_REVIEW.md` |
| `0701e642e6cb12e60e28a3b45591235852b4d43113f2243375a15e20b1ff487f` | `ASTRA_DESIGN_REVIEW.md` |
| `92be40273751c4f21bdb4cd067fba978b8c674cd7be515c259cbdabc1cebf2a0` | `ASTRA_REVIEW.md` |
| `3f3f45ccfcaccbdb4a234cdda46672a245d4eed66246cb5b36047101b0f547cd` | `BINANCE_LOCKBOX_REVIEW.md` |
| `3152742ecb9ca884cd8bd776fbb631e381ee7bc5944a12f38f6e495a84ab1e66` | `BINANCE_QUANT_REVIEW.md` |
| `f6bdb1d50ef557da39f450ea7df8fe9d9117c83b24cceea460c66505e91f9a5d` | `CALIBRATION_PREREGISTRATION_DRAFT.md` |
| `9dff6580938d8bf435a873eb3d4e507cf5c9f3266051ea2a1543ba455c4a92f9` | `DESIGN_GATE.md` |
| `6aaa2cab0e3da51dbede9e2ce11f7404d09cb6bf431b2c17e3df12a59cd03979` | `DRAFT_AMENDMENT_PROPOSAL.md` |
| `6a9a764b056fffc6a7efcf56a340cea90262359dd00876fa2e5d3ad34d0e49cc` | `DSR_AGENT_REVIEW_ADDENDUM.md` |
| `c0120d23eea20f37ce951be5436cec19ce19538eb19f04decf4094c71e5c2c4b` | `DSR_CALIBRATION_PLAN.md` |
| `4017d27d784e81db18245aae233e5cfc025ccffcc2c5bcff3184b78f0da47da8` | `DSR_CALIBRATION_RECONCILIATION.md` |
| `b0854fdc6444936b277a8188d2954224525ff7225bb1d00e9d17de3a31639568` | `DSR_DRAFT_REVIEW_PACKET.md` |
| `1391f81edbcfdb2aaad2d49d8c0843688514b5c224dfc4e9f4d8332cdd00ce91` | `DSR_METHOD_PREREGISTRATION_DRAFT.md` |
| `1234bee0e962306c1041588a57f2d091b4f14ef79fd05b552b5f39429e36d4d1` | `DSR_RECONCILIATION_REVIEW_PACKET.md` |
| `b5f5de16adb9538725a9b5c1219b00ef5dfaa74e3e8550f2395d5cb232ef9324` | `INDEPENDENT_REVIEW_PACKET.md` |
| `2c9dc1bcf6bc0b33574b9825df8f9337ec61fd1a45c28ad52c0b0d694f59f8af` | `LOCAL_REVIEW.md` |
| `17c7945c3ed2b5ffb8c678bd2d03487bb8f49ef4f52257b5662ed4bccf1ebc17` | `LOCKBOX_PREDICTION_PROPOSAL.md` |
| `5d205127511a9e8d1c4972b51a3b405dfb852d4259e74bb6654e5a14d2b9d1e2` | `OWNER_ACTION_CHECKLIST.md` |
| `dc0e77f9a6b85c68f7eb9de49520bb5660a6a590b38501513864a0c5403570d2` | `OWNER_DECISION.md` |
| `8aee76b499f8c3b3fc851e541da7622d649437c6da7ce01071a5a84515c35531` | `OWNER_DSR_DEFER_DECISION.md` |

Five of these hashes (`DSR_CALIBRATION_RECONCILIATION.md`,
`CALIBRATION_PREREGISTRATION_DRAFT.md`,
`ASTRA_CALIBRATION_PREREGISTRATION_REVIEW.md`, `OWNER_ACTION_CHECKLIST.md`,
`OWNER_DSR_DEFER_DECISION.md`) reproduce exactly the values independently recorded
in `DSR_RECONCILIATION_REVIEW_PACKET.md` lines 24–28, confirming those bytes are
unchanged.

## 6. Deterministic checks run while preparing this packet

Exact commands and results are recorded once, in `REVIEWER_DECISION_FORM.md` §5,
and cover: frozen protected-byte and inventory verification against the Task 1
baseline; frozen manifest and protocol hash bindings; packet link and path
resolution; generation and re-verification of `MANIFEST.sha256` over all seven
packet Markdown files; `git diff --check`; and `git status --short`. That section
also records, explicitly, which step of `review/task6/verify_frozen.ps1` could not
be re-executed in the preparing session and why that does not weaken the result.
`REVIEWER_DECISION_FORM.md` §5.1 supplies the reviewer-completed byte
verification for every manifest entry and for `MANIFEST.sha256` itself.

Tests, Ruff, mypy, and import-linter are not applicable: this packet adds review
Markdown only and changes no executable code, configuration, or import boundary.
No simulation was run, no network or exchange access occurred, and no credentials,
confirmation data, or lockbox data were touched.
