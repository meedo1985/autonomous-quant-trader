# RESEARCH_CONSTITUTION.md
## autonomous-quant-trader — Research Constitution v1.0

**Status:** FROZEN  
**Effective date:** 2026-09-11  
**Hash canonicalization spec:** `schemas/HASH_CANONICALIZATION_v1.md`  
**Hash canonicalization spec SHA-256:** `189e3525c5c63f9605f739386aa3edc16b7bf44b5f4f7196dd7f698c9fbdc3cf`  
**Content hash:** `4cb6c7d35e238bdd778e8dd74b25d1b978e57fedffdbfae83b2867b5ec4fb8d7`

## §0 Definitions
Cycle = bounded period governed by one immutable protocol hash.  
Family = named hypothesis class with current-cycle and lifetime trial accounting.  
Trial = registered evaluation counted when evaluation begins.  
Hypothesis = immutable preregistered claim with hash/lineage.  
Candidate = hypothesis/model passing non-lockbox eligibility.  
Benchmark = fixed comparison strategy.  
Deployable baseline = exactly one protocol-designated benchmark eligible for the NO_EDGE_FOUND path.  
Exploration partition = data available for free-form biased exploration.  
Confirmation partition = data available only through the registered experiment engine.  
Lockbox = future data readable only by lockbox_eval.  
Promotion = eligibility → lockbox → signed attestation.  
Incident = HALT, reconciliation mismatch, unexplained exposure, ambiguous order, credential anomaly, or comparable safety event.

## §1 Purpose
Build a scientifically defensible, reproducible, cost-aware, risk-controlled crypto spot exposure platform.

**NO EDGE FOUND is acceptable.**

Passing validation means only failure to falsify under the tests actually run.

Success criteria may not be redefined after results; §§5 and 13 enforce this.

## §2 Scope
Binance Spot; BTC/USDT and ETH/USDT initially; exposure per asset in [0,1]; no shorting, margin, futures, leverage, withdrawals, RL, deep learning without a later Constitution-compliant amendment, autonomous production promotion, or LLM in the live decision path.

BTC+ETH agreement is a sanity check, not independent replication.

Known incompletely modelable risks include custody/insolvency, stablecoin depeg, venue/regulatory action, account-access loss, rule changes, and extreme discontinuities.

## §3 Governance
Constitution → Schemas/Threat Model → Cycle Protocol → Hypothesis → Experiment → Artifacts.

This binds owner, humans, AIs, and software.

Scientific/safety-relevant schema or threat-model changes during a cycle follow the protocol-change rule and end that cycle.

## §4 Amendment rule
Amendment requires version bump, written rationale, owner-of-record signed/dated commit, cycle termination, pre-new-cycle activation, preserved history, and no retroactive effect on open promotions.

Research/coding AI may propose but not author/merge/activate/self-approve amendments.

No protocol may set capital-increase cooling-off, risk-loosening cooling-off, or safety-amendment activation delay below **72 hours**.

`owner_change_control` is governed by this Constitution, not ordinary protocol editing.

Safety-clause amendments cannot be proposed/activated during an open incident or post-HALT cooling-off.

## §5 Cycle rule
One frozen protocol hash per cycle.

Every cycle protocol must define family-budget exhaustion, calendar/time limit, and candidate-promotion termination. Otherwise invalid.

Outcomes: `CANDIDATE_PROMOTED`, `NO_EDGE_FOUND`, `PROTOCOL_REVISION`, `INVALIDATED`.

Invalidation voids scientific results but not lockbox exposure or lifetime trial counts.

Prior-cycle results are not pooled into later DSR/PBO matrices; lifetime trial counts persist.

## §6 Data invariants
Raw immutable; no silent deletion/correction; outages untradeable; full hash lineage; causal time semantics; no future leakage; features versioned; point-in-time fees/filters/status where available; UTC only; one tested bar-semantics module.

## §7 Lockbox
Only lockbox_eval reads it.

Research/coding environments receive no raw lockbox data or full diagnostics.

Access requires ELIGIBLE; every read consumes budget, logs, creates evaluation ID, and marks segment EXPOSED.

Research receives PASS/FAIL only.

Exposed segments never re-lock and roll forward only into **confirmation**. Lockbox boundary only moves forward.

Exploration/confirmation boundary changes only between cycles and only forward.

After LOCKBOX_FAIL, descendants cannot request another lockbox read in that cycle.

## §7a Exploration/confirmation
Sandbox mounts exploration only.

Confirmation is accessible only through the registered experiment engine.

Sandbox receives only metrics.json, 3-month fold aggregates, and report.md from confirmation.

Per-bar confirmation returns/equity/trades remain under experiment-engine identity.

## §8 Hypotheses
Immutable after preregistration. Required fields include ID/hash/family/creator/target/horizon/bar+decision frequency/feature hash/exposure mapping/rebalance rule including band+min hold/cost hash/training rule/retrain hash/grid/protocol hash/parent lineage.

Hashes follow §27 canonicalization.

## §9 Trials
Count when evaluation begins; aborted evaluated runs count.

All failures count. Lifetime family accounting persists.

If no frozen effective-count method exists, raw count is used.

Exploration is not a registered trial because it is confined to exploration data.

## §10 Benchmarks
Fixed, hashed, untuned, and evaluated under identical bar semantics, comparison benchmark, cost model, execution baseline, and applicable band/min-hold rules.

## §11 NO_EDGE baseline
Exactly one deployable baseline named before cycle. Changing it ends cycle.

Exempt only from beating itself; all live-safety, paper, reconciliation, canary, owner, and cooling-off gates still apply.

## §12 Vol-managed constraint
Spot max exposure 100% means vol management is **de-risking, not alpha**. It may lag B&H in bull markets and this alone is not grounds for override.

## §13 Promotion
`eligibility_gate → lockbox_request → promotion_attestation`.

Attestation binds constitution/protocol/hypothesis/benchmark/cost/feature/data-manifest/backtester hashes, eligibility ID, lockbox ID, and cooling-off start.

Human decision: `APPROVE_AS_IS` or `REJECT` only.

## §14 Owner clauses
Risk increases require formal review/cooling-off.

Risk reductions are immediate: reduce capital, tighten limits, kill, HALT, FREEZE.

HALT override requires: written incident record, identified or bounded cause, successful reconciliation, explicit owner action, and timestamp.

Trading resumes only after incident closure plus successful reconciliation.

## §15 Research AI
Exploration only; aggregate confirmation artifacts only; no direct confirmation/lockbox; no protected-code writes; no credentials/live access; Cycle-1 network denied.

## §16 Coding AI
Untrusted.

Backtester order: human spec review → oracle tests → leakage canaries → NumPy reference → production implementation.

Accepted oracle/canary tests are frozen; changes require human rationale/review.

The following **enumerated components** require different-model + human PR review before merge:
- validation engine
- promotion gate
- governor
- executor state machine
- lockbox ACL tooling
- protocol-enforcement logic

Tests/fixtures use only synthetic or exploration data.

## §17 Import boundaries
CI enforces: research !→ governor/execution/lockbox_eval; governor !→ execution/model-training; execution !→ research/model-training; live !→ AI-agent code.

## §18 Backtester trust
Must pass analytic identities, zero exposure, known turnover, cost monotonicity, future-feature canary, lagged-feature canary, shuffled-label null, NumPy reference, deterministic rerun.

Any backtester change creates a new hash and reruns the suite.

## §19 Live path
predictor → governor → executor → exchange.

Alerting before shadow. Startup reconciliation required. Config/hash mismatch → REFUSE_START.

Separate deployment protocol required before shadow.

## §20 Governor
Authorization binds bounded state transition: proposal hash, current-state reference, symbol, target/qty bounds, max slippage, expiry, nonce. Re-evaluate from actual fills.

## §21 Ambiguous orders
Timeout → query clientOrderId. NOT_FOUND → wait protocol delay → query again. Confirmed absence may resend only with same clientOrderId and unexpired authorization; otherwise get new authorization. UNKNOWN → reconcile/FREEZE.

## §22 HALT/FLATTEN/FREEZE
HALT adds no risk. FLATTEN is bounded de-risking. FREEZE makes no autonomous risk change. State transitions logged; exit FREEZE only after reconciliation.

## §23 Reporting honesty
Every report states raw decisions, overlap factor, ESS+method, trial counts, comparison benchmark, costs, protocol hash, and confirmation-period limitations. Bar count is never sample size.

## §24 Required before Task 1
Constitution, research protocol, protocol/hypothesis/experiment/metrics/attestation schemas, threat model, backtester spec, cost-model spec.

## §25 Owner acknowledgment
Owner signs/date before first equity curve: NO_EDGE acceptable; BTC/ETH not independent replication; de-risking may lag B&H; no risk-increase bypass; no HALT override without incident process; AI advisory only; total deployed allocation can be lost via risks no backtest captures; only fully-loss-acceptable capital may be deployed; owner read §§12/14.

## §26 Audit logs
Registry, trials, lockbox logs, attestations, incidents, cycle outcomes are append-only/tamper-evident.

## §27 Reproducibility/hash canonicalization
Promotion-relevant artifacts must reproduce from recorded hashes/seeds or are void.

Self-referential hashes are computed with that hash value blanked/removed according to `HASH_CANONICALIZATION_v1.md`, whose sidecar hash is itself recorded.

## §28 Secrets
No secrets in repo/artifacts/logs/reports/screenshots/LLM context/CI. Production keys only under executor identity. Rotation/revocation rehearsal and permission/IP checks required before canary; withdrawals disabled.
