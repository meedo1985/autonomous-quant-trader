# Roadmap proposal — Task 13 to a working paper-trading app

**Status:** PROPOSAL. Nothing here is authorized until the owner approves it.
**Author:** Claude (Opus 5), coding AI, advisory only per Constitution sections 15/16.
**Date:** 2026-09-26
**Baseline:** Milestone 0.1 / Task 12 complete. Cycle `C1` not started, verdict
`KEEP_BLOCKED`. No frozen artifact is touched by any task below.

## 0. What this roadmap is and is not

It is a route from the current inactive foundations to an application that runs
the full `predictor -> governor -> executor -> exchange` loop of Constitution
section 19 **against a deterministic in-process simulated exchange**, with
monitoring, reconciliation, and a drafted deployment protocol.

Explicitly **out of scope of every task below**, and not reachable by finishing
all of them:

- live or testnet orders, and any network call to an order endpoint
- real API keys or any credential (section 28; Milestone 0.1 forbids them)
- lockbox or confirmation data of any kind (sections 7, 7a)
- statistical bindings: `D-16`, `D-17`, effective trial count, DSR, PBO, CPCV,
  ESS, bootstrap intervals, promotion statistics
- registering trials, starting cycle `C1`, binding the cycle record
- ML or LLM implementation (section 2; not yet scheduled)
- shadow mode, canary, or promotion

Paper trading against a simulator is **not** the section 19 live path and opens
no live gate. Sections 19 and 25 remain unsatisfied when this roadmap finishes,
by design.

## 1. Conventions that apply to every task

- **Size:** each task is scoped to one session, target <= 400 changed lines
  including tests. Where a task risks exceeding that, a split point is named.
- **Validation:** every task ends with `python -m pytest`, `ruff check .`,
  `ruff format --check .`, `mypy src`, `lint-imports`, `git diff --check`, with
  exact commands and results recorded under `review/task<NN>/`. A mandatory
  check that fails or cannot run blocks completion.
- **Reviews:** every task ends with `task-gate-review`. Tasks touching data
  semantics or research also invoke `scientific-reproducibility-review` and
  `quant-code-review`. Tasks touching Binance market data, exchange rules,
  orders, fills, fees, or reconciliation also invoke `binance-quant-review`.
  Every review record is committed in or before the commit that applies its
  repairs, per the AGENTS.md record discipline.
- **Data:** all tests and fixtures are synthetic or exploration-partition only.
- **Frozen artifacts:** `docs/`, `protocols/`, `schemas/`, `specs/`,
  `FROZEN_HASHES.json`, and every `.sha256` sidecar are read-only in all tasks.
  New documents are new files, never edits to frozen ones.

## 2. Dependency shape

```
13 -> 14 -> 15 -> 16 -> 17            (data and exploration; unblocked)
18                                    (simulated exchange; unblocked)
19                                    (monitoring; unblocked)
20                                    (deployment protocol draft; unblocked)
(18, 19) -> 21 -> 22 -> 23 -> 24 -> 25   (control path; gated by section 16)
```

Tasks 13–20 are unblocked today and are listed first. Tasks 21–25 are
implementable but **cannot merge** until the section 16 reviewer question is
answered (see 4.1).

---

# Part A — Unblocked tasks

## Task 13 — Binance public market-data downloader (no credentials)

**Goal.** A deterministic, credential-free client that fetches Binance Spot
public 1h klines and exchange metadata into immutable raw artifacts on disk. It
downloads bytes and verifies them; it parses nothing and interprets nothing.

**Files touched.**
- `src/aqt/data/binance_public.py` (new)
- `scripts/download_market_data.py` (new, operator-run CLI)
- `tests/unit/test_binance_public.py` (new; offline, fixture-driven)
- `README.md` (status paragraph)

**Constitution sections satisfied.** 6 (raw immutable, no silent deletion, full
hash lineage, UTC only, point-in-time filters and status where available);
28 (no credentials: the client refuses to send an auth header and refuses to
start if a Binance key variable is present in the environment); 2 (Binance Spot,
BTCUSDT and ETHUSDT only); 15 (the AI writes this code, the **owner runs it** —
Cycle-1 research network access is denied; see Q4).

**Design points.**
- Sources: `data.binance.vision` monthly and daily kline archives plus their
  published `.CHECKSUM` files, and one `exchangeInfo` snapshot for filters and
  symbol status. Public endpoints only: no signature, no key.
- Every artifact is written once, never overwritten, alongside a recorded
  SHA-256, source URL, and `as_of` UTC timestamp — exactly the inputs
  `aqt.data.manifest.RawArtifact` and `AvailabilityRecord` already expect.
- Missing months are recorded as unavailable, never silently skipped.
- Bounded retries with fixed backoff; no unbounded loop; no rate-limit evasion.

**Acceptance tests.**
1. With a fake transport, a fetch produces the exact declared bytes and the
   recorded SHA-256 matches an independently computed digest.
2. A checksum mismatch raises and writes no artifact.
3. The client refuses to construct a request carrying any authentication header,
   signature, or `apiKey` query parameter (asserted on the built request object).
4. Construction fails fast if `BINANCE_API_KEY` or `BINANCE_API_SECRET` (or the
   `.env.example` names) are set in the environment.
5. A missing archive yields an `unavailable(reason=...)` record, not a gap-fill.
6. Re-running over existing artifacts is a no-op and never rewrites bytes.
7. The whole test module runs with sockets blocked by a fixture.

**Blocking decisions.** None to start. Q3 (which partitions to fetch) and Q4
(who executes the network calls) shape the CLI defaults only; the code is
partition-agnostic, so either answer applies at run time.

---

## Task 14 — Raw archives to bar series, and exploration partition manifests

**Goal.** Parse raw kline artifacts into `BarSeries` through the frozen
bar-semantics module and produce a signed `PartitionManifest` for the
**exploration** window only. Produces a hash; binds nothing.

**Files touched.**
- `src/aqt/data/klines.py` (new: raw CSV/ZIP -> `Bar` objects)
- `scripts/build_manifests.py` (new)
- `tests/unit/test_klines.py`, `tests/integration/test_exploration_manifest.py`

**Constitution sections satisfied.** 6 (causal time semantics, no future
leakage, UTC only, one tested bar-semantics module — this task adds no second
one, it calls `aqt.data.bars`); 7 and 7a (the builder refuses the lockbox
partition; only `exploration` is built here); 27 (canonical hashing through the
existing `aqt.data.manifest` canonicalizer, with floats rejected in JSON
identity).

**Design points.**
- Reuses `aqt.data.bars.contiguous_bar_series` and
  `aqt.data.manifest.build_partition_manifest` unchanged. No new hashing code.
- The exploration window is read from `protocols/protocol_v1.yaml`
  (`partitions.exploration`, 2017-08-17 to 2021-12-31), not hard-coded.
- Gaps become `Gap` records. No interpolation, no forward fill.

**Acceptance tests.**
1. A synthetic raw archive round-trips to the exact expected `BarSeries`.
2. A malformed row raises; no partial series is returned.
3. Rebuilding the manifest from the same artifacts yields byte-identical
   canonical JSON and the same manifest hash.
4. Requesting the lockbox window raises before any file is read.
5. Requesting the confirmation window is refused by this task's CLI (see Q3).
6. A deliberately holed archive produces `Gap` records covering exactly the
   missing intervals.
7. `verify_partition_manifest` accepts the produced manifest and rejects a
   manifest with one flipped byte.

**Blocking decisions.** The produced `data_manifest_hash` is **not** bound into
a cycle record. Binding is a `cycle_start_bindings` governance act that starts
`C1`, which `KEEP_BLOCKED` forbids and which this roadmap does not touch.

---

## Task 15 — Exploration data quality and outage report

**Goal.** A deterministic report over the exploration manifest: coverage, gaps,
declared-untradeable outage windows, symbol status, and the filter snapshot at
manifest time. Human-readable evidence that the data is fit to explore on.

**Files touched.**
- `src/aqt/data/quality.py` (new)
- `scripts/data_quality_report.py` (new)
- `tests/unit/test_data_quality.py`
- `review/task15/DATA_QUALITY_REPORT.md` (generated evidence, committed)

**Constitution sections satisfied.** 6 (outages untradeable — this task is what
makes outage windows explicit rather than implicit); 23 (reporting honesty: the
report states bar counts as bar counts and never as sample size).

**Acceptance tests.**
1. The report is a pure function of the manifest plus parsed bars; two runs give
   byte-identical output.
2. Every `Gap` in the manifest appears in the report's outage table.
3. The report refuses to emit if the manifest hash does not verify.
4. A content check asserts the report contains no sample-size claim and no
   statistic beyond counts, coverage fractions, and timestamps.

**Blocking decisions.** None.

---

## Task 16 — Exploration-only research harness

**Goal.** A runner that evaluates a fixed configuration end to end on the
exploration partition: features -> exposure mapping -> backtest -> descriptive
metrics. Free-form, biased, and explicitly **not a registered trial**.

**Files touched.**
- `src/aqt/research/harness.py` (new)
- `src/aqt/research/__init__.py` (exports)
- `tests/integration/test_research_harness.py`
- `pyproject.toml` (extend the existing research forbidden contract if a new
  submodule needs naming)

**Constitution sections satisfied.** 7a (the sandbox mounts exploration only —
the harness takes an exploration manifest and refuses any other partition
name); 9 (exploration is not a registered trial because it is confined to
exploration data — the harness never calls `start_attempt`); 15 (research AI:
exploration only, no confirmation, no lockbox, no protected-code writes);
17 (import boundaries: `aqt.research` must not reach governor, execution, or
lockbox_eval — already contracted, extended to any new module).

**Design points.**
- Composes existing frozen-behavior modules only: `features.factory`,
  `benchmarks.canonical`, `backtest.engine`, `backtest.costs`,
  `metrics.descriptive`.
- **No model class is implemented.** Configurations are the canonical baseline
  and the rule-based exposure mappings the protocol already names. The classes
  in `models.allowed_classes_cycle_1` stay unimplemented until their scheduled
  task.
- No DSR, PBO, CPCV, ESS, bootstrap, or paired promotion statistic is computed
  or reported here. Those are bound decisions and out of scope.

**Acceptance tests.**
1. A run on a synthetic exploration manifest is deterministic across two runs
   and two processes.
2. Passing a confirmation or lockbox manifest raises before any data is read.
3. The harness writes no ledger attempt record and registers no trial.
4. `lint-imports` passes with the research contract intact.
5. The result object exposes descriptive metrics only; a content assertion
   rejects any promotion-statistic key.

**Blocking decisions.** Kept exploration-only precisely because `D-16` and
`D-17` are open: with the effective trial count unbound, no run may be allowed
to count as a trial. See also Q1 (section 25 and equity curves).

---

## Task 17 — Sandbox exploration job log and the 250-job review trigger

**Goal.** Implement `protocol_v1.yaml sandbox_exploration_policy`: every
exploration job is logged, and the 250th job in a cycle raises a human-review
flag that the harness surfaces and cannot clear itself.

**Files touched.**
- `src/aqt/research/joblog.py` (new)
- `tests/unit/test_joblog.py`

**Constitution sections satisfied.** 26 (append-only and tamper-evident —
reuses the existing hash-chained `aqt.core.ledger`); 3 (governance: the
partition boundary is the control, and high exploratory volume triggers review).

**Acceptance tests.**
1. Job 250 sets the review flag; jobs 1–249 do not.
2. The flag cannot be cleared by library code; only a committed human record
   file clears it.
3. The log is hash-chained, and a mutated entry fails verification.
4. Concurrent writers from two processes produce a single valid chain, via the
   ledger's existing cross-process Windows lock.

**Blocking decisions.** None. Small task; may be folded into Task 16 if both
together stay under the line budget.

---

## Task 18 — Deterministic simulated Binance Spot exchange

**Goal.** An in-process test double answering the order API the executor will
use: place, query by `clientOrderId`, cancel, account balances. Deterministic,
offline, with injectable faults (timeout, `NOT_FOUND`, partial fill, duplicate
`clientOrderId`, rejection on a filter violation).

**Files touched.**
- `src/aqt/execution/simulator.py` (new)
- `tests/unit/test_simulator.py`

**Constitution sections satisfied.** 2 (spot, long-only, exposure in [0,1], no
shorting, margin, or leverage — the simulator rejects anything else); 6 (bar
semantics: a decision at close(t) fills at open(t+1)); 10 and 18 (identical bar
semantics and cost model as the backtester: the simulator applies the frozen
`cost_model_hash` fee model, it does not invent one); 28 (no credentials: the
simulator has no auth surface at all).

**Design points.**
- Applies the real Binance Spot filter families (`LOT_SIZE`, `MIN_NOTIONAL`,
  `PRICE_FILTER`, `PERCENT_PRICE`) from the Task 13 exchangeInfo snapshot, so
  the executor meets realistic rejections rather than a permissive stub.
- Faults are declared up front in a scenario object; nothing is random.
- Lives under `aqt.execution`, so the contracts forbidding execution from
  reaching `aqt.models` and `aqt.research` already cover it.

**Acceptance tests.**
1. A market buy at a known bar fills at `open(t+1)` with the frozen cost model's
   fee, matching an independently computed expected value.
2. An order violating `MIN_NOTIONAL` is rejected with a stable error code.
3. Re-placing the same `clientOrderId` is idempotent, never a second fill.
4. A scripted timeout scenario leaves the order in a state that a later query by
   `clientOrderId` resolves to the same terminal outcome.
5. Any sell exceeding the simulated base balance is rejected (no shorting).
6. A full scenario replay is byte-identical across two runs.

**Blocking decisions.** None. This is a test double, not an exchange client, and
is deliberately built **before** the governor so the control path never has a
reason to talk to a real venue.

---

## Task 19 — Monitoring, alerting, and the operational event log

**Goal.** The alerting layer section 19 requires **before** shadow: a typed
event stream, health checks, severity routing, and an append-only tamper-evident
operational log. Sinks are local only (stdout plus a rotating file).

**Files touched.**
- `src/aqt/monitoring/events.py`, `src/aqt/monitoring/alerts.py` (new)
- `src/aqt/monitoring/health.py` (new)
- `tests/unit/test_monitoring.py`

**Constitution sections satisfied.** 19 (alerting before shadow); 22 (state
transitions are logged); 26 (append-only, tamper-evident); 28 (a redaction pass
asserts no secret-shaped value reaches any sink — no credential exists, and the
log must stay unable to carry one); 17 (monitoring must not import research).

**Acceptance tests.**
1. Every event type serializes to canonical JSON and round-trips.
2. The log is hash-chained; a mutated line fails verification.
3. A value matching a credential pattern is redacted before reaching a sink, and
   the redaction is itself logged.
4. A critical event with no configured sink is a startup error, not a silent
   drop: alerting must exist before the loop can run.
5. Health checks report stale-data, clock-skew, and loop-lag conditions on
   synthetic inputs.

**Blocking decisions.** None. External alert channels (email, phone, webhook)
are deliberately excluded: each needs a credential and an outbound network path,
both forbidden in Milestone 0.1. They belong in the deployment protocol
(Task 20) as a named prerequisite for shadow.

---

## Task 20 — Deployment protocol draft (section 19)

**Goal.** Write the separate deployment protocol that section 19 requires before
shadow. A **draft document for owner review**, not an activated protocol and not
a frozen artifact.

**Files touched.**
- `protocols/drafts/DEPLOYMENT_PROTOCOL_v1_DRAFT.md` (new file in a new
  `drafts/` subdirectory; no frozen file is edited, no sidecar is written,
  nothing is added to `FROZEN_HASHES.json`)
- `review/task20/REVIEW_NOTES.md`

**Constitution sections addressed (as a draft).** 19 (live path order, alerting
before shadow, startup reconciliation, config or hash mismatch ->
`REFUSE_START`, separate deployment protocol); 14 (owner clauses: risk decreases
immediate, HALT override requirements); 22 (HALT / FLATTEN / FREEZE semantics);
28 (key handling, rotation and revocation rehearsal, permission and IP checks,
withdrawals disabled — all stated as future prerequisites, none performed);
4 and 24 (the 72-hour floors on cooling-off and safety-amendment activation).

**Contents.** Preconditions for shadow; preconditions for canary; the startup
reconciliation procedure; the `REFUSE_START` condition list; the alerting
channels that must exist and be tested; the incident and HALT-exit procedure;
the key lifecycle rehearsal; the rollback procedure; and an explicit dependency
list naming the section 25 signature and the `L-01`–`L-04` loss bounds as inputs
the draft cannot supply.

**Acceptance tests.** A documentation task, so instead: a citation check that
every referenced Constitution section number exists and matches the frozen text;
`git diff --check`; a test asserting no frozen file or sidecar changed in the
commit; `task-gate-review`.

**Blocking decisions.** The draft **cannot be activated** by the AI (section 4:
amendment and activation require the owner of record). `L-01`–`L-04` are
unanswered, so the capital and loss-bound clauses stand as placeholders
referencing the owner's pending adoption. Section 25 is unsigned.

---

# Part B — Control path (gated by the section 16 review requirement)

Tasks 21–24 each touch a component Constitution section 16 **enumerates** as
requiring different-model plus human PR review before merge: the governor, the
executor state machine, and protocol-enforcement logic. Each can be *written* in
one session, but none may merge until question Q2 is answered. As of 2026-09-22
Codex was reported unavailable and three Fable attempts died on HTTP 429.

## Task 21 — Governor state machine (section 20)

**Goal.** The authorization issuer. Given a proposed target exposure and the
actual current state, it either issues a bounded authorization or refuses.

**Files touched.**
- `src/aqt/governor/authorization.py`, `src/aqt/governor/machine.py` (new)
- `tests/unit/test_governor.py`
- `pyproject.toml` (import contracts, if a new submodule needs naming)

**Constitution sections satisfied.** 20 (an authorization binds proposal hash,
current-state reference, symbol, target and quantity bounds, max slippage,
expiry, and nonce; re-evaluation is from actual fills, never intended state);
12 (vol management is de-risking, not alpha — lagging buy-and-hold is never an
override reason); 14 (risk increases take the formal path, risk decreases are
immediate); 17 (governor must not import execution or models — already
contracted).

**Protocol rules enforced.** `risk_increase_rule` (only at 00:00 UTC and only if
24h since the last increase); `intraday_action_rule` (intraday actions only
reduce, and only when the target is at least 0.10 below current);
`rebalance_band_absolute` 0.10; `minimum_holding_hours_for_risk_increase` 24;
`max_exposure_per_asset` 1.0.

**Acceptance tests.**
1. A risk increase at 03:00 UTC is refused; the same increase at 00:00 UTC with
   25h elapsed is authorized.
2. A risk increase 23h after the last one is refused.
3. An intraday reduction of 0.09 is refused; 0.11 is authorized.
4. A target above 1.0 or below 0.0 is refused.
5. An authorization carries every section 20 field, and a nonce never repeats.
6. An expired authorization is refused at use time.
7. After a partial fill, the next decision is computed from the **actual** filled
   exposure; a test supplying a deliberately wrong intended state proves the
   intended state is not consulted.
8. Property test: no input sequence produces an authorization that increases
   exposure outside the 00:00 UTC window.

**Blocking decisions.** Q2. The governor is on the section 16 enumerated list;
merging without a different-model review violates section 16.

---

## Task 22 — Executor state machine and the ambiguous-order protocol (section 21)

**Goal.** The order lifecycle: consume one authorization, place at most what it
allows, and resolve every ambiguous outcome by the section 21 rules. Runs only
against the Task 18 simulator.

**Files touched.**
- `src/aqt/execution/machine.py`, `src/aqt/execution/orders.py` (new)
- `tests/unit/test_executor.py`, `tests/integration/test_executor_simulator.py`

**Constitution sections satisfied.** 21 (timeout -> query `clientOrderId`;
`NOT_FOUND` -> wait the protocol delay -> query again; confirmed absence may
resend **only** with the same `clientOrderId` and an unexpired authorization,
otherwise a new authorization is required; `UNKNOWN` -> reconcile or FREEZE);
19 (the executor is the only identity that would ever hold a key — none exists
now); 20 (an authorization is consumed, never exceeded); 28.

**Acceptance tests.**
1. Each of the timeout, `NOT_FOUND`-then-found, `NOT_FOUND`-then-absent, and
   `UNKNOWN` scenarios drives exactly the transition section 21 names.
2. A resend after confirmed absence reuses the identical `clientOrderId`.
3. A resend with an expired authorization is refused and a new authorization is
   demanded.
4. `UNKNOWN` ends in reconcile-or-FREEZE and never in a new order.
5. No path places two distinct orders under one authorization.
6. Exhaustive transition-table test: every (state, event) pair is either defined
   or explicitly rejected — no implicit fallthrough.

**Blocking decisions.** Q2. The executor state machine is enumerated in
section 16.

---

## Task 23 — HALT, FLATTEN, FREEZE, and reconciliation

**Goal.** The safety controller plus the startup and periodic reconciliation
routine.

**Files touched.**
- `src/aqt/execution/safety.py`, `src/aqt/execution/reconcile.py` (new)
- `tests/unit/test_safety.py`, `tests/integration/test_reconciliation.py`

**Constitution sections satisfied.** 22 (HALT adds no risk; FLATTEN is bounded
de-risking; FREEZE makes no autonomous risk change; all transitions logged; exit
FREEZE only after reconciliation); 14 (HALT override requires a written incident
record, an identified or bounded cause, successful reconciliation, an explicit
owner action, and a timestamp — the code requires all five artifacts and can
synthesize none of them); 19 (startup reconciliation required); 26 (incidents
append-only and tamper-evident).

**Acceptance tests.**
1. HALT while holding exposure places no order at all.
2. FLATTEN reduces exposure monotonically and never crosses zero into a short.
3. FREEZE takes no autonomous action even as simulated prices move.
4. Exiting FREEZE without a successful reconciliation record is refused.
5. A HALT override missing any one of the five section 14 artifacts is refused,
   tested once per missing artifact.
6. Startup reconciliation detects an injected mismatch between local state and
   simulated exchange state and refuses to start.

**Blocking decisions.** Q2 — this is protocol-enforcement logic under section 16.

---

## Task 24 — Paper-trading loop

**Goal.** Wire it together: a scheduled loop that reads bars, asks the predictor
for a target, asks the governor for an authorization, hands it to the executor,
and records everything through monitoring — all against the simulator.

**Files touched.**
- `src/aqt/allocation/predictor.py` (new: the frozen deployable baseline as the
  target source — **no model is trained or implemented**; see Q5)
- `src/aqt/app/paper_loop.py` (new package `aqt.app`)
- `scripts/run_paper_trading.py` (new)
- `configs/paper_trading.example.toml` (new)
- `pyproject.toml` (import contracts for `aqt.app`)
- `tests/integration/test_paper_loop.py`

**Constitution sections satisfied.** 19 (the exact `predictor -> governor ->
executor -> exchange` order; alerting wired before the loop can start; startup
reconciliation; config or hash mismatch -> `REFUSE_START`); 11 (the deployable
baseline stays `VOL_TARGET_BUY_AND_HOLD`, unchanged); 12; 17 (a new contract
forbidding `aqt.app` from importing `aqt.research`, keeping live packages clear
of AI-agent code); 23 (the run report states decision counts and never calls a
bar count a sample size); 28.

**Design points.**
- The loop refuses to start if any configured hash mismatches the frozen value,
  no alert sink is configured, reconciliation fails, the exchange adapter is
  anything other than the simulator, or any Binance credential variable is set.
- The clock is injectable; a simulated run over a year of exploration bars
  completes in seconds and is deterministic.
- If wiring plus tests exceed the line budget, split at the seam: loop skeleton
  and `REFUSE_START` first, monitoring and reporting second.

**Acceptance tests.**
1. A full multi-month simulated run is deterministic across two runs.
2. Every `REFUSE_START` condition is tested individually.
3. The loop never places an order without a live, unexpired authorization.
4. Selecting a non-simulator adapter raises at configuration time.
5. A mid-run injected exchange fault drives the section 21 path and then the
   section 22 path, and the run ends in FREEZE rather than in an order.
6. The end-of-run report names the protocol hash, the data manifest hash, the
   decision count, and the cost model hash (section 23).

**Blocking decisions.** Q2 (depends on Tasks 21–23). Q5 (predictor choice).
Q1 (whether a paper equity curve triggers the section 25 signature requirement).

---

## Task 25 — Paper-trading acceptance run and evidence packet

**Goal.** Run the app, exercise the drills, and commit the evidence. The
milestone's closing artifact.

**Files touched.**
- `review/task25/PAPER_TRADING_EVIDENCE.md`, plus the run's committed logs
- `README.md` (status)

**Constitution sections satisfied.** 23 (reporting honesty: raw decisions,
overlap factor, trial counts stated as zero because no trial was registered,
comparison benchmark, costs, protocol hash, and the limitation that a simulated
run is not evidence of edge); 26; 19 and 25 (the packet states plainly that both
remain unsatisfied and that no live gate is opened).

**Acceptance tests.** The committed drills: a clean multi-month run; a HALT
drill; a FLATTEN drill; a FREEZE-and-reconcile drill; an ambiguous-order drill;
and a `REFUSE_START` drill — each with its log excerpt and expected outcome.

**Blocking decisions.** Q1. If a paper equity curve counts as the "first equity
curve" of section 25, this task cannot run before the acknowledgment is signed,
and that reading would also reach Task 16.

---

# 3. What is still not possible after Task 25

- Cycle `C1` has not started; no trial is registered; no hypothesis is
  preregistered; `data_manifest_hash` and `backtester_code_hash` are unbound.
- `D-16`, `D-17`, and every other statistical binding remain open.
- Section 25 is unsigned, `L-01`–`L-04` are unadopted, and the deployment
  protocol exists only as an unactivated draft.
- No key exists, no live or testnet order has been placed, and shadow has not
  begun.

`KEEP_BLOCKED` and `NO_EDGE_FOUND` remain valid and untouched.

# 4. Known blockers carried by this roadmap

**4.1 Section 16 different-model review (Tasks 21–25).** The governor, the
executor state machine, and protocol-enforcement logic require different-model
plus human PR review before merge. Codex was reported unavailable on 2026-09-22;
three Fable attempts failed on HTTP 429. Until a reviewer exists, Part B can be
written but not merged. This is question Q2.

**4.2 Section 25 acknowledgment (Tasks 16, 24, 25).** Unsigned, and already
written out for signature. Whether a simulated equity curve triggers the clause
is a reading the owner must give, not the AI. Question Q1.

**4.3 `L-01`–`L-04` (Task 20).** Unadopted, so the deployment protocol draft
carries placeholders. Not blocking for paper trading.

**4.4 Network execution under section 15 (Tasks 13–15).** Research-side network
access is denied in Cycle 1. The AI writes the downloader; the owner runs it.
Question Q4.

# 5. Questions the owner must answer

**Q1 — Section 25 and the first equity curve.** Does a paper-trading equity
curve produced on exploration data against a simulated exchange count as the
"first equity curve" of section 25? If yes, the acknowledgment must be signed
before Task 16, and Tasks 16–25 wait on that signature. If no, please record the
reading so the roadmap can cite it. (The AI's view: the safest reading is yes,
and signing is the cheapest safety step available regardless.)

**Q2 — Section 16 different-model reviewer.** Who reviews the governor, the
executor state machine, and the protocol-enforcement logic before merge — Codex
if it is available again, Fable if credits are restored, or another model you
name? Tasks 21–25 cannot merge without an answer.

**Q3 — Which partitions to download in Task 13.** Exploration only for now, or
all three windows with the confirmation and lockbox archives written to
separate, access-restricted directories the research path cannot read? Only the
exploration data is needed for anything in this roadmap.

**Q4 — Who executes the network calls.** Confirm that you run
`scripts/download_market_data.py` yourself and that the AI never makes a network
call, consistent with section 15's Cycle-1 network denial.

**Q5 — The paper loop's predictor.** Should the paper loop's target source be
the frozen deployable baseline `VOL_TARGET_BUY_AND_HOLD` only (proposed: it
implements no model and stays inside section 2), or do you also want a
placeholder predictor interface reserved for a future scheduled model task?

---

**Approval.** Approving this document authorizes Tasks 13–20 in order, subject
to the answers above. Tasks 21–25 are authorized to be written only, and may
merge only after Q2 is answered and the section 16 review is on record.
